# Perplexity API Fix - Deployment Guide

## Overview

The Perplexity API domain filtering fix is complete and ready for deployment. This guide walks through testing and deploying the fix to production.

---

## What Was Fixed

**Problem**:
- 89% irrelevant results
- 0% .gov.cn domains
- `site:.gov.cn` operators in query text (ignored by Perplexity)

**Solution**:
- Added `search_domain_filter` API parameter (actually enforced)
- Added `search_recency_filter: "year"`
- Removed `site:` operators from query text

**Expected Impact**:
- .gov.cn domains: 0% → 100%
- Relevant results: 10.5% → 80%+
- Geographic accuracy: 5.3% → 85%+

---

## Prerequisites

### 1. GCP Project Access

```bash
gcloud config set project day-planner-london-mvp
gcloud auth login
```

### 2. Required Secrets

Create these secrets in GCP Secret Manager if they don't exist:

```bash
# Perplexity API Key (REQUIRED for fix)
echo 'your-perplexity-api-key' | gcloud secrets create PERPLEXITY_API_KEY --data-file=-

# Other required secrets
echo 'your-cse-api-key' | gcloud secrets create GOOGLE_CSE_API_KEY --data-file=-
echo 'your-cse-engine-id' | gcloud secrets create GOOGLE_CSE_ENGINE_ID --data-file=-
echo 'your-gemini-key' | gcloud secrets create GEMINI_API_KEY --data-file=-
```

### 3. Enable Required APIs

```bash
gcloud services enable cloudfunctions.googleapis.com
gcloud services enable secretmanager.googleapis.com
gcloud services enable cloudbuild.googleapis.com
```

---

## Step 1: Test Locally (Optional but Recommended)

Test the Perplexity API fix with a live API call:

```bash
# Set your API key
export PERPLEXITY_API_KEY='your_api_key_here'

# Run the test
python3 test_perplexity_api.py
```

**Expected Output**:
```
✅ API call successful!
📊 RESULTS SUMMARY
Total Citations: 6
.gov.cn Domains: 6/6 (100.0%)

🎉 SUCCESS! 100.0% .gov.cn domains
```

If the test passes, you're ready to deploy!

---

## Step 2: Deploy to GCP Cloud Functions

Deploy the updated query function:

```bash
./deploy-query-function.sh
```

This script will:
1. ✅ Check for required secrets
2. ✅ Deploy the function with Gen2 runtime
3. ✅ Configure environment variables
4. ✅ Set up secret mounts
5. ✅ Test function health

**Deployment takes ~2-3 minutes.**

---

## Step 3: Verify Production Deployment

### Quick Health Check

```bash
./quick-test.sh
```

### Manual Test

Get your function URL:

```bash
gcloud functions describe nemo-query \
  --region=asia-east2 \
  --format="value(serviceConfig.uri)"
```

Test with the original failing query:

```bash
curl -X POST "YOUR_FUNCTION_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "光伏发电项目土地勘测需要什么材料和流程",
    "province": "gd",
    "asset": "solar",
    "doc_class": "land_survey",
    "lang": "zh-CN"
  }' | jq .
```

### Validate Results

Check the response for:
- ✅ `citations` array has 3-6 items
- ✅ All URLs end with `.gov.cn`
- ✅ Domains include `gd.gov.cn`, `nr.gd.gov.cn`, `mnr.gov.cn`, etc.
- ✅ `answer_zh` contains relevant Chinese regulatory guidance

---

## Step 4: Monitor Production

### Check Function Logs

```bash
gcloud functions logs read nemo-query \
  --region=asia-east2 \
  --limit=50
```

### Monitor Metrics

```bash
gcloud monitoring dashboards list
```

Look for:
- Response latency < 5s
- Error rate < 5%
- Citation quality (manual spot checks)

---

## Troubleshooting

### Issue: "PERPLEXITY_API_KEY not found"

**Solution**: Create the secret in Secret Manager:

```bash
echo 'your-key' | gcloud secrets create PERPLEXITY_API_KEY --data-file=-
```

Then redeploy:

```bash
./deploy-query-function.sh
```

### Issue: "Permission denied" during deployment

**Solution**: Grant Cloud Build permissions:

```bash
./deploy/grant-cloud-build-permissions.sh
```

### Issue: Function deployed but returns errors

**Solution**: Check function logs:

```bash
gcloud functions logs read nemo-query --region=asia-east2 --limit=100
```

Common errors:
- Missing secrets → Create them in Secret Manager
- Vertex AI not initialized → Run `./deploy/setup-vertex-ai.sh`
- IAM permissions → Run `./deploy/grant-permissions.sh`

---

## Rollback (if needed)

If the deployment causes issues, rollback to previous version:

```bash
# List recent revisions
gcloud functions describe nemo-query \
  --region=asia-east2 \
  --format="value(serviceConfig.revision)"

# Rollback to specific revision
gcloud functions deploy nemo-query \
  --region=asia-east2 \
  --image=PREVIOUS_IMAGE_URL
```

---

## Files Changed

| File | Purpose |
|------|---------|
| `functions/query/perplexity.py` | Core fix implementation |
| `deploy-query-function.sh` | Deployment script |
| `test_perplexity_api.py` | Live API test |
| `PERPLEXITY_FIX_IMPLEMENTATION.md` | Technical details |

---

## Success Criteria

**Before Fix**:
- ❌ 0% .gov.cn domains
- ❌ 89% irrelevant results
- ❌ Domain filtering not working

**After Fix**:
- ✅ 100% .gov.cn domains
- ✅ 80%+ relevant results
- ✅ Domain filtering working

---

## Next Steps After Deployment

1. **Monitor for 24 hours**: Check logs and metrics
2. **Spot-check queries**: Validate citation quality manually
3. **Update documentation**: Document any issues found
4. **Scale if needed**: Increase max-instances if traffic spikes

---

## Support

**Issues**: https://github.com/basedlsg/Nemo_Time/issues

**Key Contacts**:
- Project: day-planner-london-mvp
- Region: asia-east2
- Function: nemo-query

---

**Deployment Status**: ✅ Ready to deploy
**Estimated Time**: 5-10 minutes (including tests)
**Risk Level**: Low (simple parameter change)
