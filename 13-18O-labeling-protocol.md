# 13 — ¹⁸O Isotope Labeling: The Single Most Informative Experiment in OER

## Why This Experiment Is Uniquely Powerful

The ¹⁸O isotope labeling experiment definitively answers the most important mechanistic
question in OER catalysis: **Does the oxygen in O₂ come from water (AEM pathway) or from
the catalyst lattice (LOM pathway)?**

This matters because:
- **AEM pathway** → scaling relations hold → theoretical minimum η ≈ 370 mV
- **LOM pathway** → scaling relations potentially broken → η could approach 0 mV

If ANY earth-abundant acid OER catalyst shows LOM, it becomes the most important material
in the field. Every group would pivot to it.

**Current gap:** This experiment has been done for IrO_x and alkaline Co/Ni systems.
It has NOT been systematically done for earth-abundant acid OER candidates.
**This gap can be closed with ~6 weeks of work.**

---

## The Chemistry

### AEM (Adsorbate Evolution Mechanism)

```
Step 1:  H₂¹⁸O + * → ¹⁸OH* + H⁺ + e⁻
Step 2:  ¹⁸OH* → ¹⁸O* + H⁺ + e⁻
Step 3:  ¹⁸O* + H₂¹⁸O → ¹⁸O-¹⁸OH* + H⁺ + e⁻    (OOH* formed from water ¹⁸O)
Step 4:  ¹⁸O-¹⁸OH* → ¹⁸O₂ + * + H⁺ + e⁻
```

**Prediction:** If H₂¹⁸O is the electrolyte, evolved O₂ is 100% ¹⁸O₂ (m/z = 36).
¹⁶O₂ (m/z = 32) = 0%.

### LOM (Lattice Oxygen Mechanism)

```
Step 1:  H₂¹⁸O + * → ¹⁸OH* + H⁺ + e⁻
Step 2:  ¹⁸OH* → ¹⁸O* + H⁺ + e⁻
Step 3:  ¹⁸O* + ¹⁶O_lattice → ¹⁸O-¹⁶O (gas)      ← O-O bond from lattice!
         OR:  ¹⁶O_lattice + ¹⁶O_lattice → ¹⁶O₂    ← pure lattice O₂
Step 4:  Vacancy + H₂¹⁸O → ¹⁸O_refill
```

**Prediction:** O₂ contains ¹⁶O from the catalyst lattice.
- Pure LOM: ¹⁶O₂ (m/z=32) + ¹⁸O¹⁶O (m/z=34) detected
- Mixed AEM+LOM: ratio of ¹⁸O₂:¹⁸O¹⁶O:¹⁶O₂ reveals LOM fraction

### The Observable Signal

```
m/z = 32:  ¹⁶O₂  (lattice oxygen, LOM indicator)
m/z = 34:  ¹⁶O¹⁸O (one lattice + one water oxygen)
m/z = 36:  ¹⁸O₂  (both from water, AEM pathway)
m/z = 44:  ¹²C¹⁶O₂ (CO₂ — carbon corrosion indicator, must track separately)
m/z = 40:  Ar (carrier gas, internal standard)
```

---

## Part 1: Experimental Design

### Catalyst Panel (5 to test)

Select to span the activity/stability space:

| Catalyst | Electrolyte | Rationale |
|----------|-------------|-----------|
| **MnO₂ (birnessite)** | 0.1M H₂SO₄ | Most acid-stable earth-abundant, Mn³⁺/Mn⁴⁺ cycling |
| **Ca₀.₁₅Mn₀.₈₅O_x** | 0.1M H₂SO₄ | PSII-inspired, test if Ca enables LOM |
| **FeCoNiCr HEA** | 0.1M H₂SO₄ | Best acid-stable HEA, test Cr effect on mechanism |
| **NiFe LDH** | 1M KOH | Known partial LOM in alkaline — positive control |
| **IrO₂ (commercial)** | 0.1M H₂SO₄ | Reference: known partial LOM, validate setup |

**Why these 5:**
- IrO₂ validates the setup (known result to compare against)
- NiFe LDH is an internal positive control (LOM confirmed in literature)
- MnO₂, Ca-MnO₂, FeCoNiCr are the earth-abundant acid candidates

### Isotope-Labeled Electrolyte

**H₂¹⁸O specifications:**
- Enrichment: ≥97 atom% ¹⁸O (from Sigma-Aldrich, catalog 329878, ~£200/10mL)
- Volume needed: 5 mL per experiment (hermetic cell)
- H₂¹⁸O diluted in natural H₂O reduces sensitivity — keep cell volume small

**Electrolyte preparation:**
- Acid: 0.1M H₂SO₄ prepared from H₂SO₄ (96%) + H₂¹⁸O
  - 28 μL conc. H₂SO₄ + 4.97 mL H₂¹⁸O → 0.1M H₂¹⁸SO₄ in H₂¹⁸O
  - NOTE: Use H₂¹⁸O for all dilutions — every μL of H₂¹⁶O dilutes the signal
- Alkaline: 1M KOH in H₂¹⁸O
  - Dissolve 0.056g KOH pellets in 1 mL H₂¹⁸O → 1M KOH in H₂¹⁸O
  - Caution: CO₂ from air rapidly forms K₂CO₃ in KOH — degas thoroughly

**CRITICAL: Natural abundance correction**
¹⁶O natural abundance = 99.76%, ¹⁸O natural abundance = 0.204%
At 97% ¹⁸O enrichment, ¹⁸O₂ signal has 3% ¹⁶O background contamination.
Any ¹⁶O₂ signal above 3% of ¹⁸O₂ signal indicates genuine LOM.

---

## Part 2: Cell Design

### DEMS (Differential Electrochemical Mass Spectrometry) Cell

This is the key instrument. Home-built or commercial cells both work.

**DEMS principle:**
1. Electrochemical cell with a PTFE membrane (0.02–0.1 μm pores)
2. Gas bubbles at electrode permeate through membrane into vacuum chamber
3. Mass spectrometer (residual gas analyser) detects m/z in real-time
4. Correlation of MS signal with current confirms electrochemical origin

**Cell schematic:**
```
         Potentiostat
              |
     ┌────────┴────────┐
     │   WE  |  RE  CE  │  ← 3-electrode electrochemical cell
     │                  │  ← 5 mL H₂¹⁸O electrolyte
     │    PTFE membrane │
     └────────┬─────────┘
              │ gas permeation
     ┌────────▼─────────┐
     │    Vacuum pump   │  ← 10⁻² mbar
     │    RGA / QMS     │  ← quadrupole mass spec, 1–50 amu
     └──────────────────┘
              │ m/z 32, 34, 36, 40, 44 signals vs. time
```

**PTFE membrane specifications:**
- Material: Hydrophobic PTFE (Millipore Fluoropore or Supor membrane)
- Pore size: 0.02–0.05 μm (smaller = slower response but less liquid breakthrough)
- Diameter: 5–10 mm (matches working electrode area)

**Alternatives if DEMS not available:**
- Online electrochemical mass spectrometry (OEMS): closed cell, headspace sampling
- GC-MS sampling of evolved gas (slower, but works without DEMS setup)
- DEMS requires most investment; GC-MS is accessible to most labs

### GC-MS Alternative Protocol (Accessible to All Labs)

If no DEMS cell available:

```
Equipment needed:
- Gas-tight syringe (1 mL, Hamilton or equivalent)
- Headspace vials (2 mL, crimp-seal)
- GC-MS with manual injection port
- Closed electrochemical cell (modified Schlenk flask)

Protocol:
1. Purge closed cell with Ar (30 min, 20 mL/min)
2. Add H₂¹⁸O electrolyte via syringe (minimize air exposure)
3. Apply OER conditions: 10 mA/cm² for 30 min
4. Sample 200 μL headspace with gas-tight syringe
5. Inject into GC-MS, measure m/z 32, 34, 36
6. Calculate LOM fraction from isotope ratios

Advantages: No special DEMS equipment, accessible at any university
Disadvantages: No real-time correlation, slower response, larger cell volume dilutes signal
```

---

## Part 3: Step-by-Step Protocol

### Day 1: Cell Assembly and Leak Testing

```
Equipment:
  □ DEMS cell (or GC-MS setup)
  □ H₂¹⁸O (97% enrichment, keep sealed under Ar)
  □ Potentiostat
  □ Hg/HgO reference (for alkaline) or Ag/AgCl (for acid)
  □ Pt counter electrode (in separate compartment!)
  □ Catalysts on GC electrode (0.5 mg/cm², 0.196 cm² GCE)
  □ Ar gas line (ultra-high purity, <1 ppm O₂)

Step 1: Assemble DEMS cell with natural H₂O (do not use ¹⁸O yet)
Step 2: Leak test by applying 50 mV above OER onset — detect m/z=32 signal
         If m/z=32 appears: O₂ from natural water detected — cell working
         If no signal: check membrane integrity, membrane wetting, vacuum
Step 3: Verify m/z=32/m/z=40 (Ar) ratio is stable before OER (~0)
Step 4: Once verified: replace with H₂¹⁸O electrolyte (minimal exposure to air)
```

### Day 2: Reference Measurements

```
Step 1: Run IrO₂ in H₂¹⁸O electrolyte (0.1M H₂SO₄)
  - CV activation: 0.9–1.8V vs. RHE, 50 mV/s, 50 cycles
  - CA: 1 mA/cm², 5 min — collect DEMS trace
  - Observe: m/z 36 (¹⁸O₂) rising immediately
             m/z 34 (¹⁸O¹⁶O) — small signal from lattice?
             m/z 32 (¹⁶O₂) — baseline or small LOM signal

Step 2: Quantify LOM fraction for IrO₂
  LOM% = [m/z(34)/2 + m/z(32)] / [m/z(36) + m/z(34) + m/z(32)] × 100
  Literature expectation for IrO₂: LOM% ≈ 30–50% depending on conditions

Step 3: Compare your IrO₂ LOM% to literature (Kasian et al. 2019, Reier et al. 2019)
  If match: experimental setup validated
  If different: investigate cell volume, membrane pore size, enrichment level
```

### Day 3–5: Earth-Abundant Catalyst Measurements

For each catalyst (MnO₂, Ca-MnO₂, FeCoNiCr HEA):

```
Step 1: Fresh H₂¹⁸O electrolyte (5 mL, newly prepared under Ar)
        CRITICAL: Replace electrolyte entirely between catalysts
        ¹⁸O exchange between catalyst lattice and ¹⁶O in old electrolyte
        would contaminate measurements

Step 2: Mount electrode, establish vacuum, check background m/z signals

Step 3: Activation: 20 CV cycles (0.9–1.8V vs. RHE, 50 mV/s)
        During CV: monitor m/z continuously — note when signal appears

Step 4: Steady-state DEMS:
        CA protocol: 0.5, 1, 2, 5, 10 mA/cm² (3 min each, DEMS recording)
        This gives current-dependent LOM fraction — key mechanistic insight

Step 5: Potential-dependent DEMS:
        Slow LSV: 0 → 600 mV overpotential at 1 mV/s (DEMS recording)
        Note potential at which ¹⁶O₂ first appears
        Note if ¹⁶O₂:¹⁸O₂ ratio changes with potential

Step 6: Collect electrolyte (1 mL) for ICP-MS — check metal dissolution
        This correlates LOM activity with dissolution
        Hypothesis: High LOM → high vacancy formation → potentially more dissolution

Step 7: Repeat 3 times (n=3) with fresh electrodes and electrolyte each time
```

### Day 6: NiFe LDH in Alkaline (Positive Control)

Same protocol as above but:
- Electrolyte: 1M KOH in H₂¹⁸O (5 mL)
- Reference: Hg/HgO in 1M KOH
- Expected: LOM% > 50% (literature value for NiFe LDH in alkaline)

---

## Part 4: Data Analysis

### Calculating LOM Fraction

```python
import numpy as np
import pandas as pd

def calculate_lom_fraction(m32, m34, m36, natural_18O_abundance=0.00204, enrichment=0.97):
    """
    Calculate LOM fraction from DEMS mass signals.

    Args:
        m32: DEMS signal at m/z=32 (16O2, arb. units)
        m34: DEMS signal at m/z=34 (16O18O, arb. units)
        m36: DEMS signal at m/z=36 (18O2, arb. units)
        natural_18O_abundance: 18O in natural water (0.00204)
        enrichment: 18O enrichment of labeled water (0.97)

    Returns:
        lom_fraction: fraction of O2 involving lattice oxygen (0-1)
        lom_pct: percentage
    """
    # Correct for natural abundance background
    # In 97% enriched water, ~3% of O is still 16O
    # This produces background m32 and m34 even without LOM
    bg_correction = (1 - enrichment) / enrichment  # ≈ 0.031

    # The true LOM signal = observed m32/m36 - expected from enrichment alone
    m32_bg = m36 * bg_correction**2      # Expected 16O2 from 3% 16O in water
    m34_bg = m36 * 2 * bg_correction     # Expected 16O18O from 3% 16O in water

    m32_lom = np.maximum(m32 - m32_bg, 0)
    m34_lom = np.maximum(m34 - m34_bg, 0)

    # LOM contributes:
    # - 16O2 (two lattice oxygens): contributes m32 fully
    # - 16O18O (one lattice + one water): contributes m34 at 50% (other half is AEM)
    lom_signal = m32_lom + 0.5 * m34_lom
    total_o2   = m32_lom + 0.5 * m34_lom + m36 + 0.5 * m34_lom  # count all O atoms

    lom_fraction = lom_signal / (total_o2 + 1e-12)
    return lom_fraction, lom_fraction * 100


# Example: Apply to time-series DEMS data
def analyse_dems_timeseries(time, current, m32, m34, m36, catalyst_name):
    """
    Analyse DEMS time-series data.
    All arrays should be same length (one point per second or similar).
    """
    # Only analyse when OER current is flowing
    oer_mask = current > 0.5  # mA/cm2 threshold

    lom_frac, lom_pct = calculate_lom_fraction(m32, m34, m36)

    results = {
        'catalyst': catalyst_name,
        'mean_lom_pct': float(np.mean(lom_pct[oer_mask])),
        'std_lom_pct':  float(np.std(lom_pct[oer_mask])),
        'max_lom_pct':  float(np.max(lom_pct[oer_mask])),
        'onset_potential': None,  # Fill in manually from LSV data
    }

    print(f"\n{catalyst_name}:")
    print(f"  LOM fraction: {results['mean_lom_pct']:.1f} +/- {results['std_lom_pct']:.1f} %")
    print(f"  Max LOM:      {results['max_lom_pct']:.1f} %")

    interpretation = (
        "STRONG LOM — scaling relations likely broken" if results['mean_lom_pct'] > 30
        else "PARTIAL LOM — some scaling relation escape" if results['mean_lom_pct'] > 10
        else "WEAK/NO LOM — AEM dominant, scaling relations hold"
    )
    print(f"  Interpretation: {interpretation}")

    return results


# Example with synthetic data (replace with real DEMS output):
if __name__ == '__main__':
    t = np.linspace(0, 600, 600)  # 600 seconds
    current = np.where(t > 60, 10.0, 0.0)  # 10 mA/cm2 after 60s

    # Simulate NiFe LDH (strong LOM ~50%)
    m36_base = np.where(t > 60, 1000, 5)  # 18O2 baseline
    m34_nife = np.where(t > 60, 200, 1)   # 16O18O — from partial LOM
    m32_nife = np.where(t > 60, 40, 0.5)  # 16O2 — from full LOM

    # Simulate MnO2 (weak LOM ~5%)
    m34_mn = np.where(t > 60, 30, 1)
    m32_mn = np.where(t > 60, 5, 0.5)

    # Simulate FeCoNiCr HEA (unknown — this is what we want to find)
    # Placeholder: assume intermediate ~15%
    m34_hea = np.where(t > 60, 80, 1)
    m32_hea = np.where(t > 60, 20, 0.5)

    all_results = []
    for name, m34, m32 in [
        ('IrO2 (reference)',    np.where(t>60, 150, 1), np.where(t>60, 30, 0.5)),
        ('NiFe LDH (control)', m34_nife, m32_nife),
        ('MnO2 birnessite',    m34_mn,   m32_mn),
        ('Ca-MnO2',            np.where(t>60, 50, 1), np.where(t>60, 12, 0.5)),
        ('FeCoNiCr HEA',       m34_hea,  m32_hea),
    ]:
        r = analyse_dems_timeseries(t, current, m32, m34, m36_base, name)
        all_results.append(r)

    df = pd.DataFrame(all_results)
    print("\n\nSUMMARY TABLE:")
    print(df[['catalyst','mean_lom_pct','std_lom_pct']].to_string(index=False))
    print("\nNote: Values above are synthetic. Replace with real DEMS data.")
```

Save this as: `code/dems_analysis.py`

---

## Part 5: Interpreting Results

### Decision Tree

```
For each catalyst:

Is LOM% > 30%?
  YES → Significant LOM
    Is the catalyst acid-stable (from ICP-MS)?
      YES → *** MAJOR FINDING — acid-stable LOM catalyst ***
            → Deep dive into composition, file patent, write paper
      NO  → Important mechanistic result, stability challenge remains

  Is LOM% 10–30%?
    → Partial LOM — promising
    → Investigate: does LOM fraction correlate with overpotential reduction?
    → DFT: compute vacancy formation energy, compare to LOM% from experiment

  Is LOM% < 10%?
    → AEM dominant — scaling relations hold for this material
    → Lower priority for further investigation
```

### Expected Results and Implications

| Catalyst | Expected LOM% | If Confirmed | Implication |
|----------|--------------|--------------|-------------|
| IrO₂ (ref) | 30–50% | Setup validated | Reference only |
| NiFe LDH (alkaline) | 40–60% | Literature confirmed | Setup validated |
| MnO₂ (acid) | 5–15% | Partial LOM in acid? | Would be first confirmation |
| Ca-MnO₂ (acid) | 10–25% | Ca enables LOM? | PSII mechanism support |
| FeCoNiCr HEA (acid) | Unknown | — | This is the key unknown |

**The result that would change the field:**
FeCoNiCr HEA shows LOM% > 20% in acid AND dissolution < 5 ng/cm²/s.
This would prove: acid-stable + LOM-active catalyst exists → scaling can be broken in acid.

---

## Part 6: Cost and Timeline

### Budget Estimate

| Item | Cost | Notes |
|------|------|-------|
| H₂¹⁸O (10 mL, 97%) | £200–280 | Sigma-Aldrich, sufficient for 5–8 experiments |
| PTFE membrane (50 pk) | £80 | Millipore Fluoropore |
| Gas-tight syringes | £60 | If using GC-MS alternative |
| Catalyst synthesis materials | £150 | For 5 catalysts |
| ICP-MS analysis (outsourced) | £200 | 15 samples, £12–15 each |
| **Total** | **£690–770** | Entire experiment |

This is an extraordinarily cheap experiment for the potential impact.

### Timeline

```
Week 1:  Synthesise 5 catalysts (parallel), order H₂¹⁸O
Week 2:  Build/calibrate DEMS cell, test with natural water
Week 3:  Run IrO₂ and NiFe LDH controls
Week 4:  Run all 3 earth-abundant acid OER candidates (3× each)
Week 5:  Data analysis, ICP-MS results
Week 6:  Interpretation, write results section
```

---

## Part 7: Publication Strategy

### Scenario A: LOM found in acid-stable catalyst (best case)

**Paper: "Lattice Oxygen Mechanism in Acid OER: First Observation in Earth-Abundant Catalyst"**
- Journal: Nature Catalysis or Nature Energy
- Impact: Immediate field-shaping — proof that AEM scaling constraint is not universal in acid
- Follow-up: DFT to understand why this composition enables LOM
- Patent: composition + any synthesis specifics before submission

### Scenario B: LOM found in some materials, not all (likely)

**Paper: "Correlation of Lattice Oxygen Participation with OER Activity Across Earth-Abundant Catalyst Classes"**
- Journal: ACS Catalysis or JACS
- Impact: Establishes LOM as design target for acid OER
- Framework: LOM fraction as new descriptor alongside η₁₀ and Tafel slope

### Scenario C: No LOM found in any earth-abundant acid catalyst

**Paper: "AEM Dominance in Earth-Abundant Acid OER: Implications for Overpotential Scaling"**
- Journal: Journal of Physical Chemistry Letters or ACS Energy Letters
- Impact: Negative result — still publishable because it rules out a design pathway
- Conclusion: Must focus on breaking scaling differently (dual-site, Lewis acid stabilization)

**All three scenarios are publishable.** The experiment is worth running regardless.
