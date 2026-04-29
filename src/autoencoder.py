"""
TriNetra AI — Autoencoder Anomaly Detection
Trained ONLY on normal (non-fraud) users.
Reconstruction error on fraud users is high → anomaly_score.
"""

import sys
from pathlib import Path
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset
import joblib

ROOT = Path(__file__).parent.parent
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
EPOCHS = 20
BATCH  = 256
LR     = 1e-3


# ─────────────────────────────────────────────────────────────────────────────
# Model
# ─────────────────────────────────────────────────────────────────────────────

class Autoencoder(nn.Module):
    def __init__(self, input_dim: int):
        super().__init__()
        self.encoder = nn.Sequential(
            nn.Linear(input_dim, 64),
            nn.ReLU(),
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Linear(32, 16),
            nn.ReLU(),
        )
        self.decoder = nn.Sequential(
            nn.Linear(16, 32),
            nn.ReLU(),
            nn.Linear(32, 64),
            nn.ReLU(),
            nn.Linear(64, input_dim),
        )

    def forward(self, x):
        return self.decoder(self.encoder(x))


# ─────────────────────────────────────────────────────────────────────────────
# Training
# ─────────────────────────────────────────────────────────────────────────────

def train_autoencoder(X_normal: np.ndarray, models_dir: Path) -> Autoencoder:
    input_dim = X_normal.shape[1]
    tensor    = torch.tensor(X_normal, dtype=torch.float32)
    loader    = DataLoader(TensorDataset(tensor), batch_size=BATCH, shuffle=True)

    model     = Autoencoder(input_dim).to(DEVICE)
    criterion = nn.MSELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=LR)
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(optimizer, patience=3)

    best_loss = float("inf")
    for epoch in range(1, EPOCHS + 1):
        model.train()
        total_loss = 0
        for (xb,) in loader:
            xb = xb.to(DEVICE)
            recon = model(xb)
            loss = criterion(recon, xb)
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            total_loss += loss.item()

        avg_loss = total_loss / max(len(loader), 1)
        scheduler.step(avg_loss)

        if epoch % 4 == 0 or epoch == 1:
            print(f"  Epoch {epoch:02d}/{EPOCHS} | loss={avg_loss:.6f}")

        if avg_loss < best_loss:
            best_loss = avg_loss
            torch.save(model.state_dict(), models_dir / "autoencoder_best.pt")

    model.load_state_dict(torch.load(models_dir / "autoencoder_best.pt", map_location=DEVICE))
    return model


# ─────────────────────────────────────────────────────────────────────────────
# Reconstruction Error → Score
# ─────────────────────────────────────────────────────────────────────────────

def compute_anomaly_scores(model: Autoencoder, X_all: np.ndarray,
                           X_normal: np.ndarray) -> np.ndarray:
    """
    Compute per-user reconstruction error, normalized against normal distribution.
    Returns anomaly_score in [0, 100].
    """
    model.eval()

    def recon_errors(X):
        t = torch.tensor(X, dtype=torch.float32).to(DEVICE)
        with torch.no_grad():
            recon = model(t)
        return ((recon - t) ** 2).mean(dim=1).cpu().numpy()

    all_errors    = recon_errors(X_all)
    normal_errors = recon_errors(X_normal)

    # Normalise: use normal user error distribution as baseline
    mu  = normal_errors.mean()
    sig = normal_errors.std() + 1e-6

    z_scores   = (all_errors - mu) / sig
    # Clip to [0, 4] sigma range then map to [0, 100]
    normalized = np.clip(z_scores, 0, 4) / 4.0 * 100
    return normalized.clip(0, 100)


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────

def run_autoencoder(df_merged: pd.DataFrame, feat_cols: list,
                    models_dir: Path) -> pd.Series:
    print("\n[Autoencoder] Preparing data...")
    X_all = df_merged[feat_cols].values.astype(np.float32)

    normal_mask = df_merged["fraud_label"] == 0
    X_normal    = X_all[normal_mask]

    print(f"[Autoencoder] Training on {X_normal.shape[0]:,} normal users "
          f"({X_normal.shape[1]} features)...")
    model = train_autoencoder(X_normal, models_dir)

    print("[Autoencoder] Computing anomaly scores for all users...")
    scores = compute_anomaly_scores(model, X_all, X_normal)

    # Save threshold info for inference
    joblib.dump({"model_dim": X_all.shape[1]}, models_dir / "autoencoder_meta.pkl")

    result = pd.Series(scores, index=df_merged["user_id"].values,
                       name="anomaly_score")
    print(f"[Autoencoder] Done. Mean={result.mean():.1f}, Max={result.max():.1f}")
    return result
