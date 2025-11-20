#!/usr/bin/env bash
# ONE-COMMAND DEPLOYMENT SCRIPT
# Deploys both backend and frontend to Google Cloud

set -e

echo "=========================================="
echo "🚀 NEMO COMPLETE DEPLOYMENT"
echo "=========================================="
echo ""

# Configuration
PROJECT_ID="day-planner-london-mvp"
REGION="asia-east2"

# Check if Perplexity API key is set
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
echo "=========================================="
echo "📦 PART 1: BACKEND DEPLOYMENT"
echo "=========================================="
echo ""

# Deploy backend
./deploy-production.sh

# Get backend URL
BACKEND_URL=$(gcloud functions describe nemo-query \
    --region="$REGION" \
    --project="$PROJECT_ID" \
    --format="value(serviceConfig.uri)" 2>/dev/null || echo "")

if [ -z "$BACKEND_URL" ]; then
    echo "❌ Failed to get backend URL"
    exit 1
fi

echo ""
echo "✅ Backend deployed: $BACKEND_URL"
echo ""

echo "=========================================="
echo "🎨 PART 2: FRONTEND DEPLOYMENT"
echo "=========================================="
echo ""

# Configure frontend
echo "Step 1: Configuring frontend with backend URL..."
cd frontend
echo "VITE_API_URL=$BACKEND_URL" > .env

# Deploy frontend to Cloud Run
echo ""
echo "Step 2: Deploying frontend to Cloud Run..."
gcloud run deploy nemo-frontend \
    --source . \
    --region="$REGION" \
    --project="$PROJECT_ID" \
    --allow-unauthenticated \
    --platform managed \
    --port 8080 \
    --memory 512Mi \
    --cpu 1 \
    --min-instances 0 \
    --max-instances 10

# Get frontend URL
FRONTEND_URL=$(gcloud run services describe nemo-frontend \
    --region="$REGION" \
    --project="$PROJECT_ID" \
    --format="value(status.url)" 2>/dev/null || echo "")

cd ..

echo ""
echo "=========================================="
echo "🎉 DEPLOYMENT COMPLETE!"
echo "=========================================="
echo ""
echo "📊 Deployment Summary:"
echo "  Backend URL:  $BACKEND_URL"
echo "  Frontend URL: $FRONTEND_URL"
echo ""
echo "🧪 Testing:"
echo "  1. Open frontend: $FRONTEND_URL"
echo "  2. Select province: 广东省 (Guangdong)"
echo "  3. Select asset: 光伏 (Solar)"
echo "  4. Ask question: 并网验收需要哪些资料？"
echo "  5. Verify 100% .gov.cn citations"
echo ""
echo "📝 Next steps:"
echo "  - Test bilingual support (Chinese/English toggle)"
echo "  - Test chat history (new chat + switch between chats)"
echo "  - Monitor logs: gcloud functions logs read nemo-query"
echo "  - Set up custom domain (optional)"
echo ""
echo "🔗 Quick links:"
echo "  Frontend: $FRONTEND_URL"
echo "  Backend:  $BACKEND_URL"
echo "  GCP Console: https://console.cloud.google.com/run?project=$PROJECT_ID"
echo ""
