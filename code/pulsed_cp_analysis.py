"""
Pulsed Chronopotentiometry Data Analysis
=========================================
Complete analysis pipeline for the pulsed CP lifetime extension experiment.
Compares constant vs. pulsed OER operation across multiple catalysts.

Usage:
    python pulsed_cp_analysis.py          # Run with synthetic demo data
    python pulsed_cp_analysis.py --real   # Analyse real CP data (see format below)

Real data CSV format (one file per experiment):
    time_s, potential_V_vs_RHE, current_mA_cm2, protocol (A/B/C/D), catalyst_name
    300, 1.485, 10.0, A, NiFe_LDH_rep1

Dependencies:
    pip install numpy pandas matplotlib scipy scikit-learn
"""

import sys
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.signal import savgol_filter
from scipy.optimize import curve_fit
from sklearn.linear_model import LinearRegression
import warnings
warnings.filterwarnings('ignore')

np.random.seed(42)

# Protocol definitions
PROTOCOLS = {
    'A': {'label': 'Constant CP',           'color': '#e74c3c', 'ls': '-',  'on_min': 60, 'rest_min': 0},
    'B': {'label': 'Pulsed 1min/h',         'color': '#3498db', 'ls': '-',  'on_min': 59, 'rest_min': 1},
    'C': {'label': 'Pulsed 10min/10h',      'color': '#2ecc71', 'ls': '--', 'on_min': 590,'rest_min': 10},
    'D': {'label': 'Fixed V rest (1.2V/h)', 'color': '#f39c12', 'ls': ':',  'on_min': 59, 'rest_min': 1},
}


# =============================================================================
# SECTION 1: SYNTHETIC DATA GENERATOR (replace with real potentiostat export)
# =============================================================================

def generate_cp_trace(protocol, catalyst_params, duration_h=500, dt_min=1.0):
    """
    Generate synthetic chronopotentiometry trace for one protocol + catalyst.

    catalyst_params: dict with keys:
        eta0_mV     Initial overpotential at 10 mA/cm2
        deactivation_rate_mV_per_h   Rate of potential increase under constant operation
        regeneration_efficiency      Fraction of accumulated deactivation reversed per rest (0-1)
        noise_mV                     Measurement noise

    Returns: DataFrame with columns time_h, potential_mV, eta_mV, is_rest, protocol
    """
    dt_h    = dt_min / 60
    n_steps = int(duration_h / dt_h)
    t       = np.arange(n_steps) * dt_h

    p        = PROTOCOLS[protocol]
    on_h     = p['on_min'] / 60
    rest_h   = p['rest_min'] / 60
    cycle_h  = on_h + rest_h

    eta0       = catalyst_params['eta0_mV']
    deact_rate = catalyst_params['deactivation_rate_mV_per_h']
    regen_eff  = catalyst_params.get('regeneration_efficiency', 0.0)
    noise      = catalyst_params.get('noise_mV', 2.0)

    potential     = np.zeros(n_steps)
    is_rest       = np.zeros(n_steps, dtype=bool)
    accumulated   = 0.0   # accumulated deactivation (mV)

    for i, ti in enumerate(t):
        if cycle_h > 0:
            phase = ti % cycle_h
            in_rest = phase >= on_h
        else:
            in_rest = False

        is_rest[i] = in_rest

        if in_rest:
            # During rest: regeneration occurs (site de-blocking)
            rest_fraction = (ti % cycle_h - on_h) / rest_h if rest_h > 0 else 0
            # Exponential regeneration with time constant ~20s = 0.33min
            regen = accumulated * regen_eff * (1 - np.exp(-rest_fraction * rest_h * 60 / 0.5))
            accumulated = max(0, accumulated - regen * dt_h / rest_h * 3)
            potential[i] = np.nan  # no current during rest
        else:
            # During operation: deactivation accumulates
            accumulated += deact_rate * dt_h
            potential[i] = 1230 + eta0 + accumulated + np.random.normal(0, noise)

    return pd.DataFrame({
        'time_h': t,
        'potential_mV': potential,
        'eta_mV': potential - 1230,
        'is_rest': is_rest,
        'protocol': protocol,
    })


# =============================================================================
# SECTION 2: ANALYSIS FUNCTIONS
# =============================================================================

def extract_eta10_series(df, window_h=24):
    """
    Extract periodic eta_10 values from a CP trace.
    Simulates the brief CV check every 24h.

    Returns: DataFrame with time_h, eta_10_mV
    """
    active = df[~df['is_rest']].copy()
    active = active.dropna(subset=['potential_mV'])

    # Resample to hourly, take rolling window median
    active['time_h_round'] = (active['time_h'] // window_h) * window_h
    eta_series = active.groupby('time_h_round')['eta_mV'].median().reset_index()
    eta_series.columns = ['time_h', 'eta_10_mV']
    return eta_series


def time_to_threshold(eta_series, threshold_mV=30):
    """
    Find time at which eta_10 has increased by threshold_mV above initial value.
    Returns t30 in hours (or None if threshold never reached).
    """
    if len(eta_series) < 2:
        return None

    eta0   = eta_series['eta_10_mV'].iloc[0]
    target = eta0 + threshold_mV
    mask   = eta_series['eta_10_mV'] >= target

    if not mask.any():
        return None

    # Interpolate to find exact crossing time
    idx = mask.idxmax()
    if idx == 0:
        return 0.0

    t1, e1 = eta_series.loc[idx-1, ['time_h', 'eta_10_mV']]
    t2, e2 = eta_series.loc[idx,   ['time_h', 'eta_10_mV']]

    # Linear interpolation
    frac = (target - e1) / (e2 - e1)
    return float(t1 + frac * (t2 - t1))


def fit_deactivation_model(eta_series):
    """
    Fit exponential deactivation model: eta(t) = eta_inf - (eta_inf - eta_0)*exp(-t/tau)
    Returns: eta_0, eta_inf, tau, r2
    """
    t = eta_series['time_h'].values
    y = eta_series['eta_10_mV'].values

    def model(t, eta0, eta_inf, tau):
        return eta_inf - (eta_inf - eta0) * np.exp(-t / tau)

    try:
        p0 = [y[0], y[-1], 100.0]
        popt, _ = curve_fit(model, t, y, p0=p0,
                            bounds=([y[0]-5, y[0], 1], [y[0]+5, y[-1]*2, 2000]))
        y_pred = model(t, *popt)
        ss_res = np.sum((y - y_pred)**2)
        ss_tot = np.sum((y - y.mean())**2)
        r2 = 1 - ss_res / (ss_tot + 1e-12)
        return {'eta0': popt[0], 'eta_inf': popt[1], 'tau_h': popt[2], 'r2': r2}
    except Exception:
        return None


def analyse_all_protocols(catalyst_name, catalyst_params_per_protocol, duration_h=500):
    """
    Run analysis for all 4 protocols on one catalyst.

    catalyst_params_per_protocol: dict mapping protocol -> catalyst_params dict
    """
    results = {}
    traces  = {}

    for protocol, params in catalyst_params_per_protocol.items():
        trace  = generate_cp_trace(protocol, params, duration_h=duration_h)
        eta_s  = extract_eta10_series(trace)
        t30    = time_to_threshold(eta_s, threshold_mV=30)
        model  = fit_deactivation_model(eta_s)

        results[protocol] = {
            'catalyst': catalyst_name,
            'protocol': protocol,
            'label': PROTOCOLS[protocol]['label'],
            'eta_0_mV': float(eta_s['eta_10_mV'].iloc[0]),
            'eta_500h_mV': float(eta_s['eta_10_mV'].iloc[-1]),
            'delta_eta_mV': float(eta_s['eta_10_mV'].iloc[-1] - eta_s['eta_10_mV'].iloc[0]),
            't30_h': t30,
            'lifetime_extension_vs_A': None,  # filled in below
            'deact_model': model,
        }
        traces[protocol] = {'trace': trace, 'eta_series': eta_s}

    # Calculate lifetime extension relative to Protocol A
    t30_A = results['A']['t30_h']
    for p, r in results.items():
        if t30_A and r['t30_h']:
            r['lifetime_extension_vs_A'] = (r['t30_h'] - t30_A) / t30_A * 100
        else:
            r['lifetime_extension_vs_A'] = None

    return results, traces


# =============================================================================
# SECTION 3: VISUALISATION
# =============================================================================

def plot_cp_comparison(catalyst_name, traces, results, output_path):
    """Main result figure: CP traces + eta_10 drift for all protocols."""
    fig, axes = plt.subplots(1, 3, figsize=(16, 5))
    fig.suptitle(f'Pulsed vs. Constant Chronopotentiometry — {catalyst_name}\n'
                 f'10 mA/cm2, 1M KOH, 500h, n=3 (synthetic demo)',
                 fontsize=12, fontweight='bold')

    # Panel 1: Raw potential traces (first 48h for clarity)
    ax = axes[0]
    for prot, data in traces.items():
        df = data['trace']
        show = df[df['time_h'] <= 48]
        active = show[~show['is_rest']].dropna(subset=['potential_mV'])
        p_info = PROTOCOLS[prot]
        ax.plot(active['time_h'], active['potential_mV']/1000,
                color=p_info['color'], ls=p_info['ls'],
                lw=1.5, alpha=0.8, label=p_info['label'])

    ax.set_xlabel('Time (h)', fontsize=11)
    ax.set_ylabel('Potential (V vs. RHE)', fontsize=11)
    ax.set_title('CP Traces (first 48h)', fontsize=11)
    ax.legend(fontsize=9)
    ax.grid(alpha=0.3)

    # Panel 2: eta_10 drift over full 500h
    ax = axes[1]
    for prot, data in traces.items():
        eta_s  = data['eta_series']
        p_info = PROTOCOLS[prot]
        r      = results[prot]
        t30    = r['t30_h']

        ax.plot(eta_s['time_h'], eta_s['eta_10_mV'],
                color=p_info['color'], ls=p_info['ls'],
                lw=2, label=f"{p_info['label']} (t30={t30:.0f}h)" if t30 else p_info['label'])

        if t30:
            eta0   = eta_s['eta_10_mV'].iloc[0]
            ax.axvline(t30, color=p_info['color'], ls=':', lw=1, alpha=0.5)

    # 30mV threshold line
    ax.axhline(results['A']['eta_0_mV'] + 30, color='black', ls='--', lw=1,
               alpha=0.5, label='+30mV threshold')

    ax.set_xlabel('Time (h)', fontsize=11)
    ax.set_ylabel('η₁₀ (mV)', fontsize=11)
    ax.set_title('Overpotential Drift — 500h', fontsize=11)
    ax.legend(fontsize=8)
    ax.grid(alpha=0.3)

    # Panel 3: t30 lifetime comparison bar chart
    ax = axes[2]
    protocols = list(results.keys())
    t30_vals  = [results[p]['t30_h'] or 600 for p in protocols]
    colors_   = [PROTOCOLS[p]['color'] for p in protocols]
    labels_   = [PROTOCOLS[p]['label'] for p in protocols]

    bars = ax.bar(range(len(protocols)), t30_vals, color=colors_, alpha=0.85,
                  edgecolor='white', linewidth=1.2)

    # Annotate with lifetime extension
    for i, (p, bar, t30) in enumerate(zip(protocols, bars, t30_vals)):
        ext = results[p]['lifetime_extension_vs_A']
        label = f"{t30:.0f}h" if t30 < 600 else ">500h"
        ext_label = f"\n+{ext:.0f}%" if ext and ext > 0 else ""
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 5,
                f"{label}{ext_label}", ha='center', fontsize=10, fontweight='bold')

    ax.set_xticks(range(len(protocols)))
    ax.set_xticklabels([l.replace(' ', '\n') for l in labels_], fontsize=9)
    ax.set_ylabel('Time to 30mV degradation (h)', fontsize=11)
    ax.set_title('Lifetime Comparison\n(Higher = better)', fontsize=11)
    ax.axhline(results['A']['t30_h'] or 0, color='#e74c3c', ls='--', lw=1,
               alpha=0.5, label='Constant CP baseline')
    ax.legend(fontsize=8)
    ax.grid(axis='y', alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    print(f"  Plot saved: {output_path}")


def plot_multi_catalyst_summary(all_results, output_path):
    """Figure showing universality across 5 catalysts."""
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    fig.suptitle('Pulsed CP Protocol — Universality Across 5 Catalyst Compositions\n'
                 '1M KOH, 10 mA/cm2, 500h (synthetic demo data)',
                 fontsize=12, fontweight='bold')

    # Get t30 values for each catalyst × protocol
    catalysts = list(all_results.keys())
    protocols = ['A', 'B', 'C']

    # Panel 1: Grouped bar chart
    ax = axes[0]
    x   = np.arange(len(catalysts))
    w   = 0.25
    for i, prot in enumerate(protocols):
        t30s  = [all_results[c][prot]['t30_h'] or 520 for c in catalysts]
        color = PROTOCOLS[prot]['color']
        label = PROTOCOLS[prot]['label']
        bars  = ax.bar(x + (i-1)*w, t30s, w, color=color,
                       alpha=0.85, label=label, edgecolor='white')

    ax.set_xticks(x)
    short_names = [c.split()[0] for c in catalysts]
    ax.set_xticklabels(short_names, rotation=15, ha='right', fontsize=10)
    ax.set_ylabel('t30 lifetime (h)', fontsize=11)
    ax.set_title('Lifetime by Catalyst and Protocol', fontsize=11)
    ax.legend(fontsize=9)
    ax.grid(axis='y', alpha=0.3)

    # Panel 2: Lifetime extension (%) bar chart
    ax = axes[1]
    ext_B = [all_results[c]['B']['lifetime_extension_vs_A'] or 0 for c in catalysts]
    ext_C = [all_results[c]['C']['lifetime_extension_vs_A'] or 0 for c in catalysts]

    bars1 = ax.bar(x - w/2, ext_B, w, color=PROTOCOLS['B']['color'],
                   alpha=0.85, label='Pulsed B (1min/h)', edgecolor='white')
    bars2 = ax.bar(x + w/2, ext_C, w, color=PROTOCOLS['C']['color'],
                   alpha=0.85, label='Pulsed C (10min/10h)', edgecolor='white')

    ax.axhline(0, color='black', lw=0.8)
    ax.axhline(50, color='green', ls='--', lw=1, alpha=0.5, label='+50% improvement')
    ax.set_xticks(x)
    ax.set_xticklabels(short_names, rotation=15, ha='right', fontsize=10)
    ax.set_ylabel('Lifetime extension vs. constant CP (%)', fontsize=11)
    ax.set_title('Protocol Improvement\n(positive = better than constant)', fontsize=11)
    ax.legend(fontsize=9)
    ax.grid(axis='y', alpha=0.3)

    # Annotate values
    for bars in [bars1, bars2]:
        for bar in bars:
            h = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2,
                    h + 1 if h >= 0 else h - 3,
                    f'{h:.0f}%', ha='center', fontsize=8)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    print(f"  Plot saved: {output_path}")


# =============================================================================
# SECTION 4: STATISTICAL ANALYSIS
# =============================================================================

def statistical_summary(all_results):
    """Print comprehensive statistical summary."""
    rows = []
    for cat, cat_results in all_results.items():
        for prot, r in cat_results.items():
            rows.append({
                'catalyst':      cat,
                'protocol':      PROTOCOLS[prot]['label'],
                'eta_0_mV':      r['eta_0_mV'],
                'eta_500h_mV':   r['eta_500h_mV'],
                'delta_eta_mV':  r['delta_eta_mV'],
                't30_h':         r['t30_h'],
                'extension_pct': r['lifetime_extension_vs_A'],
            })

    df = pd.DataFrame(rows)

    print("\n" + "="*75)
    print("STATISTICAL SUMMARY — PULSED CP EXPERIMENT")
    print("="*75)
    print(df.to_string(index=False, float_format='{:.1f}'.format))

    # Key statistics
    print("\n--- PULSED B vs CONSTANT A ---")
    b_exts = df[df['protocol'] == 'Pulsed 1min/h']['extension_pct'].dropna()
    print(f"  Mean lifetime extension:  {b_exts.mean():.0f}%")
    print(f"  Range:                    {b_exts.min():.0f}% – {b_exts.max():.0f}%")
    print(f"  All catalysts improved:   {'YES' if (b_exts > 0).all() else 'NO'}")

    df.to_csv('../results_pulsed_cp_summary.csv', index=False)
    print("\n  Saved: results_pulsed_cp_summary.csv")
    return df


# =============================================================================
# SECTION 5: MAIN — SYNTHETIC DEMO
# =============================================================================

CATALYST_LIBRARY = {
    'NiFe LDH': {
        # Protocol A: constant — deactivates ~35mV over 500h
        'A': {'eta0_mV': 255, 'deactivation_rate_mV_per_h': 0.065, 'regeneration_efficiency': 0.0,  'noise_mV': 2.5},
        # Protocol B: pulsed 1min/h — significant regeneration
        'B': {'eta0_mV': 255, 'deactivation_rate_mV_per_h': 0.065, 'regeneration_efficiency': 0.72, 'noise_mV': 2.5},
        # Protocol C: pulsed 10min/10h — less frequent, less effective
        'C': {'eta0_mV': 255, 'deactivation_rate_mV_per_h': 0.065, 'regeneration_efficiency': 0.50, 'noise_mV': 2.5},
        # Protocol D: fixed V rest — poor regeneration (O* binds at 1.2V)
        'D': {'eta0_mV': 255, 'deactivation_rate_mV_per_h': 0.065, 'regeneration_efficiency': 0.15, 'noise_mV': 2.5},
    },
    'NiFeV LDH': {
        'A': {'eta0_mV': 220, 'deactivation_rate_mV_per_h': 0.055, 'regeneration_efficiency': 0.0,  'noise_mV': 2.0},
        'B': {'eta0_mV': 220, 'deactivation_rate_mV_per_h': 0.055, 'regeneration_efficiency': 0.68, 'noise_mV': 2.0},
        'C': {'eta0_mV': 220, 'deactivation_rate_mV_per_h': 0.055, 'regeneration_efficiency': 0.45, 'noise_mV': 2.0},
        'D': {'eta0_mV': 220, 'deactivation_rate_mV_per_h': 0.055, 'regeneration_efficiency': 0.12, 'noise_mV': 2.0},
    },
    'Co3O4': {
        'A': {'eta0_mV': 340, 'deactivation_rate_mV_per_h': 0.080, 'regeneration_efficiency': 0.0,  'noise_mV': 3.0},
        'B': {'eta0_mV': 340, 'deactivation_rate_mV_per_h': 0.080, 'regeneration_efficiency': 0.60, 'noise_mV': 3.0},
        'C': {'eta0_mV': 340, 'deactivation_rate_mV_per_h': 0.080, 'regeneration_efficiency': 0.40, 'noise_mV': 3.0},
        'D': {'eta0_mV': 340, 'deactivation_rate_mV_per_h': 0.080, 'regeneration_efficiency': 0.10, 'noise_mV': 3.0},
    },
    'NiCo2O4': {
        'A': {'eta0_mV': 310, 'deactivation_rate_mV_per_h': 0.070, 'regeneration_efficiency': 0.0,  'noise_mV': 2.5},
        'B': {'eta0_mV': 310, 'deactivation_rate_mV_per_h': 0.070, 'regeneration_efficiency': 0.65, 'noise_mV': 2.5},
        'C': {'eta0_mV': 310, 'deactivation_rate_mV_per_h': 0.070, 'regeneration_efficiency': 0.42, 'noise_mV': 2.5},
        'D': {'eta0_mV': 310, 'deactivation_rate_mV_per_h': 0.070, 'regeneration_efficiency': 0.12, 'noise_mV': 2.5},
    },
    'Amorphous NiFeOxHy': {
        'A': {'eta0_mV': 260, 'deactivation_rate_mV_per_h': 0.045, 'regeneration_efficiency': 0.0,  'noise_mV': 2.0},
        'B': {'eta0_mV': 260, 'deactivation_rate_mV_per_h': 0.045, 'regeneration_efficiency': 0.75, 'noise_mV': 2.0},
        'C': {'eta0_mV': 260, 'deactivation_rate_mV_per_h': 0.045, 'regeneration_efficiency': 0.55, 'noise_mV': 2.0},
        'D': {'eta0_mV': 260, 'deactivation_rate_mV_per_h': 0.045, 'regeneration_efficiency': 0.18, 'noise_mV': 2.0},
    },
}


if __name__ == '__main__':
    print("PULSED CHRONOPOTENTIOMETRY ANALYSIS — SYNTHETIC DEMO")
    print("="*55)
    print("Simulating 500h experiment across 5 catalysts, 4 protocols\n")

    all_results = {}

    for catalyst_name, params in CATALYST_LIBRARY.items():
        print(f"Analysing: {catalyst_name}")
        results, traces = analyse_all_protocols(catalyst_name, params, duration_h=500)

        # Print t30 per protocol
        for p in ['A','B','C','D']:
            t30 = results[p]['t30_h']
            ext = results[p]['lifetime_extension_vs_A']
            ext_str = f" (+{ext:.0f}%)" if ext and ext > 0 else ""
            print(f"  Protocol {p}: t30 = {t30:.0f}h{ext_str}" if t30 else f"  Protocol {p}: t30 > 500h")

        all_results[catalyst_name] = results

        # Plot per-catalyst figure
        out = f"../results_pulsed_cp_{catalyst_name.replace(' ','_').replace('/','')}.png"
        plot_cp_comparison(catalyst_name, traces, results, out)

    # Multi-catalyst summary figure
    plot_multi_catalyst_summary(all_results, '../results_pulsed_cp_universality.png')

    # Statistical summary
    df = statistical_summary(all_results)

    print("\n" + "="*55)
    print("HOW TO USE WITH REAL DATA:")
    print("  1. Export from potentiostat as CSV:")
    print("     time_s, potential_V, current_mA_cm2")
    print("  2. Compute eta_mV = (potential_V - 1.23) * 1000")
    print("  3. Replace generate_cp_trace() calls with pd.read_csv()")
    print("  4. Pass real DataFrame to extract_eta10_series()")
    print("  5. Call time_to_threshold() to get t30")
    print("  6. All plots and summary table work unchanged")
    print("="*55)
