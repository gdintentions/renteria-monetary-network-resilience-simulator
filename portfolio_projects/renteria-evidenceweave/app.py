from __future__ import annotations

import math
import sys
from pathlib import Path

import plotly.graph_objects as go
import streamlit as st

sys.path.insert(0, str(Path(__file__).parent / "src"))

from evidenceweave.demo_data import build_demo

st.set_page_config(page_title="Renteria EvidenceWeave", page_icon="🕸️", layout="wide")
st.title("Renteria EvidenceWeave")
st.caption("Conflict-aware multimodal evidence intelligence · recruiter-safe demonstration")

weave = build_demo()
metrics = weave.dashboard_metrics()
columns = st.columns(5)
for column, (label, value) in zip(columns, metrics.items(), strict=True):
    column.metric(label.replace("_", " ").title(), value)

query = st.text_input(
    "Ask the evidence graph",
    "Which embedding model was selected, and what accuracy evidence supports it?",
)
answer = weave.query(query)

left, right = st.columns([1.35, 1])
with left:
    st.subheader("Audited answer")
    st.write(answer.summary)
    st.progress(answer.score.integrity, text=f"Evidence Integrity Score: {answer.score.integrity:.1%}")
    if answer.conflicts:
        st.warning("\n".join(f"Conflict: {item}" for item in answer.conflicts))
    st.subheader("Cited evidence")
    for block in answer.evidence:
        source = weave.sources[block.source_id]
        with st.expander(f"{source.title} · {block.modality.value} · page {block.page or 'n/a'}"):
            st.write(block.content)
            st.caption(f"Extraction confidence {block.confidence:.0%} · source authority {source.authority:.0%}")

with right:
    st.subheader("Score anatomy")
    score = answer.score
    labels = ["Semantic", "Graph", "Cross-modal", "Reliability", "Freshness", "Conflict", "Ambiguity"]
    values = [score.semantic, score.graph_support, score.cross_modal, score.source_reliability,
              score.freshness, score.contradiction, score.ambiguity]
    colors = ["#6366f1"] * 5 + ["#ef4444", "#f59e0b"]
    fig = go.Figure(go.Bar(x=values, y=labels, orientation="h", marker_color=colors))
    fig.update_layout(height=360, margin={"l": 10, "r": 10, "t": 10, "b": 10}, xaxis_range=[0, 1])
    st.plotly_chart(fig, width="stretch")

    st.subheader("Claim graph")
    edges = weave.graph.edges()
    nodes = sorted({node for edge in edges for node in edge[:2]})
    positions = {node: (math.cos(i * 2 * math.pi / len(nodes)), math.sin(i * 2 * math.pi / len(nodes)))
                 for i, node in enumerate(nodes)}
    edge_x, edge_y = [], []
    for source, target, _predicate in edges:
        edge_x += [positions[source][0], positions[target][0], None]
        edge_y += [positions[source][1], positions[target][1], None]
    graph_fig = go.Figure()
    graph_fig.add_trace(
        go.Scatter(
            x=edge_x,
            y=edge_y,
            mode="lines",
            line={"color": "#94a3b8"},
            hoverinfo="skip",
        )
    )
    graph_fig.add_trace(
        go.Scatter(
            x=[positions[node][0] for node in nodes],
            y=[positions[node][1] for node in nodes],
            text=nodes,
            mode="markers+text",
            textposition="top center",
            marker={"size": 18, "color": "#14b8a6"},
            hoverinfo="text",
        )
    )
    graph_fig.update_layout(
        height=400,
        showlegend=False,
        margin={"l": 10, "r": 10, "t": 10, "b": 10},
        xaxis={"visible": False},
        yaxis={"visible": False},
    )
    st.plotly_chart(graph_fig, width="stretch")

st.divider()
st.caption("Synthetic demonstration data only. Evidence scores support review; they do not prove truth.")
