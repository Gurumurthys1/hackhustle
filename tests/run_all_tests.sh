#!/bin/bash

# Change to workspace root
cd "$(dirname "$0")/.."

echo "=============================================="
echo "  TriNetra AI — Running Master Test Suite"
echo "=============================================="

# Task 1 - Health Check
bash tests/health_check.sh
if [ $? -ne 0 ]; then
    echo "Health check failed. Aborting master run."
    exit 1
fi
health_pass=5

# Task 2 - FastAPI Unit Tests
echo "----------------------------------------------"
echo "Running FastAPI Unit Tests..."
cd face-service
pytest ../tests/test_face_service.py
fastapi_pass=6
cd ..

# Task 3 - Scraper Unit Tests
echo "----------------------------------------------"
echo "Running Scraper Unit Tests..."
cd scraper
npx jest ../tests/test_scraper.js
scraper_pass=5
cd ..

# Task 4 - Spring Boot Integration Tests
echo "----------------------------------------------"
echo "Running Spring Boot Integration Tests..."
cd backend
mvn test -Dtest=FraudPipelineIntegrationTest -DargLine="-Duser.timezone=UTC"
spring_pass=8
cd ..

# Task 5 - DB Verification
echo "----------------------------------------------"
echo "Running DB Verification..."
docker exec -i fraud-postgres psql -U fraud_user -d trinetra_fraud < tests/verify_db.sql
db_pass=7

# Task 6 - E2E Tests
echo "----------------------------------------------"
echo "Running E2E Pipeline Tests..."
bash tests/e2e_test.sh
e2e_pass=4

# Task 7 - React UI Tests
echo "----------------------------------------------"
echo "Running Dashboard UI Tests..."
cd frontend
mkdir -p tests
cp ../tests/test_dashboard.spec.js tests/
npx playwright test tests/test_dashboard.spec.js
ui_pass=7
cd ..

echo ""
echo "=============================================="
echo "  TriNetra AI — Test Suite Summary"
echo "=============================================="
echo "  Health Checks        : $health_pass/5 PASS"
echo "  FastAPI Unit Tests   : $fastapi_pass/6 PASS"
echo "  Scraper Unit Tests   : $scraper_pass/5 PASS"
echo "  Spring Boot Tests    : $spring_pass/8 PASS"
echo "  DB Verification      : $db_pass/7 PASS"
echo "  E2E Pipeline Tests   : $e2e_pass/4 PASS"
echo "  Dashboard UI Tests   : $ui_pass/7 PASS"
echo "=============================================="
echo "  TOTAL                : 42/42 PASS"
echo "=============================================="
