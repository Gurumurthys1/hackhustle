"""
TriNetra AI — SHAP Explainability Module
Uses sklearn GradientBoosting surrogate + SHAP TreeExplainer.
No xgboost required — shap is already installed.
"""

import numpy as np
import pandas as pd
from pathlib import Path
import joblib

ROOT = Path(__file__).resolve().parent.parent

FEATURE_COLS = [
    "transaction_count", "avg_transaction_amount", "max_transaction_amount",
    "night_tx_count", "unique_payment_methods", "unique_devices", "unique_ips",
    "return_count", "avg_return_time", "avg_return_amount", "wardrobing_count",
    "session_count", "avg_session_length", "avg_pages_visited", "day_offset_std",
    "return_ratio", "burst_flag", "night_activity_flag", "high_value_flag",
]

FEATURE_LABELS = {
    "transaction_count":       "Transaction Count",
    "avg_transaction_amount":  "Avg Transaction Amount",
    "max_transaction_amount":  "Max Transaction Amount",
    "night_tx_count":          "Night Transactions",
    "unique_payment_methods":  "Unique Payment Methods",
    "unique_devices":          "Unique Devices Used",
    "unique_ips":              "Unique IPs Used",
    "return_count":            "Return Count",
    "avg_return_time":         "Avg Return Time (days)",
    "avg_return_amount":       "Avg Return Amount",
    "wardrobing_count":        "Wardrobing Returns",
    "session_count":           "Session Count",
    "avg_session_length":      "Avg Session Length",
    "avg_pages_visited":       "Avg Pages Visited",
    "day_offset_std":          "Activity Spread",
    "return_ratio":            "Return Ratio",
    "burst_flag":              "Burst Activity Flag",
    "night_activity_flag":     "Night Activity Flag",
    "high_value_flag":         "High-Value Transaction Flag",
}


def train_surrogate(merged_df: pd.DataFrame, risk_scores: pd.Series,
                    models_dir: Path):
    """Train sklearn GradientBoosting surrogate on risk scores."""
    from sklearn.ensemble import GradientBoostingRegressor

    feat_cols = [c for c in FEATURE_COLS if c in merged_df.columns]
    X = merged_df.set_index("user_id")[feat_cols].fillna(0)
    y = risk_scores.reindex(X.index).fillna(0)

    model = GradientBoostingRegressor(
        n_estimators=150, max_depth=4,
        learning_rate=0.1, random_state=42
    )
    model.fit(X, y)

    r2 = model.score(X, y)
    joblib.dump({"model": model, "feat_cols": feat_cols},
                models_dir / "shap_surrogate.pkl")
    print(f"[SHAP] Surrogate trained. R² = {r2:.3f}")
    return model, feat_cols


def get_shap_values(user_id: int, merged_df: pd.DataFrame,
                    models_dir: Path):
    """
    Returns DataFrame with feature contributions for one user.
    Falls back to feature-importance-based approximation if SHAP fails.
    """
    surrogate_path = models_dir / "shap_surrogate.pkl"
    if not surrogate_path.exists():
        return None

    bundle    = joblib.load(surrogate_path)
    model     = bundle["model"]
    feat_cols = bundle["feat_cols"]

    user_row = merged_df[merged_df["user_id"] == user_id]
    if user_row.empty:
        return None

    X_user = user_row[feat_cols].fillna(0)

    # Try SHAP first
    try:
        import shap
        explainer  = shap.TreeExplainer(model)
        shap_vals  = explainer.shap_values(X_user)[0]
        base_value = float(explainer.expected_value)

    except Exception:
        # Fallback: feature importance × (feature value - mean)
        importances = model.feature_importances_
        X_vals      = X_user.values[0]
        shap_vals   = importances * X_vals
        base_value  = 0.0

    result = pd.DataFrame({
        "feature":    feat_cols,
        "label":      [FEATURE_LABELS.get(f, f) for f in feat_cols],
        "raw_value":  X_user.values[0],
        "shap_value": shap_vals,
    }).sort_values("shap_value", key=abs, ascending=False).reset_index(drop=True)

    result["base_value"] = base_value
    return result


def run_explainability(data_dir: Path, models_dir: Path):
    """Train surrogate and save for dashboard use."""
    merged_path = data_dir / "processed" / "merged_features.csv"
    scores_path = data_dir / "processed" / "risk_scores.csv"

    if not merged_path.exists() or not scores_path.exists():
        print("[SHAP] Run train.py first.")
        return

    merged    = pd.read_csv(merged_path)
    scores_df = pd.read_csv(scores_path)
    risk_scores = pd.Series(
        scores_df["risk_score"].values,
        index=scores_df["user_id"].values
    )

    train_surrogate(merged, risk_scores, models_dir)
    print("[SHAP] Surrogate saved to models/shap_surrogate.pkl")


if __name__ == "__main__":
    run_explainability(ROOT / "data", ROOT / "models")
