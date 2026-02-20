"""
Train the MoistureLSTM on processed data.

Usage:
  python train.py [--epochs 50] [--lr 0.001] [--batch 32]
"""

import argparse
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset
from pathlib import Path
from model import MoistureLSTM

PROCESSED_DIR = Path("../data/processed")
MODELS_DIR = Path("../data/models")
MODELS_DIR.mkdir(parents=True, exist_ok=True)


def load_data(device: torch.device):
    X_train = torch.tensor(np.load(PROCESSED_DIR / "X_train.npy")).to(device)
    y_train = torch.tensor(np.load(PROCESSED_DIR / "y_train.npy")).to(device)
    X_val   = torch.tensor(np.load(PROCESSED_DIR / "X_val.npy")).to(device)
    y_val   = torch.tensor(np.load(PROCESSED_DIR / "y_val.npy")).to(device)
    return (
        DataLoader(TensorDataset(X_train, y_train), batch_size=32, shuffle=True),
        DataLoader(TensorDataset(X_val, y_val),   batch_size=64),
    )


def train(epochs: int = 50, lr: float = 1e-3, batch_size: int = 32):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Training on {device}")

    train_loader, val_loader = load_data(device)

    model = MoistureLSTM().to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(optimizer, patience=5, factor=0.5)
    criterion = nn.MSELoss()

    best_val_loss = float("inf")

    for epoch in range(1, epochs + 1):
        model.train()
        train_loss = 0.0
        for X_batch, y_batch in train_loader:
            optimizer.zero_grad()
            pred = model(X_batch)
            loss = criterion(pred, y_batch)
            loss.backward()
            nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()
            train_loss += loss.item() * len(X_batch)
        train_loss /= len(train_loader.dataset)

        model.eval()
        val_loss = 0.0
        with torch.no_grad():
            for X_batch, y_batch in val_loader:
                pred = model(X_batch)
                val_loss += criterion(pred, y_batch).item() * len(X_batch)
        val_loss /= len(val_loader.dataset)

        scheduler.step(val_loss)

        print(f"Epoch {epoch:03d}/{epochs}  train={train_loss:.5f}  val={val_loss:.5f}")

        if val_loss < best_val_loss:
            best_val_loss = val_loss
            torch.save(model.state_dict(), MODELS_DIR / "best_model.pt")
            print(f"  -> Saved best model (val={val_loss:.5f})")

    print(f"\nTraining complete. Best val loss: {best_val_loss:.5f}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--epochs", type=int, default=50)
    parser.add_argument("--lr", type=float, default=1e-3)
    parser.add_argument("--batch", type=int, default=32)
    args = parser.parse_args()
    train(epochs=args.epochs, lr=args.lr, batch_size=args.batch)
