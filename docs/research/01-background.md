# 01 — Background: Electrochemistry Primer & Performance Metrics

## The Electrochemistry of Water Splitting

Water electrolysis consists of two coupled half-reactions:

### Cathode — Hydrogen Evolution Reaction (HER)

**In acid (PEM):**
```
2H⁺ + 2e⁻ → H₂        E° = 0.00 V vs. RHE
```

**In alkaline (AEL / AEM):**
```
2H₂O + 2e⁻ → H₂ + 2OH⁻    E° = 0.00 V vs. RHE
```

**Mechanism (Volmer-Heyrovsky or Volmer-Tafel):**
1. **Volmer step:** H⁺ + e⁻ → H*  (adsorption)
2. **Heyrovsky step:** H* + H⁺ + e⁻ → H₂  (electrochemical desorption)
   **OR**
   **Tafel step:** 2H* → H₂  (chemical desorption)

The rate-limiting step determines the Tafel slope:
- Volmer-limited: ~120 mV/dec
- Heyrovsky-limited: ~40 mV/dec
- Tafel-limited: ~30 mV/dec

### Anode — Oxygen Evolution Reaction (OER)

**In acid:**
```
2H₂O → O₂ + 4H⁺ + 4e⁻    E° = +1.23 V vs. RHE
```

**In alkaline:**
```
4OH⁻ → O₂ + 2H₂O + 4e⁻   E° = +1.23 V vs. RHE
```

**Mechanism (4-electron, adsorbate evolution mechanism - AEM):**
1. OH* formation
2. O* formation
3. OOH* formation  ← rate-limiting for most catalysts
4. O₂ release

**Lattice Oxygen Mechanism (LOM)** — alternative pathway bypassing OOH*:
- Can break scaling relations
- Involves bulk oxygen participation
- Observed in Ni-based, Co-based perovskites

---

## The Scaling Relations Problem

The fundamental thermodynamic constraint binding OER catalysts:

```
ΔG(OOH*) ≈ ΔG(OH*) + 3.2 eV  (± 0.2 eV, ~80% of materials)
```

This means that for any catalyst following the AEM:
- **Theoretical minimum overpotential: ~0.37 V** (vs. ~0 V for ideal catalyst)
- No single-site catalyst obeying scaling relations can beat this

**Strategies to escape:**
- Dual-site catalysts (OOH forms across two adjacent sites)
- LOM pathway (avoids OOH* entirely)
- Non-covalent stabilization of OOH*
- Strain/ligand field engineering

The OER scaling wall is why IrO₂ (η ≈ 270 mV) remains dominant — it sits closest to
the volcano peak and has acceptable stability.

---

## Performance Metrics — Definitions

### Primary Metrics

| Metric | Symbol | Unit | Definition | Benchmark |
|--------|--------|------|------------|-----------|
| Overpotential | η | mV | Extra voltage above thermodynamic minimum | η₁₀ at 10 mA/cm² |
| Tafel slope | b | mV/dec | Slope of η vs log(j) | Lower = better kinetics |
| Exchange current density | j₀ | mA/cm² | Rate at equilibrium | Higher = more active |
| Turnover frequency | TOF | s⁻¹ | H₂ or O₂ per active site per second | Normalizes for surface area |
| Faradaic efficiency | FE | % | Fraction of charge → product | Should be >95% |

### Stability Metrics

| Metric | Definition | Challenge |
|--------|------------|-----------|
| Chronoamperometry | Current vs. time at fixed V | 100h minimum for credible claim |
| Chronopotentiometry | Voltage vs. time at fixed j | More industrially relevant |
| Accelerated stress test (AST) | Potential cycling protocol | Standardization lacking |
| ICP-MS after test | Dissolved metal concentration | Often omitted in papers |
| Post-mortem XPS/TEM | Surface structure after test | Reveals reconstruction |

### Common Mistakes in the Literature

1. **Geometric vs. ECSA normalization** — reporting η₁₀ on geometric area inflates performance of high-surface materials
2. **Omitting stability** — >60% of HER papers report <10h stability data
3. **pH inconsistency** — comparing catalysts across different pH without RHE correction
4. **Loading effects** — higher loading can mask poor intrinsic activity
5. **IR compensation** — failing to correct for electrolyte resistance (can misrepresent η by 50+ mV)

---

## Electrolysis Technologies

### 1. Alkaline Electrolysis (AEL)
- **Electrolyte:** 25–30 wt% KOH or NaOH, ~80°C
- **Membrane:** Asbestos (old) / Zirfon (modern)
- **Current density:** 200–400 mA/cm² (commercial), up to 1 A/cm² (R&D)
- **Catalyst freedom:** More tolerant of earth-abundant materials
- **Maturity:** 100+ year history, GW-scale deployed
- **Challenge:** Low current density, slow startup/shutdown

### 2. PEM Electrolysis
- **Electrolyte:** Nafion membrane, highly acidic
- **Current density:** 1–3 A/cm² (commercial)
- **Advantage:** High purity H₂, dynamic response, compact
- **Challenge:** REQUIRES acid-stable catalysts → forces PGM use
- **Bottleneck:** IrO₂ for OER is the hardest to replace

### 3. Anion Exchange Membrane (AEM)
- **Newest technology** — combines alkaline chemistry with membrane architecture
- Could allow earth-abundant catalysts at PEM current densities
- **Key challenge:** Membrane durability at elevated temperature/pH
- Companies: Enapter, Markel (Advent), Evonik
- **Most exciting space for new catalyst development**

### 4. High-Temperature (SOEC)
- **Operating temperature:** 700–900°C
- **Electrolyte:** Yttria-stabilized zirconia (YSZ)
- **Advantage:** Uses waste heat, better thermodynamics
- **Catalysts:** Perovskites (LSCF, LSC), Ni-cermet
- Different materials challenge — out of scope here

---

## Cost Context

| Component | PEM cost contribution | Replacement target |
|-----------|----------------------|-------------------|
| IrO₂ (OER) | ~$50–200/kW | Any non-PGM with η < 350 mV, 50,000h |
| Pt (HER) | ~$20–80/kW | Any non-PGM with η < 100 mV, 50,000h |
| Nafion membrane | ~$100–300/kW | AEM alternative |

**Target for green H₂ at $2/kg:** Stack cost < $300/kW, which requires Ir loading
reduction from ~2 mg/cm² → < 0.1 mg/cm² OR complete replacement.

---

## How to Read This Document

- **η₁₀** = overpotential at 10 mA/cm² in mV. Lower is better. Pt reference: ~30–50 mV.
- **Acid/Alkaline** = electrolyte context. Acid results often better but acid stability is harder.
- All overpotentials reported vs. RHE unless stated.
- Performance ranges reflect literature variation — synthesis matters enormously.
