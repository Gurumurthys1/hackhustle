from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from scoring.engine import compute_fraud_score
from compliance.checker import run_compliance_check
import os
import psycopg2
import structlog

# Initialize logger
log = structlog.get_logger()

# RUN COMPLIANCE CHECK ON STARTUP
run_compliance_check()

app = FastAPI(title="TriNetra Fraud Intelligence Engine")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    conn = psycopg2.connect(os.getenv("DATABASE_URL", "postgresql://trinetra:trinetra_dev@localhost:5433/trinetra"))
    try:
        yield conn
    finally:
        conn.close()

@app.post("/fraud/score")
async def get_score(claim: dict, db=Depends(get_db)):
    """Manual trigger for fraud scoring (usually handled async via Kafka)."""
    try:
        # Mock storage for manual trigger
        class MockStorage:
            async def get(self, key): return b"mock_data"
        
        score_result = await compute_fraud_score(claim, db, MockStorage())
        return score_result
    except Exception as e:
        log.error("Scoring failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health():
    return {"status": "healthy", "compliance": "passed"}
