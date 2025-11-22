#!/usr/bin/env bash
# NEMO RAG SYSTEM DEPLOYMENT
# Deploys complete RAG system with Vertex AI primary + Perplexity fallback
# Architecture: Vector Search (PRIMARY) → Perplexity (FALLBACK) → Honest Refusal

set -e

echo "=========================================="
echo "🚀 NEMO RAG System Deployment"
echo "=========================================="
echo ""
echo "Architecture:"
echo "  ✅ Vertex AI Vector Search (PRIMARY - 90%+)"
echo "  ✅ Perplexity API (FALLBACK - <10%)"
echo "  ✅ Real document discovery with Perplexity"
echo "  ✅ Document ingestion pipeline"
echo ""

# Configuration
PROJECT_ID="${PROJECT_ID:-day-planner-london-mvp}"
REGION="${REGION:-asia-east2}"
INGEST_TOKEN="${INGEST_TOKEN:-secret123}"

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
echo "✅ Ingest token: ${INGEST_TOKEN:0:6}..."
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

# Create or update INGEST_TOKEN secret
if gcloud secrets describe INGEST_TOKEN --project="$PROJECT_ID" &>/dev/null; then
    echo "  Updating INGEST_TOKEN..."
    echo -n "$INGEST_TOKEN" | gcloud secrets versions add INGEST_TOKEN --data-file=-
else
    echo "  Creating INGEST_TOKEN..."
    echo -n "$INGEST_TOKEN" | gcloud secrets create INGEST_TOKEN --data-file=-
fi

echo ""
echo "Step 3: Deploying Query function (RAG-first architecture)..."
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
echo "Step 4: Deploying Ingest function (document discovery + ingestion)..."
echo ""

./deploy/deploy-function-tolerate-iam.sh functions deploy nemo-ingest \
    --gen2 \
    --runtime=python311 \
    --region="$REGION" \
    --source=./functions/ingest \
    --entry-point=ingest_handler \
    --trigger-http \
    --allow-unauthenticated \
    --timeout=540s \
    --memory=4Gi \
    --max-instances=3 \
    --set-env-vars="PROJECT_ID=$PROJECT_ID,REGION=$REGION" \
    --set-secrets="PERPLEXITY_API_KEY=PERPLEXITY_API_KEY:latest,INGEST_TOKEN=INGEST_TOKEN:latest"

echo ""
echo "=========================================="
echo "✅ Deployment Complete!"
echo "=========================================="
echo ""

# Get function URLs
QUERY_URL=$(gcloud functions describe nemo-query \
    --region="$REGION" \
    --project="$PROJECT_ID" \
    --format="value(serviceConfig.uri)" 2>/dev/null || echo "")

INGEST_URL=$(gcloud functions describe nemo-ingest \
    --region="$REGION" \
    --project="$PROJECT_ID" \
    --format="value(serviceConfig.uri)" 2>/dev/null || echo "")

if [ -n "$QUERY_URL" ]; then
    echo "🌐 Query Function URL: $QUERY_URL"
fi

if [ -n "$INGEST_URL" ]; then
    echo "🌐 Ingest Function URL: $INGEST_URL"
fi

echo ""
echo "=========================================="
echo "📊 Next Steps: Populate Vector Database"
echo "=========================================="
echo ""
echo "Your vector database is currently EMPTY. You need to ingest documents:"
echo ""
echo "Option 1: Automatic Discovery (Recommended)"
echo "  for province in gd sd nm; do"
echo "    for asset in solar coal wind; do"
echo "      echo \"Ingesting \$province \$asset...\""
echo "      curl -X POST $INGEST_URL \\"
echo "        -H \"X-Ingest-Token: $INGEST_TOKEN\" \\"
echo "        -H \"Content-Type: application/json\" \\"
echo "        -d '{\"province\":\"'\$province'\",\"asset\":\"'\$asset'\",\"doc_class\":\"grid\"}'"
echo "      sleep 30"
echo "    done"
echo "  done"
echo ""
echo "Option 2: Single Province/Asset"
echo "  curl -X POST $INGEST_URL \\"
echo "    -H \"X-Ingest-Token: $INGEST_TOKEN\" \\"
echo "    -H \"Content-Type: application/json\" \\"
echo "    -d '{\"province\":\"gd\",\"asset\":\"solar\",\"doc_class\":\"grid\"}'"
echo ""
echo "=========================================="
echo "🧪 Testing"
echo "=========================================="
echo ""
echo "Before ingestion (should return mode: perplexity_fallback):"
echo "  curl -X POST $QUERY_URL \\"
echo "    -H \"Content-Type: application/json\" \\"
echo "    -d '{\"province\":\"gd\",\"asset\":\"solar\",\"question\":\"并网验收需要什么资料？\",\"lang\":\"zh\"}' | jq .mode"
echo ""
echo "After ingestion (should return mode: vertex_rag):"
echo "  curl -X POST $QUERY_URL \\"
echo "    -H \"Content-Type: application/json\" \\"
echo "    -d '{\"province\":\"gd\",\"asset\":\"solar\",\"question\":\"并网验收需要什么资料？\",\"lang\":\"zh\"}' | jq"
echo ""
echo "=========================================="
echo "🎉 RAG System Ready!"
echo "=========================================="
echo ""
echo "Success Criteria:"
echo "  ✅ mode: 'vertex_rag' in 90%+ of queries (using YOUR documents)"
echo "  ✅ mode: 'perplexity_fallback' in <10% of queries (web search)"
echo "  ✅ Citations from curated government documents"
echo "  ✅ Response time <500ms"
echo "  ✅ 90%+ accuracy on manual review"
echo ""
