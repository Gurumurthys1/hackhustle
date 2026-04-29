-- infrastructure/postgres/init.sql

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";  -- For fuzzy text matching
CREATE EXTENSION IF NOT EXISTS "btree_gin"; -- For JSONB indexing

-- ── ACCOUNTS ────────────────────────────────────────────
CREATE TABLE accounts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    external_id VARCHAR(100) UNIQUE NOT NULL, -- ID from e-commerce platform
    email_hash VARCHAR(64) NOT NULL,           -- SHA-256 hashed, never plaintext
    phone_hash VARCHAR(64),
    account_age_days INTEGER DEFAULT 0,
    total_orders INTEGER DEFAULT 0,
    total_returns INTEGER DEFAULT 0,
    lifetime_order_value DECIMAL(14,2) DEFAULT 0,
    consent_given BOOLEAN DEFAULT FALSE,
    consent_timestamp TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ── ORDERS ──────────────────────────────────────────────
CREATE TABLE orders (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    account_id UUID NOT NULL REFERENCES accounts(id),
    external_order_id VARCHAR(100) UNIQUE NOT NULL,
    product_sku VARCHAR(100) NOT NULL,
    product_category VARCHAR(100) NOT NULL,
    product_name TEXT NOT NULL,
    order_amount DECIMAL(12,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'INR',
    ordered_at TIMESTAMPTZ NOT NULL,
    delivered_at TIMESTAMPTZ,
    carrier_name VARCHAR(50),
    tracking_number VARCHAR(100),
    delivery_address_hash VARCHAR(64), -- Hashed for privacy
    delivery_city VARCHAR(100),
    delivery_pincode VARCHAR(10),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ── RETURN CLAIMS (Core Table) ───────────────────────────
CREATE TABLE return_claims (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    account_id UUID NOT NULL REFERENCES accounts(id),
    order_id UUID NOT NULL REFERENCES orders(id),
    claim_type VARCHAR(50) NOT NULL 
        CHECK (claim_type IN ('DAMAGE','INR','WRONG_ITEM','QUALITY_ISSUE','CHANGE_OF_MIND')),
    status VARCHAR(30) NOT NULL DEFAULT 'SUBMITTED'
        CHECK (status IN ('SUBMITTED','PROCESSING','SCORED','UNDER_REVIEW',
                          'APPROVED','DENIED','ESCALATED','APPEALED')),
    description TEXT,
    fraud_score INTEGER CHECK (fraud_score BETWEEN 0 AND 100),
    fraud_tier VARCHAR(20) 
        CHECK (fraud_tier IN ('TRUSTED','CAUTION','ELEVATED_RISK','HIGH_RISK')),
    recommended_action VARCHAR(50),
    evidence JSONB DEFAULT '[]'::jsonb,
    explainability_text TEXT,
    reviewed_by UUID,
    reviewer_decision VARCHAR(20),
    reviewer_notes TEXT,
    review_started_at TIMESTAMPTZ,
    device_fingerprint VARCHAR(200),
    ip_address INET,
    user_agent TEXT,
    consent_given BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    resolved_at TIMESTAMPTZ
);

-- ── IMAGE FORENSICS RESULTS ──────────────────────────────
CREATE TABLE image_forensics_results (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    claim_id UUID NOT NULL REFERENCES return_claims(id) ON DELETE CASCADE,
    image_url TEXT NOT NULL,
    image_storage_key TEXT NOT NULL,       -- MinIO object key
    ela_score FLOAT,                        -- 0.0–1.0 manipulation probability
    ela_heatmap_key TEXT,                  -- MinIO key for heatmap image
    phash VARCHAR(64),                     -- 64-bit perceptual hash
    phash_match_claim_id UUID,             -- If recycled image detected
    phash_similarity FLOAT,               -- 0.0–1.0
    exif_capture_date DATE,
    exif_gps_lat FLOAT,
    exif_gps_lng FLOAT,
    exif_device_model VARCHAR(100),
    exif_missing BOOLEAN DEFAULT FALSE,
    clip_similarity_score FLOAT,           -- vs. product catalog image
    manipulation_detected BOOLEAN DEFAULT FALSE,
    defect_class VARCHAR(50),              -- From defect classifier
    defect_confidence FLOAT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ── RECEIPT VALIDATIONS ──────────────────────────────────
CREATE TABLE receipt_validations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    claim_id UUID NOT NULL REFERENCES return_claims(id) ON DELETE CASCADE,
    receipt_storage_key TEXT NOT NULL,
    receipt_type VARCHAR(10) CHECK (receipt_type IN ('IMAGE','PDF')),
    ocr_raw_text TEXT,
    ocr_extracted_amount DECIMAL(12,2),
    ocr_extracted_date DATE,
    ocr_extracted_sku TEXT,
    ocr_extracted_store TEXT,
    ocr_transaction_id TEXT,
    db_order_amount DECIMAL(12,2),
    amount_match BOOLEAN,
    amount_variance_pct FLOAT,
    date_in_window BOOLEAN,
    sku_match BOOLEAN,
    transaction_id_valid BOOLEAN,
    pdf_layer_count INTEGER,
    pdf_creation_date DATE,
    pdf_manipulation_detected BOOLEAN DEFAULT FALSE,
    thermal_pattern_valid BOOLEAN,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ── BEHAVIORAL SCORES ────────────────────────────────────
CREATE TABLE behavioral_scores (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    account_id UUID NOT NULL REFERENCES accounts(id),
    computed_at TIMESTAMPTZ DEFAULT NOW(),
    total_orders INTEGER DEFAULT 0,
    total_returns INTEGER DEFAULT 0,
    return_rate_30d FLOAT DEFAULT 0,
    return_rate_90d FLOAT DEFAULT 0,
    return_rate_lifetime FLOAT DEFAULT 0,
    inr_claim_count_90d INTEGER DEFAULT 0,
    chargeback_count_365d INTEGER DEFAULT 0,
    wardrobing_score FLOAT DEFAULT 0,
    account_age_days INTEGER DEFAULT 0,
    avg_order_value DECIMAL(12,2) DEFAULT 0,
    risk_percentile FLOAT DEFAULT 0,
    behavioral_risk_score INTEGER DEFAULT 0,
    UNIQUE(account_id)
);

-- ── CARRIER VALIDATIONS ──────────────────────────────────
CREATE TABLE carrier_validations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    claim_id UUID NOT NULL REFERENCES return_claims(id) ON DELETE CASCADE,
    order_id UUID NOT NULL REFERENCES orders(id),
    carrier_name VARCHAR(50),
    tracking_number VARCHAR(100),
    delivery_confirmed BOOLEAN,
    delivery_timestamp TIMESTAMPTZ,
    delivery_gps_lat FLOAT,
    delivery_gps_lng FLOAT,
    delivery_photo_url TEXT,
    pod_available BOOLEAN DEFAULT FALSE,
    scan_history JSONB DEFAULT '[]'::jsonb,
    api_response_raw JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ── ENTITY RELATIONSHIPS (Graph Mirror) ──────────────────
CREATE TABLE entity_relationships (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    entity_a_type VARCHAR(30) NOT NULL,
    entity_a_id TEXT NOT NULL,
    relationship VARCHAR(50) NOT NULL,
    entity_b_type VARCHAR(30) NOT NULL,
    entity_b_id TEXT NOT NULL,
    risk_weight FLOAT DEFAULT 1.0,
    first_seen TIMESTAMPTZ DEFAULT NOW(),
    last_seen TIMESTAMPTZ DEFAULT NOW(),
    occurrence_count INTEGER DEFAULT 1,
    UNIQUE(entity_a_id, relationship, entity_b_id)
);

-- ── FRAUD RINGS ──────────────────────────────────────────
CREATE TABLE fraud_rings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    ring_name VARCHAR(100),
    status VARCHAR(30) DEFAULT 'ACTIVE' 
        CHECK (status IN ('ACTIVE','UNDER_INVESTIGATION','CONFIRMED','CLOSED')),
    member_count INTEGER DEFAULT 0,
    total_claimed_value DECIMAL(14,2) DEFAULT 0,
    total_prevented_value DECIMAL(14,2) DEFAULT 0,
    detection_algorithm VARCHAR(50),
    confidence_score FLOAT,
    first_detected_at TIMESTAMPTZ DEFAULT NOW(),
    confirmed_at TIMESTAMPTZ,
    ring_metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE fraud_ring_members (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    ring_id UUID NOT NULL REFERENCES fraud_rings(id),
    account_id UUID NOT NULL REFERENCES accounts(id),
    role VARCHAR(30) DEFAULT 'MEMBER' 
        CHECK (role IN ('RING_LEADER','MULE','MEMBER','SUSPECTED')),
    centrality_score FLOAT,
    added_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(ring_id, account_id)
);

-- ── AUDIT LOG (IMMUTABLE) ────────────────────────────────
CREATE TABLE audit_log (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    entity_type VARCHAR(50) NOT NULL,
    entity_id UUID NOT NULL,
    action VARCHAR(100) NOT NULL,
    actor_type VARCHAR(20) NOT NULL CHECK (actor_type IN ('SYSTEM','ADMIN','CUSTOMER')),
    actor_id UUID,
    old_state JSONB,
    new_state JSONB,
    ip_address INET,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
-- CRITICAL: Revoke UPDATE and DELETE on audit_log
REVOKE UPDATE, DELETE ON audit_log FROM PUBLIC;
CREATE RULE no_update_audit AS ON UPDATE TO audit_log DO INSTEAD NOTHING;
CREATE RULE no_delete_audit AS ON DELETE TO audit_log DO INSTEAD NOTHING;

-- ── INDEXES ──────────────────────────────────────────────
CREATE INDEX idx_return_claims_account ON return_claims(account_id);
CREATE INDEX idx_return_claims_status ON return_claims(status);
CREATE INDEX idx_return_claims_fraud_score ON return_claims(fraud_score);
CREATE INDEX idx_return_claims_created ON return_claims(created_at DESC);
CREATE INDEX idx_entity_rel_a ON entity_relationships(entity_a_id, entity_a_type);
CREATE INDEX idx_entity_rel_b ON entity_relationships(entity_b_id, entity_b_type);
CREATE INDEX idx_behavioral_account ON behavioral_scores(account_id);
CREATE INDEX idx_audit_entity ON audit_log(entity_id, entity_type);
CREATE INDEX idx_audit_created ON audit_log(created_at DESC);

-- ── SEED DEMO DATA ───────────────────────────────────────
-- Insert demo scenarios for judge presentation
INSERT INTO accounts (id, external_id, email_hash, account_age_days, total_orders, consent_given, consent_timestamp)
VALUES 
  ('a1000000-0000-0000-0000-000000000001', 'CUST-INNOCENT-001', 'abc123hash', 1095, 47, true, NOW()),
  ('a2000000-0000-0000-0000-000000000002', 'CUST-FRAUDSTER-002', 'def456hash', 15, 2, true, NOW()),
  ('a3000000-0000-0000-0000-000000000003', 'CUST-RING-003', 'ghi789hash', 8, 1, true, NOW()),
  ('a4000000-0000-0000-0000-000000000004', 'CUST-RING-004', 'jkl012hash', 6, 1, true, NOW()),
  ('a5000000-0000-0000-0000-000000000005', 'CUST-RING-005', 'mno345hash', 9, 1, true, NOW());
