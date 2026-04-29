import imagehash
from PIL import Image
import io
from dataclasses import dataclass
from typing import Optional

@dataclass
class PHashResult:
    phash: str
    recycled_image: bool
    matching_claim_id: Optional[str]
    similarity: float

def check_perceptual_hash(
    image_bytes: bytes,
    db_conn
) -> PHashResult:
    """
    Compute pHash and compare against ALL prior claim images in DB.
    A recycled image (same photo reused across claims) is near-certain fraud.
    """
    image = Image.open(io.BytesIO(image_bytes)).convert('RGB')
    current_hash = imagehash.phash(image, hash_size=16)
    current_hash_str = str(current_hash)
    
    # Query all existing hashes from DB
    cursor = db_conn.cursor()
    cursor.execute("""
        SELECT claim_id, phash FROM image_forensics_results
        WHERE phash IS NOT NULL
        ORDER BY created_at DESC
        LIMIT 10000
    """)
    
    best_match_id = None
    best_similarity = 0.0
    
    for row in cursor.fetchall():
        existing_claim_id, existing_hash_str = row
        existing_hash = imagehash.hex_to_hash(existing_hash_str)
        
        # Hamming distance: 0 = identical, 256 = completely different
        distance = current_hash - existing_hash
        similarity = 1.0 - (distance / 256.0)
        
        if similarity > 0.92 and similarity > best_similarity:  # >92% match
            best_similarity = similarity
            best_match_id = str(existing_claim_id)
    
    return PHashResult(
        phash=current_hash_str,
        recycled_image=best_similarity > 0.92,
        matching_claim_id=best_match_id,
        similarity=best_similarity
    )
