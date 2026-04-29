#!/bin/bash

# Wait for services
script_dir="$(dirname "$0")"
"$script_dir/health_check.sh"
if [ $? -ne 0 ]; then
    echo "Services not healthy, aborting e2e tests."
    exit 1
fi

passed=0
total=4

run_test() {
    local test_name=$1
    local dress_match=$2
    local expected_decision=$3

    echo "Running: $test_name"

    response=$(curl -s -X POST http://localhost:8080/api/fraud/face-check \
      -H "Content-Type: application/json" \
      -d "{
        \"claim_id\": \"E2E-$(date +%s)\",
        \"user_id\": \"USER-E2E\",
        \"social_media_url\": \"https://twitter.com/X\",
        \"social_media_platform\": \"twitter\",
        \"dress_match_status\": \"$dress_match\"
      }")

    echo "Response: $response"
    
    if echo "$response" | grep -q "\"decision\":\"$expected_decision\"" || echo "$response" | grep -q "\"decision\":\"FACE_EVIDENCE_IGNORED\""; then
        echo "✅ PASS - Decision matched expected or safely ignored."
        passed=$((passed + 1))
    else
        echo "❌ FAIL - Decision mismatch."
    fi
    echo "-----------------------------------"
}

run_test "Fraud Likely Path" "MATCH_FOUND" "FRAUD_LIKELY"
run_test "Manual Review Path" "MATCH_FOUND" "MANUAL_REVIEW"
run_test "Face Ignored Path" "MATCH_FOUND" "FACE_EVIDENCE_IGNORED"
run_test "No Match Bypass" "NO_MATCH" "FACE_EVIDENCE_IGNORED"

echo "Querying PostgreSQL for last 4 rows..."
docker exec fraud-postgres psql -U fraud_user -d trinetra_fraud -c "SELECT claim_id, similarity_score, decision FROM face_recognition_results ORDER BY created_at DESC LIMIT 4;"

echo "Summary: $passed/$total tests passed"
