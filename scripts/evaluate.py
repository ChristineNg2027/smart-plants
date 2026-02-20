"""
Evaluate LSTM performance: MAE, RMSE, and prediction vs actual plots.

Usage:
  python evaluate.py
"""

import numpy as np
import torch
import pickle
import matplotlib.pyplot as plt
from pathlib import Path
from sklearn.metrics import mean_absolute_error, mean_squared_error
from model import load_model
from data_processing import FEATURES, TARGET

PROCESSED_DIR = Path("../data/processed")
MODELS_DIR    = Path("../data/models")


def evaluate():
    model = load_model(str(MODELS_DIR / "best_model.pt"))

    X_val = np.load(PROCESSED_DIR / "X_val.npy")
    y_val = np.load(PROCESSED_DIR / "y_val.npy")

    with open(PROCESSED_DIR / "scaler.pkl", "rb") as f:
        scaler = pickle.load(f)

    model.eval()
    with torch.no_grad():
        preds_norm = model(torch.tensor(X_val, dtype=torch.float32)).numpy()

    # Denormalize
    target_idx = FEATURES.index(TARGET)
    n = len(preds_norm)
    dummy_pred = np.zeros((n, len(FEATURES)))
    dummy_true = np.zeros((n, len(FEATURES)))
    dummy_pred[:, target_idx] = preds_norm
    dummy_true[:, target_idx] = y_val

    preds = scaler.inverse_transform(dummy_pred)[:, target_idx]
    trues = scaler.inverse_transform(dummy_true)[:, target_idx]

    mae  = mean_absolute_error(trues, preds)
    rmse = mean_squared_error(trues, preds) ** 0.5

    print(f"MAE:  {mae:.2f}%")
    print(f"RMSE: {rmse:.2f}%")

    # Plot
    plt.figure(figsize=(14, 4))
    plt.plot(trues[:200], label="Actual moisture", alpha=0.8)
    plt.plot(preds[:200], label="Predicted moisture", alpha=0.8)
    plt.axhline(30, color="red", linestyle="--", label="Dry threshold (30%)")
    plt.xlabel("Time step (hours)")
    plt.ylabel("Soil moisture (%)")
    plt.title(f"LSTM Forecast  |  MAE={mae:.2f}%  RMSE={rmse:.2f}%")
    plt.legend()
    plt.tight_layout()
    plt.savefig(MODELS_DIR / "evaluation.png", dpi=150)
    plt.show()
    print(f"Plot saved to {MODELS_DIR / 'evaluation.png'}")


if __name__ == "__main__":
    evaluate()
