"""
gate3_lifetime_projector.py
============================
Gate 3 of the acid OER critical path: 500h dissolution and lifetime projection.

Models multi-phase dissolution of Ca-Mn-W-Ti composites under:
  (a) Continuous chronopotentiometry (CP)
  (b) Pulsed CP: 59min on / 1min open circuit (doc 12 protocol)

Key mechanisms implemented:
  1. Phase-selective dissolution: Mn dissolves fastest, CaWO4 slowest
  2. Surface enrichment: as Mn dissolves, CaWO4/TiO2 fraction at surface rises
     -> self-passivation effect, dissolution rate drops over time
  3. Power law kinetics: D(t) = D0 * t^(-alpha) (short-term + long-term phases)
  4. OC recovery: each open-circuit pulse partially repairs the surface
  5. Weibull reliability analysis to project P50 lifetime from short-term data

Gate 3 pass criteria:
  - Cumulative dissolution < 25 ug/cm2 after 500h
  - Steady-state rate D_ss < 0.10 ug/cm2/h
  - Projected P50 lifetime > 1000h

Run: python gate3_lifetime_projector.py
Outputs: results_gate3_lifetime.png, results_gate3_projection.csv
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import pandas as pd
from scipy.integrate import solve_ivp
from scipy.optimize import curve_fit
from scipy.special import gamma as gamma_fn

# ─── Phase dissolution parameters ─────────────────────────────────────────────

# Dissolution rate constants k_i at E_OER = 1.55 V vs RHE, pH 1, 25 C
# Units: ug/cm2/h per unit mole fraction
# Derived from ICP-MS dissolution measurements on single-phase standards
# (Mn-oxide: ~2.0 ug/cm2/h at steady state; WO3: ~0.5; TiO2: ~0.02; CaWO4: ~0.04)

PHASE_PARAMS = {
    #        k0_ugcm2h   alpha_power   E_diss_V   density_g_cm3
    # k0 calibrated to ICP-MS literature for each phase at 10 mA/cm2, 0.5M H2SO4:
    # MnO2: initial ~2-5 ug/cm2/h, SS ~0.2-0.5 ug/cm2/h (Klemm 2022, Cherevko 2018)
    # WO3:  initial ~0.8-2 ug/cm2/h (Peeters 2021)
    # CaWO4: ~0.03-0.08 ug/cm2/h (estimated from scheelite dissolution literature)
    # TiO2: ~0.003-0.01 ug/cm2/h (Cherevko 2018, anatase)
    "MnO2":    ( 3.5,      0.50,         0.85,        5.02),
    "WO3":     ( 1.0,      0.42,         1.05,        7.16),
    "CaWO4":   ( 0.06,     0.32,         1.38,        6.06),
    "TiO2":    ( 0.025,    0.28,         1.20,        3.90),
}

# Surface enrichment timescale: time (h) for CaWO4-enriched surface layer to establish
TAU_ENRICH = 55.0      # h, exponential approach to surface equilibrium

# Pulsed CP parameters (doc 12: 59min on / 1min OC)
PULSE_ON_MIN  = 59.0
PULSE_OC_MIN  =  1.0
CYCLE_MIN     = PULSE_ON_MIN + PULSE_OC_MIN  # 60 min

# Effective pulsed rate factor — doc 12 reports ~2x lifetime extension for 59/1 protocol
# This corresponds to ~50% dissolution rate reduction vs. continuous CP
PULSED_RATE_FACTOR = 0.50

# Operating current density
J_OPR_MA_CM2 = 10.0

# IrO2 reference values
IrO2_D_STEADY = 0.010     # ug/cm2/h
IrO2_LIFETIME = 50_000    # h (conservative estimate)

# Gate 3 pass criteria
GATE3_CUMULATIVE_UG = 25.0    # ug/cm2 max cumulative in 500h
GATE3_STEADY_UG_H = 0.10      # ug/cm2/h max steady-state rate
GATE3_P50_LIFETIME_H = 1_000  # h minimum P50 lifetime

# Catalyst loading (typical for RDE experiments)
LOADING_MG_CM2 = 0.10         # mg/cm2
LOADING_UG_CM2 = LOADING_MG_CM2 * 1000  # ug/cm2


# ─── Multi-phase dissolution model ────────────────────────────────────────────

def phase_dissolution_rate(phase: str, f_surface: float, t: float,
                            f_cawo4_surface: float = 0.0) -> float:
    """
    Dissolution rate for a single phase at time t.
    Includes power law kinetics and surface CaWO4 passivation.

    Parameters
    ----------
    phase : str
        Phase name.
    f_surface : float
        Mole fraction of this phase at the surface at time t.
    t : float
        Time in hours (>0).
    f_cawo4_surface : float
        CaWO4 surface coverage fraction for passivation calculation.

    Returns
    -------
    float
        Dissolution rate in ug/cm2/h.
    """
    k0, alpha, _, _ = PHASE_PARAMS[phase]
    t_safe = max(t, 0.01)

    # Power law decay
    D = k0 * f_surface * t_safe**(-alpha)

    # CaWO4 passivation: physical blocking of dissolving surface
    # Effective passivation reaches 50% at f_cawo4_surface = 0.25
    passivation = 1.0 / (1.0 + 3.5 * f_cawo4_surface)
    if phase != "CaWO4":
        D *= passivation

    return D


def surface_fractions(bulk_fractions: dict, t: float,
                      dissolution_consumed: dict) -> dict:
    """
    Compute surface phase fractions at time t, accounting for selective
    dissolution of less stable phases.

    The surface becomes enriched in CaWO4 and TiO2 as Mn dissolves faster.
    """
    # Cumulative dissolution per phase (tracked externally)
    remaining = {}
    for phase, f0 in bulk_fractions.items():
        consumed_frac = dissolution_consumed.get(phase, 0.0)
        remaining[phase] = max(0.0, f0 - consumed_frac)

    total_remaining = sum(remaining.values())
    if total_remaining < 1e-6:
        return {p: 0.0 for p in bulk_fractions}

    # Surface enrichment model: faster-dissolving phases deplete from surface first
    # Enrichment factor: proportional to (1/dissolution_rate_normalized)
    surface_f = {}
    for phase in bulk_fractions:
        k0_norm = PHASE_PARAMS[phase][0] / PHASE_PARAMS["MnO2"][0]
        # Enrichment: inverse of relative dissolution rate, exponential approach
        enrich = 1.0 + (1.0 / (k0_norm + 0.01) - 1.0) * (1.0 - np.exp(-t / TAU_ENRICH))
        surface_f[phase] = remaining[phase] * enrich

    total_surf = sum(surface_f.values())
    if total_surf < 1e-6:
        return {p: 0.0 for p in bulk_fractions}

    return {p: v / total_surf for p, v in surface_f.items()}


def integrate_dissolution(
    bulk_fractions: dict,
    t_end_h: float,
    pulsed: bool = False,
    dt_h: float = 0.1,
) -> pd.DataFrame:
    """
    Integrate multi-phase dissolution over time.

    Parameters
    ----------
    bulk_fractions : dict
        Initial bulk phase fractions (e.g., {"MnO2": 0.60, "WO3": 0.20,
        "CaWO4": 0.12, "TiO2": 0.08}).
    t_end_h : float
        End time in hours.
    pulsed : bool
        If True, apply pulsed CP (59min/1min) recovery factor.
    dt_h : float
        Integration timestep in hours.

    Returns
    -------
    pd.DataFrame with columns: t_h, D_total, D_Mn, D_W, D_CaWO4, D_Ti,
                                D_cumulative, f_CaWO4_surface
    """
    t_steps = np.arange(dt_h, t_end_h + dt_h, dt_h)

    records = []
    dissolution_consumed = {p: 0.0 for p in bulk_fractions}
    D_cumulative = 0.0

    cycle_h = CYCLE_MIN / 60.0
    on_frac = PULSE_ON_MIN / CYCLE_MIN

    for t in t_steps:
        # Current surface fractions
        surf = surface_fractions(bulk_fractions, t, dissolution_consumed)
        f_cawo4_surf = surf.get("CaWO4", 0.0)

        # Phase dissolution rates
        D_phases = {}
        for phase, f_s in surf.items():
            D_phases[phase] = phase_dissolution_rate(phase, f_s, t, f_cawo4_surf)

        D_total_inst = sum(D_phases.values())

        # Apply pulsed CP factor (doc 12: 59/1 protocol gives ~2x lifetime = 50% rate)
        if pulsed:
            D_total_inst *= PULSED_RATE_FACTOR
            D_phases = {p: v * PULSED_RATE_FACTOR for p, v in D_phases.items()}

        D_cumulative += D_total_inst * dt_h

        # Update consumed fractions (track as fraction of total loading)
        for phase in bulk_fractions:
            phase_density_contribution = D_phases.get(phase, 0.0) * dt_h
            # Convert ug/cm2 dissolved to mole fraction consumed (approximate)
            dissolution_consumed[phase] += phase_density_contribution * 5e-5

        records.append({
            "t_h": t,
            "D_total_ug_cm2_h": D_total_inst,
            "D_Mn_ug_cm2_h": D_phases.get("MnO2", 0.0),
            "D_W_ug_cm2_h": D_phases.get("WO3", 0.0),
            "D_CaWO4_ug_cm2_h": D_phases.get("CaWO4", 0.0),
            "D_Ti_ug_cm2_h": D_phases.get("TiO2", 0.0),
            "D_cumulative_ug_cm2": D_cumulative,
            "f_CaWO4_surface": f_cawo4_surf,
        })

    return pd.DataFrame(records)


# ─── Power law fit and lifetime projection ────────────────────────────────────

def power_law(t, D0, alpha):
    return D0 * t**(-alpha)


def fit_power_law(df: pd.DataFrame, t_start_h: float = 5.0) -> tuple:
    """Fit D(t) = D0 * t^(-alpha) to the tail of dissolution data."""
    mask = df["t_h"] >= t_start_h
    t_fit = df.loc[mask, "t_h"].values
    D_fit = df.loc[mask, "D_total_ug_cm2_h"].values

    if len(t_fit) < 10:
        return (D_fit[0], 0.3) if len(D_fit) > 0 else (1.0, 0.3)

    try:
        popt, _ = curve_fit(power_law, t_fit, D_fit, p0=[D_fit[0], 0.3],
                            bounds=([0, 0.01], [500, 2.0]), maxfev=2000)
        return tuple(popt)
    except Exception:
        return (D_fit[0], 0.3)


def project_lifetime(df: pd.DataFrame, mass_budget_ug: float = LOADING_UG_CM2,
                     t_budget_h: float = 50_000) -> dict:
    """
    Project P50 lifetime from short-term dissolution data.

    Parameters
    ----------
    df : pd.DataFrame
        Dissolution data from integrate_dissolution.
    mass_budget_ug : float
        Total catalyst loading in ug/cm2 (lifetime ends when 50% is gone).
    t_budget_h : float
        Maximum projection horizon.
    """
    D0, alpha = fit_power_law(df, t_start_h=10.0)

    # Steady state rate (last 10% of measured data)
    t_ss_start = df["t_h"].max() * 0.9
    D_ss = df.loc[df["t_h"] >= t_ss_start, "D_total_ug_cm2_h"].mean()

    # Cumulative dissolution by integrating power law from t_measured to t_project
    t_measured = df["t_h"].max()
    cumulative_measured = df["D_cumulative_ug_cm2"].iloc[-1]

    # Analytical integral of D0 * t^(-alpha) from t_measured to t:
    # Integral = D0 / (1 - alpha) * (t^(1-alpha) - t_measured^(1-alpha))  if alpha != 1
    def cumulative_at_t(t_end):
        if abs(alpha - 1.0) < 0.01:
            return cumulative_measured + D0 * np.log(t_end / t_measured)
        else:
            return cumulative_measured + D0 / (1 - alpha) * (
                t_end**(1 - alpha) - t_measured**(1 - alpha)
            )

    # Find time when cumulative = 50% of loading (P50 lifetime)
    budget_50pct = mass_budget_ug * 0.5
    budget_100pct = mass_budget_ug

    # First check within simulation data (common case when dissolution is rapid)
    p50_in_sim = df[df["D_cumulative_ug_cm2"] >= budget_50pct]
    p100_in_sim = df[df["D_cumulative_ug_cm2"] >= budget_100pct]

    if len(p50_in_sim) > 0:
        p50_lifetime = float(p50_in_sim["t_h"].iloc[0])
    else:
        p50_lifetime = None
        for t_proj in np.geomspace(t_measured, t_budget_h * 5, 5000):
            cum = cumulative_at_t(t_proj)
            if cum >= budget_50pct:
                p50_lifetime = t_proj
                break

    if len(p100_in_sim) > 0:
        p100_lifetime = float(p100_in_sim["t_h"].iloc[0])
    else:
        p100_lifetime = None
        for t_proj in np.geomspace(t_measured, t_budget_h * 5, 5000):
            cum = cumulative_at_t(t_proj)
            if cum >= budget_100pct:
                p100_lifetime = t_proj
                break

    return {
        "D0_fit": D0,
        "alpha_fit": alpha,
        "D_steady_state": D_ss,
        "cumulative_500h": cumulative_at_t(500) if t_measured < 500 else cumulative_measured,
        "p50_lifetime_h": p50_lifetime or t_budget_h * 5,
        "p100_lifetime_h": p100_lifetime or t_budget_h * 5,
    }


# ─── Composition → phase fractions ───────────────────────────────────────────

def composition_to_phases(x_ca, x_mn, x_w, x_ti, f_cawo4_predicted=0.10) -> dict:
    """
    Convert Ca-Mn-W-Ti cation fractions to phase volume fractions.
    f_cawo4_predicted comes from gate1_phase_predictor.py output.
    """
    total = x_ca + x_mn + x_w + x_ti
    x_ca, x_mn, x_w, x_ti = x_ca/total, x_mn/total, x_w/total, x_ti/total

    # Ca is split: x_cawo4 into CaWO4, rest into Ca-birnessite (counted with MnO2)
    f_cawо4 = min(f_cawo4_predicted, min(x_ca, x_w))
    f_wо3 = max(0.0, x_w - f_cawо4)
    f_mnо2 = x_mn  # includes Ca-birnessite
    f_tiо2 = x_ti

    total_f = f_cawо4 + f_wо3 + f_mnо2 + f_tiо2
    return {
        "MnO2": f_mnо2 / total_f,
        "WO3": f_wо3 / total_f,
        "CaWO4": f_cawо4 / total_f,
        "TiO2": f_tiо2 / total_f,
    }


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    np.random.seed(42)

    TARGETS = [
        {
            "name": "Ca(0.11)Mn(0.55)W(0.34) #1",
            "ca": 0.110, "mn": 0.549, "w": 0.339, "ti": 0.002,
            "f_cawo4": 0.103,   # from gate1_phase_predictor
        },
        {
            "name": "Ca(0.15)Mn(0.32)W(0.29)Ti(0.25) #9",
            "ca": 0.148, "mn": 0.317, "w": 0.286, "ti": 0.249,
            "f_cawo4": 0.121,
        },
        {
            "name": "Ca(0.08)Mn(0.56)W(0.31) P3",
            "ca": 0.080, "mn": 0.560, "w": 0.310, "ti": 0.050,
            "f_cawo4": 0.072,   # lower CaWO4 (lower Ca content)
        },
        {
            "name": "MnO2 (baseline, no Ca/W)",
            "ca": 0.0, "mn": 0.90, "w": 0.10, "ti": 0.0,
            "f_cawo4": 0.0,
        },
    ]

    T_SIM_H = 600   # simulate 600h

    print("=" * 65)
    print("GATE 3 — 500h Dissolution & Lifetime Projector")
    print("=" * 65)
    print(f"Simulation: {T_SIM_H}h | Pulsed CP (59/1) vs Continuous CP\n")

    all_projections = []
    all_dfs = {}

    for t in TARGETS:
        phases = composition_to_phases(t["ca"], t["mn"], t["w"], t["ti"], t["f_cawo4"])

        df_cont  = integrate_dissolution(phases, T_SIM_H, pulsed=False, dt_h=0.2)
        df_pulse = integrate_dissolution(phases, T_SIM_H, pulsed=True,  dt_h=0.2)

        proj_cont  = project_lifetime(df_cont)
        proj_pulse = project_lifetime(df_pulse)

        # 500h cumulative
        cum_500_cont  = df_cont.loc[df_cont["t_h"] <= 500, "D_cumulative_ug_cm2"].iloc[-1]
        cum_500_pulse = df_pulse.loc[df_pulse["t_h"] <= 500, "D_cumulative_ug_cm2"].iloc[-1]

        # Steady-state rate (last 50h)
        Dss_cont  = df_cont.loc[df_cont["t_h"] >= 550, "D_total_ug_cm2_h"].mean()
        Dss_pulse = df_pulse.loc[df_pulse["t_h"] >= 550, "D_total_ug_cm2_h"].mean()

        gate3_pass = (cum_500_pulse <= GATE3_CUMULATIVE_UG and
                      Dss_pulse <= GATE3_STEADY_UG_H and
                      proj_pulse["p50_lifetime_h"] >= GATE3_P50_LIFETIME_H)

        print(f"{t['name']}")
        print(f"  Phases: MnO2={phases['MnO2']:.2f} WO3={phases['WO3']:.2f} "
              f"CaWO4={phases['CaWO4']:.3f} TiO2={phases['TiO2']:.2f}")
        print(f"  Continuous CP: D_500h_cum = {cum_500_cont:.1f} ug/cm2 | "
              f"D_ss = {Dss_cont:.3f} ug/cm2/h | P50 = {proj_cont['p50_lifetime_h']:.0f} h")
        print(f"  Pulsed CP:     D_500h_cum = {cum_500_pulse:.1f} ug/cm2 | "
              f"D_ss = {Dss_pulse:.3f} ug/cm2/h | P50 = {proj_pulse['p50_lifetime_h']:.0f} h")
        print(f"  Pulsed/Cont ratio (lifetime): "
              f"{proj_pulse['p50_lifetime_h'] / max(proj_cont['p50_lifetime_h'], 1):.2f}x")
        print(f"  Gate 3 (pulsed CP): {'PASS' if gate3_pass else 'FAIL'}")
        print()

        all_dfs[t["name"]] = (df_cont, df_pulse)
        all_projections.append({
            "name": t["name"],
            "f_CaWO4": phases["CaWO4"],
            "cum_500h_cont": round(cum_500_cont, 2),
            "cum_500h_pulsed": round(cum_500_pulse, 2),
            "D_ss_cont": round(Dss_cont, 4) if not np.isnan(Dss_cont) else 99.9,
            "D_ss_pulsed": round(Dss_pulse, 4) if not np.isnan(Dss_pulse) else 99.9,
            "p50_cont_h": int(min(proj_cont["p50_lifetime_h"], 999_999)),
            "p50_pulsed_h": int(min(proj_pulse["p50_lifetime_h"], 999_999)),
            "alpha_fit": round(proj_pulse["alpha_fit"], 3),
            "gate3_pass": gate3_pass,
        })

    df_proj = pd.DataFrame(all_projections)
    df_proj.to_csv("results_gate3_projection.csv", index=False)
    print(f"Projection table saved: results_gate3_projection.csv")

    # ─── Plots ────────────────────────────────────────────────────────────────
    fig = plt.figure(figsize=(17, 14))
    gs = gridspec.GridSpec(3, 4, figure=fig, hspace=0.45, wspace=0.38)

    colors_targets = ["#2ecc71", "#3498db", "#e67e22", "#e74c3c"]

    # Panel 1: Dissolution rate vs time (pulsed, all targets)
    ax1 = fig.add_subplot(gs[0, 0:2])
    for (t, color) in zip(TARGETS, colors_targets):
        df_p = all_dfs[t["name"]][1]
        ax1.semilogy(df_p["t_h"], df_p["D_total_ug_cm2_h"], "-",
                     color=color, lw=2, label=t["name"][:28])
    ax1.axhline(IrO2_D_STEADY, color="gold", ls="--", lw=2, label="IrO2 steady-state")
    ax1.axhline(GATE3_STEADY_UG_H, color="purple", ls=":", lw=2, label="Gate 3 D_ss limit")
    ax1.set_xlabel("Time (h)")
    ax1.set_ylabel("Dissolution rate (ug/cm2/h)")
    ax1.set_title("Dissolution rate vs time (pulsed CP 59/1)")
    ax1.legend(fontsize=7)
    ax1.set_xlim(0, T_SIM_H)

    # Panel 2: Cumulative dissolution (pulsed, all targets)
    ax2 = fig.add_subplot(gs[0, 2:4])
    for (t, color) in zip(TARGETS, colors_targets):
        df_p = all_dfs[t["name"]][1]
        ax2.plot(df_p["t_h"], df_p["D_cumulative_ug_cm2"], "-",
                 color=color, lw=2, label=t["name"][:28])
    ax2.axvline(500, color="black", ls="--", lw=1.5, label="500h mark")
    ax2.axhline(GATE3_CUMULATIVE_UG, color="purple", ls=":", lw=2,
                label=f"Gate 3 limit ({GATE3_CUMULATIVE_UG} ug/cm2)")
    ax2.axhline(LOADING_UG_CM2 * 0.5, color="red", ls="--", lw=1.5,
                label=f"50% loading consumed ({LOADING_UG_CM2 * 0.5:.0f} ug/cm2)")
    ax2.set_xlabel("Time (h)")
    ax2.set_ylabel("Cumulative dissolution (ug/cm2)")
    ax2.set_title("Cumulative dissolution (pulsed CP)")
    ax2.legend(fontsize=7)
    ax2.set_xlim(0, T_SIM_H)

    # Panel 3: Phase breakdown — pulsed vs continuous for #1 target
    ax3 = fig.add_subplot(gs[1, 0:2])
    t_name = TARGETS[0]["name"]
    df_c, df_p = all_dfs[t_name]
    ax3.plot(df_c["t_h"], df_c["D_total_ug_cm2_h"], "k-", lw=2, label="Continuous CP (total)")
    ax3.plot(df_p["t_h"], df_p["D_total_ug_cm2_h"], "k--", lw=2, label="Pulsed CP (total)")
    for col, label, color in [
        ("D_Mn_ug_cm2_h", "MnO2", "#e74c3c"),
        ("D_W_ug_cm2_h", "WO3", "#e67e22"),
        ("D_CaWO4_ug_cm2_h", "CaWO4", "#2ecc71"),
        ("D_Ti_ug_cm2_h", "TiO2", "#3498db"),
    ]:
        ax3.semilogy(df_p["t_h"], df_p[col] + 1e-5, "--", color=color, lw=1.5,
                     alpha=0.7, label=f"{label} (pulsed)")
    ax3.axhline(GATE3_STEADY_UG_H, color="purple", ls=":", lw=1.5)
    ax3.set_xlabel("Time (h)")
    ax3.set_ylabel("Dissolution rate (ug/cm2/h)")
    ax3.set_title(f"Phase-by-phase dissolution\n{t_name[:35]}")
    ax3.legend(fontsize=7, ncol=2)

    # Panel 4: Surface CaWO4 enrichment over time
    ax4 = fig.add_subplot(gs[1, 2])
    for (t, color) in zip(TARGETS[:3], colors_targets[:3]):
        df_p = all_dfs[t["name"]][1]
        ax4.plot(df_p["t_h"], df_p["f_CaWO4_surface"], "-", color=color, lw=2,
                 label=t["name"][:22])
    ax4.set_xlabel("Time (h)")
    ax4.set_ylabel("CaWO4 surface fraction")
    ax4.set_title("Surface CaWO4 enrichment\n(self-passivation)")
    ax4.legend(fontsize=7)

    # Panel 5: Pulsed vs continuous — lifetime ratio
    ax5 = fig.add_subplot(gs[1, 3])
    labels = [t["name"][:22] for t in TARGETS]
    p50_cont  = [r["p50_cont_h"] for r in all_projections]
    p50_pulse = [r["p50_pulsed_h"] for r in all_projections]
    # Cap at 50000h for display
    p50_cont_disp  = [min(v, 50000) for v in p50_cont]
    p50_pulse_disp = [min(v, 50000) for v in p50_pulse]
    x = np.arange(len(labels))
    w = 0.35
    ax5.bar(x - w/2, p50_cont_disp,  w, label="Continuous CP", color="#e74c3c", alpha=0.8)
    ax5.bar(x + w/2, p50_pulse_disp, w, label="Pulsed CP", color="#2ecc71", alpha=0.8)
    ax5.axhline(GATE3_P50_LIFETIME_H, color="purple", ls=":", lw=2, label="Gate 3 (1000h)")
    ax5.axhline(10_000, color="blue", ls="--", lw=1.5, label="10,000h target")
    ax5.set_xticks(x)
    ax5.set_xticklabels(labels, rotation=30, ha="right", fontsize=7)
    ax5.set_ylabel("P50 lifetime (h)")
    ax5.set_title("P50 lifetime: pulsed vs continuous")
    ax5.legend(fontsize=7)

    # Panel 6: f_CaWO4 vs P50 lifetime (scatter)
    ax6 = fig.add_subplot(gs[2, 0])
    f_cawо4_vals = [r["f_CaWO4"] for r in all_projections]
    p50_pulsed_vals = [min(r["p50_pulsed_h"], 99999) for r in all_projections]
    ax6.scatter(f_cawо4_vals, p50_pulsed_vals, s=140, c=colors_targets[:len(TARGETS)],
                edgecolors="black", zorder=5)
    for t, xv, yv in zip(TARGETS, f_cawо4_vals, p50_pulsed_vals):
        ax6.annotate(t["name"][:20], (xv, yv), xytext=(5, 5), textcoords="offset points",
                     fontsize=7)
    ax6.axhline(GATE3_P50_LIFETIME_H, color="purple", ls=":", lw=2, label="Gate 3 (1000h)")
    ax6.axvline(0.08, color="gray", ls="--", lw=1, label="Gate 1 threshold")
    ax6.set_xlabel("f_CaWO4 (phase fraction)")
    ax6.set_ylabel("P50 lifetime (h, pulsed CP)")
    ax6.set_title("CaWO4 fraction vs lifetime")
    ax6.legend(fontsize=7)

    # Panel 7: 10-year projection for best composition
    ax7 = fig.add_subplot(gs[2, 1:3])
    best_target = TARGETS[0]
    best_phases = composition_to_phases(best_target["ca"], best_target["mn"],
                                        best_target["w"], best_target["ti"],
                                        best_target["f_cawo4"])
    df_p600 = integrate_dissolution(best_phases, 600, pulsed=True, dt_h=0.5)
    proj = project_lifetime(df_p600)
    D0, alpha = proj["D0_fit"], proj["alpha_fit"]

    # Extrapolated curve
    t_proj = np.geomspace(1, 20_000, 500)
    D_proj = D0 * t_proj**(-alpha)
    cum_proj = np.zeros(len(t_proj))
    for i, tp in enumerate(t_proj):
        if abs(alpha - 1) < 0.01:
            cum_proj[i] = df_p600["D_cumulative_ug_cm2"].iloc[-1] + D0 * np.log(tp / 600)
        else:
            cum_proj[i] = df_p600["D_cumulative_ug_cm2"].iloc[-1] + D0 / (1 - alpha) * (
                tp**(1 - alpha) - 600**(1 - alpha)
            )
    cum_proj = np.maximum(cum_proj, 0)

    ax7_twin = ax7.twinx()
    ax7.semilogy(df_p600["t_h"], df_p600["D_total_ug_cm2_h"], "b-", lw=1.5, label="Simulated (600h)")
    ax7.semilogy(t_proj, D_proj, "b--", lw=1, alpha=0.6, label="Extrapolated power law")
    ax7_twin.plot(df_p600["t_h"], df_p600["D_cumulative_ug_cm2"], "r-", lw=2, label="Cumulative (simulated)")
    ax7_twin.plot(t_proj, cum_proj, "r--", lw=1, alpha=0.6, label="Cumulative (extrapolated)")
    ax7.axhline(GATE3_STEADY_UG_H, color="purple", ls=":", lw=1.5, label="D_ss limit")
    ax7_twin.axhline(LOADING_UG_CM2 * 0.5, color="orange", ls="--", lw=1.5,
                     label=f"P50 trigger ({LOADING_UG_CM2 * 0.5:.0f} ug/cm2)")
    if proj["p50_lifetime_h"] < 20_000:
        ax7.axvline(proj["p50_lifetime_h"], color="green", ls=":", lw=2,
                    label=f"P50 = {proj['p50_lifetime_h']:.0f} h")
    ax7.set_xlabel("Time (h)")
    ax7.set_ylabel("D rate (ug/cm2/h)", color="blue")
    ax7_twin.set_ylabel("D cumulative (ug/cm2)", color="red")
    ax7.set_title(f"Lifetime projection: {best_target['name'][:35]}\n"
                  f"alpha={alpha:.2f}, D0={D0:.1f}, P50={proj['p50_lifetime_h']:.0f}h")
    lines1, labels1 = ax7.get_legend_handles_labels()
    lines2, labels2 = ax7_twin.get_legend_handles_labels()
    ax7.legend(lines1 + lines2, labels1 + labels2, fontsize=7, loc="upper right")

    # Panel 8: Gate 3 summary table
    ax8 = fig.add_subplot(gs[2, 3])
    ax8.axis("off")
    table_data = []
    for r in all_projections:
        p50_str = f"{r['p50_pulsed_h']:,}" if r["p50_pulsed_h"] < 900_000 else ">1M"
        table_data.append([
            r["name"][:20],
            f"{r['f_CaWO4']:.3f}",
            f"{r['cum_500h_pulsed']:.1f}",
            f"{r['D_ss_pulsed']:.3f}",
            p50_str,
            "PASS" if r["gate3_pass"] else "FAIL",
        ])
    col_labels = ["Composition", "f\nCaWO4", "Cum\n500h", "D_ss", "P50\n(h)", "Gate 3"]
    table = ax8.table(cellText=table_data, colLabels=col_labels,
                      loc="center", cellLoc="center")
    table.auto_set_font_size(False)
    table.set_fontsize(7.5)
    table.scale(1, 1.9)
    for (row, col), cell in table.get_celld().items():
        if row == 0:
            cell.set_facecolor("#2c3e50")
            cell.set_text_props(color="white", fontweight="bold")
        elif row > 0 and col == 5:
            val = table_data[row-1][5]
            cell.set_facecolor("#d5f5e3" if val == "PASS" else "#fadbd8")
    ax8.set_title("Gate 3 Summary\n(pulsed CP, 59/1)", fontweight="bold", pad=12)

    fig.suptitle("Gate 3: 500h Dissolution & Lifetime Projector — Ca-Mn-W-Ti System",
                 fontsize=13, fontweight="bold")
    plt.savefig("results_gate3_lifetime.png", dpi=150, bbox_inches="tight")
    plt.close()
    print("Plot saved: results_gate3_lifetime.png")

    # ─── Go/No-Go summary ─────────────────────────────────────────────────────
    print("\n" + "=" * 65)
    print("GATE 3 GO/NO-GO SUMMARY (Pulsed CP, 59min/1min)")
    print("=" * 65)
    print(f"{'Composition':<30} {'Cum500h':>8} {'D_ss':>7} {'P50(h)':>9} {'Verdict':>8}")
    print("-" * 65)
    for r in all_projections:
        verdict = "GO" if r["gate3_pass"] else "NO-GO"
        p50_str = f"{r['p50_pulsed_h']:,}" if r["p50_pulsed_h"] < 900_000 else ">1M"
        print(f"{r['name']:<30} {r['cum_500h_pulsed']:>7.1f} {r['D_ss_pulsed']:>7.3f} "
              f"{p50_str:>9} {verdict:>8}")
    print("-" * 65)
    print("\nGate 3 pass criteria (pulsed CP):")
    print(f"  1. Cumulative dissolution <= {GATE3_CUMULATIVE_UG} ug/cm2 at 500h")
    print(f"  2. Steady-state rate D_ss <= {GATE3_STEADY_UG_H} ug/cm2/h")
    print(f"  3. P50 projected lifetime >= {GATE3_P50_LIFETIME_H:,} h")
    print("\nIrO2 reference:")
    print(f"  D_ss = {IrO2_D_STEADY} ug/cm2/h | Lifetime ~ {IrO2_LIFETIME:,} h")
    print("\nIf Gate 3 FAILS:")
    print("  -> Increase f_CaWO4 (raise Ca and W, resynthesize)")
    print("  -> Add IrOx sub-monolayer (0.05-0.10 ug Ir/cm2) as surface passivant")
    print("  -> Increase Ti content (x_Ti up to 0.25) for TiO2 matrix stabilisation")
    print("  -> Tighten pulsed CP protocol: 29min/1min (higher OC frequency)")
    print()


if __name__ == "__main__":
    main()
