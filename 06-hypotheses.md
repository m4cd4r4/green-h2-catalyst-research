# 06 — Testable Research Hypotheses

## How to Use This Document

Each hypothesis is formatted for experimental testing. They are ranked by:
- **Impact** (1–5): How significant would confirmation be?
- **Tractability** (1–5): How testable with existing equipment?
- **Novelty** (1–5): How unexplored is the space?

A score of 15 = highest priority.

---

## Category A: HER Catalyst Hypotheses

### A1 — W-doped CoP improves acid stability without compromising activity
**Hypothesis:** Substituting 5–15% W into CoP lattice slows Co dissolution in acid by
creating a more stable Co-W-P ternary surface without significantly changing H-binding energy.

**Rationale:** W-based phosphides (WP) show better acid stability than CoP. Co-W alloys
in HER literature show intermediate stability. A controlled W gradient (core CoP, W-rich surface)
could decouple activity (CoP bulk) from stability (WP surface).

**Test:** Synthesize Co₁₋ₓWₓP (x = 0, 0.05, 0.10, 0.15, 0.20) by co-reduction.
Measure η₁₀ (acid), 100h chronopotentiometry at 10 mA/cm², ICP-MS of Co and W dissolution.

| Impact | Tractability | Novelty | Total |
|--------|-------------|---------|-------|
| 4 | 4 | 3 | 11 |

---

### A2 — F-doping stabilizes MoS₂ edges against oxidation

**Hypothesis:** Fluorine atoms at MoS₂ edge sites form Mo-F bonds that are more resistant
to oxidation than Mo-S, preserving edge activity in acid over extended cycling.

**Rationale:** F has highest electronegativity, strongest M-F bonds. F-doped TiO₂ shows
superior photocatalytic stability. MoS₂ edge site oxidation to MoO₃ is a known failure mode.

**Test:** Synthesize F-doped MoS₂ via hydrothermal with NH₄F addition (0, 1, 5, 10 mM).
Characterize by XPS (F 1s, Mo 3d, S 2p). Compare η₁₀ and stability (500 cycles CV, 50h CP).
Post-mortem Raman to detect MoO₃ formation.

| Impact | Tractability | Novelty | Total |
|--------|-------------|---------|-------|
| 3 | 4 | 4 | 11 |

---

### A3 — Ordered FeNi intermetallic outperforms disordered alloy per active site

**Hypothesis:** Ordered FeNi (L1₀ structure) has a well-defined surface termination that
exposes a more uniform set of active sites than disordered FeNi, resulting in higher TOF
even if total activity is similar.

**Rationale:** Site heterogeneity in disordered alloys means some fraction of sites are
suboptimal. Intermetallics guarantee specific Fe-Ni coordination that can be DFT-computed
and optimized.

**Test:** Synthesize L1₀-FeNi by annealing FeNi alloy under high magnetic field (accelerates
ordering). Compare ECSA-normalized TOF to disordered FeNi. DFT calculate H* binding on
L1₀ vs. disordered surfaces.

| Impact | Tractability | Novelty | Total |
|--------|-------------|---------|-------|
| 3 | 3 | 4 | 10 |

---

### A4 — Mo SAC coordination number determines acid vs. alkaline selectivity

**Hypothesis:** Mo-N₄ single-atom sites prefer alkaline HER, while Mo-N₂C₂ sites prefer
acid HER, due to different proton transfer mechanisms at each coordination environment.

**Rationale:** N-coordination changes Mo oxidation state and d-electron density.
Different mechanisms dominate in acid (Volmer-Heyrovsky) vs. alkaline (Volmer-Tafel).
Coordination-selective synthesis can tune pH preference.

**Test:** Synthesize Mo@NC via different N/C precursors to vary N:C coordination ratio.
XANES/EXAFS to determine coordination. CV in both 0.5M H₂SO₄ and 1M KOH.
Correlate coordination number (from EXAFS) with Tafel slope (mechanism indicator).

| Impact | Tractability | Novelty | Total |
|--------|-------------|---------|-------|
| 4 | 3 | 5 | 12 |

---

### A5 — FeP on phosphorus-rich carbon shows 10× better acid stability than FeP on carbon

**Hypothesis:** P-rich carbon support creates a continuous P environment around FeP nanoparticles
that slows Fe dissolution by maintaining local P saturation around the catalyst.

**Rationale:** Le Chatelier's principle — high local P concentration suppresses FeP dissolution
equilibrium. P-rich carbon can be made from P-doped precursors.

**Test:** Prepare FeP on N,P-co-doped carbon vs. N-doped carbon. ICP-MS Fe dissolution during
100h chronopotentiometry. XPS phosphorus speciation before/after.

| Impact | Tractability | Novelty | Total |
|--------|-------------|---------|-------|
| 3 | 4 | 4 | 11 |

---

### A6 — Strained MoS₂ on convex substrate activates basal plane sites

**Hypothesis:** Deposition of MoS₂ on curved (convex) substrates (e.g., hollow carbon spheres)
introduces tensile biaxial strain that shifts S 2p binding energy by >0.3 eV, activating
basal plane for HER.

**Rationale:** DFT shows strain tunes ΔG_H* on basal plane. Convex curvature causes tensile strain.
Unlike flat substrates, curvature is uniform and quantifiable.

**Test:** Grow MoS₂ on hollow carbon spheres (diameters 50, 100, 200, 500 nm to vary strain).
Measure strain by SAED/XRD peak shift. Correlate with HER activity.

| Impact | Tractability | Novelty | Total |
|--------|-------------|---------|-------|
| 4 | 3 | 4 | 11 |

---

## Category B: OER Catalyst Hypotheses

### B1 — Ca incorporation in birnessite MnO₂ enables acid OER via PSII-inspired mechanism

**Hypothesis:** Ca²⁺ in the Mn₄O₄ cubane-like unit of birnessite MnO₂ stabilizes Mn⁴⁺
by structural templating, reducing Mn dissolution in acid by ≥50% while maintaining OER activity.

**Rationale:** Photosystem II's Mn₄CaO₅ cluster has been catalyzing acid water oxidation
in nature for 2.7 billion years. The Ca is structurally essential for cluster stability.
Birnessite already has a similar layered Mn oxide structure with interlayer cations.
Replacing Na⁺/K⁺ with Ca²⁺ could mimic the PSII coordination environment.

**Test:** Synthesize Ca-birnessite (Ca_x Mn_{1-x}O₂) via coprecipitation. Compare to K-birnessite.
XRD for structural change. CV in 0.5M H₂SO₄. ICP-MS for Mn dissolution.
XANES to track Mn oxidation state vs. Ca content.

| Impact | Tractability | Novelty | Total |
|--------|-------------|---------|-------|
| 5 | 4 | 4 | 13 |

---

### B2 — Cr/Fe dual-doped NiO enables acid OER via Cr₂O₃ passivation + Fe active sites

**Hypothesis:** In Ni₁₋ₓ₋yCrₓFeyO, Cr forms a continuous Cr₂O₃ passivation layer that
blocks Ni and Cr dissolution while Fe³⁺/Fe⁴⁺ sites at the surface remain accessible for OER.

**Rationale:** Stainless steel concept: Cr₂O₃ is acid-stable, self-healing, conformal.
Fe is the active OER site in NiFe systems. Ni provides structure.
If Cr₂O₃ doesn't block ALL surface Fe sites, net activity + stability improvement is possible.

**Test:** Synthesize Ni₁₋ₓ₋yCrₓFeyO (x = 0.10–0.25, y = 0.10–0.20) by sol-gel + calcination.
OER in 0.5M H₂SO₄ at 50 mA/cm². ICP-MS: Ni, Cr, Fe dissolution. XPS depth profile post-test.
Target: η₁₀ < 450 mV, dissolution < 5 ng/cm²/s.

| Impact | Tractability | Novelty | Total |
|--------|-------------|---------|-------|
| 5 | 4 | 3 | 12 |

---

### B3 — Trace Ru doping of NiFe LDH improves acid tolerance without full Ir/Ru content

**Hypothesis:** 1–5 mol% Ru incorporated into NiFe LDH maintains the LDH's alkaline activity
while extending tolerable pH range toward 3–5, enabling AEM electrolyzer operation with
slightly acidic membrane-adjacent environment.

**Rationale:** Ru at that doping level provides acid-resistant anchor sites around which
Ni/Fe dissolution is kinetically suppressed. Doesn't require acid stability — just slightly
lower pH tolerance (AEM membranes create a pH gradient, not full acid).

**Test:** Synthesize NiFeRu LDH (Ru = 0, 1, 3, 5 mol%). CV in pH 7, 5, 3, 1.
Track when activity collapses as function of Ru content.

| Impact | Tractability | Novelty | Total |
|--------|-------------|---------|-------|
| 4 | 5 | 3 | 12 |

---

### B4 — High-entropy OER catalysts with >6 elements outperform 5-element systems due to orbital hybridization diversity

**Hypothesis:** Increasing from 5-element to 7-element HEO (adding Ti and V to FeCoNiCrMn)
improves OER activity by >30 mV reduction in η₁₀ because additional elements introduce
d-orbital energies at the OER transition states not achievable with 5 elements.

**Rationale:** Each element contributes a unique d-orbital energy. More diverse d-orbital
manifold increases probability of favorable intermediate binding. Ti⁴⁺/Ti³⁺ and V⁵⁺/V⁴⁺
redox couples are underexplored in HEO OER.

**Test:** Systematic synthesis: 5-element → 6-element (+Ti) → 7-element (+Ti+V).
All at equimolar ratios. Electrochemical fingerprinting. DFT on simplified slab models.

| Impact | Tractability | Novelty | Total |
|--------|-------------|---------|-------|
| 3 | 3 | 5 | 11 |

---

### B5 — LOM (lattice oxygen mechanism) can be induced in NiFe LDH by reducing Fe-O bond strength via V substitution

**Hypothesis:** Vanadium in NiFeV LDH weakens Fe-O bonds, shifting OER mechanism from AEM
(adsorbate) to LOM (lattice oxygen), breaking the scaling relation constraint and enabling
η₁₀ < 200 mV.

**Rationale:** V is a known promoter in NiFeV LDH (record claim: 195 mV). LOM bypasses
OOH* intermediate. V incorporation changes Fe electronic environment. LOM in Ni/Co systems
has been confirmed by ¹⁸O isotope labeling.

**Test:** ¹⁸O isotope labeling — if O₂ contains ¹⁸O from lattice, LOM is confirmed.
Operando Raman — look for lattice O vibration changes. ¹ H₂ gas purity (LOM can produce
H₂O₂ as side product).

| Impact | Tractability | Novelty | Total |
|--------|-------------|---------|-------|
| 5 | 3 | 4 | 12 |

---

### B6 — Electrodeposited amorphous NiFe(OOH) outperforms crystalline NiFe LDH at industrial current densities

**Hypothesis:** Amorphous NiFeOOH (electrodeposited) maintains lower overpotential than
crystalline NiFe LDH at j > 200 mA/cm² because amorphous material has no grain boundary
resistance and superior ion diffusion through disordered structure.

**Rationale:** Crystalline → amorphous performance crossover is known in battery materials.
At high j, ion transport through the catalyst bulk becomes rate-limiting. Amorphous
materials have faster ion diffusion. Most OER papers only test at 10 mA/cm² — missing this.

**Test:** Prepare both. Compare at 10, 50, 100, 200, 500, 1000 mA/cm².
Plot overpotential vs. log(j) — look for crossover.

| Impact | Tractability | Novelty | Total |
|--------|-------------|---------|-------|
| 4 | 5 | 4 | 13 |

---

## Category C: Stability Hypotheses

### C1 — Short-term (100h) dissolution rate predicts long-term (10,000h) stability

**Hypothesis:** Dissolution rate measured by inline ICP-MS during the first 100h follows
a power-law decay D(t) = D₀·t^(-α), and the exponent α can predict 10,000h total dissolution
from early data.

**Rationale:** If α > 0.5, dissolution self-passivates and long-term stability is achievable.
If α < 0.2, dissolution rate remains nearly constant — long-term failure inevitable.
This would create an early-stage screening tool that doesn't require 10,000h tests.

**Test:** Run inline ICP-MS for 100h on 10 different catalysts. Fit power law. Validate
on 3 catalysts known to succeed/fail at 1000h (NiMo should succeed, CoP in acid should fail).

| Impact | Tractability | Novelty | Total |
|--------|-------------|---------|-------|
| 5 | 3 | 5 | 13 |

---

### C2 — Potential pulsing protocols extend catalyst lifetime by preventing intermediate accumulation

**Hypothesis:** Periodic reverse-potential pulses (returning to open circuit for 1 min every
1 hour) extend NiFe LDH OER lifetime by >50% by allowing desorption of accumulated O*
intermediates that block active sites.

**Rationale:** Site blocking by O* is a known OER deactivation mechanism. In battery cycling,
pulsed protocols extend lifetime. No systematic study exists for OER catalysts.

**Test:** Compare constant CP vs. pulsed CP (1min OC every 1h) for NiFe LDH over 500h.
Monitor overpotential drift. EIS before/during/after to track charge transfer resistance.

| Impact | Tractability | Novelty | Total |
|--------|-------------|---------|-------|
| 4 | 5 | 5 | 14 |

---

### C3 — Fluorinated polymer coatings slow catalyst dissolution without blocking active sites

**Hypothesis:** Ultra-thin PFPE (perfluoropolyether) coatings on NiFe LDH reduce metal
dissolution rate by 10× while causing <20 mV overpotential increase, because PFPE is
permeable to water/OH⁻ but presents a barrier to dissolved metal ion diffusion.

**Rationale:** PFPE is used in anti-fingerprint coatings — very thin (2–5 nm), conformal,
electrochemically inert. Metal ion diffusion coefficient in PFPE is much lower than in water.
Water/OH⁻ can still penetrate — active sites preserved.

**Test:** Dip-coat NiFe LDH in PFPE solution (0.01, 0.1, 1 wt%). CV to check activity.
1000h CP with ICP-MS. Compare dissolution rates.

| Impact | Tractability | Novelty | Total |
|--------|-------------|---------|-------|
| 4 | 4 | 5 | 13 |

---

## Category D: Mechanistic Hypotheses

### D1 — Fe⁴⁺ (not Fe³⁺) is the active OER species in NiFe LDH

**Hypothesis:** OER activity in NiFe LDH correlates with Fe⁴⁺ population, not total Fe
content, and can be enhanced by pre-oxidative treatments that increase steady-state Fe⁴⁺.

**Rationale:** Fe³⁺ → Fe⁴⁺ transition has been proposed as OER-active species. Pre-activation
by cycling to high potential should increase Fe⁴⁺. Operando Mössbauer on Fe-57-enriched
samples can directly measure Fe valence states.

**Test:** Prepare NiFe LDH with ⁵⁷Fe (Mössbauer-active). Operando ⁵⁷Fe Mössbauer during OER.
Correlate OER current with Fe⁴⁺ signal intensity.

| Impact | Tractability | Novelty | Total |
|--------|-------------|---------|-------|
| 5 | 2 | 3 | 10 |

---

### D2 — Electrolyte cation (Li⁺, Na⁺, K⁺, Cs⁺) strongly modifies NiFe LDH activity

**Hypothesis:** Larger cations (Cs⁺ > K⁺ > Na⁺ > Li⁺) intercalate into NiFe LDH interlayer
and expand the d-spacing, improving OH⁻ access to active sites and reducing η₁₀ by up to 30 mV.

**Rationale:** Cation effects on OER are well-documented for other oxides. LDH interlayer
spacing is known to expand with larger cations. Systematic comparison across alkali metal
hydroxides has not been done for NiFe LDH.

**Test:** OER in LiOH, NaOH, KOH, CsOH (all 1M). CV + EIS. XRD d-spacing measurement.
Confirm cation is in interlayer.

| Impact | Tractability | Novelty | Total |
|--------|-------------|---------|-------|
| 3 | 5 | 4 | 12 |

---

## Hypothesis Priority Ranking

| Rank | Hypothesis | Score | Why Prioritize |
|------|-----------|-------|----------------|
| 1 | C2 — Pulsed CP extends lifetime | 14 | High impact, easy test, novel protocol |
| 2 | B1 — Ca-birnessite for acid OER | 13 | PSII inspiration, acid OER urgency |
| 3 | B6 — Amorphous vs crystalline at high j | 13 | Tests real industrial conditions |
| 4 | C1 — Dissolution power law predicts 10kh | 13 | Would create universal screening tool |
| 5 | C3 — PFPE coating reduces dissolution | 13 | Novel material approach, tractable |
| 6 | A4 — Mo SAC coordination vs pH | 12 | Fundamental insight, acid HER relevant |
| 7 | B2 — Cr/Fe NiO for acid OER | 12 | Addresses biggest gap (acid OER) |
| 8 | B3 — Trace Ru in NiFe LDH for AEM | 12 | Practical for near-term AEM deployment |
| 9 | B5 — LOM induction by V in NiFeLDH | 12 | Scaling relation escape, high impact |
| 10 | D2 — Cation effects on NiFe LDH | 12 | Zero materials cost to test |

---

## Quick-Win Experiments (No New Synthesis Required)

These hypotheses can be tested with commercially available or easily prepared materials,
making them ideal for labs with limited synthesis capability:

1. **D2** — Just change the base (LiOH vs KOH vs CsOH)
2. **B6** — Electrodeposit amorphous NiFeOOH, compare to commercial NiFe LDH at high j
3. **C2** — Standard NiFe LDH, modified electrochemical protocol only
4. **A1 (partial)** — W-doped CoP, if you already make CoP
