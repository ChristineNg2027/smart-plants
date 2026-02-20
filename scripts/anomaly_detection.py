"""
Anomaly detection using LSTM reconstruction error.

Strategy: train on normal data, flag windows where prediction error
exceeds a learned threshold (mean + k*std of training errors).

Usage:
  python anomaly_detection.py [--k 3.0]
"""

import argparse
import numpy as np
import torch
import pickle
from pathlib import Path
from model import load_model
from data_processing import FEATURES, TARGET, SEQ_LEN

PROCESSED_DIR = Path("../data/processed")
MODELS_DIR    = Path("../data/models")


def compute_errors(model, X: np.ndarray) -> np.ndarray:
    """Return per-sequence absolute prediction error on the target feature."""
    target_idx = FEATURES.index(TARGET)
    model.eval()
    errors = []
    with torch.no_grad():
        for i in range(len(X)):
            x = torch.tensor(X[i][np.newaxis], dtype=torch.float32)
            pred = model(x).item()
            actual = X[i, -1, target_idx]  # last known value as proxy
            errors.append(abs(pred - actual))
    return np.array(errors)


def detect(k: float = 3.0):
    model = load_model(str(MODELS_DIR / "best_model.pt"))

    X_train = np.load(PROCESSED_DIR / "X_train.npy")
    X_val   = np.load(PROCESSED_DIR / "X_val.npy")

    train_errors = compute_errors(model, X_train)
    threshold = train_errors.mean() + k * train_errors.std()
    print(f"Anomaly threshold (k={k}): {threshold:.4f}")

    val_errors = compute_errors(model, X_val)
    anomaly_indices = np.where(val_errors > threshold)[0]

    print(f"Anomalies in validation set: {len(anomaly_indices)} / {len(X_val)}")
    for idx in anomaly_indices[:20]:
        print(f"  Index {idx:4d} — error={val_errors[idx]:.4f}")

    np.save(PROCESSED_DIR / "val_errors.npy", val_errors)
    np.save(PROCESSED_DIR / "anomaly_threshold.npy", np.array([threshold]))
    print("Saved val_errors.npy and anomaly_threshold.npy")

    return anomaly_indices, threshold


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--k", type=float, default=3.0,
                        help="Number of std deviations above mean to set threshold")
    args = parser.parse_args()
    detect(k=args.k)
