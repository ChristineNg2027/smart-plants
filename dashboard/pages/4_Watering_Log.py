import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import os

BACKEND = os.getenv("BACKEND_URL", "http://localhost:8000")

st.set_page_config(page_title="Watering Log", page_icon="💧", layout="wide")
st.title("💧 Watering Log")


def fetch_pump_events() -> pd.DataFrame:
    try:
        resp = requests.get(f"{BACKEND}/pump?limit=200", timeout=5)
        resp.raise_for_status()
        df = pd.DataFrame(resp.json())
        if not df.empty:
            df["created_at"] = pd.to_datetime(df["created_at"])
        return df
    except Exception as e:
        st.error(f"Could not reach backend: {e}")
        return pd.DataFrame()


if st.button("Refresh"):
    st.rerun()

df = fetch_pump_events()

if df.empty:
    st.info("No watering events recorded yet.")
else:
    col1, col2, col3 = st.columns(3)
    col1.metric("Total events", len(df))
    col2.metric("Total water time", f"{df['duration_ms'].sum() / 1000:.0f}s")
    col3.metric("Last watering", df["created_at"].max().strftime("%Y-%m-%d %H:%M"))

    fig = px.bar(
        df, x="created_at", y="duration_ms", color="triggered_by",
        title="Pump Events Over Time",
        labels={"created_at": "Time", "duration_ms": "Duration (ms)", "triggered_by": "Trigger"},
        color_discrete_map={"manual": "#3498db", "model": "#2ecc71", "emergency": "#e74c3c"},
    )
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Event Table")
    st.dataframe(
        df[["id", "created_at", "duration_ms", "triggered_by"]]
        .sort_values("created_at", ascending=False)
        .reset_index(drop=True)
    )
