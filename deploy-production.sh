#!/usr/bin/env bash
# NEMO PRODUCTION DEPLOYMENT
# Deploy Perplexity-optimized backend with real API key

set -e

echo "=========================================="
echo "🚀 NEMO Production Deployment"
echo "=========================================="
echo ""

# Configuration
PROJECT_ID="day-planner-london-mvp"
REGION="asia-east2"

# Get API key from environment or prompt user
if [ -z "$PERPLEXITY_API_KEY" ]; then
    echo "⚠️  PERPLEXITY_API_KEY not set in environment"
    echo ""
    read -sp "Enter your Perplexity API key: " PERPLEXITY_API_KEY
    echo ""
    echo ""
fi

echo "✅ Using Perplexity API key (${PERPLEXITY_API_KEY:0:8}...)"
echo "✅ Google Cloud project: $PROJECT_ID"
echo "✅ Region: $REGION"
echo ""

# Set GCP project
echo "Step 1: Setting GCP project..."
gcloud config set project "$PROJECT_ID"

echo ""
echo "Step 2: Creating/updating secrets..."

# Create or update PERPLEXITY_API_KEY secret
if gcloud secrets describe PERPLEXITY_API_KEY --project="$PROJECT_ID" &>/dev/null; then
    echo "  Updating PERPLEXITY_API_KEY..."
    echo -n "$PERPLEXITY_API_KEY" | gcloud secrets versions add PERPLEXITY_API_KEY --data-file=-
else
    echo "  Creating PERPLEXITY_API_KEY..."
    echo -n "$PERPLEXITY_API_KEY" | gcloud secrets create PERPLEXITY_API_KEY --data-file=-
fi

echo ""
echo "Step 3: Deploying Query function (Perplexity-first, NO CSE)..."
echo ""

cd "$(dirname "$0")"

./deploy/deploy-function-tolerate-iam.sh functions deploy nemo-query \
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
    --set-env-vars="PROJECT_ID=$PROJECT_ID,REGION=$REGION,PERPLEXITY_MODEL=sonar-pro" \
    --set-secrets="PERPLEXITY_API_KEY=PERPLEXITY_API_KEY:latest"

echo ""
echo "=========================================="
echo "✅ Deployment Complete!"
echo "=========================================="
echo ""

# Get function URL
FUNCTION_URL=$(gcloud functions describe nemo-query \
    --region="$REGION" \
    --project="$PROJECT_ID" \
    --format="value(serviceConfig.uri)" 2>/dev/null || echo "")

if [ -n "$FUNCTION_URL" ]; then
    echo "🌐 Function URL: $FUNCTION_URL"
    echo ""

    echo "Step 4: Testing deployed function..."
    echo ""

    # Test with real query
    TEST_RESPONSE=$(curl -s -X POST "$FUNCTION_URL" \
        -H "Content-Type: application/json" \
        -d '{
            "question": "光伏发电项目土地勘测需要什么材料和流程",
            "province": "gd",
            "asset": "solar",
            "doc_class": "land_survey",
            "lang": "zh-CN"
        }')

    echo "$TEST_RESPONSE" | jq . 2>/dev/null || echo "$TEST_RESPONSE"

    # Count .gov.cn domains in response
    GOV_CN_COUNT=$(echo "$TEST_RESPONSE" | grep -o "\.gov\.cn" | wc -l || echo "0")

    echo ""
    echo "=========================================="
    echo "📊 Validation Results"
    echo "=========================================="
    echo ""
    echo ".gov.cn domains found: $GOV_CN_COUNT"

    if [ "$GOV_CN_COUNT" -gt 0 ]; then
        echo "✅ Fix is working! .gov.cn domains detected in citations"
    else
        echo "⚠️  No .gov.cn domains detected - check response above"
    fi
else
    echo "⚠️  Could not retrieve function URL"
fi

echo ""
echo "=========================================="
echo "🎉 NEMO Production Deployment Complete!"
echo "=========================================="
echo ""
echo "Architecture:"
echo "  ✅ Perplexity API (PRIMARY) - 90%+ queries"
echo "  ✅ Vertex AI (BACKUP) - <10% queries"
echo "  ❌ Google CSE - REMOVED"
echo ""
echo "Improvements:"
echo "  ✅ search_domain_filter parameter"
echo "  ✅ web_search_options: search_context_size=high"
echo "  ✅ temperature: 0.1 (factual precision)"
echo "  ✅ max_tokens: 4000"
echo "  ✅ return_related_questions: True"
echo "  ✅ Retry logic with exponential backoff"
echo ""
echo "Expected Results:"
echo "  📊 .gov.cn domains: 100%"
echo "  📊 Relevant results: 90-95%"
echo "  📊 Response time: <3s"
echo ""
