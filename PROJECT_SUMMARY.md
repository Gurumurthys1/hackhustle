# 🛡️ TriNetra AI v3.0 — Production-Grade Fraud Intelligence

**TriNetra AI** is a state-of-the-art, legally compliant, and ethically sound return & refund fraud detection platform. Built for high-volume e-commerce, it transforms return management from a loss center into a **Trust Engine**.

---

## 💎 The "Trust Engine" Philosophy
The system prioritizes the **97% of legitimate customers**, providing a frictionless, instant-approval experience, while silently identifying the **3% of fraudulent attempts** using multi-layered AI forensics and Graph Intelligence.

### ⚖️ Legal & Ethical Mandate (DPDPA 2023 / GDPR)
- ✅ **Zero Unauthorized Scraping**: Social media scraping is strictly banned.
- ✅ **Privacy by Design**: All PII is hashed; biometric data is only used with explicit KYC consent.
- ✅ **Right to Explanation**: Customers can request and receive clear reasons for flagged returns.
- ✅ **Human-in-the-Loop**: Automated decisions never exceed 60 points; senior admins review high-risk cases.

---

## 🚀 Technical Architecture (100% Open Source)
TriNetra AI utilizes a high-performance, asynchronous microservices architecture with zero paid dependencies.

- **Return API (Spring Boot 3.x / Java 21)**: High-speed orchestrator with Redpanda (Kafka) event publishing.
- **Fraud Engine (FastAPI / Python 3.11)**: Parallel ML pipeline (ELA, CLIP, EXIF, pHash, OCR).
- **Graph Service (FastAPI / NetworkX)**: Real-time community detection and fraud ring identification.
- **Workers (Celery / Redis)**: Horizontally scalable forensics workers.
- **Infrastructure**: PostgreSQL (Audit Log + Behavioral), MinIO (S3-compatible), Prometheus & Grafana.

---

## 🕵️‍♂️ Detection Stack
1.  **Image Forensics**: Error Level Analysis (ELA) and EXIF metadata validation.
2.  **Visual AI**: HuggingFace CLIP for semantic catalog-to-claim comparison.
3.  **Document AI**: Tesseract-based OCR with PDF font layer forensics.
4.  **Behavioral Analytics**: scikit-learn models for INR abuse and wardrobing patterns.
5.  **Graph Intelligence**: D3.js visualizations of shared entities and coordinated ring attacks.

---

## 📊 Dashboard Modules
- **Live Intelligence Center**: Real-time histogram of fraud scores and system throughput.
- **Fraud Ring Graph**: Interactive force-directed graph showing connected suspicious accounts.
- **Claims Queue**: Multi-tier review system (Trusted | Caution | Elevated | High Risk).
- **Audit Vault**: Immutable DPDPA-compliant log of every system and admin decision.

---

## 🔧 Production Startup
```bash
# 1. Start Infrastructure
docker-compose up -d

# 2. Start AI Services
cd services/fraud-engine && uvicorn main:app --port 8000
cd services/graph-service && uvicorn main:app --port 8001

# 3. Start Workers
celery -A celery_app worker --loglevel=info

# 4. Start API & Dashboards
cd services/return-api && mvn spring-boot:run
cd dashboard && npm run dev
```

*TriNetra AI — Securing the Future of E-commerce Returns through Intelligence and Trust.*
