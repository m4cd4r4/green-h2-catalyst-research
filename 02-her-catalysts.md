# 02 — HER Catalysts: Earth-Abundant Candidates

## Overview

The Hydrogen Evolution Reaction is the easier half of the water-splitting problem. Several
earth-abundant catalyst classes now approach Pt performance in alkaline conditions. Acid
stability remains the primary gap.

**Reference:** Pt in 0.5M H₂SO₄: η₁₀ ≈ 30–50 mV, Tafel slope ~30 mV/dec

---

## Class 1: Transition Metal Phosphides

The most studied and highest-performing class of earth-abundant HER catalysts.

### CoP

| Property | Value |
|----------|-------|
| η₁₀ (acid) | 67–100 mV |
| η₁₀ (alkaline) | 100–150 mV |
| Tafel slope | 50–70 mV/dec |
| Stability | 20–50h demonstrated |
| Active sites | Both Co and P sites |
| Mechanism | P acts as H-acceptor, Co as hydride donor |

**Best synthesis route:**
1. Hydrothermal synthesis of Co(OH)₂ precursor on substrate
2. Phosphidation at 300–400°C in PH₃/Ar or with sodium hypophosphite
3. Key: nanostructuring (nanowires, nanosheets) maximizes active area

**Key papers to investigate:**
- CoP nanoarrays on carbon cloth (avoids binder resistance)
- CoP with N-doped carbon shell (improved acid stability)
- Janus CoP structures with asymmetric surfaces

**Open questions:**
- True active site under reaction conditions (CoP or surface-reconstructed CoO_x?)
- Long-term P leaching mechanism
- Can F-doping improve acid stability?

---

### Ni₂P

| Property | Value |
|----------|-------|
| η₁₀ (acid) | 100–140 mV |
| η₁₀ (alkaline) | 80–130 mV |
| Tafel slope | 46–65 mV/dec |
| Stability | Good in alkaline (100h+), poor in acid |
| Analogy | Hydrogenase enzyme active site (Fe₂S cluster) |

**Notes:** Ni₂P was the breakthrough paper (Popczun 2013, JACS) that launched the phosphide field.
Strongly prefers alkaline conditions. High activity attributed to both Ni (hydride) and P (proton relay).

**Promising modifications:**
- Ni₂P/MoS₂ heterostructures — synergistic active sites
- Fe-doped Ni₂P — improves OER simultaneously
- Ni₂P with phosphate surface — self-passivation reduces corrosion

---

### FeP

| Property | Value |
|----------|-------|
| η₁₀ (acid) | 120–180 mV |
| η₁₀ (alkaline) | 100–150 mV |
| Tafel slope | 38–65 mV/dec |
| Earth abundance | Very high — Fe is #4 in Earth's crust |
| Key challenge | Phase control (FeP vs Fe₂P vs Fe₃P) |

**Why it matters:** Iron is among the cheapest transition metals. FeP approaches CoP performance
but Fe is ~100× cheaper than Co.

---

### MoP

| Property | Value |
|----------|-------|
| η₁₀ (acid) | 90–130 mV |
| η₁₀ (alkaline) | 100–140 mV |
| Tafel slope | 45–55 mV/dec |
| Unique feature | High metallic conductivity |

**Notes:** Mo is relatively expensive but far cheaper than Pt. MoP has excellent electronic conductivity
(metallic), which improves charge transfer. Good candidate for carbon-free electrode design.

---

### WP / W₂P

| Property | Value |
|----------|-------|
| η₁₀ (acid) | 120–160 mV |
| η₁₀ (alkaline) | 110–150 mV |
| Stability | Among best non-PGM in acid |
| Cost | W is expensive but not PGM-class |

**Notes:** W-based phosphides show notably better acid stability than Co or Ni phosphides.
Potential for PEM applications if activity can be improved.

---

## Class 2: Transition Metal Sulfides

### MoS₂ (Molybdenum Disulfide)

| Property | Value |
|----------|-------|
| η₁₀ (acid, engineered) | 100–200 mV |
| η₁₀ (bare basal plane) | >300 mV (inactive) |
| Tafel slope (edge-rich) | 40–60 mV/dec |
| Key insight | Edge sites active, basal plane inactive |
| 2008 breakthrough | Jaramillo et al., Science — edge site activity proven |

**Engineering strategies to maximize active sites:**
1. **Vertical alignment** — edges exposed to electrolyte
2. **Single-layer exfoliation** — maximizes edge-to-area ratio
3. **Defect engineering** — S vacancies activate basal plane
4. **Metallic 1T phase** — conductive, activates basal plane
5. **Strain engineering** — lattice strain activates basal plane sites

**1T-MoS₂ is particularly promising:**
- Metallic conductivity vs. semiconducting 2H phase
- Basal plane becomes active
- η₁₀ as low as 130 mV reported
- Challenge: 1T phase is metastable, reverts to 2H on heating

**Dopants that improve performance:**
- Co-doped: Co substitutes Mo, weakens Mo-S bond optimally
- Ni-doped: similar effect, both Co and Ni at ~1–5% optimal
- Fe-doped: activates S sites differently

**Open questions:**
- Can basal plane ever truly match edge site activity?
- What is the mechanism of 1T→2H conversion and can it be prevented?
- Role of amorphous MoS_x vs crystalline phases

---

### NiS₂ / Ni₃S₂

| Property | Value |
|----------|-------|
| η₁₀ (alkaline) | 150–230 mV |
| Tafel slope | 60–90 mV/dec |
| Advantage | Self-supported on Ni foam (no binder) |

**Notes:** Ni sulfides are commonly grown directly on Ni foam substrates via hydrothermal
sulfidation, creating binder-free electrodes with excellent adhesion and conductivity.

---

### CoS₂ / Co₉S₈

| Property | Value |
|----------|-------|
| η₁₀ (acid) | 145–190 mV |
| η₁₀ (alkaline) | 130–180 mV |
| Tafel slope | 51–93 mV/dec |

---

### FeS₂ (Pyrite)

| Property | Value |
|----------|-------|
| η₁₀ (alkaline) | 170–250 mV |
| Advantage | Extremely cheap, naturally abundant |
| Challenge | Lower activity, poor acid stability |

**Notes:** Pyrite is naturally occurring and essentially free. Even at 250 mV overpotential,
its cost advantage could be decisive for large-scale applications where capital cost dominates.

---

## Class 3: Transition Metal Carbides

### Mo₂C

| Property | Value |
|----------|-------|
| η₁₀ (acid) | 90–150 mV |
| η₁₀ (alkaline) | 100–160 mV |
| Tafel slope | 55–70 mV/dec |
| Key property | Pt-like d-band density of states |
| Acid stability | Good — carbides more stable than phosphides/sulfides |

**Why it matters:** Mo₂C has electronic structure resembling Pt due to C modifying Mo's d-band.
Its acid stability is among the best of any non-PGM, making it a candidate for PEM.

**Synthesis:**
- High-temperature carburization of MoO₃ in CH₄/H₂
- Temperature-programmed reduction (TPR) route
- Nanostructuring key: Mo₂C@carbon core-shell improves stability

---

### WC (Tungsten Carbide)

| Property | Value |
|----------|-------|
| η₁₀ (acid) | 100–170 mV |
| Acid stability | Excellent |
| Electrocatalysis analogy | "Platinum substitute" — long recognized (Levy 1973) |
| Challenge | Low surface area in bulk form |

**Notes:** WC was identified as Pt-like 50 years ago. Key challenge: synthesizing high-surface-area
WC at low temperature (high-T synthesis gives low-SA). Recent nanostructured WC approaches
η < 150 mV.

---

### Mo₂C–MXene Composites

MXene (Ti₃C₂) + Mo₂C gives:
- High conductivity from MXene backbone
- Active Mo₂C sites
- η₁₀ as low as 76 mV reported in acid

---

## Class 4: Transition Metal Nitrides

### Mo₂N

| Property | Value |
|----------|-------|
| η₁₀ (acid) | 140–200 mV |
| Stability | Good — nitrides more corrosion resistant |
| Conductivity | High (metallic) |

---

### Ni₃N

| Property | Value |
|----------|-------|
| η₁₀ (alkaline) | 80–150 mV |
| Notes | Excellent water adsorption |

---

### Co-Mo-N / Ni-Mo-N

Bimetallic nitrides synergize the individual metals:
- η₁₀ as low as 67 mV in alkaline reported for Ni-Mo-N nanosheets
- One of the best alkaline HER performers among earth-abundant materials

---

## Class 5: Metal Alloys & Intermetallics

### NiMo Alloys (Industrial Standard)

| Property | Value |
|----------|-------|
| η₁₀ (alkaline) | 50–100 mV |
| Stability | Excellent (industrially deployed) |
| Maturity | Used in commercial alkaline electrolyzers |
| Tafel slope | 30–45 mV/dec |

**Notes:** NiMo is the de facto industrial non-PGM HER catalyst. It's not "new chemistry"
but it works and it's deployed at scale. All new candidates should benchmark against NiMo,
not just against Pt.

**Derivatives worth exploring:**
- NiMoFe — Fe improves OER simultaneously
- NiMoP — phosphide formation under reaction conditions
- NiMoCo — Co synergizes with Ni for water dissociation

---

### CoMo

| Property | Value |
|----------|-------|
| η₁₀ (alkaline) | 70–120 mV |
| Notes | Intermediate between NiMo and pure Co performance |

---

### FeNi Intermetallics (Ordered Phases)

Ordered intermetallics have well-defined, reproducible surface terminations:
- Fe₃Ni, FeNi, FeNi₃ phases
- Predictable active site geometry
- Better than disordered alloys for mechanistic understanding

---

## Class 6: Single-Atom Catalysts (SACs)

The most atom-efficient approach — every metal atom is accessible and active.

### Mo SAC on N-doped Carbon (Mo@NC)

| Property | Value |
|----------|-------|
| η₁₀ (acid) | 75–130 mV |
| TOF | 10–100× higher than nanoparticles |
| Loading | 0.1–2 wt% Mo (vs. 20–40 wt% for NPs) |
| Coordination | Mo-N₄, Mo-N₃C₁ sites |

**Synthesis:**
- Pyrolysis of Mo-containing MOF or polymer at 800–1000°C in N₂/Ar
- Atomic trapping on defective graphene

---

### Co SAC on NC

| Property | Value |
|----------|-------|
| η₁₀ (acid) | 100–160 mV |
| Key: | Co-N₄ vs Co-N₂C₂ — coordination matters |
| Mechanism | Side-on H₂ binding at Co-N₄ sites |

---

### Ni SAC on NC

| Property | Value |
|----------|-------|
| η₁₀ (alkaline) | 80–150 mV |
| Notes | Ni SAC particularly good in alkaline |

---

### Fe SAC on NC

| Property | Value |
|----------|-------|
| η₁₀ (alkaline) | 100–200 mV |
| Challenge | Fe tends to agglomerate during synthesis |

---

**SAC Challenges:**
1. Scale-up — maintaining atomically dispersed sites at high loading is difficult
2. Stability — sintering during extended operation
3. Confirmation — proving single-atom nature requires HAADF-STEM (expensive)
4. Reproducibility — synthesis very sensitive to temperature, atmosphere

---

## Class 7: MXenes

2D transition metal carbides/nitrides — Ti₃C₂Tₓ is most studied.

| Property | Value |
|----------|-------|
| η₁₀ (acid, functionalized) | 120–200 mV |
| Key property | Extremely high electronic conductivity |
| Role | Usually as support/conductive backbone |
| Functionalization | -OH, -F, -O terminations — active or passive |

**Best use:** MXenes as conductive supports for Mo₂C, CoP, or NiP — rather than as
standalone catalysts.

---

## Class 8: Carbon-Based Heteroatom-Doped Materials

### N,P-co-doped Carbon

| Property | Value |
|----------|-------|
| η₁₀ (alkaline) | 200–350 mV |
| Advantage | Metal-free — simplest possible system |
| Active sites | Pyridinic-N, graphitic-N, P-sites |
| Stability | Excellent (carbon) |

**Notes:** Cannot compete with metal-based catalysts on activity, but the stability and
cost advantages make them worth studying for ultra-long-duration applications.

---

## Comparative Summary Table

| Catalyst | Electrolyte | η₁₀ (mV) | Tafel (mV/dec) | Acid Stable? | Cost | Maturity |
|----------|-------------|-----------|-----------------|--------------|------|----------|
| Pt | Both | 30–50 | 30 | Yes | $$$$$ | Deployed |
| NiMo alloy | Alkaline | 50–100 | 30–45 | No | $ | Deployed |
| CoP | Both | 67–150 | 50–70 | Moderate | $$ | Lab |
| Ni₂P | Alkaline | 80–130 | 46–65 | No | $ | Lab |
| MoP | Both | 90–140 | 45–55 | Moderate | $$ | Lab |
| WP | Acid | 120–160 | 45–65 | Good | $$$ | Lab |
| Mo₂C | Both | 90–150 | 55–70 | Good | $$ | Lab |
| WC | Acid | 100–170 | 50–80 | Good | $$$ | Lab |
| 1T-MoS₂ | Acid | 130–200 | 40–60 | Moderate | $ | Lab |
| Ni-Mo-N | Alkaline | 67–150 | 35–60 | No | $ | Lab |
| Mo SAC@NC | Acid | 75–130 | 30–55 | Good | $$ | Lab |
| NiS₂ (foam) | Alkaline | 150–230 | 60–90 | No | $ | Lab |
| FeP | Both | 120–180 | 38–65 | Moderate | $ | Lab |
| FeS₂ (pyrite) | Alkaline | 170–250 | 70–100 | No | $ | Lab |

---

## Most Promising Directions (Synthesis Summary)

**For AEM electrolyzers (alkaline chemistry, membrane architecture):**
→ NiMoN or Ni₂P — best activity, acceptable stability

**For PEM electrolyzers (acid, requires stability):**
→ Mo₂C@NC core-shell OR Mo SAC@NC — best acid stability, approaching competitive activity

**For cost-first applications (large-scale AEL):**
→ FeP on carbon cloth OR FeS₂ — cheapest materials, adequate performance

**For mechanistic understanding:**
→ Ordered FeNi intermetallics OR Co SAC@NC — well-defined surfaces, reproducible
