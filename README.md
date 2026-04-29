# 🛡️ TriNetra AI v3.0 — Production Fraud Intelligence Platform

> **Zero paid dependencies. 100% open-source. DPDPA 2023 compliant.**

TriNetra AI is a production-grade, multi-layered return-fraud detection system for high-volume e-commerce platforms. It protects against image manipulation, receipt forgery, INR abuse, wardrobing, and coordinated fraud ring attacks — while ensuring frictionless approvals for the **94% of legitimate customers**.

---

## 🏗️ Architecture

```
Customer Portal (Vite:5174)  →  Return API (Spring Boot:8085)  →  Kafka (Redpanda:9092)
                                                                          ↓
Admin Dashboard (Vite:5173)  ←  DB (PostgreSQL:5433)  ←  Celery Workers (image/receipt/carrier/graph)
                                                              ↑
                                               Fraud Engine (FastAPI:8000)
                                               Graph Service (FastAPI:8001)
```

### Open-Source Stack
| Component | Technology |
|---|---|
| API Gateway | Traefik v3 |
| Return API | Spring Boot 3.2 / Java 21 |
| Fraud Engine | FastAPI / Python 3.11 |
| Graph Service | FastAPI + NetworkX (Louvain) |
| Async Workers | Celery + Redis |
| Message Queue | Redpanda (Kafka-compatible) |
| Database | PostgreSQL 16 |
| Object Storage | MinIO (S3-compatible) |
| OCR | Tesseract 5 + PyMuPDF |
| Visual AI | HuggingFace CLIP (local inference) |
| Image Forensics | PIL/Pillow (ELA), piexif, imagehash |
| Monitoring | Prometheus + Grafana |
| Frontend | React 18 + Vite + D3.js |

---

## 🚀 Quick Start

### Step 1 — Start Infrastructure

```powershell
# Full production stack (all services)
docker-compose -f infrastructure/docker-compose.yml up -d

# OR minimal dev (just postgres + redis)
docker-compose up -d
```

### Step 2 — Set Environment Variables

```powershell
# Copy the template
copy .env.example .env

# OR use the PowerShell startup script (sets all vars automatically)
.\start_services.ps1
```

### Step 3 — Start Python Services

```powershell
# Set PYTHONPATH to resolve cross-service imports
$env:PYTHONPATH = "services\common;services\fraud-engine;services\workers"

# Fraud Engine (port 8000)
cd services\fraud-engine
uvicorn main:app --port 8000 --host 0.0.0.0 --reload

# Graph Service (port 8001)
cd services\graph-service
uvicorn main:app --port 8001 --host 0.0.0.0 --reload

# Celery Workers (in services\ directory)
cd services
celery -A workers.celery_app worker -Q image,receipt,carrier,behavioral,graph,aggregator --loglevel=info

# Kafka Consumer Bridge
cd services\fraud-engine
python kafka_consumer.py
```

### Step 4 — Start Return API (Spring Boot)

```powershell
cd services\return-api
mvn spring-boot:run
# API available at http://localhost:8085
```

### Step 5 — Start Frontend Apps

```powershell
# Admin Dashboard (port 5173)
cd dashboard
npm install
npm run dev

# Customer Portal (port 5174)
cd customer-portal
npm install
npm run dev
```

---

## 🔗 Service URLs

| Service | URL | Description |
|---|---|---|
| Admin Dashboard | http://localhost:5173 | Intelligence Center, Claims Queue, Fraud Rings |
| Customer Portal | http://localhost:5174 | Submit & Track Returns |
| Return API | http://localhost:8085 | Spring Boot REST API |
| Fraud Engine | http://localhost:8000/docs | FastAPI Swagger UI |
| Graph Service | http://localhost:8001/docs | Graph Intelligence API |
| Grafana | http://localhost:3001 | Monitoring (admin/admin) |
| Prometheus | http://localhost:9090 | Metrics scraper |
| MinIO Console | http://localhost:9001 | Object storage (trinetra/trinetra_dev_secret) |
| Redpanda Console | http://localhost:8081 | Kafka topics viewer |
| Traefik Dashboard | http://localhost:8090 | API gateway |

---

## 🕵️ Fraud Detection Stack

### 1. Image Forensics (`services/common/ml/`)
- **ELA (Error Level Analysis)** — detects pixel-level editing via JPEG re-compression delta
- **EXIF Metadata** — flags photos taken before purchase date, missing GPS in damage claims
- **pHash (Perceptual Hash)** — detects recycled images reused across multiple claims
- **CLIP Similarity** — compares returned item vs. official product catalog image

### 2. Document AI
- **Tesseract OCR** — extracts amount, date, SKU from receipt images
- **PyMuPDF** — detects suspicious font layers in PDF receipts (text replacement)

### 3. Behavioral Analytics
- Return rate percentile (vs. category peers)
- INR claim frequency (90-day window)
- Wardrobing score (purchase-to-return timing)
- Chargeback history

### 4. Graph Intelligence (`services/graph-service/`)
- **Louvain community detection** — finds fraud rings from shared entity clusters
- **PageRank** — identifies ring leaders vs. mules
- **Temporal burst detection** — coordinated claims in 3-hour windows
- Shared device fingerprint, IP cluster, address sharing

### 5. Carrier Validation
- Delivery confirmation cross-check for INR claims
- Scan history city mismatch detection
- Proof of delivery photo availability

---

## 📊 Fraud Score Tiers

| Score | Tier | Action |
|---|---|---|
| 0–29 | 🟢 TRUSTED | Auto-approve (no human needed) |
| 30–59 | 🟡 CAUTION | Request additional photo |
| 60–79 | 🟠 ELEVATED_RISK | Queue for human review (24hr SLA) |
| 80–100 | 🔴 HIGH_RISK | Escalate to senior reviewer (4hr SLA) |

---

## ⚖️ Compliance (DPDPA 2023)

The following compliance rules are enforced at **startup** — the service will not start if any are violated:

| Rule | Status |
|---|---|
| All PII is SHA-256 hashed — no plaintext storage | ✅ Enforced |
| Social media scraping disabled | ✅ `SOCIAL_MEDIA_SCRAPING_ENABLED=false` |
| Biometric processing requires explicit KYC consent | ✅ `BIOMETRIC_PROCESSING_ENABLED=false` |
| Auto-blocking accounts disabled (Consumer Protection Act) | ✅ `AUTO_BLOCK_ENABLED=false` |
| Fraud score never exposed to customer | ✅ `CUSTOMER_SCORE_EXPOSED=false` |
| Customer Right to Explanation | ✅ `GET /api/v1/returns/{id}/explanation` |
| Immutable audit log (DELETE/UPDATE revoked) | ✅ PostgreSQL rules enforced |
| Data retention capped at 24 months | ✅ `DATA_RETENTION_DAYS=730` |

---

## 🧪 Demo Scenarios

| Scenario | Account ID | Expected Score | Trigger |
|---|---|---|---|
| Legitimate customer | `CUST-INNOCENT-001` | 0–15 | Auto-approved in seconds |
| Fraudulent claim | `CUST-FRAUDSTER-002` | 65–80 | Elevated risk, queued for review |
| Fraud ring member | `CUST-RING-003` | 85–99 | High risk, escalated |
| Track return | Portal: `CLM-DEMO-001` | — | Approved status |
| Track review | Portal: `CLM-DEMO-002` | — | Under review status |

---

## 📁 Project Structure

```
trinetra-ai/
├── services/
│   ├── fraud-engine/         # FastAPI — scoring, ELA, EXIF, CLIP, OCR, compliance
│   ├── graph-service/        # FastAPI — ring detection, D3-ready graph API
│   ├── return-api/           # Spring Boot 3.2 — submit/track returns, Kafka publish
│   ├── workers/              # Celery — image, receipt, carrier, behavioral, graph, aggregator
│   └── common/ml/            # Shared ML modules (ELA, CLIP, pHash, OCR, EXIF)
├── dashboard/                # React 18 + Vite — admin intelligence center
├── customer-portal/          # React 18 + Vite — customer submit & track
├── infrastructure/
│   ├── docker-compose.yml    # Full production stack
│   ├── postgres/init.sql     # Complete schema + seed data
│   └── monitoring/
│       └── prometheus.yml    # Scrape configs for all services
├── docker-compose.yml        # Dev quickstart (postgres + redis only)
├── .env.example              # All environment variables documented
├── start_services.ps1        # Windows PowerShell startup script
└── README.md                 # This file
```

---

*TriNetra AI — Securing the Future of E-commerce Returns through Intelligence and Trust.*
*Built with: PostgreSQL · Redis · Redpanda · MinIO · FastAPI · Spring Boot · NetworkX · HuggingFace CLIP · Tesseract · PyMuPDF · D3.js · Celery · Prometheus · Grafana · Traefik*
