#!/bin/bash

# Vertex AI Vector Search Setup Script
# Creates index and endpoint for Nemo Compliance MVP

set -e

PROJECT_ID=${GOOGLE_CLOUD_PROJECT:-$(gcloud config get-value project 2>/dev/null || echo "")}
REGION=${REGION:-"asia-east2"}
BUCKET_NAME="day-planner-london-mvp-nemo-clean"
SERVICE_ACCOUNT="service-612990030705@gcp-sa-aiplatform.iam.gserviceaccount.com"

if [ -z "$PROJECT_ID" ] || [ "$PROJECT_ID" = "your-project-id" ]; then
  echo "ERROR: PROJECT_ID is not set. Export GOOGLE_CLOUD_PROJECT or set gcloud config project."
  exit 1
fi

echo "🤖 Setting up Vertex AI Vector Search"
echo "Project: $PROJECT_ID"
echo "Region: $REGION"

echo "🔐 Granting roles/storage.objectViewer to $SERVICE_ACCOUNT on bucket $BUCKET_NAME"
gcloud storage buckets add-iam-policy-binding gs://$BUCKET_NAME \
  --member serviceAccount:$SERVICE_ACCOUNT \
  --role roles/storage.objectViewer
echo "✅ Permissions granted successfully"

# Create Vector Search Index
echo "📊 Creating Vertex AI Vector Search index..."
INDEX_OUTPUT=$(gcloud ai indexes create \
  --display-name="nemo-compliance-index" \
  --description="Chinese regulatory documents vector index" \
  --metadata-file="deploy/index_metadata.json" \
  --region=$REGION \
  --project=$PROJECT_ID \
  --format="value(name)")

# Resolve Index ID by listing (more reliable than parsing operation output)
INDEX_NAME=$(gcloud ai indexes list --region=$REGION --project=$PROJECT_ID \
  --filter="display_name=nemo-compliance-index" --format="value(name)" | tail -n 1)
INDEX_ID=$(basename "$INDEX_NAME")
echo "✅ Created index with ID: ${INDEX_ID}"

# Create Index Endpoint
echo "🔗 Creating Vertex AI index endpoint..."
ENDPOINT_OUTPUT=$(gcloud ai index-endpoints create \
  --display-name="nemo-compliance-endpoint" \
  --region=$REGION \
  --project=$PROJECT_ID \
  --format="value(name)")

ENDPOINT_ID=$(echo $ENDPOINT_OUTPUT | sed 's/.*\/\([^\/]*\)$/\1/')
echo "✅ Created endpoint with ID: $ENDPOINT_ID"

# Wait for index to be ready
echo "⏳ Waiting for index to be ready..."
while true; do
  INDEX_STATE=$(gcloud ai indexes describe $INDEX_ID --region=$REGION --project=$PROJECT_ID --format="value(state)")
  if [ "$INDEX_STATE" = "INDEX_STATE_READY" ]; then
    echo "✅ Index is ready"
    break
  fi
  echo "Index state: $INDEX_STATE (waiting...)"
  sleep 30
done

# Deploy index to endpoint
echo "🚀 Deploying index to endpoint..."
gcloud ai index-endpoints deploy-index $ENDPOINT_ID \
  --deployed-index-id="nemo-deployed-index" \
  --display-name="Nemo Compliance Deployed Index" \
  --index=$INDEX_ID \
  --region=$REGION \
  --project=$PROJECT_ID

echo "✅ Vertex AI setup complete!"
echo ""
echo "📋 Configuration:"
echo "INDEX_ID=$INDEX_ID"
echo "ENDPOINT_ID=$ENDPOINT_ID"
echo ""
echo "🔧 Update your Cloud Functions with these environment variables:"
echo "gcloud functions deploy nemo-query --gen2 --region=$REGION --update-env-vars VERTEX_INDEX_ID=$INDEX_ID,VERTEX_ENDPOINT_ID=$ENDPOINT_ID"
echo "gcloud functions deploy nemo-ingest --gen2 --region=$REGION --update-env-vars VERTEX_INDEX_ID=$INDEX_ID,VERTEX_ENDPOINT_ID=$ENDPOINT_ID"
