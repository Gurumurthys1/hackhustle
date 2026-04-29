"""
Runs on every service startup. Fails fast if compliance requirements not met.
This MUST pass before any fraud analysis runs.
"""
import os
import sys
import structlog

log = structlog.get_logger()

COMPLIANCE_REQUIREMENTS = [
    ("DATA_RETENTION_DAYS", "Fraud signal retention period must be configured (max 24 months)",
     lambda v: v and int(v) <= 730),
    
    ("CONSENT_REQUIRED", "Consent enforcement must be enabled", 
     lambda v: v and v.lower() == 'true'),
    
    ("AUDIT_LOG_IMMUTABLE", "Audit log immutability must be enabled",
     lambda v: v and v.lower() == 'true'),
    
    ("SOCIAL_MEDIA_SCRAPING_ENABLED", "Social media scraping must be DISABLED (illegal)",
     lambda v: v and v.lower() == 'false'),
    
    ("BIOMETRIC_PROCESSING_ENABLED", "Biometric processing must be DISABLED without explicit consent",
     lambda v: v and v.lower() == 'false'),
    
    ("AUTO_BLOCK_ENABLED", "Auto-blocking must be DISABLED (violates Consumer Protection Act)",
     lambda v: v and v.lower() == 'false'),
    
    ("CUSTOMER_SCORE_EXPOSED", "Customer fraud score exposure must be DISABLED",
     lambda v: v and v.lower() == 'false'),
]

def run_compliance_check():
    log.info("Running DPDPA compliance check...")
    failures = []
    
    for env_var, description, validator in COMPLIANCE_REQUIREMENTS:
        value = os.getenv(env_var)
        if value is None:
            failures.append(f"MISSING: {env_var} — {description}")
            continue
        try:
            if not validator(value):
                failures.append(f"VIOLATION: {env_var}={value} — {description}")
        except Exception as e:
            failures.append(f"ERROR: {env_var} validation failed — {str(e)}")
    
    if failures:
        print("\n" + "!" * 60)
        print("!!! COMPLIANCE CHECK FAILED — SERVICE WILL NOT START !!!")
        print("!" * 60)
        for f in failures:
            print(f" - {f}")
        print("!" * 60 + "\n")
        sys.exit(1)
    
    log.info("All DPDPA compliance checks passed. Service starting.")

if __name__ == "__main__":
    # Test run
    # Set mock env vars for testing
    os.environ["DATA_RETENTION_DAYS"] = "730"
    os.environ["CONSENT_REQUIRED"] = "true"
    os.environ["AUDIT_LOG_IMMUTABLE"] = "true"
    os.environ["SOCIAL_MEDIA_SCRAPING_ENABLED"] = "false"
    os.environ["BIOMETRIC_PROCESSING_ENABLED"] = "false"
    os.environ["AUTO_BLOCK_ENABLED"] = "false"
    os.environ["CUSTOMER_SCORE_EXPOSED"] = "false"
    run_compliance_check()
