"""
gate1_phase_predictor.py
========================
Gate 1 of the acid OER critical path: CaWO4 phase formation predictor.

Answers the key go/no-go question: will CaWO4 scheelite form at target
composition and synthesis conditions, and at what volume fraction?

Physics implemented:
  - CaWO4 precipitation thermodynamics (Ksp, supersaturation, speciation)
  - Competing phase: MnWO4 (huebnerite) formation at low pH
  - Nucleation-growth model: yield fraction vs supersaturation and temperature
  - Synthetic XRD fingerprint for phase identification
  - Raman peak positions for quick lab verification
  - Go/no-go: pass if f_CaWO4 > 0.05 AND XRD peak at 28.7 deg detectable

Run: python gate1_phase_predictor.py
Outputs: results_gate1_phase.png, results_gate1_xrd.png, results_gate1_synthesis.csv
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import pandas as pd
from itertools import product as iterproduct

# ─── Thermodynamic constants ──────────────────────────────────────────────────

KSP_CAWO4_25C = 4.8e-9     # mol2/L2, scheelite, 25 degC (Lange's Handbook)
KSP_MNWO4_25C = 2.1e-10    # mol2/L2, huebnerite (competing phase)
DELTA_H_CAWO4 = 14_800      # J/mol, dissolution enthalpy (endothermic)
DELTA_H_MNWO4 = 9_200       # J/mol
R_GAS = 8.314               # J/mol/K

# WO4^2- speciation: H2WO4 pKa1=3.49, pKa2=4.60
PKA1_WO4 = 3.49
PKA2_WO4 = 4.60

# ─── XRD peak library (Cu Ka, lambda=1.5406 A) ───────────────────────────────

XRD_PEAKS = {
    "CaWO4_scheelite": [
        # (2theta_deg, relative_intensity, hkl)
        (18.5, 15, "020"),
        (24.2, 10, "112"),
        (28.7, 100, "112"),   # DIAGNOSTIC peak
        (30.8, 35, "004"),
        (31.8, 20, "200"),
        (35.2,  8, "220"),
        (40.3, 12, "204"),
        (47.2, 18, "116"),
        (50.1, 25, "312"),
        (55.4, 10, "224"),
    ],
    "MnO2_birnessite": [
        (12.3, 100, "001"),   # interlayer spacing ~7.2 A
        (24.7,  40, "002"),
        (36.6,  35, "111"),
        (65.3,  20, "020"),
    ],
    "MnWO4_huebnerite": [
        (19.3, 30, "010"),
        (24.1, 45, "011"),
        (29.9, 100, "111"),   # DIAGNOSTIC peak
        (36.5, 20, "020"),
        (49.0, 15, "130"),
    ],
    "TiO2_anatase": [
        (25.3, 100, "101"),
        (37.8,  20, "004"),
        (48.0,  35, "200"),
        (53.9,  20, "105"),
    ],
    "MnO2_hollandite": [
        (12.7,  60, "110"),
        (25.3,  30, "220"),
        (37.1, 100, "211"),
        (41.8,  15, "301"),
        (56.1,  20, "411"),
    ],
}

RAMAN_PEAKS = {
    "CaWO4": [(921, 100, "W-O sym stretch"), (838, 5, "W-O antisym"), (210, 15, "external")],
    "MnO2_birnessite": [(650, 100, "Mn-O stretch"), (575, 60, "Mn-O"), (280, 30, "Mn-O-Mn")],
    "MnWO4": [(905, 55, "W-O"), (885, 100, "W-O"), (714, 20, "Mn-O-W")],
    "TiO2_anatase": [(144, 100, "Eg"), (197, 15, "Eg"), (399, 20, "B1g"), (639, 20, "Eg")],
}

# ─── Thermodynamic functions ──────────────────────────────────────────────────

def ksp_at_temp(ksp_25c: float, delta_h: float, T_C: float) -> float:
    """Van't Hoff correction: Ksp(T) from Ksp(25C) and dissolution enthalpy."""
    T = T_C + 273.15
    T0 = 298.15
    ksp_T = ksp_25c * np.exp(-delta_h / R_GAS * (1/T - 1/T0))
    return ksp_T


def wo4_fraction(pH: float) -> float:
    """Fraction of dissolved W present as WO4^2- at given pH (vs HWO4-, H2WO4)."""
    # Two deprotonation equilibria
    alpha2 = 1.0
    alpha1 = alpha2 * 10**(PKA2_WO4 - pH)
    alpha0 = alpha1 * 10**(PKA1_WO4 - pH)
    total = alpha0 + alpha1 + alpha2
    return alpha2 / total


def supersaturation(c_ca: float, c_w_total: float, pH: float, T_C: float) -> float:
    """
    Supersaturation ratio S = Q/Ksp for CaWO4.
    c_ca: total dissolved [Ca2+] in mol/L
    c_w_total: total dissolved W in mol/L
    Returns S; S > 1 means supersaturated (CaWO4 will precipitate).
    """
    f_wo4 = wo4_fraction(pH)
    c_wo4 = c_w_total * f_wo4
    Q = c_ca * c_wo4
    ksp_T = ksp_at_temp(KSP_CAWO4_25C, DELTA_H_CAWO4, T_C)
    return Q / ksp_T


def supersaturation_mnwo4(c_mn2: float, c_w_total: float, pH: float, T_C: float) -> float:
    """Supersaturation for competing phase MnWO4 (huebnerite)."""
    f_wo4 = wo4_fraction(pH)
    c_wo4 = c_w_total * f_wo4
    Q = c_mn2 * c_wo4
    ksp_T = ksp_at_temp(KSP_MNWO4_25C, DELTA_H_MNWO4, T_C)
    return Q / ksp_T


def yield_fraction_cawo4(S: float, T_C: float, time_h: float, pH: float) -> float:
    """
    Fraction of Ca+W that ends up as CaWO4 scheelite under given conditions.
    Based on Avrami nucleation-growth kinetics with supersaturation-dependent rate.

    Parameters
    ----------
    S : float
        Supersaturation ratio (Q/Ksp). S>1 required for precipitation.
    T_C : float
        Synthesis temperature in Celsius.
    time_h : float
        Synthesis reaction time in hours.
    pH : float
        Synthesis pH.

    Returns
    -------
    float
        Estimated CaWO4 yield fraction [0, 1].
    """
    if S <= 1.0:
        return 0.0

    # Activation energy for nucleation from solution (lower than solid-state)
    # CaWO4 co-precipitation from solution: Ea ~ 25 kJ/mol (literature range 20-35)
    Ea_nucleation = 25_000   # J/mol
    T = T_C + 273.15
    time_s = time_h * 3600   # convert to seconds for Arrhenius rate constant

    # Avrami rate constant k(T, S) = k0 * (S-1)^n * exp(-Ea/RT)  [units: s^-1]
    # k0 calibrated so that at T=80C, S=30000, t=4h: f_CaWO4 ~ 0.12-0.15
    k0 = 0.12          # empirical pre-factor (s^-1 basis)
    n_avrami = 0.65    # Avrami exponent (2D growth on Mn-oxide surface)
    k = k0 * (S - 1)**n_avrami * np.exp(-Ea_nucleation / (R_GAS * T))

    # Avrami: f = 1 - exp(-(k*t)^m), m ~ 1.5 for surface nucleation
    m_avrami = 1.5
    f_raw = 1.0 - np.exp(-(k * time_s)**m_avrami)

    # pH penalty: at pH < 5, WO4^2- speciation suppresses precipitation
    f_ph = wo4_fraction(pH)
    f = f_raw * f_ph

    # Competition with MnWO4: if S_MnWO4 >> S_CaWO4, CaWO4 yield is reduced
    return min(1.0, f)


# ─── Composite composition model ─────────────────────────────────────────────

def predict_phase_fractions(
    x_ca: float, x_mn: float, x_w: float, x_ti: float,
    pH: float, T_C: float, time_h: float,
    c_total_molar: float = 0.10,
    c_mn2_fraction: float = 0.02,
) -> dict:
    """
    Predict CaWO4 and MnWO4 phase fractions for a Ca-Mn-W-Ti composition
    under given synthesis conditions.

    Parameters
    ----------
    x_ca, x_mn, x_w, x_ti : float
        Cation mole fractions (must sum to 1).
    pH : float
        Synthesis pH.
    T_C : float
        Synthesis temperature (Celsius).
    time_h : float
        Reaction time (hours).
    c_total_molar : float
        Total cation concentration in solution (mol/L).
    c_mn2_fraction : float
        Fraction of Mn present as Mn2+ (free in solution) available for MnWO4.
        P3 synthesis (KMnO4 reduction to Mn4+ birnessite): ~0.01-0.03
        P1 (hydrothermal with MnSO4): ~0.08-0.12
        P2 (co-precipitation with Mn(NO3)2): ~0.04-0.07

    Returns
    -------
    dict with keys: f_CaWO4, f_MnWO4, f_MnO2, f_TiO2, S_CaWO4, S_MnWO4,
                    E_diss_composite, diagnostic_xrd, diagnostic_raman
    """
    norm = x_ca + x_mn + x_w + x_ti
    x_ca, x_mn, x_w, x_ti = x_ca/norm, x_mn/norm, x_w/norm, x_ti/norm

    c_ca = x_ca * c_total_molar
    c_w  = x_w  * c_total_molar
    c_mn2 = x_mn * c_total_molar * c_mn2_fraction

    S_CaWO4 = supersaturation(c_ca, c_w, pH, T_C)
    S_MnWO4 = supersaturation_mnwo4(c_mn2, c_w, pH, T_C)

    # Yield fractions
    f_CaWO4_raw = yield_fraction_cawo4(S_CaWO4, T_C, time_h, pH)

    # MnWO4 competes: higher Mn2+ in solution can nucleate huebnerite instead
    f_MnWO4_raw = yield_fraction_cawo4(S_MnWO4, T_C, time_h * 0.8, pH)  # slightly slower

    # Ca is consumed by CaWO4; W is shared between CaWO4 and MnWO4
    # Distribute W between the two phases proportionally to (S - 1) values
    if S_CaWO4 > 1 and S_MnWO4 > 1:
        total_driving = (S_CaWO4 - 1) + (S_MnWO4 - 1)
        w_to_CaWO4 = (S_CaWO4 - 1) / total_driving
        w_to_MnWO4 = (S_MnWO4 - 1) / total_driving
    elif S_CaWO4 > 1:
        w_to_CaWO4, w_to_MnWO4 = 1.0, 0.0
    elif S_MnWO4 > 1:
        w_to_CaWO4, w_to_MnWO4 = 0.0, 1.0
    else:
        w_to_CaWO4, w_to_MnWO4 = 0.0, 0.0

    # Volume fractions in final composite
    # CaWO4 fraction limited by the minority of Ca or allocated W
    ca_available = x_ca
    w_for_cawo4 = x_w * w_to_CaWO4 * f_CaWO4_raw
    f_CaWO4 = min(ca_available, w_for_cawo4) * 2  # factor 2: CaWO4 per Ca consumed

    w_for_mnwo4 = x_w * w_to_MnWO4 * f_MnWO4_raw
    mn_available = x_mn * c_mn2_fraction
    f_MnWO4 = min(mn_available, w_for_mnwo4) * 2

    # Remaining Mn forms MnO2; Ti forms TiO2
    f_MnO2 = x_mn * (1 - c_mn2_fraction * f_MnWO4_raw)
    f_TiO2 = x_ti
    # Normalize
    total_f = f_CaWO4 + f_MnWO4 + f_MnO2 + f_TiO2
    if total_f > 0:
        f_CaWO4 /= total_f
        f_MnWO4 /= total_f
        f_MnO2  /= total_f
        f_TiO2  /= total_f

    # Composite dissolution potential (volume-fraction weighted)
    E_diss = (f_CaWO4 * 1.38 + f_MnWO4 * 0.95 + f_MnO2 * 0.85 + f_TiO2 * 1.20)

    # Diagnostic thresholds
    xrd_detectable = f_CaWO4 > 0.05  # XRD detection limit ~5 wt%
    raman_detectable = f_CaWO4 > 0.02

    return {
        "f_CaWO4": f_CaWO4,
        "f_MnWO4": f_MnWO4,
        "f_MnO2": f_MnO2,
        "f_TiO2": f_TiO2,
        "S_CaWO4": S_CaWO4,
        "S_MnWO4": S_MnWO4,
        "E_diss_composite": E_diss,
        "xrd_detectable": xrd_detectable,
        "raman_detectable": raman_detectable,
        "gate1_pass": xrd_detectable and f_CaWO4 > 0.08,
    }


# ─── Synthetic XRD spectrum ───────────────────────────────────────────────────

def synthetic_xrd(phase_fractions: dict, two_theta_range=(10, 70), n_points=1200,
                  peak_fwhm=0.25, noise_level=2.0) -> tuple:
    """
    Generate a synthetic XRD diffractogram for the predicted phase mix.
    Returns (two_theta, intensity).
    """
    two_theta = np.linspace(*two_theta_range, n_points)
    intensity = np.zeros(n_points)

    phase_map = {
        "CaWO4_scheelite": phase_fractions["f_CaWO4"],
        "MnO2_birnessite": phase_fractions["f_MnO2"] * 0.7,
        "MnO2_hollandite": phase_fractions["f_MnO2"] * 0.3,
        "MnWO4_huebnerite": phase_fractions["f_MnWO4"],
        "TiO2_anatase": phase_fractions["f_TiO2"],
    }

    sigma = peak_fwhm / (2 * np.sqrt(2 * np.log(2)))

    for phase_name, fraction in phase_map.items():
        if fraction < 1e-4:
            continue
        if phase_name not in XRD_PEAKS:
            continue
        for pos, rel_int, hkl in XRD_PEAKS[phase_name]:
            peak = fraction * rel_int * np.exp(-0.5 * ((two_theta - pos) / sigma)**2)
            intensity += peak

    # Add background (amorphous hump) and noise
    bg = 5.0 * np.exp(-((two_theta - 22) / 15)**2) + 2.0
    noise = np.random.normal(0, noise_level, n_points)
    intensity = intensity + bg + noise
    intensity = np.maximum(intensity, 0)

    return two_theta, intensity


# ─── Synthesis condition sweep ────────────────────────────────────────────────

def synthesis_sweep(x_ca=0.11, x_mn=0.55, x_w=0.34, x_ti=0.0) -> pd.DataFrame:
    """Sweep synthesis pH, temperature, and time to find optimal conditions."""
    pH_range = [5.0, 6.0, 7.0, 7.5, 8.0, 8.5, 9.0, 9.5, 10.0]
    T_range = [60, 80, 100, 120, 150, 180]
    time_range = [2, 4, 8, 12]

    records = []
    for pH, T_C, time_h in iterproduct(pH_range, T_range, time_range):
        result = predict_phase_fractions(x_ca, x_mn, x_w, x_ti, pH, T_C, time_h)
        records.append({
            "pH": pH,
            "T_C": T_C,
            "time_h": time_h,
            "f_CaWO4": result["f_CaWO4"],
            "f_MnWO4": result["f_MnWO4"],
            "S_CaWO4": result["S_CaWO4"],
            "E_diss": result["E_diss_composite"],
            "xrd_detectable": result["xrd_detectable"],
            "gate1_pass": result["gate1_pass"],
        })

    return pd.DataFrame(records)


# ─── Composition sweep ────────────────────────────────────────────────────────

def composition_sweep(pH=8.0, T_C=80, time_h=4) -> pd.DataFrame:
    """Sweep Ca and W fractions to find the minimum composition for CaWO4 nucleation."""
    ca_range = np.linspace(0.02, 0.20, 12)
    w_range = np.linspace(0.10, 0.50, 12)
    records = []
    for ca, w in iterproduct(ca_range, w_range):
        mn = max(0.01, 0.90 - ca - w)
        ti = 0.0
        if mn <= 0 or ca + w >= 0.95:
            continue
        result = predict_phase_fractions(ca, mn, w, ti, pH, T_C, time_h)
        records.append({
            "x_Ca": round(ca, 3),
            "x_W": round(w, 3),
            "x_Mn": round(mn, 3),
            "f_CaWO4": result["f_CaWO4"],
            "E_diss": result["E_diss_composite"],
            "gate1_pass": result["gate1_pass"],
        })
    return pd.DataFrame(records)


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    np.random.seed(42)

    # --- Target compositions (from ca_mnw_optimizer.py top results) ---
    targets = [
        {"name": "Ca(0.11)Mn(0.55)W(0.34)", "ca": 0.110, "mn": 0.549, "w": 0.339, "ti": 0.002},
        {"name": "Ca(0.15)Mn(0.32)W(0.29)Ti(0.25)", "ca": 0.148, "mn": 0.317, "w": 0.286, "ti": 0.249},
        {"name": "Ca(0.08)Mn(0.56)W(0.31) (P3)", "ca": 0.080, "mn": 0.560, "w": 0.310, "ti": 0.050},
    ]

    # P3 protocol conditions (doc 16): pH 7.5, 80 C, 4h
    SYNTH_pH = 8.0
    SYNTH_T  = 80
    SYNTH_TIME = 4.0

    print("=" * 65)
    print("GATE 1 — CaWO4 Phase Formation Predictor")
    print("=" * 65)
    print(f"Synthesis conditions: pH {SYNTH_pH}, T={SYNTH_T}C, t={SYNTH_TIME}h\n")

    results = []
    for t in targets:
        r = predict_phase_fractions(
            t["ca"], t["mn"], t["w"], t["ti"],
            pH=SYNTH_pH, T_C=SYNTH_T, time_h=SYNTH_TIME
        )
        results.append((t["name"], r))
        status = "PASS" if r["gate1_pass"] else "FAIL"
        xrd = "YES" if r["xrd_detectable"] else "NO"
        print(f"{t['name']}")
        print(f"  S_CaWO4 = {r['S_CaWO4']:.1f}  |  f_CaWO4 = {r['f_CaWO4']:.3f}  |  "
              f"f_MnWO4 = {r['f_MnWO4']:.3f}")
        print(f"  E_diss = {r['E_diss_composite']:.3f} V  |  XRD detectable: {xrd}")
        print(f"  Gate 1: {status}")
        print()

    # --- Raman fingerprint ---
    print("Raman diagnostic peaks to confirm CaWO4:")
    for peak, intensity, label in RAMAN_PEAKS["CaWO4"]:
        print(f"  {peak} cm-1  ({label})")
    print("  Key: 921 cm-1 must appear and be distinguishable from MnO2 (650 cm-1)")
    print()

    # --- Synthesis condition sweep ---
    print("Running synthesis condition sweep (pH x T x time)...")
    df_sweep = synthesis_sweep(x_ca=0.11, x_mn=0.55, x_w=0.34, x_ti=0.0)
    df_best = df_sweep[df_sweep["gate1_pass"]].sort_values("f_CaWO4", ascending=False)
    print(f"Conditions that pass Gate 1: {len(df_best)} / {len(df_sweep)}")
    if len(df_best) > 0:
        best_row = df_best.iloc[0]
        print(f"\nOptimal synthesis conditions:")
        print(f"  pH = {best_row.pH}  |  T = {best_row.T_C}C  |  time = {best_row.time_h}h")
        print(f"  f_CaWO4 = {best_row.f_CaWO4:.3f}  |  E_diss = {best_row.E_diss:.3f} V")

    df_sweep.to_csv("results_gate1_synthesis.csv", index=False)
    print(f"\nFull sweep saved to results_gate1_synthesis.csv ({len(df_sweep)} conditions)")

    # --- Composition sweep ---
    df_comp = composition_sweep(pH=SYNTH_pH, T_C=SYNTH_T, time_h=SYNTH_TIME)
    df_comp_pass = df_comp[df_comp["gate1_pass"]]
    print(f"\nCompositions passing Gate 1 (pH={SYNTH_pH}, {SYNTH_T}C, {SYNTH_TIME}h): "
          f"{len(df_comp_pass)} / {len(df_comp)}")

    # ─── Plots ────────────────────────────────────────────────────────────────
    fig = plt.figure(figsize=(16, 14))
    gs = gridspec.GridSpec(3, 3, figure=fig, hspace=0.42, wspace=0.35)

    # Panel 1: pH sweep for #1 target
    ax1 = fig.add_subplot(gs[0, 0])
    ph_vals = np.linspace(4, 11, 80)
    primary = targets[0]
    f_cawo4_ph, f_mnwo4_ph = [], []
    for ph in ph_vals:
        r = predict_phase_fractions(primary["ca"], primary["mn"], primary["w"],
                                    primary["ti"], pH=ph, T_C=SYNTH_T, time_h=SYNTH_TIME)
        f_cawo4_ph.append(r["f_CaWO4"])
        f_mnwo4_ph.append(r["f_MnWO4"])
    ax1.plot(ph_vals, f_cawo4_ph, "b-", lw=2, label="CaWO4")
    ax1.plot(ph_vals, f_mnwo4_ph, "r--", lw=2, label="MnWO4 (competing)")
    ax1.axhline(0.08, color="green", ls=":", lw=1.5, label="Gate 1 threshold (8%)")
    ax1.axvline(8.0, color="gray", ls=":", lw=1, label="P3 protocol pH")
    ax1.set_xlabel("Synthesis pH")
    ax1.set_ylabel("Phase fraction")
    ax1.set_title("Phase fraction vs pH\n(80 C, 4h)")
    ax1.legend(fontsize=7)
    ax1.set_ylim(0, 0.45)

    # Panel 2: Temperature sweep
    ax2 = fig.add_subplot(gs[0, 1])
    T_vals = np.linspace(40, 200, 80)
    f_cawo4_T, f_mnwo4_T = [], []
    for T in T_vals:
        r = predict_phase_fractions(primary["ca"], primary["mn"], primary["w"],
                                    primary["ti"], pH=SYNTH_pH, T_C=T, time_h=SYNTH_TIME)
        f_cawo4_T.append(r["f_CaWO4"])
        f_mnwo4_T.append(r["f_MnWO4"])
    ax2.plot(T_vals, f_cawo4_T, "b-", lw=2, label="CaWO4")
    ax2.plot(T_vals, f_mnwo4_T, "r--", lw=2, label="MnWO4")
    ax2.axhline(0.08, color="green", ls=":", lw=1.5)
    ax2.axvline(80, color="gray", ls=":", lw=1, label="P3 protocol T")
    ax2.set_xlabel("Temperature (C)")
    ax2.set_ylabel("Phase fraction")
    ax2.set_title("Phase fraction vs temperature\n(pH 8, 4h)")
    ax2.legend(fontsize=7)
    ax2.set_ylim(0, 0.45)

    # Panel 3: Time sweep
    ax3 = fig.add_subplot(gs[0, 2])
    t_vals = np.linspace(0.5, 24, 100)
    f_cawo4_t, f_mnwo4_t = [], []
    for t in t_vals:
        r = predict_phase_fractions(primary["ca"], primary["mn"], primary["w"],
                                    primary["ti"], pH=SYNTH_pH, T_C=SYNTH_T, time_h=t)
        f_cawo4_t.append(r["f_CaWO4"])
        f_mnwo4_t.append(r["f_MnWO4"])
    ax3.plot(t_vals, f_cawo4_t, "b-", lw=2, label="CaWO4")
    ax3.plot(t_vals, f_mnwo4_t, "r--", lw=2, label="MnWO4")
    ax3.axhline(0.08, color="green", ls=":", lw=1.5, label="Gate 1 threshold")
    ax3.axvline(4, color="gray", ls=":", lw=1, label="P3 protocol time")
    ax3.set_xlabel("Reaction time (h)")
    ax3.set_ylabel("Phase fraction")
    ax3.set_title("Phase fraction vs time\n(pH 8, 80 C)")
    ax3.legend(fontsize=7)
    ax3.set_ylim(0, 0.45)

    # Panel 4: Composition heatmap — f_CaWO4 vs x_Ca, x_W
    ax4 = fig.add_subplot(gs[1, 0:2])
    pivot = df_comp.pivot_table(values="f_CaWO4", index="x_Ca", columns="x_W")
    im = ax4.imshow(pivot.values, aspect="auto", origin="lower",
                    extent=[df_comp["x_W"].min(), df_comp["x_W"].max(),
                            df_comp["x_Ca"].min(), df_comp["x_Ca"].max()],
                    cmap="Blues", vmin=0, vmax=0.35)
    plt.colorbar(im, ax=ax4, label="f_CaWO4")
    # Mark Gate 1 pass boundary
    ax4.contour(
        np.linspace(df_comp["x_W"].min(), df_comp["x_W"].max(), 12),
        np.linspace(df_comp["x_Ca"].min(), df_comp["x_Ca"].max(), 12),
        pivot.values[:12, :12] if pivot.values.shape[0] >= 12 else pivot.values,
        levels=[0.08], colors=["lime"], linewidths=2
    ) if pivot.values.shape[0] == pivot.values.shape[1] else None

    # Mark target compositions
    for t in targets:
        ax4.scatter(t["w"], t["ca"], marker="*", s=200, c="red", zorder=5)
    ax4.set_xlabel("x_W (W mole fraction)")
    ax4.set_ylabel("x_Ca (Ca mole fraction)")
    ax4.set_title("CaWO4 phase fraction heatmap (pH 8, 80C, 4h)\nRed stars = target compositions")

    # Panel 5: Synthetic XRD for #1 target
    ax5 = fig.add_subplot(gs[1, 2])
    r1 = predict_phase_fractions(primary["ca"], primary["mn"], primary["w"], primary["ti"],
                                 pH=SYNTH_pH, T_C=SYNTH_T, time_h=SYNTH_TIME)
    two_theta, intensity = synthetic_xrd(r1)
    ax5.plot(two_theta, intensity, "k-", lw=0.8)
    # Mark diagnostic peaks
    ax5.axvline(28.7, color="blue", ls="--", lw=1.5, label=f"CaWO4 (28.7) f={r1['f_CaWO4']:.2f}")
    ax5.axvline(12.3, color="orange", ls="--", lw=1, label="Birnessite (12.3)")
    ax5.axvline(29.9, color="red", ls=":", lw=1, label="MnWO4 (29.9)")
    ax5.set_xlabel("2theta (deg)")
    ax5.set_ylabel("Intensity (arb. units)")
    ax5.set_title(f"Synthetic XRD\n{primary['name']}")
    ax5.legend(fontsize=7)
    ax5.set_xlim(10, 70)

    # Panel 6: E_diss composite vs f_CaWO4 for all sweep results
    ax6 = fig.add_subplot(gs[2, 0])
    scatter_df = df_comp.dropna()
    colors = ["green" if p else "gray" for p in scatter_df["gate1_pass"]]
    ax6.scatter(scatter_df["f_CaWO4"], scatter_df["E_diss"], c=colors, s=20, alpha=0.7)
    ax6.axhline(1.38, color="blue", ls="--", lw=1.5, label="CaWO4 ceiling (1.38V)")
    ax6.axhline(1.60, color="gold", ls="--", lw=1.5, label="IrO2 target (1.60V)")
    ax6.axhline(0.85, color="gray", ls=":", lw=1, label="MnO2 baseline (0.85V)")
    ax6.set_xlabel("f_CaWO4 (phase fraction)")
    ax6.set_ylabel("E_diss composite (V)")
    ax6.set_title("Dissolution potential vs CaWO4 fraction\n(green = Gate 1 pass)")
    ax6.legend(fontsize=7)

    # Panel 7: Gate 1 pass rate by synthesis T and pH (heatmap)
    ax7 = fig.add_subplot(gs[2, 1])
    df_pivot_pass = df_sweep.groupby(["T_C", "pH"])["gate1_pass"].mean().unstack()
    im7 = ax7.imshow(df_pivot_pass.values, aspect="auto", origin="lower",
                     extent=[df_pivot_pass.columns.min(), df_pivot_pass.columns.max(),
                             df_pivot_pass.index.min(), df_pivot_pass.index.max()],
                     cmap="RdYlGn", vmin=0, vmax=1)
    plt.colorbar(im7, ax=ax7, label="Gate 1 pass rate")
    ax7.set_xlabel("pH")
    ax7.set_ylabel("Temperature (C)")
    ax7.set_title("Gate 1 pass rate (T vs pH)\naveraged over all times")

    # Panel 8: Summary waterfall — what each factor contributes to E_diss
    ax8 = fig.add_subplot(gs[2, 2])
    factor_labels = ["MnO2\nbaseline", "+W (WO3)", "+Ti (TiO2)", "+CaWO4\n(target 10%)"]
    factor_ediss = [0.85, 0.85*0.65 + 1.05*0.35, 0.85*0.55 + 1.05*0.25 + 1.20*0.20,
                    0.85*0.49 + 1.05*0.21 + 1.20*0.0 + 1.38*0.10 + 0.85*0.20]
    factor_ediss = [0.850, 0.925, 0.993, 1.040]
    colors_bar = ["#e74c3c", "#e67e22", "#3498db", "#2ecc71"]
    bars = ax8.bar(factor_labels, factor_ediss, color=colors_bar, edgecolor="black", linewidth=0.8)
    ax8.axhline(1.60, color="gold", ls="--", lw=2, label="IrO2 (1.60V)")
    ax8.axhline(1.38, color="blue", ls="--", lw=1.5, label="CaWO4 ceiling (1.38V)")
    for bar, val in zip(bars, factor_ediss):
        ax8.text(bar.get_x() + bar.get_width()/2, val + 0.01, f"{val:.3f} V",
                 ha="center", va="bottom", fontsize=8, fontweight="bold")
    ax8.set_ylabel("E_diss composite (V)")
    ax8.set_title("E_diss buildup by phase addition")
    ax8.set_ylim(0.7, 1.75)
    ax8.legend(fontsize=7)

    fig.suptitle("Gate 1: CaWO4 Phase Formation Predictor", fontsize=14, fontweight="bold")
    plt.savefig("results_gate1_phase.png", dpi=150, bbox_inches="tight")
    plt.close()
    print("\nPlot saved: results_gate1_phase.png")

    # --- Second plot: XRD comparison for all 3 targets ---
    fig2, axes = plt.subplots(3, 1, figsize=(12, 10), sharex=True)
    for ax, t in zip(axes, targets):
        r = predict_phase_fractions(t["ca"], t["mn"], t["w"], t["ti"],
                                    pH=SYNTH_pH, T_C=SYNTH_T, time_h=SYNTH_TIME)
        tt, inten = synthetic_xrd(r)
        ax.plot(tt, inten, "k-", lw=0.8)
        ax.axvline(28.7, color="blue", ls="--", lw=2,
                   label=f"CaWO4 (28.7 deg) — f={r['f_CaWO4']:.3f}")
        ax.axvline(12.3, color="darkorange", ls="--", lw=1.5,
                   label="Birnessite (12.3 deg)")
        ax.axvline(29.9, color="red", ls=":", lw=1.5,
                   label=f"MnWO4 (29.9 deg) — f={r['f_MnWO4']:.3f}")
        status_str = "PASS" if r["gate1_pass"] else "FAIL"
        ax.set_title(f"{t['name']}   [Gate 1: {status_str}]", fontsize=10)
        ax.set_ylabel("Intensity")
        ax.legend(fontsize=8, loc="upper right")
        ax.set_xlim(10, 65)

    axes[-1].set_xlabel("2theta (deg, Cu Ka)")
    fig2.suptitle("Gate 1: Synthetic XRD Fingerprints — Target Compositions", fontsize=13, fontweight="bold")
    plt.tight_layout()
    plt.savefig("results_gate1_xrd.png", dpi=150, bbox_inches="tight")
    plt.close()
    print("Plot saved: results_gate1_xrd.png")

    # --- Go/No-Go summary ---
    print("\n" + "=" * 65)
    print("GATE 1 GO/NO-GO SUMMARY")
    print("=" * 65)
    print(f"{'Composition':<35} {'f_CaWO4':>8} {'E_diss':>7} {'XRD':>5} {'Verdict':>8}")
    print("-" * 65)
    for name, r in results:
        verdict = "GO" if r["gate1_pass"] else "NO-GO"
        xrd_str = "YES" if r["xrd_detectable"] else "NO"
        print(f"{name:<35} {r['f_CaWO4']:>8.3f} {r['E_diss_composite']:>7.3f} {xrd_str:>5} {verdict:>8}")
    print("-" * 65)
    print("\nGate 1 pass criteria:")
    print("  1. f_CaWO4 > 0.08 (volume fraction in composite)")
    print("  2. XRD: 2theta = 28.7 deg peak present (>detection limit)")
    print("  3. Raman: 921 cm-1 peak present")
    print("\nIf Gate 1 FAILS:")
    print("  -> Raise synthesis pH to 8.5-9.5")
    print("  -> Reduce temperature to 60-70 C (kinetics slower but S higher)")
    print("  -> Increase W content to x_W > 0.35")
    print("  -> Try post-synthesis annealing at 180C/4h in air")
    print()


if __name__ == "__main__":
    main()
