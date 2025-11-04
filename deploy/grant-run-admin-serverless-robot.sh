#!/usr/bin/env bash
set -euo pipefail

# Optionally grant Cloud Run Admin to the Cloud Run Service Agent.
# Use only if deployments still fail with run.services.setIamPolicy after
# granting GCF service agent permissions.

PROJECT_ID=${PROJECT_ID:-day-planner-london-mvp}
PROJECT_NUMBER=$(gcloud projects describe "$PROJECT_ID" --format='value(projectNumber)')
CR_SA="service-${PROJECT_NUMBER}@serverless-robot-prod.iam.gserviceaccount.com"

echo "Project:        $PROJECT_ID"
echo "Project Number: $PROJECT_NUMBER"
echo "Cloud Run SA:   $CR_SA"

echo "\nGranting roles/run.admin on project to Cloud Run Service Agent..."
gcloud projects add-iam-policy-binding "$PROJECT_ID" \
  --member "serviceAccount:${CR_SA}" \
  --role roles/run.admin

echo "\nDone. Re-run deploy or Cloud Build."

