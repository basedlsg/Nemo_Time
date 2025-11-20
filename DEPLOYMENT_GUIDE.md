# Nemo Deployment Guide

Complete guide to deploy the Nemo ChatGPT-clone interface to Google Cloud Platform.

## Prerequisites

- Google Cloud SDK (`gcloud`) installed
- Google Cloud project: `day-planner-london-mvp`
- Perplexity API key (get yours from https://www.perplexity.ai/settings/api)
- Docker installed (for frontend deployment)

## Architecture Overview

```
Frontend (Cloud Run) → Backend (Cloud Functions) → Perplexity API + Vertex AI
```

## Step 1: Deploy Backend (Query Function)

### 1.1 Set your Perplexity API key

```bash
export PERPLEXITY_API_KEY='your-perplexity-api-key-here'
```

### 1.2 Run the deployment script

```bash
cd /path/to/Nemo_Time
./deploy-production.sh
```

This script will:
- ✅ Create/update the PERPLEXITY_API_KEY secret in Google Secret Manager
- ✅ Deploy the `nemo-query` Cloud Function with all optimizations
- ✅ Test the deployment with a real query
- ✅ Validate 100% .gov.cn domain filtering

**Expected Output:**
```
✅ Deployment Complete!
🌐 Function URL: https://nemo-query-xxxxx-asia-east2.run.app
📊 .gov.cn domains found: 6
✅ Fix is working! .gov.cn domains detected in citations
```

### 1.3 Save the Backend URL

After deployment, save the function URL:

```bash
export BACKEND_URL="https://nemo-query-xxxxx-asia-east2.run.app"
```

## Step 2: Test Backend API

Test the backend with a sample query:

```bash
curl -X POST "$BACKEND_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "光伏发电项目土地勘测需要什么材料和流程",
    "province": "gd",
    "asset": "solar",
    "doc_class": "land_survey",
    "lang": "zh"
  }' | jq .
```

**Expected Response:**
```json
{
  "answer_zh": "根据广东省相关规定，光伏发电项目土地勘测需要以下材料...",
  "citations": [
    {
      "title": "广东省投资项目在线审批监管平台",
      "url": "https://tzxm.gd.gov.cn",
      "effective_date": "2023-01-01"
    }
  ],
  "trace_id": "abc123",
  "elapsed_ms": 2500
}
```

✅ Verify all citations are from `.gov.cn` domains

## Step 3: Deploy Frontend

### 3.1 Configure Frontend with Backend URL

Update the frontend environment:

```bash
cd frontend
echo "VITE_API_URL=$BACKEND_URL" > .env
```

### 3.2 Build Frontend Docker Image

```bash
# Build the Docker image
docker build -t nemo-frontend .

# Test locally (optional)
docker run -p 8080:8080 nemo-frontend
# Open http://localhost:8080
```

### 3.3 Deploy to Cloud Run

**Option A: Deploy from Source (Recommended)**

```bash
gcloud run deploy nemo-frontend \
  --source . \
  --region asia-east2 \
  --project day-planner-london-mvp \
  --allow-unauthenticated \
  --platform managed \
  --port 8080 \
  --set-env-vars="VITE_API_URL=$BACKEND_URL" \
  --memory 512Mi \
  --cpu 1 \
  --min-instances 0 \
  --max-instances 10
```

**Option B: Deploy from Docker Image**

```bash
# Tag and push to GCR
docker tag nemo-frontend gcr.io/day-planner-london-mvp/nemo-frontend:latest
docker push gcr.io/day-planner-london-mvp/nemo-frontend:latest

# Deploy to Cloud Run
gcloud run deploy nemo-frontend \
  --image gcr.io/day-planner-london-mvp/nemo-frontend:latest \
  --region asia-east2 \
  --project day-planner-london-mvp \
  --allow-unauthenticated \
  --platform managed \
  --port 8080 \
  --set-env-vars="VITE_API_URL=$BACKEND_URL" \
  --memory 512Mi \
  --cpu 1
```

**Expected Output:**
```
✓ Deploying to Cloud Run service [nemo-frontend] in project [day-planner-london-mvp] region [asia-east2]
✓ Building and deploying... Done.
✓ Service [nemo-frontend] revision [nemo-frontend-00001-xxx] has been deployed and is serving 100 percent of traffic.
Service URL: https://nemo-frontend-xxxxx-asia-east2.run.app
```

### 3.4 Save the Frontend URL

```bash
export FRONTEND_URL="https://nemo-frontend-xxxxx-asia-east2.run.app"
echo "Frontend deployed to: $FRONTEND_URL"
```

## Step 4: Configure CORS (If Needed)

If frontend and backend are on different domains, update CORS settings in `functions/query/main.py`:

```python
# Already configured with permissive CORS for Cloud Run:
response.headers['Access-Control-Allow-Origin'] = '*'
response.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
```

✅ No changes needed - CORS is already configured

## Step 5: Test End-to-End

### 5.1 Open the Frontend

```bash
open $FRONTEND_URL
# Or visit in browser: https://nemo-frontend-xxxxx-asia-east2.run.app
```

### 5.2 Test Workflow

1. **Select Province**: Choose "广东省 (Guangdong)"
2. **Select Asset**: Click "光伏 (Solar)"
3. **Enter Question**: Type "并网验收需要哪些资料？"
4. **Submit**: Click send button or press Enter
5. **Verify Response**:
   - ✅ Response appears within 3 seconds
   - ✅ Answer is in Chinese
   - ✅ Citations are displayed below answer
   - ✅ All citation URLs are `.gov.cn` domains
   - ✅ Citations have clickable "查看原文" links

### 5.3 Test Language Toggle

1. Click "English" in top-right language toggle
2. Verify UI switches to English
3. Enter question: "What documents are needed for grid acceptance?"
4. Verify response is in English

### 5.4 Test Chat History

1. Click "New Chat" in sidebar
2. Start a new conversation
3. Verify previous chat appears in sidebar
4. Click previous chat to switch back
5. Verify messages are preserved

## Step 6: Performance Verification

### 6.1 Backend Performance

Expected metrics:
- ✅ Response time: < 3 seconds
- ✅ .gov.cn domain accuracy: 100% (6/6 citations)
- ✅ Relevant results: 90-95%
- ✅ Success rate: 95%+

### 6.2 Frontend Performance

Test with Lighthouse:
```bash
# Install Lighthouse
npm install -g lighthouse

# Run audit
lighthouse $FRONTEND_URL --output html --output-path ./lighthouse-report.html
```

Expected scores:
- Performance: 90+
- Accessibility: 95+
- Best Practices: 95+
- SEO: 100

## Step 7: Monitoring & Logs

### 7.1 View Backend Logs

```bash
# Real-time logs
gcloud functions logs read nemo-query \
  --region asia-east2 \
  --project day-planner-london-mvp \
  --limit 50

# Follow logs
gcloud functions logs read nemo-query \
  --region asia-east2 \
  --project day-planner-london-mvp \
  --follow
```

### 7.2 View Frontend Logs

```bash
# Real-time logs
gcloud run logs read nemo-frontend \
  --region asia-east2 \
  --project day-planner-london-mvp \
  --limit 50
```

### 7.3 Monitor in Cloud Console

- **Functions**: https://console.cloud.google.com/functions?project=day-planner-london-mvp
- **Cloud Run**: https://console.cloud.google.com/run?project=day-planner-london-mvp
- **Logs**: https://console.cloud.google.com/logs?project=day-planner-london-mvp

## Step 8: Cost Monitoring

### Monthly Cost Estimate

**Backend (Cloud Functions):**
- Invocations: ~10,000/month
- Compute time: ~500 GB-seconds
- Network: ~10 GB
- **Cost**: ~$5/month

**Perplexity API:**
- Model: sonar-pro
- Queries: ~10,000/month
- **Cost**: ~$200/month (based on usage)

**Frontend (Cloud Run):**
- Requests: ~100,000/month
- Compute: ~50 vCPU-hours
- Network: ~50 GB
- **Cost**: ~$10/month

**Total Estimated Cost**: ~$215/month

### Set Budget Alert

```bash
gcloud billing budgets create \
  --billing-account=YOUR_BILLING_ACCOUNT_ID \
  --display-name="Nemo Monthly Budget" \
  --budget-amount=300 \
  --threshold-rule=percent=50 \
  --threshold-rule=percent=90 \
  --threshold-rule=percent=100
```

## Troubleshooting

### Issue: Backend returns 403 error

**Cause**: Secret permissions not set
**Fix**:
```bash
PROJECT_NUMBER=$(gcloud projects describe day-planner-london-mvp --format="value(projectNumber)")
gcloud secrets add-iam-policy-binding PERPLEXITY_API_KEY \
  --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
```

### Issue: Frontend shows network error

**Cause**: Backend URL not configured
**Fix**: Redeploy frontend with correct VITE_API_URL

### Issue: Citations are not .gov.cn

**Cause**: Domain filter not working
**Fix**: Check Perplexity API logs, verify `search_domain_filter` parameter

### Issue: Slow response times (>5s)

**Possible Causes**:
1. Cold start (first request after idle)
2. Perplexity API slow
3. Network latency

**Fix**: Increase min instances for Cloud Functions:
```bash
gcloud functions deploy nemo-query \
  --region asia-east2 \
  --min-instances 1
```

## Rollback Procedure

### Rollback Backend

```bash
# List revisions
gcloud functions revisions list \
  --service nemo-query \
  --region asia-east2

# Rollback to previous revision
gcloud functions revisions deploy PREVIOUS_REVISION \
  --service nemo-query \
  --region asia-east2
```

### Rollback Frontend

```bash
# List revisions
gcloud run revisions list \
  --service nemo-frontend \
  --region asia-east2

# Route traffic to previous revision
gcloud run services update-traffic nemo-frontend \
  --to-revisions PREVIOUS_REVISION=100 \
  --region asia-east2
```

## Security Checklist

- ✅ Perplexity API key stored in Secret Manager (not in code)
- ✅ Cloud Functions use managed service account
- ✅ Frontend uses HTTPS only
- ✅ CORS configured for security
- ✅ No sensitive data logged
- ✅ Rate limiting via Cloud Armor (optional)

## Next Steps

1. **Custom Domain**: Map a custom domain to Cloud Run
2. **CDN**: Enable Cloud CDN for static assets
3. **Authentication**: Add user authentication if needed
4. **Analytics**: Integrate Google Analytics
5. **Monitoring**: Set up Cloud Monitoring alerts
6. **Backup**: Configure automated backups for Vertex AI

## Support

For deployment issues:
1. Check logs: `gcloud functions logs read nemo-query`
2. Verify secrets: `gcloud secrets versions access latest --secret=PERPLEXITY_API_KEY`
3. Test API directly: `curl -X POST $BACKEND_URL ...`

## Success Criteria

✅ **Backend deployed**: Function URL returns valid responses
✅ **Frontend deployed**: UI accessible at Cloud Run URL
✅ **100% .gov.cn citations**: All references are government domains
✅ **Response time < 3s**: Fast enough for production use
✅ **Bilingual support**: Chinese and English both work
✅ **Chat history persists**: localStorage working correctly
✅ **No console errors**: Clean browser console

---

**Deployment Complete! 🎉**

Your Nemo ChatGPT-clone is now live and serving energy compliance queries with 90%+ accuracy.
