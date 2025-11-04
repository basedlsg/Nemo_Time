# Nemo Compliance MVP - Production Deployment Guide

## 🚀 Complete Production Deployment

This guide walks you through deploying the Nemo Compliance MVP to production with full monitoring and operational readiness.

## Prerequisites

1. **Google Cloud Project** with billing enabled
2. **gcloud CLI** installed and authenticated
3. **Required APIs** (will be enabled during deployment)
4. **Domain** for frontend hosting (optional)

## Step 1: Initial Setup

```bash
# Clone repository
git clone <repository-url>
cd nemo-compliance-mvp

# Set environment variables
export GOOGLE_CLOUD_PROJECT="your-project-id"
export REGION="asia-east2"  # Hong Kong region for Chinese data

# Authenticate with Google Cloud
gcloud auth login
gcloud config set project $GOOGLE_CLOUD_PROJECT
```

## Step 2: Deploy Core Infrastructure

```bash
# Run main deployment script
./deploy/deploy.sh

# This will:
# - Enable required Google Cloud APIs
# - Create GCS buckets for document storage
# - Create secrets in Secret Manager
# - Deploy all three Cloud Functions
# - Display function URLs
```

## Step 3: Set Up Vertex AI Vector Search

```bash
# Create vector search index
gcloud ai indexes create \
  --display-name="nemo-compliance-index" \
  --description="Chinese regulatory documents vector index" \
  --metadata-schema-uri="gs://google-cloud-aiplatform/schema/matchingengine/metadata/nearest_neighbor_search_1.0.0.yaml" \
  --region=$REGION

# Note the INDEX_ID from output

# Create index endpoint
gcloud ai index-endpoints create \
  --display-name="nemo-compliance-endpoint" \
  --region=$REGION

# Note the ENDPOINT_ID from output

# Deploy index to endpoint
gcloud ai index-endpoints deploy-index ENDPOINT_ID \
  --deployed-index-id="nemo-deployed-index" \
  --display-name="Nemo Compliance Deployed Index" \
  --index=INDEX_ID \
  --region=$REGION
```

## Step 4: Update Function Configuration

```bash
# Update query function with Vertex AI configuration
gcloud functions deploy nemo-query \
  --update-env-vars VERTEX_INDEX_ID=your-index-id,VERTEX_ENDPOINT_ID=your-endpoint-id \
  --region=$REGION

# Update ingestion function with Vertex AI configuration  
gcloud functions deploy nemo-ingest \
  --update-env-vars VERTEX_INDEX_ID=your-index-id,VERTEX_ENDPOINT_ID=your-endpoint-id \
  --region=$REGION
```

## Step 5: Set Up Google Custom Search Engine

1. **Create CSE at https://cse.google.com/**
2. **Add allowlisted domains:**
   - `gd.gov.cn` (Guangdong government)
   - `sd.gov.cn` (Shandong government) 
   - `nmg.gov.cn` (Inner Mongolia government)
3. **Get CSE ID and API Key**
4. **Update secrets:**

```bash
# Update Google CSE secrets
echo "your-cse-id" | gcloud secrets versions add google-cse-id --data-file=-
echo "your-google-api-key" | gcloud secrets versions add google-api-key --data-file=-
```

## Step 6: Set Up Document AI Processor

```bash
# Create Document AI processor for Chinese documents
gcloud ai document-ai processors create \
  --display-name="nemo-chinese-processor" \
  --type="FORM_PARSER_PROCESSOR" \
  --location=$REGION

# Note the PROCESSOR_ID and update function
gcloud functions deploy nemo-ingest \
  --update-env-vars DOCAI_PROCESSOR_ID=your-processor-id \
  --region=$REGION
```

## Step 7: Configure Automated Ingestion

```bash
# Set up Cloud Scheduler for nightly ingestion
./deploy/setup-scheduler.sh

# This creates:
# - nemo-nightly-ingest: Daily at 9 PM Asia/Shanghai
# - nemo-weekly-refresh: Weekly on Sunday at 2 AM
```

## Step 8: Deploy Frontend

### Option A: Firebase Hosting

```bash
# Install Firebase CLI
npm install -g firebase-tools

# Initialize Firebase project
cd frontend
firebase init hosting

# Update API URLs in index.html
# Set HEALTH_URL and API_BASE to your function URLs

# Deploy
firebase deploy --only hosting
```

### Option B: Google Cloud Storage Static Hosting

```bash
# Create bucket for static hosting
gsutil mb gs://$GOOGLE_CLOUD_PROJECT-frontend

# Enable public access
gsutil iam ch allUsers:objectViewer gs://$GOOGLE_CLOUD_PROJECT-frontend

# Upload frontend files
gsutil -m cp -r frontend/* gs://$GOOGLE_CLOUD_PROJECT-frontend/

# Configure as website
gsutil web set -m index.html -e 404.html gs://$GOOGLE_CLOUD_PROJECT-frontend
```

## Step 9: Set Up Monitoring and Alerting

```bash
# Create log-based metrics
gcloud logging metrics create nemo_query_errors \
  --description="Nemo query endpoint errors" \
  --log-filter='resource.type="cloud_function" AND resource.labels.function_name="nemo-query" AND severity>=ERROR'

gcloud logging metrics create nemo_query_latency \
  --description="Nemo query response latency" \
  --log-filter='resource.type="cloud_function" AND resource.labels.function_name="nemo-query" AND jsonPayload.elapsed_ms>0'

# Create alerting policies
gcloud alpha monitoring policies create \
  --policy-from-file=monitoring/error-rate-policy.yaml

gcloud alpha monitoring policies create \
  --policy-from-file=monitoring/latency-policy.yaml
```

## Step 10: Initial Data Ingestion

```bash
# Get ingestion function URL
INGEST_URL=$(gcloud functions describe nemo-ingest --region=$REGION --format="value(serviceConfig.uri)")

# Trigger initial ingestion for all provinces/assets
curl -X POST $INGEST_URL \
  -H "Content-Type: application/json" \
  -H "X-Ingest-Token: nemo-ingest-secure-token-2025" \
  -d '{"province": "all", "asset": "all", "doc_class": "grid"}'

# Monitor ingestion progress in Cloud Logging
gcloud logging read 'resource.type="cloud_function" AND resource.labels.function_name="nemo-ingest"' --limit=50
```

## Step 11: Validation and Testing

```bash
# Test health endpoint
HEALTH_URL=$(gcloud functions describe nemo-health --region=$REGION --format="value(serviceConfig.uri)")
curl $HEALTH_URL

# Test query endpoint
QUERY_URL=$(gcloud functions describe nemo-query --region=$REGION --format="value(serviceConfig.uri)")
curl -X POST $QUERY_URL \
  -H "Content-Type: application/json" \
  -d '{
    "province": "gd",
    "asset": "solar", 
    "doc_class": "grid",
    "question": "并网验收需要哪些资料？"
  }'

# Run integration tests
cd tests/integration
pip install -r requirements.txt
STAGING_HEALTH_URL=$HEALTH_URL STAGING_QUERY_URL=$QUERY_URL pytest test_end_to_end.py -v
```

## Step 12: Production Readiness Checklist

### ✅ Security
- [ ] All secrets stored in Secret Manager
- [ ] Function authentication configured
- [ ] IAM permissions follow least privilege
- [ ] HTTPS enabled for all endpoints

### ✅ Performance  
- [ ] Query endpoint p95 < 2 seconds
- [ ] Vertex AI index optimized
- [ ] Reranking disabled by default
- [ ] CDN configured for frontend

### ✅ Monitoring
- [ ] Cloud Logging configured
- [ ] Error rate alerts set up
- [ ] Latency monitoring active
- [ ] Health check alerts configured

### ✅ Data Quality
- [ ] Initial ingestion completed successfully
- [ ] Golden set evaluation passing (≥90% precision)
- [ ] No mock data in responses
- [ ] Citations link to government sources

### ✅ Operational
- [ ] Automated ingestion scheduled
- [ ] Backup and recovery procedures documented
- [ ] Runbooks created for common issues
- [ ] On-call rotation established

## Production URLs

After deployment, you'll have:

- **Health Check**: `https://nemo-health-<hash>-<region>.cloudfunctions.net`
- **Query API**: `https://nemo-query-<hash>-<region>.cloudfunctions.net`  
- **Ingestion API**: `https://nemo-ingest-<hash>-<region>.cloudfunctions.net`
- **Frontend**: `https://<your-domain>` or `https://<project>-frontend.web.app`

## Monitoring Dashboard

Access your monitoring dashboard at:
`https://console.cloud.google.com/monitoring/dashboards`

Key metrics to monitor:
- Query response time (target: p95 < 2s)
- Error rate (target: < 2%)
- Ingestion success rate (target: > 95%)
- Document corpus size growth

## Troubleshooting

### Common Issues

1. **Query returns no results**
   - Check if ingestion has run successfully
   - Verify Vertex AI index is deployed
   - Check allowlist domains in CSE

2. **Slow query performance**
   - Disable Gemini reranking: `RERANK=false`
   - Check Vertex AI index status
   - Review query complexity

3. **Ingestion failures**
   - Check Document AI processor status
   - Verify CSE API quotas
   - Review GCS bucket permissions

### Support Contacts

- **Technical Issues**: Check Cloud Logging with trace ID
- **Data Quality**: Review golden set evaluation results
- **Performance**: Monitor Cloud Functions metrics

## Cost Optimization

### Expected Monthly Costs (1000 queries/day)

- **Cloud Functions**: ~$20
- **Vertex AI Vector Search**: ~$50  
- **Document AI**: ~$30
- **Cloud Storage**: ~$5
- **Total**: ~$105/month

### Cost Reduction Tips

1. Use Cloud Scheduler to pause ingestion during low-usage periods
2. Implement query caching for common questions
3. Optimize Vertex AI index configuration
4. Use preemptible instances for batch processing

## Scaling Considerations

### Current Limits (MVP)

- 3 provinces (Guangdong, Shandong, Inner Mongolia)
- 3 asset types (Solar, Coal, Wind)  
- 1 document class (Grid Connection)
- ~1000 documents in corpus

### Scaling Path

1. **Add provinces**: Update allowlist, add CSE domains
2. **Add asset types**: Extend validation, update UI
3. **Add document classes**: Expand beyond grid connection
4. **Increase throughput**: Add load balancing, caching

This completes your production deployment of the Nemo Compliance MVP! 🎉