# -*- coding: utf-8 -*-
import os
os.environ["PYTHONIOENCODING"] = "utf-8"
"""
TriNetra AI - Main Training Script
Runs the complete pipeline:
  1. Preprocess + feature engineering
  2. Graph model (fraud ring detection)
  3. LSTM temporal model
  4. Autoencoder anomaly detection
  5. Risk fusion + decisions
  6. Save all outputs
"""

import sys
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT / "src"))

from preprocess   import run_preprocessing, FEATURE_COLS
from graph_model  import run_graph_model
from lstm_model   import run_lstm_model
from autoencoder  import run_autoencoder
from risk_fusion  import fuse_scores, apply_decisions, save_results, print_report

DATA_DIR   = ROOT / "data"
MODELS_DIR = ROOT / "models"
MODELS_DIR.mkdir(exist_ok=True)


def main():
    print("\n" + "="*62)
    print("  TriNetra AI - Fraud Detection System | Training Pipeline")
    print("="*62)

    # ── Step 1: Preprocess ────────────────────────────────────────────────
    merged, feat_cols = run_preprocessing(DATA_DIR, MODELS_DIR)

    # Load raw fraud transactions for graph + LSTM (need row-level data)
    raw_fraud = pd.read_csv(DATA_DIR / "raw" / "fraud_transactions.csv")

    # ── Step 2: Graph Model ───────────────────────────────────────────────
    graph_scores = run_graph_model(raw_fraud, merged, MODELS_DIR)

    # ── Step 3: LSTM Temporal Model ───────────────────────────────────────
    temporal_scores = run_lstm_model(raw_fraud, merged, MODELS_DIR)

    # ── Step 4: Autoencoder ───────────────────────────────────────────────
    # Use the actual feature columns present in merged df
    available_feats = [c for c in FEATURE_COLS if c in merged.columns]
    anomaly_scores  = run_autoencoder(merged, available_feats, MODELS_DIR)

    # ── Step 5: Fuse + Decide ─────────────────────────────────────────────
    print("\n[RiskFusion] Fusing scores...")
    result_df = fuse_scores(merged, graph_scores, temporal_scores, anomaly_scores)
    result_df = apply_decisions(result_df)
    save_results(result_df, DATA_DIR)

    # ── Step 6: Sample Reports ────────────────────────────────────────────
    print("\n" + "-"*62)
    print("  SAMPLE RISK REPORTS")
    print("-"*62)

    # Show highest-risk user
    top_risk = result_df.nlargest(1, "risk_score").iloc[0]
    print_report(top_risk)

    # Show lowest-risk user
    low_risk = result_df.nsmallest(1, "risk_score").iloc[0]
    print_report(low_risk)

    # Show a VERIFY-range user
    verify_users = result_df[result_df["decision"] == "VERIFY"]
    if not verify_users.empty:
        print_report(verify_users.iloc[0])

    print("\n✅ Training complete! All models saved to:", MODELS_DIR)
    print("   Run the dashboard with:  streamlit run app/dashboard.py\n")

    return result_df


if __name__ == "__main__":
    main()
