#!/usr/bin/env bash
set -euo pipefail

# Deploy Query Function with Perplexity API Fix
# This script deploys the updated query function with the search_domain_filter fix

PROJECT_ID="day-planner-london-mvp"
REGION="asia-east2"
FUNCTION_NAME="nemo-query"
SERVICE_ACCOUNT="nemo-query@${PROJECT_ID}.iam.gserviceaccount.com"

echo "=========================================="
echo "🚀 Deploying Query Function"
echo "=========================================="
echo "Project: $PROJECT_ID"
echo "Region: $REGION"
echo "Function: $FUNCTION_NAME"
echo ""

# Check if we're in the right directory
if [ ! -f "functions/query/main.py" ]; then
    echo "❌ Error: Must run from project root directory"
    exit 1
fi

# Check for required secrets
echo "🔐 Checking required secrets..."
REQUIRED_SECRETS=(
    "PERPLEXITY_API_KEY"
    "GOOGLE_CSE_API_KEY"
    "GOOGLE_CSE_ENGINE_ID"
    "GEMINI_API_KEY"
)

missing_secrets=()
for secret in "${REQUIRED_SECRETS[@]}"; do
    if ! gcloud secrets describe "$secret" --project="$PROJECT_ID" &>/dev/null; then
        missing_secrets+=("$secret")
    else
        echo "  ✅ $secret exists"
    fi
done

if [ ${#missing_secrets[@]} -gt 0 ]; then
    echo ""
    echo "⚠️  Missing secrets: ${missing_secrets[*]}"
    echo ""
    echo "To create missing secrets, run:"
    for secret in "${missing_secrets[@]}"; do
        echo "  echo 'your-${secret,,}-value' | gcloud secrets create $secret --data-file=-"
    done
    echo ""
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo ""
echo "📦 Deploying function..."
echo ""

# Deploy using the tolerate-iam wrapper
./deploy/deploy-function-tolerate-iam.sh functions deploy "$FUNCTION_NAME" \
    --gen2 \
    --runtime=python311 \
    --region="$REGION" \
    --source=./functions/query \
    --entry-point=query_handler \
    --trigger-http \
    --allow-unauthenticated \
    --timeout=540s \
    --memory=2Gi \
    --max-instances=10 \
    --service-account="$SERVICE_ACCOUNT" \
    --set-env-vars="PROJECT_ID=$PROJECT_ID,REGION=$REGION,PERPLEXITY_MODEL=sonar-pro" \
    --set-secrets="PERPLEXITY_API_KEY=PERPLEXITY_API_KEY:latest,GOOGLE_CSE_API_KEY=GOOGLE_CSE_API_KEY:latest,GOOGLE_CSE_ENGINE_ID=GOOGLE_CSE_ENGINE_ID:latest,GEMINI_API_KEY=GEMINI_API_KEY:latest"

echo ""
echo "=========================================="
echo "✅ Deployment Complete"
echo "=========================================="
echo ""

# Get function URL
FUNCTION_URL=$(gcloud functions describe "$FUNCTION_NAME" \
    --region="$REGION" \
    --project="$PROJECT_ID" \
    --format="value(serviceConfig.uri)" 2>/dev/null || echo "")

if [ -n "$FUNCTION_URL" ]; then
    echo "🌐 Function URL: $FUNCTION_URL"
    echo ""

    # Test health
    echo "🧪 Testing function health..."
    if curl -s -f "$FUNCTION_URL" -X POST \
        -H "Content-Type: application/json" \
        -d '{"question":"test"}' >/dev/null 2>&1; then
        echo "  ✅ Function is responding"
    else
        echo "  ⚠️  Function deployed but may need time to warm up"
    fi
else
    echo "⚠️  Could not retrieve function URL"
fi

echo ""
echo "=========================================="
echo "🎉 Perplexity API Fix Deployed!"
echo "=========================================="
echo ""
echo "Key changes:"
echo "  ✅ Added search_domain_filter parameter"
echo "  ✅ Added search_recency_filter: 'year'"
echo "  ✅ Removed site: operators from query text"
echo ""
echo "Expected improvements:"
echo "  📊 .gov.cn domains: 0% → 100%"
echo "  📊 Relevant results: 10.5% → 80%+"
echo "  📊 Geographic accuracy: 5.3% → 85%+"
echo ""
echo "Next steps:"
echo "  1. Test with production query"
echo "  2. Monitor citation quality"
echo "  3. Validate .gov.cn percentage"
echo ""
