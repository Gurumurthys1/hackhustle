from .celery_app import app
import structlog
from ml.receipt_ocr import analyze_receipt

log = structlog.get_logger()

@app.task(name='workers.receipt_worker.analyze_claim_receipt')
def analyze_claim_receipt(claim_id, claim):
    log.info("Starting receipt analysis", claim_id=claim_id)
    
    score = 0
    evidence = []
    
    receipt_url = claim.get("receiptImage")
    if not receipt_url:
        return {"score": 0, "evidence": [], "category": "receipt"}

    # Mock storage fetch
    receipt_bytes = b"mock_receipt_bytes"
    file_type = "PDF" if receipt_url.endswith(".pdf") else "IMAGE"
    
    result = analyze_receipt(receipt_bytes, file_type)
    
    # Amount validation
    order_amount = claim.get("order", {}).get("order_amount", 0)
    if result.extracted_amount and order_amount:
        diff_pct = abs(result.extracted_amount - order_amount) / order_amount
        if diff_pct > 0.05:
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

    return {
        "score": min(score, 35),
        "evidence": evidence,
        "category": "receipt"
    }
