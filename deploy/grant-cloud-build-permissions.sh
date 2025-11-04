#!/usr/bin/env bash
set -euo pipefail

# Grants the minimum roles needed for Cloud Build to deploy
# Cloud Functions (Gen 2) with --allow-unauthenticated using the
# App Engine default service account as the runtime SA.

PROJECT_ID=${PROJECT_ID:-day-planner-london-mvp}
PROJECT_NUMBER=$(gcloud projects describe "$PROJECT_ID" --format='value(projectNumber)')
CB_SA="${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com"
RUNTIME_SA="${PROJECT_ID}@appspot.gserviceaccount.com"

echo "Project:        $PROJECT_ID"
echo "Project Number: $PROJECT_NUMBER"
echo "Cloud Build SA: $CB_SA"
echo "Runtime SA:     $RUNTIME_SA"

echo "\nGranting project roles to Cloud Build SA..."
gcloud projects add-iam-policy-binding "$PROJECT_ID" \
  --member "serviceAccount:${CB_SA}" \
  --role roles/cloudfunctions.developer

gcloud projects add-iam-policy-binding "$PROJECT_ID" \
  --member "serviceAccount:${CB_SA}" \
  --role roles/run.admin

echo "\nGranting Service Account User on runtime SA..."
gcloud iam service-accounts add-iam-policy-binding "$RUNTIME_SA" \
  --member "serviceAccount:${CB_SA}" \
  --role roles/iam.serviceAccountUser

echo "\nDone. Verify with: deploy/verify-cloud-build-permissions.sh"

