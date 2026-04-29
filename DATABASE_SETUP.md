# TriNetra AI — Database Setup Guide

Two options depending on your setup. **Option A (Docker) is recommended** — easiest and most complete.

---

## Option A — Docker (Recommended, One Command)

### Step 1: Install Docker Desktop
Download from: https://www.docker.com/products/docker-desktop/
- Install → Restart PC → Make sure Docker Desktop is running (whale icon in taskbar)

### Step 2: Start the Database
Open PowerShell in the TriNetra AI folder and run:

```powershell
docker-compose up -d
```

This starts:
- **PostgreSQL 16** on port `5433`
- **Redis 7** on port `6379`

### Step 3: Schema is Auto-Applied
The `infrastructure/postgres/init.sql` file is automatically run when the container starts.
All 11 tables are created + demo accounts are seeded.

### Step 4: Verify It's Running
```powershell
docker exec -it trinetra-postgres psql -U trinetra -d trinetra_db -c "\dt"
```

You should see all tables listed:
```
 accounts
 audit_log
 behavioral_scores
 carrier_validations
 entity_relationships
 fraud_ring_members
 fraud_rings
 image_forensics_results
 orders
 receipt_validations
 return_claims
```

### Step 5: Check Seed Data
```powershell
docker exec -it trinetra-postgres psql -U trinetra -d trinetra_db -c "SELECT external_id, account_age_days FROM accounts;"
```

Should show:
```
    external_id     | account_age_days
--------------------+-----------------
 CUST-INNOCENT-001  |     1095
 CUST-FRAUDSTER-002 |       15
 CUST-RING-003      |        8
 CUST-RING-004      |        6
 CUST-RING-005      |        9
```

---

## Option B — PostgreSQL Installed Directly (No Docker)

### Step 1: Install PostgreSQL 16
Download from: https://www.postgresql.org/download/windows/
- During install: set password to `trinetra_dev_password`
- Port: `5432` (default)

### Step 2: Create the Database
Open pgAdmin or psql and run:

```sql
CREATE USER trinetra WITH PASSWORD 'trinetra_dev_password';
CREATE DATABASE trinetra_db OWNER trinetra;
GRANT ALL PRIVILEGES ON DATABASE trinetra_db TO trinetra;
```

### Step 3: Apply the Schema
In PowerShell:
```powershell
psql -U trinetra -d trinetra_db -f "infrastructure\postgres\init.sql"
```

Or in pgAdmin:
1. Open pgAdmin → Connect to trinetra_db
2. Click Query Tool
3. Open file: `infrastructure/postgres/init.sql`
4. Click Run (F5)

### Step 4: Update Your .env
Change the DB port from 5433 to 5432:
```
DATABASE_URL=postgresql://trinetra:trinetra_dev_password@localhost:5432/trinetra_db
```

---

## What Each Table Stores

| Table | What It Holds |
|---|---|
| `accounts` | Customer accounts with consent flag, hashed email/phone |
| `orders` | Order history — SKU, amount, delivery details |
| `return_claims` | Every return request + fraud score + evidence JSONB |
| `image_forensics_results` | ELA score, pHash, EXIF date, CLIP score per claim |
| `receipt_validations` | OCR extracted amount, PDF layer count, variance % |
| `behavioral_scores` | INR count, return rate, wardrobing score per account |
| `carrier_validations` | Delivery confirmation, scan history, POD status |
| `entity_relationships` | Graph edges (USES_DEVICE, SHARES_IP, etc.) |
| `fraud_rings` | Detected rings with confidence, value prevented |
| `fraud_ring_members` | Which accounts belong to which ring + their role |
| `audit_log` | IMMUTABLE — every action ever taken (no delete/update) |

---

## Connect from Python Services

The fraud engine reads from `.env`:
```
DATABASE_URL=postgresql://trinetra:trinetra_dev_password@localhost:5433/trinetra_db
```

Python connection example:
```python
import psycopg2, os
conn = psycopg2.connect(os.getenv("DATABASE_URL"))
```

## Connect from Spring Boot

`services/return-api/src/main/resources/application.properties`:
```properties
spring.datasource.url=jdbc:postgresql://localhost:5433/trinetra_db
spring.datasource.username=trinetra
spring.datasource.password=trinetra_dev_password
```

---

## Useful Database Commands

```powershell
# Connect to DB
docker exec -it trinetra-postgres psql -U trinetra -d trinetra_db

# View all return claims
SELECT id, claim_type, fraud_score, fraud_tier, status FROM return_claims ORDER BY created_at DESC;

# View fraud rings
SELECT ring_name, status, member_count, confidence_score FROM fraud_rings;

# View audit log
SELECT action, actor_type, created_at FROM audit_log ORDER BY created_at DESC LIMIT 20;

# View entity graph edges
SELECT entity_a_id, relationship, entity_b_id FROM entity_relationships;

# Check immutability (this will silently do nothing - audit is protected)
DELETE FROM audit_log WHERE id = (SELECT id FROM audit_log LIMIT 1);
SELECT COUNT(*) FROM audit_log; -- count unchanged, proves immutability
```

---

## Wipe and Reset (Fresh Start)

```powershell
# Docker: destroy all data and restart clean
docker-compose down -v
docker-compose up -d
# init.sql re-runs automatically
```

---

## Credentials Summary

| Field | Value |
|---|---|
| Host | `localhost` |
| Port | `5433` (Docker) or `5432` (direct install) |
| Database | `trinetra_db` |
| Username | `trinetra` |
| Password | `trinetra_dev_password` |
| Redis Host | `localhost:6379` |
