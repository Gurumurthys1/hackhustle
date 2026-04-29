"""
Fraud ring detection using NetworkX community detection.
No paid graph DB needed — Apache AGE on PostgreSQL handles persistence.
NetworkX for in-memory analysis.
"""
import networkx as nx
from networkx.algorithms import community
import numpy as np
from dataclasses import dataclass
from typing import Optional
import structlog

log = structlog.get_logger()

@dataclass
class RingDetectionResult:
    ring_detected: bool
    ring_id: Optional[str]
    ring_size: int
    role: str                   # RING_LEADER / MULE / MEMBER
    centrality_score: float
    connected_fraud_accounts: int

def build_entity_graph(relationships: list[dict]) -> nx.Graph:
    """
    Build in-memory graph from entity relationship table.
    Nodes: accounts, devices, IPs, addresses
    Edges: weighted by relationship type risk
    """
    G = nx.Graph()
    
    RELATIONSHIP_WEIGHTS = {
        "USES_DEVICE": 0.8,        # Strong signal
        "SHARES_IP": 0.4,          # Medium signal  
        "SHARES_ADDRESS": 0.9,     # Very strong signal
        "SAME_PHONE": 1.0,         # Definitive signal
        "SAME_EMAIL_DOMAIN": 0.2,  # Weak signal
    }
    
    for rel in relationships:
        weight = RELATIONSHIP_WEIGHTS.get(rel["relationship"], 0.5)
        G.add_edge(
            f"{rel['entity_a_type']}:{rel['entity_a_id']}",
            f"{rel['entity_b_type']}:{rel['entity_b_id']}",
            weight=weight,
            relationship=rel["relationship"]
        )
    
    return G

def detect_rings(G: nx.Graph, 
                 confirmed_fraud_nodes: set[str]) -> list[dict]:
    """
    Use Louvain community detection to find clusters.
    Flag clusters containing confirmed fraud nodes.
    """
    if len(G.nodes) < 2:
        return []
    
    # Louvain community detection (best for this use case)
    # Built into NetworkX 3.x
    try:
        communities = list(community.louvain_communities(G, seed=42))
    except Exception:
        # Fallback: connected components
        communities = list(nx.connected_components(G))
    
    rings = []
    
    for idx, comm in enumerate(communities):
        if len(comm) < 3:  # Need at least 3 members to be a ring
            continue
        
        # Check if any confirmed fraud node is in this community
        fraud_overlap = comm.intersection(confirmed_fraud_nodes)
        
        # Extract only account nodes from community
        account_nodes = {n for n in comm if n.startswith("account:")}
        
        if len(account_nodes) >= 3:
            # Compute PageRank for this subgraph to find ring leader
            subgraph = G.subgraph(comm)
            try:
                pagerank = nx.pagerank(subgraph, weight='weight')
            except:
                pagerank = {n: 1.0/len(comm) for n in comm}
            
            rings.append({
                "ring_id": f"RING-{idx:04d}",
                "members": list(account_nodes),
                "member_count": len(account_nodes),
                "has_confirmed_fraud": len(fraud_overlap) > 0,
                "confirmed_fraud_count": len(fraud_overlap),
                "ring_leader": max(
                    account_nodes, 
                    key=lambda n: pagerank.get(n, 0)
                ),
                "pagerank_scores": {
                    n: pagerank.get(n, 0) for n in account_nodes
                },
                "confidence": min(0.99, 0.5 + len(account_nodes) * 0.05 + 
                                  len(fraud_overlap) * 0.15)
            })
    
    return rings

def detect_temporal_burst(claims: list[dict], 
                          window_seconds: int = 10800) -> list[dict]:
    """
    Detect if graph-connected accounts all submitted claims within a time window.
    Classic signature of coordinated ring attacks.
    """
    # Group claims by 3-hour windows
    from datetime import datetime, timedelta
    
    if not claims:
        return []
    
    bursts = []
    sorted_claims = sorted(claims, key=lambda c: c["created_at"])
    
    i = 0
    while i < len(sorted_claims):
        window_start = sorted_claims[i]["created_at"]
        window_end = window_start + timedelta(seconds=window_seconds)
        
        window_claims = [
            c for c in sorted_claims[i:]
            if c["created_at"] <= window_end
        ]
        
        if len(window_claims) >= 5:  # 5+ claims in 3 hours = burst
            bursts.append({
                "window_start": window_start.isoformat(),
                "window_end": window_end.isoformat(),
                "claim_count": len(window_claims),
                "account_ids": list({c["account_id"] for c in window_claims}),
                "total_claimed_value": sum(c.get("claimed_amount", 0) for c in window_claims)
            })
        
        i += 1
    
    return bursts
