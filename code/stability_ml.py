"""
Green Hydrogen Catalyst Stability Predictor
============================================
Predicts OER/HER catalyst lifetime from composition + structural features.

This is a working ML pipeline seeded with data from our literature synthesis.
Designed to be extended as real experimental data is collected.

Usage:
    python stability_ml.py              # Run full pipeline with synthetic data
    python stability_ml.py --predict    # Predict for new compositions

Dependencies:
    pip install pandas numpy scikit-learn matplotlib seaborn xgboost shap
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import cross_val_score, LeaveOneOut
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.pipeline import Pipeline
import warnings
warnings.filterwarnings('ignore')


# =============================================================================
# SECTION 1: DATA — Literature-extracted catalyst performance + features
# =============================================================================

def build_catalyst_dataset():
    """
    Build dataset from literature synthesis in 08-datasets.md
    Features are estimated from first principles and literature values.
    IMPORTANT: These are starting estimates — replace with experimental values.

    Feature definitions:
    - eta_10_mv: Overpotential at 10 mA/cm² (mV) — primary activity metric
    - tafel_slope: Tafel slope (mV/dec) — reaction mechanism indicator
    - reaction: 'HER' or 'OER'
    - electrolyte: 'acid' or 'alkaline'
    - stability_h: Hours to 20% performance degradation (target variable)
    - dissolution_potential_v: Potential at which metal dissolves in Pourbaix diagram
    - mo_bond_energy_ev: M-O bond dissociation energy (eV) from DFT/literature
    - mh_bond_energy_ev: M-H bond dissociation energy (eV, HER only)
    - d_band_center_ev: Center of d-band density of states (eV, relative to EF)
    - eg_electrons: eg orbital electron occupancy (for OER perovskites/oxides)
    - dominant_metal: Primary active metal
    - crystal_class: Structural class
    - acid_stable_score: 0-3 scale from Pourbaix analysis
    """

    data = [
        # =====================================================================
        # OER CATALYSTS — ALKALINE (pH 14, 1M KOH)
        # =====================================================================
        # --- LDH Family ---
        {
            'id': 'O004', 'name': 'NiFe LDH', 'reaction': 'OER', 'electrolyte': 'alkaline',
            'eta_10_mv': 255, 'tafel_slope': 47, 'stability_h': 150,
            'dissolution_potential_v': 0.1, 'mo_bond_energy_ev': 3.8, 'mh_bond_energy_ev': None,
            'd_band_center_ev': -1.8, 'eg_electrons': 1.2,
            'dominant_metal': 'Ni', 'crystal_class': 'LDH',
            'acid_stable_score': 0, 'n_metals': 2, 'has_cr': 0, 'has_mn': 0,
            'coordination': 6, 'surface_area_m2g': 80,
        },
        {
            'id': 'O005', 'name': 'NiFeV LDH', 'reaction': 'OER', 'electrolyte': 'alkaline',
            'eta_10_mv': 220, 'tafel_slope': 42, 'stability_h': 50,
            'dissolution_potential_v': 0.1, 'mo_bond_energy_ev': 3.7, 'mh_bond_energy_ev': None,
            'd_band_center_ev': -1.9, 'eg_electrons': 1.1,
            'dominant_metal': 'Ni', 'crystal_class': 'LDH',
            'acid_stable_score': 0, 'n_metals': 3, 'has_cr': 0, 'has_mn': 0,
            'coordination': 6, 'surface_area_m2g': 90,
        },
        {
            'id': 'O006', 'name': 'NiCo LDH', 'reaction': 'OER', 'electrolyte': 'alkaline',
            'eta_10_mv': 295, 'tafel_slope': 55, 'stability_h': 60,
            'dissolution_potential_v': 0.12, 'mo_bond_energy_ev': 3.6, 'mh_bond_energy_ev': None,
            'd_band_center_ev': -1.85, 'eg_electrons': 1.25,
            'dominant_metal': 'Ni', 'crystal_class': 'LDH',
            'acid_stable_score': 0, 'n_metals': 2, 'has_cr': 0, 'has_mn': 0,
            'coordination': 6, 'surface_area_m2g': 70,
        },
        {
            'id': 'O031', 'name': 'NiFeMn LDH', 'reaction': 'OER', 'electrolyte': 'alkaline',
            'eta_10_mv': 238, 'tafel_slope': 41, 'stability_h': 80,
            'dissolution_potential_v': 0.1, 'mo_bond_energy_ev': 3.75, 'mh_bond_energy_ev': None,
            'd_band_center_ev': -1.85, 'eg_electrons': 1.18,
            'dominant_metal': 'Ni', 'crystal_class': 'LDH',
            'acid_stable_score': 0, 'n_metals': 3, 'has_cr': 0, 'has_mn': 1,
            'coordination': 6, 'surface_area_m2g': 85,
        },
        {
            'id': 'O032', 'name': 'NiFeAl LDH', 'reaction': 'OER', 'electrolyte': 'alkaline',
            'eta_10_mv': 246, 'tafel_slope': 43, 'stability_h': 70,
            'dissolution_potential_v': 0.1, 'mo_bond_energy_ev': 3.75, 'mh_bond_energy_ev': None,
            'd_band_center_ev': -1.85, 'eg_electrons': 1.2,
            'dominant_metal': 'Ni', 'crystal_class': 'LDH',
            'acid_stable_score': 0, 'n_metals': 3, 'has_cr': 0, 'has_mn': 0,
            'coordination': 6, 'surface_area_m2g': 88,
        },
        {
            'id': 'O033', 'name': 'NiFeV LDH exfoliated', 'reaction': 'OER', 'electrolyte': 'alkaline',
            'eta_10_mv': 208, 'tafel_slope': 36, 'stability_h': 30,
            'dissolution_potential_v': 0.1, 'mo_bond_energy_ev': 3.65, 'mh_bond_energy_ev': None,
            'd_band_center_ev': -1.92, 'eg_electrons': 1.08,
            'dominant_metal': 'Ni', 'crystal_class': 'LDH',
            'acid_stable_score': 0, 'n_metals': 3, 'has_cr': 0, 'has_mn': 0,
            'coordination': 5, 'surface_area_m2g': 180,
        },
        {
            'id': 'O034', 'name': 'NiFe LDH + rGO', 'reaction': 'OER', 'electrolyte': 'alkaline',
            'eta_10_mv': 222, 'tafel_slope': 38, 'stability_h': 80,
            'dissolution_potential_v': 0.1, 'mo_bond_energy_ev': 3.78, 'mh_bond_energy_ev': None,
            'd_band_center_ev': -1.82, 'eg_electrons': 1.18,
            'dominant_metal': 'Ni', 'crystal_class': 'LDH',
            'acid_stable_score': 0, 'n_metals': 2, 'has_cr': 0, 'has_mn': 0,
            'coordination': 6, 'surface_area_m2g': 110,
        },
        # --- Perovskite Family ---
        {
            'id': 'O008', 'name': 'BSCF perovskite', 'reaction': 'OER', 'electrolyte': 'alkaline',
            'eta_10_mv': 250, 'tafel_slope': 70, 'stability_h': 20,
            'dissolution_potential_v': 0.2, 'mo_bond_energy_ev': 3.5, 'mh_bond_energy_ev': None,
            'd_band_center_ev': -2.1, 'eg_electrons': 1.0,
            'dominant_metal': 'Co', 'crystal_class': 'perovskite',
            'acid_stable_score': 0, 'n_metals': 4, 'has_cr': 0, 'has_mn': 0,
            'coordination': 6, 'surface_area_m2g': 12,
        },
        {
            'id': 'O009', 'name': 'LaCoO3', 'reaction': 'OER', 'electrolyte': 'alkaline',
            'eta_10_mv': 390, 'tafel_slope': 75, 'stability_h': 50,
            'dissolution_potential_v': 0.2, 'mo_bond_energy_ev': 3.4, 'mh_bond_energy_ev': None,
            'd_band_center_ev': -2.0, 'eg_electrons': 1.0,
            'dominant_metal': 'Co', 'crystal_class': 'perovskite',
            'acid_stable_score': 0, 'n_metals': 2, 'has_cr': 0, 'has_mn': 0,
            'coordination': 6, 'surface_area_m2g': 8,
        },
        {
            'id': 'O035', 'name': 'SrCoO3 perovskite', 'reaction': 'OER', 'electrolyte': 'alkaline',
            'eta_10_mv': 295, 'tafel_slope': 65, 'stability_h': 15,
            'dissolution_potential_v': 0.25, 'mo_bond_energy_ev': 3.4, 'mh_bond_energy_ev': None,
            'd_band_center_ev': -2.2, 'eg_electrons': 0.85,
            'dominant_metal': 'Co', 'crystal_class': 'perovskite',
            'acid_stable_score': 0, 'n_metals': 2, 'has_cr': 0, 'has_mn': 0,
            'coordination': 6, 'surface_area_m2g': 6,
        },
        {
            'id': 'O036', 'name': 'NdBaCoO3 double perovskite', 'reaction': 'OER', 'electrolyte': 'alkaline',
            'eta_10_mv': 248, 'tafel_slope': 60, 'stability_h': 15,
            'dissolution_potential_v': 0.22, 'mo_bond_energy_ev': 3.48, 'mh_bond_energy_ev': None,
            'd_band_center_ev': -2.08, 'eg_electrons': 0.95,
            'dominant_metal': 'Co', 'crystal_class': 'perovskite',
            'acid_stable_score': 0, 'n_metals': 3, 'has_cr': 0, 'has_mn': 0,
            'coordination': 6, 'surface_area_m2g': 10,
        },
        # --- Spinel Family ---
        {
            'id': 'O011', 'name': 'NiCo2O4', 'reaction': 'OER', 'electrolyte': 'alkaline',
            'eta_10_mv': 310, 'tafel_slope': 70, 'stability_h': 80,
            'dissolution_potential_v': 0.25, 'mo_bond_energy_ev': 3.6, 'mh_bond_energy_ev': None,
            'd_band_center_ev': -2.0, 'eg_electrons': 1.3,
            'dominant_metal': 'Co', 'crystal_class': 'spinel',
            'acid_stable_score': 0, 'n_metals': 2, 'has_cr': 0, 'has_mn': 0,
            'coordination': 6, 'surface_area_m2g': 60,
        },
        {
            'id': 'O037', 'name': 'MnCo2O4 spinel', 'reaction': 'OER', 'electrolyte': 'alkaline',
            'eta_10_mv': 320, 'tafel_slope': 70, 'stability_h': 40,
            'dissolution_potential_v': 0.4, 'mo_bond_energy_ev': 3.42, 'mh_bond_energy_ev': None,
            'd_band_center_ev': -2.18, 'eg_electrons': 1.38,
            'dominant_metal': 'Co', 'crystal_class': 'spinel',
            'acid_stable_score': 0, 'n_metals': 2, 'has_cr': 0, 'has_mn': 1,
            'coordination': 6, 'surface_area_m2g': 45,
        },
        {
            'id': 'O038', 'name': 'MnFe2O4 spinel', 'reaction': 'OER', 'electrolyte': 'alkaline',
            'eta_10_mv': 368, 'tafel_slope': 78, 'stability_h': 30,
            'dissolution_potential_v': 0.55, 'mo_bond_energy_ev': 3.32, 'mh_bond_energy_ev': None,
            'd_band_center_ev': -2.28, 'eg_electrons': 1.48,
            'dominant_metal': 'Fe', 'crystal_class': 'spinel',
            'acid_stable_score': 0, 'n_metals': 2, 'has_cr': 0, 'has_mn': 1,
            'coordination': 6, 'surface_area_m2g': 38,
        },
        {
            'id': 'O039', 'name': 'CoFe2O4 spinel', 'reaction': 'OER', 'electrolyte': 'alkaline',
            'eta_10_mv': 335, 'tafel_slope': 68, 'stability_h': 35,
            'dissolution_potential_v': 0.2, 'mo_bond_energy_ev': 3.45, 'mh_bond_energy_ev': None,
            'd_band_center_ev': -2.0, 'eg_electrons': 1.35,
            'dominant_metal': 'Co', 'crystal_class': 'spinel',
            'acid_stable_score': 0, 'n_metals': 2, 'has_cr': 0, 'has_mn': 0,
            'coordination': 6, 'surface_area_m2g': 42,
        },
        # --- Amorphous / Electrodeposited ---
        {
            'id': 'O025', 'name': 'Amorphous NiFeO_xH_y', 'reaction': 'OER', 'electrolyte': 'alkaline',
            'eta_10_mv': 260, 'tafel_slope': 50, 'stability_h': 200,
            'dissolution_potential_v': 0.1, 'mo_bond_energy_ev': 3.8, 'mh_bond_energy_ev': None,
            'd_band_center_ev': -1.8, 'eg_electrons': 1.2,
            'dominant_metal': 'Ni', 'crystal_class': 'amorphous',
            'acid_stable_score': 0, 'n_metals': 2, 'has_cr': 0, 'has_mn': 0,
            'coordination': 5, 'surface_area_m2g': 150,
        },
        {
            'id': 'O040', 'name': 'NiCoFe amorphous', 'reaction': 'OER', 'electrolyte': 'alkaline',
            'eta_10_mv': 248, 'tafel_slope': 45, 'stability_h': 150,
            'dissolution_potential_v': 0.1, 'mo_bond_energy_ev': 3.75, 'mh_bond_energy_ev': None,
            'd_band_center_ev': -1.82, 'eg_electrons': 1.2,
            'dominant_metal': 'Ni', 'crystal_class': 'amorphous',
            'acid_stable_score': 0, 'n_metals': 3, 'has_cr': 0, 'has_mn': 0,
            'coordination': 5, 'surface_area_m2g': 160,
        },
        {
            'id': 'O041', 'name': 'NiFeMo amorphous', 'reaction': 'OER', 'electrolyte': 'alkaline',
            'eta_10_mv': 232, 'tafel_slope': 40, 'stability_h': 180,
            'dissolution_potential_v': 0.1, 'mo_bond_energy_ev': 3.8, 'mh_bond_energy_ev': None,
            'd_band_center_ev': -1.85, 'eg_electrons': 1.12,
            'dominant_metal': 'Ni', 'crystal_class': 'amorphous',
            'acid_stable_score': 0, 'n_metals': 3, 'has_cr': 0, 'has_mn': 0,
            'coordination': 5, 'surface_area_m2g': 170,
        },
        {
            'id': 'O042', 'name': 'CoPi cobalt phosphate', 'reaction': 'OER', 'electrolyte': 'alkaline',
            'eta_10_mv': 320, 'tafel_slope': 68, 'stability_h': 60,
            'dissolution_potential_v': 0.2, 'mo_bond_energy_ev': 3.45, 'mh_bond_energy_ev': None,
            'd_band_center_ev': -2.0, 'eg_electrons': 1.3,
            'dominant_metal': 'Co', 'crystal_class': 'amorphous',
            'acid_stable_score': 0, 'n_metals': 1, 'has_cr': 0, 'has_mn': 0,
            'coordination': 4, 'surface_area_m2g': 50,
        },
        {
            'id': 'O043', 'name': 'NiB amorphous film', 'reaction': 'OER', 'electrolyte': 'alkaline',
            'eta_10_mv': 278, 'tafel_slope': 52, 'stability_h': 100,
            'dissolution_potential_v': 0.12, 'mo_bond_energy_ev': 3.72, 'mh_bond_energy_ev': None,
            'd_band_center_ev': -1.88, 'eg_electrons': 1.18,
            'dominant_metal': 'Ni', 'crystal_class': 'amorphous',
            'acid_stable_score': 0, 'n_metals': 1, 'has_cr': 0, 'has_mn': 0,
            'coordination': 5, 'surface_area_m2g': 95,
        },
        # --- Oxide ---
        {
            'id': 'O014', 'name': 'Co3O4 on graphene', 'reaction': 'OER', 'electrolyte': 'alkaline',
            'eta_10_mv': 350, 'tafel_slope': 65, 'stability_h': 50,
            'dissolution_potential_v': 0.2, 'mo_bond_energy_ev': 3.45, 'mh_bond_energy_ev': None,
            'd_band_center_ev': -2.0, 'eg_electrons': 1.3,
            'dominant_metal': 'Co', 'crystal_class': 'oxide',
            'acid_stable_score': 0, 'n_metals': 1, 'has_cr': 0, 'has_mn': 0,
            'coordination': 6, 'surface_area_m2g': 90,
        },
        {
            'id': 'O016', 'name': 'MnO2 birnessite', 'reaction': 'OER', 'electrolyte': 'alkaline',
            'eta_10_mv': 420, 'tafel_slope': 85, 'stability_h': 80,
            'dissolution_potential_v': 1.2, 'mo_bond_energy_ev': 3.2, 'mh_bond_energy_ev': None,
            'd_band_center_ev': -2.5, 'eg_electrons': 1.5,
            'dominant_metal': 'Mn', 'crystal_class': 'layered_oxide',
            'acid_stable_score': 2, 'n_metals': 1, 'has_cr': 0, 'has_mn': 1,
            'coordination': 6, 'surface_area_m2g': 40,
        },
        # --- High-Entropy Oxides ---
        {
            'id': 'O019', 'name': 'FeCoNiCrMn HEO', 'reaction': 'OER', 'electrolyte': 'alkaline',
            'eta_10_mv': 270, 'tafel_slope': 57, 'stability_h': 50,
            'dissolution_potential_v': 0.8, 'mo_bond_energy_ev': 3.9, 'mh_bond_energy_ev': None,
            'd_band_center_ev': -2.0, 'eg_electrons': 1.2,
            'dominant_metal': 'Ni', 'crystal_class': 'high_entropy',
            'acid_stable_score': 1, 'n_metals': 5, 'has_cr': 1, 'has_mn': 1,
            'coordination': 6, 'surface_area_m2g': 30,
        },
        {
            'id': 'O044', 'name': 'FeCoNiCrTi HEO', 'reaction': 'OER', 'electrolyte': 'alkaline',
            'eta_10_mv': 258, 'tafel_slope': 50, 'stability_h': 60,
            'dissolution_potential_v': 0.85, 'mo_bond_energy_ev': 3.88, 'mh_bond_energy_ev': None,
            'd_band_center_ev': -2.02, 'eg_electrons': 1.18,
            'dominant_metal': 'Ni', 'crystal_class': 'high_entropy',
            'acid_stable_score': 1, 'n_metals': 5, 'has_cr': 1, 'has_mn': 0,
            'coordination': 6, 'surface_area_m2g': 32,
        },
        {
            'id': 'O045', 'name': 'FeCoNiCrMnV HEO 6-element', 'reaction': 'OER', 'electrolyte': 'alkaline',
            'eta_10_mv': 245, 'tafel_slope': 46, 'stability_h': 70,
            'dissolution_potential_v': 0.82, 'mo_bond_energy_ev': 3.92, 'mh_bond_energy_ev': None,
            'd_band_center_ev': -2.0, 'eg_electrons': 1.15,
            'dominant_metal': 'Ni', 'crystal_class': 'high_entropy',
            'acid_stable_score': 1, 'n_metals': 6, 'has_cr': 1, 'has_mn': 1,
            'coordination': 6, 'surface_area_m2g': 35,
        },
        # --- MOF-Derived ---
        {
            'id': 'O046', 'name': 'ZIF-67 derived Co@NC', 'reaction': 'OER', 'electrolyte': 'alkaline',
            'eta_10_mv': 318, 'tafel_slope': 65, 'stability_h': 60,
            'dissolution_potential_v': 0.2, 'mo_bond_energy_ev': 3.42, 'mh_bond_energy_ev': None,
            'd_band_center_ev': -1.95, 'eg_electrons': 1.28,
            'dominant_metal': 'Co', 'crystal_class': 'MOF_derived',
            'acid_stable_score': 0, 'n_metals': 1, 'has_cr': 0, 'has_mn': 0,
            'coordination': 4, 'surface_area_m2g': 250,
        },
        {
            'id': 'O047', 'name': 'FeNi@NC MOF-derived', 'reaction': 'OER', 'electrolyte': 'alkaline',
            'eta_10_mv': 285, 'tafel_slope': 58, 'stability_h': 70,
            'dissolution_potential_v': 0.12, 'mo_bond_energy_ev': 3.78, 'mh_bond_energy_ev': None,
            'd_band_center_ev': -1.85, 'eg_electrons': 1.2,
            'dominant_metal': 'Ni', 'crystal_class': 'MOF_derived',
            'acid_stable_score': 0, 'n_metals': 2, 'has_cr': 0, 'has_mn': 0,
            'coordination': 4, 'surface_area_m2g': 280,
        },
        # =====================================================================
        # OER CATALYSTS — ACID (pH 0, 0.5M H2SO4)
        # =====================================================================
        {
            'id': 'O017', 'name': 'MnO2 birnessite (acid)', 'reaction': 'OER', 'electrolyte': 'acid',
            'eta_10_mv': 500, 'tafel_slope': 100, 'stability_h': 5,
            'dissolution_potential_v': 1.2, 'mo_bond_energy_ev': 3.2, 'mh_bond_energy_ev': None,
            'd_band_center_ev': -2.5, 'eg_electrons': 1.5,
            'dominant_metal': 'Mn', 'crystal_class': 'layered_oxide',
            'acid_stable_score': 2, 'n_metals': 1, 'has_cr': 0, 'has_mn': 1,
            'coordination': 6, 'surface_area_m2g': 40,
        },
        {
            'id': 'O018', 'name': 'Ca-MnO2 (acid)', 'reaction': 'OER', 'electrolyte': 'acid',
            'eta_10_mv': 462, 'tafel_slope': 92, 'stability_h': 12,
            'dissolution_potential_v': 1.22, 'mo_bond_energy_ev': 3.22, 'mh_bond_energy_ev': None,
            'd_band_center_ev': -2.48, 'eg_electrons': 1.48,
            'dominant_metal': 'Mn', 'crystal_class': 'layered_oxide',
            'acid_stable_score': 2, 'n_metals': 2, 'has_cr': 0, 'has_mn': 1,
            'coordination': 6, 'surface_area_m2g': 42,
        },
        {
            'id': 'O020', 'name': 'FeCoNi HEA (acid)', 'reaction': 'OER', 'electrolyte': 'acid',
            'eta_10_mv': 400, 'tafel_slope': 75, 'stability_h': 10,
            'dissolution_potential_v': 0.6, 'mo_bond_energy_ev': 3.7, 'mh_bond_energy_ev': None,
            'd_band_center_ev': -1.9, 'eg_electrons': 1.2,
            'dominant_metal': 'Fe', 'crystal_class': 'high_entropy',
            'acid_stable_score': 1, 'n_metals': 3, 'has_cr': 0, 'has_mn': 0,
            'coordination': 6, 'surface_area_m2g': 25,
        },
        {
            'id': 'O021', 'name': 'FeCoNiCr HEA (acid)', 'reaction': 'OER', 'electrolyte': 'acid',
            'eta_10_mv': 420, 'tafel_slope': 80, 'stability_h': 30,
            'dissolution_potential_v': 0.9, 'mo_bond_energy_ev': 3.8, 'mh_bond_energy_ev': None,
            'd_band_center_ev': -2.0, 'eg_electrons': 1.1,
            'dominant_metal': 'Cr', 'crystal_class': 'high_entropy',
            'acid_stable_score': 2, 'n_metals': 4, 'has_cr': 1, 'has_mn': 0,
            'coordination': 6, 'surface_area_m2g': 20,
        },
        {
            'id': 'O048', 'name': 'FeCoNiCrMo HEA (acid)', 'reaction': 'OER', 'electrolyte': 'acid',
            'eta_10_mv': 378, 'tafel_slope': 70, 'stability_h': 20,
            'dissolution_potential_v': 0.92, 'mo_bond_energy_ev': 3.82, 'mh_bond_energy_ev': None,
            'd_band_center_ev': -2.0, 'eg_electrons': 1.1,
            'dominant_metal': 'Cr', 'crystal_class': 'high_entropy',
            'acid_stable_score': 2, 'n_metals': 5, 'has_cr': 1, 'has_mn': 0,
            'coordination': 6, 'surface_area_m2g': 22,
        },
        {
            'id': 'O049', 'name': 'FeCoNiCrMnV HEA 6-el (acid)', 'reaction': 'OER', 'electrolyte': 'acid',
            'eta_10_mv': 358, 'tafel_slope': 65, 'stability_h': 30,
            'dissolution_potential_v': 0.95, 'mo_bond_energy_ev': 3.88, 'mh_bond_energy_ev': None,
            'd_band_center_ev': -2.0, 'eg_electrons': 1.08,
            'dominant_metal': 'Cr', 'crystal_class': 'high_entropy',
            'acid_stable_score': 2, 'n_metals': 6, 'has_cr': 1, 'has_mn': 1,
            'coordination': 6, 'surface_area_m2g': 25,
        },
        {
            'id': 'O050', 'name': 'Ca-Mn-Ru-Ox 3% Ru (acid)', 'reaction': 'OER', 'electrolyte': 'acid',
            'eta_10_mv': 355, 'tafel_slope': 72, 'stability_h': 35,
            'dissolution_potential_v': 1.8, 'mo_bond_energy_ev': 3.3, 'mh_bond_energy_ev': None,
            'd_band_center_ev': -2.3, 'eg_electrons': 1.4,
            'dominant_metal': 'Mn', 'crystal_class': 'doped_oxide',
            'acid_stable_score': 2, 'n_metals': 3, 'has_cr': 0, 'has_mn': 1,
            'coordination': 6, 'surface_area_m2g': 48,
        },
        {
            'id': 'O051', 'name': 'IrO2 (acid reference)', 'reaction': 'OER', 'electrolyte': 'acid',
            'eta_10_mv': 280, 'tafel_slope': 50, 'stability_h': 5000,
            'dissolution_potential_v': 2.0, 'mo_bond_energy_ev': 3.9, 'mh_bond_energy_ev': None,
            'd_band_center_ev': -1.5, 'eg_electrons': 1.0,
            'dominant_metal': 'Ir', 'crystal_class': 'rutile',
            'acid_stable_score': 3, 'n_metals': 1, 'has_cr': 0, 'has_mn': 0,
            'coordination': 6, 'surface_area_m2g': 20,
        },
        # --- Optimizer-guided Mn-W compositions (acid OER, March 2026) ---
        # Stability hours estimated from dissolution model: h = 100ug/cm2 / D(ug/cm2/h)
        # Features from Hammer-Norskov tables and weighted Pourbaix potentials
        {
            'id': 'O052', 'name': 'MnW-binary P1 (acid)', 'reaction': 'OER', 'electrolyte': 'acid',
            'eta_10_mv': 331, 'tafel_slope': 68, 'stability_h': 6,
            'dissolution_potential_v': 0.94, 'mo_bond_energy_ev': 3.18, 'mh_bond_energy_ev': None,
            'd_band_center_ev': -1.94, 'eg_electrons': 0.15,
            'dominant_metal': 'Mn', 'crystal_class': 'doped_oxide',
            'acid_stable_score': 2, 'n_metals': 2, 'has_cr': 0, 'has_mn': 1,
            'coordination': 6, 'surface_area_m2g': 100,
        },
        {
            'id': 'O053', 'name': 'MnWTiNi quad (acid)', 'reaction': 'OER', 'electrolyte': 'acid',
            'eta_10_mv': 335, 'tafel_slope': 70, 'stability_h': 9,
            'dissolution_potential_v': 0.87, 'mo_bond_energy_ev': 3.25, 'mh_bond_energy_ev': None,
            'd_band_center_ev': -1.83, 'eg_electrons': 0.20,
            'dominant_metal': 'Mn', 'crystal_class': 'doped_oxide',
            'acid_stable_score': 2, 'n_metals': 4, 'has_cr': 0, 'has_mn': 1,
            'coordination': 6, 'surface_area_m2g': 180,
        },
        {
            'id': 'O054', 'name': 'W-dominant MnWCr (acid)', 'reaction': 'OER', 'electrolyte': 'acid',
            'eta_10_mv': 341, 'tafel_slope': 72, 'stability_h': 10,
            'dissolution_potential_v': 1.00, 'mo_bond_energy_ev': 3.05, 'mh_bond_energy_ev': None,
            'd_band_center_ev': -1.87, 'eg_electrons': 0.05,
            'dominant_metal': 'W', 'crystal_class': 'doped_oxide',
            'acid_stable_score': 2, 'n_metals': 3, 'has_cr': 1, 'has_mn': 1,
            'coordination': 6, 'surface_area_m2g': 55,
        },
        {
            'id': 'O055', 'name': 'MnWCoTi Pareto (acid)', 'reaction': 'OER', 'electrolyte': 'acid',
            'eta_10_mv': 344, 'tafel_slope': 71, 'stability_h': 7,
            'dissolution_potential_v': 0.94, 'mo_bond_energy_ev': 3.15, 'mh_bond_energy_ev': None,
            'd_band_center_ev': -1.80, 'eg_electrons': 0.13,
            'dominant_metal': 'W', 'crystal_class': 'doped_oxide',
            'acid_stable_score': 2, 'n_metals': 4, 'has_cr': 0, 'has_mn': 1,
            'coordination': 6, 'surface_area_m2g': 85,
        },
        {
            'id': 'O056', 'name': 'MnWTiCr most-stable (acid)', 'reaction': 'OER', 'electrolyte': 'acid',
            'eta_10_mv': 451, 'tafel_slope': 88, 'stability_h': 14,
            'dissolution_potential_v': 0.99, 'mo_bond_energy_ev': 3.08, 'mh_bond_energy_ev': None,
            'd_band_center_ev': -1.98, 'eg_electrons': 0.05,
            'dominant_metal': 'Mn', 'crystal_class': 'doped_oxide',
            'acid_stable_score': 2, 'n_metals': 4, 'has_cr': 1, 'has_mn': 1,
            'coordination': 6, 'surface_area_m2g': 120,
        },
        {
            'id': 'O057', 'name': 'CaMnW birnessite 8% Ca (acid)', 'reaction': 'OER', 'electrolyte': 'acid',
            'eta_10_mv': 325, 'tafel_slope': 65, 'stability_h': 9,
            'dissolution_potential_v': 1.06, 'mo_bond_energy_ev': 3.10, 'mh_bond_energy_ev': None,
            'd_band_center_ev': -2.10, 'eg_electrons': 0.30,
            'dominant_metal': 'Mn', 'crystal_class': 'layered_oxide',
            'acid_stable_score': 2, 'n_metals': 3, 'has_cr': 0, 'has_mn': 1,
            'coordination': 6, 'surface_area_m2g': 65,
        },
        {
            'id': 'O058', 'name': 'WFeMnV activity-focus (acid)', 'reaction': 'OER', 'electrolyte': 'acid',
            'eta_10_mv': 356, 'tafel_slope': 73, 'stability_h': 3,
            'dissolution_potential_v': 0.84, 'mo_bond_energy_ev': 3.22, 'mh_bond_energy_ev': None,
            'd_band_center_ev': -1.62, 'eg_electrons': 0.18,
            'dominant_metal': 'W', 'crystal_class': 'high_entropy',
            'acid_stable_score': 1, 'n_metals': 4, 'has_cr': 0, 'has_mn': 1,
            'coordination': 6, 'surface_area_m2g': 70,
        },
        {
            'id': 'O059', 'name': 'CrWNiMn Pareto-stable (acid)', 'reaction': 'OER', 'electrolyte': 'acid',
            'eta_10_mv': 364, 'tafel_slope': 74, 'stability_h': 5,
            'dissolution_potential_v': 0.83, 'mo_bond_energy_ev': 3.20, 'mh_bond_energy_ev': None,
            'd_band_center_ev': -1.95, 'eg_electrons': 0.08,
            'dominant_metal': 'Cr', 'crystal_class': 'high_entropy',
            'acid_stable_score': 2, 'n_metals': 4, 'has_cr': 1, 'has_mn': 1,
            'coordination': 6, 'surface_area_m2g': 40,
        },
        # =====================================================================
        # HER CATALYSTS — ACID (pH 0, 0.5M H2SO4)
        # =====================================================================
        {
            'id': 'H001', 'name': 'Pt/C (acid reference)', 'reaction': 'HER', 'electrolyte': 'acid',
            'eta_10_mv': 40, 'tafel_slope': 32, 'stability_h': 1000,
            'dissolution_potential_v': 1.5, 'mo_bond_energy_ev': None, 'mh_bond_energy_ev': 2.3,
            'd_band_center_ev': -1.2, 'eg_electrons': None,
            'dominant_metal': 'Pt', 'crystal_class': 'alloy',
            'acid_stable_score': 3, 'n_metals': 1, 'has_cr': 0, 'has_mn': 0,
            'coordination': 12, 'surface_area_m2g': 150,
        },
        {
            'id': 'H003', 'name': 'CoP (acid)', 'reaction': 'HER', 'electrolyte': 'acid',
            'eta_10_mv': 88, 'tafel_slope': 60, 'stability_h': 24,
            'dissolution_potential_v': 0.3, 'mo_bond_energy_ev': None, 'mh_bond_energy_ev': 2.8,
            'd_band_center_ev': -1.5, 'eg_electrons': None,
            'dominant_metal': 'Co', 'crystal_class': 'phosphide',
            'acid_stable_score': 1, 'n_metals': 1, 'has_cr': 0, 'has_mn': 0,
            'coordination': 6, 'surface_area_m2g': 45,
        },
        {
            'id': 'H009', 'name': 'MoP (acid)', 'reaction': 'HER', 'electrolyte': 'acid',
            'eta_10_mv': 110, 'tafel_slope': 50, 'stability_h': 20,
            'dissolution_potential_v': 0.48, 'mo_bond_energy_ev': None, 'mh_bond_energy_ev': 2.52,
            'd_band_center_ev': -1.62, 'eg_electrons': None,
            'dominant_metal': 'Mo', 'crystal_class': 'phosphide',
            'acid_stable_score': 2, 'n_metals': 1, 'has_cr': 0, 'has_mn': 0,
            'coordination': 6, 'surface_area_m2g': 42,
        },
        {
            'id': 'H010', 'name': 'WP (acid)', 'reaction': 'HER', 'electrolyte': 'acid',
            'eta_10_mv': 140, 'tafel_slope': 55, 'stability_h': 50,
            'dissolution_potential_v': 0.6, 'mo_bond_energy_ev': None, 'mh_bond_energy_ev': 2.6,
            'd_band_center_ev': -1.7, 'eg_electrons': None,
            'dominant_metal': 'W', 'crystal_class': 'phosphide',
            'acid_stable_score': 2, 'n_metals': 1, 'has_cr': 0, 'has_mn': 0,
            'coordination': 6, 'surface_area_m2g': 35,
        },
        {
            'id': 'H011', 'name': 'MoS2 edge-rich (acid)', 'reaction': 'HER', 'electrolyte': 'acid',
            'eta_10_mv': 200, 'tafel_slope': 68, 'stability_h': 50,
            'dissolution_potential_v': 0.45, 'mo_bond_energy_ev': None, 'mh_bond_energy_ev': 2.55,
            'd_band_center_ev': -1.65, 'eg_electrons': None,
            'dominant_metal': 'Mo', 'crystal_class': 'sulfide',
            'acid_stable_score': 1, 'n_metals': 1, 'has_cr': 0, 'has_mn': 0,
            'coordination': 6, 'surface_area_m2g': 60,
        },
        {
            'id': 'H012', 'name': '1T-MoS2 (acid)', 'reaction': 'HER', 'electrolyte': 'acid',
            'eta_10_mv': 165, 'tafel_slope': 50, 'stability_h': 20,
            'dissolution_potential_v': 0.45, 'mo_bond_energy_ev': None, 'mh_bond_energy_ev': 2.52,
            'd_band_center_ev': -1.62, 'eg_electrons': None,
            'dominant_metal': 'Mo', 'crystal_class': 'sulfide',
            'acid_stable_score': 1, 'n_metals': 1, 'has_cr': 0, 'has_mn': 0,
            'coordination': 6, 'surface_area_m2g': 85,
        },
        {
            'id': 'H016', 'name': 'Mo2C (acid)', 'reaction': 'HER', 'electrolyte': 'acid',
            'eta_10_mv': 120, 'tafel_slope': 62, 'stability_h': 50,
            'dissolution_potential_v': 0.5, 'mo_bond_energy_ev': None, 'mh_bond_energy_ev': 2.5,
            'd_band_center_ev': -1.6, 'eg_electrons': None,
            'dominant_metal': 'Mo', 'crystal_class': 'carbide',
            'acid_stable_score': 2, 'n_metals': 1, 'has_cr': 0, 'has_mn': 0,
            'coordination': 6, 'surface_area_m2g': 55,
        },
        {
            'id': 'H017', 'name': 'Mo2C@NC core-shell (acid)', 'reaction': 'HER', 'electrolyte': 'acid',
            'eta_10_mv': 105, 'tafel_slope': 57, 'stability_h': 100,
            'dissolution_potential_v': 0.5, 'mo_bond_energy_ev': None, 'mh_bond_energy_ev': 2.5,
            'd_band_center_ev': -1.6, 'eg_electrons': None,
            'dominant_metal': 'Mo', 'crystal_class': 'carbide_encapsulated',
            'acid_stable_score': 3, 'n_metals': 1, 'has_cr': 0, 'has_mn': 0,
            'coordination': 6, 'surface_area_m2g': 120,
        },
        {
            'id': 'H018', 'name': 'WC nanostructured (acid)', 'reaction': 'HER', 'electrolyte': 'acid',
            'eta_10_mv': 135, 'tafel_slope': 65, 'stability_h': 50,
            'dissolution_potential_v': 0.58, 'mo_bond_energy_ev': None, 'mh_bond_energy_ev': 2.62,
            'd_band_center_ev': -1.68, 'eg_electrons': None,
            'dominant_metal': 'W', 'crystal_class': 'carbide',
            'acid_stable_score': 2, 'n_metals': 1, 'has_cr': 0, 'has_mn': 0,
            'coordination': 6, 'surface_area_m2g': 48,
        },
        {
            'id': 'H024', 'name': 'Mo SAC@NC (acid)', 'reaction': 'HER', 'electrolyte': 'acid',
            'eta_10_mv': 100, 'tafel_slope': 42, 'stability_h': 50,
            'dissolution_potential_v': 0.5, 'mo_bond_energy_ev': None, 'mh_bond_energy_ev': 2.4,
            'd_band_center_ev': -1.5, 'eg_electrons': None,
            'dominant_metal': 'Mo', 'crystal_class': 'SAC',
            'acid_stable_score': 2, 'n_metals': 1, 'has_cr': 0, 'has_mn': 0,
            'coordination': 4, 'surface_area_m2g': 800,
        },
        {
            'id': 'H025', 'name': 'Co SAC@NC (acid)', 'reaction': 'HER', 'electrolyte': 'acid',
            'eta_10_mv': 130, 'tafel_slope': 48, 'stability_h': 30,
            'dissolution_potential_v': 0.32, 'mo_bond_energy_ev': None, 'mh_bond_energy_ev': 2.78,
            'd_band_center_ev': -1.52, 'eg_electrons': None,
            'dominant_metal': 'Co', 'crystal_class': 'SAC',
            'acid_stable_score': 1, 'n_metals': 1, 'has_cr': 0, 'has_mn': 0,
            'coordination': 4, 'surface_area_m2g': 750,
        },
        {
            'id': 'H030', 'name': 'CoMoP ternary (acid)', 'reaction': 'HER', 'electrolyte': 'acid',
            'eta_10_mv': 95, 'tafel_slope': 52, 'stability_h': 50,
            'dissolution_potential_v': 0.42, 'mo_bond_energy_ev': None, 'mh_bond_energy_ev': 2.65,
            'd_band_center_ev': -1.58, 'eg_electrons': None,
            'dominant_metal': 'Co', 'crystal_class': 'phosphide',
            'acid_stable_score': 1, 'n_metals': 2, 'has_cr': 0, 'has_mn': 0,
            'coordination': 6, 'surface_area_m2g': 55,
        },
        {
            'id': 'H031', 'name': 'CoP2 nanoarrays (acid)', 'reaction': 'HER', 'electrolyte': 'acid',
            'eta_10_mv': 112, 'tafel_slope': 62, 'stability_h': 30,
            'dissolution_potential_v': 0.32, 'mo_bond_energy_ev': None, 'mh_bond_energy_ev': 2.82,
            'd_band_center_ev': -1.52, 'eg_electrons': None,
            'dominant_metal': 'Co', 'crystal_class': 'phosphide',
            'acid_stable_score': 1, 'n_metals': 1, 'has_cr': 0, 'has_mn': 0,
            'coordination': 6, 'surface_area_m2g': 50,
        },
        {
            'id': 'H032', 'name': 'Ni2P@NC encapsulated (acid)', 'reaction': 'HER', 'electrolyte': 'acid',
            'eta_10_mv': 125, 'tafel_slope': 58, 'stability_h': 80,
            'dissolution_potential_v': 0.35, 'mo_bond_energy_ev': None, 'mh_bond_energy_ev': 2.72,
            'd_band_center_ev': -1.52, 'eg_electrons': None,
            'dominant_metal': 'Ni', 'crystal_class': 'carbide_encapsulated',
            'acid_stable_score': 2, 'n_metals': 1, 'has_cr': 0, 'has_mn': 0,
            'coordination': 6, 'surface_area_m2g': 90,
        },
        {
            'id': 'H033', 'name': 'NiMoP ternary (acid)', 'reaction': 'HER', 'electrolyte': 'acid',
            'eta_10_mv': 88, 'tafel_slope': 50, 'stability_h': 60,
            'dissolution_potential_v': 0.38, 'mo_bond_energy_ev': None, 'mh_bond_energy_ev': 2.68,
            'd_band_center_ev': -1.55, 'eg_electrons': None,
            'dominant_metal': 'Ni', 'crystal_class': 'phosphide',
            'acid_stable_score': 1, 'n_metals': 2, 'has_cr': 0, 'has_mn': 0,
            'coordination': 6, 'surface_area_m2g': 58,
        },
        {
            'id': 'H034', 'name': 'WC@NC core-shell (acid)', 'reaction': 'HER', 'electrolyte': 'acid',
            'eta_10_mv': 118, 'tafel_slope': 62, 'stability_h': 100,
            'dissolution_potential_v': 0.6, 'mo_bond_energy_ev': None, 'mh_bond_energy_ev': 2.62,
            'd_band_center_ev': -1.68, 'eg_electrons': None,
            'dominant_metal': 'W', 'crystal_class': 'carbide_encapsulated',
            'acid_stable_score': 3, 'n_metals': 1, 'has_cr': 0, 'has_mn': 0,
            'coordination': 6, 'surface_area_m2g': 140,
        },
        {
            'id': 'H035', 'name': 'CoSe2 nanosheets (acid)', 'reaction': 'HER', 'electrolyte': 'acid',
            'eta_10_mv': 152, 'tafel_slope': 70, 'stability_h': 30,
            'dissolution_potential_v': 0.35, 'mo_bond_energy_ev': None, 'mh_bond_energy_ev': 2.75,
            'd_band_center_ev': -1.55, 'eg_electrons': None,
            'dominant_metal': 'Co', 'crystal_class': 'selenide',
            'acid_stable_score': 1, 'n_metals': 1, 'has_cr': 0, 'has_mn': 0,
            'coordination': 6, 'surface_area_m2g': 55,
        },
        {
            'id': 'H036', 'name': 'MoSe2 nanoflowers (acid)', 'reaction': 'HER', 'electrolyte': 'acid',
            'eta_10_mv': 192, 'tafel_slope': 78, 'stability_h': 30,
            'dissolution_potential_v': 0.42, 'mo_bond_energy_ev': None, 'mh_bond_energy_ev': 2.55,
            'd_band_center_ev': -1.62, 'eg_electrons': None,
            'dominant_metal': 'Mo', 'crystal_class': 'selenide',
            'acid_stable_score': 1, 'n_metals': 1, 'has_cr': 0, 'has_mn': 0,
            'coordination': 6, 'surface_area_m2g': 65,
        },
        {
            'id': 'H037', 'name': 'Fe-N4 SAC (acid)', 'reaction': 'HER', 'electrolyte': 'acid',
            'eta_10_mv': 142, 'tafel_slope': 54, 'stability_h': 40,
            'dissolution_potential_v': 0.28, 'mo_bond_energy_ev': None, 'mh_bond_energy_ev': 2.85,
            'd_band_center_ev': -1.48, 'eg_electrons': None,
            'dominant_metal': 'Fe', 'crystal_class': 'SAC',
            'acid_stable_score': 1, 'n_metals': 1, 'has_cr': 0, 'has_mn': 0,
            'coordination': 4, 'surface_area_m2g': 820,
        },
        {
            'id': 'H038', 'name': 'V2C MXene (acid)', 'reaction': 'HER', 'electrolyte': 'acid',
            'eta_10_mv': 138, 'tafel_slope': 63, 'stability_h': 35,
            'dissolution_potential_v': 0.55, 'mo_bond_energy_ev': None, 'mh_bond_energy_ev': 2.58,
            'd_band_center_ev': -1.72, 'eg_electrons': None,
            'dominant_metal': 'V', 'crystal_class': 'MXene',
            'acid_stable_score': 2, 'n_metals': 1, 'has_cr': 0, 'has_mn': 0,
            'coordination': 8, 'surface_area_m2g': 200,
        },
        {
            'id': 'H039', 'name': 'W-doped CoP (acid)', 'reaction': 'HER', 'electrolyte': 'acid',
            'eta_10_mv': 85, 'tafel_slope': 49, 'stability_h': 55,
            'dissolution_potential_v': 0.45, 'mo_bond_energy_ev': None, 'mh_bond_energy_ev': 2.72,
            'd_band_center_ev': -1.58, 'eg_electrons': None,
            'dominant_metal': 'Co', 'crystal_class': 'phosphide',
            'acid_stable_score': 2, 'n_metals': 2, 'has_cr': 0, 'has_mn': 0,
            'coordination': 6, 'surface_area_m2g': 50,
        },
        {
            'id': 'H040', 'name': 'MoP@C core-shell (acid)', 'reaction': 'HER', 'electrolyte': 'acid',
            'eta_10_mv': 82, 'tafel_slope': 47, 'stability_h': 70,
            'dissolution_potential_v': 0.5, 'mo_bond_energy_ev': None, 'mh_bond_energy_ev': 2.52,
            'd_band_center_ev': -1.62, 'eg_electrons': None,
            'dominant_metal': 'Mo', 'crystal_class': 'carbide_encapsulated',
            'acid_stable_score': 2, 'n_metals': 1, 'has_cr': 0, 'has_mn': 0,
            'coordination': 6, 'surface_area_m2g': 115,
        },
        # =====================================================================
        # HER CATALYSTS — ALKALINE (pH 14, 1M KOH)
        # =====================================================================
        {
            'id': 'H002', 'name': 'NiMo alloy (alkaline)', 'reaction': 'HER', 'electrolyte': 'alkaline',
            'eta_10_mv': 75, 'tafel_slope': 38, 'stability_h': 10000,
            'dissolution_potential_v': 0.1, 'mo_bond_energy_ev': None, 'mh_bond_energy_ev': 2.7,
            'd_band_center_ev': -1.4, 'eg_electrons': None,
            'dominant_metal': 'Ni', 'crystal_class': 'alloy',
            'acid_stable_score': 0, 'n_metals': 2, 'has_cr': 0, 'has_mn': 0,
            'coordination': 12, 'surface_area_m2g': 20,
        },
        {
            'id': 'H004', 'name': 'CoP alkaline', 'reaction': 'HER', 'electrolyte': 'alkaline',
            'eta_10_mv': 125, 'tafel_slope': 65, 'stability_h': 100,
            'dissolution_potential_v': 0.1, 'mo_bond_energy_ev': None, 'mh_bond_energy_ev': 2.8,
            'd_band_center_ev': -1.5, 'eg_electrons': None,
            'dominant_metal': 'Co', 'crystal_class': 'phosphide',
            'acid_stable_score': 0, 'n_metals': 1, 'has_cr': 0, 'has_mn': 0,
            'coordination': 6, 'surface_area_m2g': 45,
        },
        {
            'id': 'H006', 'name': 'Ni2P (alkaline)', 'reaction': 'HER', 'electrolyte': 'alkaline',
            'eta_10_mv': 105, 'tafel_slope': 55, 'stability_h': 100,
            'dissolution_potential_v': 0.1, 'mo_bond_energy_ev': None, 'mh_bond_energy_ev': 2.72,
            'd_band_center_ev': -1.5, 'eg_electrons': None,
            'dominant_metal': 'Ni', 'crystal_class': 'phosphide',
            'acid_stable_score': 0, 'n_metals': 1, 'has_cr': 0, 'has_mn': 0,
            'coordination': 6, 'surface_area_m2g': 50,
        },
        {
            'id': 'H021', 'name': 'Ni-Mo-N (alkaline)', 'reaction': 'HER', 'electrolyte': 'alkaline',
            'eta_10_mv': 100, 'tafel_slope': 47, 'stability_h': 100,
            'dissolution_potential_v': 0.1, 'mo_bond_energy_ev': None, 'mh_bond_energy_ev': 2.65,
            'd_band_center_ev': -1.45, 'eg_electrons': None,
            'dominant_metal': 'Ni', 'crystal_class': 'nitride',
            'acid_stable_score': 0, 'n_metals': 2, 'has_cr': 0, 'has_mn': 0,
            'coordination': 6, 'surface_area_m2g': 70,
        },
        {
            'id': 'H022', 'name': 'FeNi intermetallic (alkaline)', 'reaction': 'HER', 'electrolyte': 'alkaline',
            'eta_10_mv': 105, 'tafel_slope': 45, 'stability_h': 200,
            'dissolution_potential_v': 0.1, 'mo_bond_energy_ev': None, 'mh_bond_energy_ev': 2.68,
            'd_band_center_ev': -1.42, 'eg_electrons': None,
            'dominant_metal': 'Ni', 'crystal_class': 'alloy',
            'acid_stable_score': 0, 'n_metals': 2, 'has_cr': 0, 'has_mn': 0,
            'coordination': 12, 'surface_area_m2g': 25,
        },
        {
            'id': 'H023', 'name': 'NiMoFe alloy (alkaline)', 'reaction': 'HER', 'electrolyte': 'alkaline',
            'eta_10_mv': 85, 'tafel_slope': 41, 'stability_h': 500,
            'dissolution_potential_v': 0.1, 'mo_bond_energy_ev': None, 'mh_bond_energy_ev': 2.68,
            'd_band_center_ev': -1.42, 'eg_electrons': None,
            'dominant_metal': 'Ni', 'crystal_class': 'alloy',
            'acid_stable_score': 0, 'n_metals': 3, 'has_cr': 0, 'has_mn': 0,
            'coordination': 12, 'surface_area_m2g': 22,
        },
        {
            'id': 'H026', 'name': 'Ni SAC@NC (alkaline)', 'reaction': 'HER', 'electrolyte': 'alkaline',
            'eta_10_mv': 115, 'tafel_slope': 52, 'stability_h': 30,
            'dissolution_potential_v': 0.1, 'mo_bond_energy_ev': None, 'mh_bond_energy_ev': 2.7,
            'd_band_center_ev': -1.48, 'eg_electrons': None,
            'dominant_metal': 'Ni', 'crystal_class': 'SAC',
            'acid_stable_score': 0, 'n_metals': 1, 'has_cr': 0, 'has_mn': 0,
            'coordination': 4, 'surface_area_m2g': 780,
        },
        {
            'id': 'H027', 'name': 'Ti3C2 MXene + Mo2C (alkaline)', 'reaction': 'HER', 'electrolyte': 'alkaline',
            'eta_10_mv': 103, 'tafel_slope': 51, 'stability_h': 30,
            'dissolution_potential_v': 0.1, 'mo_bond_energy_ev': None, 'mh_bond_energy_ev': 2.55,
            'd_band_center_ev': -1.68, 'eg_electrons': None,
            'dominant_metal': 'Mo', 'crystal_class': 'MXene',
            'acid_stable_score': 0, 'n_metals': 2, 'has_cr': 0, 'has_mn': 0,
            'coordination': 8, 'surface_area_m2g': 210,
        },
        {
            'id': 'H028', 'name': 'N-P co-doped carbon (alkaline)', 'reaction': 'HER', 'electrolyte': 'alkaline',
            'eta_10_mv': 272, 'tafel_slope': 98, 'stability_h': 200,
            'dissolution_potential_v': 0.1, 'mo_bond_energy_ev': None, 'mh_bond_energy_ev': 3.0,
            'd_band_center_ev': -2.2, 'eg_electrons': None,
            'dominant_metal': 'None', 'crystal_class': 'heteroatom_carbon',
            'acid_stable_score': 0, 'n_metals': 0, 'has_cr': 0, 'has_mn': 0,
            'coordination': 3, 'surface_area_m2g': 1200,
        },
        {
            'id': 'H029', 'name': 'FeCoP ternary (alkaline)', 'reaction': 'HER', 'electrolyte': 'alkaline',
            'eta_10_mv': 108, 'tafel_slope': 56, 'stability_h': 80,
            'dissolution_potential_v': 0.1, 'mo_bond_energy_ev': None, 'mh_bond_energy_ev': 2.75,
            'd_band_center_ev': -1.52, 'eg_electrons': None,
            'dominant_metal': 'Co', 'crystal_class': 'phosphide',
            'acid_stable_score': 0, 'n_metals': 2, 'has_cr': 0, 'has_mn': 0,
            'coordination': 6, 'surface_area_m2g': 58,
        },
        {
            'id': 'H041', 'name': 'NiCoP ternary (alkaline)', 'reaction': 'HER', 'electrolyte': 'alkaline',
            'eta_10_mv': 125, 'tafel_slope': 62, 'stability_h': 80,
            'dissolution_potential_v': 0.1, 'mo_bond_energy_ev': None, 'mh_bond_energy_ev': 2.76,
            'd_band_center_ev': -1.52, 'eg_electrons': None,
            'dominant_metal': 'Ni', 'crystal_class': 'phosphide',
            'acid_stable_score': 0, 'n_metals': 2, 'has_cr': 0, 'has_mn': 0,
            'coordination': 6, 'surface_area_m2g': 62,
        },
        {
            'id': 'H042', 'name': 'NiFeP ternary (alkaline)', 'reaction': 'HER', 'electrolyte': 'alkaline',
            'eta_10_mv': 95, 'tafel_slope': 48, 'stability_h': 100,
            'dissolution_potential_v': 0.1, 'mo_bond_energy_ev': None, 'mh_bond_energy_ev': 2.72,
            'd_band_center_ev': -1.5, 'eg_electrons': None,
            'dominant_metal': 'Ni', 'crystal_class': 'phosphide',
            'acid_stable_score': 0, 'n_metals': 2, 'has_cr': 0, 'has_mn': 0,
            'coordination': 6, 'surface_area_m2g': 65,
        },
        {
            'id': 'H043', 'name': 'NiMo@NC (alkaline)', 'reaction': 'HER', 'electrolyte': 'alkaline',
            'eta_10_mv': 68, 'tafel_slope': 36, 'stability_h': 200,
            'dissolution_potential_v': 0.1, 'mo_bond_energy_ev': None, 'mh_bond_energy_ev': 2.68,
            'd_band_center_ev': -1.42, 'eg_electrons': None,
            'dominant_metal': 'Ni', 'crystal_class': 'alloy',
            'acid_stable_score': 0, 'n_metals': 2, 'has_cr': 0, 'has_mn': 0,
            'coordination': 12, 'surface_area_m2g': 85,
        },
        {
            'id': 'H044', 'name': 'CoMoN nanosheets (alkaline)', 'reaction': 'HER', 'electrolyte': 'alkaline',
            'eta_10_mv': 85, 'tafel_slope': 42, 'stability_h': 100,
            'dissolution_potential_v': 0.1, 'mo_bond_energy_ev': None, 'mh_bond_energy_ev': 2.62,
            'd_band_center_ev': -1.46, 'eg_electrons': None,
            'dominant_metal': 'Co', 'crystal_class': 'nitride',
            'acid_stable_score': 0, 'n_metals': 2, 'has_cr': 0, 'has_mn': 0,
            'coordination': 6, 'surface_area_m2g': 80,
        },
        {
            'id': 'H045', 'name': 'Co4N nanowires (alkaline)', 'reaction': 'HER', 'electrolyte': 'alkaline',
            'eta_10_mv': 90, 'tafel_slope': 40, 'stability_h': 100,
            'dissolution_potential_v': 0.1, 'mo_bond_energy_ev': None, 'mh_bond_energy_ev': 2.78,
            'd_band_center_ev': -1.48, 'eg_electrons': None,
            'dominant_metal': 'Co', 'crystal_class': 'nitride',
            'acid_stable_score': 0, 'n_metals': 1, 'has_cr': 0, 'has_mn': 0,
            'coordination': 8, 'surface_area_m2g': 72,
        },
        {
            'id': 'H046', 'name': 'CoSe2 alkaline', 'reaction': 'HER', 'electrolyte': 'alkaline',
            'eta_10_mv': 115, 'tafel_slope': 52, 'stability_h': 60,
            'dissolution_potential_v': 0.1, 'mo_bond_energy_ev': None, 'mh_bond_energy_ev': 2.75,
            'd_band_center_ev': -1.55, 'eg_electrons': None,
            'dominant_metal': 'Co', 'crystal_class': 'selenide',
            'acid_stable_score': 0, 'n_metals': 1, 'has_cr': 0, 'has_mn': 0,
            'coordination': 6, 'surface_area_m2g': 55,
        },
        {
            'id': 'H047', 'name': 'NiCoSe2 ternary (alkaline)', 'reaction': 'HER', 'electrolyte': 'alkaline',
            'eta_10_mv': 104, 'tafel_slope': 50, 'stability_h': 80,
            'dissolution_potential_v': 0.1, 'mo_bond_energy_ev': None, 'mh_bond_energy_ev': 2.73,
            'd_band_center_ev': -1.54, 'eg_electrons': None,
            'dominant_metal': 'Ni', 'crystal_class': 'selenide',
            'acid_stable_score': 0, 'n_metals': 2, 'has_cr': 0, 'has_mn': 0,
            'coordination': 6, 'surface_area_m2g': 68,
        },
        {
            'id': 'H048', 'name': 'NiCo alloy (alkaline)', 'reaction': 'HER', 'electrolyte': 'alkaline',
            'eta_10_mv': 85, 'tafel_slope': 40, 'stability_h': 500,
            'dissolution_potential_v': 0.1, 'mo_bond_energy_ev': None, 'mh_bond_energy_ev': 2.75,
            'd_band_center_ev': -1.42, 'eg_electrons': None,
            'dominant_metal': 'Ni', 'crystal_class': 'alloy',
            'acid_stable_score': 0, 'n_metals': 2, 'has_cr': 0, 'has_mn': 0,
            'coordination': 12, 'surface_area_m2g': 22,
        },
        {
            'id': 'H049', 'name': 'NiFeCo ternary alloy (alkaline)', 'reaction': 'HER', 'electrolyte': 'alkaline',
            'eta_10_mv': 78, 'tafel_slope': 38, 'stability_h': 300,
            'dissolution_potential_v': 0.1, 'mo_bond_energy_ev': None, 'mh_bond_energy_ev': 2.72,
            'd_band_center_ev': -1.4, 'eg_electrons': None,
            'dominant_metal': 'Ni', 'crystal_class': 'alloy',
            'acid_stable_score': 0, 'n_metals': 3, 'has_cr': 0, 'has_mn': 0,
            'coordination': 12, 'surface_area_m2g': 20,
        },
        {
            'id': 'H050', 'name': 'NiMoW alloy (alkaline)', 'reaction': 'HER', 'electrolyte': 'alkaline',
            'eta_10_mv': 65, 'tafel_slope': 34, 'stability_h': 1000,
            'dissolution_potential_v': 0.1, 'mo_bond_energy_ev': None, 'mh_bond_energy_ev': 2.65,
            'd_band_center_ev': -1.38, 'eg_electrons': None,
            'dominant_metal': 'Ni', 'crystal_class': 'alloy',
            'acid_stable_score': 0, 'n_metals': 3, 'has_cr': 0, 'has_mn': 0,
            'coordination': 12, 'surface_area_m2g': 18,
        },
        {
            'id': 'H051', 'name': 'Ni3N@NC (alkaline)', 'reaction': 'HER', 'electrolyte': 'alkaline',
            'eta_10_mv': 80, 'tafel_slope': 40, 'stability_h': 120,
            'dissolution_potential_v': 0.1, 'mo_bond_energy_ev': None, 'mh_bond_energy_ev': 2.7,
            'd_band_center_ev': -1.46, 'eg_electrons': None,
            'dominant_metal': 'Ni', 'crystal_class': 'nitride',
            'acid_stable_score': 0, 'n_metals': 1, 'has_cr': 0, 'has_mn': 0,
            'coordination': 6, 'surface_area_m2g': 78,
        },
        {
            'id': 'H052', 'name': 'NiCo2P heterojunction (alkaline)', 'reaction': 'HER', 'electrolyte': 'alkaline',
            'eta_10_mv': 98, 'tafel_slope': 50, 'stability_h': 90,
            'dissolution_potential_v': 0.1, 'mo_bond_energy_ev': None, 'mh_bond_energy_ev': 2.78,
            'd_band_center_ev': -1.52, 'eg_electrons': None,
            'dominant_metal': 'Co', 'crystal_class': 'phosphide',
            'acid_stable_score': 0, 'n_metals': 2, 'has_cr': 0, 'has_mn': 0,
            'coordination': 6, 'surface_area_m2g': 68,
        },
        {
            'id': 'H053', 'name': 'NiS2 on Ni foam (alkaline)', 'reaction': 'HER', 'electrolyte': 'alkaline',
            'eta_10_mv': 190, 'tafel_slope': 72, 'stability_h': 50,
            'dissolution_potential_v': 0.1, 'mo_bond_energy_ev': None, 'mh_bond_energy_ev': 2.7,
            'd_band_center_ev': -1.65, 'eg_electrons': None,
            'dominant_metal': 'Ni', 'crystal_class': 'sulfide',
            'acid_stable_score': 0, 'n_metals': 1, 'has_cr': 0, 'has_mn': 0,
            'coordination': 6, 'surface_area_m2g': 48,
        },
    ]

    return pd.DataFrame(data)


# =============================================================================
# SECTION 2: FEATURE ENGINEERING
# =============================================================================

def engineer_features(df):
    """
    Create ML-ready features from catalyst descriptors.
    Mix of physically-motivated and data-driven features.
    """
    features = df.copy()

    # Encode categorical features
    features['is_acid'] = (features['electrolyte'] == 'acid').astype(int)
    features['is_HER'] = (features['reaction'] == 'HER').astype(int)

    # Crystal class one-hot
    crystal_classes = ['LDH', 'perovskite', 'spinel', 'layered_oxide', 'high_entropy',
                       'amorphous', 'phosphide', 'carbide', 'carbide_encapsulated',
                       'SAC', 'alloy', 'nitride', 'sulfide', 'selenide', 'oxide',
                       'MOF_derived', 'MXene', 'doped_oxide', 'rutile', 'heteroatom_carbon']
    for cls in crystal_classes:
        features[f'is_{cls}'] = (features['crystal_class'] == cls).astype(int)

    # Interaction features (physically motivated)
    # Acid stability score × dissolution potential → combined stability predictor
    features['stability_index'] = features['acid_stable_score'] * features['dissolution_potential_v']

    # Activity / mechanism interaction
    features['activity_kinetics'] = features['eta_10_mv'] * features['tafel_slope'] / 1000

    # Number of protective elements (Cr, Mn = partial stability)
    features['protective_elements'] = features['has_cr'] + features['has_mn']

    # Encapsulation benefit (carbide@NC has extra protection)
    features['is_encapsulated'] = features['is_carbide_encapsulated'].copy()

    # Fill NaN values
    features['mo_bond_energy_ev'] = features['mo_bond_energy_ev'].fillna(
        features['mo_bond_energy_ev'].mean()
    )
    features['mh_bond_energy_ev'] = features['mh_bond_energy_ev'].fillna(
        features['mh_bond_energy_ev'].mean()
    )
    features['eg_electrons'] = features['eg_electrons'].fillna(
        features['eg_electrons'].mean()
    )

    return features


def get_feature_columns():
    """Return the feature columns to use for ML."""
    return [
        # Primary electrochemical descriptors
        'eta_10_mv', 'tafel_slope',
        # Thermodynamic stability features
        'dissolution_potential_v', 'acid_stable_score', 'stability_index',
        # Electronic structure
        'd_band_center_ev', 'mo_bond_energy_ev', 'mh_bond_energy_ev', 'eg_electrons',
        # Structural features
        'n_metals', 'has_cr', 'has_mn', 'coordination', 'surface_area_m2g',
        'protective_elements', 'is_encapsulated',
        # Reaction/electrolyte context
        'is_acid', 'is_HER',
        # Crystal class one-hot
        'is_LDH', 'is_perovskite', 'is_spinel', 'is_high_entropy', 'is_amorphous',
        'is_phosphide', 'is_carbide', 'is_SAC', 'is_alloy', 'is_nitride',
        'is_selenide', 'is_oxide', 'is_MOF_derived', 'is_MXene', 'is_doped_oxide',
        # Interaction features
        'activity_kinetics',
    ]


# =============================================================================
# SECTION 3: MODEL TRAINING AND EVALUATION
# =============================================================================

def train_stability_model(df_features, feature_cols, target='stability_h'):
    """
    Train multiple models and compare performance.
    Uses 5-fold stratified CV for n>50; LOO for smaller datasets.
    With 100+ samples, 5-fold CV gives more reliable estimates than LOO.
    """
    from sklearn.model_selection import KFold
    X = df_features[feature_cols].values
    y = np.log1p(df_features[target].values)  # Log transform: stability is right-skewed

    n_samples = len(y)
    use_kfold = n_samples >= 50

    models = {
        'Ridge Regression': Pipeline([
            ('scaler', StandardScaler()),
            ('model', Ridge(alpha=1.0))
        ]),
        'Random Forest': Pipeline([
            ('scaler', StandardScaler()),
            ('model', RandomForestRegressor(n_estimators=200, max_depth=6, random_state=42))
        ]),
        'Gradient Boosting': Pipeline([
            ('scaler', StandardScaler()),
            ('model', GradientBoostingRegressor(n_estimators=200, max_depth=4,
                                                learning_rate=0.05, random_state=42))
        ]),
    }

    results = {}
    cv_label = '5-Fold CV' if use_kfold else 'Leave-One-Out CV'
    splitter = KFold(n_splits=5, shuffle=True, random_state=42) if use_kfold else LeaveOneOut()

    print("=" * 60)
    print(f"STABILITY MODEL PERFORMANCE ({cv_label})")
    print(f"Dataset size: {n_samples} catalysts")
    print("Target: log(stability_hours + 1)")
    print("=" * 60)

    for name, model in models.items():
        y_pred = []
        y_true = []

        for train_idx, test_idx in splitter.split(X):
            X_train, X_test = X[train_idx], X[test_idx]
            y_train, y_test = y[train_idx], y[test_idx]

            model.fit(X_train, y_train)
            y_pred.extend(model.predict(X_test).tolist())
            y_true.extend(y_test.tolist())

        y_pred = np.array(y_pred)
        y_true = np.array(y_true)

        mae_log = mean_absolute_error(y_true, y_pred)
        # Convert back to hours space for interpretability
        mae_hours = mean_absolute_error(np.expm1(y_true), np.expm1(y_pred))
        r2 = r2_score(y_true, y_pred)

        results[name] = {
            'model': model, 'y_pred': y_pred, 'y_true': y_true,
            'mae_log': mae_log, 'mae_hours': mae_hours, 'r2': r2
        }

        print(f"\n{name}:")
        print(f"  MAE (log space): {mae_log:.3f}")
        print(f"  MAE (hours):     {mae_hours:.0f}h")
        print(f"  R² (log space):  {r2:.3f}")

    # Fit best model on all data for feature importance
    best_name = max(results, key=lambda k: results[k]['r2'])
    print(f"\nBest model: {best_name} (R² = {results[best_name]['r2']:.3f})")

    best_pipeline = models[best_name]
    best_pipeline.fit(X, y)

    return results, best_pipeline, best_name


def plot_results(results, df_features, feature_cols):
    """Generate diagnostic plots."""

    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    fig.suptitle('Catalyst Stability Predictor — Model Diagnostics', fontsize=14, fontweight='bold')

    # 1. Predicted vs. Actual
    ax = axes[0]
    best_name = max(results, key=lambda k: results[k]['r2'])
    r = results[best_name]

    y_true_h = np.expm1(r['y_true'])
    y_pred_h = np.expm1(r['y_pred'])

    ax.scatter(y_true_h, y_pred_h, c='steelblue', s=80, alpha=0.8, zorder=3)
    max_val = max(y_true_h.max(), y_pred_h.max()) * 1.1
    ax.plot([0, max_val], [0, max_val], 'k--', alpha=0.5, label='Perfect prediction')
    ax.set_xlabel('Actual Stability (hours)', fontsize=11)
    ax.set_ylabel('Predicted Stability (hours)', fontsize=11)
    ax.set_title(f'Predicted vs. Actual\n({best_name}, CV)', fontsize=11)
    ax.legend(fontsize=9)
    ax.grid(alpha=0.3)

    # Add catalyst labels
    names = df_features['name'].values
    for i, (x, y_pt) in enumerate(zip(y_true_h, y_pred_h)):
        if abs(x - y_pt) / (x + 1) > 0.3:  # Label points with >30% error
            ax.annotate(names[i].split()[0], (x, y_pt), fontsize=7, ha='left')

    # 2. Model comparison
    ax = axes[1]
    model_names = list(results.keys())
    r2_scores = [results[n]['r2'] for n in model_names]
    mae_scores = [results[n]['mae_hours'] for n in model_names]

    bars = ax.bar(range(len(model_names)), r2_scores, color=['steelblue', 'coral', 'mediumseagreen'])
    ax.set_xticks(range(len(model_names)))
    ax.set_xticklabels([n.replace(' ', '\n') for n in model_names], fontsize=9)
    ax.set_ylabel('R² Score (5-Fold CV)', fontsize=11)
    ax.set_title('Model Comparison\n(Higher = Better)', fontsize=11)
    ax.set_ylim(min(0, min(r2_scores)) - 0.05, 1.0)
    ax.axhline(0, color='black', linewidth=0.5)
    ax.grid(axis='y', alpha=0.3)

    for bar, score in zip(bars, r2_scores):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                f'{score:.2f}', ha='center', fontsize=10)

    # 3. Key features vs. stability
    ax = axes[2]
    colors = {'alkaline': 'steelblue', 'acid': 'coral'}
    for electrolyte in ['alkaline', 'acid']:
        mask = df_features['electrolyte'] == electrolyte
        ax.scatter(
            df_features.loc[mask, 'acid_stable_score'],
            df_features.loc[mask, 'stability_h'],
            label=electrolyte, color=colors[electrolyte],
            s=80, alpha=0.8, zorder=3
        )

    ax.set_xlabel('Acid Stability Score (0=none, 3=excellent)', fontsize=11)
    ax.set_ylabel('Stability (hours)', fontsize=11)
    ax.set_title('Acid Stability Score\nvs. Measured Stability', fontsize=11)
    ax.legend(fontsize=9)
    ax.grid(alpha=0.3)
    ax.set_yscale('log')

    plt.tight_layout()
    plt.savefig('stability_model_diagnostics.png', dpi=150, bbox_inches='tight')
    plt.show()
    print("\nPlot saved: stability_model_diagnostics.png")


# =============================================================================
# SECTION 4: FEATURE IMPORTANCE ANALYSIS
# =============================================================================

def analyze_feature_importance(model_pipeline, feature_cols):
    """
    Extract and visualize feature importance.
    Works with tree-based models.
    """
    try:
        # Get the actual model from pipeline
        inner_model = model_pipeline.named_steps['model']

        if hasattr(inner_model, 'feature_importances_'):
            importances = inner_model.feature_importances_
        elif hasattr(inner_model, 'coef_'):
            importances = np.abs(inner_model.coef_)
        else:
            print("Model doesn't support feature importance")
            return

        importance_df = pd.DataFrame({
            'feature': feature_cols,
            'importance': importances
        }).sort_values('importance', ascending=True).tail(15)

        fig, ax = plt.subplots(figsize=(8, 6))
        bars = ax.barh(importance_df['feature'], importance_df['importance'],
                       color='steelblue', alpha=0.8)
        ax.set_xlabel('Feature Importance', fontsize=12)
        ax.set_title('Top Features for Stability Prediction\n(Higher = More Predictive)', fontsize=12)
        ax.grid(axis='x', alpha=0.3)

        plt.tight_layout()
        plt.savefig('feature_importance.png', dpi=150, bbox_inches='tight')
        plt.show()
        print("Plot saved: feature_importance.png")

        print("\nTop 10 most predictive features:")
        print(importance_df.tail(10)[['feature', 'importance']].to_string(index=False))

    except Exception as e:
        print(f"Feature importance analysis failed: {e}")


# =============================================================================
# SECTION 5: PREDICT NEW CATALYSTS
# =============================================================================

def predict_new_catalyst(model_pipeline, feature_cols):
    """
    Interactive prediction for new catalyst candidates.
    Returns predicted stability in hours.
    """
    print("\n" + "="*60)
    print("PREDICT STABILITY FOR NEW CATALYST")
    print("="*60)

    # Example predictions for our top hypotheses
    new_catalysts = [
        {
            'name': 'Ca0.15Ru0.03Mn0.82O_x (Hypothesis B1 target)',
            'eta_10_mv': 380, 'tafel_slope': 80, 'electrolyte': 'acid',
            'reaction': 'OER', 'dissolution_potential_v': 1.3, 'acid_stable_score': 2,
            'mo_bond_energy_ev': 3.3, 'mh_bond_energy_ev': None,
            'd_band_center_ev': -2.4, 'eg_electrons': 1.4,
            'n_metals': 3, 'has_cr': 0, 'has_mn': 1, 'coordination': 6,
            'surface_area_m2g': 60, 'crystal_class': 'layered_oxide',
        },
        {
            'name': 'FeCoNiCrW HEA (Hypothesis A, 7-element)',
            'eta_10_mv': 390, 'tafel_slope': 72, 'electrolyte': 'acid',
            'reaction': 'OER', 'dissolution_potential_v': 1.0, 'acid_stable_score': 2,
            'mo_bond_energy_ev': 3.9, 'mh_bond_energy_ev': None,
            'd_band_center_ev': -2.0, 'eg_electrons': 1.1,
            'n_metals': 5, 'has_cr': 1, 'has_mn': 0, 'coordination': 6,
            'surface_area_m2g': 25, 'crystal_class': 'high_entropy',
        },
        {
            'name': 'Co0.85W0.15P (Hypothesis A1)',
            'eta_10_mv': 120, 'tafel_slope': 60, 'electrolyte': 'acid',
            'reaction': 'HER', 'dissolution_potential_v': 0.5, 'acid_stable_score': 2,
            'mo_bond_energy_ev': None, 'mh_bond_energy_ev': 2.7,
            'd_band_center_ev': -1.6, 'eg_electrons': None,
            'n_metals': 2, 'has_cr': 0, 'has_mn': 0, 'coordination': 6,
            'surface_area_m2g': 40, 'crystal_class': 'phosphide',
        },
    ]

    for catalyst in new_catalysts:
        # Build feature vector
        df_new = pd.DataFrame([catalyst])
        df_new = engineer_features(df_new)

        # Fill missing crystal class columns
        crystal_classes = ['LDH', 'perovskite', 'spinel', 'layered_oxide', 'high_entropy',
                           'amorphous', 'phosphide', 'carbide', 'carbide_encapsulated',
                           'SAC', 'alloy', 'nitride', 'sulfide']
        for cls in crystal_classes:
            col = f'is_{cls}'
            if col not in df_new.columns:
                df_new[col] = 0

        # Fill NaN
        df_new = df_new.fillna(df_new.mean(numeric_only=True))

        # Predict (handle missing features gracefully)
        available_features = [f for f in feature_cols if f in df_new.columns]
        missing_features = [f for f in feature_cols if f not in df_new.columns]

        if missing_features:
            for f in missing_features:
                df_new[f] = 0

        X_new = df_new[feature_cols].values

        try:
            log_pred = model_pipeline.predict(X_new)[0]
            pred_h = np.expm1(log_pred)

            print(f"\nCatalyst: {catalyst['name']}")
            print(f"  Predicted stability: {pred_h:.0f} hours")
            print(f"  Context: {'Acid' if catalyst['electrolyte']=='acid' else 'Alkaline'} "
                  f"{catalyst['reaction']}, η₁₀ ≈ {catalyst['eta_10_mv']} mV")
            print(f"  Confidence: {'LOW (extrapolating)' if pred_h > 500 else 'MODERATE'}")
        except Exception as e:
            print(f"  Prediction failed: {e}")


# =============================================================================
# SECTION 6: DISSOLUTION POWER LAW FITTING
# =============================================================================

def fit_dissolution_power_law(time_hours, dissolution_rate, catalyst_name, metal='metal'):
    """
    Fit D(t) = D0 * t^(-alpha) to dissolution kinetics data.

    Args:
        time_hours: array of time points
        dissolution_rate: array of dissolution rates (μg/cm²/h) at each time
        catalyst_name: string for plot labels
        metal: string for which metal is being tracked

    Returns:
        D0, alpha, predicted_10kh_total
    """
    from scipy.optimize import curve_fit

    def power_law(t, D0, alpha):
        return D0 * np.power(t, -alpha)

    # Fit
    p0 = [dissolution_rate[0], 0.5]
    try:
        popt, pcov = curve_fit(power_law, time_hours, dissolution_rate, p0=p0,
                                bounds=([0, 0.01], [np.inf, 2.0]))
        D0, alpha = popt

        # Predict total dissolution at 10,000h
        if alpha != 1.0:
            total_10kh = D0 / (1 - alpha) * (10000**(1-alpha) - time_hours[0]**(1-alpha))
        else:
            total_10kh = D0 * np.log(10000 / time_hours[0])

        stability_prognosis = (
            "GOOD (self-passivating)" if alpha > 0.5 else
            "MODERATE (slow passivation)" if alpha > 0.2 else
            "POOR (constant dissolution)"
        )

        print(f"\n{catalyst_name} — {metal} dissolution kinetics:")
        print(f"  D₀ = {D0:.4f} μg/cm²/h")
        print(f"  α  = {alpha:.3f}")
        print(f"  Prognosis: {stability_prognosis}")
        print(f"  Predicted total dissolution (10,000h): {total_10kh:.1f} μg/cm²")
        print(f"  Acceptable limit (Ir ref): <100 μg/cm²")

        return D0, alpha, total_10kh

    except Exception as e:
        print(f"Fit failed for {catalyst_name}: {e}")
        return None, None, None


# Example usage:
def demo_dissolution_kinetics():
    """Demonstrate with synthetic dissolution data matching literature patterns."""

    t = np.array([1, 2, 5, 10, 20, 50, 100])  # hours

    # NiFe LDH: self-passivating (α ≈ 0.6)
    D_NiFeLDH = 0.5 * t**(-0.6) + np.random.normal(0, 0.02, len(t))

    # CoP in acid: near-constant dissolution (α ≈ 0.1)
    D_CoP = 2.0 * t**(-0.1) + np.random.normal(0, 0.05, len(t))

    # Mo2C@NC: moderate (α ≈ 0.35)
    D_Mo2C = 1.0 * t**(-0.35) + np.random.normal(0, 0.03, len(t))

    print("\nDEMO: Dissolution Power Law Fitting")
    print("(Using synthetic data matching literature patterns)")

    fit_dissolution_power_law(t, np.abs(D_NiFeLDH), 'NiFe LDH', 'Fe')
    fit_dissolution_power_law(t, np.abs(D_CoP), 'CoP (acid)', 'Co')
    fit_dissolution_power_law(t, np.abs(D_Mo2C), 'Mo2C@NC (acid)', 'Mo')


# =============================================================================
# MAIN
# =============================================================================

if __name__ == '__main__':
    print("GREEN HYDROGEN CATALYST STABILITY PREDICTOR")
    print("=" * 60)
    print("Built from literature synthesis — March 2026")
    print("Extend with experimental data as it becomes available\n")

    # Build dataset
    df = build_catalyst_dataset()
    print(f"Dataset: {len(df)} catalysts loaded")
    print(f"  HER: {(df['reaction']=='HER').sum()}, OER: {(df['reaction']=='OER').sum()}")
    print(f"  Acid: {(df['electrolyte']=='acid').sum()}, "
          f"Alkaline: {(df['electrolyte']=='alkaline').sum()}")
    print(f"  Stability range: {df['stability_h'].min()}–{df['stability_h'].max()} hours")

    # Feature engineering
    df_features = engineer_features(df)
    feature_cols = get_feature_columns()

    # Remove any feature columns that don't exist
    feature_cols = [f for f in feature_cols if f in df_features.columns]

    print(f"\nFeatures: {len(feature_cols)} descriptors")

    # Train and evaluate
    results, best_model, best_name = train_stability_model(df_features, feature_cols)

    # Plots
    plot_results(results, df_features, feature_cols)
    analyze_feature_importance(best_model, feature_cols)

    # Predict new catalysts
    predict_new_catalyst(best_model, feature_cols)

    # Dissolution kinetics demo
    demo_dissolution_kinetics()

    print("\n" + "="*60)
    print("NEXT STEPS TO IMPROVE THIS MODEL:")
    print("1. Add more catalyst entries from literature (target: 100+)")
    print("2. Replace estimated features with DFT-computed values")
    print("3. Add ICP-MS dissolution rate data as additional feature")
    print("4. Include synthesis condition features (temperature, precursor)")
    print("5. Train separate models for HER/OER and acid/alkaline")
    print("6. Add SHAP values for individual prediction explanation")
    print("7. Connect to Materials Project API for automated feature extraction")
    print("="*60)
