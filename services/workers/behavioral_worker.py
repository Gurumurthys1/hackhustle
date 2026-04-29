from .celery_app import app
import structlog
import os
import psycopg2

log = structlog.get_logger()

@app.task(name='workers.behavioral_worker.score_claim_behavior')
def score_claim_behavior(claim_id, claim):
    log.info("Starting behavioral analysis", claim_id=claim_id)
    
    score = 0
    evidence = []
    account_id = claim.get("account_id")
    
    if not account_id:
        return {"score": 0, "evidence": [], "category": "behavioral"}

    try:
        conn = psycopg2.connect(os.getenv("DATABASE_URL", "postgresql://trinetra:trinetra_dev@localhost:5433/trinetra"))
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT inr_claim_count_90d, risk_percentile, wardrobing_score
            FROM behavioral_scores WHERE account_id = %s
        """, (account_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            inr_count, percentile, wardrobing = row
            if inr_count and inr_count > 2:
                score += 15
                evidence.append({"type": "HIGH_INR_RATE", "severity": "MEDIUM", "detail": f"{inr_count} INR claims in 90d", "score_added": 15})
            if percentile and percentile > 95:
                score += 10
                evidence.append({"type": "HIGH_RETURN_PERCENTILE", "severity": "MEDIUM", "detail": "Top 5% return rate", "score_added": 10})
    except Exception as e:
        log.error("Behavioral scoring failed", error=str(e))

    return {
        "score": min(score, 30),
        "evidence": evidence,
        "category": "behavioral"
    }
