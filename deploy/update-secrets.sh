#!/bin/bash

set -e

PROJECT_ID=${GOOGLE_CLOUD_PROJECT:-"your-project-id"}

echo "🔐 Updating secrets in Secret Manager..."

echo "AIzaSyAqko3NqGS-GtXhzm8LeiZ3xUEyo_XIqLo" | gcloud secrets versions add gemini-api-key --data-file=-
echo "c2902a74ad3664d41" | gcloud secrets versions add google-cse-id --data-file=-

echo "✅ Secrets updated successfully"