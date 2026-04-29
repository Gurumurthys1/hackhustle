"""
Central orchestrator. Runs all detectors in parallel via asyncio.
Never blocks. Returns score + full evidence trail.
"""
import asyncio
from dataclasses import dataclass, field
from typing import Optional
from datetime import date
import structlog

log = structlog.get_logger()

@dataclass
class FraudScore:
    score: int                    # 0–100
    tier: str                     # TRUSTED / CAUTION / ELEVATED_RISK / HIGH_RISK
    recommended_action: str
    evidence: list[dict]          # Structured evidence items
    explainability_text: str      # Human-readable for admin
    customer_message: str         # Safe message for customer
    sub_scores: dict              # Breakdown by category
    computed_in_ms: int

TIER_MAP = {
    (0,  29):  ("TRUSTED",       "AUTO_APPROVE"),
    (30, 59):  ("CAUTION",       "SOFT_CHECK"),
    (60, 79):  ("ELEVATED_RISK", "QUEUE_REVIEW"),
    (80, 100): ("HIGH_RISK",     "ESCALATE"),
}

async def compute_fraud_score(claim: dict, db, storage) -> FraudScore:
    import time
    start = time.time()
    
    score = 0
    evidence = []
    sub_scores = {"image": 0, "receipt": 0, "behavioral": 0,
                  "carrier": 0, "graph": 0}
    
    # Run all analyses in parallel — crucial for < 10s SLA
    tasks = [
        _score_images(claim, db, storage),
        _score_receipt(claim, db, storage),
        _score_behavior(claim, db),
        _score_carrier(claim, db),
        _score_graph(claim, db),
    ]
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    for result in results:
        if isinstance(result, Exception):
            log.error("Scoring component failed", error=str(result))
            continue  # Never crash — degrade gracefully
        
        component_score, component_evidence, component_name = result
        score += component_score
        sub_scores[component_name] = component_score
        evidence.extend(component_evidence)
    
    # Cap at 100
    final_score = min(score, 100)
    
    # Determine tier
    tier, action = "TRUSTED", "AUTO_APPROVE"
    for (low, high), (t, a) in TIER_MAP.items():
        if low <= final_score <= high:
            tier, action = t, a
            break
    
    elapsed_ms = int((time.time() - start) * 1000)
    
    return FraudScore(
        score=final_score,
        tier=tier,
        recommended_action=action,
        evidence=evidence,
        explainability_text=_build_admin_explanation(final_score, tier, evidence, sub_scores),
        customer_message=_build_customer_message(tier),
        sub_scores=sub_scores,
        computed_in_ms=elapsed_ms
    )

async def _score_images(claim, db, storage) -> tuple:
    from ml.ela import analyze_ela
    from ml.exif_analyzer import analyze_exif
    from ml.phash_analyzer import check_perceptual_hash
    from ml.clip_analyzer import compute_clip_similarity
    
    score = 0
    evidence = []
    
    if not claim.get("images"):
        return score, evidence, "image"
    
    for image_url in claim["images"]:
        image_bytes = await storage.get(image_url)
        if not image_bytes: continue
        
        # ELA
        ela = analyze_ela(image_bytes)
        if ela.manipulation_detected:
            score += 20
            evidence.append({
                "type": "IMAGE_ELA",
                "severity": "HIGH",
                "detail": f"Image editing detected in regions: {', '.join(ela.high_variance_regions)}",
                "score_added": 20
            })
        
        # EXIF
        purchase_date_str = claim.get("order", {}).get("ordered_at", "2024-01-01")[:10]
        purchase_date = date.fromisoformat(purchase_date_str)
        exif = analyze_exif(image_bytes, purchase_date, claim.get("order", {}).get("delivery_city", "Unknown"))
        if exif.photo_before_purchase:
            score += 15
            evidence.append({
                "type": "EXIF_DATE_MISMATCH",
                "severity": "HIGH",
                "detail": f"Photo taken {exif.days_before_purchase} days before purchase date",
                "score_added": 15
            })
        if exif.exif_missing:
            score += 5
            evidence.append({
                "type": "EXIF_MISSING",
                "severity": "LOW",
                "detail": "EXIF metadata stripped — possible manipulation",
                "score_added": 5
            })
        
        # pHash
        phash_result = check_perceptual_hash(image_bytes, db)
        if phash_result.recycled_image:
            score += 25
            evidence.append({
                "type": "RECYCLED_IMAGE",
                "severity": "CRITICAL",
                "detail": f"Image matches prior claim #{phash_result.matching_claim_id} ({phash_result.similarity:.0%} similarity)",
                "score_added": 25
            })
        
        # CLIP vs catalog
        catalog_bytes = await storage.get(f"catalog/{claim.get('order', {}).get('product_sku', 'default')}.jpg")
        if catalog_bytes:
            clip = compute_clip_similarity(image_bytes, catalog_bytes)
            if not clip.product_match:
                score += 15
                evidence.append({
                    "type": "PRODUCT_MISMATCH",
                    "severity": "HIGH",
                    "detail": f"Returned item {clip.similarity_score:.0%} similar to purchased product",
                    "score_added": 15
                })
    
    return min(score, 45), evidence, "image"

async def _score_receipt(claim, db, storage) -> tuple:
    from ml.receipt_ocr import analyze_receipt
    score = 0
    evidence = []
    
    if not claim.get("receipt_image"):
        return score, evidence, "receipt"
    
    receipt_bytes = await storage.get(claim["receipt_image"])
    if not receipt_bytes: return score, evidence, "receipt"
    
    file_type = "PDF" if claim["receipt_image"].endswith(".pdf") else "IMAGE"
    
    result = analyze_receipt(receipt_bytes, file_type)
    
    # Amount validation
    order_amount = claim.get("order", {}).get("order_amount")
    if result.extracted_amount and order_amount:
        diff_pct = abs(result.extracted_amount - order_amount) / order_amount
        if diff_pct > 0.05:  # > 5% difference
            score += 20
            evidence.append({
                "type": "RECEIPT_AMOUNT_MISMATCH",
                "severity": "HIGH",
                "detail": f"Receipt: ₹{result.extracted_amount} vs Order: ₹{order_amount}",
                "score_added": 20
            })
    
    if result.pdf_layers_detected:
        score += 15
        evidence.append({
            "type": "PDF_MANIPULATION",
            "severity": "HIGH",
            "detail": "Multiple font layers detected in PDF — text replacement suspected",
            "score_added": 15
        })
    
    return min(score, 35), evidence, "receipt"

async def _score_behavior(claim, db) -> tuple:
    score = 0
    evidence = []
    account_id = claim.get("account_id")
    if not account_id: return score, evidence, "behavioral"
    
    cursor = db.cursor()
    cursor.execute("""
        SELECT inr_claim_count_90d, return_rate_lifetime, 
               risk_percentile, wardrobing_score, chargeback_count_365d
        FROM behavioral_scores WHERE account_id = %s
    """, (account_id,))
    row = cursor.fetchone()
    
    if not row:
        return score, evidence, "behavioral"
    
    inr_count, return_rate, percentile, wardrobing, chargebacks = row
    
    if inr_count and inr_count > 2:
        score += 15
        evidence.append({
            "type": "HIGH_INR_RATE",
            "severity": "MEDIUM",
            "detail": f"{inr_count} INR claims in last 90 days (threshold: 2)",
            "score_added": 15
        })
    
    if percentile and percentile > 95:
        score += 10
        evidence.append({
            "type": "HIGH_RETURN_PERCENTILE",
            "severity": "MEDIUM",
            "detail": f"Account in top {100-int(percentile)}% return rate for category",
            "score_added": 10
        })
    
    if wardrobing and wardrobing > 0.7:
        score += 15
        evidence.append({
            "type": "WARDROBING_PATTERN",
            "severity": "MEDIUM",
            "detail": "Purchase-return timing matches wardrobing pattern for this category",
            "score_added": 15
        })
    
    if chargebacks and chargebacks > 2:
        score += 10
        evidence.append({
            "type": "HIGH_CHARGEBACK_HISTORY",
            "severity": "MEDIUM",
            "detail": f"{chargebacks} chargebacks in last 12 months",
            "score_added": 10
        })
    
    return min(score, 30), evidence, "behavioral"

async def _score_carrier(claim, db) -> tuple:
    score = 0
    evidence = []
    order_id = claim.get("order_id")
    
    if claim.get("claim_type") != "INR" or not order_id:
        return score, evidence, "carrier"
    
    # Query carrier validation result (populated by carrier-worker)
    cursor = db.cursor()
    cursor.execute("""
        SELECT delivery_confirmed, delivery_timestamp, carrier_name
        FROM carrier_validations WHERE order_id = %s
        ORDER BY created_at DESC LIMIT 1
    """, (order_id,))
    row = cursor.fetchone()
    
    if row and row[0]:  # delivery_confirmed = True
        score += 25
        evidence.append({
            "type": "CARRIER_DELIVERY_CONFIRMED",
            "severity": "HIGH",
            "detail": f"{row[2]} confirmed delivery at {row[1]}",
            "score_added": 25
        })
    
    return min(score, 25), evidence, "carrier"

async def _score_graph(claim, db) -> tuple:
    score = 0
    evidence = []
    account_id = claim.get("account_id")
    device_fp = claim.get("device_fingerprint")
    
    if not account_id: return score, evidence, "graph"
    
    # Check entity relationships
    cursor = db.cursor()
    
    # Shared device fingerprint check
    if device_fp:
        cursor.execute("""
            SELECT COUNT(DISTINCT entity_a_id) FROM entity_relationships
            WHERE entity_b_id = %s AND relationship = 'USES_DEVICE'
            AND entity_a_id != %s
        """, (device_fp, account_id))
        shared_accounts = cursor.fetchone()[0]
        
        if shared_accounts > 0:
            score += 15
            evidence.append({
                "type": "SHARED_DEVICE_FINGERPRINT",
                "severity": "HIGH",
                "detail": f"Device shared with {shared_accounts} other account(s)",
                "score_added": 15
            })
    
    # Check if account is in detected fraud ring
    cursor.execute("""
        SELECT fr.id, fr.ring_name, frm.role, fr.member_count
        FROM fraud_rings fr
        JOIN fraud_ring_members frm ON fr.id = frm.ring_id
        WHERE frm.account_id = %s AND fr.status IN ('ACTIVE','CONFIRMED')
    """, (account_id,))
    ring = cursor.fetchone()
    
    if ring:
        score += 50
        evidence.append({
            "type": "FRAUD_RING_MEMBER",
            "severity": "CRITICAL",
            "detail": f"Account is member of fraud ring {ring[1]} ({ring[3]} members). Role: {ring[2]}",
            "score_added": 50
        })
    
    return min(score, 50), evidence, "graph"

def _build_admin_explanation(score, tier, evidence, sub_scores) -> str:
    lines = [f"Fraud Score: {score}/100 — {tier}\n", "Evidence Summary:", "─" * 40]
    
    categories = {
        "image": "📷 Image Analysis",
        "receipt": "🧾 Receipt Validation",
        "behavioral": "📊 Behavioral Pattern",
        "carrier": "📦 Carrier Validation",
        "graph": "🕸️ Network Analysis"
    }
    
    for key, label in categories.items():
        cat_score = sub_scores.get(key, 0)
        lines.append(f"\n{label:30s} +{cat_score} pts")
        cat_evidence = [e for e in evidence if e.get("type", "").startswith(key.upper())]
        for ev in cat_evidence:
            lines.append(f"   • {ev['detail']}")
    
    lines.append(f"\nRecommended Action: {_get_action_label(tier)}")
    return "\n".join(lines)

def _build_customer_message(tier: str) -> str:
    messages = {
        "TRUSTED": "Your return request has been approved. Your refund will be processed in 3-5 business days.",
        "CAUTION": "We need a bit more information to process your return. Please provide an additional photo showing the specific issue.",
        "ELEVATED_RISK": "Your return is being reviewed by our team. This typically takes 24-48 hours. We'll email you once complete.",
        "HIGH_RISK": "Your return request is under review. Our team will contact you within 4 business hours."
    }
    return messages.get(tier, messages["ELEVATED_RISK"])

def _get_action_label(tier: str) -> str:
    labels = {
        "TRUSTED": "AUTO-APPROVE (no human needed)",
        "CAUTION": "SOFT CHECK (request additional photo)",
        "ELEVATED_RISK": "QUEUE FOR HUMAN REVIEW (24hr SLA)",
        "HIGH_RISK": "ESCALATE TO SENIOR REVIEWER (4hr SLA)"
    }
    return labels.get(tier, "QUEUE FOR HUMAN REVIEW")
