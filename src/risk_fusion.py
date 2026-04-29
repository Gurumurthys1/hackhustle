"""
TriNetra AI - Risk Fusion Engine + Decision Engine
Formula: Risk = 0.3 x Graph + 0.4 x Temporal + 0.3 x Anomaly
"""

import pandas as pd
import numpy as np
from pathlib import Path

APPROVE_MAX = 30
VERIFY_MAX  = 70
W_GRAPH     = 0.30
W_TEMPORAL  = 0.40
W_ANOMALY   = 0.30


def fuse_scores(df_merged, graph_scores, temporal_scores, anomaly_scores):
    df = df_merged.copy().set_index("user_id")
    df["graph_risk_score"]    = graph_scores.reindex(df.index).fillna(0)
    df["temporal_risk_score"] = temporal_scores.reindex(df.index).fillna(0)
    df["anomaly_score"]       = anomaly_scores.reindex(df.index).fillna(0)
    df["risk_score"] = (
        W_GRAPH    * df["graph_risk_score"] +
        W_TEMPORAL * df["temporal_risk_score"] +
        W_ANOMALY  * df["anomaly_score"]
    ).clip(0, 100).round(1)
    return df.reset_index()


def make_decision(risk_score):
    if risk_score <= APPROVE_MAX:
        return "APPROVE"
    elif risk_score <= VERIFY_MAX:
        return "VERIFY"
    else:
        return "BLOCK"


def explain(row):
    reasons = []
    if row.get("graph_risk_score", 0) > 50:
        reasons.append("Connected to multiple suspicious accounts (fraud ring detected)")
    elif row.get("graph_risk_score", 0) > 25:
        reasons.append("Shares device or IP with flagged users")
    if row.get("temporal_risk_score", 0) > 60:
        reasons.append("Abnormal transaction burst or return spike detected")
    if row.get("night_activity_flag", 0) == 1:
        reasons.append("High volume of late-night transactions (11PM-5AM)")
    if row.get("burst_flag", 0) == 1:
        reasons.append("Sudden spike in transaction count (burst behavior)")
    if row.get("anomaly_score", 0) > 60:
        reasons.append("Behavior significantly deviates from normal user profile")
    if row.get("return_ratio", 0) > 0.5:
        reasons.append(f"High return ratio ({row['return_ratio']:.0%} of orders returned)")
    if row.get("high_value_flag", 0) == 1:
        reasons.append("High-value transaction (above 95th percentile)")
    if row.get("unique_devices", 0) > 3:
        reasons.append(f"Multiple devices used ({int(row['unique_devices'])} devices)")
    if row.get("unique_ips", 0) > 3:
        reasons.append(f"Multiple IP addresses detected ({int(row['unique_ips'])} IPs)")
    if row.get("wardrobing_count", 0) > 2:
        reasons.append("Multiple 'Wardrobing' returns flagged")
    if not reasons:
        reasons.append("No significant risk signals detected")
    return reasons


def apply_decisions(df):
    df["decision"]   = df["risk_score"].apply(make_decision)
    df["reasons"]    = df.apply(explain, axis=1)
    df["reason_str"] = df["reasons"].apply(lambda r: " | ".join(r))
    return df


DECISION_TAG = {"APPROVE": "[OK]", "VERIFY": "[!!]", "BLOCK": "[BLOCK]"}


def print_report(row):
    uid      = row["user_id"]
    score    = row["risk_score"]
    decision = row["decision"]
    tag      = DECISION_TAG[decision]
    print(f"""
==========================================
  TriNetra AI - Risk Report
==========================================
  User ID     : {uid}
  Risk Score  : {score:.1f} / 100
  Decision    : {tag} {decision}

  Component Scores:
    Graph (Fraud Rings)  : {row.get('graph_risk_score', 0):.1f}
    Temporal (LSTM)      : {row.get('temporal_risk_score', 0):.1f}
    Anomaly (Autoencoder): {row.get('anomaly_score', 0):.1f}

  Reasons:""")
    for r in row["reasons"]:
        print(f"    * {r}")
    print("==========================================\n")


def save_results(df, data_dir):
    out = data_dir / "processed" / "risk_scores.csv"
    df[["user_id", "risk_score", "decision", "reason_str",
        "graph_risk_score", "temporal_risk_score", "anomaly_score",
        "fraud_label"]].to_csv(out, index=False)
    print(f"[RiskFusion] Results saved -> {out}")
    dist = df["decision"].value_counts()
    print("\n[RiskFusion] Decision distribution:")
    for d, cnt in dist.items():
        print(f"  {DECISION_TAG[d]} {d}: {cnt:,} ({cnt/len(df):.1%})")
