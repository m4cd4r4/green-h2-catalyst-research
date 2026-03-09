# 04 — Bifunctional Catalysts (HER + OER)

## Why Bifunctional Catalysts Matter

In reversible electrolyzers and regenerative fuel cells, the same electrode must sometimes
catalyze both HER and OER. Even in dedicated electrolyzers, a single bifunctional catalyst
can simplify manufacturing and reduce cost.

**Challenge:** HER and OER have opposite electronic requirements.
- HER: needs good H-binding, moderate M-H bond strength
- OER: needs good O-binding, tuned M-O bond strength
- These are often anticorrelated — volcano plots for each reaction pull in opposite directions

**Best approach:** Heterostructures where different domains handle different reactions.

---

## Top Bifunctional Catalyst Systems

### 1. NiFe LDH / CoP Heterostructure

| Property | Value |
|----------|-------|
| η₁₀ (HER, alkaline) | 100–140 mV |
| η₁₀ (OER, alkaline) | 240–280 mV |
| Cell voltage at 10 mA/cm² | ~1.56–1.68 V |
| Reference (two-electrode) | Commercial electrolyzers: ~1.8–2.0 V |
| Mechanism | CoP handles HER, NiFe LDH handles OER |
| Synergy | Intimate contact enables electron transfer |

**How to make it:**
1. Grow CoP nanowire array on Ni foam
2. Hydrothermal NiFe LDH on same substrate
3. Result: LDH nanosheets decorated with CoP nanoparticles
4. Both phases exposed to electrolyte, electrically connected

---

### 2. NiMoP / NiFeP Core-Shell

| Property | Value |
|----------|-------|
| η₁₀ (HER, alkaline) | 80–120 mV |
| η₁₀ (OER, alkaline) | 250–300 mV |
| Notes | P-rich shell promotes HER, oxide layer (formed in situ) promotes OER |

---

### 3. Fe₃N / NiFe₂O₄ Heterostructure

| Property | Value |
|----------|-------|
| η₁₀ (HER) | 90–140 mV |
| η₁₀ (OER) | 255–290 mV |
| Notes | N promotes HER, spinel oxide promotes OER |

---

### 4. Co-based MOF-Derived Bifunctional Catalysts

Pyrolysis of bimetallic MOFs (Co/Ni, Co/Fe) gives:
- Co nanoparticles in N-doped carbon: HER active
- Surface oxide layer: OER active
- Self-optimizing under cycling: each reaction drives surface restructuring in its favor

| Property | Value |
|----------|-------|
| η₁₀ (HER, alkaline) | 120–180 mV |
| η₁₀ (OER, alkaline) | 280–340 mV |
| Advantage | Single synthesis step, scalable |

---

### 5. NiCo₂S₄ / NiFe LDH

| Property | Value |
|----------|-------|
| η₁₀ (HER) | 130–170 mV |
| η₁₀ (OER) | 250–290 mV |
| Notes | Sulfide backbone for conductivity + LDH for OER |

---

### 6. Transition Metal Carbide / Oxide Composites

**Mo₂C / MoO₃:**
- Mo₂C handles HER (Pt-like)
- MoO₃ or MoS₂ handles OER
- η₁₀ HER: 100–150 mV, OER: 310–380 mV

---

## Full-Cell Performance Comparison

The real metric: **voltage at target current density in a two-electrode setup**

| System | Electrolyte | j (mA/cm²) | Cell Voltage (V) |
|--------|-------------|------------|------------------|
| Pt/IrO₂ (reference) | 1M KOH | 10 | 1.51–1.55 |
| NiFe LDH / CoP | 1M KOH | 10 | 1.56–1.68 |
| NiMoP / NiFe | 1M KOH | 10 | 1.58–1.70 |
| NiCo₂S₄ / NiFeLDH | 1M KOH | 10 | 1.60–1.72 |
| Commercial AEL | 30% KOH | 400 | 1.85–2.05 |

**Note:** Lab cell voltages at 10 mA/cm² are not directly comparable to commercial 400 mA/cm².
Industrial performance of these lab materials is typically much worse than lab numbers suggest.

---

## Design Principles for Bifunctional Heterostructures

1. **Phase separation but electronic contact** — distinct phases for each reaction, electrically coupled
2. **Interface engineering** — charge transfer at the interface is often where synergy occurs
3. **Self-optimization** — design materials that restructure to optimal surface during operation
4. **Stability matching** — both phases must survive each other's reaction conditions
5. **Avoid phase mixing** — too much mixing loses the specialized active sites

---

## The Self-Restructuring Paradigm

**Key insight (2022–2025):** Many of the "best" bifunctional catalysts are actually converting
to their active form in situ:
- Phosphides → phosphate/hydroxide surface during OER
- Sulfides → sulfate/hydroxide surface during OER
- The starting material is the "pre-catalyst"

**What this means for design:**
- Don't optimize the initial structure — optimize what it becomes
- Use in-situ XAS/Raman to track structural evolution during OER
- Design the metal composition for the final active hydroxide
- The phosphide/sulfide precursor is just a convenient synthesis handle

**Testable hypothesis:** Can we skip the precursor entirely by directly synthesizing the
in-situ-transformed phase (e.g., amorphous NiFeOOH doped with P)? Several papers suggest yes.
