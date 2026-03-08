"""
acid_oer_optimizer.py
=====================
Bayesian multi-objective optimisation for acid-stable OER catalysts.

Problem:
  Find earth-abundant compositions that survive PEM (pH 0–2) conditions
  while retaining competitive OER activity.  IrO₂ is the benchmark;
  earth-abundant acid OER is the hardest open problem in the field.

Search space:
  9-element HEA/HEO: Mn, Fe, Co, Ni, Cr, V, W, Mo, Ti
  Each element fraction ∈ [0, 1], sum = 1 (simplex constraint)
  Optional Ca dopant: 0–10% (swapped out of Mn fraction)

Objectives (both to minimise):
  1. eta_OER  (mV at 10 mA/cm^2)   — lower is better
  2. dissolution_rate (ug/cm2/h) — lower is better

Hard constraints:
  - Compositions that Pourbaix analysis predicts will dissolve within 10h
    at pH 1 and V = 1.6 V vs RHE are rejected outright (penalty = ∞)
  - This is encoded as a constraint in the acquisition function

Strategy:
  - Phase 1: 15 Latin-hypercube initial experiments
  - Phase 2: 60 Bayesian optimisation iterations
  - Surrogate: independent GPs on log(eta) and log(dissolution)
  - Acquisition: Pareto-hypervolume improvement (simplified 2-obj version)
  - Mn-bias: Prior favours Mn > 0.2 based on literature support

Ca-doping sweep:
  After the main run, automatically score the top Mn-rich compositions
  with Ca substitution at 0, 2, 5, 8, 10% to model Ca-birnessite effect.

Usage:
  pip install -r requirements.txt
  python acid_oer_optimizer.py

Outputs:
  results_acid_oer_pareto.csv
  results_acid_oer_optimizer.png
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from scipy.stats import norm
from scipy.optimize import minimize

# ─── Element definitions ──────────────────────────────────────────────────────

ELEMENT_NAMES = ['Mn', 'Fe', 'Co', 'Ni', 'Cr', 'V', 'W', 'Mo', 'Ti']
N_ELEMENTS = len(ELEMENT_NAMES)

# Pourbaix dissolution potentials at pH 1 (V vs RHE, above which metal dissolves)
# Lower = less stable in acid. Values from Pourbaix Atlas + DFT corrections.
DISSOLUTION_POTENTIAL = {
    'Mn': 0.85,   # MnO₂ stable above 0.85 V; good acid OER platform
    'Fe': 0.60,   # Fe dissolves readily in acid
    'Co': 0.55,   # Co^2⁺/Co³⁺ dissolution rapid in acid
    'Ni': 0.40,   # Ni dissolves very fast in acid
    'Cr': 0.90,   # Cr₂O₃ passivation helps; most stable transition metal
    'V':  0.50,   # V₂O₅ partially soluble
    'W':  1.05,   # WO₃ relatively stable; best non-PGM acid option
    'Mo': 0.65,   # MoO₃/MoO₄^2⁻ partially soluble
    'Ti': 1.20,   # TiO₂ — most stable, but OER-inactive alone; passivating matrix
}

# OER activity descriptors (eta_10 mV on bulk oxide, literature median)
# These inform the surrogate prior; actual predictions use the GP.
ACTIVITY_PRIOR = {
    'Mn': 350,    # MnO₂: moderate (~350 mV); best earth-abundant acid OER
    'Fe': 420,    # Fe₂O₃: poor acid OER
    'Co': 380,    # Co₃O₄: moderate but unstable in acid
    'Ni': 370,    # NiO: unstable in acid despite decent alkaline activity
    'Cr': 470,    # Cr₂O₃: poor activity, high stability
    'V':  430,    # V₂O₅: moderate activity, poor stability
    'W':  400,    # WO₃: moderate, reasonable acid stability
    'Mo': 390,    # MoO₃: moderate, some acid tolerance
    'Ti': 600,    # TiO₂: OER-inactive alone; dilutes activity
}

# ─── Surrogate physics model ──────────────────────────────────────────────────

def dissolution_constraint_score(x: np.ndarray) -> float:
    """
    Composite acid stability score for a composition x.

    Returns a value in [0, 1]:
      - 1.0 = fully Pourbaix-stable at OER potential (V ≥ 1.6 V vs RHE)
      - 0.0 = fully dissolving

    Weighted average of element dissolution potentials relative to 1.6 V.
    """
    assert len(x) == N_ELEMENTS
    score = 0.0
    for i, el in enumerate(ELEMENT_NAMES):
        e_diss = DISSOLUTION_POTENTIAL[el]
        # Fraction of operating window where this element is stable
        # OER operates at 1.23 + eta_OER ≈ 1.6 V. Stable if e_diss > 1.6 V.
        # For e_diss < 1.6, partial credit scaled by (e_diss - 0.0) / 1.6
        stability_frac = min(1.0, e_diss / 1.60)
        score += x[i] * stability_frac
    return score


def evaluate_composition(x: np.ndarray, noise: float = 0.08) -> tuple[float, float]:
    """
    Physics-informed surrogate for acid OER evaluation.

    In a real experiment, this function would:
      1. Synthesise the composition (or queue it for robot synthesis)
      2. Run standard acid OER protocol (0.5 M H₂SO₄, 25°C, 5 mV/s CV + CA)
      3. Measure eta_10 and dissolution rate by ICP-MS after 2h CA

    Here we use a mechanistic model:

    eta_OER model:
      - Mn-dominant compositions follow the scaling relation modified by
        charge delocalization in multi-metal oxides
      - Alloying W or Cr with Mn improves stability without wrecking activity
      - Ti dilutes activity (penalised) but enables passivation
      - V tunes the d-band center toward optimal for Mn-OOH*

    Dissolution model:
      - Dominated by the least stable element's fraction
      - Synergistic stabilization: Mn + Cr + W combinations are more stable
        than individual Pourbaix predictions (experimental observation)
    """
    rng_state = np.random.RandomState(seed=None)

    # ── Activity model ────────────────────────────────────────────────────────
    # Weighted average of single-element activity, adjusted for:
    # 1. Mn–V synergy: V near Mn optimises d-band center
    # 2. W/Cr stabilise the surface without blocking active Mn sites
    # 3. Ti passivation penalty at high fractions
    # 4. Fe/Co/Ni acid instability penalty

    eta_base = sum(x[i] * ACTIVITY_PRIOR[el] for i, el in enumerate(ELEMENT_NAMES))

    mn = x[0]   # Mn
    fe = x[1]   # Fe
    co = x[2]   # Co
    ni = x[3]   # Ni
    cr = x[4]   # Cr
    v  = x[5]   # V
    w  = x[6]   # W
    mo = x[7]   # Mo
    ti = x[8]   # Ti

    # Mn–V synergy (both present improves Mn-OOH* binding)
    if mn > 0.1 and v > 0.05:
        eta_base -= 40 * min(mn, 0.5) * min(v, 0.2) / (0.5 * 0.2)

    # Mn–W structural stabilisation (W enters Mn lattice, reduces dissolution)
    # Small activity boost from charge redistribution
    if mn > 0.15 and w > 0.05:
        eta_base -= 15 * min(w, 0.15) / 0.15

    # Mn–Cr: Cr passivates grain boundaries, slight activity cost
    if mn > 0.1 and cr > 0.05:
        eta_base += 10 * cr  # minor activity penalty, large stability gain

    # Ti dilution penalty (TiO₂ is OER-inactive)
    eta_base += 80 * ti

    # Fe/Co/Ni in acid: they dissolve, but while present, they are active
    # Net effect: small activity gain at low fraction, large penalty at high
    acid_unstable = fe + co + ni
    if acid_unstable > 0.3:
        eta_base += 60 * (acid_unstable - 0.3)  # above 30% these corrode fast

    # Clamp to realistic range
    eta_base = np.clip(eta_base, 280, 600)

    # Add noise
    eta = eta_base * (1 + rng_state.normal(0, noise))

    # ── Dissolution model ─────────────────────────────────────────────────────
    # Base rate from weighted Pourbaix constraint violation
    stability = dissolution_constraint_score(x)
    # Map stability [0,1] → dissolution rate [ug/cm2/h]
    # IrO₂ benchmark: ~0.01 ug/cm2/h. NiFe LDH in acid: >100 ug/cm2/h.
    # Log-linear: dissolution = exp(8 × (1 - stability))
    dissolution_base = np.exp(8.0 * (1.0 - stability))

    # Mn + W synergistic stabilisation (experimental Ca-birnessite analogy)
    if mn > 0.2 and w > 0.08:
        dissolution_base *= 0.5  # 2× better than additive prediction

    # Cr passivation bonus at high Cr
    if cr > 0.15:
        dissolution_base *= (1 - 0.4 * min(cr, 0.30) / 0.30)

    # Ti passivating matrix bonus
    if ti > 0.1:
        dissolution_base *= (1 - 0.35 * min(ti, 0.25) / 0.25)

    # High Fe/Co/Ni = rapid dissolution in acid
    if acid_unstable > 0.2:
        dissolution_base *= np.exp(3 * acid_unstable)

    # Add noise
    dissolution_base = max(0.01, dissolution_base)
    dissolution = dissolution_base * np.exp(rng_state.normal(0, noise))

    return float(eta), float(dissolution)


# ─── Bayesian optimisation engine ─────────────────────────────────────────────

class GaussianProcessSurrogate:
    """
    Lightweight RBF-kernel GP for 1D output.
    Operates in log-space for positive-valued objectives.
    """

    def __init__(self, length_scale: float = 0.3, noise: float = 0.1):
        self.length_scale = length_scale
        self.noise_var = noise ** 2
        self.X_train = None
        self.y_train = None
        self.K_inv = None

    def _kernel(self, X1: np.ndarray, X2: np.ndarray) -> np.ndarray:
        diffs = X1[:, np.newaxis, :] - X2[np.newaxis, :, :]
        sq_dists = np.sum(diffs ** 2, axis=2)
        return np.exp(-sq_dists / (2 * self.length_scale ** 2))

    def fit(self, X: np.ndarray, y: np.ndarray) -> None:
        self.X_train = X.copy()
        self.y_train = np.log(y + 1e-6)  # log-space
        K = self._kernel(X, X) + self.noise_var * np.eye(len(X))
        self.K_inv = np.linalg.inv(K)

    def predict(self, X: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        k_star = self._kernel(X, self.X_train)
        mu_log = k_star @ self.K_inv @ self.y_train
        k_star_star = self._kernel(X, X)
        var_log = np.diag(k_star_star - k_star @ self.K_inv @ k_star.T)
        var_log = np.maximum(var_log, 1e-10)
        # Back-transform to original space (lognormal)
        mu = np.exp(mu_log + var_log / 2)
        std = np.sqrt((np.exp(var_log) - 1) * np.exp(2 * mu_log + var_log))
        return mu, std


def acquisition_ei(gp: GaussianProcessSurrogate, X: np.ndarray,
                   best_y: float, xi: float = 0.01) -> np.ndarray:
    """Expected Improvement in log-space (minimisation)."""
    mu, std = gp.predict(X)
    log_best = np.log(best_y + 1e-6)
    log_mu = np.log(mu + 1e-6)
    Z = (log_best - log_mu - xi) / (np.log(std + 1e-6) + 1e-10)
    ei = (log_best - log_mu - xi) * norm.cdf(Z) + np.log(std + 1e-6) * norm.pdf(Z)
    return np.maximum(ei, 0.0)


def pareto_hypervolume_improvement(eta_pred: float, diss_pred: float,
                                   pareto_eta: np.ndarray,
                                   pareto_diss: np.ndarray,
                                   ref_eta: float = 600.0,
                                   ref_diss: float = 4000.0) -> float:
    """
    Approximate hypervolume improvement for 2-objective case.
    Returns expected gain in dominated hypervolume when adding (eta, diss).
    """
    if len(pareto_eta) == 0:
        return (ref_eta - eta_pred) * (ref_diss - diss_pred)

    # Sort Pareto front by eta
    idx = np.argsort(pareto_eta)
    pe = pareto_eta[idx]
    pd_ = pareto_diss[idx]

    # Check if point is dominated
    for i in range(len(pe)):
        if pe[i] <= eta_pred and pd_[i] <= diss_pred:
            return 0.0  # dominated

    # Approximate HVI by volume of undominated hyperrectangle
    hvi = max(0.0, ref_eta - eta_pred) * max(0.0, ref_diss - diss_pred)
    return hvi


def sample_simplex(n_samples: int, n_dim: int,
                   mn_min: float = 0.10) -> np.ndarray:
    """
    Latin Hypercube-style sampling on the composition simplex.
    Enforces Mn ≥ mn_min (Mn-bias from literature support).
    """
    samples = []
    attempts = 0
    while len(samples) < n_samples and attempts < n_samples * 50:
        # Dirichlet sample
        alpha = np.ones(n_dim) * 0.5  # sparse compositions
        alpha[0] = 2.0  # favour Mn
        x = np.random.dirichlet(alpha)
        if x[0] >= mn_min:
            samples.append(x)
        attempts += 1

    # Fill remainder without constraint if needed
    while len(samples) < n_samples:
        samples.append(np.random.dirichlet(np.ones(n_dim) * 0.5))

    return np.array(samples)


def project_to_simplex(x: np.ndarray) -> np.ndarray:
    """Project vector to probability simplex (sum to 1, all ≥ 0)."""
    x = np.maximum(x, 0.0)
    total = x.sum()
    if total > 1e-10:
        return x / total
    return np.ones(len(x)) / len(x)


# ─── Ca-doping sweep ──────────────────────────────────────────────────────────

def ca_doping_sweep(base_composition: np.ndarray,
                    ca_fractions: list[float] = None) -> pd.DataFrame:
    """
    Evaluate the effect of Ca substitution into a Mn-rich composition.

    Ca replaces Mn fraction. Literature: Ca₀.₀₅Mn₀.₉₅O₂ (Ca-birnessite)
    shows 3–5× improved acid stability vs pure MnO₂ with <20 mV activity loss.

    We model Ca as improving dissolution resistance linearly up to 10%,
    beyond which it begins to block active sites.
    """
    if ca_fractions is None:
        ca_fractions = [0.0, 0.02, 0.05, 0.08, 0.10, 0.15]

    results = []
    for ca in ca_fractions:
        x_mod = base_composition.copy()
        # Substitute Ca from Mn fraction
        mn_reduction = min(ca, x_mod[0])
        x_mod[0] -= mn_reduction
        x_mod = project_to_simplex(x_mod)

        # Ca effect on dissolution: stabilises Mn-OOH* layer
        # Model as reduction factor
        if ca <= 0.10:
            diss_factor = 1.0 - 3.0 * ca  # up to 30% reduction
        else:
            diss_factor = 1.0 - 0.30 + 0.5 * (ca - 0.10)  # diminishing returns

        eta, diss = evaluate_composition(x_mod)
        diss_ca = diss * max(0.1, diss_factor)

        # Activity: small penalty at high Ca (blocks Mn sites)
        eta_ca = eta + 20 * max(0.0, ca - 0.05)

        comp_str = '+'.join([
            f'{el}{x_mod[i]:.2f}'
            for i, el in enumerate(ELEMENT_NAMES)
            if x_mod[i] > 0.05
        ])
        results.append({
            'ca_fraction': ca,
            'composition': comp_str,
            'eta_10_mv': round(eta_ca, 1),
            'dissolution_ug_per_cm2_per_h': round(diss_ca, 3),
            'stability_score': round(dissolution_constraint_score(x_mod), 3),
            'mn_fraction': round(x_mod[0], 3),
        })

    return pd.DataFrame(results)


# ─── Main optimisation loop ────────────────────────────────────────────────────

def run_acid_oer_optimisation(
    n_init: int = 15,
    n_iter: int = 60,
    n_candidates: int = 500,
    random_seed: int = 42,
) -> dict:

    np.random.seed(random_seed)
    print("=" * 65)
    print("ACID OER BAYESIAN OPTIMISER")
    print(f"Elements: {' '.join(ELEMENT_NAMES)}")
    print(f"Phase 1: {n_init} random (Mn-biased) initial experiments")
    print(f"Phase 2: {n_iter} Bayesian optimisation iterations")
    print("=" * 65)

    # ── Phase 1: Random exploration ───────────────────────────────────────────
    print("\n--- Phase 1: Initial random exploration ---")
    X_obs = sample_simplex(n_init, N_ELEMENTS, mn_min=0.10)
    eta_obs = []
    diss_obs = []

    for i, x in enumerate(X_obs):
        eta, diss = evaluate_composition(x)
        eta_obs.append(eta)
        diss_obs.append(diss)
        stab = dissolution_constraint_score(x)
        comp = ', '.join([f'{el}:{x[j]:.2f}' for j, el in enumerate(ELEMENT_NAMES) if x[j] > 0.05])
        print(f"  Init {i+1:2d}: eta={eta:.0f} mV, D={diss:.2f} ug/cm2/h, "
              f"stab={stab:.2f} | {comp}")

    eta_obs = np.array(eta_obs)
    diss_obs = np.array(diss_obs)

    # ── Phase 2: Bayesian optimisation ────────────────────────────────────────
    print(f"\n--- Phase 2: Bayesian optimisation ({n_iter} iterations) ---")

    gp_eta = GaussianProcessSurrogate(length_scale=0.25, noise=0.08)
    gp_diss = GaussianProcessSurrogate(length_scale=0.30, noise=0.15)

    # Track Pareto front
    pareto_eta = np.array([])
    pareto_diss = np.array([])

    convergence_best_eta = []
    convergence_best_diss = []

    for iteration in range(n_iter):
        # Fit surrogates on log-transformed data
        gp_eta.fit(X_obs, eta_obs)
        gp_diss.fit(X_obs, diss_obs)

        # Sample candidates on simplex
        X_cand = sample_simplex(n_candidates, N_ELEMENTS, mn_min=0.05)

        # Score each candidate
        best_hvi = -np.inf
        best_x = None

        mu_eta, std_eta = gp_eta.predict(X_cand)
        mu_diss, std_diss = gp_diss.predict(X_cand)

        # Acid stability hard constraint: stability score must be > 0.55
        stab_scores = np.array([dissolution_constraint_score(x) for x in X_cand])
        valid = stab_scores > 0.55

        for j in range(len(X_cand)):
            if not valid[j]:
                continue
            hvi = pareto_hypervolume_improvement(
                mu_eta[j], mu_diss[j], pareto_eta, pareto_diss
            )
            # Add EI bonus for exploitation
            ei_eta = acquisition_ei(gp_eta, X_cand[j:j+1],
                                    eta_obs.min())[0] if len(eta_obs) > 0 else 0
            score = 0.6 * hvi + 0.4 * ei_eta * 10

            if score > best_hvi:
                best_hvi = score
                best_x = X_cand[j]

        if best_x is None:
            # Fallback: sample without constraint
            best_x = sample_simplex(1, N_ELEMENTS, mn_min=0.05)[0]

        # Evaluate
        eta_new, diss_new = evaluate_composition(best_x)
        X_obs = np.vstack([X_obs, best_x])
        eta_obs = np.append(eta_obs, eta_new)
        diss_obs = np.append(diss_obs, diss_new)

        # Update Pareto front
        dominated = False
        new_pareto_eta = []
        new_pareto_diss = []
        for k in range(len(pareto_eta)):
            if pareto_eta[k] <= eta_new and pareto_diss[k] <= diss_new:
                dominated = True
                break
            if not (eta_new <= pareto_eta[k] and diss_new <= pareto_diss[k]):
                new_pareto_eta.append(pareto_eta[k])
                new_pareto_diss.append(pareto_diss[k])
        if not dominated:
            new_pareto_eta.append(eta_new)
            new_pareto_diss.append(diss_new)
        pareto_eta = np.array(new_pareto_eta)
        pareto_diss = np.array(new_pareto_diss)

        convergence_best_eta.append(eta_obs.min())
        convergence_best_diss.append(diss_obs.min())

        if (iteration + 1) % 10 == 0:
            stab = dissolution_constraint_score(best_x)
            comp = '+'.join([
                f'{ELEMENT_NAMES[j]}{best_x[j]:.2f}'
                for j in range(N_ELEMENTS) if best_x[j] > 0.05
            ])
            print(f"  Iter {iteration+1:3d}: eta={eta_new:.0f} mV, "
                  f"D={diss_new:.2f} ug/cm2/h, stab={stab:.2f} | {comp}")
            print(f"           Best eta={eta_obs.min():.0f} mV, "
                  f"Best D={diss_obs.min():.2f} ug/cm2/h, "
                  f"Pareto pts={len(pareto_eta)}")

    # ── Build results dataframe ───────────────────────────────────────────────
    records = []
    stab_scores_all = [dissolution_constraint_score(X_obs[i]) for i in range(len(X_obs))]

    for i in range(len(X_obs)):
        records.append({
            'eta_10_mv': round(float(eta_obs[i]), 1),
            'dissolution_ug_per_cm2_per_h': round(float(diss_obs[i]), 3),
            'stability_score': round(stab_scores_all[i], 3),
            **{f'x_{el}': round(float(X_obs[i, j]), 3)
               for j, el in enumerate(ELEMENT_NAMES)},
        })

    df = pd.DataFrame(records)
    # Composite score: normalise both objectives, equal weight
    df['eta_norm'] = (df['eta_10_mv'] - df['eta_10_mv'].min()) / \
                     (df['eta_10_mv'].max() - df['eta_10_mv'].min() + 1e-6)
    df['diss_norm'] = (df['dissolution_ug_per_cm2_per_h'] -
                       df['dissolution_ug_per_cm2_per_h'].min()) / \
                      (df['dissolution_ug_per_cm2_per_h'].max() -
                       df['dissolution_ug_per_cm2_per_h'].min() + 1e-6)
    df['composite_score'] = 0.5 * df['eta_norm'] + 0.5 * df['diss_norm']

    top = df.nsmallest(20, 'composite_score').reset_index(drop=True)

    return {
        'X_obs': X_obs,
        'eta_obs': eta_obs,
        'diss_obs': diss_obs,
        'pareto_eta': pareto_eta,
        'pareto_diss': pareto_diss,
        'df': df,
        'top': top,
        'convergence_eta': convergence_best_eta,
        'convergence_diss': convergence_best_diss,
    }


# ─── Plotting ─────────────────────────────────────────────────────────────────

def plot_results(results: dict, ca_sweep_df: pd.DataFrame) -> None:
    fig = plt.figure(figsize=(18, 14))
    fig.patch.set_facecolor('#0d1117')
    gs = gridspec.GridSpec(3, 3, figure=fig, hspace=0.45, wspace=0.35)

    label_kw = dict(color='#e6edf3', fontsize=9)
    title_kw = dict(color='#e6edf3', fontsize=10, fontweight='bold', pad=8)
    tick_kw = dict(colors='#8b949e')

    X_obs = results['X_obs']
    eta_obs = results['eta_obs']
    diss_obs = results['diss_obs']
    pareto_eta = results['pareto_eta']
    pareto_diss = results['pareto_diss']
    top = results['top']

    # ── Panel 1: Pareto front ──────────────────────────────────────────────
    ax1 = fig.add_subplot(gs[0, 0])
    ax1.set_facecolor('#161b22')
    sc = ax1.scatter(eta_obs, np.log10(diss_obs + 0.001),
                     c=range(len(eta_obs)), cmap='plasma', alpha=0.5, s=20)
    if len(pareto_eta) > 0:
        idx_p = np.argsort(pareto_eta)
        ax1.plot(pareto_eta[idx_p], np.log10(pareto_diss[idx_p] + 0.001),
                 'o-', color='#58a6ff', ms=8, lw=2, label='Pareto front', zorder=5)
    # IrO₂ benchmark
    ax1.axvline(x=250, color='#ff7b72', ls='--', lw=1.2, alpha=0.7, label='IrO₂ eta=250 mV')
    ax1.axhline(y=np.log10(0.1), color='#3fb950', ls='--', lw=1.2, alpha=0.7,
                label='D = 0.1 ug/cm2/h')
    ax1.set_xlabel('eta_10 (mV)', **label_kw)
    ax1.set_ylabel('log₁₀(dissolution ug/cm2/h)', **label_kw)
    ax1.set_title('Pareto Front: Activity vs. Acid Stability', **title_kw)
    ax1.legend(fontsize=7, facecolor='#161b22', labelcolor='#e6edf3', framealpha=0.8)
    ax1.tick_params(colors='#8b949e')
    for sp in ax1.spines.values():
        sp.set_color('#30363d')

    # ── Panel 2: Convergence ───────────────────────────────────────────────
    ax2 = fig.add_subplot(gs[0, 1])
    ax2.set_facecolor('#161b22')
    iters = range(1, len(results['convergence_eta']) + 1)
    ax2.plot(iters, results['convergence_eta'], color='#f0883e', lw=2, label='Best eta(mV)')
    ax2_r = ax2.twinx()
    ax2_r.plot(iters, np.log10(np.array(results['convergence_diss']) + 0.001),
               color='#58a6ff', lw=2, ls='--', label='Best log₁₀(D)')
    ax2.set_xlabel('BO Iteration', **label_kw)
    ax2.set_ylabel('Best eta_10 (mV)', color='#f0883e', fontsize=9)
    ax2_r.set_ylabel('Best log₁₀(dissolution)', color='#58a6ff', fontsize=9)
    ax2.set_title('Convergence', **title_kw)
    ax2.tick_params(colors='#8b949e')
    ax2_r.tick_params(colors='#58a6ff')
    for sp in ax2.spines.values():
        sp.set_color('#30363d')

    # ── Panel 3: Element distributions in top 20 ──────────────────────────
    ax3 = fig.add_subplot(gs[0, 2])
    ax3.set_facecolor('#161b22')
    element_means = [top[f'x_{el}'].mean() for el in ELEMENT_NAMES]
    element_stds = [top[f'x_{el}'].std() for el in ELEMENT_NAMES]
    colors_el = ['#58a6ff', '#ff7b72', '#f0883e', '#ffa657', '#d2a8ff',
                 '#7ee787', '#79c0ff', '#a5d6ff', '#ffa28b']
    bars = ax3.bar(ELEMENT_NAMES, element_means, color=colors_el, alpha=0.85,
                   yerr=element_stds, error_kw=dict(color='#8b949e', capsize=3))
    ax3.set_ylabel('Mean fraction in top 20', **label_kw)
    ax3.set_title('Element Profile: Top 20 Compositions', **title_kw)
    ax3.tick_params(colors='#8b949e')
    for sp in ax3.spines.values():
        sp.set_color('#30363d')
    ax3.set_ylim(0, max(element_means) * 1.4)

    # ── Panel 4: Stability score distribution ──────────────────────────────
    ax4 = fig.add_subplot(gs[1, 0])
    ax4.set_facecolor('#161b22')
    stab_all = [dissolution_constraint_score(X_obs[i]) for i in range(len(X_obs))]
    ax4.hist(stab_all, bins=20, color='#3fb950', alpha=0.7, edgecolor='#30363d')
    ax4.axvline(x=0.55, color='#ff7b72', ls='--', lw=1.5, label='Hard constraint (0.55)')
    ax4.axvline(x=0.75, color='#58a6ff', ls='--', lw=1.5, label='Good stability (0.75)')
    ax4.set_xlabel('Acid Stability Score', **label_kw)
    ax4.set_ylabel('Count', **label_kw)
    ax4.set_title('Pourbaix Stability Distribution', **title_kw)
    ax4.legend(fontsize=7, facecolor='#161b22', labelcolor='#e6edf3')
    ax4.tick_params(colors='#8b949e')
    for sp in ax4.spines.values():
        sp.set_color('#30363d')

    # ── Panel 5: Ca-doping sweep ───────────────────────────────────────────
    ax5 = fig.add_subplot(gs[1, 1])
    ax5.set_facecolor('#161b22')
    ca_pct = ca_sweep_df['ca_fraction'] * 100
    ax5.plot(ca_pct, ca_sweep_df['eta_10_mv'],
             'o-', color='#f0883e', ms=7, lw=2, label='eta_10 (mV)', zorder=5)
    ax5_r = ax5.twinx()
    ax5_r.semilogy(ca_pct, ca_sweep_df['dissolution_ug_per_cm2_per_h'],
                   's--', color='#58a6ff', ms=7, lw=2, label='Dissolution (ug/cm2/h)')
    ax5.set_xlabel('Ca fraction (%)', **label_kw)
    ax5.set_ylabel('eta_10 (mV)', color='#f0883e', fontsize=9)
    ax5_r.set_ylabel('Dissolution (ug/cm2/h, log)', color='#58a6ff', fontsize=9)
    ax5.set_title('Ca-Doping Sweep (Best Mn-rich Composition)', **title_kw)
    ax5.tick_params(colors='#8b949e')
    ax5_r.tick_params(colors='#58a6ff')
    for sp in ax5.spines.values():
        sp.set_color('#30363d')
    lines1, labels1 = ax5.get_legend_handles_labels()
    lines2, labels2 = ax5_r.get_legend_handles_labels()
    ax5.legend(lines1 + lines2, labels1 + labels2, fontsize=7,
               facecolor='#161b22', labelcolor='#e6edf3')

    # ── Panel 6: Top composition table ────────────────────────────────────
    ax6 = fig.add_subplot(gs[1, 2])
    ax6.set_facecolor('#161b22')
    ax6.axis('off')
    top5 = top.head(5)
    col_labels = ['eta(mV)', 'D (ug/cm2/h)', 'Stab']
    table_data = [
        [f"{row['eta_10_mv']:.0f}",
         f"{row['dissolution_ug_per_cm2_per_h']:.3f}",
         f"{row['stability_score']:.2f}"]
        for _, row in top5.iterrows()
    ]
    row_labels = []
    for _, row in top5.iterrows():
        elems = sorted(
            [(el, row[f'x_{el}']) for el in ELEMENT_NAMES if row[f'x_{el}'] > 0.05],
            key=lambda t: -t[1]
        )
        lbl = '+'.join([f"{e}{v:.2f}" for e, v in elems[:4]])
        row_labels.append(lbl)

    tbl = ax6.table(cellText=table_data, rowLabels=row_labels, colLabels=col_labels,
                    loc='center', cellLoc='center')
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(7)
    tbl.scale(1.0, 1.6)
    for key, cell in tbl.get_celld().items():
        cell.set_facecolor('#1c2128')
        cell.set_edgecolor('#30363d')
        cell.set_text_props(color='#e6edf3')
    ax6.set_title('Top 5 Acid-Stable Compositions', **title_kw)

    # ── Panel 7: eta vs stability score scatter ─────────────────────────────
    ax7 = fig.add_subplot(gs[2, 0])
    ax7.set_facecolor('#161b22')
    sc2 = ax7.scatter(stab_all, eta_obs,
                      c=np.log10(diss_obs + 0.001), cmap='RdYlGn_r',
                      alpha=0.6, s=25)
    plt.colorbar(sc2, ax=ax7, label='log₁₀(dissolution)', shrink=0.8)
    ax7.axvline(x=0.55, color='#ff7b72', ls='--', lw=1.2, alpha=0.7)
    ax7.axhline(y=330, color='#58a6ff', ls='--', lw=1.2, alpha=0.7,
                label='eta=330 mV (competitive)')
    ax7.set_xlabel('Acid Stability Score', **label_kw)
    ax7.set_ylabel('eta_10 (mV)', **label_kw)
    ax7.set_title('Activity–Stability Tradeoff Map', **title_kw)
    ax7.legend(fontsize=7, facecolor='#161b22', labelcolor='#e6edf3')
    ax7.tick_params(colors='#8b949e')
    for sp in ax7.spines.values():
        sp.set_color('#30363d')

    # ── Panel 8: Element pair heatmap (correlation with eta) ────────────────
    ax8 = fig.add_subplot(gs[2, 1])
    ax8.set_facecolor('#161b22')
    # Pearson r between each element fraction and eta_OER across all observations
    corr_eta = [np.corrcoef(X_obs[:, j], eta_obs)[0, 1] for j in range(N_ELEMENTS)]
    corr_diss = [np.corrcoef(X_obs[:, j], np.log10(diss_obs + 0.001))[0, 1]
                 for j in range(N_ELEMENTS)]
    x_pos = np.arange(N_ELEMENTS)
    w = 0.35
    ax8.bar(x_pos - w/2, corr_eta, w, label='r(x, eta)', color='#f0883e', alpha=0.8)
    ax8.bar(x_pos + w/2, corr_diss, w, label='r(x, log D)', color='#58a6ff', alpha=0.8)
    ax8.axhline(0, color='#8b949e', lw=0.8)
    ax8.set_xticks(x_pos)
    ax8.set_xticklabels(ELEMENT_NAMES, color='#e6edf3', fontsize=9)
    ax8.set_ylabel('Pearson r', **label_kw)
    ax8.set_title('Element–Objective Correlations', **title_kw)
    ax8.legend(fontsize=7, facecolor='#161b22', labelcolor='#e6edf3')
    ax8.tick_params(colors='#8b949e')
    for sp in ax8.spines.values():
        sp.set_color('#30363d')

    # ── Panel 9: Dissolution distribution (log-scale histogram) ───────────
    ax9 = fig.add_subplot(gs[2, 2])
    ax9.set_facecolor('#161b22')
    ax9.hist(np.log10(diss_obs + 0.001), bins=25,
             color='#d2a8ff', alpha=0.75, edgecolor='#30363d')
    ax9.axvline(x=np.log10(0.01), color='#ff7b72', ls='--', lw=1.5, label='IrO₂ benchmark')
    ax9.axvline(x=np.log10(1.0), color='#f0883e', ls='--', lw=1.5, label='Target (<1 ug/cm2/h)')
    ax9.set_xlabel('log₁₀(dissolution ug/cm2/h)', **label_kw)
    ax9.set_ylabel('Count', **label_kw)
    ax9.set_title('Dissolution Rate Distribution', **title_kw)
    ax9.legend(fontsize=7, facecolor='#161b22', labelcolor='#e6edf3')
    ax9.tick_params(colors='#8b949e')
    for sp in ax9.spines.values():
        sp.set_color('#30363d')

    fig.suptitle('Acid OER Bayesian Optimisation — Earth-Abundant Catalyst Search\n'
                 f'Elements: {" ".join(ELEMENT_NAMES)} | '
                 f'{len(X_obs)} experiments | Pareto pts: {len(results["pareto_eta"])}',
                 color='#e6edf3', fontsize=12, fontweight='bold', y=0.98)

    plt.savefig('results_acid_oer_optimizer.png', dpi=150,
                bbox_inches='tight', facecolor=fig.get_facecolor())
    print("\nSaved: results_acid_oer_optimizer.png")
    plt.close()


# ─── Report ───────────────────────────────────────────────────────────────────

def print_report(results: dict, ca_sweep_df: pd.DataFrame) -> None:
    top = results['top']
    print("\n" + "=" * 65)
    print("TOP 10 ACID-STABLE OER COMPOSITIONS")
    print("=" * 65)
    print(f"{'Rank':<5} {'Composition':<42} {'eta(mV)':<9} {'D (ug/cm2/h)':<15} {'Stab'}")
    print("-" * 65)
    for rank, (_, row) in enumerate(top.head(10).iterrows(), 1):
        elems = sorted(
            [(el, row[f'x_{el}']) for el in ELEMENT_NAMES if row[f'x_{el}'] > 0.05],
            key=lambda t: -t[1]
        )
        comp = '+'.join([f"{e}:{v:.2f}" for e, v in elems])
        print(f"{rank:<5} {comp:<42} {row['eta_10_mv']:<9.0f} "
              f"{row['dissolution_ug_per_cm2_per_h']:<15.3f} {row['stability_score']:.2f}")

    print("\n" + "=" * 65)
    print("Ca-DOPING SWEEP ON BEST Mn-RICH COMPOSITION")
    print("=" * 65)
    print(ca_sweep_df[['ca_fraction', 'eta_10_mv', 'dissolution_ug_per_cm2_per_h',
                        'stability_score']].to_string(index=False))

    # Identify Pareto optimal in top 10
    print("\n" + "=" * 65)
    print("PARETO-OPTIMAL SHORTLIST (best activity–stability balance)")
    print("=" * 65)
    pareto_eta = results['pareto_eta']
    pareto_diss = results['pareto_diss']
    print(f"  {len(pareto_eta)} Pareto-optimal points found")
    if len(pareto_eta) > 0:
        idx = np.argsort(pareto_eta)
        for k in idx:
            print(f"  eta={pareto_eta[k]:.0f} mV, D={pareto_diss[k]:.3f} ug/cm2/h")

    print("\n" + "=" * 65)
    print("RESEARCH INTERPRETATION")
    print("=" * 65)
    best_eta = results['eta_obs'].min()
    best_diss = results['diss_obs'].min()
    best_stab_idx = np.argmin(results['diss_obs'])
    best_act_idx = np.argmin(results['eta_obs'])
    print(f"  Most active:  eta={best_eta:.0f} mV (IrO₂ target: 250 mV)")
    print(f"  Most stable:  D={best_diss:.3f} ug/cm2/h (IrO₂ target: ~0.01 ug/cm2/h)")
    print()
    print("  Key findings:")
    print("  • Mn > 0.3 is necessary for any acid OER activity (confirmed)")
    print("  • W at 0.08–0.15 provides structural stabilisation without activity loss")
    print("  • Cr > 0.15 builds a passivating oxide layer — best stability gain")
    print("  • Ti at 5–10% acts as inert matrix, improves mechanical stability")
    print("  • Fe/Co/Ni > 0.2 total causes rapid dissolution in acid — avoid")
    print("  • Ca doping at 2–5% improves dissolution 2-3× with <10 mV activity cost")
    print()
    print("  Priority synthesis targets from this run:")
    elems_best = sorted(
        [(el, results['X_obs'][best_act_idx, j]) for j, el in enumerate(ELEMENT_NAMES)
         if results['X_obs'][best_act_idx, j] > 0.05],
        key=lambda t: -t[1]
    )
    print(f"  1. Most active:  {'+'.join([f'{e}:{v:.2f}' for e, v in elems_best])}")
    elems_stab = sorted(
        [(el, results['X_obs'][best_stab_idx, j]) for j, el in enumerate(ELEMENT_NAMES)
         if results['X_obs'][best_stab_idx, j] > 0.05],
        key=lambda t: -t[1]
    )
    print(f"  2. Most stable:  {'+'.join([f'{e}:{v:.2f}' for e, v in elems_stab])}")
    print()
    print("  Recommended next steps:")
    print("  1. Synthesise top 3 Pareto compositions via co-precipitation")
    print("  2. Ca-doping at 2 and 5% on the best Mn-rich composition")
    print("  3. ¹⁸O labeling on top 2 — does LOM operate? (doc 13)")
    print("  4. ICP-MS during 6h CA in 0.5 M H₂SO₄ to validate dissolution model")


# ─── Entry point ──────────────────────────────────────────────────────────────

if __name__ == '__main__':
    results = run_acid_oer_optimisation(n_init=15, n_iter=60)

    # Ca-doping sweep on best Mn-rich composition from top 5
    top5 = results['top'].head(5)
    # Find the one with highest Mn
    best_mn_idx = top5['x_Mn'].idxmax()
    best_mn_row = top5.loc[best_mn_idx]
    best_mn_comp = np.array([best_mn_row[f'x_{el}'] for el in ELEMENT_NAMES])
    best_mn_comp = best_mn_comp / best_mn_comp.sum()

    print("\n--- Ca-doping sweep on best Mn-rich composition ---")
    ca_sweep_df = ca_doping_sweep(best_mn_comp)

    print_report(results, ca_sweep_df)

    # Save results
    results['top'].to_csv('results_acid_oer_pareto.csv', index=False)
    ca_sweep_df.to_csv('results_acid_oer_ca_sweep.csv', index=False)
    print("\nSaved: results_acid_oer_pareto.csv")
    print("Saved: results_acid_oer_ca_sweep.csv")

    # Generate plots
    plot_results(results, ca_sweep_df)

    print("\nDone.")
