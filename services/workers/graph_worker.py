from .celery_app import app
import structlog, sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'common'))
from db import get_collection, ENTITY_RELATIONS, RING_MEMBERS, FRAUD_RINGS

log = structlog.get_logger()

@app.task(name='workers.graph_worker.analyze_claim_graph')
def analyze_claim_graph(claim_id, claim):
    log.info("Starting graph analysis", claim_id=claim_id)

    score    = 0
    evidence = []
    account_id = claim.get("account_id")
    device_fp  = claim.get("device_fingerprint")

    if not account_id:
        return {"score": 0, "evidence": [], "category": "graph"}

    try:
        rels = get_collection(ENTITY_RELATIONS)

        # 1. Check shared device fingerprint
        if device_fp:
            shared_device_accounts = rels.count_documents({
                "relationship":  "USES_DEVICE",
                "entity_b_id":   device_fp,
                "entity_a_id":   {"$ne": account_id}
            })
            if shared_device_accounts >= 2:
                pts = min(8 * shared_device_accounts, 20)
                score += pts
                evidence.append({
                    "signal":   "SHARED_DEVICE_FINGERPRINT",
                    "severity": "HIGH" if shared_device_accounts >= 3 else "MEDIUM",
                    "points":   pts,
                    "detail":   f"Device fingerprint shared with {shared_device_accounts} other accounts"
                })

        # 2. Check ring membership
        members = get_collection(RING_MEMBERS)
        membership = members.find_one({"account_id": account_id})
        if membership:
            rings  = get_collection(FRAUD_RINGS)
            ring   = rings.find_one({"_id": membership["ring_id"]})
            ring_name = ring["ring_name"] if ring else membership["ring_id"]
            pts = 40
            score += pts
            evidence.append({
                "signal":   "FRAUD_RING_MEMBER",
                "severity": "HIGH",
                "points":   pts,
                "detail":   f"Member of {membership['ring_id']}: {ring_name}"
            })

        # 3. Check shared delivery address
        shared_addr = rels.count_documents({
            "relationship": "SHARES_ADDRESS",
            "entity_a_id":  account_id
        })
        if shared_addr > 0:
            pts = min(shared_addr * 3, 10)
            score += pts
            evidence.append({
                "signal":   "SHARED_DELIVERY_ADDRESS",
                "severity": "MEDIUM",
                "points":   pts,
                "detail":   f"Delivery address shared with {shared_addr} other accounts"
            })

    except Exception as e:
        log.error("Graph analysis failed", error=str(e))

    return {
        "score":    min(score, 50),
        "evidence": evidence,
        "category": "graph"
    }
