# 07 — AI/ML Opportunities in Catalyst Discovery

## Where AI Can Have Maximum Impact

The catalyst discovery pipeline has several bottlenecks. AI is not equally useful at all of them.
This document maps the highest-leverage AI opportunities, from most to least impactful.

---

## Opportunity 1: Stability Prediction (Highest Gap)

**The problem:** ~95% of ML catalyst work predicts activity. Almost none predicts stability.
A 10 mA/cm² activity prediction is scientifically interesting but industrially useless without
a paired stability estimate.

**What's needed:**
- Dataset of (composition, structure) → (dissolution rate, hours to 20% degradation)
- Currently fragmented across papers, rarely in machine-readable form

**Approach:**
1. **Data extraction from literature** — NLP pipeline to extract stability data from papers
   - Extract: catalyst composition, synthesis conditions, electrolyte, test duration, performance retention %
   - Sources: Electrochimica Acta, ACS Catalysis, Journal of the Electrochemical Society
   - Tools: ChemDataExtractor, BERT fine-tuned on electrochemistry

2. **Stability fingerprint** — What features predict long-term stability?
   - Metal oxide dissolution potential (Pourbaix diagram features)
   - M-O bond dissociation energy from DFT
   - Charge transfer resistance (EIS Nyquist features)
   - Surface reconstruction tendency (energetics from DFT)

3. **Graph Neural Network (GNN) on crystal structure**
   - Node features: element, oxidation state, coordination number
   - Edge features: bond length, bond type
   - Target: log(dissolution rate) or lifetime in hours
   - Architecture: SchNet, DimeNet++, or CGCNN variants

**Expected impact:** A stability predictor would be more valuable to industry than any activity predictor.
Electrolyzer manufacturers care about 80,000h catalyst life, not 10 mA/cm² overpotential.

---

## Opportunity 2: High-Entropy Composition Optimization

**The problem:** HEO catalyst space has >10⁶ possible compositions at 5-element level.
Human intuition cannot explore this.

**Bayesian Optimization approach:**
```
1. Initial: Random sample 50–100 compositions
2. Train surrogate model (Gaussian Process or neural network)
3. Acquisition function (Expected Improvement) selects next experiment
4. Measure, update model, repeat
5. After 200–500 iterations: find Pareto front of activity vs. stability
```

**Active learning loop:**
- Features: elemental fractions, average electronegativity, d-electron count, lattice mismatch
- Target: η₁₀ (OER), dissolution rate (stability)
- Multi-objective: Pareto optimization of both simultaneously

**Existing tools:**
- EDBO (Experimental Design via Bayesian Optimization) — chemistry-focused
- Ax (Meta) — general-purpose BO
- BoTorch — multi-objective BO

**What's been done:** Groups at MIT, Stanford, and CMU have applied BO to HEA electrocatalysts.
Early results show 3–5× faster discovery than grid search.

**What hasn't been done:** Multi-objective stability + activity optimization in HEO OER with
>6 elements.

---

## Opportunity 3: DFT Surrogate Models for Adsorption Energies

**The problem:** DFT calculation of ΔG_H* or ΔG_OH* takes 1–24 hours per surface per
configuration. Exploring even a modest composition space requires millions of calculations.

**ML potentials that work:**
- **SchNet / DimeNet++** — message passing neural networks, trained on DFT datasets
- **MACE** — equivariant neural network potential, faster and more accurate
- **AIMNet2** — general-purpose, pre-trained on large DFT dataset
- **UMA (Meta)** — universal model for atomistic simulation (2025)

**Key datasets:**
- OC20 (Open Catalyst 2020) — 260M DFT calculations on surface+adsorbate systems
- OC22 — extended to oxide surfaces (more relevant to OER)
- OQMD, Materials Project — bulk properties

**Workflow:**
1. Use OC20-trained model as starting point
2. Fine-tune on your catalyst class (phosphides, LDH, etc.)
3. Screen millions of compositions in hours vs. months for DFT
4. Send top candidates to DFT validation
5. Add DFT results to training set (active learning loop)

**Expected speedup:** 1000–10,000× for adsorption energy screening vs. DFT

---

## Opportunity 4: Operando Spectroscopy Data Analysis

**The problem:** Operando XAS, Raman, and XPS generate rich time-series data that is
analyzed manually and slowly. Key structural dynamics during OER are being missed.

**AI approaches:**

### Operando XANES/EXAFS
- **Linear combination fitting** (current standard) — limited, assumes you know end-members
- **ML phase identification** — train on DFT-computed XANES spectra, identify unknown phases
- **Neural network EXAFS inversion** — extract local structure from EXAFS without fitting
- Tools: PyTorch + FEFF (XANES simulation), Athena + ML classifier

### Operando Raman
- **Peak deconvolution** — automated identification of overlapping peaks
- **Time-series clustering** — identify structural transition points
- **CNN on spectrogram images** — classify spectra by phase automatically

### Benefit:
- Identify surface reconstruction kinetics that manual analysis misses
- Correlate structural features with activity peaks in real-time
- Build structure-activity relationships from dynamic data, not just before/after

---

## Opportunity 5: Literature Mining & Knowledge Graphs

**The problem:** Electrochemistry literature is fragmented. The same catalyst is measured
differently across labs. Contradictions are common and unresolved.

**What AI can do:**

### Automated Data Extraction
Extract from PDFs:
- Catalyst formula
- Synthesis method (temperature, precursors, atmosphere)
- Electrolyte composition and pH
- η₁₀, Tafel slope, stability duration
- Performance retention after stability test

Tools: ChemDataExtractor 2.0, BERT-Chem, GPT-4 with structured output

**Estimated yield:** ~40–60% successful extraction from well-formatted papers

### Contradiction Detection
- Same catalyst, different groups, 50 mV different η₁₀
- Root cause: different ECSA normalization? Different Ni foam? KOH purity?
- ML can flag systematic patterns in contradictions → points to confounding variables

### Knowledge Graph
Nodes: catalysts, elements, synthesis methods, performance metrics
Edges: "synthesized by", "achieves η₁₀ of", "degrades via", "outperforms"

This enables:
- "Find all CoP synthesis routes that achieve η₁₀ < 100 mV in acid" — semantic query
- "What synthesis condition is correlated with best stability?" — pattern detection
- "Which papers contradict each other about NiFe LDH Fe content?" — inconsistency flagging

---

## Opportunity 6: Synthesis Condition Optimization

**The problem:** Synthesis conditions (temperature, precursor ratios, pH, time) have enormous
effect on performance. Most papers try only a handful of conditions.

**ML approach:**
- Train on existing synthesis-performance data
- Use Gaussian Process to predict performance from synthesis conditions
- Suggest next synthesis conditions via expected improvement
- Laboratory robots can execute automated synthesis loops

**Currently deployed at:**
- CMU — automated electrochemistry platform
- MIT — flow chemistry + Bayesian optimization
- National labs (NREL, Argonne) — high-throughput synthesis robots

**For small labs without robots:**
- Design of Experiments (DoE) — factorial design to cover synthesis space efficiently
- Response Surface Methodology — classic approach, available in Python (pyDOE2)
- Even DoE without ML gives 5–10× efficiency vs. one-at-a-time synthesis

---

## Opportunity 7: Pourbaix Diagram Machine Learning

**The problem:** Standard Pourbaix diagrams (thermodynamic stability vs. pH, potential)
are calculated for pure elements. Real catalysts are multi-element, nanostructured, and
far from equilibrium.

**AI extensions:**
1. **Multi-element Pourbaix** — ML trained on DFT formation energies for ternary/quaternary oxides
2. **Kinetic Pourbaix** — add dissolution kinetics to thermodynamic diagram
3. **Nanoparticle corrections** — surface energy corrections for <10 nm particles
4. **Uncertainty quantification** — confidence intervals on stability windows

**Existing tools:**
- Pymatgen Pourbaix diagram (single element, built)
- MP-Pourbaix (Materials Project, multi-element, basic)
- Need: ML-corrected kinetic multi-element Pourbaix for real catalyst materials

---

## Opportunity 8: Transfer Learning Across Catalyst Classes

**Insight:** Activity descriptors (M-H bond strength, d-band center) are universal across
catalyst classes. A model trained on phosphide HER data can transfer to sulfide HER with
minimal fine-tuning.

**Transfer learning pipeline:**
1. Pre-train GNN on large DFT dataset (OC20: 260M samples, all adsorbates)
2. Fine-tune on specific reaction (HER phosphides, 5000 samples)
3. Apply to new class (HER carbides, 100 samples) — only fine-tune last 2 layers
4. Dramatic reduction in labeled data needed for new catalyst classes

**This is the "ImageNet moment" for catalysis** — OC20/OC22 are enabling transfer learning
that was impossible 3 years ago.

---

## Recommended Starting Point for a Small Team

If you want to contribute to this field with AI/ML, the highest ROI starting points are:

### Option A: Data Infrastructure (2–4 weeks)
Build a public dataset:
1. Scrape/parse 200–300 papers on NiFe LDH OER performance
2. Extract: composition, synthesis conditions, η₁₀, Tafel slope, stability data
3. Standardize units and conditions
4. Publish on Zenodo/HuggingFace datasets

**Why this matters:** No standardized performance dataset exists. Every new ML paper
compiles its own dataset privately. A public dataset would be immediately cited.

### Option B: Stability Model (4–8 weeks)
1. Use Option A dataset
2. Feature engineer: Pourbaix stability window, M-O bond energy, dissolution potential
3. Train XGBoost or small GNN to predict stability (hours to 10% degradation)
4. Validate on held-out data
5. Publish model + dataset

**Why this matters:** Literally no one has published a stability ML model for OER catalysts.
This is a gap with immediate industrial relevance.

### Option C: Composition Optimizer (6–10 weeks)
1. Focus on HEO (high-entropy oxides) for alkaline OER
2. Bayesian optimization over 5-element space (FeCoNiCrMn + 2 optional)
3. Surrogate: Gaussian Process on element fraction features
4. Propose 20 compositions for experimental validation
5. Publish code + workflow

**This is the kind of human-AI collaboration that accelerates real research.**

---

## Existing Open Resources

| Resource | Type | URL | Content |
|----------|------|-----|---------|
| Open Catalyst Project | DFT dataset | opencatalystproject.org | 260M DFT, surface+adsorbate |
| Materials Project | Property DB | materialsproject.org | Crystal structures, formation energies |
| AFLOW | Property DB | aflow.org | 3.5M compounds, properties |
| Catalysis-Hub | Reaction data | catalysis-hub.org | DFT reaction energies on surfaces |
| NIST WebBook | Thermodynamics | webbook.nist.gov | Thermochemical data |
| Citrination (now Citrine) | ML platform | citrine.io | Materials ML (commercial) |
| NOMAD | DFT archive | nomad-lab.eu | Raw DFT output data |
| HuggingFace | Model hosting | huggingface.co | Many pre-trained chemistry models |

### Key Pre-trained Models
- **CHGNet** — universal neural network potential (2023, Nature ML)
- **MACE-MP-0** — foundation model for materials (2023, NeurIPS)
- **UMA** — Meta's universal model for atomistic simulation (2025)
- **DimeNet++** — directional message passing for molecules/materials

---

## The Grand Challenge

**Ultimate AI target:** A model that, given:
- Element composition (5–10 elements)
- Target electrolyte (acid/alkaline, concentration)
- Target current density (10–500 mA/cm²)
- Synthesis constraints (max temperature, available precursors)

Outputs:
- Predicted η₁₀ with uncertainty
- Predicted lifetime (hours to 20% degradation) with uncertainty
- Recommended synthesis route
- Confidence in prediction and suggested experiments to reduce uncertainty

**This does not exist yet. Building it would be a landmark contribution.**
