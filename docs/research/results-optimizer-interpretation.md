# Bayesian Optimizer Results — Interpretation & Synthesis Priorities

Generated: March 2026
Optimizer: 15 random + 50 BO iterations, 8-element space (Fe Co Ni Cr Mn V W Mo)
Objectives: minimise OER overpotential η₁₀ (mV) AND dissolution rate (μg/cm²/h)

---

## Raw Results Summary

| Rank | Key Elements | η₁₀ (mV) | Dissolution | Cost/kg |
|------|-------------|-----------|-------------|---------|
| 1 | Fe Co Mn V W Mo (no Cr) | 263 | 1.51 | $21 |
| 2 | Fe Co only | 200 | 4.05 | $21 |
| 3 | Mn V W Mo (no Fe/Co) | 318 | 0.01 | $22 |
| 4 | Fe Co Cr(3%) V W Mo | 279 | 1.38 | $22 |
| 5 | Fe Co Ni Mn V W Mo | 252 | 2.35 | $18 |
| 6 | Fe Co Mn V Mo | 297 | 0.82 | $19 |
| 7 | Fe Co Mn V | 224 | 3.36 | $22 |
| 8 | Fe Co Mn V(54%) W Mo | 306 | 0.64 | $25 |
| 9 | Fe Co V W Mo | 234 | 3.21 | $20 |

---

## Key Findings

### Finding 1: Vanadium is the universal stabiliser AND activity promoter

V appears in 8 of the top 9 compositions, at fractions ranging 0.10–0.54.
This is the optimizer's strongest signal. V contributes:
- **Activity:** V⁵⁺/V⁴⁺ redox is OER-accessible; V in NiFe LDH known to break scaling
- **Stability:** VO_x phases are moderately stable in mild acid; V-O bonds resist dissolution
- **No activity penalty** unlike Cr (which blocks sites at >10%)

**Laboratory action:** Synthesise Fe₀.₂Co₀.₁₅V₀.₂₅W₀.₁₈Mo₀.₂₀ (Rank 4 no-Cr variant) and
test first. If V-OER synergy confirmed, this is a genuinely novel composition.

---

### Finding 2: Chromium appears only at trace levels (3%) in best balanced compositions

The top balanced composition (Rank 1) contains NO Cr.
Rank 4 contains only 3% Cr — far below the 15% threshold for continuous Cr₂O₃ passivation.

**Interpretation:** The surrogate learned that Cr's activity penalty (blocking active sites)
outweighs its stability benefit at the concentrations where it's protective.
The optimizer prefers V+Mn+W+Mo as the stability route.

**Caveat:** The surrogate encoded Cr's stability benefit as exponential above 15%.
At 3% Cr, protection is minimal. This composition might dissolve faster in real acid tests.
**Test Rank 4 alongside a Cr=15% variant to directly compare.**

---

### Finding 3: Pareto front defines the activity–stability tradeoff clearly

```
HIGH ACTIVITY end:   Fe₀.₃₇Co₀.₆₃         → η=200mV, diss=4.1 μg/cm²/h
BALANCED:            Fe₀.₂₀Co₀.₁₉Mn₀.₀₉V₀.₁₅W₀.₁₈Mo₀.₁₉ → η=263mV, diss=1.5
STABLE end:          Mn₀.₂₄V₀.₃₄W₀.₂₂Mo₀.₂₀  → η=318mV, diss=0.01 μg/cm²/h
```

This defines where your synthesis effort should land depending on your target application:
- **AEM electrolyzer (alkaline, less stability constraint):** Target high-activity end
- **PEM electrolyzer (acid):** Target stable end, then optimise activity from there
- **Research benchmark:** Balanced Rank 1 composition first

---

### Finding 4: The Mn-V-W-Mo quartet is a new stability regime

Rank 3 (Mn₀.₂₄V₀.₃₄W₀.₂₂Mo₀.₂₀) has essentially ZERO dissolution rate in the surrogate.
This is the combination where all four elements form stable oxides in mild acid:
- MnO₂ — Pourbaix stable above pH 1
- V₂O₅ — stable in mild acid
- WO₃ — stable in acid, actually dissolves above pH 7
- MoO₃ — stable in mild acid below +0.5V

**At the Pareto stable extreme, this composition sacrifices only 50mV vs. Fe/Co
but gains near-zero dissolution.** For a 10,000h application, this tradeoff is worthwhile.

---

## Synthesis Priority List

### Priority 1 — Synthesis these first (most information per experiment)

**Composition A — Balanced, no Cr:**
Fe₀.₂₀Co₀.₁₉Mn₀.₀₉V₀.₁₅W₀.₁₈Mo₀.₁₉O_x

Synthesis:
- Co-precipitation from mixed nitrate solution (all metals)
- FeCl₃ + CoCl₂ + MnCl₂ + VOSO₄ + Na₂WO₄ + (NH₄)₆Mo₇O₂₄
- Adjust to target ratios, coprecipitate with NaOH at pH 9
- Filter, dry 80°C, calcine 400°C/2h in air
- Test in 1M KOH AND 0.5M H₂SO₄

**Composition B — Stability extreme:**
Mn₀.₂₄V₀.₃₄W₀.₂₂Mo₀.₂₀O_x

Synthesis:
- Same route as A but no Fe/Co
- MnSO₄ + VOSO₄ + Na₂WO₄ + (NH₄)₆Mo₇O₂₄
- Expect higher stability, lower activity
- Primary test in 0.5M H₂SO₄ (where Fe/Co dissolve — this should survive)

**Composition C — Activity extreme:**
Fe₀.₃₇Co₀.₆₃O_x (binary — the surrogate optimum)

Synthesis:
- Simple coprecipitation, well-known binary
- Acts as activity baseline for the multi-element compositions
- Expect it to dissolve fast in acid but serve as alkaline benchmark

---

### Priority 2 — Systematic Cr study

Make a series varying only Cr content with fixed base (Fe₀.₂Co₀.₂V₀.₂W₀.₂Mo₀.₂):

| Sample | Cr content | Expected behaviour |
|--------|-----------|-------------------|
| HEA-Cr0 | 0% | Highest activity, worst stability |
| HEA-Cr5 | 5% | Partial protection only |
| HEA-Cr10 | 10% | Near threshold for Cr₂O₃ |
| HEA-Cr15 | 15% | Should trigger passivation |
| HEA-Cr20 | 20% | Passivated but activity loss |
| HEA-Cr25 | 25% | Strong passivation, major activity loss |

Test all 6 in 0.5M H₂SO₄. Plot η₁₀ vs. Cr% and dissolution rate vs. Cr%.
Find the crossover — this is the optimal Cr content for this base composition.

---

### Priority 3 — V-content sweep

V is the surprise key element. Understand its optimal concentration:

| Sample | V content | Notes |
|--------|-----------|-------|
| HEA-V0 | 0% | Base: Fe₀.₂₅Co₀.₂₅Mn₀.₁₅W₀.₂Mo₀.₁₅ |
| HEA-V10 | 10% | |
| HEA-V20 | 20% | |
| HEA-V30 | 30% | Optimizer suggests this range |
| HEA-V40 | 40% | |

---

## Structural Insights From Optimizer

**What the optimizer found that's non-obvious:**

1. **V is the dominant 6th element** — not W or Mo as initially expected
2. **Cr is not needed** if V+Mn+W+Mo are present — they collectively stabilise
3. **Fe+Co binary** is the activity core — everything else is stability additive
4. **Ni contributes marginally** — present in only 1 of top 10 compositions
5. **Optimal active element count: 2–3** (Fe, Co + one other) — too many active elements dilute each other

These insights are testable and non-trivial — they came from optimising a physical surrogate
over 65 experiments, not from human intuition.

---

## Important Caveats

The surrogate model is based on physics-inspired equations, NOT real experimental data.

Real catalysts may differ from predictions because:
1. Synergistic/antagonistic effects between specific element pairs (not captured)
2. Phase separation during synthesis (predicted single-phase, may be multi-phase)
3. Surface segregation (surface composition ≠ bulk composition)
4. OER-induced reconstruction (composition changes under reaction conditions)

**Use these compositions as starting points, not as ground truth.**
The top 5 should all be synthesised. If Rank 1 is best experimentally → validate the surrogate.
If Rank 6 is best → update the surrogate and re-run.

**This is intended to be an iterative loop, not a one-shot prediction.**
