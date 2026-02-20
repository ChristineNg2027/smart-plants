"""
Run the trained LSTM to forecast future moisture and POST result to backend.

Usage:
  python predict.py [--horizon 6] [--post]
"""

import argparse
import numpy as np
import torch
import pickle
import json
import requests
from pathlib import Path
from model import load_model
from data_processing import FEATURES, TARGET, SEQ_LEN

PROCESSED_DIR = Path("../data/processed")
MODELS_DIR    = Path("../data/models")
BACKEND_URL   = "http://localhost:8000"
DRY_THRESHOLD = 0.30  # normalized — corresponds to 30% moisture


def get_latest_window() -> np.ndarray:
    """Load the most recent SEQ_LEN rows from processed data as model input."""
    X_val = np.load(PROCESSED_DIR / "X_val.npy")
    return X_val[-1]  # shape: (SEQ_LEN, n_features)


def predict(horizon: int = 6, post_to_backend: bool = False):
    model = load_model(str(MODELS_DIR / "best_model.pt"))

    with open(PROCESSED_DIR / "scaler.pkl", "rb") as f:
        scaler = pickle.load(f)

    window = get_latest_window()  # (SEQ_LEN, n_features)
    forecast = []

    for _ in range(horizon):
        x = torch.tensor(window[np.newaxis], dtype=torch.float32)  # (1, SEQ_LEN, n_features)
        with torch.no_grad():
            pred_normalized = model(x).item()

        # Denormalize moisture only
        target_idx = FEATURES.index(TARGET)
        dummy = np.zeros((1, len(FEATURES)))
        dummy[0, target_idx] = pred_normalized
        moisture_pct = scaler.inverse_transform(dummy)[0, target_idx]
        forecast.append(round(float(moisture_pct), 2))

        # Roll window forward: append predicted step
        new_row = window[-1].copy()
        new_row[target_idx] = pred_normalized
        window = np.vstack([window[1:], new_row])

    predicted_dry_at = None
    for i, m in enumerate(forecast):
        if m < DRY_THRESHOLD * 100:
            predicted_dry_at = float(i + 1)
            break

    print(f"Forecast ({horizon}h): {forecast}")
    print(f"Predicted dry at: {predicted_dry_at} hours" if predicted_dry_at else "Plant stays OK within forecast window")

    if post_to_backend:
        payload = {
            "forecast": forecast,
            "horizon_hours": horizon,
            "dry_threshold": DRY_THRESHOLD * 100,
            "predicted_dry_at_hours": predicted_dry_at,
        }
        # Store via internal DB endpoint (direct insert — extend backend if needed)
        print(f"[POST] Would send to {BACKEND_URL}/predictions (extend backend to accept this)")

    return forecast, predicted_dry_at


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--horizon", type=int, default=6)
    parser.add_argument("--post", action="store_true", help="Post forecast to backend")
    args = parser.parse_args()
    predict(horizon=args.horizon, post_to_backend=args.post)
