"""
Bayesian Optimization for High-Entropy Oxide (HEO) Catalyst Discovery
=======================================================================
Searches the multi-element composition space for optimal OER catalysts.
Optimizes both activity (η₁₀) and stability simultaneously.

This is a complete, runnable implementation using:
- Gaussian Process surrogate model
- Expected Hypervolume Improvement (multi-objective acquisition)
- Pareto front tracking

Usage:
    python bayesian_heo_optimizer.py

    The optimizer will:
    1. Start with 10 random compositions ("initial design")
    2. Run 40 Bayesian optimization iterations
    3. Plot the Pareto front of activity vs. stability
    4. Output the top 10 recommended compositions for synthesis

Dependencies:
    pip install numpy scipy scikit-learn matplotlib pandas
    pip install botorch torch  # For production use (optional, better performance)
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import norm
from scipy.optimize import minimize
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import Matern, ConstantKernel, WhiteKernel
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')

np.random.seed(42)


# =============================================================================
# SECTION 1: ELEMENT SPACE DEFINITION
# =============================================================================

# 8 candidate elements for HEO optimization
# Each contributes different electrochemical properties
ELEMENTS = {
    'Fe': {
        'role': 'primary OER active site (Fe³⁺/Fe⁴⁺)',
        'dissolution_potential_acid': 0.3,   # V vs RHE at which dissolution starts
        'activity_contribution': 0.85,       # Relative OER activity (0-1)
        'cost_usd_per_kg': 0.10,
    },
    'Co': {
        'role': 'OER active, synergizes with Fe',
        'dissolution_potential_acid': 0.35,
        'activity_contribution': 0.80,
        'cost_usd_per_kg': 33.0,
    },
    'Ni': {
        'role': 'structural, electron buffering, activates Fe',
        'dissolution_potential_acid': 0.10,
        'activity_contribution': 0.60,
        'cost_usd_per_kg': 13.0,
    },
    'Cr': {
        'role': 'protective Cr₂O₃ passivation, suppresses dissolution',
        'dissolution_potential_acid': 1.20,  # Cr₂O₃ very stable
        'activity_contribution': 0.05,       # Low OER activity alone
        'cost_usd_per_kg': 9.5,
    },
    'Mn': {
        'role': 'OER active in alkaline/mild acid, Mn³⁺/Mn⁴⁺',
        'dissolution_potential_acid': 1.10,  # MnO₂ more stable than Fe/Co/Ni
        'activity_contribution': 0.50,
        'cost_usd_per_kg': 1.75,
    },
    'V': {
        'role': 'V⁵⁺/V⁴⁺ redox, breaks scaling relations in LDH',
        'dissolution_potential_acid': 0.80,
        'activity_contribution': 0.40,
        'cost_usd_per_kg': 30.0,
    },
    'W': {
        'role': 'WO₃ stable phase, secondary OER activity',
        'dissolution_potential_acid': 0.90,
        'activity_contribution': 0.35,
        'cost_usd_per_kg': 35.0,
    },
    'Mo': {
        'role': 'MoO₃ stable in mild acid, secondary OER activity',
        'dissolution_potential_acid': 0.80,
        'activity_contribution': 0.40,
        'cost_usd_per_kg': 20.0,
    },
}

ELEMENT_NAMES = list(ELEMENTS.keys())
N_ELEMENTS = len(ELEMENTS)


# =============================================================================
# SECTION 2: SURROGATE OBJECTIVE FUNCTION
# =============================================================================
# In a real experiment, these functions would call your potentiostat.
# Here we use physics-inspired surrogate functions.

def composition_to_array(composition_dict):
    """Convert composition dict to numpy array (fractions, sum to 1)."""
    return np.array([composition_dict.get(el, 0.0) for el in ELEMENT_NAMES])


def predict_eta10(x):
    """
    Physics-inspired surrogate for OER overpotential in acid (mV).
    x: numpy array of element fractions (Fe, Co, Ni, Cr, Mn, V, W, Mo)

    Based on:
    - Activity volcano: Fe+Co active, Cr inactive
    - Optimal 3–5 active elements
    - Too much Cr kills activity (blocks sites)
    - Mn and V can help break scaling relations
    """
    fe, co, ni, cr, mn, v, w, mo = x

    # Base activity from active elements (lower = better OER)
    active_content = 0.8*fe + 0.75*co + 0.5*ni + 0.45*mn + 0.35*v + 0.30*w + 0.35*mo

    # Cr penalty on activity (blocks sites)
    cr_activity_penalty = cr * 200  # mV penalty per unit Cr

    # Synergy bonus for Fe+Co combination
    fe_co_synergy = -40 * (fe * co) / (0.25 * 0.25)  # Up to -40 mV bonus at equal amounts

    # V bonus (breaks scaling relations in some compositions)
    v_bonus = -20 * v * (fe + co)  # Only helps if Fe/Co present

    # Entropy bonus (more elements = slightly better active site diversity)
    n_active = sum(1 for el in [fe, co, ni, mn, v, w, mo] if el > 0.05)
    entropy_bonus = -5 * n_active if n_active > 3 else 0

    # Reference: pure Fe+Co (50/50) → η₁₀ ≈ 380 mV
    base_eta = 380 - active_content * 120 + cr_activity_penalty + fe_co_synergy + v_bonus + entropy_bonus

    # Add noise (experimental variability)
    noise = np.random.normal(0, 8)  # ±8 mV typical measurement noise

    return np.clip(base_eta + noise, 200, 600)


def predict_dissolution_rate(x):
    """
    Physics-inspired surrogate for metal dissolution rate in acid OER (μg/cm²/h at 10 mA/cm²).
    Lower = more stable.

    Based on:
    - Cr₂O₃ passivation: exponential reduction above ~15% Cr
    - Mn thermodynamic stability in MnO₂
    - W, Mo form stable oxide phases
    - Fe, Co, Ni dissolve readily in acid
    """
    fe, co, ni, cr, mn, v, w, mo = x

    # Unstable elements contribute to dissolution
    unstable_contribution = 5.0*fe + 4.5*co + 6.0*ni

    # Cr provides exponential protection above threshold (like stainless steel)
    if cr > 0.15:
        cr_protection = np.exp(-8 * (cr - 0.15))  # Exponential protection
    elif cr > 0.08:
        cr_protection = 0.5 + 0.5 * (cr / 0.15)   # Partial protection
    else:
        cr_protection = 1.0  # No protection

    # Mn and W/Mo provide moderate stability
    mn_protection = 1.0 - 0.3 * mn
    w_mo_protection = 1.0 - 0.25 * (w + mo)

    base_rate = unstable_contribution * cr_protection * mn_protection * w_mo_protection

    # Add noise
    noise = np.random.normal(0, base_rate * 0.15)

    return np.clip(base_rate + noise, 0.01, 20)


def evaluate_composition(x):
    """
    Evaluate a composition — in a real system, this calls the experiment.
    Returns both objectives (both to be minimized).

    Returns:
        (eta_10, dissolution_rate): Both minimize
    """
    # Ensure valid composition (sum to 1, all positive)
    x = np.clip(x, 0, 1)
    if x.sum() > 0:
        x = x / x.sum()
    else:
        x = np.ones(N_ELEMENTS) / N_ELEMENTS

    eta = predict_eta10(x)
    dissolution = predict_dissolution_rate(x)
    return eta, dissolution


# =============================================================================
# SECTION 3: GAUSSIAN PROCESS SURROGATE MODELS
# =============================================================================

class TwoObjectiveGPSurrogate:
    """
    Separate GP for each objective.
    """
    def __init__(self):
        kernel = ConstantKernel(1.0) * Matern(nu=2.5, length_scale=np.ones(N_ELEMENTS)) + \
                 WhiteKernel(noise_level=0.1)

        self.gp_eta = GaussianProcessRegressor(kernel=kernel, normalize_y=True,
                                               n_restarts_optimizer=5, random_state=42)
        self.gp_diss = GaussianProcessRegressor(kernel=kernel, normalize_y=True,
                                                n_restarts_optimizer=5, random_state=42)
        self.scaler_eta = StandardScaler()
        self.scaler_diss = StandardScaler()
        self.X_train = None
        self.y_eta = None
        self.y_diss = None

    def fit(self, X, y_eta, y_diss):
        self.X_train = X.copy()
        self.y_eta = y_eta.copy()
        self.y_diss = y_diss.copy()

        y_eta_scaled = self.scaler_eta.fit_transform(y_eta.reshape(-1, 1)).ravel()
        y_diss_scaled = self.scaler_diss.fit_transform(y_diss.reshape(-1, 1)).ravel()

        self.gp_eta.fit(X, y_eta_scaled)
        self.gp_diss.fit(X, y_diss_scaled)

    def predict(self, X, return_std=False):
        mu_eta_s, std_eta_s = self.gp_eta.predict(X, return_std=True)
        mu_diss_s, std_diss_s = self.gp_diss.predict(X, return_std=True)

        # Inverse transform
        mu_eta = self.scaler_eta.inverse_transform(mu_eta_s.reshape(-1, 1)).ravel()
        std_eta = std_eta_s * self.scaler_eta.scale_[0]
        mu_diss = self.scaler_diss.inverse_transform(mu_diss_s.reshape(-1, 1)).ravel()
        std_diss = std_diss_s * self.scaler_diss.scale_[0]

        if return_std:
            return mu_eta, std_eta, mu_diss, std_diss
        return mu_eta, mu_diss


# =============================================================================
# SECTION 4: PARETO FRONT UTILITIES
# =============================================================================

def is_pareto_optimal(costs):
    """
    Find the Pareto-optimal points (both objectives to minimize).
    costs: (n_points, 2) array
    Returns: boolean mask
    """
    is_optimal = np.ones(len(costs), dtype=bool)
    for i, c in enumerate(costs):
        if is_optimal[i]:
            # Check if any other point dominates this one
            dominated = np.all(costs <= c, axis=1) & np.any(costs < c, axis=1)
            dominated[i] = False  # Don't compare to itself
            is_optimal[i] = not np.any(dominated)
    return is_optimal


def hypervolume_improvement(new_point, pareto_front, ref_point):
    """
    Approximate Expected Hypervolume Improvement (EHVI) for multi-objective BO.
    Simplified version — uses dominated hypervolume contribution.

    In production: use BoTorch's qEHVI for better performance.
    """
    all_points = np.vstack([pareto_front, new_point])
    new_pareto = all_points[is_pareto_optimal(all_points)]

    # Compute hypervolume (approximate, 2D)
    def hypervolume_2d(front, ref):
        """Compute hypervolume dominated by front wrt reference point."""
        front = front[np.argsort(front[:, 0])]  # Sort by first objective
        front = front[front[:, 0] < ref[0]]      # Only points better than ref
        front = front[front[:, 1] < ref[1]]

        if len(front) == 0:
            return 0.0

        hv = 0
        prev_x = ref[0]
        for point in reversed(front):
            hv += (prev_x - point[0]) * (ref[1] - point[1])
            prev_x = point[0]
        return hv

    current_hv = hypervolume_2d(pareto_front[is_pareto_optimal(pareto_front)], ref_point)
    new_hv = hypervolume_2d(new_pareto, ref_point)

    return max(0, new_hv - current_hv)


# =============================================================================
# SECTION 5: ACQUISITION FUNCTION AND OPTIMIZATION
# =============================================================================

def acquisition_function(x_candidate, gp_model, pareto_front, ref_point, xi=0.01):
    """
    Combined acquisition: Expected Improvement on each objective + Hypervolume contribution.
    """
    x = x_candidate.reshape(1, -1)

    # Normalize to valid composition
    x = np.clip(x, 0, 1)
    x = x / (x.sum() + 1e-10)

    mu_eta, std_eta, mu_diss, std_diss = gp_model.predict(x, return_std=True)

    # Best current values
    best_eta = pareto_front[:, 0].min()
    best_diss = pareto_front[:, 1].min()

    # Expected Improvement for each objective
    def ei(mu, std, best, xi):
        if std < 1e-10:
            return 0.0
        z = (best - mu - xi) / std
        return (best - mu - xi) * norm.cdf(z) + std * norm.pdf(z)

    ei_eta = ei(mu_eta[0], std_eta[0], best_eta, xi)
    ei_diss = ei(mu_diss[0], std_diss[0], best_diss, xi)

    # Hypervolume improvement from predicted point
    predicted_point = np.array([[mu_eta[0], mu_diss[0]]])
    hvi = hypervolume_improvement(predicted_point, pareto_front, ref_point)

    # Combined score (higher = better candidate)
    score = 0.3 * ei_eta / (best_eta + 1) + 0.3 * ei_diss / (best_diss + 1) + 0.4 * hvi

    return -score  # Minimize for scipy.optimize


def suggest_next_composition(gp_model, pareto_front, ref_point, n_restarts=10):
    """
    Find the composition that maximizes the acquisition function.
    Uses multi-start optimization from random initial points.
    """
    best_score = np.inf
    best_x = None

    # Simplex constraint: compositions must sum to 1
    constraints = [{'type': 'eq', 'fun': lambda x: x.sum() - 1.0}]
    bounds = [(0.0, 0.8) for _ in range(N_ELEMENTS)]  # Max 80% of any single element

    for _ in range(n_restarts):
        # Random starting point on simplex
        x0 = np.random.dirichlet(np.ones(N_ELEMENTS))

        result = minimize(
            acquisition_function,
            x0,
            args=(gp_model, pareto_front, ref_point),
            method='SLSQP',
            bounds=bounds,
            constraints=constraints,
            options={'maxiter': 200, 'ftol': 1e-6}
        )

        if result.fun < best_score:
            best_score = result.fun
            best_x = result.x

    # Normalize to valid composition
    best_x = np.clip(best_x, 0, 1)
    best_x = best_x / best_x.sum()

    return best_x


# =============================================================================
# SECTION 6: MAIN OPTIMIZATION LOOP
# =============================================================================

def run_bayesian_optimization(n_initial=10, n_iterations=40, verbose=True):
    """
    Main Bayesian optimization loop.

    Args:
        n_initial: Number of random initial experiments
        n_iterations: Number of BO iterations
        verbose: Print progress

    Returns:
        all_X, all_eta, all_diss: All evaluated compositions and objectives
    """
    print("BAYESIAN OPTIMIZATION: HIGH-ENTROPY OXIDE COMPOSITION SEARCH")
    print("=" * 65)
    print(f"Elements: {', '.join(ELEMENT_NAMES)}")
    print(f"Objectives: minimize η₁₀ (mV) AND dissolution rate (μg/cm²/h)")
    print(f"Initial random samples: {n_initial}")
    print(f"BO iterations: {n_iterations}")
    print()

    # Reference point for hypervolume (pessimistic values)
    ref_point = np.array([600.0, 20.0])  # η₁₀ = 600 mV, dissolution = 20 μg/cm²/h

    # Phase 1: Random initial design (Space-filling)
    print("Phase 1: Random initial experiments...")
    all_X = []
    all_eta = []
    all_diss = []

    # Sample from simplex using Dirichlet
    initial_compositions = np.random.dirichlet(np.ones(N_ELEMENTS), n_initial)

    for i, x in enumerate(initial_compositions):
        eta, diss = evaluate_composition(x)
        all_X.append(x)
        all_eta.append(eta)
        all_diss.append(diss)
        if verbose:
            comp_str = ', '.join([f'{n}:{v:.2f}' for n, v in zip(ELEMENT_NAMES, x) if v > 0.05])
            print(f"  [{i+1:2d}] {comp_str}")
            print(f"        η₁₀={eta:.0f}mV, dissolution={diss:.2f}μg/cm²/h")

    all_X = np.array(all_X)
    all_eta = np.array(all_eta)
    all_diss = np.array(all_diss)

    # Phase 2: Bayesian Optimization
    print(f"\nPhase 2: Bayesian optimization ({n_iterations} iterations)...")

    gp_model = TwoObjectiveGPSurrogate()
    history = {'best_eta': [], 'best_diss': [], 'pareto_size': []}

    for iteration in range(n_iterations):
        # Fit GP to current data
        gp_model.fit(all_X, all_eta, all_diss)

        # Pareto front of current evaluations
        costs = np.column_stack([all_eta, all_diss])
        pareto_mask = is_pareto_optimal(costs)
        pareto_front = costs[pareto_mask]

        # Suggest next composition
        next_x = suggest_next_composition(gp_model, pareto_front, ref_point)

        # Evaluate (in real experiment: run in lab!)
        eta, diss = evaluate_composition(next_x)

        all_X = np.vstack([all_X, next_x])
        all_eta = np.append(all_eta, eta)
        all_diss = np.append(all_diss, diss)

        # Track progress
        history['best_eta'].append(all_eta.min())
        history['best_diss'].append(all_diss.min())
        history['pareto_size'].append(pareto_mask.sum())

        if verbose and (iteration + 1) % 10 == 0:
            print(f"  Iteration {iteration+1:3d}/{n_iterations}: "
                  f"best η₁₀={all_eta.min():.0f}mV, "
                  f"best dissolution={all_diss.min():.2f}μg/cm²/h, "
                  f"Pareto points: {pareto_mask.sum()}")

    return all_X, all_eta, all_diss, history


# =============================================================================
# SECTION 7: RESULTS ANALYSIS AND VISUALIZATION
# =============================================================================

def analyze_results(all_X, all_eta, all_diss, history, top_n=10):
    """
    Analyze optimization results and generate reports.
    """
    costs = np.column_stack([all_eta, all_diss])
    pareto_mask = is_pareto_optimal(costs)

    print("\n" + "="*65)
    print("OPTIMIZATION RESULTS")
    print("="*65)
    print(f"Total experiments: {len(all_eta)}")
    print(f"Pareto-optimal compositions: {pareto_mask.sum()}")
    print(f"Best η₁₀ achieved: {all_eta.min():.0f} mV")
    print(f"Best dissolution rate: {all_diss.min():.3f} μg/cm²/h")

    # Rank Pareto-optimal compositions by weighted score
    # Weighted score: normalize each objective, weight equally
    pareto_X = all_X[pareto_mask]
    pareto_eta = all_eta[pareto_mask]
    pareto_diss = all_diss[pareto_mask]

    # Normalized scores (lower is better for both)
    eta_norm = (pareto_eta - pareto_eta.min()) / (pareto_eta.max() - pareto_eta.min() + 1e-10)
    diss_norm = (pareto_diss - pareto_diss.min()) / (pareto_diss.max() - pareto_diss.min() + 1e-10)
    combined_score = 0.5 * eta_norm + 0.5 * diss_norm

    rank_order = np.argsort(combined_score)
    top_n = min(top_n, len(rank_order))

    print(f"\nTOP {top_n} RECOMMENDED COMPOSITIONS FOR SYNTHESIS:")
    print("-"*65)

    results = []
    for rank, idx in enumerate(rank_order[:top_n]):
        comp = pareto_X[idx]
        eta = pareto_eta[idx]
        diss = pareto_diss[idx]

        # Format composition string (only elements >2%)
        comp_parts = [(ELEMENT_NAMES[i], comp[i]) for i in range(N_ELEMENTS) if comp[i] > 0.02]
        comp_str = ''.join([f'{n}₀.{int(v*100):02d}' for n, v in comp_parts])
        comp_full = {n: round(float(v), 3) for n, v in comp_parts}

        # Estimate cost
        cost = sum(ELEMENTS[el]['cost_usd_per_kg'] * frac for el, frac in comp_full.items())

        print(f"\nRank {rank+1}: {comp_str}")
        print(f"  η₁₀ predicted: {eta:.0f} mV")
        print(f"  Dissolution:   {diss:.3f} μg/cm²/h")
        print(f"  Relative cost: ${cost:.2f}/kg (material only)")
        print(f"  Composition:   {comp_full}")
        print(f"  n_elements > 5%: {sum(1 for v in comp.tolist() if v > 0.05)}")

        results.append({
            'rank': rank + 1, 'formula': comp_str,
            'eta_10_mv': round(eta), 'dissolution_ug_cm2_h': round(diss, 3),
            'material_cost': round(cost, 2),
            **{el: round(float(comp[i]), 3) for i, el in enumerate(ELEMENT_NAMES)}
        })

    df_results = pd.DataFrame(results)
    df_results.to_csv('top_heo_compositions.csv', index=False)
    print(f"\nResults saved: top_heo_compositions.csv")

    return df_results, pareto_mask


def plot_optimization_results(all_X, all_eta, all_diss, history, pareto_mask):
    """Generate comprehensive visualization of optimization results."""

    fig, axes = plt.subplots(2, 2, figsize=(14, 11))
    fig.suptitle('Bayesian Optimization: HEO Catalyst Composition Search\n'
                 'Multi-Objective: Minimize OER Overpotential AND Dissolution Rate',
                 fontsize=13, fontweight='bold')

    n_initial = len(all_eta) - len(history['best_eta'])

    # 1. Pareto front (main result)
    ax = axes[0, 0]
    # Initial random points
    ax.scatter(all_eta[:n_initial], all_diss[:n_initial],
               c='lightgray', s=40, alpha=0.6, label='Random initial', zorder=2)
    # BO points (colored by iteration)
    bo_eta = all_eta[n_initial:]
    bo_diss = all_diss[n_initial:]
    scatter = ax.scatter(bo_eta, bo_diss, c=range(len(bo_eta)),
                         cmap='viridis', s=60, alpha=0.8, label='BO iterations', zorder=3)
    plt.colorbar(scatter, ax=ax, label='Iteration')

    # Pareto front
    pareto_eta = all_eta[pareto_mask]
    pareto_diss = all_diss[pareto_mask]
    sort_idx = np.argsort(pareto_eta)
    ax.plot(pareto_eta[sort_idx], pareto_diss[sort_idx], 'r-', linewidth=2,
            label='Pareto front', zorder=4)
    ax.scatter(pareto_eta, pareto_diss, c='red', s=80, zorder=5, marker='*',
               label=f'Pareto-optimal ({pareto_mask.sum()})')

    ax.set_xlabel('OER Overpotential η₁₀ (mV) — lower is better', fontsize=11)
    ax.set_ylabel('Dissolution Rate (μg/cm²/h) — lower is better', fontsize=11)
    ax.set_title('Pareto Front: Activity vs. Stability', fontsize=11)
    ax.legend(fontsize=8, loc='upper right')
    ax.grid(alpha=0.3)

    # 2. Convergence history
    ax = axes[0, 1]
    iterations = range(1, len(history['best_eta']) + 1)
    ax2 = ax.twinx()
    ax.plot(iterations, history['best_eta'], 'b-', linewidth=2, label='Best η₁₀ (mV)')
    ax2.plot(iterations, history['best_diss'], 'r--', linewidth=2, label='Best dissolution')
    ax.set_xlabel('BO Iteration', fontsize=11)
    ax.set_ylabel('Best η₁₀ (mV)', fontsize=11, color='blue')
    ax2.set_ylabel('Best dissolution (μg/cm²/h)', fontsize=11, color='red')
    ax.set_title('Convergence History', fontsize=11)

    lines1, labels1 = ax.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax.legend(lines1 + lines2, labels1 + labels2, fontsize=9, loc='upper right')
    ax.grid(alpha=0.3)

    # 3. Element composition of Pareto-optimal points
    ax = axes[1, 0]
    pareto_X = all_X[pareto_mask]
    pareto_df = pd.DataFrame(pareto_X, columns=ELEMENT_NAMES)
    pareto_df.index = [f'P{i+1}' for i in range(len(pareto_df))]

    # Sort by eta
    sort_idx = np.argsort(all_eta[pareto_mask])
    pareto_sorted = pareto_df.iloc[sort_idx].reset_index(drop=True)
    pareto_sorted.index = [f'Pareto {i+1}' for i in range(len(pareto_sorted))]

    pareto_sorted.plot(kind='bar', stacked=True, ax=ax,
                       colormap='tab20', alpha=0.85, width=0.8)
    ax.set_xlabel('Composition (sorted by activity)', fontsize=11)
    ax.set_ylabel('Element fraction', fontsize=11)
    ax.set_title('Element Composition of Pareto-Optimal Points\n(Sorted: left=most active, right=most stable)',
                 fontsize=10)
    ax.legend(fontsize=8, loc='upper right', ncol=2)
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45)

    # 4. Element importance across all experiments
    ax = axes[1, 1]
    # Correlation of each element fraction with η₁₀ and dissolution
    corr_eta = [np.corrcoef(all_X[:, i], all_eta)[0, 1] for i in range(N_ELEMENTS)]
    corr_diss = [np.corrcoef(all_X[:, i], all_diss)[0, 1] for i in range(N_ELEMENTS)]

    x_pos = np.arange(N_ELEMENTS)
    width = 0.35
    ax.bar(x_pos - width/2, corr_eta, width, label='Correlation with η₁₀', color='steelblue', alpha=0.8)
    ax.bar(x_pos + width/2, corr_diss, width, label='Correlation with dissolution', color='coral', alpha=0.8)

    ax.axhline(0, color='black', linewidth=0.5)
    ax.set_xticks(x_pos)
    ax.set_xticklabels(ELEMENT_NAMES, fontsize=11)
    ax.set_ylabel('Pearson Correlation', fontsize=11)
    ax.set_title('Element Correlations with Objectives\n(Negative = element reduces objective)', fontsize=10)
    ax.legend(fontsize=9)
    ax.grid(axis='y', alpha=0.3)

    plt.tight_layout()
    plt.savefig('bayesian_heo_optimization.png', dpi=150, bbox_inches='tight')
    plt.show()
    print("Plot saved: bayesian_heo_optimization.png")


# =============================================================================
# SECTION 8: EXTENSION GUIDE
# =============================================================================

def print_extension_guide():
    """Print guide for extending this code to real experiments."""

    guide = """
    ================================================================================
    HOW TO USE THIS CODE WITH REAL EXPERIMENTAL DATA
    ================================================================================

    Step 1: Replace the surrogate functions with real experimental calls

        def evaluate_composition(x):
            # x: numpy array of element fractions
            # Returns: (eta_10_mv, dissolution_rate_ug_per_cm2_per_h)

            # YOUR SYNTHESIS + MEASUREMENT CODE HERE:
            # 1. Format composition as synthesis parameters
            # 2. Call synthesis robot API (if automated) or queue for manual synthesis
            # 3. Run electrochemical measurement (potentiostat API)
            # 4. Return results

            # Example with Biologic potentiostat (via Python EC-Lab API):
            # from eclib import BiologicPotentiostat
            # pstat = BiologicPotentiostat('192.168.1.10')
            # results = pstat.run_oer_protocol(electrolyte='H2SO4_0.5M', j=10)
            # eta_10 = results.overpotential_at_10mAcm2
            # ...

            pass  # Replace with real measurement

    Step 2: Increase n_iterations to your budget

        # Each iteration = one synthesis + measurement experiment
        # Budget of 200 experiments → well-converged Pareto front
        run_bayesian_optimization(n_initial=20, n_iterations=180)

    Step 3: Add constraints relevant to your lab

        # Example: enforce at least 10% Cr for acid stability
        constraints = [
            {'type': 'eq', 'fun': lambda x: x.sum() - 1.0},
            {'type': 'ineq', 'fun': lambda x: x[ELEMENT_NAMES.index('Cr')] - 0.10},
        ]

    Step 4: Connect to Materials Project for DFT features

        from mp_api.client import MPRester
        with MPRester('YOUR_API_KEY') as mpr:
            # Get formation energies, Pourbaix stability windows
            # Use as additional GP features
            pass

    Step 5: For production-quality BO, switch to BoTorch

        # This code uses a custom GP + acquisition.
        # For larger budgets (>100 experiments), use BoTorch's qEHVI:
        # pip install botorch
        # from botorch.acquisition import qExpectedHypervolumeImprovement
        # Much better sample efficiency, GPU-accelerated, parallelizable

    Step 6: Log everything to a database

        import sqlite3
        # Log every evaluation: composition, conditions, results, timestamp
        # This creates a reproducible experimental record

    ================================================================================
    RECOMMENDED WORKFLOW FOR A 6-MONTH CAMPAIGN:
    ================================================================================

    Month 1: 20 random experiments (Phase 1) → identify rough activity/stability tradeoffs
    Month 2: 40 BO experiments (Phase 2) → refine Pareto front
    Month 3: 30 validation experiments (best Pareto points, longer stability tests)
    Month 4: 20 mechanism experiments (characterize best compositions in depth)
    Month 5: 30 synthesis optimization (optimize synthesis conditions for top compositions)
    Month 6: Write-up + publish dataset

    Total: ~140 experiments → publishable multi-objective optimization study
    ================================================================================
    """
    print(guide)


# =============================================================================
# MAIN
# =============================================================================

if __name__ == '__main__':
    # Run optimization
    all_X, all_eta, all_diss, history = run_bayesian_optimization(
        n_initial=10,
        n_iterations=40,
        verbose=True
    )

    # Analyze and report
    df_results, pareto_mask = analyze_results(all_X, all_eta, all_diss, history, top_n=10)

    # Visualize
    plot_optimization_results(all_X, all_eta, all_diss, history, pareto_mask)

    # Extension guide
    print_extension_guide()

    print("\nKey output files:")
    print("  top_heo_compositions.csv    — Top recommended compositions")
    print("  bayesian_heo_optimization.png  — Optimization visualization")
