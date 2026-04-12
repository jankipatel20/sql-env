#!/usr/bin/env bash

BASE_URL=$1

if [ -z "$BASE_URL" ]; then
  echo "Usage: ./validate-submission.sh <base_url>"
  exit 1
fi

echo " Validating API at $BASE_URL"
echo

echo " Checking /health"
curl -s "$BASE_URL/health"
echo -e "\n"

echo " Checking /schema"
curl -s "$BASE_URL/schema"
echo -e "\n"

echo " Checking /reset"
curl -s -X POST "$BASE_URL/reset"
echo -e "\n"

echo " Checking /state"
curl -s "$BASE_URL/state"
echo -e "\n"

echo " Checking /step"
curl -s -X POST "$BASE_URL/step" \
  -H "Content-Type: application/json" \
  -d '{"action": {"query": "SELECT 1;"}}'
echo -e "\n"

echo "✅ Validation complete"


