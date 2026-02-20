"""
Smart Plants Dashboard — entry point.
Run with: streamlit run app.py
"""

import streamlit as st

st.set_page_config(
    page_title="Smart Plants",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("🌱 Smart Plants")
st.markdown(
    """
    Welcome to the Smart Plants monitoring dashboard.

    Use the sidebar to navigate between views:

    | Page | What it shows |
    |------|--------------|
    | **Live Monitor** | Real-time soil moisture, temperature, humidity |
    | **Forecast** | LSTM moisture predictions for the next 6 hours |
    | **Anomalies** | Detected sensor or drying anomalies |
    | **Watering Log** | History of all pump events |
    """
)

st.info("Select a page from the sidebar to get started.")
