# 14 — Experimental Roadmap: What to Do First

## Purpose

This document translates the full analysis (docs 01–13, Bayesian optimizer results,
ML model predictions, SHAP feature importances) into a prioritized experimental plan
for a research group starting from scratch.

**Assumptions:**
- Lab is equipped for basic electrochemistry (potentiostat, 3-electrode cell)
- Hydrothermal synthesis capability
- ICP-MS available (or accessible at university core facility)
- Budget: ~$50,000 USD first year (reagents, electrodes, electrolyte)
- Timeline: 12 months

---

## Priority Logic

Three filters were applied to every hypothesis from `06-hypotheses.md`:

1. **ML stability score** — does the ML model predict high stability for this composition class?
2. **Bayesian optimizer output** — does this match optimizer-identified features?
3. **Practical tractability** — can it be made in a week with standard equipment?

The intersection of all three defines Priority 1. Everything else is sequenced by
impact and feasibility.

---

## PHASE 0 — Week 1: Infrastructure (Before Any Catalyst Work)

Before synthesizing anything, get the electrolyte right. This single step has more
impact on reproducibility than any other.

### KOH Purification Protocol (Critical)

**Why:** 99.9% KOH from suppliers contains 1–100 ppm Fe. At 10 ppm Fe in 1M KOH,
Fe deposits onto Ni electrodes activate NiOOH by >50 mV. This makes "pure" NiOH₂
look active — it isn't. It also corrupts stability data.

**Protocol:**
1. Dissolve 56 g KOH in 500 mL Milli-Q water (1M KOH)
2. Add 1 g Ni(OH)₂ powder, stir 24h at room temperature
3. Filter through 0.22 μm PTFE membrane (×2)
4. Measure [Fe] by ICP-MS — must be < 0.005 ppm before use
5. Store in sealed HDPE bottle under N₂
6. Repeat ICP-MS check weekly; discard if [Fe] > 0.01 ppm

**Expected cost:** < $50 in reagents. **Expected time:** 2 days.

---

## PHASE 1 — Weeks 2–4: Baseline Characterisation (3 Experiments)

### Experiment 1A: NiFe LDH — Full Baseline (Protocol A + B)

**Why first:** NiFe LDH is the benchmark. Every stability claim in the field is
implicitly referenced against it. Without your own baseline, you cannot interpret
any subsequent result.

**Synthesis (Day 1):**
```
Ni(NO₃)₂·6H₂O: 1.164 g
Fe(NO₃)₃·9H₂O: 0.404 g
Urea: 0.450 g
DI water: 50 mL
Hydrothermal: 120°C, 12h, PTFE-lined autoclave
Substrate: Ni foam (1 cm², cleaned: acetone → ethanol → DI water, 10 min each)
Loading: 5 mg/cm²
```

**Electrochemical testing (Days 2–21):**
- Protocol A: 10 mA/cm² constant, 500h
- Protocol B (parallel cell): 10 mA/cm² for 59 min, OC for 1 min, repeat
- CV characterization every 24h (0.9–1.7 V vs RHE, 10 mV/s, 3 cycles)
- EIS every 48h at 1.50 V vs RHE (0.1–100,000 Hz, 10 mV amplitude)

**What you'll get:**
- Your lab's NiFe LDH baseline: η₁₀(t=0), Tafel slope, deactivation rate
- First direct measurement of whether pulsed CP extends lifetime

**Expected outcome (from literature synthesis):**
- Protocol A: ~25–40% activity loss over 500h
- Protocol B: ~10–15% activity loss (our prediction) — **this would be a new result**

**Decision point:** If Protocol B shows >15 mV η₁₀ improvement vs. A at 200h,
immediately scale to 5 catalysts (Phase 2).

---

### Experiment 1B: NiFeV LDH — V Addition Baseline

**Why:** NiFeV LDH shows ~35 mV lower η₁₀ than NiFe LDH at t=0. Whether the
V-enhanced activity is maintained under stability testing is unknown. The ML model
and Bayesian optimizer both flagged V as a key stability promoter, but this is
unvalidated experimentally.

**Synthesis:**
```
NiSO₄·6H₂O: 0.526 g
FeSO₄·7H₂O: 0.278 g
VOSO₄: 0.163 g (10 mol% V vs total metal)
NaOH (4M): dropwise to pH 9 under N₂
Temperature: 80°C, 6h
Substrate: FTO (1 cm²)
Loading: 3 mg/cm²
```

**Testing:** Same as 1A — Protocols A and B in parallel, 200h minimum.

**Critical measurement:** ICP-MS on electrolyte every 24h.
Track: Ni, Fe, V dissolution rates separately.
If V dissolution < 5% of Fe dissolution rate, V is genuinely stabilising the LDH network.

---

### Experiment 1C: Quick-Win Dissolution Mapping (3 days)

**Why:** Before committing 500h to stability tests, measure short-term dissolution
kinetics for 5 candidate catalysts using the power-law fitting protocol.

**Protocol:**
1. Run each catalyst at 10 mA/cm² for 24h in H₂SO₄ or KOH (depending on catalyst)
2. Collect 1 mL electrolyte every 2h for first 12h, then every 4h
3. ICP-MS: measure primary metal concentrations
4. Fit: D(t) = D₀ · t^(−α)
   - High α (> 0.5) → dissolution self-passivates → long-term stable
   - Low α (< 0.2) → dissolution continues linearly → will fail long-term
5. Extrapolate to 1000h using power law

**Catalysts to test in 1C:**
- FeCoNiCrMn HEO (to validate our ML prediction of ~50h)
- FeCoNiCrMnV HEO (V addition — does it improve?)
- Amorphous NiFeMo (predicted 180h — verify)
- WC@NC (predicted 100h acid HER — verify)
- NiMo alloy (known commercial standard — calibration)

**Budget:** ~$800 in reagents + ICP-MS time (~$50/sample × 60 samples = $3,000)
This experiment screens 5 catalysts in 3 days vs. 5 × 500h = 2,500h for full tests.

---

## PHASE 2 — Weeks 5–12: Systematic Investigation

### Priority Ranking (from Bayesian Optimizer + ML Model)

Run these in strict priority order. Each feeds information to the next.

---

### Experiment 2A: Mn-V-W-Mo Quartet — Systematic Composition Sweep

**Background:** The Bayesian optimizer identified the Mn-V-W-Mo quartet as the
dominant stability regime. V appears in 8 of 9 top compositions. This experiment
directly tests the optimizer's prediction.

**Design:** 9 compositions from optimizer output

| Rank | Composition | η predicted (mV) | Dissolution predicted |
|------|-------------|-----------------|----------------------|
| 1 | Fe₀.₂₀Co₀.₁₉Mn₀.₀₉V₀.₁₅W₀.₁₈Mo₀.₁₉ | 263 | 1.51 |
| 2 | Fe₀.₁₅Co₀.₂₀V₀.₂₂W₀.₂₂Mo₀.₂₁ | 270 | 1.28 |
| 3 | Fe₀.₁₆Co₀.₁₈Mn₀.₁₀V₀.₁₈W₀.₂₁Mo₀.₁₇ | 268 | 1.35 |
| — | V₀.₂₅W₀.₂₅Mo₀.₂₅Fe₀.₁₂Co₀.₁₃ (V-max) | 278 | 1.22 |
| — | Fe₀.₂₀Co₀.₂₀Mn₀.₂₀V₀.₂₀Mo₀.₂₀ (no W) | 275 | 1.55 |
| — | Fe₀.₂₀Co₀.₂₀V₀.₂₀W₀.₂₀Mo₀.₂₀ (no Mn) | 271 | 1.40 |

**Synthesis (ball-milling route for speed):**
```
Metal oxide/salt precursors: Fe₂O₃, Co₃O₄, MnO₂, V₂O₅, WO₃, MoO₃
Ball-mill: 10h at 400 rpm, 10:1 ball:powder ratio, ZrO₂ balls
Calcine: 800°C, 4h, air
Screen to <75 μm
Prepare ink: 5 mg/mL in IPA + 0.05% Nafion
Load: 0.5 mg/cm² on GCE
```

**Testing (short-form, 24h):**
- CV: η₁₀, Tafel slope
- Dissolution (ICP-MS, 24h): D(t) → extrapolate to 1000h
- EIS: Rct before and after 24h

**Key comparison:** Rank 1 vs. Rank 1 minus V (same composition, V replaced by Co).
If V removal decreases stability by >2×, V role is confirmed.

---

### Experiment 2B: Pulsed CP — Mechanistic Investigation (Operando)

**Why:** This is the mechanistic heart of Hypothesis C2 and the preprint (doc 12).
Protocol A vs. B comparison in 1A gives the performance result.
This experiment gives the *mechanism*.

**Equipment needed:** Raman spectrometer with electrochemical cell window (532 nm laser)

**Protocol:**
1. Apply Protocol A (constant) for 2h — acquire Raman every 5 min
   - Track: NiOOH band at 480 cm⁻¹, Fe-O* band at ~560 cm⁻¹
   - Expected: 560 cm⁻¹ band grows slowly → O* accumulation

2. Switch to OC for 60s — acquire Raman every 5s
   - Expected: 560 cm⁻¹ band drops within 20–40s → O* desorption
   - If it drops: O* desorption mechanism confirmed

3. Reapply current — track recovery to original 560 cm⁻¹ intensity

**This is the most important single experiment in this roadmap.**
If O* accumulation/desorption is confirmed by Raman:
- Mechanism is established
- Rest protocol directly addresses mechanism
- Paper is Nature Energy quality, not just ACS Energy Letters

**Backup (no Raman):** Run EIS every 10 min during constant CP.
Rct increase during operation + Rct recovery during rest = indirect site blocking evidence.

---

### Experiment 2C: ¹⁸O Isotope Labeling on Top 3 Candidates (Protocol from doc 13)

**Why:** Determines whether catalysts are using AEM or LOM — the single most
important mechanistic question in OER research.

**Priority candidates:**
1. NiFe LDH (most-studied — need baseline LOM fraction)
2. BSCF perovskite (LOM expected from literature — calibration)
3. Best HEO from Experiment 2A (is the V-Mn-Mo combination LOM-active?)

**Protocol:** See `13-18O-labeling-protocol.md` for complete procedure.

**Expected timeline:** 6 days per catalyst × 3 = 18 days
**Budget:** ~$2,500 (H₂¹⁸O is expensive; ~£150/100 mL)

**Key result:** If HEO shows LOM contribution > 20%, it is escaping scaling relations.
This would be a genuinely new finding — no HEO has been tested for LOM to our knowledge.

---

### Experiment 2D: Acid OER — Ca-Mn-Ru-Ox System

**Why:** The single biggest gap in the field is earth-abundant acid OER.
Ca-Mn-Ru-Ox is the most promising non-IrO₂ acid OER system known.
Systematic Ru loading sweep (0%, 1%, 3%, 5%, 10%) is not in the literature.

**Synthesis:**
```
Ca(NO₃)₂: 0.82 g (in 20 mL DI water)
KMnO₄: 1.58 g
RuCl₃·xH₂O: 0.52, 1.05, 1.56, 3.13 mg (for 1, 3, 5, 10 mol% Ru)
Sol-gel: mix, age 24h at room temperature
Calcine: 550°C, 4h, air, ramp 2°C/min
Substrate: Ti mesh (1 cm², HF-etched for adhesion)
Loading: 2 mg/cm²
```

**Testing:**
- CV in 0.5M H₂SO₄: η₁₀ at each Ru loading
- 24h stability test at 10 mA/cm²: ICP-MS for Mn, Ca, Ru dissolution
- Target: η < 400 mV AND < 5% Ru dissolution at 24h → go to 200h test

**Budget:** RuCl₃ is expensive (~$800/g, but you need <50 mg for the sweep)

---

## PHASE 3 — Weeks 9–12: Scale-Up and Optimisation

### Experiment 3A: Best Catalyst from Phase 2 — 500h Stability Test

Run the winner from Phase 2 (most likely top HEO or optimised NiFeV LDH) through
the full 500h Protocol A vs. B comparison.

At this point you have:
- Established your baseline (1A)
- Validated composition (2A)
- Confirmed mechanism (2B)
- Checked for LOM (2C)

The 500h test is the quantitative confirmation that gets submitted.

### Experiment 3B: Current Density Scale-Up

All previous tests at 10 mA/cm². Industrial PEM operates at 1,000–4,000 mA/cm².

Test your best catalyst at: 10, 50, 100, 500 mA/cm² (1h each, measure η₁₀ normalised)
Key question: Does performance relative to IrO₂ improve or worsen at high current density?
If it improves: O* kinetics argument supports higher-current operation.

---

## Budget Allocation ($50,000 over 12 months)

| Category | Budget | Notes |
|----------|--------|-------|
| Reagents (synthesis) | $8,000 | Metal salts, solvents, NaH₂PO₂, Se, etc. |
| KOH (purified, large quantity) | $800 | 10 kg, multiple purification runs |
| H₂¹⁸O (isotope labeling) | $3,500 | 200 mL × £150/100mL |
| ICP-MS time (core facility) | $12,000 | ~240 samples × $50/sample |
| Electrode substrates | $3,000 | Ni foam, carbon cloth, FTO, Ti mesh |
| RuCl₃ for 2D | $1,500 | Small quantity, careful handling |
| Raman cell components | $2,500 | Electrochemical window cell |
| GC-MS / DEMS time | $5,000 | For ¹⁸O labeling validation |
| Consumables | $4,000 | Nafion, Pt counter electrode, etc. |
| Post-mortem XPS time | $4,000 | Before/after for top 3 catalysts |
| Contingency | $5,700 | Instrument failures, repeat tests |
| **Total** | **$50,000** | |

---

## Decision Tree

```
Week 4 result:
  Protocol A vs. B shows >15 mV improvement?
  ├── YES → Priority 1: Scale to 5 catalysts + Raman (2B)
  │         Priority 2: Continue composition sweep (2A)
  └── NO  → Investigate rest time: try 5 min/h rest instead
             If still no improvement → mechanism is not O* blocking
             → Pivot to ICP-MS dissolution study first

Week 8 result:
  HEO compositions — is V-Mn-Mo quartet confirmed?
  ├── YES → Write preprint + synthesize best composition at scale
  └── NO  → Check: is V dissolving? (ICP-MS)
             If V stable: problem is d-band mismatch → adjust Fe/Co ratio
             If V dissolving: V is not a structural stabiliser → pivot to W-Mo

Week 8 result:
  ¹⁸O labeling — any LOM contribution in HEO?
  ├── YES (>10% LOM) → This is potentially the most important result
  │                    Immediately write short communication + preprint
  └── NO  → AEM mechanism confirmed in HEO → adjust targets to improve AEM efficiency
```

---

## What NOT to Do First

These are common traps in the field:

1. **Don't optimise synthesis conditions before establishing stability baseline.**
   The most active catalyst is not the most useful — stability matters 100× more.

2. **Don't run Tafel slopes as primary metric for new compositions.**
   Tafel slope is mechanism-sensitive and ECSA-dependent. Use η₁₀/η₁₀₀ instead.

3. **Don't test in unpurified KOH** — your results will not be reproducible.

4. **Don't compare to literature values without checking electrolyte purity.**
   Many literature "records" were measured in Fe-contaminated KOH.

5. **Don't skip post-mortem XPS.** Knowing what changed structurally is what
   separates a mechanism paper from a performance paper.

---

## Manuscript Strategy

Based on experimental outcomes, the publications should be:

| Experiment | Target journal | IF estimate | Timeline |
|------------|---------------|-------------|----------|
| Protocol A vs. B on NiFe LDH (1A) + Raman (2B) | Nature Energy | 60 | Month 10 |
| Bayesian optimizer + HEO validation (2A) | Nature Catalysis | 42 | Month 11 |
| ¹⁸O labeling across catalyst classes (2C) | JACS | 16 | Month 12 |
| Ca-Mn-Ru-Ox acid OER sweep (2D) | ACS Energy Lett. | 19 | Month 9 |

The pulsed CP paper (experiment 1A + 2B) is the highest-impact first target
because it requires the fewest new materials — just a protocol change on existing
NiFe LDH. A positive result can be submitted within 4 months of starting.

---

## Quick Reference: Materials Needed Week 1

Verify these are in stock or ordered before starting:

**Chemicals:**
- [ ] Ni(NO₃)₂·6H₂O (ACS grade)
- [ ] Fe(NO₃)₃·9H₂O (ACS grade)
- [ ] NiSO₄·6H₂O
- [ ] FeSO₄·7H₂O
- [ ] VOSO₄ (vanadyl sulfate)
- [ ] Urea (analytical grade)
- [ ] KOH pellets (2 kg, Sigma-Aldrich or equivalent)
- [ ] Ni(OH)₂ (for KOH purification column)
- [ ] Isopropanol (anhydrous, for ink preparation)
- [ ] Nafion solution (5% in isopropanol, Sigma)

**Substrates:**
- [ ] Ni foam (PPI 100, 1mm thick, cut to 1 cm² × 30 pieces)
- [ ] FTO glass (7 Ω/sq, 1 cm² × 20 pieces)

**Reference electrodes:**
- [ ] Hg/HgO (1M KOH filling — not commercial HgO which uses KCl)
- [ ] Verify calibration against RHE daily

**Counter electrode:**
- [ ] Pt wire or Pt mesh (in separated compartment!)
  Note: Pt dissolution at high anodic potential can deposit on WE.
  Always use membrane-separated Pt counter.
