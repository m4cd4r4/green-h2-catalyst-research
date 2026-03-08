# 03 — OER Catalysts: Earth-Abundant Candidates

## Overview

The Oxygen Evolution Reaction is the bottleneck of water electrolysis. It involves a
4-electron/4-proton transfer — mechanistically complex, thermodynamically demanding, and
kinetically slow. IrO₂ remains the gold standard for PEM acid conditions.
In alkaline, earth-abundant options are genuinely competitive.

**References:**
- IrO₂ in 0.5M H₂SO₄: η₁₀ ≈ 250–320 mV, Tafel ≈ 40–60 mV/dec
- RuO₂ in 0.5M H₂SO₄: η₁₀ ≈ 200–280 mV (more active, less stable)
- IrO₂ in 1M KOH: η₁₀ ≈ 270–350 mV

---

## Class 1: Layered Double Hydroxides (LDH)

The most competitive alkaline OER class.

### NiFe LDH — The Benchmark Earth-Abundant Alkaline OER Catalyst

| Property | Value |
|----------|-------|
| η₁₀ (alkaline) | 230–280 mV |
| Tafel slope | 38–55 mV/dec |
| Stability | Good — 100h+ demonstrated |
| Fe content optimal | 15–25 mol% |
| Active site | Fe³⁺/Fe⁴⁺ redox couple |
| Ni role | Structural, electronic modulation |

**Why NiFe LDH is exceptional:**
- Ni and Fe form a lamellar hydroxide structure with excellent ion accessibility
- Fe is the genuine active site (proven by: dilute Fe in Ni matrix is active; pure NiLDH needs Fe impurities to activate)
- The Ni(OH)₂/NiOOH transition provides electron buffering
- Self-healing capability — can recover some lost performance

**Limitations:**
- Only works in alkaline — dissolves in acid
- Fe incorporation is tricky — too little → poor activity, too much → phase separation
- Long-term Fe dissolution and loss

**Modifications that improve NiFe LDH:**

| Modification | Effect |
|--------------|--------|
| V incorporation (NiFeV LDH) | Optimizes Fe oxidation state, η₁₀ down to 195 mV |
| Mo incorporation | Creates defects, improves conductivity |
| Defect engineering | Surface vacancies as additional active sites |
| Exfoliation to monolayer | Maximum site exposure |
| Carbon nanotube hybridization | Improves conductivity and stability |
| Phosphate treatment | Partial phosphidation improves charge transfer |

**Record performance (reported):** NiFeV LDH, η₁₀ = 195 mV in 1M KOH
(Treat with caution — many record claims don't reproduce)

---

### CoAl LDH

| Property | Value |
|----------|-------|
| η₁₀ (alkaline) | 290–360 mV |
| Notes | Al is redox-inactive but structure-directing |

---

### NiCo LDH

| Property | Value |
|----------|-------|
| η₁₀ (alkaline) | 270–320 mV |
| Notes | Both metals contribute to activity |

---

### NiCr LDH

| Property | Value |
|----------|-------|
| η₁₀ (alkaline) | 240–290 mV |
| Notes | Cr improves stability vs Fe |

---

## Class 2: Perovskites (ABO₃)

Structurally tunable oxides with remarkable activity potential.

### BSCF — Ba₀.₅Sr₀.₅Co₀.₈Fe₀.₂O₃₋δ

| Property | Value |
|----------|-------|
| η₁₀ (alkaline) | 230–270 mV |
| Tafel slope | 60–80 mV/dec |
| Key property | Highest mass activity of any perovskite |
| Discovery | Shao-Horn et al., Nature Chemistry 2011 |
| Challenge | Amorphizes under OER conditions |

**The BSCF paradox:** It's among the most active perovskites but transforms to amorphous
hydroxide/oxide during OER. The crystalline structure may just be a "pre-catalyst."
Understanding what the true active amorphous phase is may be more important than the
perovskite structure itself.

---

### LSCF — La₀.₆Sr₀.₄Co₀.₂Fe₀.₈O₃₋δ

| Property | Value |
|----------|-------|
| η₁₀ (alkaline) | 310–370 mV |
| Stability | Better than BSCF |
| Use case | SOEC anode (high temperature) |

---

### LaCoO₃ / LaFeO₃

| Property | Value |
|----------|-------|
| η₁₀ (alkaline) | 350–430 mV |
| Activity predictor | eg — occupancy of σ* antibonding orbital |
| Volcano peak | eg ≈ 1.2 |

**The eg framework (Shao-Horn group):**
OER activity correlates with eg electron occupancy — the ideal is ~1.0–1.2 electrons in
σ*-symmetry d orbitals. This predicts activity from electronic structure without DFT.

---

### Pr₀.₅Ba₀.₅CoO₃₋δ (PBC)

| Property | Value |
|----------|-------|
| η₁₀ (alkaline) | 220–260 mV |
| Notes | Among most active perovskites |
| Challenge | Pr and Ba are relatively expensive |

---

### Self-Reconstructing Perovskites

Key insight (2020s): Many perovskites exsolve active nanoparticles under OER conditions.
The real catalyst is Co/Fe/Ni metal nanoparticles on an oxide support — not the perovskite.

**Implications:**
- Design perovskites to exsolve optimal nanoparticle compositions
- Control exsolution particle size via A/B site stoichiometry
- This is a new design paradigm: "pre-catalyst engineering"

---

## Class 3: Spinels (AB₂O₄)

### NiCo₂O₄

| Property | Value |
|----------|-------|
| η₁₀ (alkaline) | 280–340 mV |
| Tafel slope | 60–80 mV/dec |
| Conductivity | High (semi-metallic) |
| Active sites | Both tetrahedral and octahedral sites |

**Synthesis:** Hydrothermal or urea hydrolysis, usually on Ni foam substrate.
Self-supported NiCo₂O₄ nanowire arrays are excellent — no binder, direct contact.

---

### CoFe₂O₄

| Property | Value |
|----------|-------|
| η₁₀ (alkaline) | 300–380 mV |
| Notes | Very cheap (Fe dominant), decent activity |

---

### CuCo₂O₄

| Property | Value |
|----------|-------|
| η₁₀ (alkaline) | 320–400 mV |
| Notes | Cu incorporation improves electron transfer |

---

### MnFe₂O₄

| Property | Value |
|----------|-------|
| η₁₀ (alkaline) | 330–420 mV |
| Notes | Ultra-cheap materials, moderate performance |

---

## Class 4: Metal Oxides / Oxyhydroxides

### NiOOH / β-Ni(OH)₂

| Property | Value |
|----------|-------|
| Notes | The ACTIVE phase in most Ni-based OER catalysts |
| Key insight | Most Ni catalysts convert to NiOOH during OER |
| Fe doping | Even trace Fe (from electrolyte impurities!) boosts activity 30× |

**Critical finding:** "Pure" Ni(OH)₂ electrodes in KOH are actually NiFeOOH because
commercial KOH contains Fe impurities. This contamination issue explains much of the
variability in literature — and also shows Fe is essential.

---

### FeOOH / Fe₂O₃

| Property | Value |
|----------|-------|
| η₁₀ (alkaline) | 400–500 mV |
| Notes | Poor standalone, excellent dopant |
| Insight | Fe activates neighboring Ni/Co sites — not active alone |

---

### Co₃O₄

| Property | Value |
|----------|-------|
| η₁₀ (alkaline) | 300–400 mV |
| Tafel slope | 60–70 mV/dec |
| Notes | Spinel structure, Co²⁺ in tet + Co³⁺ in oct sites |

**Engineering:** Co₃O₄ on graphene nanosheets, with Fe doping → competes with NiFe LDH.

---

### MnO₂ (Birnessite)

| Property | Value |
|----------|-------|
| η₁₀ (alkaline) | 350–500 mV |
| η₁₀ (acid) | 400–600 mV |
| Advantage | Mn is extremely cheap and abundant |
| Unique: | Only earth-abundant OER candidate with ANY acid activity |
| Stability in acid | Poor but better than most |

**Why MnO₂ matters despite moderate activity:**
- Mn is the best hope for acid OER (even IrO₂ replacement is being pursued via Mn)
- Birnessite structure has interlayer water — uniquely tolerant of electrolyte composition
- Natural water oxidation by MnOₓ clusters occurs in Photosystem II — biological proof of concept
- Ca-Mn cluster in PSII reaches η ≈ 0 mV — if we understood it, we'd win

**MnO₂ modifications:**
| Modification | Effect |
|--------------|--------|
| Ca incorporation | Mimics PSII Mn₄CaO₅ cluster |
| Ru doping (trace) | 10× activity improvement with <5% Ru |
| Defect-rich amorphous | Better than crystalline |
| Cr doping | Improved acid stability |

---

## Class 5: High-Entropy Alloy / Oxide Catalysts

### High-Entropy Oxides (HEOs) — FeCoNiCrMn-based

| Property | Value |
|----------|-------|
| η₁₀ (alkaline) | 240–300 mV |
| Key property | "Cocktail effect" — synergy of multiple elements |
| Stability | Good (multi-element dissolution is slow) |
| Reproducibility | Very challenging |

**Concept:** 5+ metals in a single phase, each at ≤20%. The enormous composition space
(>10⁶ possible combinations) makes HEOs an ideal target for AI/ML screening.

**Examples:**
- (FeCoNiCrMn)₃O₄ spinel: η₁₀ ≈ 270 mV
- (FeCoNiCuMn)₃O₄: η₁₀ ≈ 255 mV
- Amorphous HEO: sometimes outperforms crystalline

**AI opportunity:** Bayesian optimization of composition has found records here faster
than intuition-guided synthesis. This is a genuinely productive space for ML.

---

### High-Entropy Alloy Oxides for Acid OER

The holy grail: acid-stable, earth-abundant OER catalyst.

Promising: FeCoNiCr alloys that form a protective Cr₂O₃ layer (like stainless steel) while
maintaining active Fe/Co/Ni surface sites.

- Cr₂O₃ forms a self-healing protective oxide
- But Cr₂O₃ also blocks active sites — balance needed
- Early results: 350–450 mV in acid, modest stability
- **Active area of research with no clear winner yet**

---

## Class 6: MOF-Derived Catalysts

Metal-organic frameworks pyrolyzed at 700–1000°C give:
- Well-dispersed metal nodes → nanoparticles or SACs
- N-doped carbon matrix from organic linkers
- High surface area

### ZIF-67 (Co-zeolitic imidazolate) → Co@NC

| Property | Value |
|----------|-------|
| η₁₀ (alkaline) | 310–380 mV |
| Notes | Co NPs in N-doped carbon shell |

### MIL-53(Fe/Ni) → NiFe@NC

| Property | Value |
|----------|-------|
| η₁₀ (alkaline) | 260–310 mV |
| Notes | Compositionally tunable via MOF design |

**Advantage of MOF-derived approach:**
- Composition tunable at synthesis stage (swap metal nodes)
- Scale-up possible via wet chemistry
- N-doped carbon improves conductivity and provides additional sites

---

## Class 7: Phosphides and Sulfides (OER)

### NiFeP (phosphide)

| Property | Value |
|----------|-------|
| η₁₀ (alkaline) | 250–300 mV |
| Notes | Phosphides often reconstruct to active (oxy)hydroxides |
| True active phase | Surface NiFeOOH — phosphide is pre-catalyst |

**The "pre-catalyst" concept is crucial for phosphides and sulfides:**
Most non-oxide catalysts (phosphides, sulfides, nitrides) oxidize to hydroxide/oxide surfaces
during OER. The original material may just be a convenient precursor for in-situ formation
of the true active phase.

**Implication:** Design the metal composition for the final OOH/oxide surface it will become —
not the phosphide/sulfide itself.

---

### CoS₂ / Co-S

| Property | Value |
|----------|-------|
| η₁₀ (alkaline) | 300–380 mV |
| Notes | Reconstructs to CoOOH in situ |

---

## Class 8: Electrodeposited Amorphous Films

Often overlooked but practically important:

### Amorphous NiFe(O_xH_y)

| Property | Value |
|----------|-------|
| η₁₀ (alkaline) | 240–280 mV |
| Synthesis | Electrodeposition — extremely simple, scalable |
| Control | Film composition tuned by bath ratio |
| Advantage | Conformal coating on any substrate, no binder |

**Electrodeposition from NiSO₄/FeSO₄ bath is arguably the most practical OER approach:**
- Room temperature synthesis
- No furnace, no toxic precursors
- Substrate independent
- Activity competitive with hydrothermal routes

---

## OER Comparative Summary Table

| Catalyst | Electrolyte | η₁₀ (mV) | Tafel (mV/dec) | Acid Stable? | Cost | Notes |
|----------|-------------|-----------|-----------------|--------------|------|-------|
| IrO₂ | Acid | 250–320 | 40–60 | Excellent | $$$$$ | PEM gold standard |
| RuO₂ | Acid | 200–280 | 40–60 | Moderate | $$$$$ | Dissolves slowly |
| NiFe LDH | Alkaline | 230–280 | 38–55 | None | $ | Best earth-abundant |
| NiFeV LDH | Alkaline | 195–240 | 35–50 | None | $ | Record claim |
| BSCF perovskite | Alkaline | 230–270 | 60–80 | None | $$ | Amorphizes in use |
| NiCo₂O₄ | Alkaline | 280–340 | 60–80 | None | $ | Good conductivity |
| Co₃O₄ | Alkaline | 300–400 | 60–70 | None | $ | Well-studied |
| HEO (5-metal) | Alkaline | 240–300 | 45–70 | None | $$ | AI-optimizable |
| MnO₂ (birnessite) | Both | 350–500 | 70–100 | Poor | $ | Only acid option |
| NiFeP | Alkaline | 250–300 | 45–65 | None | $ | Pre-catalyst |
| FeCoNi HEA | Acid | 350–450 | 60–90 | Moderate | $$ | Best acid non-PGM |
| Amorphous NiFeO_xH_y | Alkaline | 240–280 | 40–60 | None | $ | Most practical |

---

## The Acid OER Gap — The Biggest Unsolved Problem

No earth-abundant material achieves practical performance AND stability in acid OER.

**What "acid stability" requires:**
- Dissolution current < 1 ng/cm²/s (metal into solution)
- Overpotential stable within 50 mV over 1000h at 100 mA/cm²
- No membrane contamination

**Current best candidates (none ready):**
1. **MnO₂ + Cr dopant** — modest activity, improving stability
2. **FeCoNiCr HEA** — Cr₂O₃ passivation + active surface
3. **Ir-doped MnO₂ (1–5% Ir)** — drastically reduces Ir use, maintains activity
4. **Ta₂O₅-coated active materials** — protective overlay (blocks some sites)
5. **Amorphous Mn-Co oxides** — recent promising results

**This is where a breakthrough would have maximum impact.**
