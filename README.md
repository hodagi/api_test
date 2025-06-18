# Sample API Server for Chaos Testing

This repository provides a simple REST API written in Python using Flask. The API can be used for experimenting with chaos engineering techniques and for running end‑to‑end regression tests using `curl`.

The endpoint functions live in [`controllers.py`](controllers.py) and are referenced from `api_spec.yaml` via `operationId` definitions. The server uses [Connexion](https://connexion.readthedocs.io/) to load the OpenAPI specification and dispatch requests to these controller functions.

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

The server listens on `http://localhost:5000` by default.

## API specification

See [`api_spec.yaml`](api_spec.yaml) for the OpenAPI 3.0 specification of the available endpoints.

## End‑to‑end tests

Run the provided script after starting the server. The suite now exercises
common error scenarios such as invalid input and unknown IDs:

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
