from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from deepface import DeepFace
import time

app = FastAPI(title="Face Recognition Service")

class FaceCompareRequest(BaseModel):
    registered_image_url: str
    social_image_url: str

@app.post("/compare")
def compare_faces(request: FaceCompareRequest):
    try:
        # enforce_detection=False prevents the pipeline from crashing if the RetinaFace detector 
        # cannot find a face (e.g., heavily occluded, non-human avatar).
        result = DeepFace.verify(
            img1_path=request.registered_image_url,
            img2_path=request.social_image_url,
            model_name="ArcFace",
            detector_backend="retinaface",
            distance_metric="cosine",
            enforce_detection=False
        )
        
        distance = result.get("distance", 1.0)
        similarity = max(0.0, 1.0 - distance)
        
        return {
            "verified": result.get("verified", False),
            "distance": distance,
            "similarity": similarity,
            "facial_areas": {
                "img1": result.get("facial_areas", {}).get("img1", {}),
                "img2": result.get("facial_areas", {}).get("img2", {})
            }
        }
    except Exception as e:
        print(f"Error processing faces: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Face processing error: {str(e)}")

@app.get("/health")
def health_check():
    return {"status": "up"}
