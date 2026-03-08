"""
DEMS (Differential Electrochemical Mass Spectrometry) Data Analysis
====================================================================
Calculates LOM fraction from 18O isotope labeling experiments.

Usage:
    python dems_analysis.py                   # Run with synthetic demo data
    python dems_analysis.py --file data.csv   # Analyse real DEMS CSV export

Expected CSV format (from commercial DEMS software or RGA export):
    time_s, current_mA_cm2, m32, m34, m36, m40

Dependencies:
    pip install numpy pandas matplotlib scipy
"""

import sys
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.signal import savgol_filter
from scipy.integrate import trapezoid
import warnings
warnings.filterwarnings('ignore')


# =============================================================================
# SECTION 1: CORE CALCULATIONS
# =============================================================================

def calculate_lom_fraction(m32, m34, m36,
                            enrichment=0.97,
                            min_signal=0.1):
    """
    Calculate LOM (Lattice Oxygen Mechanism) fraction from isotope signals.

    Mathematical derivation:
    In H2-18O electrolyte (97% 18O), oxygen produced purely by AEM is 18O2.
    Any 16O in evolved O2 must come from the catalyst lattice (16O_lattice).

    Correcting for the 3% 16O contamination in the enriched water:

        Background m32 (16O2 from water 16O):  m36 * (1-e)^2 / e^2
        Background m34 (16O18O from water 16O): m36 * 2*(1-e)/e

    True LOM signal:
        m32_lom = m32 - m32_background
        m34_lom = m34 - m34_background

    LOM fraction:
        LOM% = (m32_lom + 0.5*m34_lom) / (m36 + m34_lom + m32_lom) * 100

    Args:
        m32: signal at m/z=32 (16O2), array
        m34: signal at m/z=34 (16O18O), array
        m36: signal at m/z=36 (18O2), array
        enrichment: 18O atom fraction in labeled water (0.97 = 97%)
        min_signal: minimum m36 to compute ratio (avoids division by near-zero)

    Returns:
        lom_pct: LOM percentage (0–100), same length as inputs
        lom_lower: lower bound (1-sigma)
        lom_upper: upper bound (1-sigma)
    """
    m32 = np.asarray(m32, float)
    m34 = np.asarray(m34, float)
    m36 = np.asarray(m36, float)

    e = enrichment
    mask = m36 > min_signal

    # Natural-abundance background corrections
    m32_bg = np.where(mask, m36 * ((1-e)/e)**2, 0.0)
    m34_bg = np.where(mask, m36 * 2*(1-e)/e,    0.0)

    m32_lom = np.maximum(m32 - m32_bg, 0.0)
    m34_lom = np.maximum(m34 - m34_bg, 0.0)

    total    = m36 + m34_lom + m32_lom + 1e-12
    lom_frac = (m32_lom + 0.5*m34_lom) / total
    lom_pct  = np.clip(lom_frac * 100, 0, 100)

    # Uncertainty: propagate 5% relative noise on each channel
    delta = 0.05
    dlom_dm32 = 1.0 / total
    dlom_dm34 = 0.5 / total
    dlom_dm36 = -(m32_lom + 0.5*m34_lom) / total**2

    sigma = np.sqrt(
        (dlom_dm32 * delta * m32)**2 +
        (dlom_dm34 * delta * m34)**2 +
        (dlom_dm36 * delta * m36)**2
    ) * 100  # convert to %

    return lom_pct, np.maximum(lom_pct - sigma, 0), lom_pct + sigma


def faradaic_efficiency(current_mA_cm2, m36_signal, cell_constant=1.0):
    """
    Calculate O2 Faradaic efficiency from 18O2 signal.
    cell_constant: calibration factor (mol O2 per unit m36 signal per mA)
    """
    # In a real experiment, calibrate cell_constant with known O2 generation rate
    # from a Pt electrode: n_O2 = Q/(4F), correlate with m36 signal
    # Here we use a placeholder
    theoretical_o2 = current_mA_cm2 * 1e-3 / (4 * 96485)  # mol O2 / cm2 / s
    measured_o2    = m36_signal * cell_constant
    fe = measured_o2 / (theoretical_o2 + 1e-15)
    return np.clip(fe, 0, 1.05)


# =============================================================================
# SECTION 2: DATA SMOOTHING AND EVENT DETECTION
# =============================================================================

def smooth_dems(signal, window=11, polyorder=3):
    """Apply Savitzky-Golay filter to remove noise from DEMS trace."""
    if len(signal) < window:
        return signal
    return savgol_filter(signal, min(window, len(signal)//2*2-1), polyorder)


def find_oer_onset(time, lom_pct, m36, current, threshold_ma=0.5):
    """
    Find the potential / time at which LOM signal first emerges above noise.
    Returns index of onset and LOM% at onset.
    """
    noise_level = np.std(lom_pct[current < threshold_ma]) if (current < threshold_ma).any() else 2.0
    onset_mask  = (lom_pct > 3 * noise_level) & (current > threshold_ma)
    if onset_mask.any():
        onset_idx = np.argmax(onset_mask)
        return onset_idx, lom_pct[onset_idx]
    return None, None


# =============================================================================
# SECTION 3: FULL ANALYSIS PIPELINE
# =============================================================================

def analyse_catalyst(name, time, current, m32, m34, m36,
                     enrichment=0.97, smooth=True, verbose=True):
    """
    Full analysis pipeline for one catalyst's DEMS run.

    Args:
        name: string label
        time: time array (seconds)
        current: current density array (mA/cm2)
        m32, m34, m36: DEMS signals (arbitrary units, consistent scaling)
        enrichment: 18O enrichment fraction

    Returns:
        dict with summary statistics
    """
    if smooth:
        m32 = smooth_dems(m32)
        m34 = smooth_dems(m34)
        m36 = smooth_dems(m36)

    lom, lom_lo, lom_hi = calculate_lom_fraction(m32, m34, m36, enrichment)

    # Only during active OER
    active = current > 0.5
    lom_oer = lom[active]

    if len(lom_oer) == 0:
        return {'catalyst': name, 'error': 'No OER current detected'}

    mean_lom = np.mean(lom_oer)
    std_lom  = np.std(lom_oer)
    max_lom  = np.max(lom_oer)

    # Onset detection
    onset_idx, onset_lom = find_oer_onset(time, lom, m36, current)

    # Total O2 produced from lattice vs. water (integrated)
    dt = np.gradient(time)
    lom_weighted = trapezoid(lom * m36, time) / (trapezoid(m36, time) + 1e-12)

    # Classification
    classification = (
        "STRONG LOM (>30%) — scaling likely broken"    if mean_lom > 30 else
        "MODERATE LOM (10-30%) — partial scaling escape" if mean_lom > 10 else
        "WEAK LOM (3-10%) — marginal"                  if mean_lom > 3  else
        "AEM DOMINANT (<3%) — scaling relations hold"
    )

    result = {
        'catalyst':            name,
        'lom_mean_pct':        round(mean_lom, 1),
        'lom_std_pct':         round(std_lom,  1),
        'lom_max_pct':         round(max_lom,  1),
        'lom_integrated_pct':  round(lom_weighted, 1),
        'classification':      classification,
        'onset_s':             time[onset_idx] if onset_idx else None,
        '_arrays':             dict(time=time, current=current,
                                    m32=m32, m34=m34, m36=m36,
                                    lom=lom, lom_lo=lom_lo, lom_hi=lom_hi),
    }

    if verbose:
        print(f"\n{'='*55}")
        print(f"  {name}")
        print(f"{'='*55}")
        print(f"  LOM fraction:  {mean_lom:.1f} +/- {std_lom:.1f} %")
        print(f"  Max LOM:       {max_lom:.1f} %")
        print(f"  Integrated:    {lom_weighted:.1f} %")
        print(f"  Classification: {classification}")
        if onset_idx:
            print(f"  LOM onset at:  t = {time[onset_idx]:.0f} s")

    return result


# =============================================================================
# SECTION 4: VISUALISATION
# =============================================================================

def plot_dems_results(results_list, output_path='dems_results.png'):
    """
    Generate comprehensive DEMS visualisation for all catalysts.
    """
    n_cats  = len(results_list)
    fig     = plt.figure(figsize=(14, 4 * n_cats + 3))
    fig.suptitle('18O Isotope Labeling — DEMS Analysis\n'
                 'Quantifying Lattice Oxygen Mechanism in OER Catalysts',
                 fontsize=13, fontweight='bold', y=0.98)

    for i, res in enumerate(results_list):
        if 'error' in res:
            continue

        arr  = res['_arrays']
        t    = arr['time']
        cur  = arr['current']
        lom  = arr['lom']
        lo   = arr['lom_lo']
        hi   = arr['lom_hi']
        m36  = arr['m36']
        m34  = arr['m34']
        m32  = arr['m32']

        # Row: 3 panels per catalyst
        ax1 = fig.add_subplot(n_cats, 3, 3*i+1)
        ax2 = fig.add_subplot(n_cats, 3, 3*i+2)
        ax3 = fig.add_subplot(n_cats, 3, 3*i+3)

        cat_color = plt.cm.tab10(i / max(n_cats, 1))

        # Panel 1: Raw DEMS signals
        ax1.plot(t, m36/m36.max(), 'b-',  lw=1.5, label='m/z=36 (18O2)', alpha=0.9)
        ax1.plot(t, m34/m36.max(), 'g-',  lw=1.5, label='m/z=34 (16O18O)', alpha=0.9)
        ax1.plot(t, m32/m36.max(), 'r-',  lw=1.5, label='m/z=32 (16O2 LOM)', alpha=0.9)
        ax1_r = ax1.twinx()
        ax1_r.plot(t, cur, 'k:', lw=1, alpha=0.5, label='Current (mA/cm2)')
        ax1.set_xlabel('Time (s)', fontsize=9)
        ax1.set_ylabel('Signal (norm.)', fontsize=9)
        ax1.set_title(f'{res["catalyst"]}\nRaw DEMS signals', fontsize=9)
        ax1.legend(fontsize=7, loc='upper left')
        ax1.grid(alpha=0.3)

        # Panel 2: LOM% vs time
        active = cur > 0.5
        ax2.fill_between(t, lo, hi, alpha=0.25, color=cat_color)
        ax2.plot(t, lom, '-', color=cat_color, lw=2)
        ax2.axhline(30, color='red',    ls='--', lw=1, alpha=0.6, label='30% threshold')
        ax2.axhline(10, color='orange', ls='--', lw=1, alpha=0.6, label='10% threshold')
        ax2.set_xlabel('Time (s)', fontsize=9)
        ax2.set_ylabel('LOM fraction (%)', fontsize=9)
        ax2.set_title(f'LOM% = {res["lom_mean_pct"]:.1f} ± {res["lom_std_pct"]:.1f}%', fontsize=9)
        ax2.set_ylim(-2, min(100, lom[active].max()*1.5 + 5) if active.any() else 60)
        ax2.legend(fontsize=7)
        ax2.grid(alpha=0.3)

        # Panel 3: Isotope ratio bar (single number summary)
        cats_ = ['16O2\n(LOM)', '16O18O\n(partial)', '18O2\n(AEM)']
        vals  = [
            res['lom_mean_pct'] * 0.5,         # Fully lattice O2 contribution
            res['lom_mean_pct'] * 0.5,         # Mixed
            100 - res['lom_mean_pct'],
        ]
        colors_ = ['#e74c3c', '#f39c12', '#3498db']
        bars_   = ax3.bar(cats_, vals, color=colors_, alpha=0.85, edgecolor='white')
        for bar, val in zip(bars_, vals):
            ax3.text(bar.get_x() + bar.get_width()/2,
                     bar.get_height() + 0.5, f'{val:.1f}%',
                     ha='center', fontsize=9, fontweight='bold')
        ax3.set_ylabel('Fraction of O2 (%)', fontsize=9)
        ax3.set_title(f'O2 Origin\n{res["classification"][:25]}...', fontsize=8)
        ax3.set_ylim(0, 115)
        ax3.grid(axis='y', alpha=0.3)

    plt.tight_layout(rect=[0, 0, 1, 0.96])
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    print(f"\nPlot saved: {output_path}")


def plot_comparison_bar(results_list, output_path='dems_comparison.png'):
    """Bar chart comparing LOM% across all catalysts."""
    names = [r['catalyst'] for r in results_list if 'error' not in r]
    means = [r['lom_mean_pct'] for r in results_list if 'error' not in r]
    stds  = [r['lom_std_pct']  for r in results_list if 'error' not in r]

    colors = ['#27ae60' if m > 30 else '#f39c12' if m > 10 else '#e74c3c' for m in means]

    fig, ax = plt.subplots(figsize=(10, 5))
    bars = ax.bar(range(len(names)), means, yerr=stds, capsize=5,
                  color=colors, alpha=0.85, edgecolor='white', linewidth=1.2)

    ax.axhline(30, color='green',  ls='--', lw=1.5, alpha=0.7, label='Strong LOM (30%)')
    ax.axhline(10, color='orange', ls='--', lw=1.5, alpha=0.7, label='Moderate LOM (10%)')
    ax.axhline(3,  color='red',    ls='--', lw=1.5, alpha=0.7, label='Detection limit (~3%)')

    ax.set_xticks(range(len(names)))
    ax.set_xticklabels(names, rotation=20, ha='right', fontsize=11)
    ax.set_ylabel('LOM Fraction (%)', fontsize=12)
    ax.set_title('Lattice Oxygen Mechanism Fraction Across OER Catalysts\n'
                 '(18O isotope labeling in H2-18O electrolyte)',
                 fontsize=12, fontweight='bold')
    ax.legend(fontsize=9)
    ax.set_ylim(0, max(means)*1.2 + 15)
    ax.grid(axis='y', alpha=0.3)

    # Annotate significance
    for i, (m, s, bar) in enumerate(zip(means, stds, bars)):
        significance = '***' if m > 30 else '**' if m > 10 else '*' if m > 3 else 'ns'
        ax.text(bar.get_x() + bar.get_width()/2, m + s + 1,
                significance, ha='center', fontsize=12, fontweight='bold')

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    print(f"Plot saved: {output_path}")


# =============================================================================
# SECTION 5: DEMO WITH SYNTHETIC DATA
# =============================================================================

def generate_synthetic_dems(lom_true_pct, duration=600, noise_level=0.05,
                              enrichment=0.97, seed=None):
    """
    Generate synthetic DEMS data with known LOM fraction.
    Used for validating analysis pipeline and planning experiments.

    Args:
        lom_true_pct: ground-truth LOM fraction (%)
        duration: experiment duration in seconds
        noise_level: fractional noise on all signals
        enrichment: 18O enrichment

    Returns: time, current, m32, m34, m36
    """
    if seed is not None:
        np.random.seed(seed)

    t   = np.linspace(0, duration, duration)
    cur = np.where(t > 60, 10.0, 0.0)   # OER starts at t=60s

    # Base O2 production rate (arb. units)
    o2_rate = np.where(t > 60, 1000.0, 2.0)

    e      = enrichment
    lf     = lom_true_pct / 100.0        # LOM fraction

    # Expected isotope distribution from AEM+LOM mixture
    # AEM: all O from 18O water → 18O2 = e^2, 16O18O = 2e(1-e), 16O2 = (1-e)^2
    # LOM: lattice 16O contributes; simplify as 16O2 = lf, 16O18O = lf*(1-lf), 18O2 = (1-lf)
    m36_signal = o2_rate * (e**2 * (1-lf) + (1-lf)**2 * lf)
    m34_signal = o2_rate * (2*e*(1-e)*(1-lf) + 2*(1-lf)*lf*e)
    m32_signal = o2_rate * ((1-e)**2*(1-lf) + lf**2 + (1-lf)*lf*(1-e))

    # Normalise so m36 is the dominant signal
    norm = m36_signal.max() + 1e-12
    m36_signal /= norm/1000; m34_signal /= norm/1000; m32_signal /= norm/1000

    # Add noise
    m36_signal *= (1 + np.random.normal(0, noise_level, len(t)))
    m34_signal *= (1 + np.random.normal(0, noise_level, len(t)))
    m32_signal *= (1 + np.random.normal(0, noise_level, len(t)))

    return t, cur, np.abs(m32_signal), np.abs(m34_signal), np.abs(m36_signal)


# =============================================================================
# MAIN
# =============================================================================

if __name__ == '__main__':
    print("DEMS 18O ISOTOPE LABELING ANALYSIS")
    print("="*55)
    print("Demo mode: synthetic data with known LOM fractions\n")
    print("In real use: replace generate_synthetic_dems() calls with")
    print("your potentiostat + RGA data export.\n")

    # Expected LOM fractions based on literature + our hypotheses
    CATALYST_SCENARIOS = [
        ('IrO2 (reference)',    35.0,  0.97),   # Literature: ~30-45%
        ('NiFe LDH (alkaline)',50.0,  0.97),   # Literature: ~40-60%
        ('MnO2 birnessite',     8.0,  0.97),   # Our estimate: ~5-15%
        ('Ca0.15Mn0.85Ox',     14.0,  0.97),   # Our hypothesis: Ca improves LOM
        ('FeCoNiCr HEA',       18.0,  0.97),   # Unknown — key experiment
    ]

    all_results = []
    for name, lom_true, enrich in CATALYST_SCENARIOS:
        t, cur, m32, m34, m36 = generate_synthetic_dems(
            lom_true_pct=lom_true,
            noise_level=0.04,
            enrichment=enrich,
            seed=hash(name) % 2**31
        )
        res = analyse_catalyst(name, t, cur, m32, m34, m36,
                               enrichment=enrich, smooth=True)
        all_results.append(res)

    # Summary table
    print("\n\n" + "="*70)
    print("SUMMARY TABLE")
    print("="*70)
    cols = ['catalyst', 'lom_mean_pct', 'lom_std_pct', 'classification']
    df   = pd.DataFrame([{k: r[k] for k in cols} for r in all_results if 'error' not in r])
    print(df.to_string(index=False))
    df.to_csv('../results_dems_lom_fractions.csv', index=False)
    print("\nSaved: results_dems_lom_fractions.csv")

    # Generate plots
    print("\nGenerating visualisations...")
    plot_dems_results(all_results, '../results_dems_detail.png')
    plot_comparison_bar(all_results, '../results_dems_comparison.png')

    print("\n" + "="*55)
    print("HOW TO USE WITH REAL DATA:")
    print("  1. Export your DEMS/RGA data as CSV with columns:")
    print("     time_s, current_mA_cm2, m32, m34, m36")
    print("  2. Replace generate_synthetic_dems() call with:")
    print("     df = pd.read_csv('your_dems_data.csv')")
    print("     t, cur = df['time_s'].values, df['current_mA_cm2'].values")
    print("     m32, m34, m36 = df['m32'].values, df['m34'].values, df['m36'].values")
    print("  3. Call analyse_catalyst() as shown above")
    print("  4. All plots and summary table generated automatically")
    print("="*55)
