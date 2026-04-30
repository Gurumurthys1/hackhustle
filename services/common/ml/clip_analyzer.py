"""
Uses HuggingFace CLIP locally. No API key. No cost.
First run downloads ~340MB model — cache it in Docker volume.
"""
from transformers import CLIPProcessor, CLIPModel
import torch
from PIL import Image
import io
import numpy as np
from dataclasses import dataclass
from functools import lru_cache
import structlog

log = structlog.get_logger()

@dataclass
class CLIPResult:
    similarity_score: float   # 0.0–1.0 (< 0.4 = mismatch)
    product_match: bool
    confidence: float

@lru_cache(maxsize=1)
def _load_model():
    """Load once, cache in memory. ~340MB. Takes ~15s first load."""
    model_name = "openai/clip-vit-base-patch32"
    model = CLIPModel.from_pretrained(model_name)
    processor = CLIPProcessor.from_pretrained(model_name)
    model.eval()
    return model, processor

def compute_clip_similarity(
    claim_image_bytes: bytes,
    catalog_image_bytes: bytes
) -> CLIPResult:
    """
    Compare customer's claim image vs. official product catalog image.
    Low similarity = wrong product being returned (wardrobing / swap fraud).
    """
    try:
        model, processor = _load_model()
        
        claim_image = Image.open(io.BytesIO(claim_image_bytes)).convert('RGB')
        catalog_image = Image.open(io.BytesIO(catalog_image_bytes)).convert('RGB')
        
        with torch.no_grad():
            # Get image embeddings
            claim_inputs = processor(images=claim_image, return_tensors="pt")
            catalog_inputs = processor(images=catalog_image, return_tensors="pt")
            
            claim_features = model.get_image_features(**claim_inputs)
            catalog_features = model.get_image_features(**catalog_inputs)
            
            # Normalize embeddings
            claim_features = claim_features / claim_features.norm(dim=-1, keepdim=True)
            catalog_features = catalog_features / catalog_features.norm(dim=-1, keepdim=True)
            
            # Cosine similarity
            similarity = float(torch.mm(claim_features, catalog_features.T).squeeze())
        
        # CLIP cosine similarity ranges: 0.9+ same image, 0.7+ same product,
        # 0.4–0.6 similar category, < 0.4 different product
        # We use a strict threshold of 0.65 to catch similar but incorrect items (e.g., water bottle vs soda)
        return CLIPResult(
            similarity_score=similarity,
            product_match=similarity >= 0.65,
            confidence=0.88
        )
    
    except Exception as e:
        log.error("CLIP analysis failed", error=str(e))
        return CLIPResult(0.0, False, 0.0)  # Default to mismatch on error to force review
