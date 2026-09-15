#!/usr/bin/env bash
# Helper script: run these commands locally to create GCP resources for deployment.
# Replace PROJECT_ID, BUCKET_NAME and SA_NAME as needed.

set -euo pipefail

PROJECT_ID=${1:-YOUR_PROJECT_ID}
BUCKET_NAME=${2:-your-access-poc-bucket}
SA_NAME=${3:-access-run-sa}

echo "Using project: $PROJECT_ID"

gcloud config set project "$PROJECT_ID"

echo "Enabling required APIs..."
gcloud services enable run.googleapis.com cloudbuild.googleapis.com containerregistry.googleapis.com secretmanager.googleapis.com storage.googleapis.com

echo "Creating bucket: $BUCKET_NAME"
gsutil mb -l us-central1 "gs://$BUCKET_NAME" || true

echo "Creating service account: $SA_NAME"
gcloud iam service-accounts create "$SA_NAME" --display-name "$SA_NAME"
SA_EMAIL=$(gcloud iam service-accounts list --filter="$SA_NAME" --format="value(email)")

echo "Granting roles to service account"
gcloud projects add-iam-policy-binding "$PROJECT_ID" --member="serviceAccount:$SA_EMAIL" --role="roles/run.admin"
gcloud projects add-iam-policy-binding "$PROJECT_ID" --member="serviceAccount:$SA_EMAIL" --role="roles/storage.admin"
gcloud projects add-iam-policy-binding "$PROJECT_ID" --member="serviceAccount:$SA_EMAIL" --role="roles/secretmanager.secretAccessor"
gcloud projects add-iam-policy-binding "$PROJECT_ID" --member="serviceAccount:$SA_EMAIL" --role="roles/cloudbuild.builds.editor"

echo "Creating Secret Manager secret from data/reviewers.json"
gcloud secrets create reviewers-secret --data-file=data/reviewers.json || echo "secret already exists"

echo "Create a key for the service account and save to sa-key.json"
gcloud iam service-accounts keys create sa-key.json --iam-account="$SA_EMAIL"

echo "All done. Set GCS_BUCKET=$BUCKET_NAME and REVIEWERS_SECRET_NAME=reviewers-secret when deploying."
