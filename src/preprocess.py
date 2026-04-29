"""
TriNetra AI — Data Preprocessor
Loads raw CSVs (or generates synthetic data), cleans, engineers features,
and produces a merged user-level feature matrix.
"""

import sys
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
import joblib

# Allow running from anywhere
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "src"))

from data_generator import generate_all  # noqa: E402


# ─────────────────────────────────────────────────────────────────────────────
# Loaders
# ─────────────────────────────────────────────────────────────────────────────

def load_datasets(data_dir: Path) -> dict:
    """Load raw CSVs; generate synthetic if absent."""
    return generate_all(data_dir)


# ─────────────────────────────────────────────────────────────────────────────
# Feature Engineering
# ─────────────────────────────────────────────────────────────────────────────

def engineer_return_features(df_returns: pd.DataFrame) -> pd.DataFrame:
    """Aggregate return dataset to user-level features."""
    df = df_returns.copy()

    # Normalise column names from real Kaggle CSV if slightly different
    df.columns = [c.lower().strip().replace(" ", "_") for c in df.columns]

    # Best-effort column mapping
    if "user_id" not in df.columns:
        for candidate in ["customerid", "customer_id", "userid"]:
            if candidate in df.columns:
                df = df.rename(columns={candidate: "user_id"})
                break

    grp = df.groupby("user_id")

    agg = pd.DataFrame({
        "return_count":    grp.size(),
        "avg_return_time": grp["days_to_return"].mean() if "days_to_return" in df.columns
                           else pd.Series(dtype=float),
    })

    if "return_amount" in df.columns:
        agg["avg_return_amount"] = grp["return_amount"].mean()

    if "return_reason" in df.columns:
        wardrobing = (df["return_reason"].str.lower() == "wardrobing")
        agg["wardrobing_count"] = wardrobing.groupby(df["user_id"]).sum()

    return agg.reset_index()


def engineer_transaction_features(df_fraud: pd.DataFrame) -> pd.DataFrame:
    """Aggregate fraud-transaction dataset to user-level features."""
    df = df_fraud.copy()
    df.columns = [c.lower().strip().replace(" ", "_") for c in df.columns]

    for candidate in ["customerid", "customer_id", "userid"]:
        if candidate in df.columns and "user_id" not in df.columns:
            df = df.rename(columns={candidate: "user_id"})

    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
        df["hour"] = df["timestamp"].dt.hour

    grp = df.groupby("user_id")

    agg = pd.DataFrame({
        "transaction_count":      grp.size(),
        "avg_transaction_amount": grp["transaction_amount"].mean()
                                  if "transaction_amount" in df.columns else np.nan,
        "max_transaction_amount": grp["transaction_amount"].max()
                                  if "transaction_amount" in df.columns else np.nan,
        "fraud_label":            grp["is_fraud"].max()
                                  if "is_fraud" in df.columns else 0,
    })

    if "hour" in df.columns:
        night_mask = df["hour"].between(23, 5, inclusive="both") | df["hour"].lt(5)
        night_tx = night_mask.groupby(df["user_id"]).sum()
        agg["night_tx_count"] = night_tx

    if "payment_method" in df.columns:
        unique_methods = df.groupby("user_id")["payment_method"].nunique()
        agg["unique_payment_methods"] = unique_methods

    if "device_id" in df.columns:
        agg["unique_devices"] = grp["device_id"].nunique()

    if "ip_address" in df.columns:
        agg["unique_ips"] = grp["ip_address"].nunique()

    return agg.reset_index()


def engineer_behavioral_features(df_behav: pd.DataFrame) -> pd.DataFrame:
    """Aggregate behavioral dataset to user-level features."""
    df = df_behav.copy()
    df.columns = [c.lower().strip().replace(" ", "_") for c in df.columns]

    for candidate in ["customerid", "customer_id", "userid"]:
        if candidate in df.columns and "user_id" not in df.columns:
            df = df.rename(columns={candidate: "user_id"})

    grp = df.groupby("user_id")

    agg = pd.DataFrame({
        "session_count": grp.size(),
    })

    if "session_length_min" in df.columns:
        agg["avg_session_length"] = grp["session_length_min"].mean()

    if "pages_visited" in df.columns:
        agg["avg_pages_visited"] = grp["pages_visited"].mean()

    if "day_offset" in df.columns:
        # Burst flag: std of day offsets — low std = burst clustering
        agg["day_offset_std"] = grp["day_offset"].std().fillna(0)

    return agg.reset_index()


# ─────────────────────────────────────────────────────────────────────────────
# Merge & Composite Features
# ─────────────────────────────────────────────────────────────────────────────

def merge_features(ret_feat, txn_feat, beh_feat) -> pd.DataFrame:
    """Outer-join all feature tables on user_id."""
    df = txn_feat.merge(ret_feat, on="user_id", how="outer")
    df = df.merge(beh_feat, on="user_id", how="outer")
    df = df.fillna(0)

    # ── Composite features ────────────────────────────────────────────────
    df["return_ratio"] = np.where(
        df["transaction_count"] > 0,
        df["return_count"] / (df["transaction_count"] + 1e-6),
        0,
    ).clip(0, 1)

    # Burst flag: Z-score of transaction count > 2
    tc_mean = df["transaction_count"].mean()
    tc_std  = df["transaction_count"].std() + 1e-6
    df["burst_flag"] = ((df["transaction_count"] - tc_mean) / tc_std > 2).astype(int)

    # Night activity flag
    df["night_activity_flag"] = (df.get("night_tx_count", pd.Series(0, index=df.index)) > 3).astype(int)

    # High-value flag: amount > 95th percentile
    p95 = df["avg_transaction_amount"].quantile(0.95)
    df["high_value_flag"] = (df["avg_transaction_amount"] > p95).astype(int)

    # Ensure fraud_label exists
    if "fraud_label" not in df.columns:
        df["fraud_label"] = 0

    return df


# ─────────────────────────────────────────────────────────────────────────────
# Scaling
# ─────────────────────────────────────────────────────────────────────────────

FEATURE_COLS = [
    "transaction_count", "avg_transaction_amount", "max_transaction_amount",
    "night_tx_count", "unique_payment_methods", "unique_devices", "unique_ips",
    "return_count", "avg_return_time", "avg_return_amount", "wardrobing_count",
    "session_count", "avg_session_length", "avg_pages_visited", "day_offset_std",
    "return_ratio", "burst_flag", "night_activity_flag", "high_value_flag",
]


def scale_features(df: pd.DataFrame, models_dir: Path, fit: bool = True):
    """Scale numeric features; save scaler for inference."""
    cols = [c for c in FEATURE_COLS if c in df.columns]
    scaler_path = models_dir / "scaler.pkl"

    if fit:
        scaler = StandardScaler()
        df[cols] = scaler.fit_transform(df[cols])
        joblib.dump(scaler, scaler_path)
        print(f"[Preprocess] Scaler saved → {scaler_path}")
    else:
        scaler = joblib.load(scaler_path)
        df[cols] = scaler.transform(df[cols])

    return df, cols


# ─────────────────────────────────────────────────────────────────────────────
# Full Pipeline
# ─────────────────────────────────────────────────────────────────────────────

def run_preprocessing(data_dir: Path, models_dir: Path) -> tuple[pd.DataFrame, list[str]]:
    """End-to-end preprocessing. Returns (feature_df, feature_cols)."""
    print("\n" + "="*60)
    print("  TriNetra AI — Data Preprocessing")
    print("="*60)

    dfs = load_datasets(data_dir)

    print("\n[Preprocess] Engineering features...")
    ret_feat = engineer_return_features(dfs["returns"])
    txn_feat = engineer_transaction_features(dfs["fraud"])
    beh_feat = engineer_behavioral_features(dfs["behavioral"])

    print(f"  Return features:      {ret_feat.shape}")
    print(f"  Transaction features: {txn_feat.shape}")
    print(f"  Behavioral features:  {beh_feat.shape}")

    merged = merge_features(ret_feat, txn_feat, beh_feat)
    print(f"\n[Preprocess] Merged dataset: {merged.shape}")

    merged, feat_cols = scale_features(merged, models_dir, fit=True)

    out_path = data_dir / "processed" / "merged_features.csv"
    merged.to_csv(out_path, index=False)
    print(f"[Preprocess] Saved → {out_path}")

    fraud_rate = merged["fraud_label"].mean()
    print(f"[Preprocess] Fraud rate in merged dataset: {fraud_rate:.2%}")
    print("="*60 + "\n")

    return merged, feat_cols


if __name__ == "__main__":
    run_preprocessing(
        data_dir=ROOT / "data",
        models_dir=ROOT / "models",
    )
