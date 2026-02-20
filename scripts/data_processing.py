"""
Load raw sensor CSVs, clean, normalize, and produce sliding-window sequences
for LSTM training.

Expected CSV schema (from backend export or direct ESP32 logs):
  timestamp, moisture, temperature, humidity, light
"""

import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.preprocessing import MinMaxScaler
import pickle

RAW_DIR = Path("../data/raw")
PROCESSED_DIR = Path("../data/processed")
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

FEATURES = ["moisture", "temperature", "humidity", "light"]
TARGET = "moisture"
SEQ_LEN = 24       # hours of history fed to LSTM
HORIZON = 6        # hours ahead to predict
TRAIN_SPLIT = 0.8


def load_raw() -> pd.DataFrame:
    files = sorted(RAW_DIR.glob("*.csv"))
    if not files:
        raise FileNotFoundError(f"No CSV files found in {RAW_DIR}")
    df = pd.concat([pd.read_csv(f) for f in files], ignore_index=True)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df = df.sort_values("timestamp").drop_duplicates("timestamp").set_index("timestamp")
    return df


def clean(df: pd.DataFrame) -> pd.DataFrame:
    df = df.resample("1h").mean()
    df = df.interpolate(method="time", limit=6)
    df = df.dropna()
    df = df.clip(lower=0)
    df["moisture"] = df["moisture"].clip(upper=100)
    df["humidity"] = df["humidity"].clip(upper=100)
    return df


def make_sequences(
    values: np.ndarray,
    seq_len: int = SEQ_LEN,
    horizon: int = HORIZON,
) -> tuple[np.ndarray, np.ndarray]:
    X, y = [], []
    target_col = FEATURES.index(TARGET)
    for i in range(len(values) - seq_len - horizon + 1):
        X.append(values[i : i + seq_len])
        y.append(values[i + seq_len + horizon - 1, target_col])
    return np.array(X, dtype=np.float32), np.array(y, dtype=np.float32)


def process():
    df = load_raw()
    df = clean(df)

    scaler = MinMaxScaler()
    scaled = scaler.fit_transform(df[FEATURES])

    X, y = make_sequences(scaled)
    split = int(len(X) * TRAIN_SPLIT)

    np.save(PROCESSED_DIR / "X_train.npy", X[:split])
    np.save(PROCESSED_DIR / "y_train.npy", y[:split])
    np.save(PROCESSED_DIR / "X_val.npy", X[split:])
    np.save(PROCESSED_DIR / "y_val.npy", y[split:])

    with open(PROCESSED_DIR / "scaler.pkl", "wb") as f:
        pickle.dump(scaler, f)

    print(f"Processed {len(df)} hourly readings -> {len(X)} sequences")
    print(f"Train: {split}  Val: {len(X) - split}")
    return scaler


if __name__ == "__main__":
    process()
