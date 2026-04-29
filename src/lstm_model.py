"""
TriNetra AI — LSTM Temporal Model
2-layer PyTorch LSTM trained on per-user transaction sequences.
Detects sudden spikes, abnormal return patterns, night-burst behavior.
Output: temporal_risk_score (0–100) per user.
"""

import sys
from pathlib import Path
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from sklearn.model_selection import train_test_split
import joblib

ROOT = Path(__file__).parent.parent
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
SEQ_LEN = 30
HIDDEN = 128
BATCH  = 256
EPOCHS = 15
LR     = 1e-3


# ─────────────────────────────────────────────────────────────────────────────
# Sequence Builder
# ─────────────────────────────────────────────────────────────────────────────

def build_sequences(df_fraud: pd.DataFrame, df_merged: pd.DataFrame):
    """
    Build fixed-length transaction sequences per user.
    Features per timestep: [amount_norm, hour_norm, day_of_week_norm]
    """
    df = df_fraud.copy()
    df.columns = [c.lower().strip().replace(" ", "_") for c in df.columns]
    for c in ["customerid", "customer_id", "userid"]:
        if c in df.columns and "user_id" not in df.columns:
            df = df.rename(columns={c: "user_id"})

    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
        df["hour"]  = df["timestamp"].dt.hour.fillna(12).astype(int)
        df["dow"]   = df["timestamp"].dt.dayofweek.fillna(0).astype(int)
    else:
        df["hour"] = 12
        df["dow"]  = 0

    amt_max = df["transaction_amount"].max() + 1e-6 if "transaction_amount" in df.columns else 1.0

    sequences, labels, user_ids = [], [], []
    fraud_map = dict(zip(df_merged["user_id"].astype(int),
                         df_merged["fraud_label"].astype(int)))

    for uid, grp in df.groupby("user_id"):
        grp = grp.sort_values("timestamp") if "timestamp" in grp.columns else grp
        amounts = (grp["transaction_amount"].values / amt_max
                   if "transaction_amount" in grp.columns else np.zeros(len(grp)))
        hours   = grp["hour"].values / 23.0
        dows    = grp["dow"].values  / 6.0

        # Pad or truncate to SEQ_LEN
        feats = np.stack([amounts, hours, dows], axis=1)  # (T, 3)
        if len(feats) >= SEQ_LEN:
            feats = feats[-SEQ_LEN:]
        else:
            pad = np.zeros((SEQ_LEN - len(feats), 3))
            feats = np.vstack([pad, feats])

        sequences.append(feats)
        labels.append(fraud_map.get(int(uid), 0))
        user_ids.append(int(uid))

    return (np.array(sequences, dtype=np.float32),
            np.array(labels, dtype=np.float32),
            user_ids)


# ─────────────────────────────────────────────────────────────────────────────
# Dataset & Model
# ─────────────────────────────────────────────────────────────────────────────

class SeqDataset(Dataset):
    def __init__(self, X, y):
        self.X = torch.tensor(X)
        self.y = torch.tensor(y)

    def __len__(self):  return len(self.X)
    def __getitem__(self, i): return self.X[i], self.y[i]


class LSTMFraud(nn.Module):
    def __init__(self, input_size=3, hidden=HIDDEN, layers=2, dropout=0.3):
        super().__init__()
        self.lstm = nn.LSTM(input_size, hidden, layers,
                            batch_first=True, dropout=dropout)
        self.head = nn.Sequential(
            nn.Linear(hidden, 64),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(64, 1),
            nn.Sigmoid(),
        )

    def forward(self, x):
        out, _ = self.lstm(x)
        return self.head(out[:, -1, :]).squeeze(1)


# ─────────────────────────────────────────────────────────────────────────────
# Training
# ─────────────────────────────────────────────────────────────────────────────

def train_lstm(X, y, models_dir: Path) -> LSTMFraud:
    X_tr, X_val, y_tr, y_val = train_test_split(X, y, test_size=0.15,
                                                  random_state=42, stratify=(y > 0.5).astype(int))
    tr_loader  = DataLoader(SeqDataset(X_tr, y_tr),  batch_size=BATCH, shuffle=True)
    val_loader = DataLoader(SeqDataset(X_val, y_val), batch_size=BATCH)

    model = LSTMFraud().to(DEVICE)
    pos_weight = torch.tensor([(y == 0).sum() / max((y == 1).sum(), 1)]).to(DEVICE)
    criterion  = nn.BCEWithLogitsLoss(pos_weight=pos_weight)
    optimizer  = torch.optim.Adam(model.parameters(), lr=LR)
    scheduler  = torch.optim.lr_scheduler.ReduceLROnPlateau(optimizer, patience=2)

    # Re-use sigmoid output, use BCE instead for training
    criterion = nn.BCELoss()

    best_val = float("inf")
    for epoch in range(1, EPOCHS + 1):
        model.train()
        tr_loss = 0
        for xb, yb in tr_loader:
            xb, yb = xb.to(DEVICE), yb.to(DEVICE)
            pred = model(xb)
            loss = criterion(pred, yb)
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            tr_loss += loss.item()

        model.eval()
        val_loss = 0
        with torch.no_grad():
            for xb, yb in val_loader:
                xb, yb = xb.to(DEVICE), yb.to(DEVICE)
                val_loss += criterion(model(xb), yb).item()

        tr_loss  /= max(len(tr_loader), 1)
        val_loss /= max(len(val_loader), 1)
        scheduler.step(val_loss)

        if epoch % 3 == 0 or epoch == 1:
            print(f"  Epoch {epoch:02d}/{EPOCHS} | train={tr_loss:.4f} | val={val_loss:.4f}")

        if val_loss < best_val:
            best_val = val_loss
            torch.save(model.state_dict(), models_dir / "lstm_best.pt")

    model.load_state_dict(torch.load(models_dir / "lstm_best.pt", map_location=DEVICE))
    return model


# ─────────────────────────────────────────────────────────────────────────────
# Inference
# ─────────────────────────────────────────────────────────────────────────────

def predict_lstm(model: LSTMFraud, X: np.ndarray) -> np.ndarray:
    model.eval()
    all_preds = []
    loader = DataLoader(torch.tensor(X), batch_size=512)
    with torch.no_grad():
        for xb in loader:
            all_preds.append(model(xb.to(DEVICE)).cpu().numpy())
    return np.concatenate(all_preds)


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────

def run_lstm_model(df_fraud: pd.DataFrame, df_merged: pd.DataFrame,
                   models_dir: Path) -> pd.Series:
    print("\n[LSTM] Building sequences...")
    X, y, user_ids = build_sequences(df_fraud, df_merged)
    print(f"[LSTM] Sequences: {X.shape}, fraud rate: {y.mean():.2%}")

    print("[LSTM] Training...")
    model = train_lstm(X, y, models_dir)

    print("[LSTM] Predicting risk scores...")
    probs = predict_lstm(model, X)
    scores = (probs * 100).clip(0, 100)

    result = pd.Series(dict(zip(user_ids, scores)), name="temporal_risk_score")
    joblib.dump(user_ids, models_dir / "lstm_user_ids.pkl")
    print(f"[LSTM] Done. Mean={result.mean():.1f}, Max={result.max():.1f}")
    return result
