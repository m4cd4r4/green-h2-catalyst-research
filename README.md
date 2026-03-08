# Green Hydrogen Electrolysis Catalyst Discovery
### A Structured Research Synthesis for Earth-Abundant Catalyst Development

**Generated:** March 8, 2026
**Purpose:** Research roadmap for replacing platinum-group metals (PGMs) in water electrolysis
**Intended audience:** Materials scientists, electrochemists, ML researchers, grad students
**License:** Public domain — use freely

---

## Contents

### Research Documents

| File | Description |
|------|-------------|
| [01-background.md](01-background.md) | Problem framing, electrochemistry primer, performance metrics |
| [02-her-catalysts.md](02-her-catalysts.md) | Hydrogen Evolution Reaction — 50+ candidate materials |
| [03-oer-catalysts.md](03-oer-catalysts.md) | Oxygen Evolution Reaction — 40+ candidate materials |
| [04-bifunctional.md](04-bifunctional.md) | Catalysts active for both HER and OER |
| [05-failure-modes.md](05-failure-modes.md) | Degradation mechanisms and stability challenges |
| [06-hypotheses.md](06-hypotheses.md) | 30+ testable research hypotheses |
| [07-ai-ml-opportunities.md](07-ai-ml-opportunities.md) | Where AI/ML can accelerate discovery |
| [08-datasets.md](08-datasets.md) | Structured performance data (200 entries: HER, OER, selenide, molecular, synthesis) |
| [09-acid-oer-deep-dive.md](09-acid-oer-deep-dive.md) | Acid OER — the hardest stability problem in the field |
| [10-experimental-protocols.md](10-experimental-protocols.md) | Lab protocols: synthesis, characterisation, stability testing |
| [11-scaling-relations-deep-dive.md](11-scaling-relations-deep-dive.md) | Thermodynamic limits and paths to break the overpotential wall |
| [12-preprint-pulsed-cp.md](12-preprint-pulsed-cp.md) | Draft preprint: pulsed CP protocol for lifetime extension |
| [13-18O-labeling-protocol.md](13-18O-labeling-protocol.md) | ¹⁸O isotope labeling — distinguishing AEM vs LOM pathways |
| [14-experimental-roadmap.md](14-experimental-roadmap.md) | Prioritised 12-month lab plan with $50K budget breakdown |
| [15-cost-analysis.md](15-cost-analysis.md) | Techno-economic analysis: catalyst performance → $/kg H₂ |
| [16-acid-oer-synthesis-guide.md](16-acid-oer-synthesis-guide.md) | Step-by-step synthesis protocols for top 3 Ca-Mn-W-Ti compositions |
| [17-closing-the-gap.md](17-closing-the-gap.md) | Quantitative gap closure roadmap — Year 1–5 milestones, critical path, CaWO₄ ceiling |
| [18-gate-protocols.md](18-gate-protocols.md) | Go/no-go protocols for all 3 critical-path gates, contingency decision trees |
| [19-preprint-acid-oer.md](19-preprint-acid-oer.md) | ACS Energy Letters preprint — BO, SHAP, CaWO₄ phase engineering, eg tuning, lifetime (~6,050 words, 5 figures, 30 refs) |
| [20-track-comparison.md](20-track-comparison.md) | Acid vs. alkaline track comparison — risk/resource analysis, Month 8 decision gate, 70/30 split recommendation |

### Code

| File | Description |
|------|-------------|
| [code/stability_ml.py](code/stability_ml.py) | ML stability predictor — 88 catalysts, 34 features, RF/Ridge/GB (R²=0.542) |
| [code/bayesian_heo_optimizer.py](code/bayesian_heo_optimizer.py) | Multi-objective Bayesian optimizer over 8-element HEO space |
| [code/shap_analysis.py](code/shap_analysis.py) | SHAP feature importance + stability predictions for new compositions |
| [code/pulsed_cp_analysis.py](code/pulsed_cp_analysis.py) | Pulsed CP protocol simulation — dissolution kinetics, lifetime projection |
| [code/dems_analysis.py](code/dems_analysis.py) | DEMS signal modelling — AEM vs LOM oxygen isotope fractionation |
| [code/acid_oer_optimizer.py](code/acid_oer_optimizer.py) | Acid-constrained Bayesian optimizer for Mn/Fe/Co/Cr/V/W/Mo/Ti HEA space |
| [code/materials_project_api.py](code/materials_project_api.py) | DFT descriptor bridge — d-band, Pourbaix, eg, M-O bond energy gap analysis |
| [code/ca_mnw_optimizer.py](code/ca_mnw_optimizer.py) | Focused 4-element Ca-Mn-W-Ti optimizer with CaWO₄ phase thermodynamics |
| [code/gate1_phase_predictor.py](code/gate1_phase_predictor.py) | Gate 1: CaWO₄ phase formation — thermodynamics, synthetic XRD, go/no-go |
| [code/gate2_eg_tuner.py](code/gate2_eg_tuner.py) | Gate 2: eg electron occupancy — H₂/N₂ anneal optimiser, OER volcano |
| [code/gate3_lifetime_projector.py](code/gate3_lifetime_projector.py) | Gate 3: 500h dissolution + P50 lifetime projection, multi-phase model |
| [code/dashboard.py](code/dashboard.py) | Streamlit dashboard — 5 tabs: Pareto Explorer, Composition Predictor, Gate Status, Lifetime Projector, Literature |
| [code/data_ingestion.py](code/data_ingestion.py) | Real-data ingestion pipeline — ICP-MS CSV, OER polarisation curves, Gate JSON, ML dataset auto-update |

### Key Results

| File | Description |
|------|-------------|
| [results_top_heo_compositions.csv](results_top_heo_compositions.csv) | Top 10 HEO compositions from alkaline Bayesian optimizer |
| [code/results_stability_predictions.csv](code/results_stability_predictions.csv) | ML stability predictions for 6 new compositions |
| [results_pulsed_cp_summary.csv](results_pulsed_cp_summary.csv) | Pulsed CP lifetime projections for 5 catalyst families |
| [results_dems_lom_fractions.csv](results_dems_lom_fractions.csv) | DEMS-derived LOM fraction by catalyst and overpotential |

---

## The Problem in One Paragraph

Green hydrogen is produced by splitting water using renewable electricity. The best catalysts
for this — platinum (cathode) and iridium/ruthenium (anode) — are rare, expensive, and
geographically concentrated. At the scale needed for a hydrogen economy, PGM supply is a
hard ceiling. Earth-abundant alternatives exist and are improving rapidly, but no single
material yet matches PGM performance AND stability AND manufacturability. This document
maps the landscape of candidates, identifies the most promising directions, and frames
open questions as testable hypotheses.

---

## Quick Reference: Best Earth-Abundant Candidates (2026 State of the Art)

| Reaction | Electrolyte | Best Non-PGM Candidate | η₁₀ (mV) | Stability |
|----------|-------------|------------------------|-----------|-----------|
| HER | Acid | Mo₂C / CoP / SAC-Mo@NC | 75–130 | Moderate |
| HER | Alkaline | NiMo alloy / Ni₂P | 80–150 | Good |
| OER | Acid | MnO₂ variants / FeCoNi HEA | 300–450 | Poor–Moderate |
| OER | Alkaline | NiFe LDH / BSCF perovskite | 230–280 | Good |
| Both | Alkaline | NiFe/CoP heterostructure | 250/130 | Moderate |

η₁₀ = overpotential (mV) to reach 10 mA/cm² — lower is better.

---

## Why This Is Hard

1. **Stability vs. Activity tradeoff** — most active surfaces are also most reactive (corrode)
2. **Scaling relations** — thermodynamic constraints link intermediate adsorption energies,
   setting a ~0.4V theoretical minimum OER overpotential (the "overpotential wall")
3. **Acid incompatibility** — most earth-abundant OER catalysts dissolve in PEM conditions
4. **Reproducibility** — catalyst performance varies wildly with synthesis conditions
5. **Testing standards** — overpotential at 10 mA/cm² on a lab electrode ≠ industrial performance

---

## ML Model Summary (SHAP Analysis, March 2026)

Random Forest trained on 80 catalysts (34 features), 5-fold CV R² = 0.427.

**Top predictors of stability (mean |SHAP|):**

| Rank | Feature | Importance | Interpretation |
|------|---------|-----------|---------------|
| 1 | `dissolution_potential_v` | 0.193 | Pourbaix stability — strongest single predictor |
| 2 | `d_band_center_ev` | 0.161 | Electronic structure — controls adsorption energetics |
| 3 | `coordination` | 0.097 | Metal coordination number |
| 4 | `surface_area_m2g` | 0.097 | Active site density |
| 5 | `is_alloy` | 0.077 | Alloy flag — captures NiMo 10,000h outlier |

**Key economic insight** (from doc 15): At lab-scale lifetimes (<2,000h), stack replacement
cost completely dominates LCOH. Lifetime 500h → 50,000h saves $562/kg H₂, while a 100 mV
improvement in η_OER saves only $0.08–0.12/kg. Every research dollar on lifetime is worth
100–1000× more than a dollar on activity, until lifetime exceeds ~20,000h.

---

*This synthesis was generated to make the research landscape navigable for newcomers and
to surface open questions worth investigating. It is not peer-reviewed. Cross-check claims
against primary literature before building on them.*
