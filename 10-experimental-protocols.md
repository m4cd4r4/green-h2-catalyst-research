# 10 — Detailed Experimental Protocols

## Purpose

These protocols are written at lab-bench level — specific enough for a grad student with
basic electrochemistry training to follow. Each corresponds to one of the top-ranked hypotheses.

**Equipment assumed:**
- Potentiostat/galvanostat (Biologic, Gamry, or similar)
- Rotating disk electrode (RDE) setup
- ICP-MS (or access to one)
- Raman spectrometer (ideally operando-capable)
- Basic hydrothermal synthesis capability (autoclave, furnace)
- Standard electrochemistry glassware

---

## Protocol 1 — Pulsed Chronopotentiometry (Hypothesis C2)
**"Periodic rest pulses extend OER catalyst lifetime"**

### Rationale
Active OER sites may accumulate O* intermediates over extended operation.
Periodic open-circuit rest allows desorption and site regeneration.
If true, this is an operational protocol — works with ANY catalyst, no new synthesis.

### Materials
- NiFe LDH on Ni foam (synthesized by Protocol 4 or commercially available)
- 1M KOH (Sigma-Aldrich, 99.99% purity — CRITICAL: use ultra-pure KOH or pre-purify)
- KOH Fe impurity removal: pass through Ni(OH)₂ column to adsorb Fe (or use purified KOH)
- Reference electrode: Hg/HgO (1M KOH)
- Counter electrode: Pt wire or carbon rod
- 3-electrode Teflon cell

### KOH Purification (Essential)
1. Dissolve KOH to 1M in ultrapure water
2. Add Ni(NO₃)₂ to 0.1 mM (deposits Ni(OH)₂ as Fe scavenger)
3. Stir 24h, filter through 0.2 μm membrane
4. Result: <0.01 ppm Fe (verify by ICP-MS)
5. **WHY:** Fe impurities in unpurified KOH deposit on electrode and change activity
   This is a major source of NiFe LDH irreproducibility between labs

### Protocol A — Constant Chronopotentiometry (Control)
```
Equipment: Biologic SP-150 or equivalent
WE: NiFe LDH on Ni foam (1 cm²), pre-conditioned 50 CV cycles
RE: Hg/HgO in 1M KOH
CE: Pt wire
Electrolyte: 1M purified KOH, 25°C, N₂ purge
Measurement:
  1. Record CV (0.0–0.7V vs Hg/HgO, 5 mV/s, 3 cycles) → get initial η₁₀
  2. Apply constant current: 10 mA/cm² (geometric area)
  3. Record potential vs. time for 500h
  4. Every 24h: briefly interrupt for CV (5 cycles) to track η₁₀ drift
  5. Every 48h: collect 5 mL electrolyte for ICP-MS (replace with fresh KOH)
  6. Post-test: XPS (Ni 2p, Fe 2p), Raman (400–800 cm⁻¹)
```

### Protocol B — Pulsed Chronopotentiometry (Test)
```
Same as Protocol A but replace step 2 with:
  Apply 10 mA/cm² for 59 minutes
  Then open circuit for 1 minute
  Repeat for 500h total (500 pulses)
  All other measurements identical to Protocol A
```

### Protocol C — Short Pulse Variant
```
10 mA/cm² for 9 minutes → OC for 1 minute → repeat
```

### Data Analysis
```python
# Plot these for each protocol:
# 1. Potential vs. time (V vs. RHE) - main degradation metric
# 2. η₁₀ from periodic CV vs. cumulative time
# 3. Cumulative dissolved Fe (ICP-MS) vs. time
# 4. EIS (Nyquist) - Rct at 1.5V vs. RHE, measured before/during/after

# Key comparison metric:
# Time to 30 mV overpotential increase (t₃₀)
# Higher t₃₀ = longer lifetime
# Compare Protocol A vs B vs C t₃₀ values
```

### Expected Outcomes
- If hypothesis correct: Protocol B t₃₀ > Protocol A t₃₀ by ≥50%
- If wrong: no significant difference
- Useful regardless: dissolution kinetics data (ICP-MS) is publishable standalone

### Notes
- Run at least 3 replicates per protocol (catalyst variability is real)
- Ni foam itself contributes to OER — subtract Ni foam blank
- Temperature control: ±1°C is important for reproducibility

---

## Protocol 2 — Ca-Birnessite Synthesis for Acid OER (Hypothesis B1)
**"Ca incorporation in MnO₂ improves acid OER stability via PSII-inspired mechanism"**

### Rationale
Photosystem II uses a Mn₄CaO₅ cluster for water oxidation. The Ca:Mn ratio is ~1:4.
We synthesize Ca-doped birnessite at systematic Ca:Mn ratios to find the PSII-analogous optimum.

### Synthesis — Ca_x Mn_{1-x}O₂ (Birnessite)

**Precursors:**
- KMnO₄ (Sigma, ≥99%)
- MnSO₄·H₂O (Sigma, ≥99%)
- Ca(NO₃)₂·4H₂O (Sigma, ≥99%)
- Ultrapure H₂O (18.2 MΩ·cm)

**Synthesis (Target compositions: x = 0, 0.05, 0.10, 0.15, 0.20, 0.25):**
```
Step 1: Dissolve 0.79 g KMnO₄ in 50 mL H₂O
Step 2: Dissolve (1-x)×0.85 g MnSO₄ + x×Ca(NO₃)₂ (calculated) in 30 mL H₂O
         - x=0:    0.850 g MnSO₄, 0 g Ca(NO₃)₂
         - x=0.05: 0.808 g MnSO₄, 0.059 g Ca(NO₃)₂
         - x=0.10: 0.765 g MnSO₄, 0.118 g Ca(NO₃)₂
         - x=0.15: 0.723 g MnSO₄, 0.177 g Ca(NO₃)₂
         - x=0.20: 0.680 g MnSO₄, 0.236 g Ca(NO₃)₂
         - x=0.25: 0.638 g MnSO₄, 0.295 g Ca(NO₃)₂
Step 3: Add Step 2 solution dropwise to Step 1 with stirring at 25°C
Step 4: Brown precipitate forms immediately (this is birnessite)
Step 5: Transfer to 100 mL Teflon-lined autoclave
Step 6: Heat at 120°C for 12h
Step 7: Cool to RT, filter, wash 3× with ultrapure water
Step 8: Dry at 60°C under vacuum for 24h
Step 9: Weigh yield (expect 0.3–0.5 g)
```

**Electrode preparation:**
```
Mix catalyst (5 mg) with Nafion (5 wt%, 20 μL) + isopropanol (180 μL)
Sonicate 30 min → catalyst ink
Drop-cast onto glassy carbon RDE (5 mm diameter, 0.196 cm²)
Loading: 0.5 mg/cm² (10 μL of ink)
Dry at 60°C for 30 min
```

### Characterization (Before Testing)
```
1. XRD: 5–70° 2θ, 0.02° step, Co Kα or Cu Kα
   - Confirm birnessite phase (d001 ≈ 7.0–7.2 Å for K-birnessite)
   - Ca incorporation may expand d001 slightly
   - Compare peak positions vs. x

2. ICP-OES on dissolved sample: verify Ca/Mn ratio vs. target

3. Raman spectroscopy (532 nm):
   - Birnessite Raman bands: ~575, 640 cm⁻¹ (Mn-O stretching)
   - Track band shifts with Ca content

4. BET surface area (N₂ adsorption, 77K)
   - Normalize electrochemical activity to surface area
```

### Electrochemical Testing
**Electrolyte:** 0.5M H₂SO₄ (ACS grade, not purified — want acidic, not alkaline)
**Setup:** Standard 3-electrode, RDE at 1600 rpm, 25°C
```
Step 1: N₂ purge for 30 min before measurement
Step 2: CV conditioning: 0.9–1.8 V vs. RHE, 50 mV/s, 50 cycles
Step 3: Polarization curve: 5 mV/s, 0.9–1.8 V vs. RHE
Step 4: Extract η₁₀ from polarization curve (IR-corrected: subtract iR from PEIS)
Step 5: Tafel plot: log(j) vs. η, linear region 10–100 mA/cm²
Step 6: Stability: chronopotentiometry at 1 mA/cm² for 20h
        (NOTE: use 1 mA/cm² not 10 — MnO₂ is not that active in acid yet)
Step 7: Post-stability CV to compare with pre-stability
Step 8: Collect electrolyte for ICP-MS (Mn, Ca, K)
```

### Key Measurements
```python
# For each composition x:
# eta_10_mV: overpotential at 10 mA/cm² (or 1 mA/cm² if not reachable)
# tafel_slope: mV/dec from log(j) vs. η
# t_20: time to 20% activity loss in chronopotentiometry
# mn_dissolution_nmol_cm2_h: from ICP-MS
# ca_dissolution_nmol_cm2_h: from ICP-MS

# Plot: eta_10 vs. x (look for optimum)
# Plot: t_20 vs. x (look for optimum)
# Check if activity optimum = stability optimum or if they differ
```

### Expected Results
- Activity: may peak around x = 0.10–0.15 (PSII ratio)
- Stability: should improve monotonically with Ca up to x = 0.20, then plateau
- If Ca creates "Ca-pinned Mn³⁺" effect: dissolution should drop sharply above x = 0.10

---

## Protocol 3 — Amorphous vs. Crystalline NiFeOOH at High Current Density (Hypothesis B6)

### Rationale
Most OER papers benchmark at 10 mA/cm². Industrial targets are 100–1000 mA/cm².
Amorphous materials have faster ion diffusion and may outperform crystalline at high j.

### Synthesis

**Sample A — Crystalline NiFe LDH (hydrothermal):**
```
1. Dissolve Ni(NO₃)₂ (0.58 g) + Fe(NO₃)₃ (0.20 g) + urea (0.60 g) in 60 mL H₂O
   (Ni:Fe = 3:1 molar ratio — confirmed optimal in literature)
2. Transfer to 80 mL autoclave, 120°C, 12h
3. Wash, filter, dry 60°C
4. Deposit on Ni foam: drop-cast ink (5 mg catalyst + Nafion + IPA)
5. Confirm crystallinity: XRD should show LDH (003) at ~11.5° 2θ
```

**Sample B — Amorphous NiFeO_xH_y (electrodeposition):**
```
Bath: 0.1M NiSO₄ + 0.02M FeSO₄ in 0.5M Na₂SO₄, pH 3.0 (adjusted with H₂SO₄)
Substrate: Ni foam (same as A), 1 cm²
Electrodeposition: -1.0 V vs. Ag/AgCl for 300s (adjust for ~5 mg/cm² loading)
Post-treatment: rinse with water, dry at 60°C (NO calcination — must stay amorphous)
Confirm amorphous: XRD should show no sharp peaks
```

### Current-Density Benchmark Test
```
Both samples in 1M KOH, 3-electrode cell, 25°C
Test sequence (run both samples through full sequence):

1. EIS at 1.50 V vs. RHE (1 Hz–100 kHz, 10 mV amplitude)
   → extract Rct and Rs → use for iR correction

2. Polarization curves at each target j:
   CA at 10, 50, 100, 200, 500, 1000 mA/cm²
   Hold each for 5 min → record steady-state potential
   This gives η(j) — the activity at industrial current densities

3. For each j point: record potential (iR corrected) and calculate η

4. Long-term stability:
   Sample A: 200h at 100 mA/cm²
   Sample B: 200h at 100 mA/cm²
   Record potential vs. time
   Every 24h: measure ECSA (double-layer capacitance from CV in non-Faradaic region)
```

### ECSA Measurement (Important for Normalization)
```
CV in 1.0–1.1 V vs. RHE range (non-Faradaic window)
Scan rates: 20, 40, 60, 80, 100 mV/s
Plot: charging current (at 1.05 V) vs. scan rate → slope = Cdl
ECSA = Cdl / Cs (where Cs = 0.040 mF/cm² for NiFe in KOH, literature value)
Normalize all activity to ECSA not geometric area
```

### Key Analysis
```python
# For both samples, plot:
# 1. η vs. j (compare at 10, 50, 100, 200, 500, 1000 mA/cm²)
#    → look for crossover point where amorphous becomes better
# 2. Tafel slope across full j range → does it remain linear?
#    Mass transport limits at high j give upward curvature
# 3. ECSA-normalized j vs. potential → intrinsic activity comparison
# 4. Potential vs. time at 100 mA/cm² for 200h → stability comparison
# 5. EIS Nyquist at 200 and 1000 mA/cm² → ion transport resistance
```

---

## Protocol 4 — Dissolution Power Law (Hypothesis C1)
**"Short-term dissolution kinetics predict long-term stability"**

### Rationale
If dissolution rate follows D(t) = D₀·t^(-α), then:
- α > 0.5: self-passivating → long-term stable
- α ≈ 0: constant dissolution → will fail at industrial timescale

This requires inline ICP-MS — expensive but the data is uniquely valuable.

### Equipment Required
- Inline ICP-MS: flow-through cell → ICP-MS
- OR: fraction collection every 1h, batch ICP-MS analysis
- Peristaltic pump (0.1–1 mL/min)
- Custom flow-through electrochemical cell (sealable, PTFE)

### Protocol
```
Prepare 10 catalyst samples (diverse selection from datasets):
  1. NiFe LDH (alkaline, expected good)
  2. CoP on CC (acid, expected poor)
  3. Mo2C@NC (acid, expected moderate-good)
  4. BSCF perovskite (alkaline, expected moderate)
  5. Amorphous NiFeO_xH_y (alkaline, expected good)
  6. MnO2 birnessite (acid, expected poor)
  7. Ca-MnO2 (acid, test hypothesis B1)
  8. FeCoNiCr HEA (acid, expected moderate)
  9. WP (acid, expected good)
  10. NiMo alloy (alkaline, expected very good)

For each catalyst:
  Electrolyte: appropriate (KOH or H₂SO₄)
  j = 10 mA/cm² constant
  Duration: 100h
  Fraction collection: every 1h for first 10h, every 6h thereafter
  Measure: [metal] in each fraction by ICP-MS

  Compute: D(t) in μg/cm²/h
  Fit: D(t) = D₀ · t^(-α)  [log-log linear regression]
  Extract: D₀, α for each metal in each catalyst
```

### Validation
```python
# Validation data needed (from literature or external collaborator):
# Known good catalysts: NiMo (10,000h), NiFe LDH (1000h)
# Known poor catalysts: CoP in acid (<100h), BSCF in acid (<20h)

# Check: does α predict the known outcomes?
# If yes: apply model to unknown catalysts

import numpy as np
from scipy.optimize import curve_fit

def dissolution_power_law(t, D0, alpha):
    return D0 * t**(-alpha)

# For each catalyst, each metal:
# t = time array (hours)
# D = dissolution rate at each time (μg/cm²/h)
popt, pcov = curve_fit(dissolution_power_law, t, D, p0=[D[0], 0.5])
D0, alpha = popt

# Predict total dissolution at 10,000h:
t_target = 10000
total_dissolution = D0 / (1 - alpha) * t_target**(1 - alpha)
# (integral of D0*t^(-α) from 0 to t_target, α ≠ 1)

print(f"α = {alpha:.3f}")
print(f"Predicted total dissolution at 10,000h: {total_dissolution:.1f} μg/cm²")
# Compare to acceptable limit (typically <100 μg/cm² Ir in PEM literature)
```

---

## Protocol 5 — W-Doped CoP for Acid HER Stability (Hypothesis A1)

### Synthesis — Co₁₋ₓWₓP

**Method:** Co-reduction of mixed oxide precursor, then phosphidation

```
Step 1: Dissolve CoCl₂·6H₂O + WCl₆ (for W=0, 5, 10, 15, 20 mol%)
        in ethanol (50 mL) under N₂ atmosphere

Molar ratios for Co₀.₉W₀.₁P (x=0.10, target 1 mmol total metal):
  CoCl₂·6H₂O: 0.90 mmol (0.214 g)
  WCl₆: 0.10 mmol (0.040 g)
  Dissolve in 40 mL EtOH, stir 1h

Step 2: Add 1 mmol NaH₂PO₂ (0.104 g) + NaBH₄ (0.1 mmol, 0.004 g, as reducing agent)
Step 3: Reflux at 80°C for 2h under N₂
Step 4: Transfer to autoclave, 200°C, 12h (crystallization and phosphidation)
Step 5: Cool, filter, wash (water, EtOH), dry 60°C vacuum

Alternative (thermal phosphidation route, better phase control):
Step 1: Synthesize Co₁₋ₓWₓ alloy nanoparticles by coreduction
Step 2: Mix with NaH₂PO₂ (20:1 mass ratio)
Step 3: Heat to 350°C at 5°C/min in Ar
Step 4: Hold 2h at 350°C
Step 5: Cool under Ar (do not expose to air at high temp — pyrophoric risk)
```

### Characterization
```
XRD: CoP reference (JCPDS 29-0497), check for W-CoP solid solution vs. WP secondary phase
     W in CoP lattice → peak shift to smaller 2θ (larger d-spacing, W is bigger than Co)
     Secondary WP peaks → phase separation (want single phase)

XPS:
  Co 2p: peak at 778.6 eV (CoP), shifts with W content
  W 4f: peaks at ~33 eV (WP-like) or ~36 eV (WO₃) — want metallic-like W
  P 2p: ~130 eV (phosphide P), ~134 eV (surface oxidized phosphate)

ICP-OES: Confirm Co:W:P atomic ratio
TEM/EDS: Elemental mapping — confirm W distribution is uniform (not segregated)
```

### Electrochemical Testing (HER in acid)
```
Electrolyte: 0.5M H₂SO₄
Working electrode: catalyst on carbon fiber paper (0.5 mg/cm²)
Reference: RHE (Pt in H₂-saturated 0.5M H₂SO₄)
Counter: Pt mesh (separated by Nafion membrane)

Protocol:
1. CV activation: -0.4 to +0.2 V vs. RHE, 100 mV/s, 100 cycles
2. Polarization: 2 mV/s, -0.4 to 0 V vs. RHE
3. Extract η₁₀ (iR corrected)
4. Tafel slope from log(j) vs. η, linear region
5. Chronopotentiometry: -10 mA/cm² for 100h
6. Electrolyte ICP-MS: Co, W, P every 24h
7. Post-test XPS: check Co:W:P ratio change
```

### Key Metric
```
Stability Index = (η₁₀ after 100h - η₁₀ initial) / η₁₀ initial × 100%
Lower = more stable

Also: Total Co dissolved (μg/cm²) over 100h
Lower = more stable

Plot: Stability Index vs. x (W content)
Expected: CoP (x=0) degrades most; W=10-15% optimal; W=20% too inactive
```

---

## General Notes on Reproducibility

**The #1 cause of irreproducible results in this field:**
1. KOH Fe impurities (always purify or document source + lot)
2. iR compensation errors (always use PEIS to measure Rs before and after)
3. Loading differences (always confirm by weighing or ICP dissolution)
4. Reference electrode calibration (calibrate daily against RHE standard)
5. Counter electrode contamination (use separated compartment for all stability tests)
6. Ni foam contribution (always test bare Ni foam blank and subtract)

**The #1 cause of missed mechanisms:**
- Only testing at 10 mA/cm² — always include at least 100 mA/cm²
- Not running post-mortem analysis — always do XPS + Raman after stability tests
- Not measuring ECSA — always normalize to ECSA and geometric area both

**Statistical requirements:**
- Minimum n=3 replicates for any published claim
- Report mean ± standard deviation, not just best value
- If replicates vary by >20%, investigate synthesis reproducibility before claiming activity
