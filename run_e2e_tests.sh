#!/bin/bash
set -euo pipefail
PORT=${PORT:-5000}
BASE_URL=${BASE_URL:-http://localhost:${PORT}}

check_status() {
  expected=$1; shift
  status=$(curl -s -o /dev/null -w "%{http_code}" "$@")
  if [ "$status" != "$expected" ]; then
    echo "Expected $expected but got $status" >&2
    exit 1
  fi
}

echo "Running E2E tests..."

# Health check
echo "Testing health check..."
curl -fsS "$BASE_URL/ping" | grep -q 'pong'

# Create item
echo "Testing item creation..."
ITEM_ID=$(curl -fsS -X POST "$BASE_URL/items" -H 'Content-Type: application/json' -d '{"name":"test","quantity":5,"price":1.5}' | jq '.id')

# Search should find the new item (updated for pagination response)
echo "Testing search..."
curl -fsS "$BASE_URL/items?q=es" | jq -e ".items | length == 1 and .items[0].id == ${ITEM_ID}" >/dev/null
curl -fsS "$BASE_URL/items?q=zzz" | jq -e '.items | length == 0' >/dev/null

# Low-stock query (updated for pagination response)
echo "Testing low-stock query..."
curl -fsS "$BASE_URL/items/low-stock?threshold=6" | jq -e ".items | length == 1 and .items[0].id == ${ITEM_ID}" >/dev/null
check_status 400 "$BASE_URL/items/low-stock?threshold=-1"

# Invalid creates
echo "Testing invalid creates..."
check_status 400 -X POST "$BASE_URL/items" -H 'Content-Type: application/json' -d '{"name":"","quantity":1,"price":1}'
check_status 400 -X POST "$BASE_URL/items" -H 'Content-Type: application/json' -d '{"name":123,"quantity":1,"price":1}'
check_status 400 -X POST "$BASE_URL/items" -H 'Content-Type: application/json' -d '{"name":"bad","quantity":"foo","price":1}'
check_status 400 -X POST "$BASE_URL/items" -H 'Content-Type: application/json' -d '{"name":"bad","quantity":-1,"price":1}'
check_status 400 -X POST "$BASE_URL/items" -H 'Content-Type: application/json' -d '{"name":"bad","quantity":1}'

# Get item
echo "Testing get item..."
curl -fsS "$BASE_URL/items/${ITEM_ID}" | jq -e '.name == "test" and .quantity == 5 and .price == 1.5' >/dev/null
check_status 404 "$BASE_URL/items/9999"

# Update item
echo "Testing item update..."
curl -fsS -X PUT "$BASE_URL/items/${ITEM_ID}" -H 'Content-Type: application/json' -d '{"name":"updated","quantity":8,"price":2.0}' | jq -e '.name == "updated" and .quantity == 8 and .price == 2.0' >/dev/null
curl -fsS "$BASE_URL/items?q=UPD" | jq -e ".items | length == 1 and .items[0].name == \"updated\"" >/dev/null
check_status 400 -X PUT "$BASE_URL/items/${ITEM_ID}" -H 'Content-Type: application/json' -d '{"name":"","quantity":1,"price":1}'
check_status 400 -X PUT "$BASE_URL/items/${ITEM_ID}" -H 'Content-Type: application/json' -d '{"name":"updated","quantity":"foo","price":1}'
check_status 400 -X PUT "$BASE_URL/items/${ITEM_ID}" -H 'Content-Type: application/json' -d '{"name":"updated","quantity":-5,"price":1}'
check_status 404 -X PUT "$BASE_URL/items/9999" -H 'Content-Type: application/json' -d '{"name":"foo","quantity":1,"price":1}'

# Delete item
echo "Testing item deletion..."
curl -fsS -X DELETE "$BASE_URL/items/${ITEM_ID}" | jq -e ".id == ${ITEM_ID}" >/dev/null
check_status 404 "$BASE_URL/items/${ITEM_ID}"
check_status 404 -X DELETE "$BASE_URL/items/${ITEM_ID}"

# ===== PAGINATION TESTS =====
echo ""
echo "Testing pagination functionality..."

# Create 15 items for testing
echo "Creating test items for pagination..."
for i in {0..14}; do
  curl -fsS -X POST "$BASE_URL/items" -H 'Content-Type: application/json' \
    -d "{\"name\":\"item$i\",\"quantity\":$((i % 5)),\"price\":$(echo "$i * 0.5" | bc)}" >/dev/null
done

# Test default pagination
echo "Testing default pagination..."
RESULT=$(curl -fsS "$BASE_URL/items")
echo "$RESULT" | jq -e '.items | length == 10' >/dev/null || (echo "Expected 10 items" && exit 1)
echo "$RESULT" | jq -e '.total == 15' >/dev/null || (echo "Expected total 15" && exit 1)
echo "$RESULT" | jq -e '.page == 1' >/dev/null || (echo "Expected page 1" && exit 1)
echo "$RESULT" | jq -e '.per_page == 10' >/dev/null || (echo "Expected per_page 10" && exit 1)
echo "$RESULT" | jq -e '.pages == 2' >/dev/null || (echo "Expected 2 pages" && exit 1)
echo "$RESULT" | jq -e '.has_next == true' >/dev/null || (echo "Expected has_next true" && exit 1)
echo "$RESULT" | jq -e '.has_prev == false' >/dev/null || (echo "Expected has_prev false" && exit 1)

# Test page 2
echo "Testing page 2..."
RESULT=$(curl -fsS "$BASE_URL/items?page=2")
echo "$RESULT" | jq -e '.items | length == 5' >/dev/null || (echo "Expected 5 items on page 2" && exit 1)
echo "$RESULT" | jq -e '.page == 2' >/dev/null || (echo "Expected page 2" && exit 1)
echo "$RESULT" | jq -e '.has_next == false' >/dev/null || (echo "Expected has_next false" && exit 1)
echo "$RESULT" | jq -e '.has_prev == true' >/dev/null || (echo "Expected has_prev true" && exit 1)

# Test custom per_page
echo "Testing custom per_page..."
RESULT=$(curl -fsS "$BASE_URL/items?per_page=5")
echo "$RESULT" | jq -e '.items | length == 5' >/dev/null || (echo "Expected 5 items with per_page=5" && exit 1)
echo "$RESULT" | jq -e '.pages == 3' >/dev/null || (echo "Expected 3 pages" && exit 1)

# Test search with pagination
echo "Testing search with pagination..."
RESULT=$(curl -fsS "$BASE_URL/items?q=item1&per_page=3")
# Should find item1, item10, item11, item12, item13, item14 (6 items total)
echo "$RESULT" | jq -e '.total == 6' >/dev/null || (echo "Expected 6 items matching 'item1'" && exit 1)
echo "$RESULT" | jq -e '.items | length == 3' >/dev/null || (echo "Expected 3 items on first page" && exit 1)

# Test low-stock with pagination
echo "Testing low-stock with pagination..."
RESULT=$(curl -fsS "$BASE_URL/items/low-stock?threshold=3&per_page=5")
# Items with quantity < 3: 0,1,2 (9 items total)
echo "$RESULT" | jq -e '.total == 9' >/dev/null || (echo "Expected 9 low-stock items" && exit 1)
echo "$RESULT" | jq -e '.items | length == 5' >/dev/null || (echo "Expected 5 items on first page" && exit 1)
echo "$RESULT" | jq -e '.pages == 2' >/dev/null || (echo "Expected 2 pages" && exit 1)

# Test page limits
echo "Testing page limits..."
RESULT=$(curl -fsS "$BASE_URL/items?per_page=200")
echo "$RESULT" | jq -e '.per_page == 100' >/dev/null || (echo "Expected per_page capped at 100" && exit 1)

# Test invalid page (should clamp to valid range)
RESULT=$(curl -fsS "$BASE_URL/items?page=100")
echo "$RESULT" | jq -e '.page == 2' >/dev/null || (echo "Expected page clamped to 2" && exit 1)

# Clean up - delete all items
echo "Cleaning up..."
for i in {2..16}; do
  curl -fsS -X DELETE "$BASE_URL/items/$i" >/dev/null || true
done

echo ""
echo "All E2E tests passed!" >&2
