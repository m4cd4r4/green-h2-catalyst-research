# 16 — Acid OER Synthesis Guide: Mn-W-Ti Oxide Compositions

## Purpose

Translates the acid OER Bayesian optimizer output into actionable lab protocols.

**Three synthesis targets, ordered by experimental priority:**

| Priority | Composition | Rationale | Predicted η₁₀ | Predicted D |
|----------|-------------|-----------|--------------|------------|
| P1 | Mn₀.₆₁W₀.₃₂Oₓ | Highest predicted activity, Mn-W binary baseline | 331 mV | 18 µg/cm²/h |
| P2 | Mn₀.₄₅W₀.₂₂Ti₀.₁₆Ni₀.₁₃Oₓ | Best activity–stability balance, Pareto optimal | 335 mV | 12 µg/cm²/h |
| P3 | Ca₀.₀₈Mn₀.₅₆W₀.₃₁Oₓ | Ca-birnessite route — highest literature precedent | ~325 mV | ~13 µg/cm²/h |

IrO₂ benchmark: η₁₀ = 250 mV, D = 0.01 µg/cm²/h.
**Gap to close:** ~80 mV activity + 1,000–1,800× dissolution.

---

## 1. Synthesis: P1 — Mn₀.₆₁W₀.₃₂Oₓ (Hydrothermal Route)

### Rationale for hydrothermal
Hydrothermal synthesis produces well-defined α-MnO₂ tunnelled structures
(hollandite) in which W can substitute into the 2×2 tunnel framework.
W-substitution into MnO₂ tunnels (Jiao 2019, Gorlin 2013) is the most
literature-supported route to W-stabilised acid OER catalysts.

### Reagents
| Reagent | Grade | Amount (100 mg batch) |
|---------|-------|-----------------------|
| KMnO₄ | 99%, anhydrous | 0.395 mmol (62.5 mg) |
| Na₂WO₄·2H₂O | 98% | 0.210 mmol (69.3 mg) |
| HCl, conc. | 37% | 0.5 mL |
| Deionised water | 18 MΩ·cm | 20 mL |

Target Mn:W = 0.61:0.32 (molar ratio after accounting for oxidation states).

### Protocol

**Step 1 — Precursor solution**
```
1. Dissolve KMnO₄ (62.5 mg) in 15 mL DI water → pink solution
2. Dissolve Na₂WO₄·2H₂O (69.3 mg) in 5 mL DI water → clear solution
3. Add WO₄ solution dropwise to KMnO₄ solution with stirring
4. Add HCl (0.5 mL) dropwise — solution darkens, MnO₂ begins to precipitate
5. Stir 10 min at room temperature → brown suspension
```

**Step 2 — Hydrothermal treatment**
```
Transfer to 25 mL Teflon-lined autoclave
Heat at 160°C for 12 hours (ramp: 5°C/min)
Cool naturally to room temperature (do NOT quench — cracking risk)
```

**Step 3 — Workup**
```
Centrifuge at 10,000 rpm, 10 min
Wash 3× with DI water, 1× with ethanol
Dry at 80°C overnight in air
(Optional: anneal at 200°C/2h in air — sharpens XRD peaks, small activity loss)
```

**Step 4 — Ink preparation (for electrochemical testing)**
```
5 mg catalyst + 50 µL Nafion (5 wt%) + 450 µL ethanol + 500 µL DI water
Sonicate 30 min in ice bath
Drop-cast 10 µL onto glassy carbon (0.196 cm²) → loading: 0.51 mg/cm²
Dry at room temperature, then 60°C/30 min
```

### Expected characterisation

| Technique | Expected result | If different |
|-----------|----------------|-------------|
| XRD | α-MnO₂ (JCPDS 44-0141), W does not form separate phase | Check W loading — may need reduction if WO₃ peak appears |
| Raman | Mn-O peak at 630 cm⁻¹ (red-shift vs MnO₂ if W incorporated) | Sharp WO₃ peak at 807 cm⁻¹ = W not substituted |
| XPS Mn 2p₃/₂ | 642.0 eV (Mn4+); small shoulder at 641.5 eV (Mn3+) | |
| XPS W 4f₇/₂ | 35.4 eV (W6+ substituted) vs 35.9 eV (WO₃ surface) | |
| ICP-OES (digest) | Mn:W ≈ 0.61:0.32 ±5% | Adjust precursor ratio and re-run |
| BET | 80–150 m²/g (hollandite nanorod morphology) | |

---

## 2. Synthesis: P2 — Mn₀.₄₅W₀.₂₂Ti₀.₁₆Ni₀.₁₃Oₓ (Co-precipitation Route)

### Rationale for co-precipitation
Four-component compositions with Ti cannot easily be incorporated into
tunnelled MnO₂ by hydrothermal methods. Co-precipitation from mixed
nitrate/tungstate solutions gives an amorphous mixed oxide that is
more homogeneous for multi-component compositions.

Amorphous multi-component oxides also show ~0.1–0.3 eV deeper d-band
centers than crystalline counterparts (literature: Ma 2022, Kwon 2020).

### Reagents
| Reagent | Grade | Amount (100 mg batch) |
|---------|-------|-----------------------|
| Mn(NO₃)₂·4H₂O | 98% | 0.450 mmol (113.5 mg) |
| Na₂WO₄·2H₂O | 98% | 0.220 mmol (72.6 mg) |
| Ti(OiPr)₄ | 97% | 0.160 mmol (45.4 mg) |
| Ni(NO₃)₂·6H₂O | 98% | 0.130 mmol (37.8 mg) |
| NaOH (1 M) | | ~12 mL (to pH 10) |
| NH₃·H₂O (25%) | | 0.5 mL (peptising agent) |
| DI water | 18 MΩ·cm | 50 mL total |

### Protocol

**Step 1 — Metal solution**
```
Dissolve Mn(NO₃)₂, Ni(NO₃)₂, Na₂WO₄ in 30 mL DI water
Add Ti(OiPr)₄ LAST, with vigorous stirring — Ti(IV) hydrolyses rapidly
Add 0.5 mL NH₃ to prevent premature Ti precipitation
Stir 10 min → pale yellow solution with slight turbidity
```

**Step 2 — Controlled co-precipitation**
```
Heat solution to 60°C with stirring
Add 1 M NaOH dropwise at 1 mL/min using syringe pump
Monitor pH — target final pH = 10.0 ± 0.2
Maintain at 60°C, pH 10 for 1 hour with stirring (ageing step)
```

**Step 3 — Workup**
```
Filter (0.2 µm PTFE membrane)
Wash 5× with DI water until filtrate conductivity < 10 µS/cm
Re-suspend in 20 mL DI water + 0.5 mL NH₃
Lyophilise (freeze-dry) 24h → preserves amorphous structure better than oven drying
Alternative: dry at 60°C/24h in vacuum
```

**Expected characterisation**

| Technique | Expected result |
|-----------|----------------|
| XRD | Broad humps only — amorphous (good) |
| HRTEM | Disordered lattice fringes, ~3 nm coherence length |
| XPS Mn 2p₃/₂ | Mixed Mn3+/Mn4+ (641.8 eV) — more Mn3+ than P1 |
| XPS Ti 2p₃/₂ | 458.5 eV (Ti4+) |
| SAED | Diffuse rings — confirm amorphous |
| BET | 200–300 m²/g (amorphous oxides are typically higher surface area) |

---

## 3. Synthesis: P3 — Ca₀.₀₈Mn₀.₅₆W₀.₃₁Oₓ (Ca-Birnessite Route)

### Rationale
Ca-birnessite (layered MnO₂ with Ca²⁺ in interlayer) is the most
literature-validated acid-stable Mn-oxide. Ca²⁺ substitution:
1. Promotes Mn3+ formation (charge compensation → fills d-band slightly)
2. Pins the interlayer, preventing structural collapse in acid
3. Provides hydrogen-bond acceptor sites that facilitate O–O coupling

The Ca₀.₀₈ loading matches the optimizer sweet spot (8% Ca, -14% dissolution).

### Reagents
| Reagent | Amount |
|---------|--------|
| KMnO₄ | 0.56 mmol (88.6 mg) |
| CaCl₂·2H₂O | 0.08 mmol (11.8 mg) |
| Na₂WO₄·2H₂O | 0.31 mmol (102.2 mg) |
| H₂O₂ (30%) | 1 mL (reducing agent for Mn4+→Mn3+) |
| DI water | 30 mL |

### Protocol

**Step 1 — Permanganate reduction to birnessite**
```
Dissolve KMnO₄ in 20 mL DI water
Add H₂O₂ (1 mL) dropwise with stirring — CAUTION: exothermic, gas evolution
Brown precipitate forms (δ-MnO₂ birnessite precursor)
Stir 30 min at RT
```

**Step 2 — Ca and W incorporation**
```
Dissolve CaCl₂ and Na₂WO₄ in 10 mL DI water
Add to the MnO₂ suspension with stirring
Heat to 80°C for 4 hours under reflux
The Ca²⁺ exchanges into the interlayer; WO₄²⁻ partially substitutes into sheets
```

**Step 3 — Workup**
```
Centrifuge 10,000 rpm, 10 min
Wash 3× DI water
Dry 80°C/12h in air
Anneal 150°C/2h in air (maintains layered structure — higher temps collapse it)
```

**Expected characterisation**

| Technique | Expected result | Significance |
|-----------|----------------|-------------|
| XRD | Birnessite peaks at 7.2 Å and 3.6 Å (d-spacing expands with Ca) | Ca in interlayer |
| XPS Ca 2p | 347.0 eV (Ca2+) | Confirms Ca incorporation |
| ICP-OES | Ca:Mn ≈ 0.08:0.56 ±5% | Check stoichiometry |
| Raman | 578 cm⁻¹ + 650 cm⁻¹ (Mn-O birnessite pattern) | |
| TGA | Water loss at 100–200°C (interlayer H₂O) | Interlayer structure intact |

---

## 4. Electrochemical Testing Protocol (All Three)

### Setup
- Electrolyte: 0.5 M H₂SO₄ (pH 0.3), prepared from concentrated H₂SO₄ + DI water
- Working electrode: Glassy carbon (0.196 cm²) or Toray carbon paper for higher loading
- Reference: Ag/AgCl (3M KCl), convert to RHE: E_RHE = E_Ag/AgCl + 0.210 + 0.059×pH
- Counter: Platinum mesh (use carbon mesh if concerned about Pt dissolution contamination)
- Cell: H-cell or single-compartment (Nafion membrane if using Pt counter)
- Temperature: 25°C (±1°C, thermostat bath)

### Activation sequence
```
1. CVs × 50 at 100 mV/s (1.0 – 1.8 V vs RHE) — surface conditioning
2. CV × 3 at 5 mV/s — clean polarisation curve
3. EIS at 1.55 V vs RHE, 100 kHz – 0.1 Hz — measure Rs and Rct
```

### Activity measurement
```
Chronoamperometry at 10 mA/cm² (or 1.55 V vs RHE) for 30 min
After 30 min: record steady-state η₁₀ (overpotential at 10 mA/cm²)
CV at 5 mV/s: extract Tafel slope from log(j) vs η plot (linear region)
```

### Stability test — CRITICAL for validating optimizer predictions
```
Chronopotentiometry at 10 mA/cm²
Duration: 6 hours minimum, 24 hours preferred

COLLECT ICP-MS SAMPLES:
  - 1 mL aliquot at t = 0 (blank)
  - 1 mL aliquot at t = 1h
  - 1 mL aliquot at t = 6h
  - (24h test: also at t = 12h, t = 24h)

Measure: Mn, W, Ti, Ni, Ca concentrations (all elements in catalyst)
Report: dissolution rate D = mass dissolved / (electrode area × time) [µg/cm²/h]
```

### What to measure after stability test
```
Post-test characterisation (remove electrode from electrolyte carefully):
  - XPS: has oxidation state changed? (Mn3+ → Mn4+ expected under OER)
  - Raman: did crystal structure change?
  - BET: did surface area decrease (sintering)?
  - ICP digest of remaining catalyst: what fraction dissolved?
```

---

## 5. Decision Tree: What the Results Mean

```
ACTIVITY RESULT:
  η₁₀ < 310 mV → EXCELLENT — at or near NiFe LDH baseline (but in acid!)
  310–350 mV   → GOOD — worth optimising
  350–400 mV   → ACCEPTABLE — still better than most acid earth-abundant catalysts
  > 400 mV     → POOR — reconsider composition; check if activation incomplete

DISSOLUTION RESULT (6h test):
  D < 1 µg/cm²/h   → EXCELLENT — approaching practical viability
  1–10 µg/cm²/h    → GOOD — 10–100× better than unoptimised Mn-oxide
  10–50 µg/cm²/h   → MODERATE — matches optimizer prediction range; continue
  > 50 µg/cm²/h    → POOR — composition is dissolving rapidly; add more W or Ti

IF ACTIVITY POOR AND DISSOLUTION GOOD:
  → Increase Mn fraction, decrease W; try Ca doping to promote Mn3+ (eg = 1)
  → Check XPS: if all Mn4+ (eg = 0), reduce annealing atmosphere (5% H2/N2)

IF ACTIVITY GOOD AND DISSOLUTION POOR:
  → Increase W to 0.35–0.40; add Ti to 0.15–0.20
  → Try KOH leaching post-synthesis (0.1M KOH, 1h) to remove unstable phases
  → Confirm composition by ICP-OES — may have lost W during synthesis

IF BOTH POOR:
  → Check synthesis — is the composition actually what was intended?
  → Verify electrode preparation (no binder contamination)
  → Run EIS to check high-frequency resistance (electrode contact issue?)
```

---

## 6. Connecting Results Back to the ML Model

After measuring real η₁₀ and dissolution rate, add entries to `code/stability_ml.py`:

```python
# In build_catalyst_dataset(), add:
{
    'name': 'MnW-binary-P1',
    'stability_h': MEASURED_HOURS,      # from ICP-MS: when D exceeds 50 µg/cm²/h
    'eta_10_mv': MEASURED_ETA,
    'tafel_slope': MEASURED_TAFEL,
    'crystal_class': 'doped_oxide',     # W-substituted MnO2
    'is_acid': 1,
    'is_alloy': 0,
    'd_band_center_ev': -1.92,          # W-doped MnO2 (estimated from MP table)
    'dissolution_potential_v': 0.88,    # weighted Mn:W Pourbaix
    # ... other features from materials_project_api.py output
},
```

**Expected impact on model:** Each new measured data point with accurate descriptors
is worth ~5× a simulated data point. Three real measurements of the P1–P3 compositions
would likely push 5-fold CV R² from 0.43 to ~0.55–0.65.

---

## 7. Ordering List — Week 1 Priorities

| Chemical | Supplier | Cat. No. | Estimated cost |
|----------|---------|---------|---------------|
| KMnO₄, 99.9%, 100g | Sigma | 223468 | ~$35 |
| Na₂WO₄·2H₂O, 99%, 100g | Sigma | 14130 | ~$45 |
| Ti(OiPr)₄, 97%, 25g | Sigma | 87560 | ~$55 |
| Ni(NO₃)₂·6H₂O, 97%, 100g | Sigma | 72253 | ~$30 |
| CaCl₂·2H₂O, 99%, 500g | Sigma | C3306 | ~$40 |
| Nafion 117 solution, 5 wt% | Sigma | 70160 | ~$80/100mL |
| H₂SO₄, 95–98%, 1L | Sigma | 320501 | ~$50 |
| Ag/AgCl reference electrode | BASi | MF-2052 | ~$120 |
| ICP-MS standards (Mn, W, Ti, Ni) | SPEX | | ~$80 each |
| **Total materials (first batch)** | | | **~$600** |

This is ~1.2% of the $50K budget from the 12-month roadmap (doc 14).

---

*Generated from acid_oer_optimizer.py results. Refer to 13-18O-labeling-protocol.md
for the parallel ¹⁸O isotope experiment to distinguish AEM vs LOM on these compositions.*
