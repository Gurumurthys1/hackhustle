from .celery_app import app
import structlog
import os
import psycopg2
import json

log = structlog.get_logger()

@app.task(name='workers.aggregator.aggregate_scores')
def aggregate_scores(results, claim_id):
    """
    Final step: Aggregates results from all workers and updates the DB.
    'results' is a list of dicts from each worker in the group.
    """
    log.info("Aggregating fraud scores", claim_id=claim_id, results_count=len(results))
    
    total_score = 0
    all_evidence = []
    sub_scores = {}

    for res in results:
        if not res: continue
        total_score += res.get("score", 0)
        all_evidence.extend(res.get("evidence", []))
        sub_scores[res.get("category", "unknown")] = res.get("score", 0)

    final_score = min(total_score, 100)
    
    # Determine tier
    tier = "TRUSTED"
    if final_score >= 80: tier = "HIGH_RISK"
    elif final_score >= 60: tier = "ELEVATED_RISK"
    elif final_score >= 30: tier = "CAUTION"

    # Update Database
    try:
        conn = psycopg2.connect(os.getenv("DATABASE_URL", "postgresql://trinetra:trinetra_dev@localhost:5433/trinetra"))
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE return_claims 
            SET fraud_score = %s, fraud_tier = %s, evidence = %s, status = %s
            WHERE id = %s
        """, (
            final_score, 
            tier, 
            json.dumps(all_evidence),
            'SCORED' if final_score < 60 else 'UNDER_REVIEW',
            claim_id
        ))
        
        conn.commit()
        conn.close()
        log.info("Claim updated with final score", claim_id=claim_id, score=final_score)
        
    except Exception as e:
        log.error("Failed to update final score in DB", error=str(e))

    return {"claim_id": claim_id, "final_score": final_score, "tier": tier}
