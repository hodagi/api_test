# API Server Execution Guide

## Prerequisites
- Docker installed
- Python 3.11+ (for local development)

## Running with Docker

1. Build the Docker image:
```bash
docker build -t inventory-api .
```

2. Run the container:
```bash
docker run -p 5000:5000 inventory-api
```

## Running Locally

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the server:
```bash
python server.py
```

## Testing the API

Once the server is running, you can test it:

1. Health check:
```bash
curl http://localhost:5000/ping
```

2. Run the E2E tests:
```bash
./run_e2e_tests.sh
```

## API Endpoints

- `GET /ping` - Health check
- `GET /items` - List items with pagination
  - Query params: `q` (search), `page`, `per_page`
- `POST /items` - Create a new item
- `GET /items/{id}` - Get item by ID
- `PUT /items/{id}` - Update item
- `DELETE /items/{id}` - Delete item
- `GET /items/low-stock` - Get low stock items with pagination
  - Query params: `threshold` (required), `page`, `per_page`

## Pagination

The `/items` and `/items/low-stock` endpoints support pagination:

- `page`: Page number (default: 1)
- `per_page`: Items per page (default: 10, max: 100)

Response format:
```json
{
  "items": [...],
  "page": 1,
  "per_page": 10,
  "total": 100,
  "pages": 10,
  "has_next": true,
  "has_prev": false
}
```

## Notes

- The API uses in-memory storage, so data is lost when the server restarts
- The requirements.txt has been updated to include `connexion[flask,uvicorn]` which provides all necessary dependencies