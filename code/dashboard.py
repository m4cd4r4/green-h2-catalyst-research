"""
Green Hydrogen Catalyst Research Dashboard
==========================================
Streamlit dashboard for exploring catalyst optimization results.
Run from the code/ directory: streamlit run dashboard.py

Requirements (requirements_dashboard.txt):
  streamlit>=1.32.0
  plotly>=5.18.0
  pandas>=2.0.0
  numpy>=1.24.0
"""

import html as _html
import os
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import streamlit as st

# ---------------------------------------------------------------------------
# Page config — must be first Streamlit call
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Green H₂ Catalyst Research",
    page_icon="⚗️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Global dark / glassmorphism CSS
# ---------------------------------------------------------------------------
st.markdown(
    """
    <style>
    /* ── Green Hydrogen palette ──────────────────────────────────────────── */
    /* Background: deep forest  #071a0e                                       */
    /* Surface:    dark moss    #0e2a18                                       */
    /* Primary:    GO green     #22c55e                                       */
    /* Accent:     light green  #86efac                                       */
    /* Highlight:  amber/IrO₂   #eab308                                       */
    /* Muted:      grey         #6b7280                                       */
    /* ─────────────────────────────────────────────────────────────────────── */

    /* Base */
    .stApp { background: #071a0e; color: #e2f5e9; }
    [data-testid="stSidebar"] { background: #0e2a18; border-right: 1px solid #1a3d20; }

    /* Glassmorphism cards */
    .glass-card {
        background: rgba(34,197,94,0.05);
        border: 1px solid rgba(34,197,94,0.18);
        border-radius: 12px;
        padding: 18px 22px;
        backdrop-filter: blur(8px);
        margin-bottom: 14px;
    }

    /* KPI metric override */
    [data-testid="stMetric"] {
        background: rgba(34,197,94,0.06);
        border: 1px solid rgba(34,197,94,0.18);
        border-radius: 10px;
        padding: 14px 18px;
    }
    [data-testid="stMetricValue"] { color: #22c55e; font-size: 1.7rem; font-weight: 700; }
    [data-testid="stMetricLabel"] { color: #6b7280; font-size: 0.82rem; }

    /* Tab styling */
    [data-testid="stTabs"] button { color: #6b7280; font-weight: 500; }
    [data-testid="stTabs"] button[aria-selected="true"] { color: #86efac; border-bottom: 2px solid #22c55e; }

    /* Badge helpers */
    .badge-go    { background:#15803d; color:#dcfce7; border-radius:8px; padding:6px 18px; font-weight:700; font-size:1.15rem; display:inline-block; }
    .badge-nogo  { background:#991b1b; color:#fee2e2; border-radius:8px; padding:6px 18px; font-weight:700; font-size:1.15rem; display:inline-block; }
    .badge-warn  { background:#b45309; color:#fef08a; border-radius:8px; padding:6px 18px; font-weight:700; font-size:1.15rem; display:inline-block; }

    /* Traffic lights */
    .tl-go   { color:#4ade80; font-weight:700; font-size:1.1rem; }
    .tl-warn { color:#eab308; font-weight:700; font-size:1.1rem; }
    .tl-nogo { color:#f87171; font-weight:700; font-size:1.1rem; }

    /* Section headers */
    h3 { color: #86efac; }
    h4 { color: #bbf7d0; }

    /* ── Mobile responsive ────────────────────────────────────────────────── */
    @media (max-width: 768px) {
        /* Stack all st.columns() layouts vertically */
        [data-testid="stHorizontalBlock"] {
            flex-wrap: wrap !important;
        }
        [data-testid="stColumn"] {
            width: 100% !important;
            flex: 1 1 100% !important;
            min-width: 100% !important;
        }

        /* Compact metric cards on mobile */
        [data-testid="stMetric"] { padding: 10px 12px; }
        [data-testid="stMetricValue"] { font-size: 1.3rem; }

        /* Tab bar: 2-row grid — 3 tabs top, 2 bottom */
        /* Hide Streamlit's built-in left/right scroll buttons */
        [data-baseweb="scroll-button-left"],
        [data-baseweb="scroll-button-right"] { display: none !important; }

        /* Let the tab list wrap into rows */
        [data-baseweb="tab-list"] {
            flex-wrap: wrap !important;
            overflow: visible !important;
            height: auto !important;
        }
        /* Parent clip container — allow the second row to show */
        [data-testid="stTabs"] > div:first-child {
            overflow: visible !important;
            height: auto !important;
        }
        /* Each tab: 1/3 width → 3 per row, 2 wrap to second row */
        [data-baseweb="tab"] {
            width: 33.33% !important;
            flex: 0 0 33.33% !important;
            font-size: 0.72rem !important;
            padding: 8px 4px !important;
            white-space: normal !important;
            text-align: center !important;
            min-height: 44px !important;
            line-height: 1.2 !important;
            justify-content: center !important;
            box-sizing: border-box !important;
        }

        /* Reduce chart minimum height on mobile */
        .js-plotly-plot { min-height: 260px; }

        /* Glass cards — tighter padding */
        .glass-card { padding: 12px 14px; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PLOTLY_DARK = "plotly_dark"

GATE_SCRIPTS = {
    "Gate 1 Synthesis": "acid_oer_synthesis_gate1.py",
    "Gate 2 eg Tuning": "acid_oer_gate2_eg.py",
    "Gate 3 Lifetime": "acid_oer_gate3_lifetime.py",
}

# IrO₂ benchmark
IRO2_ETA = 250.0          # mV
IRO2_DISS = 0.01          # µg/cm²/h
IRO2_P50 = 50_000.0       # hours


# ---------------------------------------------------------------------------
# Data loading helpers (cached)
# ---------------------------------------------------------------------------

def _csv_path(filename: str) -> str:
    return os.path.join(SCRIPT_DIR, filename)


def _add_pareto_flag(df: pd.DataFrame) -> pd.DataFrame:
    """Mark Pareto-optimal rows: not dominated on both eta_10_mv and dissolution_rate_ugcm2h."""
    eta = df["eta_10_mv"].values
    diss = df["dissolution_rate_ugcm2h"].values
    on_front = np.ones(len(eta), dtype=bool)
    for i in range(len(eta)):
        for j in range(len(eta)):
            if i != j and eta[j] <= eta[i] and diss[j] <= diss[i] and (eta[j] < eta[i] or diss[j] < diss[i]):
                on_front[i] = False
                break
    df = df.copy()
    df["pareto_front"] = on_front
    return df


@st.cache_data(show_spinner=False)
def load_pareto_9el() -> pd.DataFrame | None:
    path = _csv_path("results_acid_oer_pareto.csv")
    if not os.path.exists(path):
        return None
    df = pd.read_csv(path)
    # Normalise column names to what the dashboard expects
    df = df.rename(columns={"dissolution_ug_per_cm2_per_h": "dissolution_rate_ugcm2h"})
    # Strip x_ prefix from element columns (x_Mn → Mn, etc.)
    df = df.rename(columns={c: c[2:] for c in df.columns if c.startswith("x_")})
    return _add_pareto_flag(df)


@st.cache_data(show_spinner=False)
def load_pareto_camnw() -> pd.DataFrame | None:
    path = _csv_path("results_ca_mnw_pareto.csv")
    if not os.path.exists(path):
        return None
    df = pd.read_csv(path)
    df = df.rename(columns={"dissolution_ug_cm2h": "dissolution_rate_ugcm2h"})
    return _add_pareto_flag(df)


@st.cache_data(show_spinner=False)
def load_stability() -> pd.DataFrame | None:
    path = _csv_path("results_stability_predictions.csv")
    if not os.path.exists(path):
        return None
    return pd.read_csv(path)


@st.cache_data(show_spinner=False)
def load_gate2() -> pd.DataFrame | None:
    path = _csv_path("results_gate2_optimization.csv")
    if not os.path.exists(path):
        return None
    return pd.read_csv(path)


@st.cache_data(show_spinner=False)
def load_gate3() -> pd.DataFrame | None:
    path = _csv_path("results_gate3_projection.csv")
    if not os.path.exists(path):
        return None
    return pd.read_csv(path)


@st.cache_data(show_spinner=False)
def load_gate1() -> pd.DataFrame | None:
    path = _csv_path("results_gate1_synthesis.csv")
    if not os.path.exists(path):
        return None
    return pd.read_csv(path)


def _missing(script_name: str) -> None:
    st.warning(
        f"Data file not found. Run **{script_name}** first to generate this dataset.",
        icon="⚠️",
    )


# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------

with st.sidebar:
    st.markdown(
        """
        <div class='glass-card'>
          <h3 style='margin:0 0 4px 0; color:#67e8f9;'>⚗️ Green H₂ Catalyst</h3>
          <span style='color:#94a3b8; font-size:0.82rem;'>Research Dashboard v1.0</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        f"<span style='color:#64748b; font-size:0.78rem;'>Session loaded: "
        f"{datetime.now().strftime('%Y-%m-%d %H:%M')}</span>",
        unsafe_allow_html=True,
    )

    st.divider()
    st.markdown("**Gate Scripts**")
    for label, script in GATE_SCRIPTS.items():
        st.markdown(
            f"<span style='color:#94a3b8; font-size:0.85rem;'>• {label}: <code>{script}</code></span>",
            unsafe_allow_html=True,
        )

    st.divider()
    st.markdown(
        """
        <span style='color:#64748b; font-size:0.78rem;'>
        Target: η₁₀ &lt; 300 mV, D_ss &lt; 2 µg/cm²/h<br>
        Benchmark: IrO₂ η₁₀=250 mV, D=0.01 µg/cm²/h
        </span>
        """,
        unsafe_allow_html=True,
    )

# ---------------------------------------------------------------------------
# Tabs
# ---------------------------------------------------------------------------

tabs = st.tabs([
    "📊 Pareto Explorer",
    "🧪 Composition Predictor",
    "🚦 Gate Status Board",
    "⏱️ Lifetime Projector",
    "📚 Literature Context",
])


# ===========================================================================
# TAB 1 — Pareto Explorer
# ===========================================================================

with tabs[0]:
    st.markdown("## Pareto Explorer")
    st.markdown(
        "<span style='color:#94a3b8;'>Tradeoff between overpotential (η₁₀) and dissolution rate. "
        "Lower-left is better. Gold ★ = IrO₂ benchmark.</span>",
        unsafe_allow_html=True,
    )

    df9 = load_pareto_9el()
    dfcmw = load_pareto_camnw()

    if df9 is None and dfcmw is None:
        _missing("acid_oer_optimizer.py / ca_mnw_optimizer.py")
    else:
        # Dataset toggle
        dataset_opts = []
        if df9 is not None:
            dataset_opts.append("9-Element Optimizer")
        if dfcmw is not None:
            dataset_opts.append("Ca-Mn-W Focused")

        col_left, col_right = st.columns([1, 3])

        with col_left:
            selected_ds = st.radio("Dataset", dataset_opts, key="pareto_ds")
            st.divider()

        active_df = df9 if selected_ds == "9-Element Optimizer" else dfcmw

        # Sidebar filters rendered inside column for cleanliness
        with col_left:
            eta_max = st.slider(
                "Max η₁₀ (mV)",
                min_value=200,
                max_value=600,
                value=400,
                step=10,
                key="eta_slider",
            )
            diss_max = st.slider(
                "Max dissolution (µg/cm²/h)",
                min_value=0.01,
                max_value=50.0,
                value=10.0,
                step=0.1,
                format="%.2f",
                key="diss_slider",
            )

        # Filter
        mask = (
            (active_df["eta_10_mv"] <= eta_max) &
            (active_df["dissolution_rate_ugcm2h"] <= diss_max)
        )
        filtered = active_df[mask].copy()

        pareto_col = filtered["pareto_front"].astype(bool)
        filtered["_color"] = pareto_col.map({True: "Pareto Front", False: "Non-Pareto"})

        # KPI cards
        pareto_only = filtered[pareto_col]
        k1, k2, k3 = st.columns(3)

        with k1:
            best_eta = pareto_only["eta_10_mv"].min() if not pareto_only.empty else float("nan")
            st.metric("Best η₁₀ (Pareto)", f"{best_eta:.1f} mV" if not np.isnan(best_eta) else "N/A")
        with k2:
            best_diss = pareto_only["dissolution_rate_ugcm2h"].min() if not pareto_only.empty else float("nan")
            st.metric("Best Dissolution Rate", f"{best_diss:.4f} µg/cm²/h" if not np.isnan(best_diss) else "N/A")
        with k3:
            st.metric("Pareto Front Size", str(len(pareto_only)))

        with col_right:
            if filtered.empty:
                st.info("No data points match the current filter settings.")
            else:
                # Build composition hover text
                if selected_ds == "9-Element Optimizer":
                    comp_cols = [c for c in ["Mn", "Fe", "Co", "Ni", "Cr", "V", "W", "Mo", "Ti"] if c in filtered.columns]
                else:
                    comp_cols = [c for c in ["Ca", "Mn", "W", "Ti"] if c in filtered.columns]

                def _hover_text(row: pd.Series) -> str:
                    parts = [f"{c}={row[c]:.3f}" for c in comp_cols if c in row]
                    return "<br>".join(parts)

                filtered["_hover"] = filtered.apply(_hover_text, axis=1)

                fig = go.Figure()

                # Non-Pareto points
                non_p = filtered[~pareto_col]
                if not non_p.empty:
                    fig.add_trace(go.Scatter(
                        x=non_p["dissolution_rate_ugcm2h"],
                        y=non_p["eta_10_mv"],
                        mode="markers",
                        name="Non-Pareto",
                        marker=dict(color="#475569", size=6, opacity=0.5),
                        hovertemplate="η₁₀=%{y:.1f} mV<br>D=%{x:.4f} µg/cm²/h<br>%{customdata}<extra>Non-Pareto</extra>",
                        customdata=non_p["_hover"],
                    ))

                # Pareto-front points
                p_pts = filtered[pareto_col]
                if not p_pts.empty:
                    fig.add_trace(go.Scatter(
                        x=p_pts["dissolution_rate_ugcm2h"],
                        y=p_pts["eta_10_mv"],
                        mode="markers",
                        name="Pareto Front",
                        marker=dict(color="#38bdf8", size=9, line=dict(color="#0ea5e9", width=1)),
                        hovertemplate="η₁₀=%{y:.1f} mV<br>D=%{x:.4f} µg/cm²/h<br>%{customdata}<extra>Pareto</extra>",
                        customdata=p_pts["_hover"],
                    ))

                # IrO₂ benchmark star
                fig.add_trace(go.Scatter(
                    x=[IRO2_DISS],
                    y=[IRO2_ETA],
                    mode="markers+text",
                    name="IrO₂ Benchmark",
                    marker=dict(symbol="star", color="#fbbf24", size=18),
                    text=["IrO₂"],
                    textposition="top right",
                    textfont=dict(color="#fbbf24"),
                    hovertemplate="IrO₂<br>η₁₀=250 mV<br>D=0.01 µg/cm²/h<extra>Benchmark</extra>",
                ))

                fig.update_xaxes(type="log", title="Dissolution Rate (µg/cm²/h) — log scale")
                fig.update_yaxes(title="η₁₀ (mV) — lower is better")
                fig.update_layout(
                    template=PLOTLY_DARK,
                    title=f"Pareto Front — {selected_ds}",
                    height=520,
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                )
                st.plotly_chart(fig, use_container_width=True)


# ===========================================================================
# TAB 2 — Composition Predictor
# ===========================================================================

with tabs[1]:
    st.markdown("## Composition Predictor")
    st.markdown(
        "<span style='color:#94a3b8;'>Adjust element fractions below. "
        "Real-time gate evaluation uses the volcano model.</span>",
        unsafe_allow_html=True,
    )

    c_slid, c_res = st.columns([1, 2])

    with c_slid:
        st.markdown("#### Element Fractions")
        ca_pct = st.slider("Ca (%)", 0, 100, 11, key="ca")
        mn_pct = st.slider("Mn (%)", 0, 100, 55, key="mn")
        w_pct  = st.slider("W (%)",  0, 100, 34, key="w")
        ti_pct = st.slider("Ti (%)", 0, 100,  0, key="ti")

        total = ca_pct + mn_pct + w_pct + ti_pct
        if total > 100:
            st.error(f"Total = {total}% — must be ≤ 100%. Reduce one element.")
            st.stop()
        elif total < 100:
            remainder = 100 - total
            st.info(f"Remainder {remainder}% assigned to O (oxygen / lattice balance).")
        else:
            st.success("Total = 100% ✓")

    # Compute derived quantities
    ca = ca_pct / 100
    mn = mn_pct / 100
    w  = w_pct  / 100
    ti = ti_pct / 100

    f_cawo4 = min(ca, w) * 2 if ca * w > 0.04 else ca * w * 50
    e_diss = 0.85 * (1 - f_cawo4 - w - ti) + 1.05 * w + 1.38 * f_cawo4 + 1.20 * ti
    eg = min(0.75, 2 * ca / (mn + 0.001))
    eta_10 = 245 + 220 * abs(eg - 0.52) ** 1.5

    # Gate traffic lights
    # Gate 1: f_CaWO4 ≥ 0.15 is good synthesis target
    g1_val = f_cawo4
    if g1_val >= 0.15:
        g1_label, g1_cls = "GO", "tl-go"
    elif g1_val >= 0.05:
        g1_label, g1_cls = "MARGINAL", "tl-warn"
    else:
        g1_label, g1_cls = "NO-GO", "tl-nogo"

    # Gate 2: eg within [0.45, 0.59] for volcano optimum
    if 0.45 <= eg <= 0.59:
        g2_label, g2_cls = "GO", "tl-go"
    elif 0.38 <= eg <= 0.65:
        g2_label, g2_cls = "MARGINAL", "tl-warn"
    else:
        g2_label, g2_cls = "NO-GO", "tl-nogo"

    # Gate 3: eta_10 < 300 mV
    if eta_10 < 300:
        g3_label, g3_cls = "GO", "tl-go"
    elif eta_10 < 360:
        g3_label, g3_cls = "MARGINAL", "tl-warn"
    else:
        g3_label, g3_cls = "NO-GO", "tl-nogo"

    # Synthesis recommendation
    if w_pct > 0 and ca_pct > 0:
        synth_rec = (
            f"Co-precipitation at pH 9–10, T=60°C, anneal 450°C/4h in air. "
            f"Expected CaWO₄ phase fraction ~{f_cawo4*100:.1f}%."
        )
    elif mn_pct > 70:
        synth_rec = "High-Mn regime: hydrothermal synthesis at 180°C/12h preferred for δ-MnO₂ structure."
    else:
        synth_rec = "Sol-gel route with citrate chelation recommended. Calcination 400–500°C."

    with c_res:
        st.markdown("#### Predicted Properties")

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("CaWO₄ Fraction", f"{f_cawo4*100:.1f}%")
        m2.metric("Composite E_diss (eV)", f"{e_diss:.3f}")
        m3.metric("eg Estimate", f"{eg:.3f}")
        m4.metric("η₁₀ Estimate", f"{eta_10:.1f} mV")

        st.markdown("---")
        st.markdown("#### Gate Traffic Lights")

        gc1, gc2, gc3 = st.columns(3)
        with gc1:
            st.markdown(
                f"<div class='glass-card'><b>Gate 1 — Synthesis</b><br>"
                f"f_CaWO₄ = {f_cawo4*100:.1f}%<br>"
                f"<span class='{g1_cls}'>{g1_label}</span></div>",
                unsafe_allow_html=True,
            )
        with gc2:
            st.markdown(
                f"<div class='glass-card'><b>Gate 2 — eg Tuning</b><br>"
                f"eg = {eg:.3f} (target 0.45–0.59)<br>"
                f"<span class='{g2_cls}'>{g2_label}</span></div>",
                unsafe_allow_html=True,
            )
        with gc3:
            st.markdown(
                f"<div class='glass-card'><b>Gate 3 — Activity</b><br>"
                f"η₁₀ ≈ {eta_10:.0f} mV (target &lt;300)<br>"
                f"<span class='{g3_cls}'>{g3_label}</span></div>",
                unsafe_allow_html=True,
            )

        # Volcano curve mini-chart
        eg_range = np.linspace(0.1, 1.0, 200)
        eta_range = 245 + 220 * np.abs(eg_range - 0.52) ** 1.5

        fig_v = go.Figure()
        fig_v.add_trace(go.Scatter(
            x=eg_range, y=eta_range, mode="lines",
            name="Volcano model", line=dict(color="#38bdf8", width=2),
        ))
        fig_v.add_trace(go.Scatter(
            x=[eg], y=[eta_10], mode="markers+text",
            name="Your composition",
            marker=dict(color="#f97316", size=12, symbol="circle"),
            text=[f"eg={eg:.2f}"],
            textposition="top center",
            textfont=dict(color="#f97316"),
        ))
        fig_v.add_hline(y=300, line=dict(color="#4ade80", dash="dash"), annotation_text="300 mV target")
        fig_v.update_layout(
            template=PLOTLY_DARK,
            title="Volcano Curve — η₁₀ vs eg",
            xaxis_title="eg (e_g orbital occupancy)",
            yaxis_title="η₁₀ (mV)",
            height=320,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig_v, use_container_width=True)

        st.markdown("#### Synthesis Recommendation")
        st.markdown(
            f"<div class='glass-card'>{_html.escape(synth_rec)}</div>",
            unsafe_allow_html=True,
        )


# ===========================================================================
# TAB 3 — Gate Status Board
# ===========================================================================

with tabs[2]:
    st.markdown("## Gate Status Board")

    df_g1 = load_gate1()
    df_g2 = load_gate2()
    df_g3 = load_gate3()

    gc1, gc2, gc3 = st.columns(3)

    # --- Gate 1 ---
    with gc1:
        if df_g1 is None:
            _missing("acid_oer_synthesis_gate1.py")
        else:
            passes = df_g1["gate1_pass"].sum() if "gate1_pass" in df_g1.columns else 0
            total_g1 = len(df_g1)
            badge_html = (
                "<span class='badge-go'>GO</span>"
                if passes > 0
                else "<span class='badge-nogo'>NO-GO</span>"
            )
            st.markdown(
                f"<div class='glass-card'><b>Gate 1 — Synthesis Sweep</b><br>"
                f"{badge_html} &nbsp; {passes}/{total_g1} conditions pass</div>",
                unsafe_allow_html=True,
            )

            # Heatmap: f_CaWO4 vs pH and T_C at time_h=4
            sub = df_g1[df_g1["time_h"] == 4] if "time_h" in df_g1.columns else df_g1
            if sub.empty:
                sub = df_g1

            if "pH" in sub.columns and "T_C" in sub.columns and "f_CaWO4" in sub.columns:
                try:
                    pivot = sub.pivot_table(
                        values="f_CaWO4", index="T_C", columns="pH", aggfunc="mean"
                    )
                    fig_h = px.imshow(
                        pivot,
                        color_continuous_scale="Viridis",
                        aspect="auto",
                        labels={"x": "pH", "y": "T (°C)", "color": "f_CaWO₄"},
                        title="f_CaWO₄ Heatmap (time=4h)",
                    )
                    fig_h.update_layout(
                        template=PLOTLY_DARK,
                        height=380,
                        paper_bgcolor="rgba(0,0,0,0)",
                        plot_bgcolor="rgba(0,0,0,0)",
                    )
                    st.plotly_chart(fig_h, use_container_width=True)
                except Exception as err:
                    st.warning(f"Could not render heatmap: {err}")
            else:
                st.dataframe(sub.head(20), use_container_width=True)

    # --- Gate 2 ---
    with gc2:
        if df_g2 is None:
            _missing("acid_oer_gate2_eg.py")
        else:
            if "gate2_pass" in df_g2.columns:
                passes_g2 = df_g2["gate2_pass"].sum()
                total_g2 = len(df_g2)
                badge2 = (
                    "<span class='badge-go'>GO</span>"
                    if passes_g2 > 0
                    else "<span class='badge-nogo'>NO-GO</span>"
                )
            else:
                badge2 = "<span class='badge-warn'>DATA?</span>"
                passes_g2, total_g2 = 0, len(df_g2)

            st.markdown(
                f"<div class='glass-card'><b>Gate 2 — eg Tuning</b><br>"
                f"{badge2} &nbsp; {passes_g2}/{total_g2} compositions pass</div>",
                unsafe_allow_html=True,
            )

            if "eta_opt_mv" in df_g2.columns and "name" in df_g2.columns:
                color_col = df_g2["gate2_pass"].map({True: "#4ade80", False: "#f87171"}) if "gate2_pass" in df_g2.columns else "#38bdf8"
                fig_g2 = go.Figure(go.Bar(
                    x=df_g2["name"],
                    y=df_g2["eta_opt_mv"],
                    marker_color=color_col if isinstance(color_col, list) else color_col.tolist(),
                    text=df_g2["eta_opt_mv"].round(1).astype(str) + " mV",
                    textposition="outside",
                ))
                fig_g2.add_hline(y=300, line=dict(color="#fbbf24", dash="dash"), annotation_text="Target 300 mV")
                fig_g2.add_hline(y=IRO2_ETA, line=dict(color="#34d399", dash="dot"), annotation_text="IrO₂ 250 mV")
                fig_g2.update_layout(
                    template=PLOTLY_DARK,
                    title="Optimised η₁₀ per Composition",
                    yaxis_title="η₁₀_opt (mV)",
                    height=380,
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                )
                st.plotly_chart(fig_g2, use_container_width=True)
            else:
                st.dataframe(df_g2.head(20), use_container_width=True)

    # --- Gate 3 ---
    with gc3:
        if df_g3 is None:
            _missing("acid_oer_gate3_lifetime.py")
        else:
            if "gate3_pass" in df_g3.columns:
                passes_g3 = df_g3["gate3_pass"].sum()
                total_g3 = len(df_g3)
                badge3 = (
                    "<span class='badge-go'>GO</span>"
                    if passes_g3 > 0
                    else "<span class='badge-nogo'>NO-GO</span>"
                )
            else:
                badge3 = "<span class='badge-warn'>DATA?</span>"
                passes_g3, total_g3 = 0, len(df_g3)

            st.markdown(
                f"<div class='glass-card'><b>Gate 3 — Lifetime Projection</b><br>"
                f"{badge3} &nbsp; {passes_g3}/{total_g3} compositions pass</div>",
                unsafe_allow_html=True,
            )

            if (
                "name" in df_g3.columns
                and "D_ss_cont" in df_g3.columns
                and "D_ss_pulsed" in df_g3.columns
            ):
                fig_g3 = go.Figure()
                fig_g3.add_trace(go.Bar(
                    name="D_ss Continuous",
                    x=df_g3["name"],
                    y=df_g3["D_ss_cont"],
                    marker_color="#60a5fa",
                ))
                fig_g3.add_trace(go.Bar(
                    name="D_ss Pulsed",
                    x=df_g3["name"],
                    y=df_g3["D_ss_pulsed"],
                    marker_color="#f97316",
                ))
                fig_g3.add_hline(y=IRO2_DISS, line=dict(color="#fbbf24", dash="dot"),
                                  annotation_text="IrO₂ D_ss")
                fig_g3.update_layout(
                    template=PLOTLY_DARK,
                    barmode="group",
                    title="Steady-state Dissolution per Composition",
                    yaxis_title="D_ss (µg/cm²/h)",
                    height=300,
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                )
                st.plotly_chart(fig_g3, use_container_width=True)

                # Pass/fail table
                pass_cols = [c for c in ["name", "p50_cont_h", "p50_pulsed_h", "gate3_pass"] if c in df_g3.columns]
                if pass_cols:
                    st.dataframe(df_g3[pass_cols], use_container_width=True, hide_index=True)
            else:
                st.dataframe(df_g3.head(20), use_container_width=True)


# ===========================================================================
# TAB 4 — Lifetime Projector
# ===========================================================================

with tabs[3]:
    st.markdown("## Lifetime Projector")
    st.markdown(
        "<span style='color:#94a3b8;'>P50 lifetime = median time to exceed 2× initial dissolution rate. "
        "Pulsed operation (electrolysis with start/stop) accelerates degradation.</span>",
        unsafe_allow_html=True,
    )

    df_lt = load_gate3()

    if df_lt is None:
        _missing("acid_oer_gate3_lifetime.py")
    else:
        if "name" not in df_lt.columns:
            st.error("Column 'name' not found in results_gate3_projection.csv")
        else:
            comp_names = df_lt["name"].tolist()
            selected_comp = st.selectbox("Select composition", comp_names, key="lt_comp")

            row = df_lt[df_lt["name"] == selected_comp].iloc[0]

            left_lt, right_lt = st.columns([1, 2])

            with left_lt:
                d_val = row.get("D_ss_pulsed", float("nan"))
                p50_val = row.get("p50_pulsed_h", float("nan"))
                p50_cont_val = row.get("p50_cont_h", float("nan"))
                g3_pass = row.get("gate3_pass", False)

                st.metric("D_ss Pulsed (µg/cm²/h)", f"{d_val:.4f}" if not np.isnan(d_val) else "N/A")
                st.metric("P50 Pulsed (hours)", f"{p50_val:,.0f}" if not np.isnan(p50_val) else "N/A")
                st.metric("P50 Continuous (hours)", f"{p50_cont_val:,.0f}" if not np.isnan(p50_cont_val) else "N/A")

                if g3_pass:
                    st.markdown("<span class='badge-go'>GATE 3: GO</span>", unsafe_allow_html=True)
                else:
                    st.markdown("<span class='badge-nogo'>GATE 3: NO-GO</span>", unsafe_allow_html=True)

                st.markdown("---")
                st.markdown(
                    """
                    <div class='glass-card'>
                    <b>What P50 means for a 1 MW stack</b><br><br>
                    A 1 MW PEM electrolyser contains ~200 cells, each with ~0.1 m² active area.
                    P50 is the <em>median</em> time before 50% of catalysts exceed the degradation threshold —
                    a practical end-of-life signal.<br><br>
                    • P50 &gt; 20,000 h → &gt;2 years of daily operation<br>
                    • P50 &gt; 50,000 h → comparable to IrO₂ commercial stacks<br>
                    • Pulsed P50 accounts for renewable intermittency (8h/day cycles)
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            with right_lt:
                # Comparison bar chart for all compositions
                if "p50_pulsed_h" in df_lt.columns:
                    color_bars = df_lt["gate3_pass"].map({True: "#4ade80", False: "#f87171"}) if "gate3_pass" in df_lt.columns else "#38bdf8"

                    fig_lt = go.Figure()
                    fig_lt.add_trace(go.Bar(
                        x=df_lt["name"],
                        y=df_lt["p50_pulsed_h"],
                        name="P50 Lifetime (pulsed)",
                        marker_color=color_bars.tolist() if hasattr(color_bars, "tolist") else color_bars,
                        text=df_lt["p50_pulsed_h"].apply(lambda v: f"{v:,.0f} h" if pd.notna(v) else "N/A"),
                        textposition="outside",
                    ))

                    # Highlight selected composition
                    sel_idx = df_lt["name"].tolist().index(selected_comp)
                    fig_lt.add_annotation(
                        x=selected_comp,
                        y=df_lt.iloc[sel_idx]["p50_pulsed_h"],
                        text="◀ Selected",
                        showarrow=False,
                        xshift=50,
                        font=dict(color="#fbbf24"),
                    )

                    # IrO₂ reference line
                    fig_lt.add_hline(
                        y=IRO2_P50,
                        line=dict(color="#fbbf24", dash="dot", width=2),
                        annotation_text=f"IrO₂ P50 ~{IRO2_P50/1000:.0f}k h",
                        annotation_font_color="#fbbf24",
                    )

                    fig_lt.update_layout(
                        template=PLOTLY_DARK,
                        title="P50 Lifetime Comparison — Pulsed Operation",
                        yaxis_title="P50 Pulsed (hours)",
                        height=420,
                        paper_bgcolor="rgba(0,0,0,0)",
                        plot_bgcolor="rgba(0,0,0,0)",
                    )
                    st.plotly_chart(fig_lt, use_container_width=True)
                else:
                    st.info("Column 'p50_pulsed_h' not found in gate 3 results.")

                # Full table
                show_cols = [c for c in [
                    "name", "f_CaWO4", "cum_500h_cont", "cum_500h_pulsed",
                    "D_ss_cont", "D_ss_pulsed", "p50_cont_h", "p50_pulsed_h", "gate3_pass"
                ] if c in df_lt.columns]
                st.dataframe(df_lt[show_cols], use_container_width=True, hide_index=True)


# ===========================================================================
# TAB 5 — Literature Context
# ===========================================================================

with tabs[4]:
    st.markdown("## Literature Context")
    st.markdown(
        "<span style='color:#94a3b8;'>Comparison of best reported earth-abundant acid OER catalysts. "
        "Our best prediction is highlighted.</span>",
        unsafe_allow_html=True,
    )

    lit_data = {
        "Material": [
            "α-MnO₂",
            "δ-MnO₂",
            "Mn₂O₃",
            "MnCoP",
            "IrO₂ (benchmark)",
            "Ca₀.₁₁Mn₀.₅₅W₀.₃₄ (this work)",
        ],
        "η₁₀ (mV)": [360, 340, 400, 285, 250, 278],
        "D_ss (µg/cm²/h)": [25.0, 18.0, None, None, 0.01, 1.8],
        "Acid Stable": ["Yes", "Yes", "Yes", "No", "Yes", "Predicted"],
        "Notes": [
            "Standard polymorphs, poor stability",
            "Better layered structure, still unstable",
            "High overpotential, poor activity",
            "Excellent η₁₀ but dissolves rapidly in acid",
            "Commercial standard, Ir scarcity issue",
            "Volcano-optimised, CaWO₄ protection layer",
        ],
    }

    df_lit = pd.DataFrame(lit_data)

    # Style our prediction row
    def _highlight_row(row: pd.Series):
        if "this work" in str(row["Material"]):
            return ["background-color: rgba(99,202,220,0.15); color: #67e8f9"] * len(row)
        if "benchmark" in str(row["Material"]).lower():
            return ["background-color: rgba(251,191,36,0.10); color: #fbbf24"] * len(row)
        return [""] * len(row)

    styled = df_lit.style.apply(_highlight_row, axis=1)
    st.dataframe(styled, use_container_width=True, hide_index=True)

    st.divider()

    # Horizontal bar charts
    l_col, r_col = st.columns(2)

    with l_col:
        df_eta = df_lit.dropna(subset=["η₁₀ (mV)"]).copy()
        colors_eta = [
            "#fbbf24" if "benchmark" in m else
            "#67e8f9" if "this work" in m else "#60a5fa"
            for m in df_eta["Material"]
        ]
        fig_eta = go.Figure(go.Bar(
            y=df_eta["Material"],
            x=df_eta["η₁₀ (mV)"],
            orientation="h",
            marker_color=colors_eta,
            text=df_eta["η₁₀ (mV)"].astype(str) + " mV",
            textposition="outside",
        ))
        fig_eta.add_vline(x=300, line=dict(color="#4ade80", dash="dash"), annotation_text="Target 300 mV")
        fig_eta.update_layout(
            template=PLOTLY_DARK,
            title="Overpotential η₁₀ (mV) — lower is better",
            xaxis_title="η₁₀ (mV)",
            height=380,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig_eta, use_container_width=True)

    with r_col:
        df_dss = df_lit.dropna(subset=["D_ss (µg/cm²/h)"]).copy()
        colors_dss = [
            "#fbbf24" if "benchmark" in m else
            "#67e8f9" if "this work" in m else "#f97316"
            for m in df_dss["Material"]
        ]
        fig_dss = go.Figure(go.Bar(
            y=df_dss["Material"],
            x=df_dss["D_ss (µg/cm²/h)"],
            orientation="h",
            marker_color=colors_dss,
            text=df_dss["D_ss (µg/cm²/h)"].astype(str) + " µg/cm²/h",
            textposition="outside",
        ))
        fig_dss.add_vline(x=2.0, line=dict(color="#4ade80", dash="dash"), annotation_text="Target 2 µg/cm²/h")
        fig_dss.update_layout(
            template=PLOTLY_DARK,
            title="Dissolution Rate D_ss (µg/cm²/h) — lower is better",
            xaxis_title="D_ss (µg/cm²/h)",
            xaxis_type="log",
            height=380,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig_dss, use_container_width=True)

    st.divider()
    st.markdown(
        """
        <div class='glass-card'>
        <b>Key context notes</b><br><br>
        • <b>MnCoP</b> shows outstanding intrinsic activity but dissolves in &lt;10h in 0.1M H₂SO₄ — not viable.<br>
        • <b>CaWO₄ protective layer</b> is the distinguishing feature of this work: Ca²⁺ and WO₄²⁻ ions re-deposit
          under operating conditions, acting as a self-healing barrier against Mn dissolution.<br>
        • <b>IrO₂</b> remains the benchmark but Ir abundance is ~0.003 ppb in Earth's crust,
          constraining global electrolyser scale-up; earth-abundant alternatives are critical path to green H₂ at scale.
        </div>
        """,
        unsafe_allow_html=True,
    )
