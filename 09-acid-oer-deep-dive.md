# 09 — The Acid OER Gap: The Most Important Unsolved Problem in Electrochemistry

## Why This Document Exists

Green hydrogen at scale requires PEM electrolyzers. PEM electrolyzers require acid-stable
OER catalysts. The only acid-stable OER catalyst that works at industrial conditions is IrO₂.
Global iridium production is ~7 tonnes/year. A hydrogen economy needs thousands of tonnes.

**This is not a materials science problem. It is a civilization-scale constraint.**

This document is a comprehensive analysis of every known approach to earth-abundant acid OER,
why each has failed, what the failure modes reveal, and where the most likely breakthroughs lie.

---

## Part 1: Why Acid OER Is Uniquely Difficult

### 1.1 The Dual Requirement

Acid OER requires a catalyst that simultaneously:

1. **Binds oxygen intermediates with just the right strength** (activity requirement)
2. **Survives highly oxidizing potentials (>1.5 V vs RHE) in strongly acidic media** (stability requirement)

These requirements are deeply anticorrelated:
- Most active OER surfaces have high-valent metal oxide surfaces (Fe⁴⁺, Co⁴⁺, Ni⁴⁺)
- High-valent metals are thermodynamically unstable in acid — they dissolve
- More active = more oxidized = more soluble

This is not a synthesis challenge. It is a thermodynamic trap.

### 1.2 The Pourbaix Diagram Tells the Story

The Pourbaix diagram (pH vs. potential) shows the stable phases of each element:

| Element | Stable oxide phase | Dissolves above | Notes |
|---------|-------------------|-----------------|-------|
| Ir | IrO₂ | ~2.0 V | Exceptionally stable |
| Ru | RuO₂ | ~1.6 V | Dissolves during OER (RuO₄) |
| Mn | MnO₂ | ~1.5 V in acid | Disproportionates |
| Fe | FeOOH | <0.5 V in acid | Dissolves rapidly |
| Co | CoO/Co₃O₄ | <0.8 V in acid | Dissolves during OER |
| Ni | NiO/NiOOH | <0.5 V in acid | Dissolves rapidly |
| Cr | Cr₂O₃ | >2.0 V | Stable — but not OER active |
| Ti | TiO₂ | >2.5 V | Very stable — completely inactive |
| Ta | Ta₂O₅ | >3.0 V | Most stable — completely inactive |
| Sn | SnO₂ | >2.0 V | Stable — low activity |

**The pattern is clear:** Elements with large stability windows (Cr, Ti, Ta, Sn) are not OER active.
Elements with OER activity (Mn, Fe, Co, Ni) dissolve under OER conditions in acid.
Ir is the only exception where stability and activity coexist.

### 1.3 Why IrO₂ Works (And What It Tells Us)

IrO₂ has three properties that coexist uniquely:

1. **Rutile crystal structure** — forms compact, slow-dissolving oxide
2. **Ir⁴⁺/Ir⁵⁺ redox** — accessible at OER potentials without over-oxidizing to soluble species
3. **Strong Ir-O covalency** — high bond dissociation energy prevents surface dissolution

Key insight: The Ir-O bond is strong enough to resist dissolution but not so strong that
O-intermediates bind irreversibly. This is the Goldilocks zone.

**What we need:** An earth-abundant metal with Ir-like Ir-O bond strength at OER potentials.
The periodic table doesn't obviously offer this — which is why the problem is hard.

---

## Part 2: Every Approach That Has Been Tried — And Why Each Fails

### 2.1 MnO₂ — The Most Explored Earth-Abundant Acid OER Catalyst

**Why it's promising:**
- Mn is the only earth-abundant transition metal with a stability window that overlaps acid OER
- Mn⁴⁺/Mn³⁺ redox is accessible at relevant potentials
- PSII uses Mn for water oxidation — biological precedent

**Why it fails:**
- MnO₂ undergoes disproportionation: 2Mn³⁺ → Mn²⁺ + Mn⁴⁺
  - Mn³⁺ is the key intermediate — but it's unstable in acid
  - Mn³⁺ dissolved = activity loss
- Structural collapse from repeated Mn³⁺/Mn⁴⁺ cycling
- Best reported stability: ~20h at 1 mA/cm² in 0.5M H₂SO₄ (commercial target: 50,000h at 1000 mA/cm²)

**What has been tried:**
| Modification | Effect on activity | Effect on stability | Net result |
|-------------|-------------------|--------------------|-----------|
| Ca doping | Slight improvement | Minor improvement | Net positive, still far short |
| Ru doping (1–10%) | Large improvement | Moderate improvement | Best MnO₂ result |
| Cr doping | Minor | Minor improvement | Net positive |
| Crystalline β-MnO₂ | Moderate | Better than birnessite | Less active |
| Amorphous MnOₓ | Better than crystalline | Worse | Tradeoff |
| Au support | Better | Minor | Cost negates benefit |
| TiO₂ support | Minor | Better | Interesting |
| Epitaxial on rutile IrO₂ | Large | Better | Uses Ir, misses the point |

**Most important result:** 3% Ru in MnO₂ gives η₁₀ ≈ 320 mV and ~50h stability.
The Ru anchors Mn³⁺ against dissolution and improves charge transfer.
This is the best starting point for MnO₂ development.

**Open mechanistic question:** Does Mn³⁺ disproportionation happen in the bulk or only at the surface?
If bulk, it can't be suppressed. If surface, it can be capped. This is unknown.

---

### 2.2 Co-Based Catalysts — Why They Fail in Acid

CoO_x catalysts show excellent alkaline OER but dissolve catastrophically in acid:
- At 1.5 V vs RHE, pH 0: Co dissolution rate ~10⁻⁷ mol/cm²/s
- Translates to complete catalyst loss in <1h at 10 mA/cm²

**Why Co dissolves:** Co³⁺/Co⁴⁺ oxides are thermodynamically unstable in acid at OER potentials.
The Pourbaix diagram shows Co²⁺(aq) as the stable phase, not CoO₂.

**Approaches tried:**
- **CoP** — converts to cobalt phosphate (Co₃(PO₄)₂) which is more stable, η ≈ 350–450 mV in acid, still dissolves
- **CoS₂** — converts to sulfate, similar issue
- **Co₃O₄ + Cr** — Cr₂O₃ partial protection, η ≈ 400 mV, marginal stability
- **Single-atom Co on carbon** — dissolution rate lower, activity marginal
- **CoFe alloy** — Fe accelerates dissolution further

**Prognosis:** Co-based acid OER is unlikely to succeed. Thermodynamic dissolution is too severe.

---

### 2.3 Ni-Based Catalysts — Similar Story

NiOOH is the active alkaline OER phase. In acid:
- Ni²⁺ dissolution: thermodynamically favored below ~0.1 V vs. RHE
- At OER potentials (1.4–1.8 V), Ni dissolves extremely rapidly
- Only approach showing any promise: Ni₁₋ₓCrₓO passivation layers

**NiCrOₓ approach:**
- Cr₂O₃ surface passivation reduces Ni dissolution by 10–50×
- But Cr₂O₃ blocks OER sites → massive activity loss
- Requires precise Cr gradient: Cr-rich surface, Ni-rich subsurface
- Epitaxial NiCrOₓ thin films show promise but not manufacturable

---

### 2.4 Fe-Based Catalysts — Hopeless in Acid

Iron dissolves instantaneously in acid above 0 V vs RHE. There is no approach to Fe-based
acid OER. Fe is best used as a dopant in more stable matrices (Mn, Ir).

---

### 2.5 Protective Overlay Approach

**Concept:** Put a thin, stable, porous layer over an active but unstable catalyst.
The overlay blocks dissolution while allowing water/OH access.

| Overlay material | Properties | Challenge |
|-----------------|------------|-----------|
| TiO₂ (2–5 nm) | Very stable, insulating | Blocks charge transfer |
| SnO₂ (2–5 nm) | Stable, semi-conducting | Some conductivity loss |
| Ta₂O₅ (2–5 nm) | Most stable oxide | Insulating, blocks sites |
| Cr₂O₃ (1–2 nm) | Self-healing | Blocks too many sites |
| Carbon (graphene) | Stable in some conditions | Burns above 1.0 V in acid |
| TaOₓ/IrOₓ mixed | Stable, semi-active | Contains Ir |

**Best result:** SnO₂-coated NiCoFe — η₁₀ ≈ 340 mV in acid, ~50h stability.
SnO₂ is conducting enough to pass current while partially protecting the surface.

**Key insight from overlay work:** The challenge is not just stopping dissolution —
it's maintaining ion/charge transport pathways through the protective layer.
Any layer thick enough to stop dissolution is usually too thick to conduct current.

**The thickness sweet spot:** ~1–3 nm is where protection and conductivity coexist.
At this scale, atomic layer deposition (ALD) is the only reliable synthesis method.

---

### 2.6 High-Entropy Alloy/Oxide Approach — Most Promising

**Concept:** In a 5–7 element alloy or oxide, dissolution of any single element is
thermodynamically suppressed by the high configurational entropy.

**Thermodynamic basis:**
```
ΔG_dissolution = ΔG_pure - TΔS_mixing

For HEA: ΔS_mixing ≈ R·ln(n) per atom, where n = number of elements
At n=5: ΔS_mixing ≈ 1.6R ≈ 13 J/mol/K
At 300K: TΔS ≈ 4 kJ/mol

This stabilizes by ~4–10 kJ/mol relative to pure elements
```

This is modest but real — it reduces dissolution rates by approximately 5–20× at the same potential.

**Best HEA results for acid OER:**
- FeCoNiCrMn oxide: η₁₀ ≈ 270 mV (alkaline), 380 mV (acid), ~30h stability
- FeCoNiCr (Cr-dominant): η₁₀ ≈ 350–420 mV (acid), ~30h — best acid non-PGM
- IrCoNiCrFe (trace Ir): η₁₀ ≈ 280 mV (acid), >100h — uses Ir but 95% less

**Why HEA is promising:**
1. Compositional space is vast (>10⁶ combinations) — AI can search it efficiently
2. Cr provides structural stability without being the active site
3. Multiple elements provide "frustrated" dissolution — dissolution of one blocked by presence of others
4. Each element can play a functional role (Fe/Co = active, Cr = stable, Ni = structural, Mn = OER-active)

**The FeCoNiCr system — what we know:**

At >15% Cr: forms continuous Cr₂O₃ passivation (like stainless steel)
- Protects against acid dissolution
- Also blocks ~40% of OER active sites
- Optimal Cr: 10–20% (balance stability vs. activity blockage)

At 10–15% Fe: maximum OER activity contribution
At 10–20% Co: synergizes with Fe for O-intermediate binding
At 10–20% Ni: structural role, slight activity contribution

**Unexplored combinations:**
- Adding Mo: Mo forms stable MoO₃ in specific pH/potential window
- Adding V: V₂O₅ partially stable in acid, V⁵⁺/V⁴⁺ OER active
- Adding W: WO₃ acid stable, electrochromic, potential OER activity
- Adding Ce: Ce³⁺/Ce⁴⁺ redox at high potential, relatively stable oxide

---

### 2.7 The PSII Inspiration — Mn₄CaO₅ Cluster

Nature's solution to acid water oxidation has been running for 2.7 billion years.
The Mn₄CaO₅ oxygen-evolving complex (OEC) in Photosystem II achieves:
- Near-zero overpotential under biological conditions
- Self-repairing (photoassembly)
- Operating in slightly acidic thylakoid lumen (pH ≈ 5–6)

**Structure:** A Mn₄ cubane-like cluster with a dangling Mn, bridged by oxo ligands,
with Ca²⁺ essential for activity (Ca removal → 80% activity loss).

**Lessons for synthetic catalysts:**

| PSII feature | Synthetic analog | Status |
|-------------|-----------------|--------|
| Mn₄ cubane structure | Mn₄O₄ molecular clusters | Synthesized, less active |
| Ca²⁺ cofactor | Ca-doped MnO₂ | Tried, modest improvement |
| Protein scaffold (orientation) | MOF scaffold | Early work |
| Self-healing | Electrodeposited MnOₓ | Partially achieved |
| Sequential 4-electron PCET | Molecular Mn complexes | Demonstrated, <10 TOF |
| pH 5–6 tolerance | pH stability | MnO₂ variants approach |

**The Ca mystery:** Ca²⁺ is redox-inactive but essential. Current understanding:
- Ca²⁺ positions the substrate water molecule correctly
- Ca²⁺ modulates Mn-O bond strength through Lewis acid effect
- Ca²⁺ lowers the barrier for O-O bond formation

**Synthetic hypothesis:** Ca₀.₁₅Mn₀.₈₅O_x with precisely 1 Ca per 5–6 Mn (mimicking ratio
in PSII) should be more stable than Ca₀.₅Mn₀.₅O_x because coordination matches PSII geometry.
**This has not been tested.**

---

## Part 3: The Most Promising Paths Forward

### 3.1 Path A: Optimized Mn-Based System (Near-term, 2–4 years)

**Target:** η₁₀ < 400 mV in 0.5M H₂SO₄, stability > 500h at 50 mA/cm²

**Strategy:**
1. Start with defect-rich amorphous MnOₓ (best performance/stability baseline)
2. Ca doping at PSII-inspired ratios (1 Ca per 5–6 Mn)
3. 1–3% Ru doping to anchor Mn³⁺ (proven approach)
4. SnO₂ ALD overlayer (1.5–2.0 nm, proven protection)
5. Ti mesh substrate (replaces carbon, no corrosion)

**Rational synthesis targets:**
- Ca₀.₁₅Ru₀.₀₃Mn₀.₈₂O_x — composition inspired by PSII + Ru stabilization
- Deposit by electrodeposition for conformal film
- ALD SnO₂ (1.5 nm) from SnCl₄ + H₂O at 120°C
- Test in 0.5M H₂SO₄ with inline ICP-MS (Mn, Ca, Ru, Sn)

**Expected performance:** η₁₀ ≈ 350–400 mV, stability ≈ 200–500h
**Why it might work:** Ru pins Mn³⁺, Ca stabilizes cubane-like structure, SnO₂ catches anything that dissolves

---

### 3.2 Path B: Optimized HEA System (Medium-term, 3–6 years)

**Target:** η₁₀ < 350 mV in 0.5M H₂SO₄, stability > 1000h at 100 mA/cm²

**AI-guided strategy:**
1. Bayesian optimization over FeCoNiCrMn + V/W/Mo space
2. Multi-objective: minimize η₁₀ AND dissolution rate simultaneously
3. Synthesis via magnetron sputtering (best compositional control for HEA)
4. Start with equimolar 5-element, branch to Cr-heavy (stability) and Fe-heavy (activity)
5. Add electrochemical in-situ XRF for real-time dissolution tracking

**Most promising composition (reasoned estimate):**
Fe₀.₁₅Co₀.₁₅Ni₀.₁₀Cr₀.₂₅Mn₀.₁₅W₀.₁₀Mo₀.₁₀O_x
- Cr₀.₂₅ — sufficient for continuous Cr₂O₃ passivation
- Fe₀.₁₅ + Co₀.₁₅ — primary OER active sites
- W₀.₁₀ + Mo₀.₁₀ — stable oxides, secondary activity
- Ni₀.₁₀ + Mn₀.₁₅ — structural + OER contribution

**This is an untested composition formulated from first principles here.**

---

### 3.3 Path C: Breaking Scaling Relations via Dual-Site Design (Long-term, 5–10 years)

**The fundamental problem:** Even if stability is solved, single-site catalysts following AEM
cannot beat ~370 mV overpotential due to scaling relations.

**Breaking scaling relations — proven strategies:**

**Dual-site mechanism:**
- OH* forms on Site A, OOH* forms across Site A + Site B
- O-O bond forms between two adjacent bound O atoms rather than OOH* pathway
- ΔG(OOH*) decoupled from ΔG(OH*)
- Demonstrated computationally, not yet experimentally at low overpotential in acid

**Lattice oxygen mechanism (LOM):**
- Lattice O participates in O-O bond formation
- Bypasses OOH* entirely
- Demonstrated in Ni-based systems in alkaline (isotope labeling)
- In acid: LOM would require lattice O to be regenerated from water
- If achieved: theoretical minimum overpotential drops from 370 mV → 200 mV

**Electrostatic stabilization of OOH*:**
- OOH* is the weakest-binding and hardest-to-stabilize intermediate
- Placing a positively charged site adjacent to O* could lower OOH* energy
- Theoretical support: Lewis acid sites near OER metal can lower OOH* binding
- Experimental: surface phosphate groups improve OER on some systems

---

## Part 4: What a Breakthrough Would Look Like

A genuine acid OER breakthrough requires meeting ALL of:

| Criterion | Minimum | Transformative |
|-----------|---------|----------------|
| Overpotential η₁₀ | < 400 mV | < 300 mV |
| Current density stability | 100 mA/cm² | 1000 mA/cm² |
| Stability duration | 1000h | 10,000h |
| Voltage drift | < 50 mV | < 20 mV |
| Dissolution rate (ICP-MS) | < 10 ng/cm²/s | < 1 ng/cm²/s |
| Earth-abundant only | Yes | Yes |
| Scalable synthesis | Yes | Yes |
| Cost (estimated) | < $10/g | < $1/g |

**Currently, no material meets even the Minimum criteria for all criteria simultaneously.**

The closest contenders:
1. **FeCoNiCr HEA** — meets η₁₀ and has partial stability, not yet 1000h
2. **Ru-doped MnO₂** — close on activity, poor on stability
3. **SnO₂-protected NiCoFe** — meets partial stability, η₁₀ too high

---

## Part 5: Experimental Recommendations — Acid OER Priority

In descending priority order:

### Priority 1 (Do This First)
**Ca₀.₁₅Ru₀.₀₃Mn₀.₈₂O_x + SnO₂ ALD overlay**
- 2-week synthesis, 4-week testing
- Highest probability of beating current MnO₂ records
- Clean mechanism hypothesis (PSII-inspired)
- Testable with ICP-MS and operando Raman

### Priority 2
**FeCoNiCrW alloy vs. FeCoNiCrMo alloy (acid OER)**
- Tests W vs. Mo as the 6th element in HEA
- Sputtering deposition (compositionally precise)
- Compare to FeCoNiCr (no 6th element)

### Priority 3
**Systematic Cr content optimization in FeCoNiCrFe**
- Cr = 0, 5, 10, 15, 20, 25, 30%
- Find crossover: below X% Cr, too much dissolution; above X%, too many blocked sites
- Expectation: optimum at 15–20% Cr

### Priority 4
**ALD SnO₂ thickness study on NiCoFe**
- SnO₂ at 0, 0.5, 1.0, 1.5, 2.0, 3.0, 5.0 nm
- Find thickness where protection emerges (expected: ~1.2–1.5 nm)
- ECSA before/after to quantify site blocking

### Priority 5
**LOM detection in Cr-protected NiOOH**
- ¹⁸O₂ isotope labeling experiment
- If LOM active in acid: game-changing mechanism confirmation

---

## Part 6: The IrO₂ Minimization Strategy (Parallel Track)

While searching for earth-abundant acid OER catalysts, an important parallel strategy is
reducing Ir loading rather than eliminating it — this buys time for the pure replacement.

**Current state:** PEM OER: ~2 mg Ir/cm² of electrode
**Target:** < 0.05 mg Ir/cm² (40× reduction, within iridium supply constraints for large scale)

### Strategies for Ir Minimization

**1. Single-atom Ir on IrO₂ support**
- Most Ir in IrO₂ is bulk — only surface contributes to OER
- Dispersing Ir as single atoms on a stable support (SnO₂, TiO₂) → 10–30× fewer Ir atoms needed
- Reported: 0.1 mg Ir/cm², similar performance to 2 mg/cm² dense IrO₂

**2. IrO₂ + MnO₂ composite**
- 10% IrO₂ + 90% MnO₂ — Ir provides stability, Mn provides activity
- Reported: η₁₀ ≈ 280 mV, stability > 500h at 0.1 mg Ir/cm²
- This is the most practical near-term approach

**3. Core-shell: MnO₂ core, IrO₂ shell (1–2 nm)**
- Minimal Ir (0.01–0.05 mg/cm²) provides surface stability
- Mn core provides OER activity
- ALD synthesis of IrO₂ shell is proven

**4. Ir-doped HEA**
- 1–5% Ir in FeCoNiCr HEA
- Ir anchors the entire HEA surface against dissolution
- Ir loading: ~0.05–0.1 mg/cm² vs. 2 mg for pure IrO₂
- Excellent near-term approach: keeps Ir in the equation but reduces by 20–40×

---

## Summary: Research Priority Matrix for Acid OER

```
                    HIGH IMPACT
                        │
                        │  Ca-Mn-Ru-O_x    FeCoNiCrW HEA
                        │  (Path A)        (Path B AI-guided)
         LOW      ──────┼──────────────────────────────     HIGH
      TRACTABILITY      │                              TRACTABILITY
                        │  LOM in acid     Ir-doped HEA
                        │  (Path C)        (Ir minimization)
                        │
                    LOW IMPACT
```

**Best first experiment:** Ca₀.₁₅Ru₀.₀₃Mn₀.₈₂O_x — combines PSII structural inspiration
with proven Ru stabilization. Could establish a new record in MnO₂-based acid OER.

**Best AI experiment:** Bayesian optimization of FeCoNiCrMn + 2 optional elements,
targeting Pareto front of activity AND dissolution rate simultaneously.

**The prize:** First earth-abundant catalyst meeting 1000h stability at 100 mA/cm² in acid
OER will be one of the most cited electrochemistry papers of the decade.
