# Access Request Intelligence POC

This project is a synthetic proof-of-concept for a document-intensive access-request workflow in an enterprise environment.

## Problem

The current process often involves a PDF request form being reviewed manually, where an analyst reads the form, identifies the requested entitlement, and then validates the request against a standard roles document and policy rules.

## Goal

Build a lightweight prototype that:

- ingests a request form (simulated here as extracted text or structured JSON)
- identifies the requested role and entitlement
- compares the request against a standard roles catalog
- decides whether the request should be approved, denied, or escalated for review
- captures a simple audit trail and evaluation metrics

## Project structure

- `src/access_request_poc/` contains the Python implementation
- `data/` contains synthetic request examples and the roles catalog
- `tests/` contains regression tests for validation logic

## Running the demo

```bash
cd /home/labber/projects/access_request_poc
source .venv/bin/activate
python -m access_request_poc.demo
```

## Commands

To run tests:

```bash
cd /home/labber/projects/access_request_poc
. .venv/bin/activate
PYTHONPATH=src pytest -q
```

Generate sample PDFs from the text samples:

```bash
cd /home/labber/projects/access_request_poc
. .venv/bin/activate
python scripts/generate_pdfs.py
```

Run the CLI on a text file:

```bash
python -m access_request_poc.cli data/samples/sample_request_1.txt
```

Run the reviewer UI (Streamlit):

```bash
cd /home/labber/projects/access_request_poc
. .venv/bin/activate
PYTHONPATH=src python -m streamlit run app.py
```

Generate PDFs with annotations (used for highlighting fields in reviewer UI):

```bash
python scripts/generate_pdfs.py
```

Export reviewer-labeled dataset for benchmarking:

```bash
python scripts/export_reviews.py
```




## Example outcomes

The system classifies requests into one of three states:

- `APPROVE`
- `REJECT`
- `NEEDS_REVIEW`

This mirrors the decisioning pattern used in enterprise access governance and document intelligence workflows.

## GCP CI/CD

This repo includes a sample `cloudbuild.yaml` (Cloud Build) and a GitHub Actions workflow `.github/workflows/deploy_gcp.yml`.

To use GitHub Actions:

1. Create a GCP service account with roles: `roles/run.admin`, `roles/storage.admin`, `roles/cloudbuild.builds.editor`, `roles/secretmanager.secretAccessor`.
2. Create a JSON key for the service account and add it to GitHub Secrets as `GCP_SA_KEY`.
3. Add `GCP_PROJECT` secret with your project id.
4. Push to `main` — the workflow will run tests, build an image, and deploy to Cloud Run.

To use Cloud Build directly:

1. Push the repo and run:
	```bash
	gcloud builds submit --config cloudbuild.yaml --substitutions=_ENV=prod
	```

