"""
TriNetra AI — Synthetic Data Generator
Generates realistic e-commerce fraud datasets when real CSVs are not available.
Auto-detected by preprocess.py; real CSVs take priority if present.
"""

import numpy as np
import pandas as pd
from pathlib import Path

RNG = np.random.default_rng(42)
N_USERS = 6000
N_TRANSACTIONS = 300_000
N_RETURNS = 10_000


def _fraud_user_ids(n=300):
    """Return a set of user IDs that are marked as fraudulent."""
    return set(RNG.choice(range(1, N_USERS + 1), size=n, replace=False).tolist())


FRAUD_USERS = _fraud_user_ids()


# ─────────────────────────────────────────────────────────────────────────────
# 1. Returns Dataset
# ─────────────────────────────────────────────────────────────────────────────

def generate_returns(out_path: Path) -> pd.DataFrame:
    """Mimics: synthetic-dataset-for-e-commerce-return-analysis"""
    user_ids = RNG.integers(1, N_USERS + 1, size=N_RETURNS)
    is_fraud_user = np.isin(user_ids, list(FRAUD_USERS))

    reasons = ["Damaged", "Wrong Item", "Quality Issue", "Changed Mind", "Wardrobing"]
    reason_probs_normal = [0.25, 0.20, 0.25, 0.20, 0.10]
    reason_probs_fraud  = [0.15, 0.10, 0.10, 0.15, 0.50]

    return_reasons = np.where(
        is_fraud_user,
        RNG.choice(reasons, size=N_RETURNS, p=reason_probs_fraud),
        RNG.choice(reasons, size=N_RETURNS, p=reason_probs_normal),
    )

    days_to_return = np.where(
        is_fraud_user,
        RNG.integers(1, 5, size=N_RETURNS),      # fraud: return very fast
        RNG.integers(3, 30, size=N_RETURNS),      # normal: varies
    )

    return_status = np.where(
        is_fraud_user,
        RNG.choice(["Approved", "Rejected", "Pending"], size=N_RETURNS, p=[0.6, 0.2, 0.2]),
        RNG.choice(["Approved", "Rejected", "Pending"], size=N_RETURNS, p=[0.7, 0.1, 0.2]),
    )

    df = pd.DataFrame({
        "user_id": user_ids,
        "return_reason": return_reasons,
        "days_to_return": days_to_return,
        "return_status": return_status,
        "return_amount": RNG.uniform(100, 5000, size=N_RETURNS).round(2),
    })

    df.to_csv(out_path, index=False)
    print(f"[DataGen] Returns dataset saved → {out_path}  ({len(df):,} rows)")
    return df


# ─────────────────────────────────────────────────────────────────────────────
# 2. Fraud Transactions Dataset
# ─────────────────────────────────────────────────────────────────────────────

def generate_fraud_transactions(out_path: Path) -> pd.DataFrame:
    """Mimics: fraudulent-e-commerce-transactions (1.4M → sampled to 200K)"""
    n = 200_000
    user_ids = RNG.integers(1, N_USERS + 1, size=n)
    is_fraud_user = np.isin(user_ids, list(FRAUD_USERS))

    # Fraud users: high-value, late-night, multiple payment methods
    normal_amounts = RNG.lognormal(mean=7.5, sigma=1.2, size=n).clip(50, 10000)
    fraud_amounts  = RNG.uniform(5000, 50000, size=n)
    amounts = np.where(is_fraud_user, fraud_amounts, normal_amounts).round(2)

    hours = np.where(
        is_fraud_user,
        RNG.choice(np.arange(23), size=n, p=_night_heavy_probs()),
        RNG.integers(6, 23, size=n),
    )

    payment_methods = np.where(
        is_fraud_user,
        RNG.choice(["Credit Card", "UPI", "Wallet", "Net Banking", "Gift Card"],
                   size=n, p=[0.10, 0.10, 0.20, 0.10, 0.50]),
        RNG.choice(["Credit Card", "UPI", "Wallet", "Net Banking", "Gift Card"],
                   size=n, p=[0.30, 0.35, 0.15, 0.15, 0.05]),
    )

    # ~5% fraud rate (matching original dataset stats)
    is_fraud = np.where(is_fraud_user, RNG.random(n) < 0.60, RNG.random(n) < 0.02).astype(int)

    # Timestamps
    base = pd.Timestamp("2023-01-01")
    timestamps = [base + pd.Timedelta(days=int(d), hours=int(h))
                  for d, h in zip(RNG.integers(0, 365, n), hours)]

    device_ids = np.where(
        is_fraud_user,
        RNG.choice([f"DEV_{i:04d}" for i in range(1, 201)], size=n),  # shared devices
        [f"DEV_{i:04d}" for i in RNG.integers(201, 3000, n)],
    )

    ip_addresses = np.where(
        is_fraud_user,
        RNG.choice([f"10.0.{i}.{j}" for i in range(5) for j in range(10)], size=n),
        [f"192.168.{RNG.integers(0,255)}.{RNG.integers(0,255)}" for _ in range(n)],
    )

    df = pd.DataFrame({
        "user_id": user_ids,
        "transaction_amount": amounts,
        "payment_method": payment_methods,
        "timestamp": timestamps,
        "hour": hours,
        "device_id": device_ids,
        "ip_address": ip_addresses,
        "is_fraud": is_fraud,
    })

    df.to_csv(out_path, index=False)
    print(f"[DataGen] Fraud transactions saved → {out_path}  ({len(df):,} rows, "
          f"fraud rate: {is_fraud.mean():.1%})")
    return df


def _night_heavy_probs():
    """Probability distribution heavy on night hours (11pm–5am)."""
    probs = np.ones(23)
    night_hours = [0, 1, 2, 3, 4, 22]
    for h in night_hours:
        probs[h] = 6.0
    return probs / probs.sum()


# ─────────────────────────────────────────────────────────────────────────────
# 3. Behavioral Dataset
# ─────────────────────────────────────────────────────────────────────────────

def generate_behavioral(out_path: Path) -> pd.DataFrame:
    """Mimics: e-commerce-fraud-detection-dataset (~300K, 6000 users)"""
    n = N_TRANSACTIONS
    user_ids = RNG.integers(1, N_USERS + 1, size=n)
    is_fraud_user = np.isin(user_ids, list(FRAUD_USERS))

    # Burst behavior: fraud users cluster transactions in short windows
    day_offsets = np.where(
        is_fraud_user,
        RNG.choice(range(365), size=n, p=_burst_probs(365)),
        RNG.integers(0, 365, size=n),
    )

    session_lengths = np.where(
        is_fraud_user,
        RNG.integers(1, 5, size=n),        # very short sessions
        RNG.integers(5, 30, size=n),
    )

    pages_visited = np.where(
        is_fraud_user,
        RNG.integers(1, 4, size=n),
        RNG.integers(3, 20, size=n),
    )

    df = pd.DataFrame({
        "user_id": user_ids,
        "day_offset": day_offsets,
        "session_length_min": session_lengths,
        "pages_visited": pages_visited,
        "is_fraud": np.where(is_fraud_user, (RNG.random(n) < 0.55).astype(int),
                              (RNG.random(n) < 0.02).astype(int)),
    })

    df.to_csv(out_path, index=False)
    print(f"[DataGen] Behavioral dataset saved → {out_path}  ({len(df):,} rows)")
    return df


def _burst_probs(n_days: int):
    """Create burst probability — fraud concentrated in short time windows."""
    probs = np.ones(n_days)
    burst_days = RNG.choice(range(n_days), size=20, replace=False)
    for d in burst_days:
        probs[d] = 15.0
    return probs / probs.sum()


# ─────────────────────────────────────────────────────────────────────────────
# Entry Point
# ─────────────────────────────────────────────────────────────────────────────

def generate_all(data_dir: Path):
    raw = data_dir / "raw"
    raw.mkdir(parents=True, exist_ok=True)

    returns_path = raw / "returns.csv"
    fraud_path   = raw / "fraud_transactions.csv"
    behav_path   = raw / "behavioral.csv"

    dfs = {}

    if not returns_path.exists():
        dfs["returns"] = generate_returns(returns_path)
    else:
        print(f"[DataGen] Using existing: {returns_path}")
        dfs["returns"] = pd.read_csv(returns_path)

    if not fraud_path.exists():
        dfs["fraud"] = generate_fraud_transactions(fraud_path)
    else:
        print(f"[DataGen] Using existing: {fraud_path}")
        dfs["fraud"] = pd.read_csv(fraud_path)

    if not behav_path.exists():
        dfs["behavioral"] = generate_behavioral(behav_path)
    else:
        print(f"[DataGen] Using existing: {behav_path}")
        dfs["behavioral"] = pd.read_csv(behav_path)

    return dfs


if __name__ == "__main__":
    generate_all(Path(__file__).parent.parent / "data")
