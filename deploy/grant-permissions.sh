#!/bin/bash

set -e

PROJECT_ID=${GOOGLE_CLOUD_PROJECT:-"your-project-id"}
BUCKET_NAME="day-planner-london-mvp-nemo-clean"
SERVICE_ACCOUNT="service-612990030705@gcp-sa-aiplatform.iam.gserviceaccount.com"

echo "Granting roles/storage.objectViewer to $SERVICE_ACCOUNT on bucket $BUCKET_NAME"

gcloud storage buckets add-iam-policy-binding gs://$BUCKET_NAME \
  --member serviceAccount:$SERVICE_ACCOUNT \
  --role roles/storage.objectViewer

echo "Permissions granted successfully"
