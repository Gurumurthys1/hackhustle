from .celery_app import app
import structlog
from ml.ela import analyze_ela
from ml.exif_analyzer import analyze_exif
from ml.phash_analyzer import check_perceptual_hash
from ml.clip_analyzer import compute_clip_similarity
from datetime import date
import io

log = structlog.get_logger()

@app.task(name='workers.image_worker.analyze_claim_images')
def analyze_claim_images(claim_id, claim):
    log.info("Starting image analysis", claim_id=claim_id)
    
    score = 0
    evidence = []
    
    # Mock storage fetch for now
    def get_image_bytes(url):
        # In prod, this would fetch from MinIO
        return b"mock_image_bytes"

    images = claim.get("images", [])
    if not images:
        return {"score": 0, "evidence": [], "category": "image"}

    for image_url in images:
        image_bytes = get_image_bytes(image_url)
        
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
        
        # pHash
        # In prod, DB connection would be passed here
        # phash_result = check_perceptual_hash(image_bytes, db)
        
    return {
        "score": min(score, 45),
        "evidence": evidence,
        "category": "image"
    }
