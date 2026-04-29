"""
TriNetra AI — Graph Model (Fraud Ring Detection)
NetworkX + Louvain community detection → graph_risk_score per user.
"""

import sys
from pathlib import Path
import numpy as np
import pandas as pd
import networkx as nx
import joblib
from collections import defaultdict

ROOT = Path(__file__).parent.parent

try:
    import community as community_louvain
    HAS_LOUVAIN = True
except ImportError:
    HAS_LOUVAIN = False
    print("[GraphModel] python-louvain not found. Using degree-based scoring.")


def build_graph(df_fraud: pd.DataFrame) -> nx.Graph:
    G = nx.Graph()
    df = df_fraud.copy()
    df.columns = [c.lower().strip().replace(" ", "_") for c in df.columns]
    for c in ["customerid", "customer_id", "userid"]:
        if c in df.columns and "user_id" not in df.columns:
            df = df.rename(columns={c: "user_id"})

    attrs = [a for a in ["device_id", "ip_address", "payment_method"] if a in df.columns]
    print(f"[GraphModel] Building graph on: {attrs}")

    for attr in attrs:
        for attr_val, users in df.groupby(attr)["user_id"].apply(list).items():
            attr_node = f"{attr}::{attr_val}"
            G.add_node(attr_node, node_type="attribute")
            for u in set(users):
                user_node = f"user::{u}"
                G.add_node(user_node, node_type="user", user_id=int(u))
                w = users.count(u)
                if G.has_edge(user_node, attr_node):
                    G[user_node][attr_node]["weight"] += w
                else:
                    G.add_edge(user_node, attr_node, weight=w)

    print(f"[GraphModel] Graph: {G.number_of_nodes():,} nodes, {G.number_of_edges():,} edges")
    return G


def detect_fraud_rings(G: nx.Graph, fraud_labels: dict) -> dict:
    user_nodes = {n for n, d in G.nodes(data=True) if d.get("node_type") == "user"}
    if not user_nodes:
        return {}

    if HAS_LOUVAIN and len(G) > 0:
        partition = community_louvain.best_partition(G, weight="weight", random_state=42)
    else:
        partition = {n: i for i, n in enumerate(G.nodes())}

    comm_users = defaultdict(set)
    for node, cid in partition.items():
        if node in user_nodes:
            comm_users[cid].add(G.nodes[node]["user_id"])

    comm_density = {
        cid: sum(fraud_labels.get(m, 0) for m in members) / max(len(members), 1)
        for cid, members in comm_users.items()
    }

    user_scores = {}
    for node in user_nodes:
        uid = G.nodes[node]["user_id"]
        cid = partition.get(node, -1)
        density = comm_density.get(cid, 0)
        deg_norm = min(G.degree(node) / 20.0, 1.0)
        shared = sum(1 for an in G.neighbors(node)
                     for nb in G.neighbors(an) if nb != node and nb in user_nodes)
        ring_factor = min(shared / 10.0, 1.0)
        score = (0.5 * density + 0.3 * deg_norm + 0.2 * ring_factor) * 100
        user_scores[uid] = round(min(score, 100), 2)

    return user_scores


def run_graph_model(df_fraud: pd.DataFrame, df_merged: pd.DataFrame,
                    models_dir: Path) -> pd.Series:
    print("\n[GraphModel] Running...")
    G = build_graph(df_fraud)
    fraud_labels = dict(zip(df_merged["user_id"].astype(int),
                            df_merged["fraud_label"].astype(int)))
    scores = detect_fraud_rings(G, fraud_labels)
    all_users = df_merged["user_id"].astype(int).tolist()
    result = pd.Series({u: scores.get(u, 0.0) for u in all_users}, name="graph_risk_score")
    joblib.dump(scores, models_dir / "graph_scores.pkl")
    print(f"[GraphModel] Done. Mean={result.mean():.1f}, Max={result.max():.1f}")
    return result
