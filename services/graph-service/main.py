from fastapi import FastAPI, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
import networkx as nx
import json
import os
import psycopg2
from ring_detector import build_entity_graph, detect_rings, detect_temporal_burst
import structlog

app = FastAPI(title="TriNetra Graph Intelligence Service")
log = structlog.get_logger()

app.add_middleware(CORSMiddleware, allow_origins=["*"], 
                   allow_methods=["*"], allow_headers=["*"])

def get_db():
    conn = psycopg2.connect(os.getenv("DATABASE_URL", "postgresql://trinetra:trinetra_dev@localhost:5433/trinetra"))
    try:
        yield conn
    finally:
        conn.close()

@app.get("/graph/network/{account_id}")
async def get_account_network(account_id: str, db=Depends(get_db)):
    """Returns D3.js-ready graph data for the dashboard."""
    
    # Get 2-hop neighborhood from entity_relationships
    cursor = db.cursor()
    cursor.execute("""
        WITH RECURSIVE hop2 AS (
            -- Direct connections
            SELECT entity_a_id, entity_a_type, relationship, 
                   entity_b_id, entity_b_type, 1 as hop
            FROM entity_relationships
            WHERE entity_a_id = %s OR entity_b_id = %s
            
            UNION
            
            -- 2nd hop connections
            SELECT er.entity_a_id, er.entity_a_type, er.relationship,
                   er.entity_b_id, er.entity_b_type, 2
            FROM entity_relationships er
            JOIN hop2 h ON (er.entity_a_id = h.entity_b_id 
                         OR er.entity_b_id = h.entity_a_id)
            WHERE h.hop = 1
        )
        SELECT * FROM hop2 LIMIT 500
    """, (account_id, account_id))
    
    relationships = [
        {"entity_a_id": r[0], "entity_a_type": r[1], "relationship": r[2],
         "entity_b_id": r[3], "entity_b_type": r[4]}
        for r in cursor.fetchall()
    ]
    
    # Build D3.js-compatible node/link format
    nodes = {}
    links = []
    
    for rel in relationships:
        for eid, etype in [(rel["entity_a_id"], rel["entity_a_type"]),
                           (rel["entity_b_id"], rel["entity_b_type"])]:
            if eid not in nodes:
                nodes[eid] = {
                    "id": eid,
                    "type": etype,
                    "label": f"{etype}:{eid[:8]}",
                    "risk_score": 0  # Populated separately
                }
        
        links.append({
            "source": rel["entity_a_id"],
            "target": rel["entity_b_id"],
            "relationship": rel["relationship"]
        })
    
    return {
        "nodes": list(nodes.values()),
        "links": links,
        "account_id": account_id
    }

@app.get("/graph/rings")
async def get_fraud_rings(db=Depends(get_db)):
    cursor = db.cursor()
    cursor.execute("""
        SELECT fr.id, fr.ring_name, fr.status, fr.member_count,
               fr.total_claimed_value, fr.confidence_score, fr.first_detected_at
        FROM fraud_rings fr
        WHERE fr.status IN ('ACTIVE','CONFIRMED')
        ORDER BY fr.total_claimed_value DESC
    """)
    rings = cursor.fetchall()
    
    return {
        "rings": [
            {
                "ring_id": str(r[0]), "ring_name": r[1], "status": r[2],
                "member_count": r[3], "total_claimed_value": float(r[4] or 0),
                "confidence": float(r[5] or 0),
                "first_detected": r[6].isoformat() if r[6] else None
            }
            for r in rings
        ],
        "total_rings": len(rings),
        "total_at_risk_value": sum(float(r[4] or 0) for r in rings)
    }

@app.get("/health")
async def health():
    return {"status": "healthy"}
