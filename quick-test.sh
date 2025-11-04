#!/bin/bash
# Quick test script for manual deployment

echo "🧪 Testing deployed functions..."

# Get function URLs
HEALTH_URL=$(gcloud functions describe nemo-health --region=us-central1 --format="value(serviceConfig.uri)" 2>/dev/null)
QUERY_URL=$(gcloud functions describe nemo-query --region=us-central1 --format="value(serviceConfig.uri)" 2>/dev/null)
INGEST_URL=$(gcloud functions describe nemo-ingest --region=us-central1 --format="value(serviceConfig.uri)" 2>/dev/null)

echo "📋 Function URLs:"
echo "Health: $HEALTH_URL"
echo "Query: $QUERY_URL" 
echo "Ingest: $INGEST_URL"

if [ ! -z "$HEALTH_URL" ]; then
    echo ""
    echo "🏥 Testing health endpoint..."
    curl -s "$HEALTH_URL" | jq . || curl -s "$HEALTH_URL"
fi

if [ ! -z "$QUERY_URL" ]; then
    echo ""
    echo "🔍 Testing query endpoint..."
    curl -s -X POST "$QUERY_URL" \
        -H "Content-Type: application/json" \
        -d '{"query": "test query"}' | jq . || echo "Query function deployed but may need secrets"
fi