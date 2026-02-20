import streamlit as st
import plotly.graph_objects as go
import requests
import os

BACKEND = os.getenv("BACKEND_URL", "http://localhost:8000")

st.set_page_config(page_title="Forecast", page_icon="🔮", layout="wide")
st.title("🔮 Moisture Forecast")


def fetch_prediction() -> dict | None:
    try:
        resp = requests.get(f"{BACKEND}/predictions/latest", timeout=5)
        if resp.status_code == 404:
            return None
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        st.error(f"Could not reach backend: {e}")
        return None


if st.button("Refresh Forecast"):
    st.rerun()

pred = fetch_prediction()

if pred is None:
    st.info("No forecast available yet. Run `python scripts/predict.py --post` to generate one.")
else:
    horizon = pred["horizon_hours"]
    forecast = pred["forecast"]
    threshold = pred["dry_threshold"]
    dry_at = pred.get("predicted_dry_at_hours")

    hours = list(range(1, horizon + 1))

    col1, col2 = st.columns(2)
    col1.metric("Forecast horizon", f"{horizon} hours")
    if dry_at:
        col2.metric("Predicted dry in", f"{dry_at:.0f}h", delta="Needs water soon", delta_color="inverse")
    else:
        col2.metric("Plant status", "OK within window", delta="No watering needed", delta_color="normal")

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=hours, y=forecast, mode="lines+markers",
        name="Predicted moisture", line=dict(color="#2ecc71", width=2),
        marker=dict(size=8),
    ))
    fig.add_hline(y=threshold, line_dash="dash", line_color="red",
                  annotation_text=f"Dry threshold ({threshold}%)")
    if dry_at:
        fig.add_vline(x=dry_at, line_dash="dot", line_color="orange",
                      annotation_text=f"Dry at h={dry_at:.0f}")

    fig.update_layout(
        title=f"LSTM Moisture Forecast — Next {horizon} Hours",
        xaxis_title="Hours from now",
        yaxis_title="Predicted Moisture (%)",
        yaxis=dict(range=[0, 100]),
        height=400,
    )
    st.plotly_chart(fig, use_container_width=True)
