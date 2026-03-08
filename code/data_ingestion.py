"""
data_ingestion.py
=================
Real-data integration layer for the green hydrogen catalyst research pipeline.

The existing tools (stability_ml.py, gate3_lifetime_projector.py, etc.) operate
on simulated / literature-derived data.  This module provides the bridge when
a real lab begins generating experimental data.  It:

  1. Ingests real ICP-MS dissolution measurements (CSV from Agilent 7800 or
     similar instruments — handles the commented-header format used on-site)
  2. Ingests OER polarisation curve data (CSV with E_v_rhe / j_ma_cm2 columns)
  3. Ingests gate data in JSON format (programmatic lab integration)
  4. Updates the running ML training dataset (stability_ml_dataset.csv)
  5. Fits a real power law to the Gate 3 lifetime model
  6. Re-projects P50 lifetime using real dissolution kinetics

Design principles
-----------------
- No external dependencies beyond numpy, pandas, scipy, matplotlib.
- All I/O functions return plain Python dicts or DataFrames — easy to chain.
- Functions are composable: call individually or via run_ingestion_pipeline().
- Validation is explicit: every ingest function flags missing / anomalous data.

Run without real files
-----------------------
    python data_ingestion.py

The __main__ block generates fully synthetic test data (Ca(0.11)Mn(0.55)W(0.34)),
runs the complete pipeline, and prints a comparison of real vs model parameters.
"""

from __future__ import annotations

import csv
import io
import json
import os
import re
import sys
import warnings
from datetime import datetime
from pathlib import Path
from typing import Optional

import matplotlib
matplotlib.use("Agg")            # non-interactive backend — works without a display
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np
import pandas as pd
from scipy.optimize import curve_fit

warnings.filterwarnings("ignore")


# ─── Physical constants and reference tables ──────────────────────────────────
# (Copied from gate3_lifetime_projector.py and materials_project_api.py so that
#  data_ingestion.py is fully self-contained.)

# Dissolution rate constants k0 at E_OER = 1.55 V vs RHE, pH 1, 25°C
# Units: µg/cm²/h per unit mole fraction
# Layout: (k0_ugcm2h, alpha_power, E_diss_V, density_g_cm3)
PHASE_PARAMS = {
    "MnO2":  (3.5,   0.50, 0.85, 5.02),
    "WO3":   (1.0,   0.42, 1.05, 7.16),
    "CaWO4": (0.06,  0.32, 1.38, 6.06),
    "TiO2":  (0.025, 0.28, 1.20, 3.90),
}

# Hammer–Norskov d-band centre table (eV relative to Fermi level)
# Source: Hammer & Norskov (1995); Vojvodic et al. (2011)
DBAND_CENTER_EV: dict[str, float] = {
    "Sc": -1.70, "Ti": -2.10, "V":  -1.85, "Cr": -2.40, "Mn": -2.00,
    "Fe": -1.29, "Co": -1.17, "Ni": -1.15, "Cu": -2.67, "Zn": -5.50,
    "Y":  -2.10, "Zr": -2.50, "Nb": -1.85, "Mo": -1.46, "Tc": -1.19,
    "Ru": -1.41, "Rh": -1.73, "Pd": -1.83, "Ag": -4.30,
    "Hf": -2.60, "Ta": -1.92, "W":  -1.80, "Re": -1.60, "Os": -1.50,
    "Ir": -2.11, "Pt": -2.25, "Au": -3.56,
    "Ca": -6.00,
}

# Dissolution potentials at pH 1, V vs RHE (Pourbaix Atlas)
DISSOLUTION_POTENTIAL_V: dict[str, float] = {
    "Mn": 0.85, "Fe": 0.60, "Co": 0.55, "Ni": 0.40, "Cr": 0.90,
    "V":  0.50, "W":  1.05, "Mo": 0.65, "Ti": 1.20, "Ca": 2.50,
    "Ru": 1.10, "Ir": 1.60, "Pt": 1.18, "Rh": 1.00,
    "Sc": 1.80, "Y":  1.90, "Nb": 1.20, "Zr": 1.50, "Hf": 1.60,
}

# eg electron occupancy for octahedral oxides
EG_ELECTRONS: dict[str, float] = {
    "Mn": 0.0, "Fe": 1.0, "Co": 1.0, "Ni": 1.2, "Cr": 0.0,
    "V":  0.0, "W":  0.0, "Mo": 0.0, "Ti": 0.0, "Ru": 1.0,
    "Ir": 0.5, "Ca": 0.0,
}

# Metal–oxygen bond energy linear scaling from d-band
# E_MO ≈ 0.8 × d_band_center + 4.5  (Rossmeisl scaling)
def _mo_bond_energy(d_band_center: float) -> float:
    return 0.8 * d_band_center + 4.5

# Gate 3 pass criteria (mirrors gate3_lifetime_projector.py)
GATE3_CUMULATIVE_UG    = 25.0     # µg/cm² cumulative in 500 h
GATE3_STEADY_UG_H      = 0.10     # µg/cm²/h steady-state rate
GATE3_P50_LIFETIME_H   = 1_000    # h projected P50 lifetime
LOADING_UG_CM2         = 100.0    # µg/cm² catalyst loading (0.10 mg/cm²)


# ─── Utility helpers ──────────────────────────────────────────────────────────

def _power_law(t: np.ndarray, D0: float, alpha: float) -> np.ndarray:
    """Power-law dissolution model: D(t) = D0 × t^(-alpha)."""
    return D0 * np.asarray(t, dtype=float) ** (-alpha)


def _fit_power_law(
    t: np.ndarray,
    D: np.ndarray,
    t_start: float = 3.0,
) -> tuple[float, float, np.ndarray]:
    """
    Fit D(t) = D0 × t^(-alpha) to dissolution data.

    Parameters
    ----------
    t : array-like
        Time points in hours (must be > 0).
    D : array-like
        Dissolution rates in µg/cm²/h at each time point.
    t_start : float
        Ignore early data before this time (avoids surface-transient bias).

    Returns
    -------
    D0 : float
        Power-law prefactor (µg/cm²/h).
    alpha : float
        Power-law exponent (dimensionless, typically 0.3–0.7).
    pcov : ndarray
        Covariance matrix from curve_fit (use np.sqrt(np.diag(pcov)) for σ).
    """
    t = np.asarray(t, dtype=float)
    D = np.asarray(D, dtype=float)

    mask = (t >= t_start) & np.isfinite(D) & (D > 0)
    t_fit = t[mask]
    D_fit = D[mask]

    if len(t_fit) < 3:
        # Fall back to first available point
        D0_guess = float(D[D > 0][0]) if np.any(D > 0) else 1.0
        return D0_guess, 0.35, np.zeros((2, 2))

    try:
        p0 = [float(D_fit[0]), 0.40]
        popt, pcov = curve_fit(
            _power_law, t_fit, D_fit,
            p0=p0,
            bounds=([1e-6, 0.01], [1000.0, 2.0]),
            maxfev=5000,
        )
        return float(popt[0]), float(popt[1]), pcov
    except RuntimeError:
        # Optimisation failed — use log-linear regression as fallback
        log_t = np.log(t_fit)
        log_D = np.log(D_fit)
        coeffs = np.polyfit(log_t, log_D, 1)
        alpha = -coeffs[0]
        D0 = np.exp(coeffs[1])
        return float(D0), float(max(0.01, min(alpha, 2.0))), np.zeros((2, 2))


def _cumulative_integral(
    D0: float,
    alpha: float,
    t_start: float,
    t_end: float,
    cum_at_start: float = 0.0,
) -> float:
    """
    Analytical integral of D0 × t^(-alpha) from t_start to t_end,
    added to cum_at_start.
    """
    if abs(alpha - 1.0) < 0.01:
        integral = D0 * np.log(t_end / t_start)
    else:
        integral = D0 / (1.0 - alpha) * (t_end ** (1.0 - alpha) - t_start ** (1.0 - alpha))
    return cum_at_start + max(0.0, integral)


def _project_p50_lifetime(
    D0: float,
    alpha: float,
    t_measured: float,
    cum_measured: float,
    mass_budget_ug: float = LOADING_UG_CM2,
    t_max_h: float = 250_000,
) -> float:
    """
    Project P50 lifetime (time when cumulative dissolution = 50% of loading).

    Uses the analytical cumulative integral of the fitted power law,
    scanning forward from t_measured.

    Parameters
    ----------
    D0, alpha : float
        Fitted power-law parameters.
    t_measured : float
        Last measured time point (h).
    cum_measured : float
        Cumulative dissolution at t_measured (µg/cm²).
    mass_budget_ug : float
        Total catalyst loading (µg/cm²).  P50 is reached at 50% of this.
    t_max_h : float
        Search horizon in hours.

    Returns
    -------
    float
        Projected P50 lifetime in hours.  Returns t_max_h if not reached.
    """
    target = mass_budget_ug * 0.5
    if cum_measured >= target:
        return t_measured  # already exceeded

    t_scan = np.geomspace(t_measured, t_max_h, 10_000)
    for t in t_scan:
        cum = _cumulative_integral(D0, alpha, t_measured, t, cum_measured)
        if cum >= target:
            return float(t)

    return float(t_max_h)


# ─── 1. ICP-MS dissolution ingestion ─────────────────────────────────────────

def ingest_icpms(
    csv_path: str,
    composition: Optional[dict[str, float]] = None,
    electrode_area_cm2: Optional[float] = None,
) -> dict:
    """
    Ingest an ICP-MS dissolution CSV and compute per-element dissolution rates.

    Expected CSV format (instrument output from Agilent 7800 or compatible):
    - Comment lines starting with '#' at the top (parsed for metadata)
    - Header row: t_h, Mn_ppb, W_ppb, Ca_ppb, Ti_ppb, V_ml, area_cm2
    - Subsequent rows: numeric values; V_ml and area_cm2 may be constant
    - The 'area_cm2' column may be absent if electrode_area_cm2 is supplied.

    Conversion formula:
        D_element (µg/cm²/h) = C_ppb × V_ml / (1000 × area_cm2 × Δt_h)
    where:
        C_ppb   = concentration in µg/L (ppb)
        V_ml    = eluate volume in mL
        area_cm2 = geometric electrode area

    The Δt_h interval is the time span of each measurement period.
    ICP-MS typically measures accumulated concentration over the whole interval,
    so we use the midpoint time for the rate assignment.

    Parameters
    ----------
    csv_path : str
        Path to the ICP-MS CSV file.
    composition : dict[str, float], optional
        Cation fractions e.g. {"Ca": 0.11, "Mn": 0.55, "W": 0.34}.
        If None, attempt to parse from the '# Sample:' comment header.
    electrode_area_cm2 : float, optional
        Override for electrode area (cm²).  Used if the 'area_cm2' column
        is absent from the CSV.

    Returns
    -------
    dict with keys:
        'sample_id' : str
        'composition' : dict[str, float]
        'data' : pd.DataFrame  — columns: t_h, D_Mn, D_W, D_Ca, D_Ti, D_total
                                  all rates in µg/cm²/h
        'fit' : dict — {'D0': float, 'alpha': float, 'D0_sigma': float,
                        'alpha_sigma': float, 'r_squared': float}
        'warnings' : list[str]
        'metadata' : dict
    """
    csv_path = str(csv_path)
    warn_list: list[str] = []
    metadata: dict = {"source_file": csv_path, "ingested_at": datetime.utcnow().isoformat()}

    # ── Parse comment header ─────────────────────────────────────────────────
    header_lines: list[str] = []
    data_lines:   list[str] = []

    with open(csv_path, "r", encoding="utf-8-sig") as fh:
        for line in fh:
            stripped = line.strip()
            if stripped.startswith("#"):
                header_lines.append(stripped)
            elif stripped:
                data_lines.append(stripped)

    # Extract metadata from comments
    sample_id = "UNKNOWN"
    for hline in header_lines:
        m = re.search(r"Sample:\s*(.+)", hline, re.IGNORECASE)
        if m:
            sample_id = m.group(1).strip()
        m = re.search(r"Date:\s*(.+)", hline, re.IGNORECASE)
        if m:
            metadata["date"] = m.group(1).strip()
        m = re.search(r"Protocol:\s*(.+)", hline, re.IGNORECASE)
        if m:
            metadata["protocol"] = m.group(1).strip()
        m = re.search(r"Instrument:\s*(.+)", hline, re.IGNORECASE)
        if m:
            metadata["instrument"] = m.group(1).strip()

    # Attempt to parse composition from sample_id string if not supplied
    # Handles patterns like Ca(0.11)Mn(0.55)W(0.34)
    if composition is None:
        parsed_comp: dict[str, float] = {}
        for match in re.finditer(r"([A-Z][a-z]?)\(([0-9.]+)\)", sample_id):
            el, frac = match.group(1), float(match.group(2))
            parsed_comp[el] = frac
        composition = parsed_comp if parsed_comp else {}

    metadata["sample_id"] = sample_id

    # ── Read tabular data ────────────────────────────────────────────────────
    reader = csv.DictReader(io.StringIO("\n".join(data_lines)))
    rows = list(reader)

    if not rows:
        raise ValueError(f"No data rows found in {csv_path}")

    # Normalise column names: strip whitespace
    def _norm(d: dict) -> dict:
        return {k.strip(): v.strip() for k, v in d.items() if k is not None}

    rows = [_norm(r) for r in rows]

    required_cols = {"t_h", "Mn_ppb", "W_ppb"}
    found_cols = set(rows[0].keys())
    missing = required_cols - found_cols
    if missing:
        raise ValueError(f"Required columns missing from {csv_path}: {missing}")

    # Build arrays
    t_h_arr    = np.array([float(r["t_h"])    for r in rows])
    Mn_ppb_arr = np.array([float(r.get("Mn_ppb", 0) or 0) for r in rows])
    W_ppb_arr  = np.array([float(r.get("W_ppb",  0) or 0) for r in rows])
    Ca_ppb_arr = np.array([float(r.get("Ca_ppb", 0) or 0) for r in rows])
    Ti_ppb_arr = np.array([float(r.get("Ti_ppb", 0) or 0) for r in rows])

    # Volume (mL) — may be constant column or single value
    if "V_ml" in found_cols:
        V_ml_arr = np.array([float(r.get("V_ml", 5.0) or 5.0) for r in rows])
    else:
        warn_list.append("V_ml column absent — assuming 5.0 mL per timepoint.")
        V_ml_arr = np.full(len(t_h_arr), 5.0)

    # Electrode area
    if electrode_area_cm2 is not None:
        area_arr = np.full(len(t_h_arr), float(electrode_area_cm2))
    elif "area_cm2" in found_cols:
        area_arr = np.array([float(r.get("area_cm2", 0.196) or 0.196) for r in rows])
    else:
        warn_list.append("area_cm2 column absent and electrode_area_cm2 not supplied. "
                         "Assuming 0.196 cm² (standard 5 mm RDE).")
        area_arr = np.full(len(t_h_arr), 0.196)

    # ── Compute interval durations ───────────────────────────────────────────
    # ICP-MS accumulates dissolved species over the interval [t_prev, t_now].
    # t_h_arr[0] is the end of the first interval, starting from t=0.
    dt_arr = np.diff(t_h_arr, prepend=0.0)
    dt_arr[dt_arr <= 0] = np.nanmedian(dt_arr[dt_arr > 0])  # guard against bad data

    # ── Conversion: ppb × V_ml → µg dissolved in interval ───────────────────
    # C_ppb = µg/L = µg / (1000 mL)
    # µg dissolved = C_ppb × V_ml / 1000
    # Rate (µg/cm²/h) = µg_dissolved / (area_cm2 × dt_h)
    def _rate(ppb_arr: np.ndarray) -> np.ndarray:
        ug_dissolved = ppb_arr * V_ml_arr / 1000.0
        with np.errstate(divide="ignore", invalid="ignore"):
            rate = np.where(
                area_arr * dt_arr > 0,
                ug_dissolved / (area_arr * dt_arr),
                0.0,
            )
        return rate

    D_Mn = _rate(Mn_ppb_arr)
    D_W  = _rate(W_ppb_arr)
    D_Ca = _rate(Ca_ppb_arr)
    D_Ti = _rate(Ti_ppb_arr)
    D_total = D_Mn + D_W + D_Ca + D_Ti

    # ── Anomaly detection: flag readings > 3σ above baseline ────────────────
    for name, arr in [("Mn", D_Mn), ("W", D_W), ("Ca", D_Ca), ("Ti", D_Ti)]:
        if len(arr) > 3:
            median_val = np.nanmedian(arr)
            mad = np.nanmedian(np.abs(arr - median_val))
            sigma_robust = 1.4826 * mad  # consistent estimator for σ under normality
            if sigma_robust > 0:
                high = arr > median_val + 3.0 * sigma_robust
                if np.any(high):
                    idxs = np.where(high)[0].tolist()
                    warn_list.append(
                        f"D_{name}: anomalous readings at timepoints "
                        f"{[round(t_h_arr[i], 1) for i in idxs]} h "
                        f"(> 3-sigma above median)"
                    )

    # ── Mass balance check ───────────────────────────────────────────────────
    # If we have composition data, Mn+W+Ca+Ti contributions should track fractions
    total_elements = D_Mn + D_W + D_Ca + D_Ti
    if composition and np.any(total_elements > 0):
        nonzero = total_elements > 0
        Mn_fraction = np.mean(D_Mn[nonzero] / total_elements[nonzero])
        if "Mn" in composition:
            expected = composition.get("Mn", 0)
            if abs(Mn_fraction - expected) > 0.35:
                warn_list.append(
                    f"Mass balance: measured Mn fraction {Mn_fraction:.2f} "
                    f"deviates from expected {expected:.2f}. "
                    f"Check ICP calibration or composition assignment."
                )

    # ── Assemble DataFrame ───────────────────────────────────────────────────
    df = pd.DataFrame({
        "t_h":              t_h_arr,
        "D_Mn_ug_cm2_h":    D_Mn,
        "D_W_ug_cm2_h":     D_W,
        "D_Ca_ug_cm2_h":    D_Ca,
        "D_Ti_ug_cm2_h":    D_Ti,
        "D_total_ug_cm2_h": D_total,
        "V_ml":             V_ml_arr,
        "area_cm2":         area_arr,
    })

    # ── Fit power law to D_total ─────────────────────────────────────────────
    D0, alpha, pcov = _fit_power_law(df["t_h"].values, df["D_total_ug_cm2_h"].values)
    sigmas = np.sqrt(np.diag(pcov)) if pcov.any() else np.zeros(2)

    # R² for fitted power law on the tail
    mask_tail = df["t_h"] >= max(3.0, df["t_h"].min())
    if mask_tail.sum() >= 3:
        D_pred = _power_law(df.loc[mask_tail, "t_h"].values, D0, alpha)
        D_obs  = df.loc[mask_tail, "D_total_ug_cm2_h"].values
        ss_res = np.sum((D_obs - D_pred) ** 2)
        ss_tot = np.sum((D_obs - np.mean(D_obs)) ** 2)
        r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else float("nan")
    else:
        r2 = float("nan")

    fit_result = {
        "D0":          round(D0, 4),
        "alpha":       round(alpha, 4),
        "D0_sigma":    round(float(sigmas[0]), 4) if len(sigmas) > 0 else float("nan"),
        "alpha_sigma": round(float(sigmas[1]), 4) if len(sigmas) > 1 else float("nan"),
        "r_squared":   round(float(r2), 4),
    }

    return {
        "sample_id":   sample_id,
        "composition": composition,
        "data":        df,
        "fit":         fit_result,
        "warnings":    warn_list,
        "metadata":    metadata,
    }


# ─── 2. OER polarisation curve ingestion ─────────────────────────────────────

def ingest_oer_curve(csv_path: str) -> dict:
    """
    Ingest an OER polarisation curve CSV and extract key electrochemical metrics.

    Expected CSV format:
    - Optional comment lines starting with '#' (parsed for metadata)
    - Header: E_v_rhe, j_ma_cm2
    - Values: potential in V vs RHE, current density in mA/cm²

    Convention: anodic currents are positive; negative values at low potential
    indicate capacitive background or residual cathodic processes and are
    excluded from Tafel analysis.

    Computed metrics
    ----------------
    eta_10_mv : float
        Overpotential at j = 10 mA/cm² (mV).  η = E - 1.23 V.
        Determined by linear interpolation between adjacent data points.
    tafel_slope_mvdec : float
        Tafel slope from a linear fit of E vs log10(j) in the kinetic region
        1–10 mA/cm².
    j_at_1p5v : float
        Current density at E = 1.50 V vs RHE (mA/cm²), by interpolation.
    onset_potential_v : float
        Potential at which j first exceeds 0.1 mA/cm² (onset of OER activity).

    Parameters
    ----------
    csv_path : str
        Path to the OER polarisation CSV.

    Returns
    -------
    dict with keys:
        'sample_id' : str
        'metrics' : dict  — eta_10_mv, tafel_slope_mvdec, j_at_1p5v,
                             onset_potential_v
        'data' : pd.DataFrame  — E_v_rhe, j_ma_cm2
        'warnings' : list[str]
        'metadata' : dict
    """
    csv_path = str(csv_path)
    warn_list: list[str] = []
    metadata: dict = {"source_file": csv_path, "ingested_at": datetime.utcnow().isoformat()}

    header_lines: list[str] = []
    data_lines:   list[str] = []

    with open(csv_path, "r", encoding="utf-8-sig") as fh:
        for line in fh:
            stripped = line.strip()
            if stripped.startswith("#"):
                header_lines.append(stripped)
            elif stripped:
                data_lines.append(stripped)

    sample_id = "UNKNOWN"
    for hline in header_lines:
        m = re.search(r"Sample:\s*(.+)", hline, re.IGNORECASE)
        if m:
            sample_id = m.group(1).strip()
        m = re.search(r"(Electrolyte|Scan rate|RDE):\s*(.+)", hline, re.IGNORECASE)
        if m:
            metadata[m.group(1).lower().replace(" ", "_")] = m.group(2).strip()

    reader = csv.DictReader(io.StringIO("\n".join(data_lines)))
    rows = [{k.strip(): v.strip() for k, v in r.items() if k} for r in reader]

    if not rows:
        raise ValueError(f"No data rows found in {csv_path}")

    required = {"E_v_rhe", "j_ma_cm2"}
    if not required.issubset(rows[0].keys()):
        raise ValueError(f"Expected columns {required}, found {set(rows[0].keys())}")

    E_arr = np.array([float(r["E_v_rhe"]) for r in rows])
    j_arr = np.array([float(r["j_ma_cm2"]) for r in rows])

    # Ensure sorted by potential (ascending)
    order = np.argsort(E_arr)
    E_arr = E_arr[order]
    j_arr = j_arr[order]

    df = pd.DataFrame({"E_v_rhe": E_arr, "j_ma_cm2": j_arr})

    # ── η₁₀: overpotential at j = 10 mA/cm² ─────────────────────────────────
    OER_EQUIL_V = 1.23  # V vs RHE (standard hydrogen electrode correction)
    J_TARGET    = 10.0  # mA/cm²

    eta_10_mv = float("nan")
    if np.any(j_arr >= J_TARGET):
        idx_above = np.argmax(j_arr >= J_TARGET)
        if idx_above > 0:
            # Linear interpolation between the two bracketing points
            j1, j2 = j_arr[idx_above - 1], j_arr[idx_above]
            E1, E2 = E_arr[idx_above - 1], E_arr[idx_above]
            if j2 > j1:
                E_at_j10 = E1 + (J_TARGET - j1) / (j2 - j1) * (E2 - E1)
                eta_10_mv = (E_at_j10 - OER_EQUIL_V) * 1000.0
        else:
            # First point is already above 10 mA/cm²
            eta_10_mv = (E_arr[0] - OER_EQUIL_V) * 1000.0
    else:
        warn_list.append("j never reaches 10 mA/cm² in scan — η₁₀ cannot be determined.")

    # ── Tafel slope: linear fit of E vs log10(j) in 1–10 mA/cm² range ───────
    tafel_mask = (j_arr >= 1.0) & (j_arr <= 10.0)
    tafel_slope_mvdec = float("nan")

    if tafel_mask.sum() >= 3:
        log_j = np.log10(j_arr[tafel_mask])
        E_tafel = E_arr[tafel_mask]
        coeffs = np.polyfit(log_j, E_tafel, 1)
        tafel_slope_mvdec = float(coeffs[0]) * 1000.0  # V/dec → mV/dec
    else:
        warn_list.append(
            f"Fewer than 3 data points in 1–10 mA/cm² range "
            f"({tafel_mask.sum()} found) — Tafel slope not computed."
        )

    # ── j at 1.50 V vs RHE ───────────────────────────────────────────────────
    j_at_1p5v = float("nan")
    if np.any(E_arr >= 1.50):
        idx_above = np.argmax(E_arr >= 1.50)
        if idx_above > 0:
            E1, E2 = E_arr[idx_above - 1], E_arr[idx_above]
            j1, j2 = j_arr[idx_above - 1], j_arr[idx_above]
            j_at_1p5v = j1 + (1.50 - E1) / (E2 - E1) * (j2 - j1)
        else:
            j_at_1p5v = j_arr[0]
    else:
        warn_list.append("Scan does not reach 1.50 V vs RHE — j@1.5V not computed.")

    # ── Onset potential: first point where j > 0.1 mA/cm² ───────────────────
    onset_mask = j_arr > 0.1
    onset_potential_v = float(E_arr[np.argmax(onset_mask)]) if onset_mask.any() else float("nan")

    # ── Sanity checks ────────────────────────────────────────────────────────
    if not np.isnan(eta_10_mv) and (eta_10_mv < 150 or eta_10_mv > 800):
        warn_list.append(
            f"η₁₀ = {eta_10_mv:.0f} mV is outside the expected 150–800 mV range. "
            f"Check potential calibration (RHE correction) or current normalisation."
        )
    if not np.isnan(tafel_slope_mvdec) and (tafel_slope_mvdec < 30 or tafel_slope_mvdec > 200):
        warn_list.append(
            f"Tafel slope = {tafel_slope_mvdec:.1f} mV/dec is outside the typical 30–200 mV/dec range."
        )

    return {
        "sample_id": sample_id,
        "metrics": {
            "eta_10_mv":         round(eta_10_mv, 1) if not np.isnan(eta_10_mv) else None,
            "tafel_slope_mvdec": round(tafel_slope_mvdec, 1) if not np.isnan(tafel_slope_mvdec) else None,
            "j_at_1p5v":         round(j_at_1p5v, 2) if not np.isnan(j_at_1p5v) else None,
            "onset_potential_v": round(onset_potential_v, 3) if not np.isnan(onset_potential_v) else None,
        },
        "data":     df,
        "warnings": warn_list,
        "metadata": metadata,
    }


# ─── 3. Gate JSON ingestion ───────────────────────────────────────────────────

# Schema: minimum required keys at each level
_GATE_JSON_REQUIRED_TOP = {"sample_id", "composition", "oer"}
_GATE_JSON_REQUIRED_OER = {"eta_10_mv"}
_GATE_JSON_OPTIONAL     = {"characterisation", "synthesis", "dissolution_500h"}


def ingest_gate_json(json_path: str) -> dict:
    """
    Ingest a gate data JSON file and validate it against the expected schema.

    The JSON format follows the programmatic lab integration schema (Format C in
    the project specification).  All fields that the ML training pipeline and
    Gate 3 projector require are checked; missing optional measurements are noted
    but do not raise exceptions.

    Parameters
    ----------
    json_path : str
        Path to the gate data JSON file.

    Returns
    -------
    dict with keys:
        'sample_id' : str
        'composition' : dict[str, float]
        'synthesis' : dict (or {})
        'characterisation' : dict (or {})
        'oer' : dict  — at minimum {'eta_10_mv': float}
        'dissolution_500h' : list[dict]  — [{t_h, D_total_ug_cm2_h}, ...]
        'warnings' : list[str]
        'metadata' : dict
    """
    json_path = str(json_path)
    warn_list: list[str] = []

    with open(json_path, "r", encoding="utf-8") as fh:
        raw = json.load(fh)

    # ── Top-level required keys ───────────────────────────────────────────────
    missing_top = _GATE_JSON_REQUIRED_TOP - set(raw.keys())
    if missing_top:
        raise ValueError(f"Gate JSON missing required keys: {missing_top}")

    # ── Composition validation ────────────────────────────────────────────────
    comp = raw["composition"]
    total_comp = sum(comp.values())
    if abs(total_comp - 1.0) > 0.05:
        warn_list.append(
            f"Composition fractions sum to {total_comp:.3f} (expected 1.0 ± 0.05). "
            f"Values will be normalised."
        )
        comp = {el: v / total_comp for el, v in comp.items()}

    # ── OER metrics ───────────────────────────────────────────────────────────
    oer = raw.get("oer", {})
    missing_oer = _GATE_JSON_REQUIRED_OER - set(oer.keys())
    if missing_oer:
        warn_list.append(f"OER section missing: {missing_oer}")

    # ── Characterisation fields ───────────────────────────────────────────────
    char = raw.get("characterisation", {})
    for field in ["xrd_cawо4_peak_present", "raman_921_peak", "bet_m2g", "xps_mn3_fraction"]:
        if field not in char:
            warn_list.append(f"Characterisation: '{field}' not present.")

    # ── Dissolution time series ───────────────────────────────────────────────
    diss = raw.get("dissolution_500h", [])
    if not diss:
        warn_list.append("No dissolution_500h time series in gate JSON.")
    else:
        for entry in diss:
            if "t_h" not in entry or "D_total_ug_cm2_h" not in entry:
                warn_list.append(
                    f"Dissolution entry missing t_h or D_total_ug_cm2_h: {entry}"
                )

    return {
        "sample_id":       raw["sample_id"],
        "composition":     comp,
        "synthesis":       raw.get("synthesis", {}),
        "characterisation": char,
        "oer":             oer,
        "dissolution_500h": diss,
        "warnings":        warn_list,
        "metadata": {
            "source_file":  json_path,
            "ingested_at":  datetime.utcnow().isoformat(),
        },
    }


# ─── 4. ML dataset update ─────────────────────────────────────────────────────

def update_ml_dataset(
    new_entry: dict,
    dataset_path: str = "stability_ml_dataset.csv",
) -> pd.DataFrame:
    """
    Append a new real-data catalyst entry to the running ML training dataset.

    The dataset CSV uses the same schema as stability_ml.py: each row is one
    catalyst characterisation, with both measured and computed features.

    New entries are assigned the next available sequential ID (O060, O061, …).
    If the CSV does not yet exist it is created with a full header.

    Feature mapping
    ---------------
    Measured directly:
        eta_10_mv, tafel_slope_mvdec, stability_h (from dissolution data)

    Derived from composition using Hammer–Norskov / Pourbaix tables:
        dissolution_potential_v  — composition-weighted Pourbaix potentials
        d_band_center_ev         — Hammer–Norskov table
        eg_electrons             — from XPS Mn3+ fraction if available, else table
        mo_bond_energy_ev        — linear scaling from d-band

    From characterisation:
        surface_area_m2g, acid_stable_score (inferred from D_total)

    Parameters
    ----------
    new_entry : dict
        A dict produced by combining ingest_icpms, ingest_oer_curve, and
        (optionally) ingest_gate_json outputs.  Expected keys:
            'sample_id', 'composition', 'oer', 'dissolution_result',
            'characterisation' (optional)

    dataset_path : str
        Path to the running dataset CSV.  Created if absent.

    Returns
    -------
    pd.DataFrame
        Full updated dataset (including the new row).
    """
    dataset_path = str(dataset_path)

    # ── Determine next ID ─────────────────────────────────────────────────────
    if os.path.exists(dataset_path):
        existing = pd.read_csv(dataset_path)
        oid_nums = []
        for oid in existing.get("id", pd.Series(dtype=str)):
            m = re.match(r"O(\d+)", str(oid))
            if m:
                oid_nums.append(int(m.group(1)))
        next_num = max(oid_nums) + 1 if oid_nums else 60
    else:
        existing = None
        next_num = 60

    new_id = f"O{next_num:03d}"

    # ── Composition → physical features ──────────────────────────────────────
    comp = new_entry.get("composition", {})
    if not comp:
        raise ValueError("new_entry must contain a non-empty 'composition' dict.")

    elements   = list(comp.keys())
    fractions  = np.array(list(comp.values()), dtype=float)
    fractions  = fractions / fractions.sum()

    dband_vals  = np.array([DBAND_CENTER_EV.get(el, -2.0) for el in elements])
    ediss_vals  = np.array([DISSOLUTION_POTENTIAL_V.get(el, 0.5) for el in elements])
    eg_vals     = np.array([EG_ELECTRONS.get(el, 0.5) for el in elements])

    d_band_center       = float(np.dot(fractions, dband_vals))
    dissolution_pot     = float(np.dot(fractions, ediss_vals))
    eg_electrons_comp   = float(np.dot(fractions, eg_vals))
    mo_bond_energy      = _mo_bond_energy(d_band_center)

    # If XPS Mn3+ fraction available, override eg_electrons
    char = new_entry.get("characterisation", {})
    xps_mn3 = char.get("xps_mn3_fraction")
    if xps_mn3 is not None:
        # Mn3+ eg occupancy: Mn3+ has 1 eg electron (t2g³eg¹, d4 high-spin)
        # Mn4+ has 0 eg electrons (t2g³, d3)
        # Weighted by Mn fraction and Mn3+/Mn4+ split
        mn_frac = comp.get("Mn", 0.0)
        eg_from_xps = mn_frac * (float(xps_mn3) * 1.0 + (1.0 - float(xps_mn3)) * 0.0)
        # Blend with other elements' contributions
        non_mn_eg = sum(
            fractions[i] * EG_ELECTRONS.get(el, 0.5)
            for i, el in enumerate(elements)
            if el != "Mn"
        )
        eg_electrons_comp = eg_from_xps + non_mn_eg

    # ── Extract measured values ───────────────────────────────────────────────
    oer = new_entry.get("oer", {})
    eta_10     = oer.get("eta_10_mv")
    tafel      = oer.get("tafel_slope_mvdec")
    bet_m2g    = char.get("bet_m2g", None)

    # Stability estimate: from dissolution_result if present
    diss_result = new_entry.get("dissolution_result", {})
    D0_real     = diss_result.get("D0")
    alpha_real  = diss_result.get("alpha")

    # Projected stability from power law: time to reach D_total < 0.1 µg/cm²/h
    stability_h = None
    if D0_real and alpha_real:
        # Time at which D(t) = GATE3_STEADY_UG_H
        # D0 × t^(-alpha) = D_ss  →  t = (D0 / D_ss)^(1/alpha)
        if alpha_real > 0:
            stability_h = (D0_real / GATE3_STEADY_UG_H) ** (1.0 / alpha_real)
            stability_h = round(float(stability_h), 0)

    # Acid stable score: infer from cumulative dissolution at 500 h
    acid_stable_score = 1  # unknown — conservative
    cum_data = new_entry.get("dissolution_result", {}).get("cum_500h")
    if cum_data is not None:
        if cum_data < GATE3_CUMULATIVE_UG:
            acid_stable_score = 3  # passes Gate 3
        elif cum_data < GATE3_CUMULATIVE_UG * 2:
            acid_stable_score = 2
        else:
            acid_stable_score = 1

    # Composition flags
    has_mn = int("Mn" in comp and comp["Mn"] > 0.01)
    has_cr = int("Cr" in comp and comp["Cr"] > 0.01)
    n_metals = len([el for el, f in comp.items() if f > 0.01])
    dominant_metal = max(comp, key=lambda el: comp[el]) if comp else "Mn"

    # ── Assemble new row ──────────────────────────────────────────────────────
    new_row = {
        "id":                   new_id,
        "name":                 new_entry.get("sample_id", new_id) + " (real)",
        "reaction":             "OER",
        "electrolyte":          "acid",
        "eta_10_mv":            eta_10,
        "tafel_slope":          tafel,
        "stability_h":          stability_h,
        "dissolution_potential_v": round(dissolution_pot, 3),
        "mo_bond_energy_ev":    round(mo_bond_energy, 3),
        "mh_bond_energy_ev":    None,
        "d_band_center_ev":     round(d_band_center, 3),
        "eg_electrons":         round(eg_electrons_comp, 3),
        "dominant_metal":       dominant_metal,
        "crystal_class":        "HEO",
        "acid_stable_score":    acid_stable_score,
        "n_metals":             n_metals,
        "has_cr":               has_cr,
        "has_mn":               has_mn,
        "coordination":         6,
        "surface_area_m2g":     bet_m2g,
        "source":               "real_experimental",
        "D0_fit":               D0_real,
        "alpha_fit":            alpha_real,
    }

    new_df = pd.DataFrame([new_row])

    if existing is not None:
        updated = pd.concat([existing, new_df], ignore_index=True)
    else:
        updated = new_df

    updated.to_csv(dataset_path, index=False)

    print(f"  [update_ml_dataset] Appended {new_id} ({new_row['name']}) "
          f"→ {dataset_path}  ({len(updated)} total rows)")

    return updated


# ─── 5. Gate 3 model update ───────────────────────────────────────────────────

def update_gate3_model(
    icpms_df: pd.DataFrame,
    composition_name: str,
    composition: Optional[dict[str, float]] = None,
    output_dir: str = ".",
) -> dict:
    """
    Re-fit and re-project the Gate 3 lifetime model from real ICP-MS data.

    Runs the same project_lifetime logic as gate3_lifetime_projector.py but
    driven by real experimental dissolution data rather than simulation.
    Generates a comparison plot: simulated vs real dissolution curves.

    Parameters
    ----------
    icpms_df : pd.DataFrame
        Output of ingest_icpms()['data'] — must contain columns
        't_h' and 'D_total_ug_cm2_h'.
    composition_name : str
        Human-readable label for plots and reports.
    composition : dict[str, float], optional
        Cation fractions (used to generate simulated reference curve).
        If None, simulated curve is omitted from the comparison plot.
    output_dir : str
        Directory for output plot and CSV.

    Returns
    -------
    dict with keys:
        'D0_real'           : float
        'alpha_real'        : float
        'D0_model'          : float  (from Gate 3 simulation for same composition)
        'alpha_model'       : float
        'cum_500h_real'     : float  (µg/cm²)
        'cum_500h_model'    : float  (µg/cm²)
        'p50_lifetime_real' : float  (h)
        'p50_lifetime_model': float  (h)
        'gate3_pass_real'   : bool
        'plot_path'         : str
        'csv_path'          : str
    """
    os.makedirs(output_dir, exist_ok=True)

    t_real = icpms_df["t_h"].values.astype(float)
    D_real = icpms_df["D_total_ug_cm2_h"].values.astype(float)

    # ── Fit power law to real data ────────────────────────────────────────────
    D0_real, alpha_real, pcov_real = _fit_power_law(t_real, D_real, t_start=3.0)
    sigmas_real = np.sqrt(np.diag(pcov_real)) if pcov_real.any() else np.zeros(2)

    # Cumulative dissolution at 500 h from real data + extrapolation
    t_max_real = float(t_real.max())
    cum_measured = float(np.trapz(D_real, t_real))
    cum_500h_real = _cumulative_integral(D0_real, alpha_real, t_max_real, 500.0, cum_measured) \
                    if t_max_real < 500.0 else cum_measured

    # P50 lifetime
    p50_real = _project_p50_lifetime(
        D0_real, alpha_real, t_max_real, cum_measured
    )

    # Steady-state rate at end of real data
    D_ss_real = float(_power_law(np.array([max(t_max_real, 1.0)]), D0_real, alpha_real)[0])

    gate3_pass_real = (
        cum_500h_real <= GATE3_CUMULATIVE_UG
        and D_ss_real <= GATE3_STEADY_UG_H
        and p50_real >= GATE3_P50_LIFETIME_H
    )

    # ── Simulated reference (Gate 3 model) ────────────────────────────────────
    D0_model = alpha_model = cum_500h_model = p50_model = float("nan")

    if composition is not None:
        # Reconstruct Gate 3 phase fractions (same logic as gate3_lifetime_projector.py)
        x_ca = composition.get("Ca", 0.0)
        x_mn = composition.get("Mn", 0.55)
        x_w  = composition.get("W",  0.34)
        x_ti = composition.get("Ti", 0.002)
        total = x_ca + x_mn + x_w + x_ti
        if total > 0:
            x_ca, x_mn, x_w, x_ti = x_ca/total, x_mn/total, x_w/total, x_ti/total

        # CaWO4 fraction: limited by min(Ca, W)
        f_cawo4 = min(x_ca, x_w) * 0.85    # 85% conversion efficiency (Gate 1 estimate)
        D0_model, alpha_model = _gate3_model_params(x_mn, x_w, x_ca, x_ti, f_cawo4)
        cum_500h_model = _cumulative_integral(D0_model, alpha_model, 1.0, 500.0)
        p50_model = _project_p50_lifetime(D0_model, alpha_model, 1.0, 0.0)

    # ── Comparison plot ───────────────────────────────────────────────────────
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    safe_name = re.sub(r"[^\w]", "_", composition_name)[:40]

    t_proj = np.geomspace(max(t_real.min(), 0.5), max(2000.0, t_real.max() * 4), 400)
    D_fit_curve = _power_law(t_proj, D0_real, alpha_real)

    ax = axes[0]
    ax.semilogy(t_real, D_real, "o", color="#e74c3c", ms=8, zorder=5, label="Real ICP-MS data")
    ax.semilogy(t_proj, D_fit_curve, "-", color="#e74c3c", lw=2,
                label=f"Real fit: D₀={D0_real:.2f}, α={alpha_real:.3f}")
    if not np.isnan(D0_model):
        D_model_curve = _power_law(t_proj, D0_model, alpha_model)
        ax.semilogy(t_proj, D_model_curve, "--", color="#3498db", lw=2,
                    label=f"Gate3 model: D₀={D0_model:.2f}, α={alpha_model:.3f}")
    ax.axhline(GATE3_STEADY_UG_H, color="purple", ls=":", lw=1.5,
               label=f"Gate3 D_ss limit ({GATE3_STEADY_UG_H} µg/cm²/h)")
    ax.set_xlabel("Time (h)")
    ax.set_ylabel("Dissolution rate (µg/cm²/h)")
    ax.set_title(f"Dissolution rate: real vs model\n{composition_name}")
    ax.legend(fontsize=8)

    # Cumulative panel
    ax2 = axes[1]
    cum_real_arr = np.zeros(len(t_proj))
    for i, tp in enumerate(t_proj):
        if tp <= t_max_real:
            # Use trapezoidal integration over real data up to this point
            mask = t_real <= tp
            cum_real_arr[i] = float(np.trapz(D_real[mask], t_real[mask])) if mask.sum() > 1 else 0.0
        else:
            cum_real_arr[i] = _cumulative_integral(D0_real, alpha_real, t_max_real, tp, cum_measured)

    ax2.plot(t_proj, cum_real_arr, "-", color="#e74c3c", lw=2, label="Real (measured + extrapolated)")
    if not np.isnan(D0_model):
        cum_model_arr = np.array([_cumulative_integral(D0_model, alpha_model, 1.0, tp) for tp in t_proj])
        ax2.plot(t_proj, cum_model_arr, "--", color="#3498db", lw=2, label="Gate3 model")
    ax2.axvline(500, color="black", ls="--", lw=1, alpha=0.7, label="500 h mark")
    ax2.axhline(GATE3_CUMULATIVE_UG, color="purple", ls=":", lw=1.5,
                label=f"Gate3 limit ({GATE3_CUMULATIVE_UG} µg/cm²)")
    ax2.axhline(LOADING_UG_CM2 * 0.5, color="orange", ls="--", lw=1.5,
                label=f"P50 trigger ({LOADING_UG_CM2 * 0.5:.0f} µg/cm²)")
    ax2.set_xlabel("Time (h)")
    ax2.set_ylabel("Cumulative dissolution (µg/cm²)")
    ax2.set_title(f"Cumulative dissolution: real vs model\n{composition_name}")
    ax2.legend(fontsize=8)

    status = "PASS" if gate3_pass_real else "FAIL"
    fig.suptitle(f"Gate 3 Real-Data Update — {composition_name}  [{status}]",
                 fontsize=11, fontweight="bold")
    plt.tight_layout()

    plot_path = os.path.join(output_dir, f"gate3_realdata_{safe_name}.png")
    plt.savefig(plot_path, dpi=150, bbox_inches="tight")
    plt.close(fig)

    # ── Summary CSV ──────────────────────────────────────────────────────────
    summary_df = pd.DataFrame([{
        "composition":       composition_name,
        "D0_real":           round(D0_real, 4),
        "alpha_real":        round(alpha_real, 4),
        "D0_sigma":          round(float(sigmas_real[0]), 4) if sigmas_real.any() else None,
        "alpha_sigma":       round(float(sigmas_real[1]), 4) if sigmas_real.any() else None,
        "D0_model":          round(D0_model, 4) if not np.isnan(D0_model) else None,
        "alpha_model":       round(alpha_model, 4) if not np.isnan(alpha_model) else None,
        "cum_500h_real":     round(cum_500h_real, 2),
        "cum_500h_model":    round(cum_500h_model, 2) if not np.isnan(cum_500h_model) else None,
        "p50_lifetime_real": round(p50_real, 0),
        "p50_lifetime_model": round(p50_model, 0) if not np.isnan(p50_model) else None,
        "D_ss_real":         round(D_ss_real, 4),
        "gate3_pass_real":   gate3_pass_real,
        "ingested_at":       datetime.utcnow().isoformat(),
    }])
    csv_out_path = os.path.join(output_dir, f"gate3_realdata_{safe_name}.csv")
    summary_df.to_csv(csv_out_path, index=False)

    result = {
        "D0_real":            D0_real,
        "alpha_real":         alpha_real,
        "D0_model":           D0_model,
        "alpha_model":        alpha_model,
        "cum_500h_real":      cum_500h_real,
        "cum_500h_model":     cum_500h_model,
        "p50_lifetime_real":  p50_real,
        "p50_lifetime_model": p50_model,
        "D_ss_real":          D_ss_real,
        "gate3_pass_real":    gate3_pass_real,
        "plot_path":          plot_path,
        "csv_path":           csv_out_path,
    }

    return result


def _gate3_model_params(
    x_mn: float,
    x_w: float,
    x_ca: float,
    x_ti: float,
    f_cawo4: float,
) -> tuple[float, float]:
    """
    Compute Gate 3 model D0 and alpha for a given composition without
    running the full ODE integration.

    Uses a composition-weighted average of the PHASE_PARAMS constants,
    matching the simplified model used in gate3_lifetime_projector.py.

    Returns (D0_model, alpha_model).
    """
    f_mno2 = x_mn
    f_wo3  = max(0.0, x_w - f_cawo4)
    f_tio2 = x_ti
    total  = f_mno2 + f_wo3 + f_cawo4 + f_tio2
    if total < 1e-9:
        return 1.0, 0.40

    weights = {
        "MnO2":  f_mno2 / total,
        "WO3":   f_wo3  / total,
        "CaWO4": f_cawo4 / total,
        "TiO2":  f_tio2  / total,
    }

    D0_model    = sum(w * PHASE_PARAMS[ph][0] for ph, w in weights.items())
    alpha_model = sum(w * PHASE_PARAMS[ph][1] for ph, w in weights.items())
    return float(D0_model), float(alpha_model)


# ─── 6. Auto-detecting pipeline ───────────────────────────────────────────────

def run_ingestion_pipeline(
    data_dir: str,
    composition: Optional[dict[str, float]] = None,
    dataset_path: str = "stability_ml_dataset.csv",
    output_dir: Optional[str] = None,
) -> dict:
    """
    Main ingestion pipeline: scan a directory for lab data files, auto-detect
    formats, ingest all files, and update the ML dataset and Gate 3 model.

    Supported file types:
    - ICP-MS CSV: recognised by columns t_h, Mn_ppb, W_ppb in header
    - OER polarisation CSV: recognised by columns E_v_rhe, j_ma_cm2 in header
    - Gate JSON: *.json files

    Parameters
    ----------
    data_dir : str
        Directory to scan for data files.
    composition : dict[str, float], optional
        Cation fractions for the batch.  If None, composition is parsed from
        file comments / JSON content.
    dataset_path : str
        Path to the ML training dataset CSV.
    output_dir : str, optional
        Directory for output plots and reports.  Defaults to data_dir.

    Returns
    -------
    dict with keys:
        'icpms_results'  : list[dict]
        'oer_results'    : list[dict]
        'json_results'   : list[dict]
        'ml_dataset'     : pd.DataFrame
        'gate3_updates'  : list[dict]
        'summary'        : str
    """
    data_dir   = str(data_dir)
    output_dir = output_dir or data_dir

    icpms_results: list[dict]  = []
    oer_results:   list[dict]  = []
    json_results:  list[dict]  = []
    gate3_updates: list[dict]  = []
    ml_dataset     = None

    all_files = sorted(Path(data_dir).glob("*"))

    for fpath in all_files:
        name = fpath.name.lower()

        if name.endswith(".json"):
            print(f"  [pipeline] JSON: {fpath.name}")
            try:
                result = ingest_gate_json(str(fpath))
                json_results.append(result)
                if result["warnings"]:
                    for w in result["warnings"]:
                        print(f"    WARNING: {w}")
            except Exception as exc:
                print(f"    ERROR ingesting {fpath.name}: {exc}")
            continue

        if not name.endswith(".csv"):
            continue

        # Peek at first non-comment line to detect format
        with open(str(fpath), "r", encoding="utf-8-sig") as fh:
            lines = [ln.strip() for ln in fh if not ln.strip().startswith("#")]
        if not lines:
            continue

        header = lines[0].lower()

        if "mn_ppb" in header or "w_ppb" in header:
            print(f"  [pipeline] ICP-MS: {fpath.name}")
            try:
                result = ingest_icpms(str(fpath), composition=composition)
                icpms_results.append(result)
                if result["warnings"]:
                    for w in result["warnings"]:
                        print(f"    WARNING: {w}")

                # Build entry for ML dataset
                comp = result["composition"] or composition or {}
                diss_result = {
                    "D0":       result["fit"]["D0"],
                    "alpha":    result["fit"]["alpha"],
                    "cum_500h": None,
                }
                ml_entry = {
                    "sample_id":         result["sample_id"],
                    "composition":       comp,
                    "oer":               {},     # will be merged from OER file if found
                    "dissolution_result": diss_result,
                    "characterisation":  {},
                }
                ml_dataset = update_ml_dataset(ml_entry, dataset_path)

                # Gate 3 model update
                g3 = update_gate3_model(
                    result["data"],
                    result["sample_id"],
                    composition=comp,
                    output_dir=output_dir,
                )
                gate3_updates.append(g3)
            except Exception as exc:
                print(f"    ERROR ingesting {fpath.name}: {exc}")

        elif "e_v_rhe" in header or "j_ma_cm2" in header:
            print(f"  [pipeline] OER curve: {fpath.name}")
            try:
                result = ingest_oer_curve(str(fpath))
                oer_results.append(result)
                if result["warnings"]:
                    for w in result["warnings"]:
                        print(f"    WARNING: {w}")
            except Exception as exc:
                print(f"    ERROR ingesting {fpath.name}: {exc}")

        else:
            print(f"  [pipeline] Unrecognised CSV format, skipping: {fpath.name}")

    # ── Summary ───────────────────────────────────────────────────────────────
    summary_lines = [
        f"Ingestion pipeline complete — {data_dir}",
        f"  ICP-MS files:     {len(icpms_results)}",
        f"  OER curve files:  {len(oer_results)}",
        f"  Gate JSON files:  {len(json_results)}",
        f"  Gate3 updates:    {len(gate3_updates)}",
    ]
    if ml_dataset is not None:
        summary_lines.append(f"  ML dataset rows:  {len(ml_dataset)}")

    summary = "\n".join(summary_lines)
    print("\n" + summary)

    return {
        "icpms_results":  icpms_results,
        "oer_results":    oer_results,
        "json_results":   json_results,
        "ml_dataset":     ml_dataset,
        "gate3_updates":  gate3_updates,
        "summary":        summary,
    }


# ─── 7. Lab report generator ─────────────────────────────────────────────────

def generate_lab_report(
    sample_id: str,
    composition: dict[str, float],
    results: dict,
    output_path: str,
) -> str:
    """
    Generate a plain-text + CSV summary suitable for a lab notebook entry.

    The report includes:
    - Sample identity and composition
    - Measured dissolution kinetics (D0, alpha, R²)
    - Computed cumulative dissolution at 500 h
    - Projected P50 lifetime
    - Gate 3 pass/fail verdict
    - Comparison to model predictions
    - Recommended next steps (conditional on gate outcome)

    Parameters
    ----------
    sample_id : str
        Sample identifier.
    composition : dict[str, float]
        Cation fractions.
    results : dict
        Dict as returned by update_gate3_model().
    output_path : str
        Path for the plain-text report.  A companion CSV is written at
        output_path.replace('.txt', '.csv').

    Returns
    -------
    str
        The full report text (also written to output_path).
    """
    comp_str = "  ".join(f"{el}({frac:.3f})" for el, frac in composition.items())
    now_str  = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")

    D0_r    = results.get("D0_real",   float("nan"))
    al_r    = results.get("alpha_real", float("nan"))
    D0_m    = results.get("D0_model",  float("nan"))
    al_m    = results.get("alpha_model", float("nan"))
    cum_r   = results.get("cum_500h_real",  float("nan"))
    cum_m   = results.get("cum_500h_model", float("nan"))
    p50_r   = results.get("p50_lifetime_real",  float("nan"))
    p50_m   = results.get("p50_lifetime_model", float("nan"))
    D_ss_r  = results.get("D_ss_real", float("nan"))
    passed  = results.get("gate3_pass_real", False)

    def _fmt(v, decimals=2):
        return f"{v:.{decimals}f}" if not (v is None or (isinstance(v, float) and np.isnan(v))) else "N/A"

    # Gate pass/fail reasons
    reasons: list[str] = []
    if cum_r > GATE3_CUMULATIVE_UG:
        reasons.append(f"Cumulative dissolution {_fmt(cum_r)} µg/cm² > limit {GATE3_CUMULATIVE_UG} µg/cm²")
    if D_ss_r > GATE3_STEADY_UG_H:
        reasons.append(f"Steady-state rate {_fmt(D_ss_r, 4)} µg/cm²/h > limit {GATE3_STEADY_UG_H} µg/cm²/h")
    if p50_r < GATE3_P50_LIFETIME_H:
        reasons.append(f"P50 lifetime {_fmt(p50_r, 0)} h < target {GATE3_P50_LIFETIME_H} h")

    # Recommended next steps
    next_steps: list[str] = []
    if not passed:
        if cum_r > GATE3_CUMULATIVE_UG:
            next_steps.append(
                "Increase CaWO4 fraction: raise Ca and W in synthesis (target f_CaWO4 > 0.10)."
            )
            next_steps.append(
                "Consider IrOx sub-monolayer passivation (0.05–0.10 µg Ir/cm²)."
            )
        if D_ss_r > GATE3_STEADY_UG_H:
            next_steps.append(
                "Increase Ti content (x_Ti → 0.20–0.25) for TiO2 matrix stabilisation."
            )
        if p50_r < GATE3_P50_LIFETIME_H:
            next_steps.append(
                "Switch to pulsed CP protocol (29 min on / 1 min OC) to extend lifetime."
            )
        next_steps.append(
            "Collect longer dissolution run (>100 h) to better constrain power-law alpha."
        )
    else:
        next_steps.append("Gate 3 PASSED. Proceed to full 500 h dissolution test.")
        next_steps.append("Prepare MEA integration sample for electrolyser testing.")
        next_steps.append("Run XPS post-dissolution to confirm CaWO4 enrichment mechanism.")

    lines = [
        "=" * 72,
        f"LAB REPORT — Gate 3 Dissolution Analysis",
        f"Generated: {now_str}",
        "=" * 72,
        "",
        f"Sample ID:    {sample_id}",
        f"Composition:  {comp_str}",
        "",
        "─" * 72,
        "DISSOLUTION KINETICS (Real ICP-MS Data)",
        "─" * 72,
        f"  Power-law fit:  D(t) = D0 × t^(−α)",
        f"  D0 (real):      {_fmt(D0_r, 4)} µg/cm²/h",
        f"  α  (real):      {_fmt(al_r, 4)}",
        f"  D0 (model):     {_fmt(D0_m, 4)} µg/cm²/h",
        f"  α  (model):     {_fmt(al_m, 4)}",
        "",
        "─" * 72,
        "GATE 3 PROJECTIONS",
        "─" * 72,
        f"  Cumulative dissolution @ 500 h (real):   {_fmt(cum_r, 2)} µg/cm²",
        f"  Cumulative dissolution @ 500 h (model):  {_fmt(cum_m, 2)} µg/cm²",
        f"  Gate 3 limit:                            {GATE3_CUMULATIVE_UG} µg/cm²",
        "",
        f"  Steady-state rate (real):   {_fmt(D_ss_r, 4)} µg/cm²/h",
        f"  Gate 3 limit:               {GATE3_STEADY_UG_H} µg/cm²/h",
        "",
        f"  P50 lifetime (real):    {_fmt(p50_r, 0)} h",
        f"  P50 lifetime (model):   {_fmt(p50_m, 0)} h",
        f"  Gate 3 target:          {GATE3_P50_LIFETIME_H} h",
        "",
        "─" * 72,
        f"GATE 3 VERDICT:  {'PASS' if passed else 'FAIL'}",
        "─" * 72,
    ]

    if not passed and reasons:
        lines += ["", "Fail reasons:"]
        for r in reasons:
            lines.append(f"  - {r}")

    lines += ["", "Recommended next steps:"]
    for i, step in enumerate(next_steps, 1):
        lines.append(f"  {i}. {step}")

    if results.get("plot_path"):
        lines += ["", f"Comparison plot saved: {results['plot_path']}"]
    if results.get("csv_path"):
        lines += [f"Summary CSV saved:     {results['csv_path']}"]

    lines.append("")
    lines.append("=" * 72)

    report_text = "\n".join(lines)

    with open(str(output_path), "w", encoding="utf-8") as fh:
        fh.write(report_text)

    # Companion CSV (key numbers only, for LIMS import)
    csv_path = str(output_path).replace(".txt", ".csv")
    csv_df = pd.DataFrame([{
        "sample_id":         sample_id,
        "composition":       comp_str,
        "D0_real":           round(D0_r, 4) if not np.isnan(D0_r) else None,
        "alpha_real":        round(al_r, 4) if not np.isnan(al_r) else None,
        "D0_model":          round(D0_m, 4) if not np.isnan(D0_m) else None,
        "alpha_model":       round(al_m, 4) if not np.isnan(al_m) else None,
        "cum_500h_real_ugcm2":   round(cum_r, 2) if not np.isnan(cum_r) else None,
        "cum_500h_model_ugcm2":  round(cum_m, 2) if not np.isnan(cum_m) else None,
        "p50_real_h":        round(p50_r, 0) if not np.isnan(p50_r) else None,
        "p50_model_h":       round(p50_m, 0) if not np.isnan(p50_m) else None,
        "gate3_pass":        passed,
        "generated_at":      now_str,
    }])
    csv_df.to_csv(csv_path, index=False)

    return report_text


# ─── Test / demo helpers ──────────────────────────────────────────────────────

def _make_synthetic_icpms_csv(
    path: str,
    composition: dict[str, float],
    noise_frac: float = 0.08,
    seed: int = 42,
) -> None:
    """
    Generate a synthetic ICP-MS CSV for Ca(0.11)Mn(0.55)W(0.34) (or any
    supplied composition) using the Gate 3 PHASE_PARAMS dissolution model.

    The file uses the same format as the Agilent 7800 export header so that
    ingest_icpms() can parse it without modification.

    Parameters
    ----------
    path : str
        Output file path.
    composition : dict[str, float]
        Cation fractions, e.g. {"Ca": 0.11, "Mn": 0.55, "W": 0.34}.
    noise_frac : float
        Fractional Gaussian noise added to each reading (σ / mean).
    seed : int
        Random seed for reproducibility.
    """
    rng = np.random.default_rng(seed)

    # Derive phase fractions from composition
    x_ca = composition.get("Ca", 0.0)
    x_mn = composition.get("Mn", 0.55)
    x_w  = composition.get("W",  0.34)
    x_ti = composition.get("Ti", 0.002)
    total = x_ca + x_mn + x_w + x_ti
    if total > 0:
        x_ca, x_mn, x_w, x_ti = x_ca/total, x_mn/total, x_w/total, x_ti/total

    f_cawo4 = min(x_ca, x_w) * 0.85
    f_wo3   = max(0.0, x_w - f_cawo4)

    # ICP-MS protocol: 59 min on / 1 min OC, measurements at these timepoints
    t_h_points = np.array([1.0, 3.0, 6.0, 12.0, 24.0, 48.0, 96.0])
    area_cm2   = 0.196   # standard 5 mm RDE
    V_ml       = 5.0     # eluate volume per measurement

    # D_total from PHASE_PARAMS (pulsed CP, fraction 0.5 factor)
    PULSED_FACTOR = 0.50
    rows = []
    for t in t_h_points:
        D_mn  = PHASE_PARAMS["MnO2"][0]  * x_mn   * t ** (-PHASE_PARAMS["MnO2"][1])  * PULSED_FACTOR
        D_w   = PHASE_PARAMS["WO3"][0]   * f_wo3   * t ** (-PHASE_PARAMS["WO3"][1])   * PULSED_FACTOR
        D_ca  = PHASE_PARAMS["CaWO4"][0] * f_cawo4 * t ** (-PHASE_PARAMS["CaWO4"][1]) * PULSED_FACTOR
        D_ti  = PHASE_PARAMS["TiO2"][0]  * x_ti    * t ** (-PHASE_PARAMS["TiO2"][1])  * PULSED_FACTOR

        # Convert µg/cm²/h → ppb using: ppb = D × area × dt × 1000 / V_ml
        # For an interval starting at the previous timepoint
        prev_t = t_h_points[t_h_points < t]
        dt_h = t - (float(prev_t[-1]) if len(prev_t) > 0 else 0.0)
        dt_h = max(dt_h, 0.1)

        def _to_ppb(D_rate: float) -> float:
            ug_dissolved = D_rate * area_cm2 * dt_h
            return (ug_dissolved * 1000.0 / V_ml) * (1.0 + rng.normal(0, noise_frac))

        rows.append({
            "t_h":     t,
            "Mn_ppb":  max(0.0, _to_ppb(D_mn)),
            "W_ppb":   max(0.0, _to_ppb(D_w)),
            "Ca_ppb":  max(0.0, _to_ppb(D_ca)),
            "Ti_ppb":  max(0.0, _to_ppb(D_ti)),
            "V_ml":    V_ml,
            "area_cm2": area_cm2,
        })

    # Format composition label for header
    comp_label = "".join(f"{el}({frac:.2f})" for el, frac in composition.items())

    with open(path, "w", newline="", encoding="utf-8") as fh:
        fh.write(f"# ICP-MS dissolution measurement\n")
        fh.write(f"# Instrument: Agilent 7800 ICP-MS (synthetic test data)\n")
        fh.write(f"# Sample: {comp_label}_pulsed_CP_synth\n")
        fh.write(f"# Date: {datetime.utcnow().strftime('%Y-%m-%d')}\n")
        fh.write(f"# Protocol: 59min on / 1min OC, 10 mA/cm2, 0.5M H2SO4\n")
        fh.write(f"# NOTE: Synthetic data generated by data_ingestion.py for testing\n")

        writer = csv.DictWriter(fh, fieldnames=["t_h", "Mn_ppb", "W_ppb", "Ca_ppb", "Ti_ppb", "V_ml", "area_cm2"])
        writer.writeheader()
        for row in rows:
            writer.writerow({k: round(v, 4) for k, v in row.items()})


def _make_synthetic_oer_csv(path: str, eta_10_mv: float = 268.0) -> None:
    """
    Generate a synthetic OER polarisation curve CSV for testing.

    Uses a Butler–Volmer–like current model:
        j(E) = j0 × exp((E - E_onset) / b)
    with b = Tafel slope / (ln(10) × 1000) in V and E in V vs RHE.

    Parameters
    ----------
    path : str
        Output path.
    eta_10_mv : float
        Target overpotential at j = 10 mA/cm² (mV).  Adjusts E_onset to match.
    """
    E_onset  = 1.23 + 0.08             # ~1.31 V vs RHE typical onset
    tafel_mv = 61.0                    # mV/dec
    b        = tafel_mv / (np.log(10) * 1000.0)   # V

    E_target_10 = 1.23 + eta_10_mv / 1000.0
    j0 = 10.0 * np.exp(-(E_target_10 - E_onset) / b)

    E_arr = np.linspace(1.20, 1.60, 50)
    j_arr = np.where(E_arr > E_onset, j0 * np.exp((E_arr - E_onset) / b), 0.0)
    j_arr += np.random.default_rng(99).normal(0, 0.03, len(j_arr))
    j_arr[j_arr < -0.5] = -0.5

    with open(path, "w", newline="", encoding="utf-8") as fh:
        fh.write("# OER polarisation curve\n")
        fh.write("# Sample: CaMnW_synth_annealed_160C (synthetic test data)\n")
        fh.write("# Electrolyte: 0.5M H2SO4, 25C, N2-purged\n")
        fh.write("# RDE: 1600 rpm, scan rate: 10 mV/s\n")
        writer = csv.DictWriter(fh, fieldnames=["E_v_rhe", "j_ma_cm2"])
        writer.writeheader()
        for E, j in zip(E_arr, j_arr):
            writer.writerow({"E_v_rhe": round(E, 4), "j_ma_cm2": round(j, 4)})


def _make_synthetic_gate_json(path: str, composition: dict[str, float]) -> None:
    """
    Generate a synthetic gate data JSON for testing ingest_gate_json().

    Parameters
    ----------
    path : str
        Output path.
    composition : dict[str, float]
        Cation fractions.
    """
    x_ca = composition.get("Ca", 0.11)
    x_mn = composition.get("Mn", 0.55)
    x_w  = composition.get("W", 0.34)
    x_ti = composition.get("Ti", 0.002)
    total = x_ca + x_mn + x_w + x_ti

    gate_data = {
        "sample_id": "CaMnW_001_synth",
        "composition": {
            el: round(frac / total, 4)
            for el, frac in [("Ca", x_ca), ("Mn", x_mn), ("W", x_w), ("Ti", x_ti)]
        },
        "synthesis": {
            "protocol": "P3",
            "pH": 8.0,
            "T_C": 80,
            "time_h": 4,
        },
        "characterisation": {
            "xrd_cawо4_peak_present": True,
            "xrd_28p7_intensity": 0.18,
            "raman_921_peak": True,
            "bet_m2g": 92.3,
            "xps_mn3_fraction": 0.48,
        },
        "oer": {
            "eta_10_mv": 268,
            "tafel_slope_mvdec": 61,
        },
        "dissolution_500h": [
            {"t_h": 1,   "D_total_ug_cm2_h": 4.2},
            {"t_h": 24,  "D_total_ug_cm2_h": 0.45},
            {"t_h": 100, "D_total_ug_cm2_h": 0.089},
            {"t_h": 500, "D_total_ug_cm2_h": 0.031},
        ],
    }

    with open(path, "w", encoding="utf-8") as fh:
        json.dump(gate_data, fh, indent=2)


# ─── Main: end-to-end demo with synthetic data ────────────────────────────────

if __name__ == "__main__":
    import tempfile

    # Ensure Unicode output works on Windows terminals (CP-1252 default)
    if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf8"):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

    np.random.seed(42)

    COMPOSITION = {"Ca": 0.11, "Mn": 0.55, "W": 0.34, "Ti": 0.002}
    COMPOSITION_NAME = "Ca(0.11)Mn(0.55)W(0.34)"

    print("=" * 72)
    print("data_ingestion.py — End-to-end demo with synthetic data")
    print(f"Composition: {COMPOSITION_NAME}")
    print("=" * 72)

    # Use a temporary directory so the demo leaves no residual files in cwd
    with tempfile.TemporaryDirectory() as tmpdir:

        # ── Step 1: Generate synthetic test files ─────────────────────────────
        icpms_csv_path = os.path.join(tmpdir, "icpms_CaMnW_synth.csv")
        oer_csv_path   = os.path.join(tmpdir, "oer_CaMnW_synth.csv")
        gate_json_path = os.path.join(tmpdir, "gate_CaMnW_synth.json")

        _make_synthetic_icpms_csv(icpms_csv_path, COMPOSITION)
        _make_synthetic_oer_csv(oer_csv_path, eta_10_mv=268.0)
        _make_synthetic_gate_json(gate_json_path, COMPOSITION)

        print("\n[1] Synthetic data files generated.")

        # ── Step 2: Ingest ICP-MS ─────────────────────────────────────────────
        print("\n[2] Ingesting ICP-MS dissolution data...")
        icpms_result = ingest_icpms(icpms_csv_path, composition=COMPOSITION)

        print(f"    Sample ID:  {icpms_result['sample_id']}")
        print(f"    Timepoints: {list(icpms_result['data']['t_h'].values)}")
        print(f"    D_total range: "
              f"{icpms_result['data']['D_total_ug_cm2_h'].min():.4f} – "
              f"{icpms_result['data']['D_total_ug_cm2_h'].max():.4f} µg/cm²/h")
        if icpms_result["warnings"]:
            for w in icpms_result["warnings"]:
                print(f"    WARNING: {w}")

        D0_real   = icpms_result["fit"]["D0"]
        alpha_real = icpms_result["fit"]["alpha"]
        r2_real    = icpms_result["fit"]["r_squared"]

        print(f"    Fitted power law: D(t) = {D0_real:.4f} × t^(−{alpha_real:.4f})")
        print(f"    R² of fit: {r2_real:.4f}")

        # ── Step 3: Ingest OER curve ──────────────────────────────────────────
        print("\n[3] Ingesting OER polarisation curve...")
        oer_result = ingest_oer_curve(oer_csv_path)

        m = oer_result["metrics"]
        print(f"    η₁₀:           {m['eta_10_mv']} mV")
        print(f"    Tafel slope:   {m['tafel_slope_mvdec']} mV/dec")
        print(f"    j @ 1.50 V:    {m['j_at_1p5v']} mA/cm²")
        print(f"    Onset pot.:    {m['onset_potential_v']} V vs RHE")
        if oer_result["warnings"]:
            for w in oer_result["warnings"]:
                print(f"    WARNING: {w}")

        # ── Step 4: Ingest gate JSON ──────────────────────────────────────────
        print("\n[4] Ingesting gate data JSON...")
        gate_result = ingest_gate_json(gate_json_path)

        print(f"    Sample ID:    {gate_result['sample_id']}")
        print(f"    Composition:  {gate_result['composition']}")
        print(f"    OER η₁₀:     {gate_result['oer'].get('eta_10_mv')} mV")
        print(f"    BET:          {gate_result['characterisation'].get('bet_m2g')} m²/g")
        print(f"    Dissolution timepoints: {len(gate_result['dissolution_500h'])}")
        if gate_result["warnings"]:
            for w in gate_result["warnings"]:
                print(f"    WARNING: {w}")

        # ── Step 5: Gate 3 model comparison ──────────────────────────────────
        print("\n[5] Updating Gate 3 model with real data...")
        g3 = update_gate3_model(
            icpms_result["data"],
            COMPOSITION_NAME,
            composition=COMPOSITION,
            output_dir=tmpdir,
        )

        print(f"\n    {'Quantity':<35} {'Real':>12}  {'Model':>12}")
        print(f"    {'-'*61}")
        print(f"    {'D0 (µg/cm²/h)':<35} {g3['D0_real']:>12.4f}  {g3['D0_model']:>12.4f}")
        print(f"    {'alpha (dimensionless)':<35} {g3['alpha_real']:>12.4f}  {g3['alpha_model']:>12.4f}")
        print(f"    {'Cumulative dissolution @ 500h (µg/cm²)':<35} {g3['cum_500h_real']:>12.2f}  {g3['cum_500h_model']:>12.2f}")
        print(f"    {'P50 lifetime (h)':<35} {g3['p50_lifetime_real']:>12.0f}  {g3['p50_lifetime_model']:>12.0f}")
        print(f"    {'Steady-state rate (µg/cm²/h)':<35} {g3['D_ss_real']:>12.4f}  {'(see model)':>12}")
        print(f"\n    Gate 3 verdict (real data): {'PASS' if g3['gate3_pass_real'] else 'FAIL'}")
        print(f"    Plot:  {g3['plot_path']}")
        print(f"    CSV:   {g3['csv_path']}")

        # ── Step 6: Update ML dataset ─────────────────────────────────────────
        print("\n[6] Updating ML training dataset...")
        ml_entry = {
            "sample_id":   icpms_result["sample_id"],
            "composition": COMPOSITION,
            "oer": {
                "eta_10_mv":         oer_result["metrics"]["eta_10_mv"],
                "tafel_slope_mvdec": oer_result["metrics"]["tafel_slope_mvdec"],
            },
            "dissolution_result": {
                "D0":      D0_real,
                "alpha":   alpha_real,
                "cum_500h": g3["cum_500h_real"],
            },
            "characterisation": gate_result.get("characterisation", {}),
        }
        dataset_path = os.path.join(tmpdir, "stability_ml_dataset.csv")
        ml_df = update_ml_dataset(ml_entry, dataset_path)
        print(f"    Dataset rows: {len(ml_df)}")
        print(f"    New entry ID: {ml_df.iloc[-1]['id']}")

        # ── Step 7: Generate lab report ───────────────────────────────────────
        print("\n[7] Generating lab report...")
        report_path = os.path.join(tmpdir, f"lab_report_{COMPOSITION_NAME.replace('(', '').replace(')', '').replace('.', '')}.txt")
        report_text = generate_lab_report(
            sample_id   = icpms_result["sample_id"],
            composition = COMPOSITION,
            results     = g3,
            output_path = report_path,
        )
        print(f"    Report saved: {report_path}")

        # ── Step 8: Print the key comparison numbers ──────────────────────────
        print("\n" + "=" * 72)
        print("SUMMARY — Real data vs Gate 3 model predictions")
        print("=" * 72)
        print(f"Real D0    = {g3['D0_real']:.4f} µg/cm²/h   "
              f"vs   Model D0    = {g3['D0_model']:.4f} µg/cm²/h  "
              f"  (ratio {g3['D0_real'] / g3['D0_model']:.2f}×)")
        print(f"Real alpha = {g3['alpha_real']:.4f}             "
              f"vs   Model alpha = {g3['alpha_model']:.4f}")
        print(f"Real P50   = {g3['p50_lifetime_real']:.0f} h             "
              f"vs   Model P50   = {g3['p50_lifetime_model']:.0f} h")
        print()
        print("Interpretation:")
        if g3["D0_real"] < g3["D0_model"] * 0.8:
            print("  Real D0 < model: catalyst is MORE stable than predicted.")
            print("  -> Model is conservative; real catalyst may exceed P50 target.")
        elif g3["D0_real"] > g3["D0_model"] * 1.2:
            print("  Real D0 > model: catalyst is LESS stable than predicted.")
            print("  -> Review synthesis protocol; check CaWO4 phase fraction.")
        else:
            print("  Real D0 ≈ model: good agreement between ICP-MS and Gate 3 simulation.")

        if g3["alpha_real"] > g3["alpha_model"] + 0.05:
            print("  Real alpha > model: dissolution decays faster than modelled.")
            print("  -> Strong self-passivation occurring; CaWO4 enrichment confirmed.")
        elif g3["alpha_real"] < g3["alpha_model"] - 0.05:
            print("  Real alpha < model: dissolution decays more slowly than modelled.")
            print("  -> Passivation weaker than expected; consider more CaWO4 precursor.")

        print()
        print(f"Gate 3 verdict: {'PASS' if g3['gate3_pass_real'] else 'FAIL'}")
        print("=" * 72)
        print()
        print("Note: All output files written to a temporary directory (auto-cleaned).")
        print("In production, specify output_dir=<project_dir>/results/ in each call.")
        print()
        print("Example real-data call:")
        print()
        print("  from data_ingestion import (")
        print("      ingest_icpms, ingest_oer_curve, update_gate3_model,")
        print("      update_ml_dataset, generate_lab_report")
        print("  )")
        print()
        print("  icpms  = ingest_icpms('2026-03-15_CaMnW_001.csv',")
        print("                        composition={'Ca':0.11,'Mn':0.55,'W':0.34,'Ti':0.002})")
        print("  oer    = ingest_oer_curve('2026-03-15_CaMnW_001_oer.csv')")
        print("  g3     = update_gate3_model(icpms['data'], 'CaMnW #1',")
        print("                             composition={'Ca':0.11,'Mn':0.55,'W':0.34})")
        print("  report = generate_lab_report(icpms['sample_id'],")
        print("                               icpms['composition'], g3,")
        print("                               'results/lab_report_CaMnW_001.txt')")
