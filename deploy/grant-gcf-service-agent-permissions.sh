#!/usr/bin/env bash
set -euo pipefail

# Grants Cloud Run Admin to the Cloud Functions Service Agent so that
# Cloud Functions (Gen 2) can set Cloud Run service IAM policies
# (required when using --allow-unauthenticated).

PROJECT_ID=${PROJECT_ID:-day-planner-london-mvp}
PROJECT_NUMBER=$(gcloud projects describe "$PROJECT_ID" --format='value(projectNumber)')
GCF_SA="service-${PROJECT_NUMBER}@gcf-admin-robot.iam.gserviceaccount.com"

echo "Project:        $PROJECT_ID"
echo "Project Number: $PROJECT_NUMBER"
echo "GCF Service SA: $GCF_SA"

echo "\nGranting roles/run.admin on project to GCF Service Agent..."
gcloud projects add-iam-policy-binding "$PROJECT_ID" \
  --member "serviceAccount:${GCF_SA}" \
  --role roles/run.admin

echo "\nDone. Re-run deploy or Cloud Build."

