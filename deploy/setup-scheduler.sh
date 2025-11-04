#!/bin/bash

# Cloud Scheduler Setup Script
# Creates nightly ingestion job and monitoring

set -e

PROJECT_ID=${GOOGLE_CLOUD_PROJECT:-"your-project-id"}
REGION=${REGION:-"asia-east2"}
INGESTION_URL=""

echo "🕐 Setting up Cloud Scheduler for Nemo Compliance MVP"
echo "Project: $PROJECT_ID"
echo "Region: $REGION"

# Get ingestion function URL
echo "📡 Getting ingestion function URL..."
INGESTION_URL=$(gcloud functions describe nemo-ingest --region=$REGION --format="value(serviceConfig.uri)")

if [ -z "$INGESTION_URL" ]; then
    echo "❌ Error: Could not get ingestion function URL"
    echo "Make sure nemo-ingest function is deployed first"
    exit 1
fi

echo "Ingestion URL: $INGESTION_URL"

# Create service account for scheduler if it doesn't exist
echo "🔐 Creating service account for Cloud Scheduler..."
gcloud iam service-accounts create nemo-scheduler \
    --display-name="Nemo Compliance Scheduler" \
    --description="Service account for automated ingestion scheduling" \
    || echo "Service account already exists"

# Grant necessary permissions
echo "🔑 Granting permissions to service account..."
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:nemo-scheduler@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/cloudfunctions.invoker"

# Create nightly ingestion job
echo "⏰ Creating nightly ingestion job..."
gcloud scheduler jobs create http nemo-nightly-ingest \
    --location=$REGION \
    --schedule="0 21 * * *" \
    --time-zone="Asia/Shanghai" \
    --uri="$INGESTION_URL" \
    --http-method=POST \
    --headers="Content-Type=application/json,X-Ingest-Token=nemo-ingest-secure-token-2025" \
    --message-body='{"province":"all","asset":"all","doc_class":"grid"}' \
    --oidc-service-account-email="nemo-scheduler@$PROJECT_ID.iam.gserviceaccount.com" \
    --max-retry-attempts=3 \
    --max-retry-duration=1800s \
    || echo "Scheduler job already exists"

# Create weekly full refresh job
echo "📅 Creating weekly full refresh job..."
gcloud scheduler jobs create http nemo-weekly-refresh \
    --location=$REGION \
    --schedule="0 2 * * 0" \
    --time-zone="Asia/Shanghai" \
    --uri="$INGESTION_URL" \
    --http-method=POST \
    --headers="Content-Type=application/json,X-Ingest-Token=nemo-ingest-secure-token-2025" \
    --message-body='{"province":"all","asset":"all","doc_class":"grid","force_refresh":true}' \
    --oidc-service-account-email="nemo-scheduler@$PROJECT_ID.iam.gserviceaccount.com" \
    --max-retry-attempts=2 \
    --max-retry-duration=3600s \
    || echo "Weekly refresh job already exists"

# Test the scheduler job
echo "🧪 Testing scheduler job..."
gcloud scheduler jobs run nemo-nightly-ingest --location=$REGION

echo "✅ Cloud Scheduler setup complete!"
echo ""
echo "📋 Created jobs:"
echo "• nemo-nightly-ingest: Daily at 9 PM (Asia/Shanghai)"
echo "• nemo-weekly-refresh: Weekly on Sunday at 2 AM (Asia/Shanghai)"
echo ""
echo "🔍 Monitor jobs:"
echo "gcloud scheduler jobs list --location=$REGION"
echo ""
echo "📊 View job logs:"
echo "gcloud logging read 'resource.type=\"cloud_scheduler_job\"' --limit=50"