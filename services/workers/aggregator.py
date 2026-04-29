from .celery_app import app
import structlog, sys, os
from datetime import datetime, timezone

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'common'))
from db import get_collection, RETURN_CLAIMS, AUDIT_LOG

log = structlog.get_logger()

@app.task(name='workers.aggregator.aggregate_scores')
def aggregate_scores(results, claim_id):
    """
    Final step: Aggregates results from all workers and writes to MongoDB.
    'results' is a list of dicts from each worker in the Celery chord group.
    """
    log.info("Aggregating fraud scores", claim_id=claim_id, results_count=len(results))

    total_score  = 0
    all_evidence = []
    sub_scores   = {}

    for res in results:
        if not res:
            continue
        total_score += res.get("score", 0)
        all_evidence.extend(res.get("evidence", []))
        sub_scores[res.get("category", "unknown")] = res.get("score", 0)

    final_score = min(total_score, 100)

    # Determine tier
    if final_score >= 80:
        tier   = "HIGH_RISK"
        status = "ESCALATED"
        action = "ESCALATE"
    elif final_score >= 60:
        tier   = "ELEVATED_RISK"
        status = "UNDER_REVIEW"
        action = "HUMAN_REVIEW"
    elif final_score >= 30:
        tier   = "CAUTION"
        status = "UNDER_REVIEW"
        action = "REQUEST_INFO"
    else:
        tier   = "TRUSTED"
        status = "APPROVED"
        action = "AUTO_APPROVE"

    # Generate human-readable explanation (DPDPA Right to Explanation)
    if tier == "TRUSTED":
        explanation = "Your return request has been approved. Refund will be credited within 3-5 business days."
    elif tier == "CAUTION":
        explanation = "We need a little more information to process your return. Our team will contact you shortly."
    elif tier == "ELEVATED_RISK":
        explanation = "We need a bit more information. Our team will contact you within 24 hours."
    else:
        explanation = "Your return request is under review by our specialist team. We will contact you within 4 hours."

    now = datetime.now(timezone.utc)

    # Update claim in MongoDB
    try:
        claims = get_collection(RETURN_CLAIMS)
        claims.update_one(
            {"_id": claim_id},
            {"$set": {
                "fraud_score":          final_score,
                "fraud_tier":           tier,
                "status":               status,
                "recommended_action":   action,
                "evidence":             all_evidence,
                "sub_scores":           sub_scores,
                "explainability_text":  explanation,
                "updated_at":           now,
                "scored_at":            now,
            }}
        )
        log.info("Claim updated with final score", claim_id=claim_id,
                 score=final_score, tier=tier)
    except Exception as e:
        log.error("Failed to update final score in MongoDB", error=str(e))

    # Write to audit log
    try:
        audit = get_collection(AUDIT_LOG)
        audit.insert_one({
            "entity_type": "return_claim",
            "entity_id":   claim_id,
            "action":      "FRAUD_SCORE_COMPUTED",
            "actor_type":  "SYSTEM",
            "actor_id":    None,
            "metadata": {
                "score":     final_score,
                "tier":      tier,
                "action":    action,
                "sub_scores": sub_scores,
                "evidence_count": len(all_evidence),
            },
            "created_at": now,
        })
    except Exception as e:
        log.error("Failed to write audit log", error=str(e))

    return {"claim_id": claim_id, "final_score": final_score, "tier": tier}
