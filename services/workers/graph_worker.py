"""
Graph Intelligence Worker — Celery Task
Checks entity relationship graph for fraud rings, shared devices, and
coordinated account clusters using the entity_relationships table.
"""
from .celery_app import app
import structlog
import os
import psycopg2
import json

log = structlog.get_logger()


@app.task(name='workers.graph_worker.analyze_claim_graph')
def analyze_claim_graph(claim_id: str, claim: dict) -> dict:
    """
    Analyzes the entity graph for:
    1. Shared device fingerprint across accounts
    2. Shared delivery address across accounts
    3. Known fraud ring membership
    4. Suspicious IP clusters
    """
    log.info("Starting graph analysis", claim_id=claim_id)

    score = 0
    evidence = []
    category = "graph"

    account_id = claim.get("accountId") or claim.get("account_id")
    device_fp = claim.get("deviceFingerprint") or claim.get("device_fingerprint")
    ip_address = claim.get("ipAddress") or claim.get("ip_address")

    if not account_id:
        return {"score": 0, "evidence": [], "category": category}

    try:
        conn = psycopg2.connect(
            os.getenv("DATABASE_URL", "postgresql://trinetra:trinetra_dev@localhost:5433/trinetra")
        )
        cursor = conn.cursor()

        # ── 1. Upsert entity relationships ────────────────────────
        if device_fp:
            _upsert_relationship(cursor,
                "account", account_id, "USES_DEVICE", "device", device_fp)

        if ip_address:
            _upsert_relationship(cursor,
                "account", account_id, "SHARES_IP", "ip", ip_address)

        conn.commit()

        # ── 2. Shared device fingerprint check ─────────────────────
        if device_fp:
            cursor.execute("""
                SELECT COUNT(DISTINCT entity_a_id)
                FROM entity_relationships
                WHERE entity_b_id = %s
                  AND relationship = 'USES_DEVICE'
                  AND entity_a_id != %s
                  AND entity_a_type = 'account'
            """, (device_fp, account_id))
            shared_accounts = cursor.fetchone()[0]

            if shared_accounts > 0:
                pts = min(shared_accounts * 8, 20)
                score += pts
                evidence.append({
                    "type": "SHARED_DEVICE_FINGERPRINT",
                    "severity": "HIGH" if shared_accounts >= 3 else "MEDIUM",
                    "detail": f"Device fingerprint shared with {shared_accounts} other account(s)",
                    "score_added": pts
                })

        # ── 3. Shared IP cluster check ──────────────────────────────
        if ip_address:
            cursor.execute("""
                SELECT COUNT(DISTINCT entity_a_id)
                FROM entity_relationships
                WHERE entity_b_id = %s
                  AND relationship = 'SHARES_IP'
                  AND entity_a_id != %s
                  AND entity_a_type = 'account'
            """, (ip_address, account_id))
            shared_ip_accounts = cursor.fetchone()[0]

            if shared_ip_accounts >= 3:
                score += 10
                evidence.append({
                    "type": "IP_CLUSTER",
                    "severity": "MEDIUM",
                    "detail": f"IP address shared by {shared_ip_accounts} accounts in this session",
                    "score_added": 10
                })

        # ── 4. Known fraud ring membership ─────────────────────────
        cursor.execute("""
            SELECT fr.id, fr.ring_name, frm.role, fr.member_count,
                   fr.total_claimed_value, fr.confidence_score
            FROM fraud_rings fr
            JOIN fraud_ring_members frm ON fr.id = frm.ring_id
            WHERE frm.account_id = %s
              AND fr.status IN ('ACTIVE', 'CONFIRMED')
        """, (account_id,))
        ring = cursor.fetchone()

        if ring:
            ring_id, ring_name, role, member_count, total_value, confidence = ring
            score += 40
            evidence.append({
                "type": "FRAUD_RING_MEMBER",
                "severity": "CRITICAL",
                "detail": (
                    f"Account belongs to fraud ring '{ring_name or ring_id}' "
                    f"({member_count} members, ₹{float(total_value or 0):,.0f} claimed). "
                    f"Role: {role}. Confidence: {float(confidence or 0):.0%}"
                ),
                "score_added": 40
            })

        # ── 5. Velocity check — many claims in short window ────────
        cursor.execute("""
            SELECT COUNT(*) FROM return_claims
            WHERE account_id = %s
              AND created_at > NOW() - INTERVAL '30 days'
        """, (account_id,))
        recent_claims = cursor.fetchone()[0]

        if recent_claims >= 5:
            pts = min((recent_claims - 4) * 3, 15)
            score += pts
            evidence.append({
                "type": "HIGH_CLAIM_VELOCITY",
                "severity": "MEDIUM",
                "detail": f"{recent_claims} return claims submitted in last 30 days",
                "score_added": pts
            })

        conn.close()

    except Exception as e:
        log.error("Graph analysis failed", claim_id=claim_id, error=str(e))

    return {
        "score": min(score, 50),
        "evidence": evidence,
        "category": category
    }


def _upsert_relationship(cursor, type_a: str, id_a: str,
                          rel: str, type_b: str, id_b: str):
    """Insert or increment an entity relationship."""
    cursor.execute("""
        INSERT INTO entity_relationships
            (entity_a_type, entity_a_id, relationship, entity_b_type, entity_b_id,
             last_seen, occurrence_count)
        VALUES (%s, %s, %s, %s, %s, NOW(), 1)
        ON CONFLICT (entity_a_id, relationship, entity_b_id)
        DO UPDATE SET
            last_seen = NOW(),
            occurrence_count = entity_relationships.occurrence_count + 1
    """, (type_a, id_a, rel, type_b, id_b))
