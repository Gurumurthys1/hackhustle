# start_services.ps1
$BaseDir = $PSScriptRoot
$EnvStr = "SET DATA_RETENTION_DAYS=730&& SET CONSENT_REQUIRED=true&& SET AUDIT_LOG_IMMUTABLE=true&& SET SOCIAL_MEDIA_SCRAPING_ENABLED=false&& SET BIOMETRIC_PROCESSING_ENABLED=false&& SET AUTO_BLOCK_ENABLED=false&& SET CUSTOMER_SCORE_EXPOSED=false&& SET DATABASE_URL=postgresql://trinetra:trinetra_dev@localhost:5433/trinetra&& SET PYTHONPATH=$BaseDir\services\common;$BaseDir\services\fraud-engine;$BaseDir\services\workers"

Write-Host "🚀 Starting TriNetra AI Services..." -ForegroundColor Cyan

# 1. Start Fraud Engine
Write-Host "Starting Fraud Engine on port 8000..."
$FraudDir = Join-Path $BaseDir "services\fraud-engine"
Start-Process cmd -ArgumentList "/c ""$EnvStr && cd /d $FraudDir && uvicorn main:app --port 8000 --host 0.0.0.0""" -NoNewWindow

# 2. Start Graph Service
Write-Host "Starting Graph Service on port 8002..."
$GraphDir = Join-Path $BaseDir "services\graph-service"
Start-Process cmd -ArgumentList "/c ""$EnvStr && cd /d $GraphDir && uvicorn main:app --port 8002 --host 0.0.0.0""" -NoNewWindow

# 3. Start Workers
Write-Host "Starting Celery Workers..."
$ServicesDir = Join-Path $BaseDir "services"
Start-Process cmd -ArgumentList "/c ""$EnvStr && cd /d $ServicesDir && celery -A workers.celery_app worker --loglevel=info""" -NoNewWindow

# 4. Start Return API (Spring Boot)
Write-Host "Starting Return API on port 8080..."
$ApiDir = Join-Path $BaseDir "services\return-api"
Start-Process cmd -ArgumentList "/c ""cd /d $ApiDir && mvn spring-boot:run""" -NoNewWindow

Write-Host "✅ All services dispatched to background." -ForegroundColor Green
Write-Host "Admin Dashboard: http://localhost:5173"
Write-Host "Customer Portal: http://localhost:5174"
Write-Host "Return API: http://localhost:8085"
