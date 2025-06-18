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
The E2E script respects this value when computing its default `BASE_URL`.

## Docker

Build the container image:

```bash
docker build -t inventory-api .
```

Run the image and expose port 5000:

```bash
docker run -p 5000:5000 inventory-api
```

Example search request:

```bash
curl http://localhost:5000/items?q=foo
```

The `/items/low-stock` endpoint lists items whose quantity is below a provided threshold:

```bash
curl http://localhost:5000/items/low-stock?threshold=5
```

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
