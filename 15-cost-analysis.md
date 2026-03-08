# 15 — Techno-Economic Analysis: Catalyst Performance to H₂ Cost

## Purpose

Translates electrochemical performance metrics into real-world economics.
**Key question: How much does catalyst performance affect green hydrogen cost ($/kg)?**

All calculations use public data and first-principles cost modelling.
Numbers are transparent so reviewers can reproduce them.

---

## 1. The Cost Equation

```
LCOH ($/kg H₂) = (CAPEX_annualised + OPEX_annual) / annual_H2_production
```

The catalyst directly affects:
1. **Overpotential** → electricity cost per kg H₂
2. **Catalyst lifetime** → annualised CAPEX (stack replacement frequency)
3. **Current density at given voltage** → throughput and footprint

---

## 2. Baseline Parameters (2026)

| Parameter | Value | Source |
|-----------|-------|--------|
| Electricity price (industrial) | $0.040/kWh | EU industrial avg 2025 |
| Electricity price (renewables PPA) | $0.025/kWh | Solar PPA, 2025 |
| Electrolyzer CAPEX (AEL) | $700/kW | IRENA 2024 |
| Electrolyzer CAPEX (PEM) | $1,100/kW | IRENA 2024 |
| Stack fraction of CAPEX | 40% | Industry standard |
| Stack lifetime (IrO₂ PEM, current) | 40,000h | Commercial ~2024 |
| Stack lifetime (IrO₂ PEM, DOE target) | 80,000h | DOE H₂ Shot |
| Stack lifetime (NiFe LDH AEL, lab) | 500h | Literature median |
| Stack lifetime (NiMo AEL, commercial) | 50,000h | Industrial AEL |
| Operating current density | 1,000 mA/cm² (PEM) | Standard |
| Faradaic efficiency | 98% | Typical |
| System efficiency (HHV) | 67% | PEM; 63% AEL |
| Capacity factor | 90% | Baseload renewable |

---

## 3. Overpotential → Electricity Cost

Cell voltage at operating current:
```
V_cell = 1.23 V (thermo) + η_OER + η_HER + η_ohmic
       = 1.23 + η_OER + 0.050 + 0.150   [V]
```

Specific energy consumption:
```
SEC = V_cell × 26.8 / η_Faradaic   [kWh/kg H₂]
```

### Overpotential sensitivity table

| OER catalyst | η_OER | V_cell | SEC (kWh/kg) | Cost at $0.04/kWh | Δ vs IrO₂ |
|-------------|--------|--------|--------------|-------------------|------------|
| IrO₂ PEM (best) | 250 mV | 1.650 V | 52.6 | $2.10/kg | — |
| IrO₂ PEM (typical) | 280 mV | 1.680 V | 53.5 | $2.14/kg | +$0.04 |
| NiFe LDH (best lab) | 250 mV | 1.650 V | 52.6 | $2.10/kg | $0.00 |
| NiFe LDH (typical) | 310 mV | 1.710 V | 54.5 | $2.18/kg | +$0.08 |
| Poor catalyst | 400 mV | 1.800 V | 57.4 | $2.30/kg | +$0.20 |
| Hypothetical ideal | 150 mV | 1.550 V | 49.4 | $1.98/kg | −$0.12 |

**Key insight:** A 100 mV improvement in η_OER saves **$0.08–0.12/kg** at industrial electricity prices.
At $0.025/kWh (renewable PPA) these savings scale proportionally downward — electricity is cheaper but still dominates.

---

## 4. Catalyst Lifetime → Capital Cost

### Stack replacement cost formula

```
Annual stack CAPEX ($/yr) = Stack_cost / Lifetime_hours × Hours_per_year
Stack_cost = 0.40 × Total_CAPEX
Hours_per_year = 8,760 × capacity_factor = 7,884h
```

For a **10 MW PEM** installation:
```
Total CAPEX = 10,000 kW × $1,100/kW = $11M
Stack cost  = 0.40 × $11M = $4.4M
Annual H₂ production ≈ 15.5 kg/hr × 7,884 = 122,202 kg/yr
```

### Lifetime scenarios for 10 MW PEM

| Scenario | Lifetime | Annual stack cost | Stack cost/kg H₂ |
|----------|----------|------------------|-----------------|
| NiFe LDH AEL (lab, 500h) | 0.063 yr | $69.7M/yr | **$570/kg** (unviable) |
| NiFe LDH (1,000h, optimistic) | 0.127 yr | $34.7M/yr | $284/kg |
| NiFe LDH + pulsed CP (2,000h est.) | 0.254 yr | $17.4M/yr | $142/kg |
| NiFe LDH + pulsed CP (5,000h target) | 0.63 yr | $6.97M/yr | $57/kg |
| NiMo AEL (commercial, 50,000h) | 6.3 yr | $697,000/yr | $5.70/kg |
| IrO₂ PEM (current, 40,000h) | 5.1 yr | $864,000/yr | $7.07/kg |
| IrO₂ PEM (DOE target, 80,000h) | 10.1 yr | $432,000/yr | $3.53/kg |

**Critical finding:** Stack lifetime is 100–1000× more important than overpotential
for earth-abundant catalysts at lab-scale lifetimes. Closing the lifetime gap
from 500h to 10,000h saves **$500+/kg** — dwarf the $0.10/kg from overpotential.

---

## 5. Pulsed CP Protocol — Return on Investment

### Protocol parameters
- Rest schedule: 59 min on / 1 min OC per hour
- Effective current delivery: **98.3%** of continuous operation
- Predicted lifetime extension: **2× minimum** (from simulation in `pulsed_cp_analysis.py`)
- Implementation cost: **$0** (software change to existing electrolyzer controller)

### Cost of the protocol (lost production)

```
Lost current fraction = 1/60 = 1.67%
Lost H₂ per year (10 MW) = 1.67% × 122,202 kg/yr = 2,041 kg/yr
Revenue lost at $4/kg H₂ = $8,164/yr
```

### Benefit (lifetime extension)

If pulsed CP achieves 2× lifetime on NiFe LDH AEL (500h → 1,000h):
```
Stack cost saving = $34.7M/yr × (1 − 1/2) = $17.4M/yr
Net gain = $17.4M − $0.008M = $17.39M/yr
ROI = 17,390,000 / 8,164 = 2,130×
```

**Even at the most conservative lifetime extension (2×), the pulsed CP protocol
has a 2,130× return on investment at $4/kg H₂.**

The break-even lifetime extension (where lost production cost equals stack savings):
```
Solving: Stack_cost × (1 − 1/X) = 0.017 × Revenue
X_min = 1 / (1 − 0.017 × Revenue / Stack_cost)
     ≈ 1.0005 × (only 0.05% lifetime improvement needed to break even)
```

The protocol is essentially free to implement and any improvement in lifetime at all
generates positive returns.

---

## 6. Full LCOH Comparison

### Per kg H₂, 10 MW system, 10-year project life

**Current state (IrO₂ PEM):**
```
Electricity:    $2.14/kg  (280 mV, $0.04/kWh)
Stack CAPEX:    $0.07/kg  (40,000h, annualised)
BoP CAPEX:      $0.09/kg  (60% of CAPEX, 20yr life)
O&M:            $0.08/kg
Water:          $0.01/kg
─────────────────────────
LCOH:  $2.39/kg
```

**Today's earth-abundant (NiFe LDH, 500h lifetime):**
```
Electricity:    $2.18/kg  (310 mV)
Stack CAPEX:    $570/kg   (500h — unviable at any price)
```
→ Not competitive. Gap is entirely lifetime, not activity.

**Near-term target (NiFe LDH + pulsed CP, 5,000h):**
```
Electricity:    $2.18/kg
Stack CAPEX:    $57/kg    (still 10× too expensive)
```
→ Still not competitive. Need 10× more lifetime improvement.

**Mid-term target (earth-abundant, 50,000h, 280 mV):**
```
Electricity:    $2.18/kg  (310 mV typical, AEL $0.04/kWh)
Stack CAPEX:    $0.07/kg  (50,000h, same as NiMo commercial)
BoP CAPEX:      $0.07/kg  (AEL is cheaper per kW)
O&M:            $0.08/kg
Water:          $0.01/kg
─────────────────────────
LCOH:  $2.41/kg
```
→ **Competitive with IrO₂ PEM at same electricity price.**

**Renewable electricity scenario ($0.025/kWh) + 50,000h earth-abundant:**
```
Electricity:    $1.36/kg
Stack CAPEX:    $0.07/kg
BoP + O&M:      $0.15/kg
─────────────────────────
LCOH:  $1.58/kg
```
→ **Below DOE $2/kg Green Hydrogen Shot target.**

---

## 7. What Matters Most — Sensitivity Ranking

Using 10 MW PEM baseline at $0.04/kWh, per kg H₂ impact:

| Lever | Change | LCOH impact | Feasibility |
|-------|--------|------------|-------------|
| Stack lifetime | 500h → 50,000h | **−$562/kg** | Hard (5–10yr research) |
| Stack lifetime | 5,000h → 50,000h | **−$51/kg** | Medium (2–5yr) |
| Stack lifetime | 50,000h → 80,000h | **−$0.04/kg** | Diminishing returns |
| Electricity price | $0.04 → $0.025/kWh | **−$0.78/kg** | External (grid) |
| η_OER | 310 → 250 mV (−60 mV) | **−$0.10/kg** | Medium |
| η_OER | 250 → 200 mV (−50 mV) | **−$0.08/kg** | Hard |
| Pulsed CP (2× lifetime) | 500h → 1,000h | **−$142/kg at lab scale** | Easy (software) |
| Current density | 400 → 1,000 mA/cm² | **−$0.31/kg** (CAPEX) | Medium |
| IrO₂ → earth-abundant (same lifetime) | CAPEX −37% | **−$0.04/kg** | Matters only at 50kh+ |

**Conclusion:** At lab-scale lifetimes (<2,000h), every research dollar spent on
lifetime extension is worth 100× more than a dollar spent on activity improvement.
Only when lifetime exceeds ~20,000h do activity and system efficiency become the
dominant cost levers.

---

## 8. IrO₂ Supply Constraint — Why Earth-Abundant is Necessary

Independent of cost, IrO₂ faces a physical supply ceiling.

```
Global Ir production:     7 tonnes/year (2024)
PEM Ir loading:           0.4 mg/cm² (state of art)
1 GW PEM electrode area:  10⁹ cm²  (at 1 A/cm²)
Ir needed per GW:         0.4 × 10⁹ mg = 400 kg/GW

Supply-limited deployment rate: 7,000 kg/yr ÷ 400 kg/GW = 17.5 GW/yr
```

**Global green H₂ scenarios require 100–500 GW/yr of electrolyzer deployment by 2035.**

Even with 10× reduction in Ir loading (a very aggressive research target):
```
175 GW/yr maximum — still insufficient for most scenarios
```

**Earth-abundant OER catalysts are not optional — they are physically required
for the energy transition at the scale needed.**

This is the deepest reason why a 50 mV improvement in η_OER on NiFe LDH matters
less than proving 10,000h stability: supply constraints mean Ir-based PEM cannot
scale, so the AEL/AEMWE path with earth-abundant catalysts must work.

---

## 9. The Winning Scenario

**What "winning" looks like for this research programme:**

| Target | Required catalyst performance | Timeline estimate |
|--------|------------------------------|------------------|
| First publications | Pulsed CP: 2× lifetime on NiFe LDH | Month 6–10 |
| Industrial relevance | Any composition: 10,000h at 10 mA/cm² | Year 2–3 |
| Market parity | 50,000h at 400+ mA/cm², η < 320 mV | Year 5–8 |
| IrO₂ replacement | 80,000h at 1,000 mA/cm², η < 280 mV | Year 10–15 |

Every step along this ladder is publishable, fundable, and economically valuable.
The pulsed CP protocol (2× lifetime for zero cost) is the first and easiest rung.

---

## Appendix: Key Formulas

**Faradaic H₂ production rate:**
```
ṁ_H₂ = (j × A × η_F × M_H₂) / (2 × F)   [g/s]
j = current density (A/cm²), A = electrode area (cm²)
η_F = Faradaic efficiency, M_H₂ = 2.016 g/mol, F = 96,485 C/mol
```

**Specific energy consumption:**
```
SEC = V_cell × 26.8 / η_F   [kWh/kg H₂]
26.8 kWh/kg = HHV of H₂
```

**Capital recovery factor:**
```
CRF = r(1+r)^n / ((1+r)^n − 1)
r = discount rate (8%), n = project lifetime (years)
```

**LCOH:**
```
LCOH = [CAPEX × CRF + OPEX_fixed] / annual_production + OPEX_variable
```
