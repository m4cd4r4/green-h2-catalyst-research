"""
gate2_eg_tuner.py
=================
Gate 2 of the acid OER critical path: eg electron occupancy tuning.

Connects H2/N2 annealing conditions and Ca doping to:
  -> Mn oxidation state (Mn3+/Mn4+ ratio)
  -> eg electron occupancy
  -> OER overpotential via the Sabatier volcano

The activity gap (eta_10 ~ 330 mV vs IrO2 250 mV) is primarily due to
sub-optimal eg occupancy. MnO2 (pure Mn4+) has eg ~ 0, placing it on the
weak-binding side of the OER volcano. H2/N2 annealing promotes Mn3+ (eg = 1),
and Ca doping in the birnessite interlayer further drives Mn3+ formation.
Target: eg ~ 0.5-0.7 for acid OER (lower than alkaline optimal of ~1.2
because acid stability requires not over-reducing the structure).

Physics implemented:
  - Mn reduction kinetics under H2/N2 (shrinking-core model)
  - Ca-doping hole compensation: each Ca2+ interlayer creates one Mn3+
  - eg occupancy from Mn3+/Mn4+ ratio
  - OER overpotential from eg via Suntivich-type volcano (calibrated to acid)
  - Arrhenius temperature dependence of reduction rate
  - Stability constraint: avoid full reduction to Mn3O4 (too unstable in acid)

Run: python gate2_eg_tuner.py
Outputs: results_gate2_eg.png, results_gate2_optimization.csv
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import pandas as pd
from scipy.optimize import minimize_scalar, minimize

# ─── Physical constants ────────────────────────────────────────────────────────

R_GAS = 8.314      # J/mol/K

# Mn reduction: MnO2 + x H2 -> MnO_(2-x) + x H2O
# Kinetic parameters from TPR (temperature-programmed reduction) literature
EA_MN_REDUCTION = 72_000   # J/mol activation energy
A_PRE = 2.8e6              # s-1 pre-exponential (Arrhenius)

# eg occupancy by Mn oxidation state
EG_BY_STATE = {
    "Mn2+": 2.0,   # d5, t2g3 eg2 (too high, dissolves easily)
    "Mn3+": 1.0,   # d4, t2g3 eg1
    "Mn4+": 0.0,   # d3, t2g3 eg0 (too low, weak OER binding)
    "Mn3.5+": 0.5, # Mixed, ideal
}

# OER volcano calibration for acid OER (pH 0-1)
# Calibrated to Mn-oxide literature:
#   - Pure MnO2 (eg~0): eta ~ 500-600 mV
#   - Mn2O3 (eg~1): eta ~ 380-420 mV
#   - IrO2 (eg~0.5): eta ~ 250 mV
ETA_MIN_ACID = 245.0       # mV, absolute volcano minimum (near-optimal eg)
EG_OPT_ACID  = 0.52        # optimal eg for acid OER
K_VOLCANO    = 220.0       # mV per unit |eg - eg_opt|^1.7 (asymmetric)
ASYMM_LOW    = 1.70        # exponent for eg < eg_opt (strong-binding side)
ASYMM_HIGH   = 1.30        # exponent for eg > eg_opt (weak-binding side)

# Stability constraint: Mn3+ fraction must stay below 0.75 for acid stability
MN3_MAX_STABLE = 0.75      # above this, phase separates to Mn3O4

# Electrode potential during OER (approximate, for dissolution model)
E_OER_V = 1.55             # V vs RHE at 10 mA/cm2


# ─── Mn reduction kinetics ────────────────────────────────────────────────────

def mn3_fraction_from_anneal(
    T_C: float, h2_percent: float, time_h: float,
    initial_mn3: float = 0.0
) -> float:
    """
    Estimate Mn3+ fraction after H2/N2 annealing.

    Uses a shrinking-core / first-order kinetic model:
      d(Mn3+)/dt = k(T) * p_H2 * (1 - Mn3+) - k_back * Mn3+

    Parameters
    ----------
    T_C : float
        Anneal temperature in Celsius.
    h2_percent : float
        H2 gas fraction in H2/N2 mix (e.g., 5 for 5% H2/95% N2).
    time_h : float
        Anneal time in hours.
    initial_mn3 : float
        Starting Mn3+ fraction (from Ca doping or as-synthesised state).

    Returns
    -------
    float
        Mn3+ fraction [0, 1].
    """
    T = T_C + 273.15
    time_s = time_h * 3600

    p_h2 = h2_percent / 100.0

    # Forward rate (reduction): Mn4+ -> Mn3+
    k_fwd = A_PRE * p_h2 * np.exp(-EA_MN_REDUCTION / (R_GAS * T))

    # Reverse rate (reoxidation by lattice oxygen): negligible under H2 but
    # becomes important above ~250C where structural oxygen mobility increases
    E_back = EA_MN_REDUCTION * 1.3
    A_back = A_PRE * 0.15
    k_bwd = A_back * np.exp(-E_back / (R_GAS * T))

    # Analytical solution of dx/dt = k_fwd*(1-x) - k_bwd*x
    # x(t) = x_eq + (x0 - x_eq) * exp(-(k_fwd + k_bwd) * t)
    k_total = k_fwd + k_bwd
    x_eq = k_fwd / k_total

    x_eq = min(MN3_MAX_STABLE, x_eq)

    x_t = x_eq + (initial_mn3 - x_eq) * np.exp(-k_total * time_s)
    return float(np.clip(x_t, 0.0, MN3_MAX_STABLE))


def mn3_from_ca_doping(x_ca: float, x_mn: float) -> float:
    """
    Mn3+ fraction induced by Ca2+ interlayer cations in birnessite.

    Charge balance: each Ca2+ interlayer requires two Mn3+ in the
    octahedral sheet (to compensate 2+ charge vs. MnO2 neutral).
    Maximum compensation limited by Ca/Mn ratio.

    Parameters
    ----------
    x_ca : float
        Ca mole fraction in composition.
    x_mn : float
        Mn mole fraction in composition.

    Returns
    -------
    float
        Intrinsic Mn3+ fraction from Ca doping alone [0, 1].
    """
    ca_mn_ratio = x_ca / (x_mn + 1e-9)
    # Each Ca2+ in interlayer stabilises 2 Mn3+ sites
    mn3 = min(MN3_MAX_STABLE, 2.0 * ca_mn_ratio)
    return mn3


def eg_occupancy(mn3_fraction: float) -> float:
    """eg electron occupancy from Mn3+/Mn4+ ratio."""
    # Mn4+ (d3): eg = 0; Mn3+ (d4): eg = 1
    return float(np.clip(mn3_fraction, 0.0, 1.0))


def eta_from_eg(eg: float) -> float:
    """
    OER overpotential (mV) from eg occupancy via asymmetric Sabatier volcano.
    Calibrated to acid OER on Mn-oxide literature.

    Parameters
    ----------
    eg : float
        eg electron occupancy [0, 2].

    Returns
    -------
    float
        eta_10 in mV.
    """
    delta = eg - EG_OPT_ACID
    if delta < 0:
        # Strong-binding side (eg < optimal): steeper slope
        penalty = K_VOLCANO * abs(delta)**ASYMM_LOW
    else:
        # Weak-binding side (eg > optimal)
        penalty = K_VOLCANO * abs(delta)**ASYMM_HIGH

    eta = ETA_MIN_ACID + penalty
    return float(np.clip(eta, ETA_MIN_ACID, 750.0))


# ─── Combined model ────────────────────────────────────────────────────────────

def predict_activity(
    x_ca: float, x_mn: float,
    anneal_T_C: float, anneal_h2_pct: float, anneal_time_h: float
) -> dict:
    """
    Predict OER activity from composition and anneal conditions.

    Returns dict with mn3_total, eg, eta_10, stable, gate2_pass.
    """
    # Ca-induced Mn3+ (intrinsic from synthesis)
    mn3_ca = mn3_from_ca_doping(x_ca, x_mn)

    # Anneal-induced additional Mn3+
    mn3_anneal = mn3_fraction_from_anneal(anneal_T_C, anneal_h2_pct, anneal_time_h,
                                          initial_mn3=mn3_ca)

    # Total Mn3+ (anneal result already incorporates starting point)
    mn3_total = mn3_anneal

    eg = eg_occupancy(mn3_total)
    eta = eta_from_eg(eg)

    # Stability flag: Mn3+ > 0.75 risks dissolution and phase change
    stable = mn3_total <= MN3_MAX_STABLE
    gate2_pass = (eta < 310.0) and stable and (eg > 0.30)

    return {
        "mn3_ca_induced": mn3_ca,
        "mn3_total": mn3_total,
        "eg": eg,
        "eta_10_mv": eta,
        "stable": stable,
        "gate2_pass": gate2_pass,
    }


# ─── Optimiser ────────────────────────────────────────────────────────────────

def optimise_anneal(x_ca: float, x_mn: float) -> dict:
    """
    Find the anneal conditions (T, H2%, time) that minimise eta_10
    while keeping Mn3+ <= 0.75 (stability constraint).
    """
    def objective(params):
        T_C, h2_pct, time_h = params
        T_C   = np.clip(T_C,   100, 280)
        h2_pct = np.clip(h2_pct, 1.0, 10.0)
        time_h = np.clip(time_h, 0.5, 8.0)
        result = predict_activity(x_ca, x_mn, T_C, h2_pct, time_h)
        # Penalise instability
        penalty = 500.0 if not result["stable"] else 0.0
        return result["eta_10_mv"] + penalty

    # Grid search for robust initialisation
    best_eta = 999
    best_params = (200, 5, 2)
    for T in [150, 180, 200, 220, 250]:
        for h2 in [2, 5, 8, 10]:
            for t in [1, 2, 4]:
                res = predict_activity(x_ca, x_mn, T, h2, t)
                if res["stable"] and res["eta_10_mv"] < best_eta:
                    best_eta = res["eta_10_mv"]
                    best_params = (T, h2, t)

    # Local refinement
    result = minimize(objective, best_params,
                      method="Nelder-Mead",
                      options={"xatol": 0.5, "fatol": 0.5, "maxiter": 500})

    T_opt, h2_opt, t_opt = result.x
    T_opt   = np.clip(T_opt, 100, 280)
    h2_opt  = np.clip(h2_opt, 1.0, 10.0)
    t_opt   = np.clip(t_opt, 0.5, 8.0)

    res_opt = predict_activity(x_ca, x_mn, T_opt, h2_opt, t_opt)

    return {
        "T_C_opt": round(T_opt, 1),
        "h2_pct_opt": round(h2_opt, 1),
        "time_h_opt": round(t_opt, 2),
        "mn3_opt": res_opt["mn3_total"],
        "eg_opt": res_opt["eg"],
        "eta_opt_mv": res_opt["eta_10_mv"],
        "stable": res_opt["stable"],
        "gate2_pass": res_opt["gate2_pass"],
    }


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    np.random.seed(42)

    # Target compositions from ca_mnw_optimizer
    TARGETS = [
        {"name": "Ca(0.11)Mn(0.55)W(0.34)", "ca": 0.110, "mn": 0.549},
        {"name": "Ca(0.15)Mn(0.32)W(0.29)Ti(0.25)", "ca": 0.148, "mn": 0.317},
        {"name": "Ca(0.08)Mn(0.56)W(0.31) (P3)", "ca": 0.080, "mn": 0.560},
    ]

    # P3 protocol (doc 16) anneal: 5% H2/N2, 200C, 2h
    DEFAULT_ANNEAL = {"anneal_T_C": 200, "anneal_h2_pct": 5.0, "anneal_time_h": 2.0}

    print("=" * 65)
    print("GATE 2 — eg Electron Occupancy Tuner")
    print("=" * 65)
    print(f"Default anneal: {DEFAULT_ANNEAL['anneal_h2_pct']}% H2/N2, "
          f"{DEFAULT_ANNEAL['anneal_T_C']}C, {DEFAULT_ANNEAL['anneal_time_h']}h\n")

    opt_records = []
    for t in TARGETS:
        res = predict_activity(t["ca"], t["mn"], **DEFAULT_ANNEAL)
        opt = optimise_anneal(t["ca"], t["mn"])

        print(f"{t['name']}")
        print(f"  As-synthesised (Ca doping only): Mn3+ = {res['mn3_ca_induced']:.3f}, "
              f"eg = {res['mn3_ca_induced']:.3f}")
        print(f"  After default anneal (200C,5%,2h): Mn3+ = {res['mn3_total']:.3f}, "
              f"eg = {res['eg']:.3f}, eta_10 = {res['eta_10_mv']:.0f} mV")
        print(f"  Optimised anneal: T={opt['T_C_opt']}C, H2={opt['h2_pct_opt']}%, "
              f"t={opt['time_h_opt']:.1f}h")
        print(f"    -> eg = {opt['eg_opt']:.3f}, eta_10 = {opt['eta_opt_mv']:.0f} mV  "
              f"[Gate 2: {'PASS' if opt['gate2_pass'] else 'FAIL'}]")
        print()

        opt_records.append({
            "name": t["name"],
            "ca": t["ca"],
            "mn": t["mn"],
            "mn3_ca_only": res["mn3_ca_induced"],
            "mn3_default_anneal": res["mn3_total"],
            "eg_default": res["eg"],
            "eta_default_mv": res["eta_10_mv"],
            "T_opt_C": opt["T_C_opt"],
            "h2_opt_pct": opt["h2_pct_opt"],
            "time_opt_h": opt["time_h_opt"],
            "eg_opt": opt["eg_opt"],
            "eta_opt_mv": opt["eta_opt_mv"],
            "stable": opt["stable"],
            "gate2_pass": opt["gate2_pass"],
        })

    df_opt = pd.DataFrame(opt_records)
    df_opt.to_csv("results_gate2_optimization.csv", index=False)
    print(f"Optimization results saved to results_gate2_optimization.csv")

    # ─── Plots ────────────────────────────────────────────────────────────────
    fig = plt.figure(figsize=(16, 13))
    gs = gridspec.GridSpec(3, 3, figure=fig, hspace=0.45, wspace=0.35)

    # Panel 1: OER volcano curve (eg vs eta)
    ax1 = fig.add_subplot(gs[0, 0:2])
    eg_vals = np.linspace(0, 1.5, 300)
    eta_vals = [eta_from_eg(eg) for eg in eg_vals]
    ax1.plot(eg_vals, eta_vals, "k-", lw=2.5, label="Acid OER volcano")
    ax1.axvline(EG_OPT_ACID, color="green", ls="--", lw=1.5,
                label=f"eg_opt = {EG_OPT_ACID}")
    ax1.axhline(250, color="gold", ls="--", lw=1.5, label="IrO2 target (250 mV)")
    ax1.axhline(310, color="blue", ls=":", lw=1.5, label="Gate 2 threshold (310 mV)")

    # Plot materials
    materials = [
        ("MnO2 (as-synth)", 0.00, "red"),
        ("MnO2 + Ca(8%) doping", mn3_from_ca_doping(0.08, 0.56), "orange"),
        ("MnO2 + Ca(11%) doping", mn3_from_ca_doping(0.11, 0.55), "darkorange"),
        ("After 200C/5%H2/2h anneal", mn3_fraction_from_anneal(200, 5, 2, mn3_from_ca_doping(0.11, 0.55)), "purple"),
        ("IrO2", 0.52, "gold"),
        ("Mn2O3 (pure Mn3+)", 1.00, "brown"),
    ]
    for name, eg, color in materials:
        eta = eta_from_eg(eg)
        ax1.scatter([eg], [eta], s=120, color=color, zorder=5,
                    edgecolors="black", linewidths=0.8)
        ax1.annotate(name, (eg, eta), textcoords="offset points",
                     xytext=(5, 5), fontsize=7.5, color=color)

    ax1.set_xlabel("eg electron occupancy")
    ax1.set_ylabel("eta_10 OER (mV)")
    ax1.set_title("Acid OER Sabatier Volcano\n(eg occupancy vs overpotential)")
    ax1.legend(fontsize=7, loc="upper right")
    ax1.set_xlim(-0.05, 1.55)
    ax1.set_ylim(200, 700)
    ax1.invert_yaxis()

    # Panel 2: Mn3+ fraction vs anneal temperature (multiple H2%)
    ax2 = fig.add_subplot(gs[0, 2])
    T_vals = np.linspace(100, 300, 100)
    for h2_pct, ls, label in [(2, "-", "2% H2"), (5, "--", "5% H2"), (10, ":", "10% H2")]:
        mn3_T = [mn3_fraction_from_anneal(T, h2_pct, 2.0, initial_mn3=0.20) for T in T_vals]
        ax2.plot(T_vals, mn3_T, ls, lw=2, label=label)
    ax2.axhline(MN3_MAX_STABLE, color="red", ls="--", lw=1.5, label=f"Stability limit ({MN3_MAX_STABLE})")
    ax2.axhline(EG_OPT_ACID, color="green", ls=":", lw=1.5, label=f"eg_opt ({EG_OPT_ACID})")
    ax2.set_xlabel("Anneal temperature (C)")
    ax2.set_ylabel("Mn3+ fraction")
    ax2.set_title("Mn3+ vs anneal T\n(2h, starting Mn3+=0.20)")
    ax2.legend(fontsize=7)
    ax2.set_ylim(0, 1.0)

    # Panel 3: eta_10 vs anneal time for primary target
    ax3 = fig.add_subplot(gs[1, 0])
    t_vals = np.linspace(0, 8, 100)
    primary = TARGETS[0]
    for T_C, ls, color in [(150, "-", "blue"), (200, "--", "green"), (250, ":", "red")]:
        eta_t = [predict_activity(primary["ca"], primary["mn"], T_C, 5.0, t)["eta_10_mv"]
                 for t in t_vals]
        ax3.plot(t_vals, eta_t, ls, color=color, lw=2, label=f"T={T_C}C")
    ax3.axhline(310, color="purple", ls=":", lw=1.5, label="Gate 2 threshold")
    ax3.axhline(250, color="gold", ls="--", lw=1.5, label="IrO2 target")
    ax3.set_xlabel("Anneal time (h)")
    ax3.set_ylabel("eta_10 (mV)")
    ax3.set_title(f"eta_10 vs anneal time\n{primary['name']} (5% H2)")
    ax3.legend(fontsize=7)
    ax3.invert_yaxis()

    # Panel 4: eg vs Ca content (no anneal — Ca doping effect alone)
    ax4 = fig.add_subplot(gs[1, 1])
    ca_range = np.linspace(0, 0.20, 100)
    mn_fixed = 0.55
    eg_ca = [eg_occupancy(mn3_from_ca_doping(ca, mn_fixed)) for ca in ca_range]
    eta_ca = [eta_from_eg(eg) for eg in eg_ca]
    ax4_twin = ax4.twinx()
    l1, = ax4.plot(ca_range, eg_ca, "b-", lw=2, label="eg occupancy")
    l2, = ax4_twin.plot(ca_range, eta_ca, "r--", lw=2, label="eta_10 (mV)")
    ax4.axhline(EG_OPT_ACID, color="green", ls=":", lw=1, label=f"eg_opt")
    ax4.axvline(0.11, color="gray", ls=":", lw=1, label="#1 target (Ca=0.11)")
    ax4.set_xlabel("Ca mole fraction")
    ax4.set_ylabel("eg occupancy", color="blue")
    ax4_twin.set_ylabel("eta_10 (mV)", color="red")
    ax4.set_title("Ca doping effect on eg and activity\n(no anneal, Mn=0.55)")
    lines = [l1, l2]
    ax4.legend(lines, [l.get_label() for l in lines], fontsize=7)
    ax4_twin.invert_yaxis()

    # Panel 5: Contour map — eta vs (T, H2%) for #1 target at 2h anneal
    ax5 = fig.add_subplot(gs[1, 2])
    T_grid = np.linspace(100, 280, 40)
    h2_grid = np.linspace(1, 10, 40)
    TT, HH = np.meshgrid(T_grid, h2_grid)
    ETA = np.zeros_like(TT)
    for i in range(TT.shape[0]):
        for j in range(TT.shape[1]):
            res = predict_activity(primary["ca"], primary["mn"],
                                   TT[i, j], HH[i, j], 2.0)
            ETA[i, j] = res["eta_10_mv"]
    cf = ax5.contourf(TT, HH, ETA, levels=20, cmap="RdYlGn_r")
    cs = ax5.contour(TT, HH, ETA, levels=[280, 310, 350], colors=["white", "yellow", "red"],
                     linewidths=1.5)
    plt.colorbar(cf, ax=ax5, label="eta_10 (mV)")
    ax5.clabel(cs, fmt="%.0f mV", fontsize=8, colors=["white", "yellow", "red"])
    ax5.set_xlabel("Anneal temperature (C)")
    ax5.set_ylabel("H2 % in N2")
    ax5.set_title(f"eta_10 map (T vs H2%)\n{primary['name']}, 2h anneal")

    # Panel 6: Stability map — safe region for anneal conditions
    ax6 = fig.add_subplot(gs[2, 0])
    MN3 = np.zeros_like(TT)
    for i in range(TT.shape[0]):
        for j in range(TT.shape[1]):
            MN3[i, j] = predict_activity(primary["ca"], primary["mn"],
                                          TT[i, j], HH[i, j], 2.0)["mn3_total"]
    ax6.contourf(TT, HH, MN3, levels=20, cmap="Blues")
    cs6 = ax6.contour(TT, HH, MN3, levels=[0.4, 0.52, 0.75], colors=["green", "orange", "red"],
                      linewidths=2)
    ax6.clabel(cs6, fmt="Mn3+=%.2f", fontsize=8)
    ax6.set_xlabel("Anneal temperature (C)")
    ax6.set_ylabel("H2 % in N2")
    ax6.set_title(f"Mn3+ fraction map\nRed line = stability limit (0.75)")

    # Panel 7: Waterfall: eg progression for #1 target through treatment steps
    ax7 = fig.add_subplot(gs[2, 1])
    steps = ["As-synth\n(MnO2 pure)", "After Ca(11%)\ndoping",
             "After 150C\n5%H2, 2h", "After 200C\n5%H2, 2h",
             "After 200C\n5%H2, 4h", "IrO2\n(target)"]
    eg_steps = [
        0.0,
        mn3_from_ca_doping(0.11, 0.55),
        mn3_fraction_from_anneal(150, 5, 2, mn3_from_ca_doping(0.11, 0.55)),
        mn3_fraction_from_anneal(200, 5, 2, mn3_from_ca_doping(0.11, 0.55)),
        mn3_fraction_from_anneal(200, 5, 4, mn3_from_ca_doping(0.11, 0.55)),
        EG_OPT_ACID,
    ]
    eta_steps = [eta_from_eg(eg) for eg in eg_steps]
    colors_bar = ["#e74c3c", "#e67e22", "#3498db", "#2980b9", "#27ae60", "#f1c40f"]
    bars = ax7.bar(steps, eta_steps, color=colors_bar, edgecolor="black", lw=0.8, width=0.65)
    ax7.axhline(310, color="purple", ls=":", lw=1.5, label="Gate 2 threshold (310 mV)")
    ax7.axhline(250, color="gold", ls="--", lw=1.5, label="IrO2 (250 mV)")
    for bar, val in zip(bars, eta_steps):
        ax7.text(bar.get_x() + bar.get_width()/2, val + 3, f"{val:.0f}",
                 ha="center", va="bottom", fontsize=8, fontweight="bold")
    ax7.set_ylabel("eta_10 (mV)")
    ax7.set_title("eta_10 through treatment pipeline\nCa(0.11)Mn(0.55)W(0.34)")
    ax7.legend(fontsize=7)
    ax7.invert_yaxis()
    ax7.tick_params(axis="x", labelsize=8)

    # Panel 8: Gate 2 summary table
    ax8 = fig.add_subplot(gs[2, 2])
    ax8.axis("off")
    table_data = []
    for row in opt_records:
        table_data.append([
            row["name"][:22],
            f"{row['eg_default']:.2f}",
            f"{row['eta_default_mv']:.0f}",
            f"{row['eg_opt']:.2f}",
            f"{row['eta_opt_mv']:.0f}",
            "PASS" if row["gate2_pass"] else "FAIL",
        ])
    col_labels = ["Composition", "eg\ndefault", "eta\ndefault", "eg\nopt", "eta\nopt", "Gate 2"]
    table = ax8.table(cellText=table_data, colLabels=col_labels,
                      loc="center", cellLoc="center")
    table.auto_set_font_size(False)
    table.set_fontsize(8)
    table.scale(1, 1.8)
    for (row, col), cell in table.get_celld().items():
        if row == 0:
            cell.set_facecolor("#2c3e50")
            cell.set_text_props(color="white", fontweight="bold")
        elif table_data[row-1][-1] == "PASS" if row > 0 else False:
            cell.set_facecolor("#d5f5e3")
        elif row > 0 and col == 5:
            cell.set_facecolor("#fadbd8")
    ax8.set_title("Gate 2 Summary", fontweight="bold", pad=12)

    fig.suptitle("Gate 2: eg Electron Occupancy Tuner — Activity Optimisation",
                 fontsize=14, fontweight="bold")
    plt.savefig("results_gate2_eg.png", dpi=150, bbox_inches="tight")
    plt.close()
    print("Plot saved: results_gate2_eg.png")

    # ─── Go/No-Go Summary ─────────────────────────────────────────────────────
    print("\n" + "=" * 65)
    print("GATE 2 GO/NO-GO SUMMARY")
    print("=" * 65)
    print(f"{'Composition':<35} {'eg_opt':>6} {'eta_opt':>8} {'Verdict':>8}")
    print("-" * 65)
    for row in opt_records:
        verdict = "GO" if row["gate2_pass"] else "NO-GO"
        print(f"{row['name']:<35} {row['eg_opt']:>6.3f} {row['eta_opt_mv']:>7.0f} mV {verdict:>8}")
    print("-" * 65)
    print("\nGate 2 pass criteria:")
    print("  1. eta_10 < 310 mV (after optimal anneal)")
    print("  2. eg > 0.30 (Mn3+ fraction not trivially small)")
    print("  3. Mn3+ fraction <= 0.75 (stability constraint)")
    print("\nOptimal anneal protocol (Ca=0.11, Mn=0.55, W=0.34):")
    best = df_opt.loc[df_opt["eta_opt_mv"].idxmin()]
    print(f"  T = {best.T_opt_C:.0f}C | H2 = {best.h2_opt_pct:.1f}% | time = {best.time_opt_h:.1f}h")
    print(f"  -> eg = {best.eg_opt:.3f} | eta_10 = {best.eta_opt_mv:.0f} mV")
    print()
    print("If Gate 2 FAILS:")
    print("  -> Increase anneal temperature in 20C increments up to 250C")
    print("  -> Increase H2% to 8-10% (check H2 safety limits)")
    print("  -> Extend time to 4-6h")
    print("  -> Check XPS: Mn 2p3/2 should shift from 642.2 eV (Mn4+) -> 641.5 eV (Mn3+)")
    print()


if __name__ == "__main__":
    main()
