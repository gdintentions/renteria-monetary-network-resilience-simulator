import pandas as pd
import plotly.express as px
import streamlit as st

from simulator import run_simulation, summarize_final_state

st.set_page_config(page_title="Monetary Network Resilience Simulator", layout="wide")

st.title("Monetary Network Resilience Simulator")
st.caption(
    "A stylized scenario-analysis tool for exploring how global payment and settlement networks might evolve under geopolitical, fiscal, cyber, and digital-currency shocks."
)

with st.sidebar:
    st.header("Scenario controls")
    start_year = st.number_input("Start year", min_value=2024, max_value=2040, value=2026, step=1)
    horizon = st.slider("Simulation horizon (years)", min_value=10, max_value=15, value=15)
    seed = st.number_input("Random seed", min_value=0, max_value=100000, value=42, step=1)
    st.info("This model is exploratory. It is not financial advice or a forecast of official reserve shares.")

rows = run_simulation(years=horizon, start_year=int(start_year), seed=int(seed))
df = pd.DataFrame(rows)

left, right = st.columns([2, 1])

with left:
    fig = px.line(
        df,
        x="year",
        y="share_pct",
        color="agent",
        markers=True,
        labels={"share_pct": "Modeled network share (%)", "year": "Year", "agent": "Network"},
        title="Modeled monetary-network share through time",
    )
    fig.update_layout(legend_title_text="Network")
    st.plotly_chart(fig, use_container_width=True)

with right:
    st.subheader("Final modeled state")
    summary = pd.DataFrame(summarize_final_state(rows))
    st.dataframe(summary, use_container_width=True, hide_index=True)

st.subheader("Scenario shock timeline")
shock_rows = df[df["event"] != "No discrete shock"][["year", "event"]].drop_duplicates()
shock_rows = shock_rows[shock_rows["event"] != "Baseline"]
st.dataframe(shock_rows, use_container_width=True, hide_index=True)

st.subheader("Full simulation data")
st.dataframe(df, use_container_width=True, hide_index=True)

csv = df.to_csv(index=False).encode("utf-8")
st.download_button("Download results as CSV", csv, "monetary_network_simulation.csv", "text/csv")

with st.expander("How the model works"):
    st.markdown(
        """
Each modeled network begins with a baseline share, structural growth rate, resilience score, and volatility level.\n\nEach year, the engine combines structural growth, residual effects from prior shocks, any new shock effects, and seeded stochastic variation. The resulting relative weights are normalized back to 100%.\n\nThe included baseline scenario contains five shocks: a BRICS gold-linked settlement unit, partial oil de-dollarization, a U.S. debt-confidence crisis, a payments-infrastructure cyberattack, and rapid digital-currency adoption.
        """
    )
