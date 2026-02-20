import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
from pathlib import Path

st.set_page_config(page_title="Anomalies", page_icon="⚠️", layout="wide")
st.title("⚠️ Anomaly Detection")

PROCESSED_DIR = Path("../../data/processed")

errors_path    = PROCESSED_DIR / "val_errors.npy"
threshold_path = PROCESSED_DIR / "anomaly_threshold.npy"

if not errors_path.exists():
    st.info(
        "No anomaly data yet. Run `python scripts/anomaly_detection.py` to compute errors.\n\n"
        "This requires a trained model and processed validation data."
    )
else:
    errors    = np.load(errors_path)
    threshold = float(np.load(threshold_path)[0])

    anomaly_mask = errors > threshold
    n_anomalies  = anomaly_mask.sum()

    col1, col2, col3 = st.columns(3)
    col1.metric("Total windows", len(errors))
    col2.metric("Anomalies detected", int(n_anomalies))
    col3.metric("Threshold", f"{threshold:.4f}")

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        y=errors, mode="lines", name="Reconstruction error",
        line=dict(color="#3498db", width=1),
    ))
    fig.add_hline(y=threshold, line_dash="dash", line_color="red",
                  annotation_text="Anomaly threshold")
    anomaly_idx = np.where(anomaly_mask)[0]
    fig.add_trace(go.Scatter(
        x=anomaly_idx, y=errors[anomaly_idx], mode="markers",
        name="Anomaly", marker=dict(color="red", size=6, symbol="x"),
    ))
    fig.update_layout(
        title="LSTM Reconstruction Error (Validation Set)",
        xaxis_title="Window index", yaxis_title="Absolute error",
        height=400,
    )
    st.plotly_chart(fig, use_container_width=True)

    if n_anomalies > 0:
        df = pd.DataFrame({"window_index": anomaly_idx, "error": errors[anomaly_idx]})
        st.dataframe(df.sort_values("error", ascending=False).reset_index(drop=True))
