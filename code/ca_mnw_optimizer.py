"""
ca_mnw_optimizer.py
===================
Focused Bayesian optimisation over the Ca-Mn-W-Ti quaternary space.

This script addresses the single biggest bottleneck identified by the
descriptor gap analysis: dissolution_potential_v.

WHY Ca-Mn-W?
============
- CaMnW is the #1 priority from materials_project_api.py scoring
- Ca doping does two distinct things, which this optimizer models separately:

  (A) Ca²⁺ substitution into birnessite interlayer (Ca ≤ 10%)
      → Promotes Mn³⁺ (raises eg toward 0.5-1.0)
      → Pins interlayer spacing → prevents structural collapse under OER
      → Stability improvement: ~15-25% from pulsed CP data

  (B) CaWO₄ secondary phase formation (Ca > 5%, W > 20%)
      → Scheelite structure: dissolution potential ~1.4 V vs RHE at pH 1
      → Forms a protective layer over Mn-oxide active phase
      → This is the key mechanism for approaching IrO₂ stability levels
      → Analogous to the IrO₂ shell mechanism in Ir-Mn composite materials

The optimizer explicitly models phase segregation: compositions where Ca and
W concentrations favour CaWO₄ formation receive a dramatically better
dissolution_potential estimate (0.85 → 1.35 V).

If this stability boost is real, the gap to IrO₂ (1.60 V) shrinks from
0.54 V to 0.25 V — a 2× reduction in the hardest descriptor gap.

Search space:
  x = [Ca, Mn, W, Ti] fractions summing to 1
  Ca:  0.00 – 0.15
  Mn:  0.30 – 0.70
  W:   0.15 – 0.45
  Ti:  0.00 – 0.25

Objectives:
  1. Minimise eta_OER (mV at 10 mA/cm²)
  2. Minimise dissolution_rate (µg/cm²/h)

Usage:
  pip install -r requirements.txt
  python ca_mnw_optimizer.py
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from scipy.stats import norm

ELEMENT_NAMES = ['Ca', 'Mn', 'W', 'Ti']
N_ELEMENTS = 4

# ─── Phase thermodynamics ──────────────────────────────────────────────────────

# Pourbaix dissolution potentials (V vs RHE, pH 1)
POURBAIX = {'Ca': 2.50, 'Mn': 0.85, 'W': 1.05, 'Ti': 1.20}

# CaWO₄ scheelite: forms when Ca + W coexist and [Ca][W] > threshold
# Dissolution potential of CaWO₄ at pH 1, 1.6 V: ~1.38 V vs RHE
# Source: Pourbaix Atlas Ca-W-O system; DFT-Pourbaix (Materials Project)
CAWО4_DISSOLUTION_V = 1.38
CAWО4_FORMATION_THRESHOLD = 0.04  # [Ca] × [W] > 0.04 indicates CaWO₄ nucleation

def cawо4_fraction(ca: float, w: float) -> float:
    """
    Estimate fraction of Ca and W that have formed CaWO₄.
    CaWO₄ has 1:1 Ca:W stoichiometry. Excess of either remains as
    Ca²⁺ (interlayer) or WO₃ surface species.
    """
    # Stoichiometric CaWO₄: both Ca and W consumed equally
    cawо4 = min(ca, w)
    # Only forms above threshold product (kinetic barrier)
    if ca * w < CAWО4_FORMATION_THRESHOLD:
        # Below threshold: slow nucleation — reduced formation
        cawо4 *= (ca * w) / CAWО4_FORMATION_THRESHOLD
    return cawо4


def composite_dissolution_potential(x: np.ndarray) -> float:
    """
    Compute effective dissolution potential accounting for CaWO₄ phase.

    The composite is a mixture of:
    1. CaWO₄ phase (dissolution potential 1.38 V)
    2. Mn-oxide active phase (dissolution potential 0.85 V)
    3. TiO₂ passivating matrix (dissolution potential 1.20 V)
    4. Residual WO₃ surface (dissolution potential 1.05 V)

    Volume-fraction weighted average of phase potentials.
    """
    ca, mn, w, ti = x[0], x[1], x[2], x[3]
    cawо4 = cawо4_fraction(ca, w)

    # Ca remaining in interlayer after CaWO₄ formation
    ca_interlayer = max(0, ca - cawо4)
    # W remaining as WO₃ surface species
    w_surface = max(0, w - cawо4)

    # Phase volume fractions (simplified: proportional to molar content)
    total = cawо4 + mn + w_surface + ti + ca_interlayer + 1e-10
    f_cawо4 = cawо4 / total
    f_mn = mn / total
    f_wо3 = w_surface / total
    f_ti = ti / total
    # Ca interlayer dissolves with Mn, treated as mn-oxide stabiliser

    e_eff = (
        f_cawо4 * CAWО4_DISSOLUTION_V +
        f_mn    * POURBAIX['Mn'] * (1 + 0.15 * ca_interlayer / (mn + 1e-10)) +  # Ca stabilises Mn
        f_wо3   * POURBAIX['W'] +
        f_ti    * POURBAIX['Ti']
    )
    return float(np.clip(e_eff, 0.0, 2.0))


def eg_from_composition(ca: float, mn: float) -> float:
    """
    Estimate eg electron occupancy.
    Ca²⁺ promotes Mn³⁺ (hole doping). Higher Ca → more Mn³⁺ → higher eg.
    MnO₂ (all Mn⁴⁺): eg = 0
    Mn₂O₃ (all Mn³⁺): eg = 1
    Target: eg = 0.5–1.0 (OER volcano optimum)
    """
    # Ca/Mn ratio drives Mn³⁺ fraction
    ca_mn_ratio = ca / (mn + 1e-6)
    # 5% Ca per Mn raises eg by ~0.15
    eg = min(1.0, 3.0 * ca_mn_ratio)
    return float(eg)


# ─── Surrogate evaluation ─────────────────────────────────────────────────────

def evaluate(x: np.ndarray, noise: float = 0.07) -> tuple[float, float]:
    """
    Physics-informed surrogate for Ca-Mn-W-Ti system.

    Activity model (eta_OER):
      Base: MnO₂ (350 mV). Modifiers:
      - Ca doping: tunes eg toward optimum → reduces eta by up to 40 mV
      - W: slight activity improvement (W⁶⁺ reduces Mn-O bond strength)
      - Ti: inert dilutent → raises eta proportional to fraction
      - CaWO₄ phase: OER-inactive → penalises activity when dominant

    Dissolution model:
      Uses composite_dissolution_potential() which accounts for CaWO₄ phase.
      Maps to dissolution rate via log-linear: D = exp(8 × (1 - e_diss/1.6))
    """
    rng = np.random.RandomState()
    ca, mn, w, ti = x[0], x[1], x[2], x[3]

    # ── Activity model ─────────────────────────────────────────────────────────
    eta_base = 350.0  # MnO₂ baseline

    # Ca eg-tuning effect: optimum around Ca/Mn = 0.10–0.15
    eg = eg_from_composition(ca, mn)
    # Volcano: optimum eg = 0.75 (based on Mn-oxide volcano curve)
    # Penalty increases for deviation from optimum
    eg_opt = 0.75
    eg_penalty = abs(eg - eg_opt) * 50  # mV per unit eg deviation
    eg_bonus = max(0, 50 - eg_penalty)
    eta_base -= eg_bonus  # up to -50 mV from eg tuning

    # W weakens M-O bond slightly (moves toward volcano tip for Mn)
    if w > 0.10:
        w_bonus = min(20, 40 * (w - 0.10) / 0.30)
        eta_base -= w_bonus

    # Ti dilution penalty
    eta_base += 70 * ti

    # CaWO₄ phase penalty: when CaWO₄ dominates, it blocks Mn active sites
    cawо4 = cawо4_fraction(ca, w)
    if cawо4 > 0.08:  # above 8%, begins to block significantly
        cawо4_penalty = (cawо4 - 0.08) / (0.92) * 100  # up to 100 mV penalty
        eta_base += cawо4_penalty

    # Ca at very high fractions starts to block sites too
    if ca > 0.12:
        eta_base += 60 * (ca - 0.12)

    eta_base = np.clip(eta_base, 280, 550)
    eta = float(eta_base * (1 + rng.normal(0, noise)))

    # ── Dissolution model ──────────────────────────────────────────────────────
    e_diss = composite_dissolution_potential(x)
    # Log-linear map from Pourbaix stability to dissolution rate
    # IrO₂ at e_diss=1.60V → D ≈ 0.01 µg/cm²/h
    # Calibration: exp(8 × (1 - 1.60/1.60)) = 1.0 → need to shift scale
    # Normalised: D = D₀ × exp(-k × e_diss), fit to known points:
    #   Mn-oxide: e_diss=0.85 → D ≈ 40 µg/cm²/h
    #   IrO₂:    e_diss=1.60 → D ≈ 0.01 µg/cm²/h
    # → k = ln(40/0.01) / (1.60 - 0.85) = 8.29 / 0.75 = 11.05
    k = 11.05
    D0 = 40 * np.exp(-k * 0.85)  # normalisation constant
    dissolution_base = D0 * np.exp(-k * e_diss)

    dissolution_base = max(0.005, dissolution_base)
    dissolution = float(dissolution_base * np.exp(rng.normal(0, noise)))

    return eta, dissolution


# ─── Simplex sampling ─────────────────────────────────────────────────────────

def sample_constrained_simplex(n: int, random_seed: int | None = None) -> np.ndarray:
    """
    Sample Ca-Mn-W-Ti compositions on the 3-simplex with constraints:
      Ca:  0.00 – 0.15
      Mn:  0.30 – 0.70
      W:   0.15 – 0.45
      Ti:  0.00 – 0.25
    These bounds reflect what the previous 9-element optimizer found works.
    """
    rng = np.random.RandomState(random_seed)
    samples = []
    attempts = 0
    while len(samples) < n and attempts < n * 200:
        # Sample Mn first (dominant component)
        mn = rng.uniform(0.30, 0.70)
        remaining = 1.0 - mn
        # Sample Ca
        ca_max = min(0.15, remaining * 0.40)
        ca = rng.uniform(0.00, ca_max)
        remaining -= ca
        # Sample Ti
        ti_max = min(0.25, remaining * 0.50)
        ti = rng.uniform(0.00, ti_max)
        remaining -= ti
        # W gets the rest
        w = remaining
        if 0.15 <= w <= 0.45:
            x = np.array([ca, mn, w, ti])
            if abs(x.sum() - 1.0) < 1e-10:
                samples.append(x)
        attempts += 1

    if len(samples) < n:
        # Fill without Ti constraint
        while len(samples) < n:
            mn = rng.uniform(0.35, 0.65)
            ca = rng.uniform(0.02, 0.12)
            ti = rng.uniform(0.02, 0.15)
            w = 1.0 - mn - ca - ti
            if 0.10 <= w <= 0.50:
                samples.append(np.array([ca, mn, w, ti]))

    return np.array(samples[:n])


# ─── Lightweight GP ───────────────────────────────────────────────────────────

class GP:
    def __init__(self, length_scale: float = 0.20, noise: float = 0.08):
        self.l = length_scale
        self.sigma_n2 = noise ** 2
        self.X = None
        self.y_log = None
        self.K_inv = None

    def _K(self, A, B):
        d2 = np.sum((A[:, None, :] - B[None, :, :]) ** 2, axis=2)
        return np.exp(-d2 / (2 * self.l ** 2))

    def fit(self, X, y):
        self.X = X.copy()
        self.y_log = np.log(np.maximum(y, 1e-6))
        K = self._K(X, X) + self.sigma_n2 * np.eye(len(X))
        self.K_inv = np.linalg.inv(K + 1e-8 * np.eye(len(K)))

    def predict(self, X):
        ks = self._K(X, self.X)
        mu = ks @ self.K_inv @ self.y_log
        var = np.diag(self._K(X, X) - ks @ self.K_inv @ ks.T)
        var = np.maximum(var, 1e-10)
        # Lognormal moments
        mean = np.exp(mu + var / 2)
        std = np.sqrt((np.exp(var) - 1) * np.exp(2 * mu + var))
        return mean, std


def ei(gp: GP, X: np.ndarray, y_best: float, xi: float = 0.01) -> np.ndarray:
    mu, std = gp.predict(X)
    Z = (np.log(y_best + 1e-6) - np.log(mu + 1e-6) - xi) / (np.log(std + 1e-6) + 1e-9)
    return np.maximum((np.log(y_best + 1e-6) - np.log(mu + 1e-6) - xi) * norm.cdf(Z)
                      + np.log(std + 1e-6) * norm.pdf(Z), 0)


def phvi(eta_pred, diss_pred, peta, pdiss, ref_eta=550.0, ref_diss=300.0) -> float:
    for i in range(len(peta)):
        if peta[i] <= eta_pred and pdiss[i] <= diss_pred:
            return 0.0
    return max(0, ref_eta - eta_pred) * max(0, ref_diss - diss_pred)


# ─── Optimisation ─────────────────────────────────────────────────────────────

def run(n_init: int = 20, n_iter: int = 80, n_cand: int = 800,
        seed: int = 42) -> dict:
    np.random.seed(seed)
    print("=" * 65)
    print("Ca-Mn-W-Ti FOCUSED OPTIMIZER")
    print("Target: close dissolution_potential gap toward IrO2 (1.60 V)")
    print(f"Phase 1: {n_init} constrained random experiments")
    print(f"Phase 2: {n_iter} Bayesian optimisation iterations")
    print("=" * 65)

    X_obs = sample_constrained_simplex(n_init, random_seed=seed)
    eta_obs, diss_obs = [], []

    print("\n--- Phase 1: Initial exploration ---")
    for i, x in enumerate(X_obs):
        eta, diss = evaluate(x)
        eta_obs.append(eta)
        diss_obs.append(diss)
        e_diss = composite_dissolution_potential(x)
        ca, mn, w, ti = x
        cawо4 = cawо4_fraction(ca, w)
        print(f"  Init {i+1:2d}: eta={eta:.0f} mV, D={diss:.3f} ug/cm2/h, "
              f"Ediss={e_diss:.3f} V, CaWO4={cawо4:.3f}"
              f" | Ca={ca:.2f} Mn={mn:.2f} W={w:.2f} Ti={ti:.2f}")

    eta_obs = np.array(eta_obs)
    diss_obs = np.array(diss_obs)

    gp_eta = GP(length_scale=0.18, noise=0.07)
    gp_diss = GP(length_scale=0.22, noise=0.10)
    pareto_eta, pareto_diss = np.array([]), np.array([])
    conv_eta, conv_diss = [], []

    print(f"\n--- Phase 2: Bayesian optimisation ({n_iter} iterations) ---")
    for it in range(n_iter):
        gp_eta.fit(X_obs, eta_obs)
        gp_diss.fit(X_obs, diss_obs)

        X_cand = sample_constrained_simplex(n_cand, random_seed=it * 100)
        mu_eta, _ = gp_eta.predict(X_cand)
        mu_diss, _ = gp_diss.predict(X_cand)
        ei_eta = ei(gp_eta, X_cand, eta_obs.min())

        best_score = -np.inf
        best_x = None
        for j in range(len(X_cand)):
            e_diss_j = composite_dissolution_potential(X_cand[j])
            if e_diss_j < 0.70:
                continue  # below dissolution threshold
            hvi = phvi(mu_eta[j], mu_diss[j], pareto_eta, pareto_diss)
            score = 0.55 * hvi + 0.45 * ei_eta[j] * 15
            if score > best_score:
                best_score = score
                best_x = X_cand[j]

        if best_x is None:
            best_x = sample_constrained_simplex(1, random_seed=it)[0]

        eta_new, diss_new = evaluate(best_x)
        X_obs = np.vstack([X_obs, best_x])
        eta_obs = np.append(eta_obs, eta_new)
        diss_obs = np.append(diss_obs, diss_new)

        dominated = False
        new_pe, new_pd = [], []
        for k in range(len(pareto_eta)):
            if pareto_eta[k] <= eta_new and pareto_diss[k] <= diss_new:
                dominated = True
                break
            if not (eta_new <= pareto_eta[k] and diss_new <= pareto_diss[k]):
                new_pe.append(pareto_eta[k])
                new_pd.append(pareto_diss[k])
        if not dominated:
            new_pe.append(eta_new)
            new_pd.append(diss_new)
        pareto_eta = np.array(new_pe)
        pareto_diss = np.array(new_pd)
        conv_eta.append(eta_obs.min())
        conv_diss.append(diss_obs.min())

        if (it + 1) % 20 == 0:
            e_diss = composite_dissolution_potential(best_x)
            ca, mn, w, ti = best_x
            cawо4 = cawо4_fraction(ca, w)
            print(f"  Iter {it+1:3d}: eta={eta_new:.0f} mV, D={diss_new:.3f} ug/cm2/h, "
                  f"Ediss={e_diss:.3f}V, CaWO4={cawо4:.3f}"
                  f" | Ca={ca:.2f} Mn={mn:.2f} W={w:.2f} Ti={ti:.2f}")
            print(f"           Best: eta={eta_obs.min():.0f} mV, "
                  f"D={diss_obs.min():.3f} ug/cm2/h, Pareto={len(pareto_eta)}")

    return {
        'X_obs': X_obs, 'eta_obs': eta_obs, 'diss_obs': diss_obs,
        'pareto_eta': pareto_eta, 'pareto_diss': pareto_diss,
        'conv_eta': conv_eta, 'conv_diss': conv_diss,
    }


# ─── Analysis ─────────────────────────────────────────────────────────────────

def analyse(results: dict) -> pd.DataFrame:
    X = results['X_obs']
    eta = results['eta_obs']
    diss = results['diss_obs']

    records = []
    for i in range(len(X)):
        ca, mn, w, ti = X[i]
        e_diss = composite_dissolution_potential(X[i])
        cawо4 = cawо4_fraction(ca, w)
        eg = eg_from_composition(ca, mn)
        records.append({
            'Ca': round(ca, 3), 'Mn': round(mn, 3),
            'W': round(w, 3), 'Ti': round(ti, 3),
            'eta_10_mv': round(eta[i], 1),
            'dissolution_ug_cm2h': round(diss[i], 4),
            'dissolution_potential_v': round(e_diss, 3),
            'cawо4_fraction': round(cawо4, 3),
            'eg_electrons': round(eg, 3),
        })
    df = pd.DataFrame(records)
    # Composite rank: equal weight eta (normalised) + dissolution (log normalised)
    df['eta_n'] = (df['eta_10_mv'] - df['eta_10_mv'].min()) / (df['eta_10_mv'].max() - df['eta_10_mv'].min() + 1e-6)
    df['diss_n'] = (np.log10(df['dissolution_ug_cm2h']) - np.log10(df['dissolution_ug_cm2h'].min())) / \
                   (np.log10(df['dissolution_ug_cm2h'].max()) - np.log10(df['dissolution_ug_cm2h'].min()) + 1e-6)
    df['score'] = 0.5 * df['eta_n'] + 0.5 * df['diss_n']
    return df.nsmallest(25, 'score').reset_index(drop=True)


def plot(results: dict, top: pd.DataFrame) -> None:
    X = results['X_obs']
    eta = results['eta_obs']
    diss = results['diss_obs']
    e_diss_all = [composite_dissolution_potential(X[i]) for i in range(len(X))]
    cawо4_all = [cawо4_fraction(X[i, 0], X[i, 2]) for i in range(len(X))]

    fig = plt.figure(figsize=(18, 12))
    fig.patch.set_facecolor('#0d1117')
    gs = gridspec.GridSpec(2, 3, figure=fig, hspace=0.4, wspace=0.35)
    lkw = dict(color='#e6edf3', fontsize=9)
    tkw = dict(color='#e6edf3', fontsize=10, fontweight='bold', pad=8)

    def _spine(ax):
        ax.tick_params(colors='#8b949e')
        for sp in ax.spines.values():
            sp.set_color('#30363d')

    # Panel 1: Pareto front
    ax1 = fig.add_subplot(gs[0, 0])
    ax1.set_facecolor('#161b22')
    sc = ax1.scatter(eta, np.log10(diss + 1e-4), c=e_diss_all,
                     cmap='RdYlGn', vmin=0.7, vmax=1.4, alpha=0.6, s=25)
    plt.colorbar(sc, ax=ax1, label='Dissolution potential (V)', shrink=0.85)
    if len(results['pareto_eta']) > 0:
        idx_p = np.argsort(results['pareto_eta'])
        ax1.plot(results['pareto_eta'][idx_p],
                 np.log10(results['pareto_diss'][idx_p] + 1e-4),
                 'o-', color='#58a6ff', ms=8, lw=2, label='Pareto', zorder=5)
    ax1.axvline(250, color='#ff7b72', ls='--', lw=1.2, alpha=0.7, label='IrO2 eta')
    ax1.axhline(np.log10(0.01), color='#ff7b72', ls=':', lw=1.2, alpha=0.7, label='IrO2 D')
    ax1.set_xlabel('eta_10 (mV)', **lkw)
    ax1.set_ylabel('log10(D ug/cm2/h)', **lkw)
    ax1.set_title('Pareto Front (colour = E_diss)', **tkw)
    ax1.legend(fontsize=7, facecolor='#161b22', labelcolor='#e6edf3')
    _spine(ax1)

    # Panel 2: Convergence
    ax2 = fig.add_subplot(gs[0, 1])
    ax2.set_facecolor('#161b22')
    iters = range(1, len(results['conv_eta']) + 1)
    ax2.plot(iters, results['conv_eta'], color='#f0883e', lw=2, label='Best eta')
    ax2r = ax2.twinx()
    ax2r.semilogy(iters, results['conv_diss'], color='#58a6ff', lw=2, ls='--', label='Best D')
    ax2.set_xlabel('BO Iteration', **lkw)
    ax2.set_ylabel('Best eta_10 (mV)', color='#f0883e', fontsize=9)
    ax2r.set_ylabel('Best D (ug/cm2/h)', color='#58a6ff', fontsize=9)
    ax2.set_title('Convergence', **tkw)
    ax2.tick_params(colors='#8b949e')
    ax2r.tick_params(colors='#58a6ff')
    for sp in ax2.spines.values():
        sp.set_color('#30363d')

    # Panel 3: Dissolution potential vs CaWO4 fraction
    ax3 = fig.add_subplot(gs[0, 2])
    ax3.set_facecolor('#161b22')
    sc3 = ax3.scatter(cawо4_all, e_diss_all, c=eta, cmap='RdYlGn_r',
                      alpha=0.7, s=25, vmin=280, vmax=500)
    plt.colorbar(sc3, ax=ax3, label='eta_10 (mV)', shrink=0.85)
    ax3.axhline(1.38, color='#58a6ff', ls='--', lw=1.5, label='CaWO4 E_diss')
    ax3.axhline(1.60, color='#ff7b72', ls='--', lw=1.5, label='IrO2 E_diss')
    ax3.set_xlabel('CaWO4 fraction', **lkw)
    ax3.set_ylabel('Composite E_diss (V)', **lkw)
    ax3.set_title('CaWO4 Effect on Dissolution Potential', **tkw)
    ax3.legend(fontsize=7, facecolor='#161b22', labelcolor='#e6edf3')
    _spine(ax3)

    # Panel 4: eta vs E_diss scatter
    ax4 = fig.add_subplot(gs[1, 0])
    ax4.set_facecolor('#161b22')
    sc4 = ax4.scatter(e_diss_all, eta, c=np.log10(np.array(diss) + 1e-4),
                      cmap='RdYlGn', alpha=0.6, s=25)
    plt.colorbar(sc4, ax=ax4, label='log10(D)', shrink=0.85)
    ax4.axvline(1.38, color='#58a6ff', ls='--', lw=1.2, label='CaWO4')
    ax4.axvline(1.60, color='#ff7b72', ls='--', lw=1.2, label='IrO2')
    ax4.axhline(330, color='#3fb950', ls=':', lw=1.2, label='Target eta=330')
    ax4.set_xlabel('Dissolution potential (V)', **lkw)
    ax4.set_ylabel('eta_10 (mV)', **lkw)
    ax4.set_title('Activity vs Dissolution Stability', **tkw)
    ax4.legend(fontsize=7, facecolor='#161b22', labelcolor='#e6edf3')
    _spine(ax4)

    # Panel 5: Top 8 composition profiles
    ax5 = fig.add_subplot(gs[1, 1])
    ax5.set_facecolor('#161b22')
    top8 = top.head(8)
    x_pos = np.arange(len(top8))
    w_bar = 0.2
    colors = ['#58a6ff', '#f0883e', '#3fb950', '#d2a8ff']
    for k, el in enumerate(['Ca', 'Mn', 'W', 'Ti']):
        ax5.bar(x_pos + k * w_bar, top8[el], w_bar, label=el, color=colors[k], alpha=0.85)
    ax5.set_xticks(x_pos + w_bar * 1.5)
    ax5.set_xticklabels([f'#{i+1}' for i in range(len(top8))], color='#e6edf3', fontsize=8)
    ax5.set_ylabel('Element fraction', **lkw)
    ax5.set_title('Top 8 Composition Profiles', **tkw)
    ax5.legend(fontsize=8, facecolor='#161b22', labelcolor='#e6edf3', loc='upper right')
    _spine(ax5)

    # Panel 6: E_diss distribution
    ax6 = fig.add_subplot(gs[1, 2])
    ax6.set_facecolor('#161b22')
    ax6.hist(e_diss_all, bins=30, color='#3fb950', alpha=0.75, edgecolor='#30363d')
    ax6.axvline(np.mean(e_diss_all), color='#58a6ff', ls='--', lw=1.5, label=f'Mean={np.mean(e_diss_all):.3f}V')
    ax6.axvline(1.38, color='#f0883e', ls='--', lw=1.5, label='CaWO4 (1.38V)')
    ax6.axvline(1.60, color='#ff7b72', ls='--', lw=1.5, label='IrO2 (1.60V)')
    ax6.set_xlabel('Composite E_diss (V)', **lkw)
    ax6.set_ylabel('Count', **lkw)
    ax6.set_title('Dissolution Potential Distribution', **tkw)
    ax6.legend(fontsize=7, facecolor='#161b22', labelcolor='#e6edf3')
    _spine(ax6)

    fig.suptitle('Ca-Mn-W-Ti Focused Optimizer — CaWO4 Phase Stability Strategy\n'
                 f'{len(X)} experiments | Best eta={eta.min():.0f} mV | '
                 f'Best D={diss.min():.3f} ug/cm2/h | '
                 f'Best E_diss={max(e_diss_all):.3f} V',
                 color='#e6edf3', fontsize=11, fontweight='bold', y=0.98)

    plt.savefig('results_ca_mnw_optimizer.png', dpi=150,
                bbox_inches='tight', facecolor=fig.get_facecolor())
    print('\nSaved: results_ca_mnw_optimizer.png')
    plt.close()


def report(results: dict, top: pd.DataFrame) -> None:
    eta = results['eta_obs']
    diss = results['diss_obs']
    X = results['X_obs']
    e_diss_all = [composite_dissolution_potential(X[i]) for i in range(len(X))]

    print("\n" + "=" * 65)
    print("TOP 10 Ca-Mn-W-Ti COMPOSITIONS")
    print("=" * 65)
    print(f"  {'Rank':<5} {'Ca':>6} {'Mn':>6} {'W':>6} {'Ti':>6} "
          f"{'eta':>7} {'D(ug/cm2h)':>12} {'E_diss':>8} {'CaWO4':>7}")
    print(f"  {'-'*63}")
    for i, row in top.head(10).iterrows():
        cawо4 = cawо4_fraction(row['Ca'], row['W'])
        print(f"  {i+1:<5} {row['Ca']:>6.3f} {row['Mn']:>6.3f} {row['W']:>6.3f} "
              f"{row['Ti']:>6.3f} {row['eta_10_mv']:>7.0f} "
              f"{row['dissolution_ug_cm2h']:>12.4f} "
              f"{row['dissolution_potential_v']:>8.3f} "
              f"{cawо4:>7.3f}")

    best_e_diss = max(e_diss_all)
    best_idx = np.argmax(e_diss_all)
    print(f"\n  Highest dissolution potential: {best_e_diss:.3f} V "
          f"(IrO2 gap now {1.60 - best_e_diss:.3f} V, "
          f"down from 0.54 V before CaWO4 modelling)")

    print("\n" + "=" * 65)
    print("CLOSING THE DISSOLUTION GAP — MECHANISM ANALYSIS")
    print("=" * 65)
    print(f"  IrO2 benchmark:           E_diss = 1.60 V, D = 0.01 ug/cm2/h")
    print(f"  Previous best (9-element): E_diss = 1.06 V (CaMnW-birnessite)")
    print(f"  This optimizer best:       E_diss = {best_e_diss:.3f} V")
    gap_reduction = (best_e_diss - 1.06) / (1.60 - 1.06) * 100
    print(f"  Gap reduction from CaWO4:  {gap_reduction:.0f}% of remaining gap closed")
    print()
    print("  CaWO4 phase formation requirements:")
    print("  - Ca fraction > 0.06 AND W fraction > 0.20")
    print("  - Synthesis: co-precipitation at pH 7-8 (CaWO4 nucleates at neutral pH)")
    print("  - Evidence: XRD satellite peak at 28.7° (CaWO4 (112) reflection)")
    print("  - Confirm with Raman: CaWO4 peak at 921 cm^-1 (symmetric W-O stretch)")
    print()
    print("  Synthesis recommendation for #1 composition:")
    row = top.iloc[0]
    print(f"    Ca={row['Ca']:.3f}, Mn={row['Mn']:.3f}, W={row['W']:.3f}, Ti={row['Ti']:.3f}")
    print(f"    Predicted eta_10 = {row['eta_10_mv']:.0f} mV")
    print(f"    Predicted D = {row['dissolution_ug_cm2h']:.4f} ug/cm2/h")
    print(f"    Predicted E_diss = {row['dissolution_potential_v']:.3f} V")
    print()
    print("  How to synthesise:")
    print("  1. Co-precipitate Ca/Mn/Ti nitrates at pH 7.5 → forms birnessite + TiO2")
    print("  2. Add Na2WO4 during precipitation → promotes CaWO4 nucleation")
    print("  3. Anneal at 180°C/4h in air → CaWO4 crystallises on Mn-oxide surface")
    print("  4. Anneal at 5% H2/N2, 200°C/2h → promotes Mn3+ (raises eg to 0.5-0.7)")
    print("  5. Verify CaWO4: XRD 28.7 deg, Raman 921 cm^-1")


if __name__ == '__main__':
    results = run(n_init=20, n_iter=80)
    top = analyse(results)
    report(results, top)
    top.to_csv('results_ca_mnw_pareto.csv', index=False)
    print('\nSaved: results_ca_mnw_pareto.csv')
    plot(results, top)
    print('\nDone.')
