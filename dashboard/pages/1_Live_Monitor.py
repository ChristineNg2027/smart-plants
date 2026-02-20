import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import requests
import time
import os

BACKEND = os.getenv("BACKEND_URL", "http://localhost:8000")
DRY_THRESHOLD = 30.0

st.set_page_config(page_title="Live Monitor", page_icon="📡", layout="wide")
st.title("📡 Live Monitor")

auto_refresh = st.sidebar.toggle("Auto-refresh (10s)", value=False)
limit = st.sidebar.slider("Readings to show", 20, 500, 100)


def fetch_readings(n: int) -> pd.DataFrame:
    try:
        resp = requests.get(f"{BACKEND}/readings?limit={n}", timeout=5)
        resp.raise_for_status()
        df = pd.DataFrame(resp.json())
        df["created_at"] = pd.to_datetime(df["created_at"])
        return df.sort_values("created_at")
    except Exception as e:
        st.error(f"Could not reach backend: {e}")
        return pd.DataFrame()


placeholder = st.empty()

while True:
    df = fetch_readings(limit)

    with placeholder.container():
        if df.empty:
            st.warning("No data yet. Is the backend running and receiving readings?")
        else:
            latest = df.iloc[-1]
            col1, col2, col3 = st.columns(3)
            col1.metric("Moisture", f"{latest['moisture']:.1f}%",
                        delta=f"{latest['moisture'] - df.iloc[-2]['moisture']:+.1f}%" if len(df) > 1 else None)
            col2.metric("Temperature", f"{latest['temperature']:.1f}°C")
            col3.metric("Humidity", f"{latest['humidity']:.1f}%")

            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=df["created_at"], y=df["moisture"],
                name="Moisture (%)", line=dict(color="#2ecc71", width=2),
            ))
            fig.add_hline(y=DRY_THRESHOLD, line_dash="dash", line_color="red",
                          annotation_text="Dry threshold")
            fig.update_layout(
                title="Soil Moisture Over Time",
                xaxis_title="Time", yaxis_title="Moisture (%)",
                yaxis=dict(range=[0, 100]),
                height=350, margin=dict(t=40, b=20),
            )
            st.plotly_chart(fig, use_container_width=True)

            fig2 = go.Figure()
            fig2.add_trace(go.Scatter(x=df["created_at"], y=df["temperature"],
                                      name="Temp (°C)", line=dict(color="#e67e22")))
            fig2.add_trace(go.Scatter(x=df["created_at"], y=df["humidity"],
                                      name="Humidity (%)", line=dict(color="#3498db")))
            fig2.update_layout(title="Temperature & Humidity", height=280,
                                margin=dict(t=40, b=20))
            st.plotly_chart(fig2, use_container_width=True)

    if not auto_refresh:
        break
    time.sleep(10)
    st.rerun()
