# Code — Green Hydrogen Catalyst Research

Five Python tools for accelerating catalyst discovery via ML and Bayesian optimisation.

## stability_ml.py — Catalyst Stability Predictor

Predicts OER/HER catalyst lifetime from composition + structural features.

```bash
pip install -r requirements.txt
python stability_ml.py
```

**What it does:**
- Loads 17-catalyst dataset from literature synthesis
- Engineers 25 physically-motivated features (d-band, Pourbaix, coordination, etc.)
- Trains Ridge, Random Forest, and Gradient Boosting models
- Evaluates via Leave-One-Out cross-validation (appropriate for small datasets)
- Predicts stability for new catalyst candidates
- Fits dissolution power law D(t) = D₀·t^(-α) to kinetics data

**Extending it:**
1. Add more rows to `build_catalyst_dataset()` as you collect data
2. Replace estimated features with DFT-computed values
3. Add `mh_bond_energy_ev` from DFT for better HER model
4. Connect Materials Project API to automate feature extraction

**Key output:**
- `stability_model_diagnostics.png` — predicted vs. actual, model comparison
- `feature_importance.png` — which features matter most
- Console: stability predictions for 3 hypothesis-target catalysts

---

## bayesian_heo_optimizer.py — Composition Search

Bayesian optimization over the 8-element HEO space (Fe, Co, Ni, Cr, Mn, V, W, Mo).
Simultaneously minimizes OER overpotential AND dissolution rate.

```bash
python bayesian_heo_optimizer.py
```

**What it does:**
- Runs 10 random initial experiments (Phase 1)
- Runs 40 Bayesian optimization iterations using GP surrogate
- Tracks Pareto front of activity vs. stability
- Outputs top 10 recommended compositions for synthesis
- Includes full extension guide for real experimental use

**Connecting to real experiments:**
Replace the `evaluate_composition()` function with real measurements:

```python
def evaluate_composition(x):
    # x: numpy array of 8 element fractions (sums to 1)
    # Returns: (eta_10_mV, dissolution_rate_ug_per_cm2_per_h)

    # Format as synthesis target
    composition = dict(zip(ELEMENT_NAMES, x))

    # Your lab automation code here:
    # 1. Queue synthesis (or call synthesis robot)
    # 2. Run standard OER protocol
    # 3. Return measurements
    eta_10 = run_oer_measurement(composition)
    dissolution = run_icp_ms_measurement(composition)

    return eta_10, dissolution
```

**For production use, switch to BoTorch:**
```python
# pip install botorch torch
# Replace GP and acquisition function with:
from botorch.models import SingleTaskGP
from botorch.acquisition import qExpectedHypervolumeImprovement
# 10-100x better sample efficiency
```

**Key output:**
- `top_heo_compositions.csv` — top 10 recommended compositions
- `bayesian_heo_optimization.png` — Pareto front, convergence, element analysis
- Console: ranked compositions with predicted performance

---

## acid_oer_optimizer.py — Acid-Stable OER Composition Search

Bayesian multi-objective optimisation over a 9-element acid-tolerant space
(Mn, Fe, Co, Ni, Cr, V, W, Mo, Ti). Targets compositions that are active AND
acid-stable — the hardest open problem in green hydrogen catalysis.

```bash
python acid_oer_optimizer.py
```

**What it does:**
- Applies hard Pourbaix dissolution constraints before scoring
- Separately models OER activity and acid dissolution rate
- Tracks Pareto front: minimise η_OER AND minimise dissolution rate
- Ca-doping sweep: automatically scores Mn-rich compositions with 0–10% Ca
- Outputs ranked shortlist with acid stability confidence scores

**Design decisions vs. alkaline optimizer:**
- Narrower element set — excludes high-dissolution metals in acid
- Asymmetric penalties — dissolution in acid is catastrophic, not gradual
- Mn-bias in prior — literature supports Mn-oxide as best acid OER platform
- Includes Ti as passivating matrix element (TiO₂ forms protective layer)

**Key output:**
- `results_acid_oer_pareto.csv` — Pareto-optimal compositions
- `results_acid_oer_optimizer.png` — Pareto front, convergence, element profiles
- Console: top 5 acid-stable compositions with predicted performance

---

## shap_analysis.py — Feature Importance & Stability Prediction

SHAP (SHapley Additive exPlanations) analysis on the 80-catalyst stability dataset.

```bash
python shap_analysis.py
```

**What it does:**
- Trains 500-tree Random Forest on full 80-catalyst dataset
- Computes permutation importance (20 repeats) and TreeExplainer SHAP values
- Plots beeswarm and bar summaries for publication
- Reports subgroup statistics by OER/HER × acid/alkaline
- Predicts stability for 6 new compositions from the Bayesian optimizer

**Top findings (March 2026):**
- `dissolution_potential_v` is the #1 SHAP predictor (0.193)
- `d_band_center_ev` is #2 (0.161)
- `is_alloy` at #5 captures the NiMo 10,000h outlier
- OER alkaline median: 60h; HER alkaline median: 100h; acid OER median: 25h

**Key output:**
- `results_shap_feature_importance.png`
- `results_shap_shap_beeswarm.png`
- `results_shap_shap_bar.png`
- `results_stability_predictions.csv`

---

## pulsed_cp_analysis.py — Pulsed CP Protocol Simulation

Simulates dissolution kinetics under pulsed (59min on / 1min OC) vs. continuous
chronopotentiometry. Calculates lifetime extension factor and production loss.

```bash
python pulsed_cp_analysis.py
```

**Key output:**
- `results_pulsed_cp_*.png` — one panel per catalyst family
- `results_pulsed_cp_universality.png` — protocol universality across materials
- `results_pulsed_cp_summary.csv`

---

## dems_analysis.py — DEMS Oxygen Isotope Modelling

Models Differential Electrochemical Mass Spectrometry signals to distinguish
the Adsorbate Evolution Mechanism (AEM) from the Lattice Oxygen Mechanism (LOM).

```bash
python dems_analysis.py
```

**Key output:**
- `results_dems_comparison.png` — AEM vs LOM signal comparison by material
- `results_dems_detail.png` — time-resolved ¹⁶O/¹⁸O signal at different η
- `results_dems_lom_fractions.csv` — LOM fraction by catalyst and overpotential

---

## Workflow: How to Use All Five Together

```
ALKALINE PATH (AEL / AEMWE):
1. bayesian_heo_optimizer.py   → top 10 alkaline HEO compositions
2. Synthesize top 5            → measure η₁₀ and 200h stability
3. stability_ml.py             → retrain on real data, predict remaining 5
4. shap_analysis.py            → identify which features explain stability
5. pulsed_cp_analysis.py       → confirm 2× lifetime with pulsed protocol
6. dems_analysis.py            → distinguish AEM vs LOM in best composition

ACID PATH (PEM without IrO₂):
1. acid_oer_optimizer.py       → top 5 acid-stable compositions
2. ¹⁸O labeling (doc 13)       → screen for LOM (more acid-stable mechanism)
3. Add acid results to dataset → retrain stability_ml.py with acid data
4. shap_analysis.py            → acid-specific feature importance
5. Iterate with new optimizer run using updated surrogate
```

Both paths feed back into the same ML model, building a unified stability database
that spans AEL (alkaline) and PEM (acid) conditions. See 14-experimental-roadmap.md
for the full 12-month plan and 15-cost-analysis.md for economic targets.
