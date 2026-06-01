#!/usr/bin/env bash
set -euo pipefail

APP_URL="${APP_URL:-http://localhost:8080}"
TEST_YEAR="${TEST_YEAR:-2025}"

# Real project that already returned data in your GitLab test.
REAL_PROJECT="${REAL_PROJECT:-tziyon31/Ted-Search}"

# This should not exist, used to verify 404 mapping.
MISSING_PROJECT="${MISSING_PROJECT:-tziyon31/project-that-does-not-exist}"

run_test() {
  local name="$1"
  local expected_status="$2"
  shift 2

  echo
  echo "=============================="
  echo "TEST: $name"
  echo "EXPECTED STATUS: $expected_status"
  echo "=============================="

  local response
  response="$("$@" -sS -w $'\nHTTP_STATUS:%{http_code}')"

  local body
  local status

  body="$(echo "$response" | sed '$d')"
  status="$(echo "$response" | tail -n1 | sed 's/HTTP_STATUS://')"

  echo "ACTUAL STATUS: $status"
  echo "BODY:"
  echo "$body" | python -m json.tool 2>/dev/null || echo "$body"

  if [[ "$status" != "$expected_status" ]]; then
    echo
    echo "FAILED: expected $expected_status but got $status"
    exit 1
  fi

  echo "PASSED"
}

echo "Using APP_URL=$APP_URL"
echo "Using TEST_YEAR=$TEST_YEAR"
echo "Using REAL_PROJECT=$REAL_PROJECT"
echo "Using MISSING_PROJECT=$MISSING_PROJECT"

run_test "health endpoint" 200 \
  curl "$APP_URL/health"

run_test "issues missing year returns 400" 400 \
  curl "$APP_URL/issues"

run_test "issues invalid year returns 400" 400 \
  curl "$APP_URL/issues?year=abc"

run_test "merge-requests missing year returns 400" 400 \
  curl "$APP_URL/merge-requests"

run_test "merge-requests invalid year returns 400" 400 \
  curl "$APP_URL/merge-requests?year=abc"

run_test "global issues by year" 200 \
  curl --get "$APP_URL/issues" \
    --data-urlencode "year=$TEST_YEAR"

run_test "global merge requests by year" 200 \
  curl --get "$APP_URL/merge-requests" \
    --data-urlencode "year=$TEST_YEAR"

run_test "project issues by year" 200 \
  curl --get "$APP_URL/issues" \
    --data-urlencode "year=$TEST_YEAR" \
    --data-urlencode "project=$REAL_PROJECT"

run_test "project merge requests by year" 200 \
  curl --get "$APP_URL/merge-requests" \
    --data-urlencode "year=$TEST_YEAR" \
    --data-urlencode "project=$REAL_PROJECT"

run_test "missing project issues returns 404" 404 \
  curl --get "$APP_URL/issues" \
    --data-urlencode "year=$TEST_YEAR" \
    --data-urlencode "project=$MISSING_PROJECT"

run_test "missing project merge requests returns 404" 404 \
  curl --get "$APP_URL/merge-requests" \
    --data-urlencode "year=$TEST_YEAR" \
    --data-urlencode "project=$MISSING_PROJECT"

echo
echo "All smoke tests passed."
