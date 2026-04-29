from .celery_app import app
import structlog
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'common'))
from db import get_collection, BEHAVIORAL_SCORES

log = structlog.get_logger()

@app.task(name='workers.behavioral_worker.score_claim_behavior')
def score_claim_behavior(claim_id, claim):
    log.info("Starting behavioral analysis", claim_id=claim_id)

    score    = 0
    evidence = []
    account_id = claim.get("account_id")

    if not account_id:
        return {"score": 0, "evidence": [], "category": "behavioral"}

    try:
        col = get_collection(BEHAVIORAL_SCORES)
        row = col.find_one({"account_id": account_id})

        if row:
            inr_count  = row.get("inr_claim_count_90d", 0)
            percentile = row.get("risk_percentile", 0)
            wardrobing = row.get("wardrobing_score", 0)

            if inr_count > 2:
                score += 15
                evidence.append({
                    "signal": "HIGH_INR_RATE", "severity": "MEDIUM",
                    "points": 15,
                    "detail": f"{inr_count} INR claims in last 90 days (threshold: 2)"
                })
            if percentile > 0.95:
                score += 10
                evidence.append({
                    "signal": "HIGH_RETURN_PERCENTILE", "severity": "MEDIUM",
                    "points": 10,
                    "detail": f"Top {round((1 - percentile) * 100, 1)}% of returners in category"
                })
            if wardrobing > 0.7:
                score += 5
                evidence.append({
                    "signal": "WARDROBING_PATTERN", "severity": "LOW",
                    "points": 5,
                    "detail": "Average return within 3 days of purchase (fashion category)"
                })

    except Exception as e:
        log.error("Behavioral scoring failed", error=str(e))

    return {
        "score":    min(score, 30),
        "evidence": evidence,
        "category": "behavioral"
    }
