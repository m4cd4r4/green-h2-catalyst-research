# 11 — Scaling Relations: The Fundamental Thermodynamic Bottleneck

## Why This Is the Deepest Problem

All approaches to improved OER catalysts eventually hit the same wall.
A catalyst might look promising — low overpotential, good current density — but the
underlying reason for high activity in most cases is simply proximity to the OER volcano
peak, not escape from the scaling relations.

**Until scaling relations are broken, the theoretical minimum OER overpotential for
single-site AEM catalysts is ~370 mV.**

This document explains why, and maps every known strategy to escape.

---

## Part 1: What Scaling Relations Are and Why They Exist

### The Four Intermediates of OER (AEM Mechanism)

```
H₂O + * → OH* + H⁺ + e⁻          ΔG₁
OH* → O* + H⁺ + e⁻                 ΔG₂
O* + H₂O → OOH* + H⁺ + e⁻        ΔG₃
OOH* → O₂ + * + H⁺ + e⁻           ΔG₄
```

At the thermodynamic potential U = 1.23 V, ΔG₁ + ΔG₂ + ΔG₃ + ΔG₄ = 4 × 0.0 = 0
(reaction is spontaneous but no overpotential applied).

For **each step** to be downhill (no thermodynamic barrier) requires:
ΔG₁ = ΔG₂ = ΔG₃ = ΔG₄ = 0.0 eV at U = 1.23 V

The ideal catalyst achieves this — but nature doesn't provide it.

### The Scaling Relation

Across hundreds of DFT-computed transition metal oxide surfaces, the binding energies of
OER intermediates are linearly correlated:

```
ΔG(OOH*) = ΔG(OH*) + 3.2 ± 0.2 eV
```

This is not a coincidence — it arises from a fundamental reason:
**OOH* and OH* bind to the same surface atom through the same oxygen atom.**
Their binding energies are therefore geometrically and electronically coupled.

### The Consequence: The Minimum Overpotential

If ΔG(OOH*) = ΔG(OH*) + 3.2 eV, and the ideal separation between all steps is 1.23 eV each,
then the best possible split with this constraint is:

```
At optimal ΔG(OH*) = 0.8 eV:
  ΔG₁ = 0.8 eV   (too large by 0.8 - 1.23/4 × ... → work through the algebra)
  ΔG₂ = ?
  ΔG₃ = OOH* - O* binding gap ≈ 1.6 eV (too large if O* strong, too small if O* weak)
  ΔG₄ = ?
```

Working through the algebra properly:

The minimum overpotential when scaling holds is:
```
η_min = (3.2 - 2 × 1.23) / 2 = (3.2 - 2.46) / 2 = 0.37 V
```

**So even a perfect AEM catalyst following scaling relations needs ≥370 mV overpotential.**

IrO₂ achieves ~270 mV — which seems to violate this. But IrO₂ benefits from slightly
non-linear scaling (Ir is at the edge of where the 3.2 eV constraint is weakest) and
may partially follow LOM in some regimes.

---

## Part 2: The Volcano Plot — Where Every Catalyst Lives

The volcano relationship arises because:
- **Left side (weak O-binding):** OH* desorption is rate-limiting, ΔG₁ is too large
- **Right side (strong O-binding):** O* or OOH* is too stable, ΔG₃ is too large
- **Peak:** Optimal balance — but constrained by scaling to η ≥ 0.37 V

### Key Positions on the Volcano (Theoretical DFT)

| Catalyst | ΔG(OH*) eV | ΔG(OOH*) eV | Position | η_theory (V) |
|----------|-----------|------------|----------|------------|
| IrO₂ | 0.78 | 3.64 | Near peak (right) | 0.41 |
| RuO₂ | 0.64 | 3.28 | Near peak (left) | 0.37 |
| MnO₂ | 1.30 | 4.70 | Left side | 0.77 |
| Co₃O₄ | 1.20 | 4.40 | Left side | 0.67 |
| NiOOH | 0.90 | 3.95 | Right side | 0.52 |
| FeOOH | 1.10 | 4.20 | Left side | 0.62 |
| NiFe LDH (Fe site) | 0.85 | 3.80 | Right of peak | 0.48 |
| BSCF (Co site) | 0.75 | 3.50 | Near peak | 0.39 |
| Ideal (if scaling broken) | 1.23/4 = 0.31 | 0.31+2.46 = 2.77 | On peak | 0.00 |

**If IrO₂ and BSCF are near the volcano peak, why are their overpotentials still >250 mV?**
Because even the volcano peak has a floor set by the 3.2 eV scaling constant.

---

## Part 3: Every Known Strategy to Break Scaling Relations

### Strategy 1: Dual-Site Mechanism

**Concept:** If OOH* forms across TWO adjacent metal sites rather than one, it can bind
differently to each intermediate:
- OH* on Site A only
- OOH* bridging Site A and Site B (sharing the oxygen-oxygen bond)

**Result:** ΔG(OOH*) becomes partially decoupled from ΔG(OH*), because the second
oxygen of OOH can interact with Site B independently.

**Theoretical prediction (DFT):**
- Optimal dual-site geometry reduces effective scaling constant from 3.2 to 2.4–2.8 eV
- Potential minimum η ≈ 0.10–0.25 V for ideal dual-site catalyst
- Best geometry: M–M distance ~2.8–3.0 Å (oxygen bridging distance)

**Experimental evidence:**
- Cobalt-Mn pairs in molecular Co-Mn oxo clusters: improved activity vs. single-Co
- Mn₄O₄ cubane: multiple adjacent sites, performance near BSCF
- FeNi dual sites in NiFe LDH: each Fe has adjacent Ni — may be naturally dual-site
- Cofacial porphyrin dimers (molecular): demonstrated 4e⁻ O-O bond at dual Co

**Why it hasn't worked well in practice:**
1. Controlling M–M distance precisely in heterogeneous catalysts is extremely hard
2. Dual-site mechanism requires specific geometric arrangement that may not persist during OER
3. Most "dual-site" claims are post-hoc rationalization of activity, not proof of mechanism

**How to prove dual-site mechanism:**
- Synthesize catalysts with precisely controlled M–M distance (MOF-derived)
- DFT + microkinetic modeling to predict optimum distance
- Compare: monometal vs. bimetal SAC at controlled spacing
- Use ¹⁸O isotope labeling to track O-O bond formation pathway

**Most tractable experiment:** M₁–M₂ diatomic catalysts (DACs) with controlled spacing.
Recently synthesized on N-doped carbon supports. Mechanistic studies needed.

---

### Strategy 2: Lattice Oxygen Mechanism (LOM)

**Concept:** Instead of the sequence:
`OH* → O* → OOH* → O₂`

The LOM proceeds:
`OH* → O* → [O* + O_lattice → O₂] → O_vacancy → [O_vacancy filled by H₂O]`

The O-O bond forms between the surface-adsorbed O* and a lattice oxygen atom,
bypassing the OOH* intermediate entirely.

**Why this breaks scaling:**
- OOH* is the bottleneck intermediate that creates the 3.2 eV constraint
- If OOH* is bypassed, ΔG₃ is replaced by a vacancy formation energy
- Vacancy formation can be tuned more independently of OH* binding

**Experimental evidence (confirmed by ¹⁸O labeling):**
- IrO_x (amorphous): ~40% LOM contribution at high overpotential
- Ba₀.₅Sr₀.₅Co₀.₈Fe₀.₂O₃ (BSCF): LOM confirmed by ¹⁸O labeling in alkaline
- Pr₀.₅Ba₀.₅CoO₃ (PBC): LOM contribution >50%
- Ni-Fe oxides at high potential: partial LOM proposed
- SrCoO₃ ultrathin films: near-complete LOM

**Requirements for LOM to work:**
1. Lattice oxygen must be oxidizable (Mn/Co/Ni oxide, not SiO₂/TiO₂)
2. Vacancy formation energy must be low enough (< 0.5 eV from DFT)
3. Vacancy must be refilled by H₂O (or OH⁻) quickly enough
4. Material must NOT dissolve during lattice O extraction (the key challenge)

**The LOM stability paradox:**
- LOM requires lattice O to participate → creates vacancies
- Vacancies weaken the oxide structure → enhanced dissolution
- This is why LOM-active catalysts (BSCF) often show poor stability
- The very mechanism that improves activity also accelerates degradation

**Can LOM be made stable?**
Two proposals:
1. **Fast vacancy refilling:** If H₂O fills the vacancy faster than dissolution kinetics → stable
   Requires: high water activity at surface, fast O-diffusion in bulk
2. **Protected LOM:** Core-shell where outer LOM-active layer is thin, core provides structural stability
   Early work: IrO₂ core + LOM-active perovskite shell

**This is an active frontier with no clear winner yet.**

---

### Strategy 3: Non-Covalent Stabilization of OOH*

**Concept:** OOH* is unstable because it has an unpaired electron (radical character).
A nearby Lewis acid site could stabilize OOH* through non-covalent interaction
without changing the active site itself.

**Analogy:** In enzymes, second-shell residues stabilize reaction intermediates
without directly bonding to the substrate.

**Implementation ideas:**
- Lewis acid metal ion (La³⁺, Ce³⁺) placed adjacent to OER active site
- Surface phosphate groups: H-bond acceptors that stabilize OOH*
- Proton relay groups: shuttle proton away from OOH* immediately after formation

**Evidence:**
- Phosphate-treated NiFeO_x: ~50 mV improvement vs. untreated — H-bond network?
- La-doped NiFe LDH: improved activity — La³⁺ as Lewis acid stabilizer?
- These effects are largely unexplained — may be OOH* stabilization

**DFT test:** Compute ΔG(OOH*) on NiFe with and without adjacent La³⁺.
If ΔG(OOH*) decreases by >0.2 eV, Lewis acid mechanism confirmed.

---

### Strategy 4: Electrochemical Non-Equilibrium Effects

**Concept:** Scaling relations are derived from thermodynamic (equilibrium) binding energies.
At high overpotential, kinetic effects may transiently populate states that thermodynamics
predicts should be empty, enabling non-equilibrium pathways.

**Specifically:**
- Spin-state changes at high potential (Co³⁺ low-spin → high-spin at >1.5V?)
- Proton-coupled electron transfer (PCET) changes intermediate stability
- Transient high-valent states (Ni⁵⁺? Ir⁶⁺?) in ultrafast OER

**Evidence:**
- In-situ XAS shows Ni reaches unusual oxidation states above 1.6 V
- Some catalysts show much better performance at 100 mA/cm² vs. 10 mA/cm²
  (if activity scaling non-linearly, suggests non-equilibrium pathway)

**This is highly speculative but worth investigating.**

---

### Strategy 5: Electrostatic Field Engineering

**Concept:** Strong local electric fields (as exist near electrode surface at high overpotential)
can shift the thermodynamics of intermediate binding. This is the "Stark effect" for catalysis.

**Mechanism:**
- OOH* has a dipole moment
- A local field aligned with this dipole can stabilize OOH* by ΔG = -μ·E
- At fields typical of solid-liquid interfaces (10⁷–10⁹ V/m), this stabilization can be 0.1–0.5 eV

**How to create local fields:**
- Charged surface groups (–SO₃⁻, –PO₄²⁻) near active sites
- Ionic liquid electrolytes with strong interfacial ordering
- SAC with asymmetric charge distribution

**Evidence:**
- Ionic liquid-modified electrodes show OER improvement → interface field effect?
- Strongly polarized zwitterionic surface treatments show activity improvement

**DFT test:** Compute ΔG intermediates with explicit field (VASP + NELECT).
Determine if field of 10⁸ V/m shifts ΔG(OOH*) by >0.2 eV.

---

### Strategy 6: Molecular Catalyst Analogy — Designed Active Sites

**Concept:** Molecular OER catalysts (Ru-bipy, Co-porphyrin) can achieve overpotentials
of 0.2–0.4 V — potentially better than solids — because ligand design allows full control
of intermediate binding.

**Transfer to heterogeneous:**
- Immobilize molecular catalysts on conductive supports
- Use molecular sites as "designed active sites" with controlled second-shell environment
- This is what enzymes do: active site + supporting protein scaffold

**State of the art:**
- [Ru(bda)] on carbon nanotubes: η₁₀ ≈ 380 mV, modest stability
- Co-porphyrin on graphene: η₁₀ ≈ 430 mV, poor stability
- Fe-corrole: η₁₀ ≈ 440 mV, poor stability
- Mn₄O₄ cubane on ITO: η₁₀ ≈ 480 mV, reasonable stability

**What's missing:** Combining molecular-level control with inorganic-level stability.
Current molecular catalysts degrade within hours in acid.

---

## Part 4: How Close Are We to Breaking Scaling?

### Current Status (2026)

| Strategy | Lab η_min achieved | Scaling broken? | Main challenge |
|----------|-------------------|-----------------|----------------|
| AEM near-volcano (IrO₂) | 250 mV | No | Ir supply |
| Dual-site (proposed) | 300 mV (estimated) | Partial | Geometric control |
| LOM (BSCF, alkaline) | 230 mV | Partial | Stability |
| OOH* stabilization | 220 mV (NiFeV LDH?) | Unknown | Mechanism unclear |
| Molecular catalysts | 380 mV (immobilized) | Potentially | Stability |
| Theoretical optimum (broken scaling) | ~50–100 mV | — | Hypothetical |

**Honest assessment:** Scaling relations have been weakened but not broken.
LOM in alkaline is the clearest evidence of partial escape.
In acid, no material has convincingly escaped the scaling constraint.

### The 200 mV Target

If a catalyst could achieve η₁₀ < 200 mV in acid with 1000h stability:
- This would prove scaling relation escape
- Would reduce PEM electrolyzer electricity cost by ~15%
- Would be one of the most impactful catalysis papers in decades
- Most groups would consider this Nobel Prize territory

**Current gap:** Best non-PGM acid OER is ~380–420 mV.
Closing the 200 mV gap requires genuine mechanism innovation, not incremental improvement.

---

## Part 5: Computational Predictions to Test

### Prediction 1: Optimal Dual-Site Distance
DFT predicts: Fe–Fe distance of 2.85 Å should enable dual-site O-O coupling.
**Test:** Fe₂ diatomic on NC support at controlled spacing (by linker length in MOF precursor).

### Prediction 2: LOM-Stable Material
Ideal LOM material requires: low vacancy formation energy AND high oxide cohesive energy.
These are normally anticorrelated — but **amorphous oxides** may decouple them.
**Test:** Amorphous vs. crystalline Co₃O₄ — is LOM more prominent in amorphous?
¹⁸O labeling experiment.

### Prediction 3: Lewis Acid Stabilization Optimum
DFT predicts: La³⁺ adjacent to Fe site in NiFe LDH reduces ΔG(OOH*) by 0.15–0.25 eV.
**Test:** La-doped NiFe LDH at 0, 2, 5, 10% La. CV + EIS + DFT comparison.

### Prediction 4: Phosphate Group H-Bond Network
Phosphate surface treatment may create H-bond acceptor for OOH* stabilization.
DFT: calculate OOH* binding on NiOOH + surface phosphate vs. clean NiOOH.
**Test:** Phosphate-treated NiFeO_x in KOH vs. untreated. Operando ATR-FTIR.

---

## Part 6: The Most Impactful Experiment in This Field

If you could do ONE experiment to advance understanding of scaling relations:

**¹⁸O isotope labeling on a series of earth-abundant catalysts in acid OER.**

Protocol:
1. Prepare 5 catalysts spanning the activity spectrum (MnO₂, Co₃O₄, NiFe LDH,
   BSCF, FeCoNiCr HEA)
2. Run OER in H₂¹⁸O-enriched electrolyte (>90% ¹⁸O)
3. Mass spectrometry on evolved O₂: measure ¹⁶O₂ vs. ¹⁸O₂ ratio
4. If ¹⁶O₂ detected: lattice O (¹⁶O) is participating → LOM active → scaling potentially broken
5. If only ¹⁸O₂: pure AEM → scaling relations hold for this material

**Why this is the most impactful:**
- Directly tests which earth-abundant materials use LOM
- If any acid-stable material shows LOM: immediately focus ALL resources there
- Cheap experiment (needs isotope-labeled water, mass spec access)
- Could be done in 2–3 weeks

**Current state:** This experiment has been done for IrO_x and alkaline catalysts.
It has NOT been systematically done for earth-abundant acid OER catalysts.
**This is a genuine gap that could be filled quickly.**
