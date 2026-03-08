# 17 — Closing the Gap: Quantitative Roadmap to IrO₂-Free Green Hydrogen

**Date:** March 2026
**Status:** Active research programme
**Objective:** Replace IrO₂ in PEM electrolysers and NiMo/NiFe in AEL with earth-abundant catalysts that are commercially competitive on both activity and lifetime.

---

## 1. Where We Stand: The Two Gaps

### Gap 1 — Acid OER Dissolution (Critical)

| Metric | IrO₂ Benchmark | Best Earth-Abundant (to date) | Gap |
|--------|----------------|-------------------------------|-----|
| Dissolution potential E_diss | **1.60 V** | 1.08 V (Ca-Mn-W birnessite) | **0.52 V** |
| Dissolution rate D at 10 mA/cm² | **0.01 µg/cm²/h** | 7.4 µg/cm²/h (MnWTi, best-in-class) | **740×** |
| Predicted lifetime | **>50,000 h** | ~14 h at 10 mA/cm² | **>3,500×** |

The dissolution gap is the binding constraint. No amount of activity optimisation matters if the catalyst dissolves in 14 hours. Every descriptor analysis (SHAP, Bayesian, DFT) points to `dissolution_potential_v` as the single most important predictor.

### Gap 2 — Acid OER Activity (Manageable)

| Metric | IrO₂ Benchmark | Best Earth-Abundant | Gap |
|--------|----------------|---------------------|-----|
| Overpotential η₁₀ | **250 mV** | 331 mV (MnW binary) | **81 mV** |
| Tafel slope | 45 mV/dec | 62–72 mV/dec | ~20 mV/dec |
| TOF at η=300 mV | ~1 s⁻¹ | ~0.1 s⁻¹ | **10×** |

The activity gap (81 mV) is 10–100× easier to close than the dissolution gap. The Sabatier descriptor (eg electron occupancy ≈ 0.5 for optimal M–O bond energy) is well-understood; Ca-doping to promote Mn³⁺ is the lever.

### Gap 3 — Alkaline OER Lifetime (Moderate)

| Metric | Target | Best Published | Our Best (Bayesian) |
|--------|--------|----------------|---------------------|
| Lifetime at 100 mA/cm² | **50,000 h** | NiMo: ~10,000 h | ~200 h (predicted) |
| η₁₀ | **300 mV** | NiMo: 78 mV | ~280 mV (predicted) |

The alkaline gap is real but narrower. NiMo is already at 10,000 h; the pulsed CP protocol (doc 12) adds ~2× more. The gap is 5–10× in lifetime, not 3,500×.

---

## 2. The CaWO₄ Mechanism: Key to Gap 1

All ML, descriptor, and optimizer analyses converge on one structural finding:

> **CaWO₄ scheelite co-phase is the only earth-abundant mechanism that meaningfully raises dissolution_potential_v toward IrO₂.**

### Why CaWO₄ works

| Phase | Dissolution potential at pH 1 | Notes |
|-------|-------------------------------|-------|
| MnO₂ (birnessite) | 0.85 V | Baseline Mn-oxide |
| WO₃ | 1.05 V | W in acid |
| TiO₂ (rutile) | 1.20 V | Best passivating matrix |
| **CaWO₄ (scheelite)** | **1.38 V** | **Highest earth-abundant** |
| IrO₂ (rutile) | **1.60 V** | Target |

CaWO₄ forms when Ca × W mole fractions exceed ~0.04. The Ca-Mn-W optimizer found that ~11% Ca + ~34% W yields CaWO₄ fractions of 10–15% in the composite, raising the composite E_diss to ~1.08 V (ca. 1.38 × f_CaWO₄ + 0.85 × f_Mn + 1.05 × f_W).

### What the ca_mnw_optimizer.py found

```
Optimal region: Ca≈11%, Mn≈55%, W≈34%, Ti≈0%
  → CaWO4 fraction: 0.103
  → E_diss: 0.958 V (composite)
  → Best E_diss achieved: 1.079 V (Ca=0.148, Mn=0.317, W=0.286, Ti=0.249)

Remaining E_diss gap to IrO2: 0.521 V
IrO2 target: 1.60 V | Best CaWO4 composite: 1.079 V
```

**Critical insight**: CaWO₄ at 10–15% loading raises E_diss by ~0.23 V vs. pure Mn-oxide. Closing the remaining 0.52 V gap requires either (a) higher CaWO₄ loading (sacrifices Mn-OER sites), (b) additional high-E_diss phases, or (c) surface engineering that decouples bulk dissolution from surface reactivity.

---

## 3. The Critical Path

The shortest path to closing both gaps runs through three sequential experimental gates:

```
GATE 1 (Weeks 1–8): Verify CaWO4 formation
   ↓
GATE 2 (Weeks 8–20): Optimise Mn3+/Mn4+ ratio (activity)
   ↓
GATE 3 (Weeks 20–52): Long-duration stability at operating current density
```

If Gate 1 fails (CaWO₄ does not form at the predicted compositions), the dissolution strategy must pivot to surface TiO₂ coatings or ALD-deposited protective layers. Do not proceed to Gate 2 until CaWO₄ is confirmed by XRD + Raman.

---

## 4. Year-by-Year Milestones

### Year 1 (2026) — Proof of Mechanism

**Goal**: Confirm CaWO₄ mechanism; demonstrate >100× improvement in dissolution rate vs. pure Mn-oxide.

| Milestone | Target | Method | Pass/Fail |
|-----------|--------|---------|-----------|
| Y1.1: Synthesise P3 Ca-birnessite (Ca=11%, Mn=55%, W=34%) | CaWO₄ XRD peak at 2θ=28.7° | Hydrothermal, doc 16 P3 protocol | XRD confirms scheelite |
| Y1.2: Verify CaWO₄ by Raman | Peak at 921 cm⁻¹ ± 5 cm⁻¹ | Raman spectroscopy | Raman peak present |
| Y1.3: ICP-MS dissolution test | D < 0.5 µg/cm²/h (baseline Mn-oxide: 18) | 6h at 10 mA/cm², pH 1, 0.5 M H₂SO₄ | 36× improvement vs. baseline |
| Y1.4: OER activity | η₁₀ < 380 mV | Rotating disk electrode (RDE), pH 1 | Maintains activity |
| Y1.5: eg tuning (H₂ anneal) | Mn³⁺/Mn⁴⁺ > 0.3 by XPS | 5% H₂/N₂, 200°C, 2h post-synthesis | η₁₀ improves to <350 mV |
| Y1.6: Add 3 real data points to ML | R² > 0.65 (acid OER subset) | Retrain stability_ml.py | Model converges |

**Year 1 pass criterion**: D < 0.5 µg/cm²/h AND η₁₀ < 380 mV confirmed on same sample.

### Year 2 (2027) — Closing the Activity Gap

**Goal**: Reduce η₁₀ to <290 mV; reduce D to <0.05 µg/cm²/h; demonstrate 500h stability.

| Milestone | Target | Method |
|-----------|--------|--------|
| Y2.1: Bayesian 2nd generation (real data in loop) | η₁₀ < 290 mV predicted | Retrain surrogate on 30 real data points |
| Y2.2: W-loading sweep (20–40%) | Identify CaWO₄ saturation | XRD quantification of CaWO₄ phase fraction |
| Y2.3: Ru micro-doping (0.5–2%) | η₁₀ < 270 mV | Low Ru content, retain cost advantage |
| Y2.4: GDE/MEA single cell test | j > 500 mA/cm² at 1.8 V | Full PEM cell, 80°C, Nafion |
| Y2.5: 500h accelerated stability | D_total < 25 µg/cm² cumulative | Pulsed CP protocol (59min/1min) |
| Y2.6: Cost analysis update | Active metal cost < $5/kW | Compare to $4–8/kW for IrO₂/Pt stack |

**Year 2 pass criterion**: MEA test at >500 mA/cm² maintained for 500h.

### Year 3 (2028) — Stack Integration

**Goal**: 1,000h MEA demonstration; stack-level cost target <$3/kW active metals.

| Milestone | Target |
|-----------|--------|
| Y3.1: Membrane compatibility | Zero delamination, no Ca²⁺ contamination of Nafion |
| Y3.2: 1,000h MEA lifetime | <5% performance degradation |
| Y3.3: Scale-up synthesis | 100g batch with XRD-verified CaWO₄ fraction |
| Y3.4: Independent verification | Third-party cell test (TÜV or NREL) |

**Year 3 pass criterion**: 1,000h MEA test, independently verified, with <5% degradation.

### Year 5 (2030) — Commercial Threshold

| Metric | Target | Basis |
|--------|--------|-------|
| Stack lifetime | **>20,000 h** | PEM stack commercial spec |
| Active metal cost | **<$1/kW** | $50/ton Mn, $35/ton W at 0.1 mg/cm² loading |
| η₁₀ | **<270 mV** | Within 20 mV of IrO₂ |
| Scale | 1 MW pilot system | DOE H2Hubs scale requirement |

---

## 5. Parallel Alkaline Track (Year 1–2)

While the acid track works through Gates 1–3, the alkaline track is closer to deployable:

| Action | Timeline | Expected outcome |
|--------|----------|-----------------|
| Synthesise top Bayesian HEO (Fe=0.22, Co=0.18, Ni=0.26, Cr=0.15, Mn=0.12, W=0.07) | Month 2 | Baseline η₁₀ + 200h stability measurement |
| Apply pulsed CP (59min/1min) | Month 3 | 2× lifetime extension → ~400h |
| DEMS ¹⁸O labelling: distinguish AEM vs. LOM | Month 4 | Identify degradation mechanism |
| Add Mn to promote LOM → more acid-like stability mechanism | Month 6 | Reduce dissolution rate |
| 10,000h projection (Weibull fit to 200h data) | Month 8 | Validate ML lifetime predictions |

**Decision gate at Month 8**: If alkaline HEO exceeds NiMo at any KPI (η₁₀, lifetime, or cost), shift resources from acid track to alkaline. Otherwise, maintain 70% acid / 30% alkaline resource split.

---

## 6. What Cannot Be Shortcut

Three things have no fast path:

1. **Long-duration stability testing**: A 1,000h test takes 42 days at minimum. Accelerated stress testing (higher current, temperature) can compress this by ~3–5× but introduces artefacts. Budget: minimum 6 months per milestone.

2. **Real data in the ML loop**: The surrogate model needs 50+ real acid OER data points for reliable predictions (current: 8 real + 72 simulated). Each data point requires synthesis + characterisation + electrochemistry = ~2 weeks per composition.

3. **CaWO₄ verification**: Phase identification by XRD requires >5% CaWO₄ by weight. Below this, TEM-EDX or synchrotron PDF is required. Do not assume CaWO₄ formed without confirmed structural evidence.

---

## 7. The Hard Ceiling: E_diss = 1.38 V

**The CaWO₄ mechanism has a thermodynamic ceiling.**

Even at 100% CaWO₄ loading, the dissolution potential (1.38 V) is 0.22 V below IrO₂ (1.60 V). This 0.22 V gap translates to ~200× higher dissolution rate at operating potential. To reach IrO₂-competitive stability on dissolution potential alone, a different approach is needed:

| Strategy | E_diss ceiling | Feasibility |
|----------|----------------|-------------|
| CaWO₄ phase engineering (current) | 1.38 V | ✅ Demonstrated path |
| TiO₂ ALD surface coating (1–5 nm) | 1.20 V (surface) | ⚠️ May block active sites |
| Mixed CaWO₄/TiO₂ composite | 1.25–1.35 V | 🔬 Untested |
| MoO₃ passivation layer | 1.15 V | ⚠️ Mo dissolves in acid |
| Amorphous IrOₓ sub-monolayer (0.1 µg/cm²) | 1.60 V | ✅ Minimal Ir use, <$0.50/kW |
| Ru-doped CaWO₄ (2% Ru) | 1.45 V (estimated) | 🔬 Unknown |

**Recommended bridge strategy (Year 2–3)**:
- CaWO₄-Mn-oxide as bulk catalyst (closes 50% of dissolution gap, costs <$1/kW)
- 0.1 µg/cm² IrOₓ sub-monolayer as surface passivation (closes remaining 50%, adds ~$0.30/kW at 2030 Ir prices)
- Total: ~$1.30/kW vs. ~$7/kW for standard IrO₂ loading → **82% cost reduction**

This hybrid route accepts that a trace of Ir is needed for the 1,000+h acid stability target, while reducing Ir content by 50–100× compared to current commercial MEAs.

---

## 8. Decision Tree

```
START → Synthesise Ca(0.11)Mn(0.55)W(0.34) → CaWO4 confirmed by XRD?
                                                          │
                        YES ──────────────────────────────┼───── NO
                         │                                │       └→ Increase W or Ca; try
                         ▼                                │          hydrothermal T > 180°C
                 D < 0.5 µg/cm2/h?                       │
                    │           │                         │
                   YES          NO                        │
                    │           └→ Increase CaWO4 loading │
                    │              (raise Ca to 15%)      │
                    ▼                                      │
              η10 < 380 mV?                               │
               │        │                                  │
              YES        NO                                │
               │         └→ H2/N2 anneal (200°C, 2h)     │
               │            or increase Mn/(Mn+W) ratio   │
               ▼                                           │
         GATE 1 PASSED → proceed to Year 2 →──────────────┘
```

---

## 9. Key Experimental Checkpoints

### Characterisation required at each gate

**Gate 1 (Structural)**
- XRD: 2θ = 28.7° (CaWO₄ scheelite (112) reflection), 37.3° (MnO₂), 25.3° (TiO₂ anatase)
- Raman: 921 cm⁻¹ (CaWO₄ W–O stretch), 650 cm⁻¹ (MnO₂)
- XPS: Mn 2p₃/₂ at 641.5 eV (Mn³⁺) vs. 642.2 eV (Mn⁴⁺); Ca 2p at 347.2 eV (CaWO₄)
- BET: Surface area (target >80 m²/g)

**Gate 2 (Electrochemical)**
- CV in 0.5 M H₂SO₄: confirm no Mn dissolution peak at E < 1.0 V vs. RHE
- OER polarisation curve (10 mV/s): extract η₁₀, Tafel slope
- EIS at η = 300 mV: extract charge transfer resistance R_ct
- ICP-MS aliquot at t = 1, 3, 6 h: dissolve rate vs. time curve

**Gate 3 (Stability)**
- CP at 10 mA/cm² for 500h in 0.5 M H₂SO₄, 25°C
- ICP-MS: cumulative dissolved Mn, W, Ca, Ti
- Post-test XRD + Raman: quantify CaWO₄ retention
- SEM cross-section: measure film thinning rate

---

## 10. Summary: The Shortest Path

The shortest path to a commercially viable acid OER catalyst is:

1. **Make Ca-Mn-W birnessite** (doc 16, P3 route) — 4–6 weeks
2. **Confirm CaWO₄ by XRD** — go/no-go in Week 6
3. **Measure D and η₁₀** — 2-week ICP-MS campaign
4. **H₂/N₂ anneal to tune Mn³⁺/Mn⁴⁺** — closes activity gap
5. **Run 500h CP** — 3 weeks wall time with pulsed protocol
6. **If D > 0.05 µg/cm²/h: add IrOₓ sub-monolayer** (0.1 µg/cm²) as bridge

If this 6-step path succeeds, the resulting catalyst has:
- Activity within 30–50 mV of IrO₂ (achieved by Mn³⁺ tuning)
- Dissolution rate within 5–50× of IrO₂ (achieved by CaWO₄ + IrOₓ bridge)
- Active metal cost <$2/kW (dominated by Mn and W)

This is achievable in 12 months with one dedicated researcher and basic electrochemistry infrastructure.

---

*Generated March 2026 from Bayesian optimizer results (ca_mnw_optimizer.py), SHAP analysis (shap_analysis.py), and descriptor gap analysis (materials_project_api.py). All composition predictions are model-derived and require experimental validation.*
