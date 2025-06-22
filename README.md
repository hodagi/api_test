# Sample Inventory API Server

This repository provides a simple REST API written in Python using Flask. The API simulates a lightweight inventory service so you can experiment with typical CRUD operations and run end‑to‑end regression tests using `curl`.

The endpoint functions live in [`controllers.py`](controllers.py) and are referenced from `api_spec.yaml` via `operationId` definitions. The server uses [Connexion](https://connexion.readthedocs.io/) to load the OpenAPI specification and dispatch requests to these controller functions. Together they expose operations for creating, listing, updating and deleting inventory items.

Each item consists of an integer `id`, a `name`, an integer `quantity` and a numeric `price` value.

The server also exposes a simple health check at `GET /ping` which returns
`{"message": "pong"}`.

## Requirements

* Python 3.11+
* `pip`
* `jq` (for the E2E test script)

Install dependencies:

```bash
pip install -r requirements.txt
```

## Running the API server

```bash
python server.py
```

Set the `PORT` environment variable to change the listen port (default `5000`).

## Running with Docker

Build and run the Docker image:

```bash
# Build the image (rebuild after code changes)
docker build -t inventory-api .

# Run the container
docker run -p 5000:5000 inventory-api
```

**Note**: Always rebuild the Docker image after making code changes to ensure the container runs the latest version.

## API Usage Examples

List all items (returns paginated response):

```bash
curl http://localhost:5000/items
# Response: {"items": [...], "page": 1, "per_page": 10, "total": n, "pages": n, "has_next": bool, "has_prev": bool}
```

Search items with pagination:

```bash
curl http://localhost:5000/items?q=foo&page=2&per_page=5
```

The `/items/low-stock` endpoint lists items whose quantity is below a provided threshold (also paginated):

```bash
curl http://localhost:5000/items/low-stock?threshold=5&page=1&per_page=20
```

**Pagination Note**: The `/items` and `/items/low-stock` endpoints now return paginated responses with the following structure:
- `items`: Array of items for the current page
- `page`: Current page number (1-based)
- `per_page`: Number of items per page (max 100)
- `total`: Total number of items
- `pages`: Total number of pages
- `has_next`: Boolean indicating if there's a next page
- `has_prev`: Boolean indicating if there's a previous page

## API specification

See [`api_spec.yaml`](api_spec.yaml) for the OpenAPI 3.0 specification of the available endpoints.

## Unit tests

Run the automated unit tests using [pytest](https://docs.pytest.org/en/stable/):

```bash
pytest -q
```

## End‑to‑end tests

Run the provided script after starting the server. The suite exercises common
error scenarios such as invalid input and unknown IDs. The script assumes the
server is reachable at `http://localhost:${PORT}` but you can override this by
setting the `BASE_URL` environment variable:

```bash
./run_e2e_tests.sh
```

The script uses `curl` to perform a sequence of API calls and fails on the first error.

## Regenerating controller stubs

Controller skeletons can be derived from the OpenAPI specification using [OpenAPI Generator](https://openapi-generator.tech/). The `python-flask` generator emits Flask + Connexion code that matches the operations defined in `api_spec.yaml`.

Run the generator with `npx`:

```bash
npx --yes @openapitools/openapi-generator-cli generate \
  -i api_spec.yaml \
  -g python-flask \
  -o gen
```

This creates stubs in `gen/openapi_server/controllers/`. Copy any new functions into `controllers.py` and then remove the temporary `gen/` directory.
