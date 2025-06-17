#!/bin/bash
set -euo pipefail
BASE_URL=${BASE_URL:-http://localhost:5000}

# Health check
curl -fsS "$BASE_URL/ping" | grep -q 'pong'

# Create item
ITEM_ID=$(curl -fsS -X POST "$BASE_URL/items" -H 'Content-Type: application/json' -d '{"name":"test"}' | jq '.id')

# Get item
curl -fsS "$BASE_URL/items/${ITEM_ID}" | jq -e '.name == "test"' >/dev/null

# Update item
curl -fsS -X PUT "$BASE_URL/items/${ITEM_ID}" -H 'Content-Type: application/json' -d '{"name":"updated"}' | jq -e '.name == "updated"' >/dev/null

# Delete item
curl -fsS -X DELETE "$BASE_URL/items/${ITEM_ID}" | jq -e ".id == ${ITEM_ID}" >/dev/null

echo "All E2E tests passed" >&2
