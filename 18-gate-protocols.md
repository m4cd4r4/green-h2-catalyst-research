# 18 — Gate Protocols: Experimental Decision Framework

**Date:** March 2026
**Depends on:** Doc 17 (gap closure roadmap), Doc 16 (synthesis guide)
**Code:** `gate1_phase_predictor.py`, `gate2_eg_tuner.py`, `gate3_lifetime_projector.py`

---

## Overview

Three sequential go/no-go gates control the critical path. Each gate is a hard decision point: if it fails, you pivot before spending weeks on downstream experiments.

```
SYNTHESISE Ca-Mn-W composite (doc 16, P3 protocol)
         │
    ─────▼─────
    │  GATE 1  │ ← Weeks 1-8
    │ CaWO4?   │ XRD 28.7 deg + Raman 921 cm-1
    ─────┬─────
        │
     GO ├──────────────────────────────────────────→ NO-GO
        │                                             └ Adjust synthesis (pH, T, W content)
        ▼
    ─────▼─────
    │  GATE 2  │ ← Weeks 8-20
    │ Activity │ H2/N2 anneal → eg → eta_10 < 310 mV
    ─────┬─────
        │
     GO ├──────────────────────────────────────────→ NO-GO
        │                                             └ Adjust anneal conditions
        ▼
    ─────▼─────
    │  GATE 3  │ ← Weeks 20-52
    │Stability │ 500h pulsed CP → D_cum < 25 ug/cm2
    ─────┬─────
        │
     GO └──────────────────────────────────────────→ YEAR 2 MEA INTEGRATION
                                                NO-GO → IrOx sub-monolayer bridge
```

---

## Gate 1 — CaWO₄ Phase Verification

**Weeks 1–8 | Code: `gate1_phase_predictor.py`**

### What to measure

| Measurement | What it tells you | Pass criterion |
|-------------|-------------------|----------------|
| XRD (Cu Kα) | CaWO₄ scheelite present? | Peak at 2θ = 28.7° ± 0.15° (intensity > 5% of MnO₂ birnessite peak) |
| Raman | CaWO₄ surface confirmed? | Peak at 921 cm⁻¹ (W–O stretch) distinct from 650 cm⁻¹ (MnO₂) |
| XRF or ICP | Bulk Ca:W:Mn ratio matches target? | Ca/W ratio ± 15% of nominal |
| BET | Surface area adequate? | > 60 m²/g |
| TEM-EDX | Local Ca+W co-location? | Ca and W co-localised on <10 nm scale |

### What the code predicts

`gate1_phase_predictor.py` models:
- **Supersaturation S**: ratio Q/Ksp at your synthesis pH and temperature
- **Yield fraction f_CaWO₄**: Avrami nucleation-growth model
- **Competition with MnWO₄** (huebnerite): unfavourable competing phase
- **Synthetic XRD fingerprint**: what your diffractogram should look like if CaWO₄ formed

**Key model output (P3 synthesis — pH 8, 80°C, 4h):**

| Composition | S_CaWO₄ | f_CaWO₄ predicted | XRD detectable | Gate 1 |
|-------------|---------|-------------------|----------------|--------|
| Ca=0.11, Mn=0.55, W=0.34 | ~520 | 0.12–0.16 | YES | GO |
| Ca=0.08, Mn=0.56, W=0.31 | ~290 | 0.07–0.09 | MARGINAL | MARGINAL |
| Ca=0.15, Mn=0.32, W=0.29, Ti=0.25 | ~680 | 0.14–0.18 | YES | GO |

### Synthesis variables and their effect

| Variable | Increase → | Decrease → |
|----------|-----------|------------|
| pH (5–10) | Higher S, more CaWO₄, BUT risk of Ca(OH)₂ competing | Less CaWO₄, more WO₃ |
| Temperature (60–180°C) | Faster kinetics but lower S (Ksp rises) | Optimal ~70–90°C |
| Time (2–12h) | More CaWO₄ yield asymptotes after 6–8h | Less yield |
| W content | More CaWO₄ (more W available) | Less |
| Ca content | More CaWO₄ up to x_Ca ≈ 0.15 | Less |

**Optimal synthesis window (from model sweep):**
- pH 7.5–9.0 (sweet spot pH 8.0)
- T = 70–90°C (sweet spot 80°C)
- Time ≥ 4h (yield plateaus after 6h)
- x_Ca × x_W > 0.035 (empirical nucleation threshold)

### If Gate 1 fails

```
f_CaWO4 < 0.05 OR XRD peak absent:
├─ Raise pH to 8.5-9.0 → increases WO4^2- fraction → higher S
├─ Lower temperature to 65°C → lower Ksp → higher S
├─ Add post-synthesis anneal: 180°C/4h in air → crystallises amorphous CaWO4
├─ Increase W content to x_W = 0.40-0.45
└─ Last resort: pre-form CaWO4 nanoparticles separately,
   then mix with Mn-oxide precursor during synthesis
```

---

## Gate 2 — eg Electron Occupancy and Activity

**Weeks 8–20 | Code: `gate2_eg_tuner.py`**

### Physical basis

The OER activity of Mn-oxide follows a Sabatier volcano with optimal eg ≈ 0.52:
- **Pure MnO₂ (Mn⁴⁺)**: eg = 0 → binds OER intermediates too weakly → η₁₀ ≈ 500–600 mV
- **Mn₂O₃ (Mn³⁺)**: eg = 1 → binds too strongly → η₁₀ ≈ 380–420 mV
- **Ca-doped MnO₂**: eg ≈ 0.2–0.4 → η₁₀ ≈ 330–400 mV
- **Optimally annealed**: eg ≈ 0.5 → η₁₀ ≈ 260–300 mV

### Two levers for eg tuning

**Lever 1 — Ca doping (intrinsic, from synthesis):**
Ca²⁺ ions in the birnessite interlayer require Mn³⁺ in the octahedral sheet for charge compensation. Each Ca²⁺ creates approximately 2 Mn³⁺ sites.

```
eg_Ca = min(0.75, 2 × x_Ca / x_Mn)

For Ca=0.11, Mn=0.55: eg_Ca ≈ 0.40
For Ca=0.15, Mn=0.32: eg_Ca ≈ 0.75 (near stability limit — do not over-reduce)
```

**Lever 2 — H₂/N₂ anneal:**
Post-synthesis reduction in dilute H₂ to promote Mn⁴⁺ → Mn³⁺:

```
Mn3+ fraction after anneal: x(t) = x_eq + (x0 - x_eq) × exp(-k_total × t)
where x_eq = k_fwd / (k_fwd + k_bwd)
      k_fwd ∝ p_H2 × exp(-72,000 / RT)
```

### Optimal anneal protocol (from model optimisation)

| Composition | T_opt (°C) | H₂% | Time (h) | eg_opt | η₁₀ predicted |
|-------------|-----------|-----|----------|--------|----------------|
| Ca=0.11, Mn=0.55, W=0.34 | 210–230 | 5% | 2–3 | 0.50–0.55 | 270–295 mV |
| Ca=0.15, Mn=0.32, W=0.29, Ti=0.25 | 180–200 | 5% | 1.5–2 | 0.52 | 260–285 mV |
| Ca=0.08, Mn=0.56, W=0.31 | 220–240 | 5% | 3–4 | 0.48 | 275–305 mV |

**Warning**: Do not exceed Mn³⁺ fraction > 0.75 — above this threshold, Mn₃O₄ (hausmannite) forms and dissolves rapidly in acid. Monitor with XPS.

### What to measure

| Measurement | Target | Method |
|-------------|--------|--------|
| XPS Mn 2p₃/₂ | Peak at 641.5 eV (Mn³⁺); ratio to 642.2 eV (Mn⁴⁺) | XPS |
| XPS Mn 3s splitting | Δ = 5.5–5.8 eV for Mn³⁺/Mn⁴⁺ mix | XPS |
| OER polarisation | η₁₀ < 310 mV in 0.5 M H₂SO₄ | RDE, 1600 rpm |
| Tafel slope | < 65 mV/dec indicates charge-transfer limited | OER curve |
| Mn 3s splitting vs eg | Map measured splitting to eg for calibration | Literature |

### Gate 2 pass criterion

```
eta_10 < 310 mV (RDE, 0.5 M H2SO4, pH 0-1, 25 C)
AND eg > 0.30 (XPS-derived Mn3+/Mn4+ ratio)
AND Mn3+ fraction <= 0.75 (structural stability)
```

### If Gate 2 fails (η₁₀ > 310 mV after optimal anneal)

```
eta > 310 mV:
├─ Increase anneal T by 20°C increments (max 260°C)
├─ Extend time to 4-6h
├─ Switch to 8-10% H2 (maintain safety margin; use H2 detector)
├─ Check for MnWO4 contaminant (Raman 905/885 cm-1) — it suppresses activity
├─ Check BET: surface area < 40 m2/g will show eta > 350 mV regardless of eg
└─ If eg > 0.7 but eta still high: W is blocking OER sites; reduce x_W to 0.25-0.28
```

---

## Gate 3 — 500h Dissolution and Lifetime

**Weeks 20–52 | Code: `gate3_lifetime_projector.py`**

### Dissolution model

`gate3_lifetime_projector.py` implements:

1. **Multi-phase selective dissolution**: Mn dissolves fastest (k₀ = 28 µg/cm²/h), CaWO₄ slowest (k₀ = 0.55 µg/cm²/h)
2. **Surface enrichment**: as Mn depletes from surface, CaWO₄/TiO₂ fraction at surface rises → self-passivation with timescale τ ≈ 55h
3. **Power law kinetics**: D(t) = D₀ × t^(−α), α ≈ 0.35–0.60 (fitted from data)
4. **Pulsed CP factor**: 59min/1min cycle gives ~30% OC recovery → ~1.6–2.0× lifetime extension

**Key prediction (Ca=0.11, Mn=0.55, W=0.34, f_CaWO₄=0.103):**

| Protocol | Cum. dissolution 500h | D_ss (after 500h) | P50 lifetime |
|----------|----------------------|-------------------|--------------|
| Continuous CP | ~35–45 µg/cm² | 0.08–0.15 µg/cm²/h | 800–1,500h |
| Pulsed CP (59/1) | ~18–28 µg/cm² | 0.04–0.09 µg/cm²/h | 1,500–3,500h |
| IrO₂ reference | ~5 µg/cm² | 0.01 µg/cm²/h | >50,000h |

### What to measure during the 500h test

**Setup:**
- Electrolyte: 0.5 M H₂SO₄, 25°C, N₂-purged
- Protocol: pulsed CP at 10 mA/cm², 59min on / 1min OC
- Collection: 5 mL aliquot every 24h (replace with fresh electrolyte)

**ICP-MS monitoring (aliquots at: 1, 3, 6, 12, 24, 48, 100, 200, 500h):**

| Analyte | Expected at steady state | Alert if |
|---------|-------------------------|----------|
| Mn | 0.01–0.05 µg/cm²/h | > 0.10 µg/cm²/h after 100h |
| W | 0.005–0.02 µg/cm²/h | > 0.05 µg/cm²/h |
| Ca | 0.001–0.005 µg/cm²/h | > 0.02 µg/cm²/h |
| Ti | < 0.002 µg/cm²/h | — |

**Electrochemical monitoring (every 24h):**
- EIS at η = 300 mV: R_ct should stabilise after 50h
- OER polarisation curve: η₁₀ should plateau or improve (as eg tunes in situ)
- Tafel slope: increasing slope → degradation

**Post-test characterisation:**
- XRD: CaWO₄ peak retention (quantify phase fraction at 500h vs. fresh)
- Raman: 921 cm⁻¹ peak still present?
- SEM cross-section: film thickness reduction rate
- TEM-EDX: surface composition (expect Ca+W enrichment if mechanism is operating)

### Gate 3 pass criterion

```
1. D_cumulative(500h) <= 25 ug/cm2  (pulsed CP)
2. D_ss(450-500h)     <= 0.10 ug/cm2/h
3. Projected P50 lifetime >= 1,000h
```

### If Gate 3 fails

**If D_ss > 0.10 µg/cm²/h after 200h (CaWO₄ mechanism insufficient):**

| Intervention | Cost | Expected D_ss reduction |
|--------------|------|------------------------|
| Increase CaWO₄ loading (re-synthesise with x_Ca=0.15) | 2 weeks | 30–50% |
| Add TiO₂ matrix (x_Ti = 0.20–0.25) | 3 weeks | 20–35% |
| IrOₓ sub-monolayer (0.05 µg Ir/cm²) | 1 week | 60–80% |
| Tighten pulse: 29min/1min | In-situ (no resynth) | 15–25% |
| ALD TiO₂ coating (3–5 nm) | 2 weeks (ALD access) | 40–60% (risk: blocks OER) |

**Recommended sequence:**
1. Try tighter pulse first (zero cost, in-situ)
2. Add TiO₂ matrix (re-synthesise x_Ti = 0.20)
3. If still failing: IrOₓ sub-monolayer (accepts minimal Ir use)

---

## Running the Gate Code

All three scripts are independent and produce self-contained outputs:

```bash
# Gate 1: CaWO4 formation under P3 synthesis conditions
cd code
python gate1_phase_predictor.py
# -> results_gate1_phase.png (synthesis condition maps)
# -> results_gate1_xrd.png (synthetic XRD fingerprints)
# -> results_gate1_synthesis.csv (full condition sweep, 216 conditions)

# Gate 2: eg tuning for optimal anneal
python gate2_eg_tuner.py
# -> results_gate2_eg.png (volcano, anneal maps, treatment waterfall)
# -> results_gate2_optimization.csv (optimal T/H2/time per composition)

# Gate 3: 500h dissolution and lifetime projection
python gate3_lifetime_projector.py
# -> results_gate3_lifetime.png (rate curves, phase breakdown, P50 projection)
# -> results_gate3_projection.csv (per-composition lifetime table)
```

**Feeding real data back into Gate 3:**

Replace `integrate_dissolution(phases, ...)` with a hybrid model by passing your first 50h of real ICP-MS data:

```python
# In gate3_lifetime_projector.py:
from gate3_lifetime_projector import fit_power_law, project_lifetime
import pandas as pd

# Load your real ICP-MS dissolution data
df_real = pd.read_csv("my_icp_ms_50h.csv")
# columns: t_h, D_total_ug_cm2_h, D_cumulative_ug_cm2

# Fit power law to short-term data
D0, alpha = fit_power_law(df_real, t_start_h=5.0)

# Project to 10,000h
proj = project_lifetime(df_real, mass_budget_ug=100.0, t_budget_h=10_000)
print(f"P50 lifetime: {proj['p50_lifetime_h']:.0f} h")
```

---

## Expected Timeline

| Week | Activity | Gate |
|------|----------|------|
| 1–2 | Synthesise Ca(0.11)Mn(0.55)W(0.34) by P3 protocol | — |
| 2–3 | XRD, Raman, BET, ICP elemental verification | Gate 1 |
| 3 | **GATE 1 GO/NO-GO decision** | **Gate 1** |
| 4–6 | If GO: H₂/N₂ annealing series (150–250°C, 1–6h) | — |
| 6–8 | XPS Mn 2p₃/₂, OER RDE polarisation curves | Gate 2 |
| 8 | **GATE 2 GO/NO-GO decision** | **Gate 2** |
| 9–30 | 500h pulsed CP (59min/1min), ICP-MS aliquots | — |
| 10–14 | Fit power law at 50h, run gate3 lifetime projector | Gate 3 |
| 30 | **GATE 3 GO/NO-GO decision** | **Gate 3** |
| 31+ | If GO: scale-up synthesis (100g batch), MEA fabrication | Year 2 |

**Wall time note**: The 500h pulsed CP test takes 21 calendar days minimum. Run it immediately after Gate 2, in parallel with synthesis of alternative compositions (Gates 1+2 for Ti-rich compositions).

---

## Contingency Paths

### If all three gates fail

The CaWO₄ mechanism is likely insufficient at room-temperature synthesis. Switch to:

1. **Hydrothermal route** (doc 16, P1 protocol): 160°C, 12h — higher crystallinity CaWO₄
2. **Atomic layer deposition (ALD) TiO₂ protection**: 3–5 nm coating, post-synthesis
3. **Minimal Ir bridge**: 0.1 µg/cm² IrOₓ sub-monolayer (electrodeposited) — reduces Ir content 50× vs. commercial MEAs while achieving IrO₂-competitive D_ss

### Decision tree for resource allocation

```
Gate 1 passed? → Gate 2 passed? → Gate 3 passed? → YEAR 2 MEA
     │                │                └── FAIL → IrOx bridge → Gate 3 retry
     │                └── FAIL → Re-anneal → Gate 2 retry
     └── FAIL → Re-synthesise → Gate 1 retry
                    OR
                Pivot to ALD-TiO2 strategy (parallel track)
```

---

*Code outputs, model parameters, and pass criteria calibrated against published ICP-MS dissolution data for Mn-oxide electrocatalysts in 0.5 M H₂SO₄. All predictions require experimental validation.*
