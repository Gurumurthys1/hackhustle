"""
Carrier Validation Worker — Celery Task
Validates delivery status via carrier API (stubbed for sandbox).
In production: calls Delhivery / Shiprocket / BlueDart APIs.
"""
from .celery_app import app
import structlog
import os
import psycopg2
import json
from datetime import datetime

log = structlog.get_logger()


@app.task(name='workers.carrier_worker.validate_claim_carrier')
def validate_claim_carrier(claim_id: str, claim: dict) -> dict:
    """
    Validates carrier delivery status for INR (Item Not Received) claims.
    High-signal: if carrier confirms delivery → strong fraud indicator.
    """
    log.info("Starting carrier validation", claim_id=claim_id)

    score = 0
    evidence = []
    category = "carrier"

    # Carrier check only applies to INR claims
    claim_type = claim.get("claimType") or claim.get("claim_type", "")
    if claim_type != "INR":
        return {"score": 0, "evidence": [], "category": category}

    order_id = claim.get("orderId") or claim.get("order_id")
    if not order_id:
        return {"score": 0, "evidence": [], "category": category}

    try:
        conn = psycopg2.connect(
            os.getenv("DATABASE_URL", "postgresql://trinetra:trinetra_dev@localhost:5433/trinetra")
        )
        cursor = conn.cursor()

        # Check if a carrier validation record already exists (populated by carrier API)
        cursor.execute("""
            SELECT delivery_confirmed, delivery_timestamp, carrier_name,
                   pod_available, scan_history
            FROM carrier_validations
            WHERE order_id = %s
            ORDER BY created_at DESC LIMIT 1
        """, (order_id,))
        row = cursor.fetchone()

        if row:
            delivery_confirmed, delivery_ts, carrier_name, pod_available, scan_history = row

            if delivery_confirmed:
                score += 25
                detail = f"{carrier_name or 'Carrier'} confirmed delivery"
                if delivery_ts:
                    detail += f" at {delivery_ts}"
                if pod_available:
                    detail += " (Proof of Delivery photo available)"
                evidence.append({
                    "type": "CARRIER_DELIVERY_CONFIRMED",
                    "severity": "HIGH",
                    "detail": detail,
                    "score_added": 25
                })

                # Extra signal: scan history shows delivery at a different city
                if scan_history:
                    scans = scan_history if isinstance(scan_history, list) else json.loads(scan_history)
                    delivery_city = claim.get("order", {}).get("delivery_city", "")
                    if scans and delivery_city:
                        last_scan = scans[-1] if scans else {}
                        scan_city = last_scan.get("city", "")
                        if scan_city and scan_city.lower() != delivery_city.lower():
                            score += 5
                            evidence.append({
                                "type": "CARRIER_CITY_MISMATCH",
                                "severity": "MEDIUM",
                                "detail": f"Delivery scanned in {scan_city}, claim says {delivery_city}",
                                "score_added": 5
                            })
        else:
            # No carrier data yet — try to fetch from API (sandbox stub)
            carrier_result = _fetch_carrier_status(claim)
            if carrier_result:
                # Persist result for future lookups
                cursor.execute("""
                    INSERT INTO carrier_validations 
                        (claim_id, order_id, carrier_name, tracking_number,
                         delivery_confirmed, delivery_timestamp, api_response_raw)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT DO NOTHING
                """, (
                    claim_id, order_id,
                    carrier_result.get("carrier_name"),
                    carrier_result.get("tracking_number"),
                    carrier_result.get("delivery_confirmed", False),
                    carrier_result.get("delivery_timestamp"),
                    json.dumps(carrier_result)
                ))
                conn.commit()

                if carrier_result.get("delivery_confirmed"):
                    score += 25
                    evidence.append({
                        "type": "CARRIER_DELIVERY_CONFIRMED",
                        "severity": "HIGH",
                        "detail": f"{carrier_result.get('carrier_name', 'Carrier')} confirmed delivery",
                        "score_added": 25
                    })

        conn.close()

    except Exception as e:
        log.error("Carrier validation failed", claim_id=claim_id, error=str(e))

    return {
        "score": min(score, 25),
        "evidence": evidence,
        "category": category
    }


def _fetch_carrier_status(claim: dict) -> dict | None:
    """
    Stub for carrier API integration.
    In production: call Delhivery / Shiprocket sandbox APIs.
    Returns None if no tracking info available.
    """
    tracking_number = claim.get("order", {}).get("tracking_number")
    carrier_name = claim.get("order", {}).get("carrier_name", "").upper()

    if not tracking_number:
        return None

    # Sandbox stub — simulates confirmed delivery for demo
    # Replace with real API calls:
    # Delhivery: GET https://track.delhivery.com/api/v1/packages/json/?waybill={tracking}
    # Shiprocket: GET https://apiv2.shiprocket.in/v1/external/courier/track/awb/{tracking}

    return {
        "carrier_name": carrier_name or "DEMO_CARRIER",
        "tracking_number": tracking_number,
        "delivery_confirmed": True,  # Sandbox always confirms for demo
        "delivery_timestamp": datetime.utcnow().isoformat(),
        "pod_available": False,
        "scan_history": [
            {"city": claim.get("order", {}).get("delivery_city", "Unknown"),
             "status": "DELIVERED", "timestamp": datetime.utcnow().isoformat()}
        ]
    }
