#!/usr/bin/env bash
set -euo pipefail

PROJECT_ID=${PROJECT_ID:-day-planner-london-mvp}
REGION=${REGION:-asia-east2}

RAW_BUCKET=day-planner-london-mvp-nemo-raw
CLEAN_BUCKET=day-planner-london-mvp-nemo-clean

RUNTIME_SA="${PROJECT_ID}@appspot.gserviceaccount.com"
VERTEX_SA="service-$(gcloud projects describe "$PROJECT_ID" --format='value(projectNumber)')@gcp-sa-aiplatform.iam.gserviceaccount.com"

echo "Granting bucket permissions in project: $PROJECT_ID"
echo "Runtime SA: $RUNTIME_SA"
echo "Vertex SA:  $VERTEX_SA"

echo "\nGrant runtime SA objectAdmin on raw and clean buckets..."
gcloud storage buckets add-iam-policy-binding gs://$RAW_BUCKET \
  --member serviceAccount:$RUNTIME_SA \
  --role roles/storage.objectAdmin

gcloud storage buckets add-iam-policy-binding gs://$CLEAN_BUCKET \
  --member serviceAccount:$RUNTIME_SA \
  --role roles/storage.objectAdmin

echo "\nGrant Vertex AI service agent objectViewer on clean bucket..."
gcloud storage buckets add-iam-policy-binding gs://$CLEAN_BUCKET \
  --member serviceAccount:$VERTEX_SA \
  --role roles/storage.objectViewer

echo "\nBucket permissions granted."

