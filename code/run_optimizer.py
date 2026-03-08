"""
Fast runner for Bayesian HEO optimizer.
Reduces multi-start restarts and iterations for quick results.
For production: increase N_RESTARTS=20, N_ITERATIONS=100+
"""

import sys
import os
sys.stdout.reconfigure(encoding='utf-8')

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend for file output
import matplotlib.pyplot as plt
from scipy.stats import norm
from scipy.optimize import minimize
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import Matern, ConstantKernel, WhiteKernel
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')

np.random.seed(42)

# --- Configuration ---
N_INITIAL    = 15   # random seed experiments
N_ITERATIONS = 50   # BO iterations
N_RESTARTS   = 5    # multi-start optimizer restarts per iteration

ELEMENTS = {
    'Fe': {'dissolution_v': 0.30, 'activity': 0.85, 'cost': 0.10},
    'Co': {'dissolution_v': 0.35, 'activity': 0.80, 'cost': 33.0},
    'Ni': {'dissolution_v': 0.10, 'activity': 0.60, 'cost': 13.0},
    'Cr': {'dissolution_v': 1.20, 'activity': 0.05, 'cost': 9.5},
    'Mn': {'dissolution_v': 1.10, 'activity': 0.50, 'cost': 1.75},
    'V':  {'dissolution_v': 0.80, 'activity': 0.40, 'cost': 30.0},
    'W':  {'dissolution_v': 0.90, 'activity': 0.35, 'cost': 35.0},
    'Mo': {'dissolution_v': 0.80, 'activity': 0.40, 'cost': 20.0},
}
NAMES = list(ELEMENTS.keys())
N = len(NAMES)

# --- Physics-inspired surrogate objectives ---

def predict_eta10(x):
    fe, co, ni, cr, mn, v, w, mo = x
    active = 0.8*fe + 0.75*co + 0.5*ni + 0.45*mn + 0.35*v + 0.30*w + 0.35*mo
    cr_penalty  = cr * 200
    synergy_feco = -40 * (fe * co) / 0.0625
    v_bonus     = -20 * v * (fe + co)
    n_active    = sum(1 for val in [fe,co,ni,mn,v,w,mo] if val > 0.05)
    entropy_b   = -5 * n_active if n_active > 3 else 0
    eta = 380 - active*120 + cr_penalty + synergy_feco + v_bonus + entropy_b
    eta += np.random.normal(0, 6)
    return float(np.clip(eta, 200, 620))

def predict_diss(x):
    fe, co, ni, cr, mn, v, w, mo = x
    unstable = 5.0*fe + 4.5*co + 6.0*ni
    cr_prot  = (np.exp(-8*(cr-0.15)) if cr > 0.15
                else 0.5+0.5*(cr/0.15) if cr > 0.08
                else 1.0)
    mn_prot  = 1.0 - 0.3*mn
    wmo_prot = 1.0 - 0.25*(w+mo)
    rate = unstable * cr_prot * mn_prot * wmo_prot
    rate += np.random.normal(0, rate*0.12)
    return float(np.clip(rate, 0.01, 20))

def evaluate(x):
    x = np.clip(x, 0, 1)
    x = x / (x.sum() + 1e-12)
    return predict_eta10(x), predict_diss(x)

# --- Pareto utilities ---

def pareto_mask(costs):
    """Return boolean mask of non-dominated rows (2D costs, both minimise)."""
    n = len(costs)
    mask = np.ones(n, bool)
    for i in range(n):
        if not mask[i]: continue
        dominated = (np.all(costs <= costs[i], axis=1) &
                     np.any(costs <  costs[i], axis=1))
        dominated[i] = False
        mask[i] = not dominated.any()
    return mask

def hv2d(front, ref):
    """2-D hypervolume dominated by front wrt ref (both minimise)."""
    f = front[(front[:,0] < ref[0]) & (front[:,1] < ref[1])]
    if len(f) == 0: return 0.0
    f = f[np.argsort(f[:,0])]
    hv, prev_x = 0.0, ref[0]
    for pt in f[::-1]:
        hv += (prev_x - pt[0]) * (ref[1] - pt[1])
        prev_x = pt[0]
    return hv

# --- GP surrogate ---

class BiObjectiveGP:
    def __init__(self):
        k = ConstantKernel(1.0) * Matern(nu=2.5, length_scale=np.ones(N)) + WhiteKernel(0.1)
        self.gp1 = GaussianProcessRegressor(k, normalize_y=True, n_restarts_optimizer=3, random_state=0)
        self.gp2 = GaussianProcessRegressor(k, normalize_y=True, n_restarts_optimizer=3, random_state=1)
        self.sc1 = StandardScaler(); self.sc2 = StandardScaler()

    def fit(self, X, y1, y2):
        self.gp1.fit(X, self.sc1.fit_transform(y1[:,None]).ravel())
        self.gp2.fit(X, self.sc2.fit_transform(y2[:,None]).ravel())

    def predict(self, X):
        m1,s1 = self.gp1.predict(X, return_std=True)
        m2,s2 = self.gp2.predict(X, return_std=True)
        m1 = self.sc1.inverse_transform(m1[:,None]).ravel()
        m2 = self.sc2.inverse_transform(m2[:,None]).ravel()
        s1 *= self.sc1.scale_[0]; s2 *= self.sc2.scale_[0]
        return m1, s1, m2, s2

# --- Acquisition ---

def acq(x_flat, gp, pareto, ref, xi=0.01):
    x = np.clip(x_flat, 0, 1).reshape(1,-1)
    x = x / (x.sum() + 1e-12)
    m1,s1,m2,s2 = gp.predict(x)
    b1, b2 = pareto[:,0].min(), pareto[:,1].min()

    def ei(mu, std, best):
        if std < 1e-10: return 0.0
        z = (best - mu - xi) / std
        return (best-mu-xi)*norm.cdf(z) + std*norm.pdf(z)

    # Hypervolume improvement from predicted point
    new_pt = np.array([[m1[0], m2[0]]])
    all_pts = np.vstack([pareto, new_pt])
    new_pareto = all_pts[pareto_mask(all_pts)]
    delta_hv = max(0, hv2d(new_pareto, ref) - hv2d(pareto[pareto_mask(pareto)], ref))

    score = (0.3*ei(m1[0],s1[0],b1)/(b1+1) +
             0.3*ei(m2[0],s2[0],b2)/(b2+1) +
             0.4*delta_hv)
    return -score

def suggest(gp, pareto, ref):
    best_score, best_x = np.inf, None
    cons = [{'type':'eq','fun': lambda x: x.sum()-1.0}]
    bnds = [(0.0, 0.75)] * N
    for _ in range(N_RESTARTS):
        x0 = np.random.dirichlet(np.ones(N))
        res = minimize(acq, x0, args=(gp,pareto,ref),
                       method='SLSQP', bounds=bnds, constraints=cons,
                       options={'maxiter':150,'ftol':1e-5})
        if res.fun < best_score:
            best_score, best_x = res.fun, res.x
    best_x = np.clip(best_x, 0, 1)
    return best_x / best_x.sum()

# --- Main loop ---

def run():
    ref = np.array([620.0, 20.0])

    print("Phase 1: Random initial sampling...")
    X  = np.random.dirichlet(np.ones(N), N_INITIAL)
    y1 = np.array([evaluate(x)[0] for x in X])
    y2 = np.array([evaluate(x)[1] for x in X])

    hist = {'eta':[], 'diss':[], 'pareto_n':[]}
    gp = BiObjectiveGP()

    print(f"Phase 2: Bayesian optimisation ({N_ITERATIONS} iterations)...")
    for it in range(N_ITERATIONS):
        gp.fit(X, y1, y2)
        costs = np.column_stack([y1, y2])
        pm    = pareto_mask(costs)
        par   = costs[pm]

        x_next = suggest(gp, par, ref)
        e, d   = evaluate(x_next)
        X  = np.vstack([X,  x_next])
        y1 = np.append(y1, e)
        y2 = np.append(y2, d)

        hist['eta'].append(y1.min())
        hist['diss'].append(y2.min())
        hist['pareto_n'].append(pm.sum())

        if (it+1) % 10 == 0:
            print(f"  [{it+1:3d}/{N_ITERATIONS}]  "
                  f"best eta={y1.min():.0f}mV  "
                  f"best diss={y2.min():.3f} ug/cm2/h  "
                  f"Pareto pts={pm.sum()}")

    return X, y1, y2, hist

# --- Report ---

def report(X, y1, y2):
    costs = np.column_stack([y1, y2])
    pm    = pareto_mask(costs)
    pX, pe, pd_ = X[pm], y1[pm], y2[pm]

    # Rank by balanced score
    en = (pe - pe.min()) / (np.ptp(pe) + 1e-9)
    dn = (pd_ - pd_.min()) / (np.ptp(pd_) + 1e-9)
    order = np.argsort(0.5*en + 0.5*dn)

    rows = []
    print("\n" + "="*70)
    print(f"TOP 10 COMPOSITIONS  (from {pm.sum()} Pareto-optimal points)")
    print("="*70)
    for rank, idx in enumerate(order[:10]):
        comp = pX[idx]
        eta, diss = pe[idx], pd_[idx]
        parts = [(NAMES[i], comp[i]) for i in range(N) if comp[i] > 0.03]
        formula = " ".join(f"{n}={v:.3f}" for n,v in parts)
        cost  = sum(ELEMENTS[n]['cost']*v for n,v in parts)
        n_el  = sum(1 for v in comp if v > 0.05)
        print(f"\n  Rank {rank+1}: {formula}")
        print(f"    eta_10 = {eta:.0f} mV  |  dissolution = {diss:.3f} ug/cm2/h")
        print(f"    elements >5%: {n_el}  |  est. material cost: ${cost:.2f}/kg")
        rows.append({
            'rank': rank+1, 'eta_10_mv': round(eta),
            'dissolution_ug_cm2_h': round(diss,3),
            'n_elements_above_5pct': n_el,
            'material_cost_usd_per_kg': round(cost,2),
            **{n: round(float(comp[i]),4) for i,n in enumerate(NAMES)}
        })

    df = pd.DataFrame(rows)
    df.to_csv('../results_top_heo_compositions.csv', index=False)
    print("\n  Saved: results_top_heo_compositions.csv")
    return df

# --- Plots ---

def plots(X, y1, y2, hist):
    n_init = N_INITIAL
    costs  = np.column_stack([y1, y2])
    pm     = pareto_mask(costs)

    fig, axes = plt.subplots(1, 3, figsize=(16, 5))
    fig.suptitle("Bayesian Optimisation: HEO Catalyst Composition Search\n"
                 "8 elements (Fe Co Ni Cr Mn V W Mo)  |  Objectives: OER overpotential + dissolution rate",
                 fontsize=12, fontweight='bold')

    # 1. Pareto front
    ax = axes[0]
    ax.scatter(y1[:n_init], y2[:n_init], c='#cccccc', s=35, alpha=0.7, label='Random init', zorder=2)
    sc = ax.scatter(y1[n_init:], y2[n_init:], c=range(N_ITERATIONS),
                    cmap='plasma', s=50, alpha=0.8, label='BO iterations', zorder=3)
    plt.colorbar(sc, ax=ax, label='Iteration')
    pe, pd_ = y1[pm], y2[pm]
    srt = np.argsort(pe)
    ax.plot(pe[srt], pd_[srt], 'r-', lw=2, label='Pareto front', zorder=4)
    ax.scatter(pe, pd_, c='red', s=90, marker='*', zorder=5,
               label=f'Pareto-optimal ({pm.sum()})')
    ax.set_xlabel('OER overpotential eta_10 (mV)  [minimize]', fontsize=10)
    ax.set_ylabel('Dissolution rate (ug/cm2/h)  [minimize]', fontsize=10)
    ax.set_title('Activity vs. Stability Pareto Front', fontsize=11)
    ax.legend(fontsize=8)
    ax.grid(alpha=0.3)

    # 2. Convergence
    ax = axes[1]
    iters = range(1, len(hist['eta'])+1)
    ax2 = ax.twinx()
    l1, = ax.plot(iters, hist['eta'],  'b-',  lw=2, label='Best eta_10 (mV)')
    l2, = ax2.plot(iters, hist['diss'], 'r--', lw=2, label='Best dissolution')
    l3, = ax.plot(iters, hist['pareto_n'], 'g:', lw=1.5, label='Pareto size')
    ax.set_xlabel('BO Iteration', fontsize=10)
    ax.set_ylabel('eta_10 (mV) / Pareto size', fontsize=10, color='blue')
    ax2.set_ylabel('Dissolution (ug/cm2/h)', fontsize=10, color='red')
    ax.set_title('Optimisation Convergence', fontsize=11)
    ax.legend(handles=[l1, l2, l3], fontsize=8)
    ax.grid(alpha=0.3)

    # 3. Element correlations
    ax = axes[2]
    c_eta  = [np.corrcoef(X[:,i], y1)[0,1] for i in range(N)]
    c_diss = [np.corrcoef(X[:,i], y2)[0,1] for i in range(N)]
    xp = np.arange(N)
    ax.bar(xp-0.2, c_eta,  0.38, label='Corr with eta_10',    color='steelblue', alpha=0.85)
    ax.bar(xp+0.2, c_diss, 0.38, label='Corr with dissolution', color='coral',     alpha=0.85)
    ax.axhline(0, color='k', lw=0.6)
    ax.set_xticks(xp); ax.set_xticklabels(NAMES, fontsize=11)
    ax.set_ylabel('Pearson r', fontsize=10)
    ax.set_title('Element Correlations\n(negative = lowers objective = good)', fontsize=10)
    ax.legend(fontsize=8)
    ax.grid(axis='y', alpha=0.3)

    plt.tight_layout()
    out = '../results_bayesian_heo.png'
    plt.savefig(out, dpi=150, bbox_inches='tight')
    print(f"  Plot saved: {out}")


# --- Pareto element composition heatmap ---

def pareto_heatmap(X, y1, y2):
    costs = np.column_stack([y1, y2])
    pm    = pareto_mask(costs)
    pX, pe = X[pm], y1[pm]
    order  = np.argsort(pe)
    pX_sorted = pX[order]

    fig, ax = plt.subplots(figsize=(12, 4))
    im = ax.imshow(pX_sorted.T, aspect='auto', cmap='YlOrRd', vmin=0, vmax=0.6)
    ax.set_yticks(range(N)); ax.set_yticklabels(NAMES, fontsize=12)
    ax.set_xlabel('Pareto-optimal compositions  (left=most active, right=most stable)', fontsize=11)
    ax.set_title('Element Fractions Across the Pareto Front', fontsize=12)

    # Annotate eta values on top
    eta_sorted = pe[order]
    for i, eta in enumerate(eta_sorted):
        ax.text(i, -0.7, f'{eta:.0f}', ha='center', va='top', fontsize=8, rotation=70)

    plt.colorbar(im, ax=ax, label='Element fraction')
    plt.tight_layout()
    out = '../results_pareto_heatmap.png'
    plt.savefig(out, dpi=150, bbox_inches='tight')
    print(f"  Plot saved: {out}")


if __name__ == '__main__':
    X, y1, y2, hist = run()
    df = report(X, y1, y2)
    plots(X, y1, y2, hist)
    pareto_heatmap(X, y1, y2)
    print("\nDone. Check I:/Scratch/green-h2-catalyst-research/ for output files.")
