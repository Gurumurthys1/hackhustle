"""
infrastructure/mongodb/seed_data.py
Populates MongoDB with demo data for all collections.
Run once: python infrastructure/mongodb/seed_data.py
"""
import os, sys, uuid
from datetime import datetime, timedelta, timezone
import random

# Allow running from project root
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'services', 'common'))

MONGODB_URI = os.getenv(
    "MONGODB_URI",
    "mongodb+srv://gurumurthys252005_db_user:TriNetra@cluster0.x7chbyg.mongodb.net/?appName=Cluster0"
)
os.environ.setdefault("MONGODB_URI", MONGODB_URI)
os.environ.setdefault("MONGODB_DB", "trinetra_db")

from db import get_db, ensure_indexes
import db as C  # collection name constants

def now():
    return datetime.now(timezone.utc)

def uid():
    return str(uuid.uuid4())


def seed():
    db = get_db()
    ensure_indexes()

    # ── Drop existing demo data ────────────────────────────
    for col in [C.ACCOUNTS, C.ORDERS, C.RETURN_CLAIMS, C.IMAGE_FORENSICS,
                C.RECEIPT_VALIDATIONS, C.BEHAVIORAL_SCORES, C.CARRIER_VALIDATIONS,
                C.ENTITY_RELATIONS, C.FRAUD_RINGS, C.RING_MEMBERS, C.AUDIT_LOG]:
        db[col].delete_many({})
    print("🗑  Cleared existing data")

    # ── ACCOUNTS ──────────────────────────────────────────
    accts = [
        {"_id": "a1-innocent-001", "external_id": "CUST-INNOCENT-001",
         "email_hash": "abc123sha256", "account_age_days": 1095,
         "total_orders": 47, "total_returns": 2, "consent_given": True,
         "consent_timestamp": now(), "created_at": now()},

        {"_id": "a2-fraudster-002", "external_id": "CUST-FRAUDSTER-002",
         "email_hash": "def456sha256", "account_age_days": 15,
         "total_orders": 2, "total_returns": 2, "consent_given": True,
         "consent_timestamp": now(), "created_at": now()},

        {"_id": "a3-ring-003", "external_id": "CUST-RING-003",
         "email_hash": "ghi789sha256", "account_age_days": 8,
         "total_orders": 1, "total_returns": 1, "consent_given": True,
         "consent_timestamp": now(), "created_at": now()},

        {"_id": "a4-ring-004", "external_id": "CUST-RING-004",
         "email_hash": "jkl012sha256", "account_age_days": 6,
         "total_orders": 1, "total_returns": 1, "consent_given": True,
         "consent_timestamp": now(), "created_at": now()},

        {"_id": "a5-ring-005", "external_id": "CUST-RING-005",
         "email_hash": "mno345sha256", "account_age_days": 9,
         "total_orders": 1, "total_returns": 1, "consent_given": True,
         "consent_timestamp": now(), "created_at": now()},

        {"_id": "a6-cust-007", "external_id": "CUST-007",
         "email_hash": "pqr678sha256", "account_age_days": 120,
         "total_orders": 8, "total_returns": 3, "consent_given": True,
         "consent_timestamp": now(), "created_at": now()},

        {"_id": "a7-cust-012", "external_id": "CUST-012",
         "email_hash": "stu901sha256", "account_age_days": 450,
         "total_orders": 22, "total_returns": 4, "consent_given": True,
         "consent_timestamp": now(), "created_at": now()},

        # New Ring 0005 Accounts
        {"_id": "a8-ring-008", "external_id": "CUST-RING-008",
         "email_hash": "vwx234sha256", "account_age_days": 12,
         "total_orders": 3, "total_returns": 3, "consent_given": True,
         "consent_timestamp": now(), "created_at": now()},

        {"_id": "a9-ring-009", "external_id": "CUST-RING-009",
         "email_hash": "yzab567sha256", "account_age_days": 11,
         "total_orders": 2, "total_returns": 2, "consent_given": True,
         "consent_timestamp": now(), "created_at": now()},

        {"_id": "a10-ring-010", "external_id": "CUST-RING-010",
         "email_hash": "cdef890sha256", "account_age_days": 10,
         "total_orders": 2, "total_returns": 2, "consent_given": True,
         "consent_timestamp": now(), "created_at": now()},

        {"_id": "a11-ring-011", "external_id": "CUST-RING-011",
         "email_hash": "ghij123sha256", "account_age_days": 5,
         "total_orders": 1, "total_returns": 1, "consent_given": True,
         "consent_timestamp": now(), "created_at": now()},
    ]
    db[C.ACCOUNTS].insert_many(accts)
    print(f"✅ Inserted {len(accts)} accounts")

    # ── ORDERS ────────────────────────────────────────────
    orders = [
        {"_id": "ord-001", "account_id": "CUST-INNOCENT-001",
         "external_order_id": "ORD-INO-001", "product_sku": "WH-PRO-2024",
         "product_name": "Wireless Headphones Pro", "product_category": "ELECTRONICS",
         "order_amount": 3499.00, "currency": "INR",
         "ordered_at": now() - timedelta(days=10),
         "delivered_at": now() - timedelta(days=7),
         "carrier_name": "Delhivery", "tracking_number": "DL123456789IN",
         "delivery_city": "Bengaluru", "created_at": now()},
         
        {"_id": "ord-001b", "account_id": "CUST-INNOCENT-001",
         "external_order_id": "ORD-INO-001B", "product_sku": "DRESS-SUM-24",
         "product_name": "Summer Floral Dress", "product_category": "APPAREL",
         "order_amount": 1899.00, "currency": "INR",
         "ordered_at": now() - timedelta(days=14),
         "delivered_at": now() - timedelta(days=11),
         "carrier_name": "BlueDart", "tracking_number": "BD444555666IN",
         "delivery_city": "Bengaluru", "created_at": now()},
         
        {"_id": "ord-001c", "account_id": "CUST-INNOCENT-001",
         "external_order_id": "ORD-INO-001C", "product_sku": "SNEAK-RUN-11",
         "product_name": "Pro Running Sneakers", "product_category": "FOOTWEAR",
         "order_amount": 4299.00, "currency": "INR",
         "ordered_at": now() - timedelta(days=25),
         "delivered_at": now() - timedelta(days=21),
         "carrier_name": "Amazon Shipping", "tracking_number": "AMZ998877665IN",
         "delivery_city": "Bengaluru", "created_at": now()},

        {"_id": "ord-001d", "account_id": "CUST-INNOCENT-001",
         "external_order_id": "ORD-INO-001D", "product_sku": "IPH-15-PM",
         "product_name": "iPhone 15 Pro Max", "product_category": "ELECTRONICS",
         "order_amount": 159900.00, "currency": "INR",
         "ordered_at": now() - timedelta(days=12),
         "delivered_at": now() - timedelta(days=10),
         "carrier_name": "Delhivery", "tracking_number": "DL888777666IN",
         "delivery_city": "Bengaluru", "created_at": now()},

        {"_id": "ord-001e", "account_id": "CUST-INNOCENT-001",
         "external_order_id": "ORD-INO-001E", "product_sku": "COF-MKR-01",
         "product_name": "Espresso Coffee Maker", "product_category": "APPLIANCES",
         "order_amount": 14500.00, "currency": "INR",
         "ordered_at": now() - timedelta(days=40),
         "delivered_at": now() - timedelta(days=36),
         "carrier_name": "BlueDart", "tracking_number": "BD112233445IN",
         "delivery_city": "Bengaluru", "created_at": now()},

        {"_id": "ord-001f", "account_id": "CUST-INNOCENT-001",
         "external_order_id": "ORD-INO-001F", "product_sku": "MECH-KB-99",
         "product_name": "Mechanical Keyboard", "product_category": "ELECTRONICS",
         "order_amount": 6999.00, "currency": "INR",
         "ordered_at": now() - timedelta(days=5),
         "delivered_at": now() - timedelta(days=2),
         "carrier_name": "Amazon Shipping", "tracking_number": "AMZ554433221IN",
         "delivery_city": "Bengaluru", "created_at": now()},

        {"_id": "ord-002", "account_id": "CUST-FRAUDSTER-002",
         "external_order_id": "ORD-FRD-001", "product_sku": "SW-BAND-101",
         "product_name": "Smart Watch Band", "product_category": "ELECTRONICS",
         "order_amount": 1299.00, "currency": "INR",
         "ordered_at": now() - timedelta(days=5),
         "delivered_at": now() - timedelta(days=2),
         "carrier_name": "Shiprocket", "tracking_number": "SR987654321IN",
         "delivery_city": "Mumbai", "created_at": now()},

        {"_id": "ord-003", "account_id": "CUST-RING-003",
         "external_order_id": "ORD-RING-001", "product_sku": "PHONE-X12",
         "product_name": "Smartphone X12", "product_category": "ELECTRONICS",
         "order_amount": 4599.00, "currency": "INR",
         "ordered_at": now() - timedelta(days=3),
         "delivered_at": now() - timedelta(days=1),
         "carrier_name": "Delhivery", "tracking_number": "DL555666777IN",
         "delivery_city": "Mumbai", "created_at": now()},

        {"_id": "ord-004", "account_id": "CUST-RING-009",
         "external_order_id": "ORD-RING-009", "product_sku": "LAPTOP-M1",
         "product_name": "Pro Laptop M1", "product_category": "ELECTRONICS",
         "order_amount": 89999.00, "currency": "INR",
         "ordered_at": now() - timedelta(days=2),
         "delivered_at": now() - timedelta(days=1),
         "carrier_name": "BlueDart", "tracking_number": "BD999888777IN",
         "delivery_city": "Bangalore", "created_at": now()},

        {"_id": "ord-005", "account_id": "CUST-RING-004", "external_order_id": "ORD-RING-004", "product_sku": "PHONE-X12", "product_name": "Smartphone X12", "product_category": "ELECTRONICS", "order_amount": 4599.00, "currency": "INR", "ordered_at": now() - timedelta(days=3), "delivered_at": now() - timedelta(days=1), "carrier_name": "Delhivery", "tracking_number": "DL555666778IN", "delivery_city": "Mumbai", "created_at": now()},
        {"_id": "ord-006", "account_id": "CUST-RING-005", "external_order_id": "ORD-RING-005", "product_sku": "PHONE-X12", "product_name": "Smartphone X12", "product_category": "ELECTRONICS", "order_amount": 4599.00, "currency": "INR", "ordered_at": now() - timedelta(days=3), "delivered_at": now() - timedelta(days=1), "carrier_name": "Delhivery", "tracking_number": "DL555666779IN", "delivery_city": "Mumbai", "created_at": now()},
        {"_id": "ord-007", "account_id": "CUST-007", "external_order_id": "ORD-INO-007", "product_sku": "WH-PRO-2024", "product_name": "Wireless Headphones Pro", "product_category": "ELECTRONICS", "order_amount": 3499.00, "currency": "INR", "ordered_at": now() - timedelta(days=10), "delivered_at": now() - timedelta(days=7), "carrier_name": "Delhivery", "tracking_number": "DL123456780IN", "delivery_city": "Bengaluru", "created_at": now()},
        {"_id": "ord-008", "account_id": "CUST-012", "external_order_id": "ORD-INO-012", "product_sku": "WH-PRO-2024", "product_name": "Wireless Headphones Pro", "product_category": "ELECTRONICS", "order_amount": 3499.00, "currency": "INR", "ordered_at": now() - timedelta(days=10), "delivered_at": now() - timedelta(days=7), "carrier_name": "Delhivery", "tracking_number": "DL123456781IN", "delivery_city": "Bengaluru", "created_at": now()},
        {"_id": "ord-009", "account_id": "CUST-RING-008", "external_order_id": "ORD-RING-008", "product_sku": "LAPTOP-M1", "product_name": "Pro Laptop M1", "product_category": "ELECTRONICS", "order_amount": 89999.00, "currency": "INR", "ordered_at": now() - timedelta(days=2), "delivered_at": now() - timedelta(days=1), "carrier_name": "BlueDart", "tracking_number": "BD999888778IN", "delivery_city": "Bangalore", "created_at": now()},
        {"_id": "ord-010", "account_id": "CUST-RING-010", "external_order_id": "ORD-RING-010", "product_sku": "LAPTOP-M1", "product_name": "Pro Laptop M1", "product_category": "ELECTRONICS", "order_amount": 89999.00, "currency": "INR", "ordered_at": now() - timedelta(days=2), "delivered_at": now() - timedelta(days=1), "carrier_name": "BlueDart", "tracking_number": "BD999888779IN", "delivery_city": "Bangalore", "created_at": now()},
        {"_id": "ord-011", "account_id": "CUST-RING-011", "external_order_id": "ORD-RING-011", "product_sku": "LAPTOP-M1", "product_name": "Pro Laptop M1", "product_category": "ELECTRONICS", "order_amount": 89999.00, "currency": "INR", "ordered_at": now() - timedelta(days=2), "delivered_at": now() - timedelta(days=1), "carrier_name": "BlueDart", "tracking_number": "BD999888780IN", "delivery_city": "Bangalore", "created_at": now()},
    ]
    
    # Generate 125 simulated orders
    for i in range(125):
        orders.append({
            "_id": f"ord-sim-{i}",
            "account_id": f"CUST-SIM-{i}",
            "external_order_id": f"ORD-SIM-{i}",
            "product_sku": "GEN-ITEM-01",
            "product_name": "Generic Apparel",
            "product_category": "APPAREL",
            "order_amount": float(random.randint(499, 1999)),
            "currency": "INR",
            "ordered_at": now() - timedelta(days=10),
            "delivered_at": now() - timedelta(days=7),
            "carrier_name": "Delhivery",
            "tracking_number": f"DL-SIM-{i}IN",
            "delivery_city": "Pune",
            "created_at": now()
        })
        
    for o in orders:
        name = o.get("product_name", "")
        if "Headphones" in name:
            o["product_image_url"] = "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=400&q=80"
        elif "Watch" in name:
            o["product_image_url"] = "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=400&q=80"
        elif "Phone" in name:
            o["product_image_url"] = "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=400&q=80"
        elif "Laptop" in name:
            o["product_image_url"] = "https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=400&q=80"
        elif "Dress" in name:
            o["product_image_url"] = "https://images.unsplash.com/photo-1515347619362-671398863fbe?w=400&q=80"
        elif "Sneakers" in name:
            o["product_image_url"] = "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=400&q=80"
        elif "iPhone" in name:
            o["product_image_url"] = "https://images.unsplash.com/photo-1696446701796-da61225697cc?w=400&q=80"
        elif "Coffee" in name:
            o["product_image_url"] = "https://images.unsplash.com/photo-1517668808822-9ebb02f2a0e6?w=400&q=80"
        elif "Keyboard" in name:
            o["product_image_url"] = "https://images.unsplash.com/photo-1595225476474-87563907a212?w=400&q=80"
        else:
            o["product_image_url"] = "https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=400&q=80"
            
    db[C.ORDERS].insert_many(orders)
    print(f"✅ Inserted {len(orders)} orders")

    # ── RETURN CLAIMS ─────────────────────────────────────
    claims = [
        {"_id": "CLM-DEMO-001", "account_id": "CUST-INNOCENT-001",
         "order_id": "ord-001", "claim_type": "DAMAGE",
         "status": "APPROVED", "fraud_score": 8, "fraud_tier": "TRUSTED",
         "recommended_action": "AUTO_APPROVE",
         "evidence": [{"signal": "NO_SIGNALS", "points": 0}],
         "explainability_text": "Your return has been approved. Refund of ₹3,499 will be credited within 3-5 business days.",
         "consent_given": True, "device_fingerprint": "fp-innocent-device-001",
         "created_at": now() - timedelta(hours=2), "updated_at": now()},

        {"_id": "CLM-DEMO-002", "account_id": "CUST-FRAUDSTER-002",
         "order_id": "ord-002", "claim_type": "INR",
         "status": "UNDER_REVIEW", "fraud_score": 82, "fraud_tier": "HIGH_RISK",
         "recommended_action": "ESCALATE",
         "evidence": [
             {"signal": "IMAGE_ELA", "points": 20, "detail": "Localized editing detected in bottom-right quadrant"},
             {"signal": "EXIF_DATE_MISMATCH", "points": 15, "detail": "Photo taken 3 days before purchase date"},
             {"signal": "RECEIPT_AMOUNT_MISMATCH", "points": 20, "detail": "Receipt: ₹2,999 vs Order: ₹4,599 (35% variance)"},
             {"signal": "SHARED_DEVICE_FINGERPRINT", "points": 15, "detail": "Device fingerprint shared with 2 other accounts"},
             {"signal": "HIGH_INR_RATE", "points": 12, "detail": "4 INR claims in last 90 days (threshold: 2)"},
         ],
         "explainability_text": "We need a bit more information. Our team will contact you within 24 hours.",
         "consent_given": True, "device_fingerprint": "fp-shared-device-ring",
         "created_at": now() - timedelta(hours=1), "updated_at": now()},

        {"_id": "CLM-2024-0041", "account_id": "CUST-RING-003",
         "order_id": "ord-003", "claim_type": "INR",
         "status": "ESCALATED", "fraud_score": 92, "fraud_tier": "HIGH_RISK",
         "recommended_action": "ESCALATE",
         "evidence": [
             {"signal": "IMAGE_ELA", "points": 25, "detail": "Image Exif data altered and clone stamp detected on package label"},
             {"signal": "RECEIPT_FORGERY", "points": 15, "detail": "Receipt font mismatch. Tax amount mathematically incorrect"},
             {"signal": "CARRIER_DELIVERED", "points": 25, "detail": "Carrier confirmed delivery at 14:32 IST via GPS ping"},
             {"signal": "FRAUD_RING_MEMBER", "points": 40, "detail": "Member of RING-0001: Mumbai Fast Return Cluster"},
             {"signal": "SHARED_DEVICE_FINGERPRINT", "points": 15, "detail": "Device shared with 3 ring accounts"},
             {"signal": "HIGH_INR_RATE", "points": 12, "detail": "Ring burst: 5 claims in 3-hour window"},
         ],
         "consent_given": True, "device_fingerprint": "fp-shared-device-ring",
         "created_at": now() - timedelta(minutes=2), "updated_at": now()},

        {"_id": "CLM-XAI-MASTER", "account_id": "CUST-RING-009",
         "order_id": "ord-004", "claim_type": "DAMAGE",
         "status": "ESCALATED", "fraud_score": 100, "fraud_tier": "HIGH_RISK",
         "recommended_action": "BLOCK",
         "evidence": [
             {"signal": "IMAGE_ELA", "points": 25, "detail": "Metadata stripped and pixels cloned in bottom-left corner"},
             {"signal": "RECEIPT_FORGERY", "points": 30, "detail": "Font mismatch in total amount. Detected ₹4,999 vs Order ₹1,999"},
             {"signal": "HIGH_INR_RATE", "points": 15, "detail": "3rd INR claim in 14 days across shared devices"},
             {"signal": "CARRIER_DELIVERED", "points": 10, "detail": "Carrier GPS ping confirmed delivery at customer address at 14:02 IST"},
             {"signal": "FRAUD_RING_MEMBER", "points": 20, "detail": "Confirmed mule node in Bangalore Electronics Scam ring (RING-0005)"},
         ],
         "consent_given": True, "device_fingerprint": "fp-bangalore-scam-dev1",
         "created_at": now() - timedelta(minutes=10), "updated_at": now()},

        {"_id": "CLM-2024-0042", "account_id": "CUST-RING-004", "order_id": "ord-005", "claim_type": "INR", "status": "ESCALATED", "fraud_score": 85, "fraud_tier": "HIGH_RISK", "recommended_action": "ESCALATE", "evidence": [{"signal": "FRAUD_RING_MEMBER", "points": 30, "detail": "Member of RING-0001"}], "consent_given": True, "device_fingerprint": "fp-shared-device-ring", "created_at": now() - timedelta(minutes=5), "updated_at": now()},
        {"_id": "CLM-2024-0043", "account_id": "CUST-RING-005", "order_id": "ord-006", "claim_type": "INR", "status": "ESCALATED", "fraud_score": 88, "fraud_tier": "HIGH_RISK", "recommended_action": "ESCALATE", "evidence": [{"signal": "FRAUD_RING_MEMBER", "points": 35, "detail": "Member of RING-0001"}], "consent_given": True, "device_fingerprint": "fp-shared-device-ring", "created_at": now() - timedelta(minutes=1), "updated_at": now()},
        {"_id": "CLM-2024-0044", "account_id": "CUST-007", "order_id": "ord-007", "claim_type": "DAMAGE", "status": "APPROVED", "fraud_score": 12, "fraud_tier": "TRUSTED", "recommended_action": "AUTO_APPROVE", "evidence": [], "explainability_text": "Refund approved.", "consent_given": True, "device_fingerprint": "fp-device-007", "created_at": now() - timedelta(hours=3), "updated_at": now()},
        {"_id": "CLM-2024-0045", "account_id": "CUST-012", "order_id": "ord-008", "claim_type": "DAMAGE", "status": "APPROVED", "fraud_score": 5, "fraud_tier": "TRUSTED", "recommended_action": "AUTO_APPROVE", "evidence": [], "explainability_text": "Refund approved.", "consent_given": True, "device_fingerprint": "fp-device-012", "created_at": now() - timedelta(hours=4), "updated_at": now()},
        {"_id": "CLM-2024-0046", "account_id": "CUST-RING-008", "order_id": "ord-009", "claim_type": "DAMAGE", "status": "ESCALATED", "fraud_score": 95, "fraud_tier": "HIGH_RISK", "recommended_action": "BLOCK", "evidence": [{"signal": "FRAUD_RING_MEMBER", "points": 45, "detail": "Member of RING-0005"}], "consent_given": True, "device_fingerprint": "fp-bangalore-scam-dev1", "created_at": now() - timedelta(minutes=8), "updated_at": now()},
        {"_id": "CLM-2024-0047", "account_id": "CUST-RING-010", "order_id": "ord-010", "claim_type": "DAMAGE", "status": "ESCALATED", "fraud_score": 91, "fraud_tier": "HIGH_RISK", "recommended_action": "BLOCK", "evidence": [{"signal": "FRAUD_RING_MEMBER", "points": 40, "detail": "Member of RING-0005"}], "consent_given": True, "device_fingerprint": "fp-bangalore-scam-dev1", "created_at": now() - timedelta(minutes=15), "updated_at": now()},
        {"_id": "CLM-2024-0048", "account_id": "CUST-RING-011", "order_id": "ord-011", "claim_type": "DAMAGE", "status": "UNDER_REVIEW", "fraud_score": 75, "fraud_tier": "HIGH_RISK", "recommended_action": "ESCALATE", "evidence": [{"signal": "FRAUD_RING_MEMBER", "points": 30, "detail": "Member of RING-0005"}], "consent_given": True, "device_fingerprint": "fp-bangalore-scam-dev1", "created_at": now() - timedelta(minutes=20), "updated_at": now()},
    ]
    
    # Generate 125 simulated innocent claims
    for i in range(125):
        claims.append({
            "_id": f"CLM-SIM-2024-{i:04d}",
            "account_id": f"CUST-SIM-{i}",
            "order_id": f"ord-sim-{i}",
            "claim_type": "CHANGE_OF_MIND",
            "status": "APPROVED",
            "fraud_score": random.randint(1, 9),
            "fraud_tier": "TRUSTED",
            "recommended_action": "AUTO_APPROVE",
            "evidence": [],
            "explainability_text": "Refund approved automatically based on strong account history.",
            "consent_given": True,
            "device_fingerprint": f"fp-sim-dev-{i}",
            "created_at": now() - timedelta(hours=random.randint(1, 24), minutes=random.randint(0, 59)),
            "updated_at": now()
        })
        
    db[C.RETURN_CLAIMS].insert_many(claims)
    print(f"✅ Inserted {len(claims)} return claims")

    # ── BEHAVIORAL SCORES ─────────────────────────────────
    behavioral = [
        {"account_id": "a1-innocent-001", "total_orders": 47, "total_returns": 2,
         "return_rate_lifetime": 0.04, "inr_claim_count_90d": 0,
         "wardrobing_score": 0.0, "risk_percentile": 0.05,
         "behavioral_risk_score": 5, "computed_at": now()},

        {"account_id": "a2-fraudster-002", "total_orders": 2, "total_returns": 2,
         "return_rate_lifetime": 1.0, "inr_claim_count_90d": 4,
         "wardrobing_score": 0.85, "risk_percentile": 0.98,
         "behavioral_risk_score": 27, "computed_at": now()},

        {"account_id": "a3-ring-003", "total_orders": 1, "total_returns": 1,
         "return_rate_lifetime": 1.0, "inr_claim_count_90d": 3,
         "wardrobing_score": 0.0, "risk_percentile": 0.99,
         "behavioral_risk_score": 30, "computed_at": now()},
    ]
    db[C.BEHAVIORAL_SCORES].insert_many(behavioral)
    print(f"✅ Inserted {len(behavioral)} behavioral scores")

    # ── ENTITY RELATIONSHIPS (Fraud Ring Graph) ───────────
    relations = [
        # Ring device sharing
        {"entity_a_type": "account", "entity_a_id": "CUST-RING-003",
         "relationship": "USES_DEVICE", "entity_b_type": "device",
         "entity_b_id": "fp-shared-device-ring", "risk_weight": 1.0,
         "first_seen": now() - timedelta(days=14), "last_seen": now(), "occurrence_count": 3},

        {"entity_a_type": "account", "entity_a_id": "CUST-RING-004",
         "relationship": "USES_DEVICE", "entity_b_type": "device",
         "entity_b_id": "fp-shared-device-ring", "risk_weight": 1.0,
         "first_seen": now() - timedelta(days=12), "last_seen": now(), "occurrence_count": 2},

        {"entity_a_type": "account", "entity_a_id": "CUST-FRAUDSTER-002",
         "relationship": "USES_DEVICE", "entity_b_type": "device",
         "entity_b_id": "fp-shared-device-ring", "risk_weight": 1.0,
         "first_seen": now() - timedelta(days=10), "last_seen": now(), "occurrence_count": 1},

        # Ring address sharing
        {"entity_a_type": "account", "entity_a_id": "CUST-RING-003",
         "relationship": "SHARES_ADDRESS", "entity_b_type": "address",
         "entity_b_id": "addr-mumbai-shared-001", "risk_weight": 0.9,
         "first_seen": now() - timedelta(days=14), "last_seen": now(), "occurrence_count": 4},

        {"entity_a_type": "account", "entity_a_id": "CUST-RING-004",
         "relationship": "SHARES_ADDRESS", "entity_b_type": "address",
         "entity_b_id": "addr-mumbai-shared-001", "risk_weight": 0.9,
         "first_seen": now() - timedelta(days=12), "last_seen": now(), "occurrence_count": 3},

        {"entity_a_type": "account", "entity_a_id": "CUST-RING-005",
         "relationship": "SHARES_ADDRESS", "entity_b_type": "address",
         "entity_b_id": "addr-mumbai-shared-001", "risk_weight": 0.9,
         "first_seen": now() - timedelta(days=9), "last_seen": now(), "occurrence_count": 2},

        {"entity_a_type": "account", "entity_a_id": "CUST-011Y",
         "relationship": "SHARES_ADDRESS", "entity_b_type": "address",
         "entity_b_id": "addr-mumbai-shared-001", "risk_weight": 0.8,
         "first_seen": now() - timedelta(days=5), "last_seen": now(), "occurrence_count": 1},

        # New Ring 0005 Relations (Device Sharing)
        {"entity_a_type": "account", "entity_a_id": "CUST-RING-008",
         "relationship": "USES_DEVICE", "entity_b_type": "device",
         "entity_b_id": "fp-bangalore-scam-dev1", "risk_weight": 1.0,
         "first_seen": now() - timedelta(days=12), "last_seen": now(), "occurrence_count": 4},

        {"entity_a_type": "account", "entity_a_id": "CUST-RING-009",
         "relationship": "USES_DEVICE", "entity_b_type": "device",
         "entity_b_id": "fp-bangalore-scam-dev1", "risk_weight": 1.0,
         "first_seen": now() - timedelta(days=11), "last_seen": now(), "occurrence_count": 3},

        {"entity_a_type": "account", "entity_a_id": "CUST-RING-010",
         "relationship": "USES_DEVICE", "entity_b_type": "device",
         "entity_b_id": "fp-bangalore-scam-dev1", "risk_weight": 1.0,
         "first_seen": now() - timedelta(days=10), "last_seen": now(), "occurrence_count": 2},

        {"entity_a_type": "account", "entity_a_id": "CUST-RING-011",
         "relationship": "USES_DEVICE", "entity_b_type": "device",
         "entity_b_id": "fp-bangalore-scam-dev2", "risk_weight": 0.9,
         "first_seen": now() - timedelta(days=5), "last_seen": now(), "occurrence_count": 1},

        # IP Sharing between devices in the ring
        {"entity_a_type": "account", "entity_a_id": "CUST-RING-008",
         "relationship": "SHARES_IP", "entity_b_type": "ip",
         "entity_b_id": "192.168.1.100", "risk_weight": 0.85,
         "first_seen": now() - timedelta(days=12), "last_seen": now(), "occurrence_count": 5},

        {"entity_a_type": "account", "entity_a_id": "CUST-RING-011",
         "relationship": "SHARES_IP", "entity_b_type": "ip",
         "entity_b_id": "192.168.1.100", "risk_weight": 0.85,
         "first_seen": now() - timedelta(days=5), "last_seen": now(), "occurrence_count": 2},
    ]
    db[C.ENTITY_RELATIONS].insert_many(relations)
    print(f"✅ Inserted {len(relations)} entity relationships")

    # ── FRAUD RINGS ───────────────────────────────────────
    rings = [
        {"_id": "RING-0001", "ring_name": "Mumbai Fast Return Cluster",
         "status": "CONFIRMED", "member_count": 7,
         "total_claimed_value": 187400, "total_prevented_value": 124000,
         "detection_algorithm": "Louvain + PageRank", "confidence_score": 0.97,
         "first_detected_at": datetime(2024, 6, 14, tzinfo=timezone.utc),
         "ring_metadata": {"shared_devices": 3, "shared_addresses": 4, "city": "Mumbai"}},

        {"_id": "RING-0002", "ring_name": "Delhi INR Syndicate",
         "status": "ACTIVE", "member_count": 4,
         "total_claimed_value": 62300, "total_prevented_value": 41000,
         "detection_algorithm": "Louvain", "confidence_score": 0.84,
         "first_detected_at": datetime(2024, 6, 18, tzinfo=timezone.utc),
         "ring_metadata": {"shared_devices": 2, "shared_addresses": 2, "city": "Delhi"}},

        {"_id": "RING-0003", "ring_name": "Wardrobing Cluster Alpha",
         "status": "UNDER_INVESTIGATION", "member_count": 5,
         "total_claimed_value": 44750, "total_prevented_value": 18000,
         "detection_algorithm": "Temporal Burst", "confidence_score": 0.71,
         "first_detected_at": datetime(2024, 6, 21, tzinfo=timezone.utc),
         "ring_metadata": {"category": "FASHION", "avg_return_days": 3}},

        {"_id": "RING-0004", "ring_name": "Refund Abuse Group",
         "status": "ACTIVE", "member_count": 3,
         "total_claimed_value": 31200, "total_prevented_value": 14200,
         "detection_algorithm": "Community Detection", "confidence_score": 0.68,
         "first_detected_at": datetime(2024, 6, 22, tzinfo=timezone.utc),
         "ring_metadata": {"shared_devices": 1, "shared_addresses": 3}},

        {"_id": "RING-0005", "ring_name": "Bangalore Electronics Scam",
         "status": "CONFIRMED", "member_count": 4,
         "total_claimed_value": 125000, "total_prevented_value": 85000,
         "detection_algorithm": "Graph Neural Network", "confidence_score": 0.94,
         "first_detected_at": datetime(2024, 7, 10, tzinfo=timezone.utc),
         "ring_metadata": {"shared_devices": 2, "shared_ips": 1, "city": "Bangalore"}},
    ]
    db[C.FRAUD_RINGS].insert_many(rings)
    print(f"✅ Inserted {len(rings)} fraud rings")

    # ── RING MEMBERS ──────────────────────────────────────
    members = [
        {"ring_id": "RING-0001", "account_id": "CUST-RING-003", "role": "RING_LEADER", "centrality_score": 0.95, "added_at": now()},
        {"ring_id": "RING-0001", "account_id": "CUST-RING-004", "role": "MULE",        "centrality_score": 0.72, "added_at": now()},
        {"ring_id": "RING-0001", "account_id": "CUST-RING-005", "role": "MULE",        "centrality_score": 0.68, "added_at": now()},
        {"ring_id": "RING-0001", "account_id": "CUST-007X",     "role": "MEMBER",      "centrality_score": 0.55, "added_at": now()},
        {"ring_id": "RING-0001", "account_id": "CUST-009X",     "role": "MEMBER",      "centrality_score": 0.50, "added_at": now()},
        {"ring_id": "RING-0001", "account_id": "CUST-011Y",     "role": "MEMBER",      "centrality_score": 0.48, "added_at": now()},
        {"ring_id": "RING-0001", "account_id": "CUST-013Z",     "role": "SUSPECTED",   "centrality_score": 0.40, "added_at": now()},

        {"ring_id": "RING-0005", "account_id": "CUST-RING-008", "role": "RING_LEADER", "centrality_score": 0.92, "added_at": now()},
        {"ring_id": "RING-0005", "account_id": "CUST-RING-009", "role": "MULE",        "centrality_score": 0.78, "added_at": now()},
        {"ring_id": "RING-0005", "account_id": "CUST-RING-010", "role": "MULE",        "centrality_score": 0.75, "added_at": now()},
        {"ring_id": "RING-0005", "account_id": "CUST-RING-011", "role": "MEMBER",      "centrality_score": 0.65, "added_at": now()},
    ]
    db[C.RING_MEMBERS].insert_many(members)
    print(f"✅ Inserted {len(members)} ring members")

    # ── AUDIT LOG ─────────────────────────────────────────
    audit_entries = [
        {"entity_type": "return_claim", "entity_id": "CLM-DEMO-001",
         "action": "CLAIM_SUBMITTED", "actor_type": "CUSTOMER",
         "actor_id": "a1-innocent-001", "metadata": {"channel": "customer_portal"},
         "created_at": now() - timedelta(hours=2)},

        {"entity_type": "return_claim", "entity_id": "CLM-DEMO-001",
         "action": "FRAUD_SCORE_COMPUTED", "actor_type": "SYSTEM",
         "actor_id": None, "metadata": {"score": 8, "tier": "TRUSTED", "latency_ms": 2800},
         "created_at": now() - timedelta(hours=2, minutes=-2)},

        {"entity_type": "return_claim", "entity_id": "CLM-DEMO-001",
         "action": "AUTO_APPROVED", "actor_type": "SYSTEM",
         "actor_id": None, "metadata": {"reason": "TRUSTED_tier_auto_approval"},
         "created_at": now() - timedelta(hours=2, minutes=-3)},

        {"entity_type": "return_claim", "entity_id": "CLM-DEMO-002",
         "action": "CLAIM_SUBMITTED", "actor_type": "CUSTOMER",
         "actor_id": "a2-fraudster-002", "metadata": {"channel": "customer_portal"},
         "created_at": now() - timedelta(hours=1)},

        {"entity_type": "return_claim", "entity_id": "CLM-DEMO-002",
         "action": "FRAUD_SCORE_COMPUTED", "actor_type": "SYSTEM",
         "actor_id": None, "metadata": {"score": 82, "tier": "HIGH_RISK", "latency_ms": 3200},
         "created_at": now() - timedelta(minutes=58)},

        {"entity_type": "return_claim", "entity_id": "CLM-DEMO-002",
         "action": "ESCALATED", "actor_type": "SYSTEM",
         "actor_id": None, "metadata": {"reason": "HIGH_RISK_tier_auto_escalation"},
         "created_at": now() - timedelta(minutes=57)},

        {"entity_type": "fraud_ring", "entity_id": "RING-0001",
         "action": "RING_CONFIRMED", "actor_type": "SYSTEM",
         "actor_id": None, "metadata": {"algorithm": "Louvain+PageRank", "members": 7, "confidence": 0.97},
         "created_at": now() - timedelta(days=15)},
    ]
    db[C.AUDIT_LOG].insert_many(audit_entries)
    print(f"✅ Inserted {len(audit_entries)} audit log entries")

    print("\n🎉 MongoDB seed complete! Collections populated:")
    for col in [C.ACCOUNTS, C.ORDERS, C.RETURN_CLAIMS, C.BEHAVIORAL_SCORES,
                C.ENTITY_RELATIONS, C.FRAUD_RINGS, C.RING_MEMBERS, C.AUDIT_LOG]:
        count = get_db()[col].count_documents({})
        print(f"   {col}: {count} documents")


if __name__ == "__main__":
    seed()
