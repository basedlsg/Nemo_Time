# Manual Deployment Steps

## Prerequisites
```bash
# Set your project
gcloud config set project day-planner-london-mvp

# Enable required APIs
gcloud services enable cloudfunctions.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable storage.googleapis.com
```

## Step 1: Deploy Health Function
```bash
cd functions/health
gcloud functions deploy nemo-health \
    --gen2 \
    --runtime python311 \
    --region us-central1 \
    --source . \
    --entry-point health_handler \
    --trigger-http \
    --allow-unauthenticated \
    --memory 256MB \
    --timeout 30s
```

## Step 2: Deploy Query Function
```bash
cd ../query
gcloud functions deploy nemo-query \
    --gen2 \
    --runtime python311 \
    --region us-central1 \
    --source . \
    --entry-point query_handler \
    --trigger-http \
    --allow-unauthenticated \
    --set-secrets 'GEMINI_API_KEY=gemini-api-key:latest,PERPLEXITY_API_KEY=perplexity-api-key:latest,GOOGLE_CSE_ID=google-cse-id:latest,GOOGLE_API_KEY=google-api-key:latest' \
    --set-env-vars 'GOOGLE_CLOUD_PROJECT=day-planner-london-mvp,RAW_BUCKET=day-planner-london-mvp-nemo-raw,CLEAN_BUCKET=day-planner-london-mvp-nemo-clean' \
    --memory 1GB \
    --timeout 300s
```

## Step 3: Deploy Ingest Function
```bash
cd ../ingest
gcloud functions deploy nemo-ingest \
    --gen2 \
    --runtime python311 \
    --region us-central1 \
    --source . \
    --entry-point ingest_handler \
    --trigger-http \
    --allow-unauthenticated \
    --set-secrets 'INGEST_TOKEN=ingest-token:latest' \
    --set-env-vars 'GOOGLE_CLOUD_PROJECT=day-planner-london-mvp,RAW_BUCKET=day-planner-london-mvp-nemo-raw,CLEAN_BUCKET=day-planner-london-mvp-nemo-clean' \
    --memory 2GB \
    --timeout 540s
```

## Step 4: Test Deployment
```bash
# Get function URLs
gcloud functions describe nemo-health --region=us-central1 --format="value(serviceConfig.uri)"
gcloud functions describe nemo-query --region=us-central1 --format="value(serviceConfig.uri)"
gcloud functions describe nemo-ingest --region=us-central1 --format="value(serviceConfig.uri)"

# Test health endpoint
curl [HEALTH_URL]
```

## Troubleshooting
- If a function fails, check logs: `gcloud functions logs read [FUNCTION_NAME] --region=us-central1`
- If secrets are missing, create them in Secret Manager console
- If permissions fail, ensure your account has Cloud Functions Admin role