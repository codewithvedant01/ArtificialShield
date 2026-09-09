from pathlib import Path
import sys

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.audit import fetch_events, init_db
from config import settings

st.set_page_config(page_title="ArtificialShield Analytics", layout="wide")
st.title("ArtificialShield — Guardrail Analytics")
st.caption(f"Model: {settings.model_name} | Threshold: {settings.threshold}")

init_db()
events = fetch_events()

if not events:
    st.info("No blocked or flagged events logged yet.")
    st.stop()

df = pd.DataFrame(events)
df["timestamp"] = pd.to_datetime(df["timestamp"])

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Events", len(df))
col2.metric("Blocked", int((df["decision"] == "blocked").sum()))
col3.metric("Flagged", int((df["decision"] == "flagged").sum()))
col4.metric("Avg Latency (ms)", round(df["latency_ms"].mean(), 2))

st.subheader("Block Rate Over Time")
trend = df.set_index("timestamp").resample("1h").size().rename("events")
st.line_chart(trend)

st.subheader("Score Distribution")
st.bar_chart(df["max_score"])

st.subheader("Recent Payloads")
st.dataframe(
    df[["timestamp", "endpoint", "decision", "max_score", "latency_ms", "payload"]],
    use_container_width=True,
)
