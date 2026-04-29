CREATE TYPE process_status AS ENUM ('COMPLETED', 'FAILED_NO_FACE', 'FAILED_DOWNLOAD', 'SKIPPED_PRIVATE');
CREATE TYPE decision_action AS ENUM ('FRAUD_LIKELY', 'MANUAL_REVIEW', 'FACE_EVIDENCE_IGNORED');

CREATE TABLE returns_claims (
    id VARCHAR(50) PRIMARY KEY,
    status VARCHAR(50)
);

CREATE TABLE face_recognition_results (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    claim_id VARCHAR(50) NOT NULL,
    user_id VARCHAR(50) NOT NULL,
    registered_image_cloudinary_url VARCHAR(255) NOT NULL,
    social_image_cloudinary_url VARCHAR(255),
    similarity_score DECIMAL(5,4),
    status process_status NOT NULL,
    decision decision_action NOT NULL,
    enforce_detection_used BOOLEAN DEFAULT FALSE,
    error_reason TEXT,
    reviewed_by VARCHAR(50),
    reviewed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT fk_claim FOREIGN KEY(claim_id) REFERENCES returns_claims(id)
);
