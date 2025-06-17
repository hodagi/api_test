# Sample API Server for Chaos Testing

This repository provides a simple REST API written in Python using Flask. The API can be used for experimenting with chaos engineering techniques and for running end‑to‑end regression tests using `curl`.

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

Run the provided script after starting the server:

```bash
./run_e2e_tests.sh
```

The script uses `curl` to perform a sequence of API calls and fails on the first error.
