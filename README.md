# SolarEdge Energy Reporting

> **Portfolio reconstruction / demonstration.** This is a reference implementation based on a described project, not a verified copy of original production source or evidence of deployment.

## Problem and purpose

Offline daily energy conversion with an illustrative Monitoring API adapter. This demo makes the workflow reproducible with synthetic data or mocked API responses and exposes the assumptions that need review before real use.

## Stack and flow

Python, requests, python-dotenv.

SolarEdge-style JSON -> unit/date/finite-value validation -> sorted daily kWh rows -> CSV.

`src/` contains processing code, `tests/` contains offline regression tests, `.github/workflows/checks.yml` runs offline checks on pushes and pull requests. Samples are synthetic; `output/` and runtime files are ignored.

## Setup and execution

Use Python 3.12 and an isolated virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.lock
python -m src.report --input samples/energy.json --output output/energy.csv
```

`requirements.txt` records direct dependencies; `requirements.lock` pins the resolved runtime set. Offline transformations/tests do not require API credentials after installation. No API or email call is executed automatically.

## Implemented behavior and example output

Synthetic sample converts 12,000/14,000 Wh to 12.0/14.0 kWh. Null readings remain blank. Missing fields, unsupported units, negative/nonfinite values and duplicate days fail. The optional adapter validates date ordering, HTTPS base URL and numeric site IDs; HTTP calls are mocked in tests.

## Tests

```powershell
python -m unittest discover -s tests -v
python -m compileall -q src tests
```

The suite uses synthetic files and mocked service responses. See the preparation validation report for actual results and environment limitations; a workflow file is not evidence of a completed GitHub Actions run.

## Limitations and future work

Live API entitlements, vendor range limits and API contract have not been verified. No range chunking, retry/backoff, OAuth or EDMS/email delivery is implemented. Do not log API URLs containing query credentials. Future work: verified vendor limits and approved delivery schema.

## Data and publication

Do not commit real customer records, tokens, production identifiers, proprietary drawings, pricing data or personal photos. Keep `.env` local. Error messages from the adapter omit request URLs and credential values. Local file paths/messages can still reveal context; review logs before sharing.

This repository contains a reconstructed demonstration prepared for a public engineering portfolio. See `docs/PROVENANCE.md` for its origin and limits. No original employer/client implementation is included. No license is granted by this publication; third-party dependencies retain their own license terms.
