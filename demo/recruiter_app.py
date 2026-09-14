from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import networkx as nx
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from simulator import run_simulation, summarize_final_state
from demo.hardening import (
    NETWORKS,
    calibrated_agents,
    concentration_metrics,
    country_exposures,
    network_edges,
    run_monte_carlo,
)


st.set_page_config(
    page_title="Monetary Network Resilience Simulator — Recruiter Demo",
    page_icon="🌐",
    layout="wide",
)

st.title("Monetary Network Resilience Simulator")
st.caption(
    "Recruiter / public demo — original scenario engine plus Monte Carlo uncertainty, "
    "country-level agents, network analysis, and historically anchored calibration."
)


with st.sidebar:
    st.header("Demo controls")
    profile = st.selectbox(
        "Model profile",
        ["Historically anchored recruiter demo", "Original baseline model"],
    )
    start_year = int(
        st.number_input("Start year", min_value=2024, max_value=2040, value=2026, step=1)
    )
    horizon = int(st.slider("Horizon (years)", 10, 15, 15))
    seed = int(st.number_input("Random seed", 0, 1_000_000, 42, 1))
    runs = int(st.slider("Monte Carlo runs", 100, 1000, 300, 100))
    calibration_weight = 0.30 if profile.startswith("Historically") else 0.0
    if profile.startswith("Historically"):
        calibration_weight = st.slider(
            "Historical calibration weight",
            0.10,
            0.60,
            0.30,
            0.05,
            help="Blend weight applied only to the USD/EUR/BRICS currency-network subset.",
        )
    st.info(
        "This is an exploratory systems model, not investment advice and not a forecast "
        "of official reserve shares."
    )


@st.cache_data(show_spinner=False)
def deterministic_rows(start_year: int, horizon: int, seed: int, weight: float):
    agents = calibrated_agents(weight)
    return run_simulation(
        years=horizon,
        start_year=start_year,
        seed=seed,
        agents=agents,
    )


@st.cache_data(show_spinner=False)
def mc_rows(start_year: int, horizon: int, seed: int, runs: int, weight: float):
    return run_monte_carlo(
        runs=runs,
        years=horizon,
        start_year=start_year,
        seed=seed,
        calibration_weight=weight,
    )


rows = deterministic_rows(start_year, horizon, seed, calibration_weight)
df = pd.DataFrame(rows)
mc = pd.DataFrame(mc_rows(start_year, horizon, seed, runs, calibration_weight))
summary = pd.DataFrame(summarize_final_state(rows))
metrics = concentration_metrics(rows)
final_year = int(df["year"].max())
final_state = df[df["year"] == final_year].copy()


def network_graph(exposure_df: pd.DataFrame) -> go.Figure:
    edges = network_edges(exposure_df.to_dict("records"), top_n=2)
    graph = nx.Graph()
    countries = sorted(exposure_df["country"].unique())
    for country in countries:
        graph.add_node(country, kind="country")
    for network in NETWORKS:
        graph.add_node(network, kind="network")
    for edge in edges:
        graph.add_edge(edge["source"], edge["target"], weight=edge["weight"])

    pos = nx.spring_layout(graph, seed=42, k=0.72)

    edge_x, edge_y = [], []
    for source, target in graph.edges():
        x0, y0 = pos[source]
        x1, y1 = pos[target]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])

    edge_trace = go.Scatter(
        x=edge_x,
        y=edge_y,
        mode="lines",
        hoverinfo="skip",
        line={"width": 1},
        name="Strongest links",
    )

    country_x, country_y, country_text = [], [], []
    for node in countries:
        x, y = pos[node]
        country_x.append(x)
        country_y.append(y)
        top = exposure_df[exposure_df["country"] == node].sort_values(
            "exposure_pct", ascending=False
        ).iloc[0]
        country_text.append(
            f"<b>{node}</b><br>Top network: {top['network']}<br>"
            f"Modeled exposure: {top['exposure_pct']:.1f}%"
        )

    country_trace = go.Scatter(
        x=country_x,
        y=country_y,
        mode="markers+text",
        text=countries,
        textposition="top center",
        hovertext=country_text,
        hoverinfo="text",
        marker={"size": 14, "symbol": "circle"},
        name="Country agents",
    )

    share_map = dict(zip(final_state["agent"], final_state["share_pct"]))
    network_x, network_y, network_text, network_size = [], [], [], []
    for node in NETWORKS:
        x, y = pos[node]
        network_x.append(x)
        network_y.append(y)
        share = float(share_map.get(node, 0.0))
        network_text.append(
            f"<b>{node}</b><br>Modeled final share: {share:.1f}%"
        )
        network_size.append(20 + share * 0.8)

    network_trace = go.Scatter(
        x=network_x,
        y=network_y,
        mode="markers+text",
        text=NETWORKS,
        textposition="bottom center",
        hovertext=network_text,
        hoverinfo="text",
        marker={"size": network_size, "symbol": "diamond"},
        name="Monetary networks",
    )

    fig = go.Figure([edge_trace, country_trace, network_trace])
    fig.update_layout(
        title=f"Country-to-network affinity graph — modeled state in {final_year}",
        showlegend=True,
        hovermode="closest",
        margin={"l": 10, "r": 10, "t": 55, "b": 10},
        xaxis={"visible": False},
        yaxis={"visible": False},
        height=680,
    )
    return fig


overview_tab, mc_tab, network_tab, calibration_tab, model_card_tab = st.tabs(
    ["Executive overview", "Monte Carlo", "Country network", "Calibration", "Model card"]
)


with overview_tab:
    c1, c2, c3, c4 = st.columns(4)
    top_row = summary.iloc[0]
    c1.metric("Leading network", str(top_row["agent"]), f"{float(top_row['share_pct']):.1f}%")
    c2.metric("Effective networks", f"{metrics['effective_networks']:.2f}")
    c3.metric("Diversification index", f"{metrics['diversification_index']:.3f}")
    c4.metric("Country agents", "12")

    st.markdown(
        """
**What changed for the recruiter build:** the public demo still executes the original
simulation engine, but adds an uncertainty layer, country-agent behavior, graph-based
network exposure, and a documented institutional-data calibration layer.
        """
    )

    fig = px.line(
        df,
        x="year",
        y="share_pct",
        color="agent",
        markers=True,
        labels={
            "year": "Year",
            "share_pct": "Modeled network share (%)",
            "agent": "Network",
        },
        title="Original engine — modeled network share through time",
    )
    st.plotly_chart(fig, use_container_width=True)

    left, right = st.columns([1.25, 1])
    with left:
        st.subheader("Final modeled ranking")
        st.dataframe(summary, use_container_width=True, hide_index=True)
    with right:
        st.subheader("Shock timeline")
        shocks = (
            df[(df["event"] != "No discrete shock") & (df["event"] != "Baseline")]
            [["year", "event"]]
            .drop_duplicates()
        )
        st.dataframe(shocks, use_container_width=True, hide_index=True)


with mc_tab:
    st.subheader("Monte Carlo confidence bands")
    selected = st.selectbox("Network", NETWORKS, index=0)
    selected_mc = mc[mc["agent"] == selected].sort_values("year")

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=selected_mc["year"],
            y=selected_mc["p90"],
            mode="lines",
            line={"width": 0},
            hoverinfo="skip",
            showlegend=False,
        )
    )
    fig.add_trace(
        go.Scatter(
            x=selected_mc["year"],
            y=selected_mc["p10"],
            mode="lines",
            fill="tonexty",
            name="10th–90th percentile",
            hovertemplate="%{x}: %{y:.2f}%<extra></extra>",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=selected_mc["year"],
            y=selected_mc["median"],
            mode="lines+markers",
            name="Median",
            hovertemplate="%{x}: %{y:.2f}%<extra></extra>",
        )
    )
    fig.update_layout(
        title=f"{selected}: {runs:,}-run uncertainty envelope",
        xaxis_title="Year",
        yaxis_title="Modeled network share (%)",
        hovermode="x unified",
    )
    st.plotly_chart(fig, use_container_width=True)

    final_mc = (
        mc[mc["year"] == mc["year"].max()]
        [["agent", "p10", "median", "p90", "mean"]]
        .sort_values("median", ascending=False)
    )
    st.subheader(f"Final-year distribution ({final_year})")
    st.dataframe(final_mc, use_container_width=True, hide_index=True)
    st.caption(
        "Confidence bands describe stochastic variation within this scenario model. "
        "They are not statistical confidence intervals for real-world outcomes."
    )


with network_tab:
    st.subheader("Country-level agents and network graph")
    exposure = pd.DataFrame(country_exposures(rows))
    st.plotly_chart(network_graph(exposure), use_container_width=True)

    leaders = (
        exposure.sort_values(["country", "exposure_pct"], ascending=[True, False])
        .groupby("country", as_index=False)
        .first()[["country", "region", "network", "exposure_pct"]]
        .rename(columns={"network": "top_network", "exposure_pct": "top_exposure_pct"})
    )
    st.dataframe(leaders, use_container_width=True, hide_index=True)
    st.caption(
        "Country affinities are scenario assumptions designed to demonstrate agent behavior. "
        "They are not claims about confidential reserve allocations or government policy."
    )


with calibration_tab:
    st.subheader("Historical-data calibration")
    calibration_path = ROOT / "demo" / "data" / "calibration_reference.csv"
    calibration = pd.read_csv(calibration_path)

    cofer = calibration[calibration["dataset"] == "IMF COFER"].copy()
    bis = calibration[calibration["dataset"] == "BIS Triennial FX Survey"].copy()

    left, right = st.columns(2)
    with left:
        fig_cofer = px.line(
            cofer,
            x="period",
            y="value",
            color="series",
            markers=True,
            labels={"value": "Share (%)", "period": "Period", "series": "Currency"},
            title="IMF COFER reserve-share anchors",
        )
        st.plotly_chart(fig_cofer, use_container_width=True)
    with right:
        fig_bis = px.line(
            bis,
            x="period",
            y="value",
            color="series",
            markers=True,
            labels={"value": "FX turnover share (%)", "period": "Survey", "series": "Currency"},
            title="BIS FX-turnover anchors",
        )
        st.plotly_chart(fig_bis, use_container_width=True)

    st.dataframe(calibration, use_container_width=True, hide_index=True)
    st.markdown(
        """
The calibration is intentionally **light-touch**. IMF COFER informs the reserve-currency
signal and the BIS Triennial Survey informs the market-usage signal. The model blends
those signals only into the USD/EUR/BRICS currency-network subset. Gold, digital assets,
and neutral-state behavior remain scenario variables because they are not directly
comparable to COFER currency shares.

The calibration layer therefore improves grounding without pretending that unlike
datasets measure the same thing.
        """
    )


with model_card_tab:
    st.subheader("Recruiter-facing model card")
    st.markdown(
        f"""
**Purpose**  
Explore resilience and substitution across competing monetary and payment networks over
a {horizon}-year scenario horizon.

**Core engine**  
The original `simulator.py` remains the source of truth for annual network evolution.
This demo calls that engine directly.

**Advanced layers**
- {runs:,}-run Monte Carlo simulation with 10th / median / 90th percentile bands.
- 12 country-level agents with transparent behavioral affinities.
- Graph representation of strongest country-to-network connections.
- Historical calibration using IMF COFER and BIS Triennial FX data.
- Concentration and diversification diagnostics.
- Reproducible seeds and exportable tables.

**Design principle**  
Observed public data, model mechanics, and scenario assumptions are kept separate.

**Limitations**  
This is a stylized systems model. It does not estimate causal effects, does not infer
confidential country reserve allocations, and should not be treated as a market,
exchange-rate, or geopolitical forecast.
        """
    )

    export = mc.to_csv(index=False).encode("utf-8")
    st.download_button(
        "Download Monte Carlo bands",
        export,
        "recruiter_demo_monte_carlo_bands.csv",
        "text/csv",
    )
