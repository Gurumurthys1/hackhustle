"""
services/common/db.py
Shared MongoDB connection utility for all Python services.
"""
import os
from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.errors import ConnectionFailure
import logging

logger = logging.getLogger(__name__)

_client = None
_db = None

def get_client() -> MongoClient:
    global _client
    if _client is None:
        uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
        _client = MongoClient(uri, serverSelectionTimeoutMS=5000)
        try:
            _client.admin.command("ping")
            logger.info("✅ MongoDB connected successfully")
        except ConnectionFailure as e:
            logger.error(f"❌ MongoDB connection failed: {e}")
            raise
    return _client


def get_db():
    global _db
    if _db is None:
        client = get_client()
        db_name = os.getenv("MONGODB_DB", "trinetra_db")
        _db = client[db_name]
    return _db


def get_collection(name: str):
    return get_db()[name]


# Collection name constants
ACCOUNTS           = "accounts"
ORDERS             = "orders"
RETURN_CLAIMS      = "return_claims"
IMAGE_FORENSICS    = "image_forensics_results"
RECEIPT_VALIDATIONS = "receipt_validations"
BEHAVIORAL_SCORES  = "behavioral_scores"
CARRIER_VALIDATIONS = "carrier_validations"
ENTITY_RELATIONS   = "entity_relationships"
FRAUD_RINGS        = "fraud_rings"
RING_MEMBERS       = "fraud_ring_members"
AUDIT_LOG          = "audit_log"


def ensure_indexes():
    """Create all indexes on first run."""
    db = get_db()

    db[RETURN_CLAIMS].create_index([("account_id", ASCENDING)])
    db[RETURN_CLAIMS].create_index([("status", ASCENDING)])
    db[RETURN_CLAIMS].create_index([("fraud_score", DESCENDING)])
    db[RETURN_CLAIMS].create_index([("created_at", DESCENDING)])

    db[ENTITY_RELATIONS].create_index(
        [("entity_a_id", ASCENDING), ("relationship", ASCENDING), ("entity_b_id", ASCENDING)],
        unique=True
    )
    db[BEHAVIORAL_SCORES].create_index([("account_id", ASCENDING)], unique=True)
    db[AUDIT_LOG].create_index([("entity_id", ASCENDING)])
    db[AUDIT_LOG].create_index([("created_at", DESCENDING)])
    db[FRAUD_RINGS].create_index([("status", ASCENDING)])

    logger.info("✅ MongoDB indexes ensured")
