# 05 — Failure Modes & Degradation Mechanisms

## Why Stability Is the Real Problem

Most catalyst papers report 10–50 hours of stability. Commercial electrolyzers need:
- **AEL:** 80,000–100,000 hours (>10 years)
- **PEM:** 50,000–80,000 hours
- **AEM:** 10,000–20,000 hours (current target, improving)

There is a **3–4 order of magnitude gap** between lab demonstration and commercial requirement.
Understanding failure modes is as important as discovering active materials.

---

## Failure Mode 1: Metal Dissolution / Leaching

### Mechanism
Anodic dissolution of transition metals under oxidizing conditions (OER) or cathodic
conditions (HER in acid after Tafel step).

**Key equations:**
```
M → Mⁿ⁺ + ne⁻   (anodic dissolution)
MO_x → Mⁿ⁺ + xH₂O  (oxide dissolution in acid)
```

### Severity by Element (acid OER, worst to best)

| Element | Dissolution rate | Notes |
|---------|-----------------|-------|
| Fe | Very high | Dissolves rapidly in acid above 1.0V |
| Co | High | Dissolves in acid at OER potentials |
| Ni | High | Dissolves, Ni²⁺ in acid |
| Mn | High | MnO₂ disproportionates to Mn²⁺ in acid |
| Mo | Moderate | Molybdate dissolution |
| W | Low–Moderate | Better than Mo |
| Cr | Low | Forms protective Cr₂O₃ layer |
| Ti | Very low | TiO₂ passive layer |
| Ir | Very low | IrO₂ is the best for a reason |

### Detection
- ICP-MS of electrolyte after testing (most sensitive)
- EQCM (electrochemical quartz crystal microbalance) — real-time mass loss
- Post-mortem XPS/EDX — bulk composition change

### Mitigation Strategies
1. **Cr/W protective overlayers** — form self-healing oxide barriers
2. **Carbon encapsulation** — graphene shells slow dissolution
3. **High-entropy alloying** — thermodynamically suppresses dissolution
4. **Alkaline preference** — stay in alkaline where oxides are stable
5. **Potential window limitation** — avoid the worst dissolution potentials
6. **Self-healing materials** — replenish dissolved species from bulk reservoir

---

## Failure Mode 2: Surface Reconstruction / Phase Transformation

### Mechanism
Catalyst transforms from initial phase (phosphide, sulfide, carbide) to oxide/hydroxide
during electrochemical operation. This is not always bad — sometimes the transformed phase
is more active.

### Cases where reconstruction is HARMFUL

| Catalyst | Initial phase | Reconstructed to | Effect |
|----------|--------------|------------------|--------|
| BSCF perovskite | Crystalline oxide | Amorphous hydroxide | Activity initially high → moderate, stability lost |
| Mo₂C | Carbide | MoO_x | Active → less active |
| 1T-MoS₂ | Metallic 1T | Semiconducting 2H | Conductivity loss |
| CoP (acid OER) | Phosphide | Cobalt phosphate | Initial activity → slight degradation |

### Cases where reconstruction is BENEFICIAL

| Catalyst | Pre-catalyst | Active phase | Insight |
|----------|-------------|--------------|---------|
| Ni phosphide | Ni₂P | NiOOH (+P sites) | P acts as promoter in transformed phase |
| NiFe sulfide | NiFeS | NiFeOOH | Sulfide is synthesis handle only |
| Fe₃N | Nitride | FeOOH | N promotes surface morphology |

### Detection
- Operando XAS — measure oxidation state and local structure during reaction
- Operando Raman — surface phase identification
- Pre/post XPS — surface composition change
- HRTEM before and after — morphology change

### Implication for Catalyst Design
**If your catalyst reconstructs, design for the final active phase, not the initial one.**
- Characterize the stable end-state thoroughly
- Understand what the initial phase contributes (porosity? metal ratios? N/P dopants?)
- Consider directly synthesizing the final phase if possible

---

## Failure Mode 3: Poisoning by Intermediates

### H Poisoning (HER)
- At very high H* coverage, all sites occupied → rate drops
- Most relevant at very high current densities (>500 mA/cm²)
- Mitigation: optimize M-H binding strength (Sabatier principle)

### O Intermediate Poisoning (OER)
- Strongly bound OH* or O* blocks site turnover
- Too strong O-binding → deactivation (right side of OER volcano)
- Fe-rich NiFe materials can over-bind O at high Fe content

### Chloride Poisoning (Seawater electrolysis)
- Cl⁻ adsorbs on OER sites, blocking O intermediates
- Competes with OH⁻ adsorption
- Also: chlorine evolution reaction (CER) produces Cl₂ instead of O₂
- Mitigation: Lewis acid layers (Cr₂O₃, MnO_x) that adsorb Cl⁻ but not OH⁻

### CO₂ / Carbonate Poisoning (Alkaline)
- CO₂ in air + KOH → K₂CO₃ → precipitates in electrodes
- KOH electrolyte must be CO₂-free (costly to maintain)
- AEM membranes particularly susceptible — carbonate reduces OH⁻ conductivity

---

## Failure Mode 4: Mechanical Degradation

### Delamination
- Gas bubble evolution creates mechanical stress on catalyst-substrate interface
- Binder (Nafion, PTFE) degradation under alkaline conditions
- Solution: self-supported (binder-free) electrodes on metal foam/carbon cloth

### Cracking / Pulverization
- Volume change during oxidation state cycling (HER ↔ OER in reversible systems)
- Phosphides expand upon phosphidation — misfit stress
- Solution: buffer layers, composite structures

### Gas Bubble Trapping
- O₂/H₂ bubbles block electrode surface
- Worse at high current density and poor wetting
- Solution: hydrophilic surface modification, porous electrodes, wetting agents

---

## Failure Mode 5: Support Degradation

### Carbon Corrosion (OER in acid)
- Carbon supports oxidize above 1.0 V vs. RHE in acid
- Reaction: C + 2H₂O → CO₂ + 4H⁺ + 4e⁻
- Destroys electrical connection to catalyst nanoparticles
- Solution: graphitized carbon (more stable), non-carbon supports (TiO₂, SnO₂, TaC)

### ITO / FTO (Lab Substrates)
- Standard lab substrates corrode under OER conditions
- Performance on ITO/FTO does not translate to Ni foam or Ti
- Lab results on FTO should be considered indicative only

### Ni Foam Oxidation
- Ni foam itself participates in OER (as NiOOH)
- Contribution must be subtracted to isolate catalyst activity
- Often not corrected in literature — inflates apparent performance

---

## Failure Mode 6: Electrolyte Degradation

### KOH Carbonation (Alkaline)
- CO₂ absorption: 2KOH + CO₂ → K₂CO₃ + H₂O
- Reduces conductivity and changes pH
- K₂CO₃ precipitation can block porous electrodes

### Membrane Degradation (AEM)
- OH⁻ attacks quaternary ammonium headgroups (Hofmann elimination)
- Membrane conductivity loss over time
- Temperature sensitivity: worse above 60°C

### Membrane Contamination (PEM)
- Metal ions from dissolved catalyst contaminate Nafion
- Reduces proton conductivity
- ICP-MS of used membranes is underreported in catalyst papers

---

## Stability Testing — Best Practices

For a stability claim to be credible:

| Criterion | Minimum | Preferred |
|-----------|---------|-----------|
| Duration | 100 h | 1000 h |
| Measurement | Chronopotentiometry | CP + periodic CV |
| Electrolyte analysis | ICP-MS (before/after) | Inline ICP-MS |
| Post-mortem analysis | XPS | XPS + TEM + Raman |
| Current density | 10 mA/cm² | 100–500 mA/cm² |
| Potential stability claim | < 30 mV drift | < 10 mV drift |

**The stability problem in one sentence:**
Most non-PGM catalysts show <20% performance loss in the first 100h but continued
slow degradation that is catastrophic at 10,000h — and almost no papers run long enough to show it.

---

## Known Long-Duration Results (>1000h)

| System | Duration | Conditions | Outcome |
|--------|---------|------------|---------|
| NiMo alloy | 10,000h+ | 30% KOH, 80°C, 200 mA/cm² | Commercially deployed |
| NiFe LDH | 1,000h | 1M KOH, 10 mA/cm² | <20 mV drift |
| Ni foam (plain) | 5,000h | Alkaline AEL | Acceptable |
| CoP (acid) | 100h max | H₂SO₄ | Significant dissolution |
| Mo₂C@NC | 200h | Acid HER | Promising but limited |

---

## Summary: Failure Mode Priority Matrix

| Failure Mode | HER Impact | OER Impact | Acid | Alkaline | Solvable? |
|--------------|-----------|-----------|------|----------|-----------|
| Metal dissolution | Medium | HIGH | CRITICAL | Low | Partial |
| Reconstruction | Medium | Medium | High | Medium | Yes (pre-catalyst design) |
| H/O poisoning | Low | Medium | Medium | Medium | Yes (composition tuning) |
| Mechanical | Medium | Medium | Medium | Medium | Yes (morphology) |
| Carbon corrosion | Low | HIGH | CRITICAL | Low | Yes (alternative supports) |
| Membrane contamination | Low | HIGH | High | Low | Partial |
| Electrolyte | Low | Medium | Low | High | Yes (gas management) |
