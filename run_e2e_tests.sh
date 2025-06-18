#!/bin/bash
set -euo pipefail
BASE_URL=${BASE_URL:-http://localhost:5000}

check_status() {
  expected=$1; shift
  status=$(curl -s -o /dev/null -w "%{http_code}" "$@")
  if [ "$status" != "$expected" ]; then
    echo "Expected $expected but got $status" >&2
    exit 1
  fi
}

# Health check
curl -fsS "$BASE_URL/ping" | grep -q 'pong'

# Create item
ITEM_ID=$(curl -fsS -X POST "$BASE_URL/items" -H 'Content-Type: application/json' -d '{"name":"test","quantity":5}' | jq '.id')

# Search should find the new item
curl -fsS "$BASE_URL/items?q=es" | jq -e "length == 1 and .[0].id == ${ITEM_ID}" >/dev/null
curl -fsS "$BASE_URL/items?q=zzz" | jq -e 'length == 0' >/dev/null

# Invalid creates
check_status 400 -X POST "$BASE_URL/items" -H 'Content-Type: application/json' -d '{"name":"","quantity":1}'
check_status 400 -X POST "$BASE_URL/items" -H 'Content-Type: application/json' -d '{"name":123,"quantity":1}'
check_status 400 -X POST "$BASE_URL/items" -H 'Content-Type: application/json' -d '{"name":"bad","quantity":"foo"}'
check_status 400 -X POST "$BASE_URL/items" -H 'Content-Type: application/json' -d '{"name":"bad","quantity":-1}'

# Get item
curl -fsS "$BASE_URL/items/${ITEM_ID}" | jq -e '.name == "test" and .quantity == 5' >/dev/null
check_status 404 "$BASE_URL/items/9999"

# Update item
curl -fsS -X PUT "$BASE_URL/items/${ITEM_ID}" -H 'Content-Type: application/json' -d '{"name":"updated","quantity":8}' | jq -e '.name == "updated" and .quantity == 8' >/dev/null
curl -fsS "$BASE_URL/items?q=UPD" | jq -e "length == 1 and .[0].name == \"updated\"" >/dev/null
check_status 400 -X PUT "$BASE_URL/items/${ITEM_ID}" -H 'Content-Type: application/json' -d '{"name":"","quantity":1}'
check_status 400 -X PUT "$BASE_URL/items/${ITEM_ID}" -H 'Content-Type: application/json' -d '{"name":"updated","quantity":"foo"}'
check_status 400 -X PUT "$BASE_URL/items/${ITEM_ID}" -H 'Content-Type: application/json' -d '{"name":"updated","quantity":-5}'
check_status 404 -X PUT "$BASE_URL/items/9999" -H 'Content-Type: application/json' -d '{"name":"foo","quantity":1}'

# Delete item
curl -fsS -X DELETE "$BASE_URL/items/${ITEM_ID}" | jq -e ".id == ${ITEM_ID}" >/dev/null
check_status 404 "$BASE_URL/items/${ITEM_ID}"
check_status 404 -X DELETE "$BASE_URL/items/${ITEM_ID}"

echo "All E2E tests passed" >&2
