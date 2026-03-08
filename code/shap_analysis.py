"""
SHAP Feature Importance Analysis for OER/HER Catalyst Stability
================================================================
Answers: Which catalyst descriptors most strongly predict stability?

Key outputs:
- Global SHAP importance bar chart
- SHAP beeswarm (shows direction of effects)
- Per-class breakdown (HER vs OER, acid vs alkaline)
- Actionable interpretation for experiment design

Usage:
    pip install shap
    python shap_analysis.py
"""

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import warnings
warnings.filterwarnings('ignore')

from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline

# Import our dataset
import sys
sys.path.insert(0, '.')
from stability_ml import build_catalyst_dataset, engineer_features, get_feature_columns

try:
    import shap
    HAS_SHAP = True
except ImportError:
    HAS_SHAP = False
    print("shap not installed — install with: pip install shap")
    print("Falling back to permutation importance + RF built-in importance")


# =============================================================================
# TRAIN MODEL ON FULL DATASET
# =============================================================================

def train_full_model(df_features, feature_cols):
    """Train on full dataset for interpretation (no CV — want all data in model)."""
    X = df_features[feature_cols].values
    y = np.log1p(df_features['stability_h'].values)

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    rf = RandomForestRegressor(
        n_estimators=500,
        max_depth=8,
        min_samples_leaf=2,
        random_state=42
    )
    rf.fit(X_scaled, y)

    return rf, scaler, X_scaled, y


# =============================================================================
# FEATURE IMPORTANCE — RF BUILT-IN + PERMUTATION
# =============================================================================

def rf_importance_analysis(rf, feature_cols, df_features, X_scaled, y):
    """Extract and rank RF feature importances."""
    from sklearn.inspection import permutation_importance

    # Built-in impurity-based importance
    builtin_imp = pd.Series(rf.feature_importances_, index=feature_cols)
    builtin_imp = builtin_imp.sort_values(ascending=False)

    # Permutation importance (more reliable, model-agnostic)
    perm = permutation_importance(rf, X_scaled, y, n_repeats=20, random_state=42)
    perm_imp = pd.Series(perm.importances_mean, index=feature_cols)
    perm_imp = perm_imp.sort_values(ascending=False)
    perm_std = pd.Series(perm.importances_std, index=feature_cols)

    return builtin_imp, perm_imp, perm_std


# =============================================================================
# PLOT: FEATURE IMPORTANCE (DUAL METHOD)
# =============================================================================

def plot_feature_importance(builtin_imp, perm_imp, perm_std, out_prefix='results_shap'):
    """Generate a clean two-panel feature importance figure."""

    # Human-readable feature labels
    label_map = {
        'dissolution_potential_v': 'Dissolution potential (V)',
        'acid_stable_score': 'Acid stability score',
        'stability_index': 'Stability index (score × pot.)',
        'is_acid': 'Is acid electrolyte',
        'is_HER': 'Is HER (vs OER)',
        'n_metals': 'Number of metals',
        'has_cr': 'Contains Cr',
        'has_mn': 'Contains Mn',
        'protective_elements': 'Protective elements (Cr+Mn)',
        'is_encapsulated': 'Is encapsulated (NC shell)',
        'eta_10_mv': 'Overpotential η₁₀ (mV)',
        'tafel_slope': 'Tafel slope (mV/dec)',
        'activity_kinetics': 'Activity×kinetics product',
        'd_band_center_ev': 'd-band center (eV)',
        'mo_bond_energy_ev': 'M-O bond energy (eV)',
        'mh_bond_energy_ev': 'M-H bond energy (eV)',
        'eg_electrons': 'eg electron occupancy',
        'coordination': 'Coordination number',
        'surface_area_m2g': 'Surface area (m²/g)',
        'is_alloy': 'Crystal: alloy',
        'is_carbide_encapsulated': 'Crystal: carbide@NC',
        'is_amorphous': 'Crystal: amorphous',
        'is_LDH': 'Crystal: LDH',
        'is_high_entropy': 'Crystal: high-entropy',
        'is_phosphide': 'Crystal: phosphide',
        'is_SAC': 'Crystal: SAC',
        'is_perovskite': 'Crystal: perovskite',
        'is_spinel': 'Crystal: spinel',
        'is_carbide': 'Crystal: carbide',
        'is_nitride': 'Crystal: nitride',
        'is_selenide': 'Crystal: selenide',
        'is_oxide': 'Crystal: oxide',
        'is_MOF_derived': 'Crystal: MOF-derived',
        'is_MXene': 'Crystal: MXene',
        'is_doped_oxide': 'Crystal: doped oxide',
    }

    top_n = 18
    top_perm = perm_imp.head(top_n)
    top_labels = [label_map.get(f, f) for f in top_perm.index]
    top_std = perm_std[top_perm.index]

    fig, axes = plt.subplots(1, 2, figsize=(14, 7))
    fig.suptitle('Catalyst Stability Predictor — Feature Importance Analysis\n'
                 '(80 catalysts, Random Forest, log(stability_h))',
                 fontsize=12, fontweight='bold')

    # --- Panel 1: Permutation importance with error bars ---
    ax = axes[0]
    colors = ['#d62728' if 'acid' in l.lower() or 'dissolution' in l.lower() or 'stability' in l.lower()
              else '#1f77b4' if 'Crystal' in l
              else '#2ca02c' if 'band' in l.lower() or 'bond' in l.lower() or 'eg' in l.lower()
              else '#ff7f0e'
              for l in top_labels]

    bars = ax.barh(range(top_n), top_perm.values[::-1],
                   xerr=top_std.values[::-1], capsize=3,
                   color=colors[::-1], alpha=0.85, edgecolor='white', linewidth=0.5)
    ax.set_yticks(range(top_n))
    ax.set_yticklabels(top_labels[::-1], fontsize=9)
    ax.set_xlabel('Permutation Importance\n(mean decrease in R²)', fontsize=10)
    ax.set_title('Permutation Importance\n(Model-Agnostic, More Reliable)', fontsize=10)
    ax.axvline(0, color='black', linewidth=0.8, linestyle='--')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    # Legend for colors
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor='#d62728', alpha=0.85, label='Stability/condition'),
        Patch(facecolor='#2ca02c', alpha=0.85, label='Electronic structure'),
        Patch(facecolor='#1f77b4', alpha=0.85, label='Crystal class'),
        Patch(facecolor='#ff7f0e', alpha=0.85, label='Structural/other'),
    ]
    ax.legend(handles=legend_elements, loc='lower right', fontsize=8)

    # --- Panel 2: RF built-in importance vs permutation comparison ---
    ax2 = axes[1]
    top20_builtin = builtin_imp.head(20)
    top20_labels = [label_map.get(f, f) for f in top20_builtin.index]

    ax2.barh(range(20), top20_builtin.values[::-1],
             color='#9467bd', alpha=0.8, edgecolor='white', linewidth=0.5)
    ax2.set_yticks(range(20))
    ax2.set_yticklabels(top20_labels[::-1], fontsize=9)
    ax2.set_xlabel('Impurity Importance\n(Gini-based, may overfit)', fontsize=10)
    ax2.set_title('RF Built-in Importance\n(Faster but biased toward high-cardinality)', fontsize=10)
    ax2.spines['top'].set_visible(False)
    ax2.spines['right'].set_visible(False)

    plt.tight_layout()
    outpath = f'{out_prefix}_feature_importance.png'
    plt.savefig(outpath, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"Saved: {outpath}")
    return outpath


# =============================================================================
# SHAP ANALYSIS (if available)
# =============================================================================

def run_shap_analysis(rf, X_scaled, feature_cols, df_features, out_prefix='results_shap'):
    """Run SHAP TreeExplainer and generate beeswarm plot."""
    if not HAS_SHAP:
        return None

    label_map = {
        'dissolution_potential_v': 'Dissolution potential',
        'acid_stable_score': 'Acid stable score',
        'stability_index': 'Stability index',
        'is_acid': 'Acid electrolyte',
        'is_HER': 'HER reaction',
        'n_metals': 'N metals',
        'has_cr': 'Has Cr',
        'has_mn': 'Has Mn',
        'protective_elements': 'Protective (Cr+Mn)',
        'is_encapsulated': 'Encapsulated',
        'eta_10_mv': 'η₁₀ (mV)',
        'tafel_slope': 'Tafel slope',
        'activity_kinetics': 'Activity×kinetics',
        'd_band_center_ev': 'd-band center',
        'mo_bond_energy_ev': 'M-O bond energy',
        'mh_bond_energy_ev': 'M-H bond energy',
        'eg_electrons': 'eg electrons',
        'coordination': 'Coordination #',
        'surface_area_m2g': 'Surface area',
        'is_alloy': 'Alloy',
        'is_amorphous': 'Amorphous',
        'is_LDH': 'LDH',
        'is_high_entropy': 'High-entropy',
        'is_phosphide': 'Phosphide',
        'is_SAC': 'SAC',
        'is_perovskite': 'Perovskite',
        'is_carbide_encapsulated': 'Carbide@NC',
    }

    print("Computing SHAP values (TreeExplainer)...")
    explainer = shap.TreeExplainer(rf)
    shap_values = explainer.shap_values(X_scaled)

    # Use readable labels
    readable_cols = [label_map.get(c, c) for c in feature_cols]
    X_df = pd.DataFrame(X_scaled, columns=readable_cols)

    # --- Beeswarm plot ---
    fig, ax = plt.subplots(figsize=(10, 8))
    shap.summary_plot(shap_values, X_df, plot_type='dot',
                      max_display=20, show=False, color_bar=True)
    plt.title('SHAP Values — Catalyst Stability Prediction\n'
              'Red = feature pushes stability UP, Blue = pushes DOWN',
              fontsize=11, fontweight='bold', pad=12)
    plt.xlabel('SHAP value (impact on log stability_h)', fontsize=10)
    plt.tight_layout()
    outpath1 = f'{out_prefix}_shap_beeswarm.png'
    plt.savefig(outpath1, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"Saved: {outpath1}")

    # --- Bar plot ---
    fig, ax = plt.subplots(figsize=(8, 6))
    shap.summary_plot(shap_values, X_df, plot_type='bar',
                      max_display=15, show=False)
    plt.title('Mean |SHAP| — Top Stability Predictors', fontsize=11, fontweight='bold')
    plt.tight_layout()
    outpath2 = f'{out_prefix}_shap_bar.png'
    plt.savefig(outpath2, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"Saved: {outpath2}")

    # Return mean absolute SHAP values for reporting
    mean_shap = pd.Series(
        np.abs(shap_values).mean(axis=0),
        index=feature_cols
    ).sort_values(ascending=False)

    return mean_shap


# =============================================================================
# SUBGROUP ANALYSIS: HER vs OER, Acid vs Alkaline
# =============================================================================

def subgroup_importance(df_features, feature_cols):
    """Compare which features matter for each reaction/electrolyte subgroup."""
    results = {}
    groups = {
        'OER_alkaline': (df_features.reaction == 'OER') & (df_features.electrolyte == 'alkaline'),
        'OER_acid': (df_features.reaction == 'OER') & (df_features.electrolyte == 'acid'),
        'HER_acid': (df_features.reaction == 'HER') & (df_features.electrolyte == 'acid'),
        'HER_alkaline': (df_features.reaction == 'HER') & (df_features.electrolyte == 'alkaline'),
    }

    print("\n" + "=" * 60)
    print("SUBGROUP STABILITY STATISTICS")
    print("=" * 60)

    for group_name, mask in groups.items():
        subset = df_features[mask]
        if len(subset) < 3:
            continue
        stab = subset['stability_h']
        print(f"\n{group_name} (n={len(subset)}):")
        print(f"  Median stability: {stab.median():.0f}h")
        print(f"  Range: {stab.min():.0f}h – {stab.max():.0f}h")
        print(f"  Top stability catalysts:")
        top3 = subset.nlargest(3, 'stability_h')[['name', 'stability_h', 'crystal_class']]
        for _, row in top3.iterrows():
            print(f"    • {row['name']}: {row.stability_h}h ({row.crystal_class})")

        results[group_name] = {
            'n': len(subset),
            'median_h': stab.median(),
            'max_h': stab.max(),
            'top_catalyst': subset.nlargest(1, 'stability_h')['name'].values[0]
        }

    return results


# =============================================================================
# STABILITY PREDICTIONS FOR KEY NEW COMPOSITIONS
# =============================================================================

def predict_new_compositions(rf, scaler, feature_cols, df_features):
    """
    Predict stability for new/hypothetical compositions not in training set.
    Based on Bayesian optimizer top results and literature hypotheses.
    """
    # Compute column means for filling
    means = df_features[feature_cols].mean()

    # New candidates (from optimizer results + hypotheses from docs)
    new_catalysts = [
        {
            'name': 'Fe0.20Co0.19Mn0.09V0.15W0.18Mo0.19 HEO [Optimizer #1]',
            'reaction': 'OER', 'electrolyte': 'alkaline',
            'eta_10_mv': 263, 'tafel_slope': 52, 'dissolution_potential_v': 1.4,
            'acid_stable_score': 2, 'stability_index': 2.8,
            'd_band_center_ev': -2.0, 'mo_bond_energy_ev': 3.85, 'mh_bond_energy_ev': 2.65,
            'eg_electrons': 1.15, 'n_metals': 6, 'has_cr': 0, 'has_mn': 1,
            'coordination': 6, 'surface_area_m2g': 30,
            'protective_elements': 1, 'is_encapsulated': 0,
            'is_acid': 0, 'is_HER': 0,
            'activity_kinetics': 263 * 52 / 1000,
        },
        {
            'name': 'Co0.20Fe0.15V0.20W0.20Mo0.25 (V-rich) [Optimizer #2]',
            'reaction': 'OER', 'electrolyte': 'alkaline',
            'eta_10_mv': 270, 'tafel_slope': 54, 'dissolution_potential_v': 1.35,
            'acid_stable_score': 2, 'stability_index': 2.7,
            'd_band_center_ev': -2.02, 'mo_bond_energy_ev': 3.88, 'mh_bond_energy_ev': 2.62,
            'eg_electrons': 1.12, 'n_metals': 5, 'has_cr': 0, 'has_mn': 0,
            'coordination': 6, 'surface_area_m2g': 28,
            'protective_elements': 0, 'is_encapsulated': 0,
            'is_acid': 0, 'is_HER': 0,
            'activity_kinetics': 270 * 54 / 1000,
        },
        {
            'name': 'Amorphous NiFeMoV (hypothesis C3)',
            'reaction': 'OER', 'electrolyte': 'alkaline',
            'eta_10_mv': 218, 'tafel_slope': 38, 'dissolution_potential_v': 0.12,
            'acid_stable_score': 0, 'stability_index': 0.0,
            'd_band_center_ev': -1.88, 'mo_bond_energy_ev': 3.82, 'mh_bond_energy_ev': 2.68,
            'eg_electrons': 1.1, 'n_metals': 4, 'has_cr': 0, 'has_mn': 0,
            'coordination': 5, 'surface_area_m2g': 190,
            'protective_elements': 0, 'is_encapsulated': 0,
            'is_acid': 0, 'is_HER': 0,
            'activity_kinetics': 218 * 38 / 1000,
        },
        {
            'name': 'NiFeV LDH pulsed-CP (post-protocol)',
            'reaction': 'OER', 'electrolyte': 'alkaline',
            'eta_10_mv': 222, 'tafel_slope': 42, 'dissolution_potential_v': 0.1,
            'acid_stable_score': 0, 'stability_index': 0.0,
            'd_band_center_ev': -1.9, 'mo_bond_energy_ev': 3.7, 'mh_bond_energy_ev': 2.7,
            'eg_electrons': 1.1, 'n_metals': 3, 'has_cr': 0, 'has_mn': 0,
            'coordination': 6, 'surface_area_m2g': 90,
            'protective_elements': 0, 'is_encapsulated': 0,
            'is_acid': 0, 'is_HER': 0,
            'activity_kinetics': 222 * 42 / 1000,
        },
        {
            'name': 'WC@NC + Mo (Hypothesis H7 enhanced)',
            'reaction': 'HER', 'electrolyte': 'acid',
            'eta_10_mv': 75, 'tafel_slope': 42, 'dissolution_potential_v': 0.55,
            'acid_stable_score': 3, 'stability_index': 1.65,
            'd_band_center_ev': -1.62, 'mo_bond_energy_ev': 3.5, 'mh_bond_energy_ev': 2.48,
            'eg_electrons': 1.0, 'n_metals': 2, 'has_cr': 0, 'has_mn': 0,
            'coordination': 6, 'surface_area_m2g': 160,
            'protective_elements': 0, 'is_encapsulated': 1,
            'is_acid': 1, 'is_HER': 1,
            'activity_kinetics': 75 * 42 / 1000,
        },
        {
            'name': 'FeCoNiCrMnV HEA (acid OER) [Optimizer candidate]',
            'reaction': 'OER', 'electrolyte': 'acid',
            'eta_10_mv': 340, 'tafel_slope': 62, 'dissolution_potential_v': 0.98,
            'acid_stable_score': 2, 'stability_index': 1.96,
            'd_band_center_ev': -2.0, 'mo_bond_energy_ev': 3.88, 'mh_bond_energy_ev': 2.6,
            'eg_electrons': 1.08, 'n_metals': 6, 'has_cr': 1, 'has_mn': 1,
            'coordination': 6, 'surface_area_m2g': 28,
            'protective_elements': 2, 'is_encapsulated': 0,
            'is_acid': 1, 'is_HER': 0,
            'activity_kinetics': 340 * 62 / 1000,
        },
    ]

    # Add crystal class columns (all zero, then set relevant one)
    crystal_classes = ['LDH', 'perovskite', 'spinel', 'layered_oxide', 'high_entropy',
                       'amorphous', 'phosphide', 'carbide', 'carbide_encapsulated',
                       'SAC', 'alloy', 'nitride', 'sulfide', 'selenide', 'oxide',
                       'MOF_derived', 'MXene', 'doped_oxide', 'rutile', 'heteroatom_carbon']

    class_map = {
        'Fe0.20Co0.19': 'high_entropy',
        'Co0.20Fe0.15': 'high_entropy',
        'Amorphous': 'amorphous',
        'NiFeV LDH': 'LDH',
        'WC@NC': 'carbide_encapsulated',
        'FeCoNiCrMnV': 'high_entropy',
    }

    rows = []
    for cat in new_catalysts:
        row = {col: 0 for col in feature_cols}
        for k, v in cat.items():
            if k in row:
                row[k] = v

        # Set crystal class
        for key, cls in class_map.items():
            if key in cat['name']:
                row[f'is_{cls}'] = 1
                break

        rows.append(row)

    X_new = np.array([[row.get(c, means[c]) for c in feature_cols] for row in rows])
    X_new_scaled = scaler.transform(X_new)
    y_pred_log = rf.predict(X_new_scaled)
    y_pred_h = np.expm1(y_pred_log)

    print("\n" + "=" * 60)
    print("STABILITY PREDICTIONS FOR NEW COMPOSITIONS")
    print("=" * 60)
    print(f"{'Catalyst':<50} {'Predicted stability':>20}")
    print("-" * 72)
    for cat, pred_h in zip(new_catalysts, y_pred_h):
        name = cat['name'][:50]
        print(f"{name:<50} {pred_h:>16.0f}h")

    return pd.DataFrame({
        'catalyst': [c['name'] for c in new_catalysts],
        'predicted_stability_h': y_pred_h.round(0)
    })


# =============================================================================
# MAIN
# =============================================================================

if __name__ == '__main__':
    print("Loading catalyst dataset...")
    df = build_catalyst_dataset()
    df_feat = engineer_features(df)
    feat_cols = get_feature_columns()

    print(f"Dataset: {len(df)} catalysts, {len(feat_cols)} features")

    # Train full model
    print("\nTraining Random Forest on full dataset...")
    rf, scaler, X_scaled, y = train_full_model(df_feat, feat_cols)
    train_r2 = rf.score(X_scaled, y)
    print(f"Training R² (full data): {train_r2:.3f}")

    # Feature importance
    print("\nComputing permutation importance (20 repeats)...")
    builtin_imp, perm_imp, perm_std = rf_importance_analysis(rf, feat_cols, df_feat, X_scaled, y)

    print("\nTop 15 features by permutation importance:")
    print("-" * 50)
    for feat, imp in perm_imp.head(15).items():
        std = perm_std[feat]
        print(f"  {feat:<35} {imp:+.4f} ± {std:.4f}")

    # Generate importance plot
    plot_feature_importance(builtin_imp, perm_imp, perm_std)

    # SHAP analysis
    mean_shap = run_shap_analysis(rf, X_scaled, feat_cols, df_feat)
    if mean_shap is not None:
        print("\nTop 10 features by mean |SHAP|:")
        for feat, val in mean_shap.head(10).items():
            print(f"  {feat:<35} {val:.4f}")

    # Subgroup analysis
    subgroup_importance(df_feat, feat_cols)

    # Predictions
    predictions = predict_new_compositions(rf, scaler, feat_cols, df_feat)
    predictions.to_csv('results_stability_predictions.csv', index=False)
    print("\nPredictions saved to results_stability_predictions.csv")

    print("\nDone.")
