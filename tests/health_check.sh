#!/bin/bash

echo "Starting TriNetra AI Health Checks..."
echo "======================================="

fail=0

check_service() {
    local port=$1
    local name=$2
    local endpoint=$3
    
    if curl -s -m 2 http://localhost:$port$endpoint > /dev/null; then
        echo "✅ PASS - $name (Port $port)"
    else
        echo "❌ FAIL - $name (Port $port)"
        fail=1
    fi
}

check_service 8080 "Spring Boot Orchestrator" "/api/fraud/face-check"
check_service 8000 "FastAPI Face Service" "/health"
check_service 3000 "Node.js Scraper" "/api/scrape"
check_service 5173 "React Admin Dashboard" "/"
check_service 5050 "pgAdmin" "/"

echo "======================================="
if [ $fail -eq 1 ]; then
    echo "Health check failed. One or more services are down."
    exit 1
fi

echo "All services healthy."
exit 0
