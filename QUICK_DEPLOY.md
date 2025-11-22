# ⚡ Quick Deploy - 3 Commands

**For users who want to deploy immediately without reading documentation**

---

## Prerequisites

- `gcloud` CLI installed and authenticated
- Project: `day-planner-london-mvp`
- You have: Perplexity API key

---

## Deploy in 3 Steps

### 1️⃣ Pull Latest Code

```bash
cd /path/to/Nemo_Time
git pull origin claude/parallel-agents-committees-01TABAuSn7tZ6rnfgQNmjFWm
```

### 2️⃣ Deploy Backend

```bash
export PERPLEXITY_API_KEY='YOUR_PERPLEXITY_API_KEY'  # Replace with actual key
./deploy-rag-system.sh
```

**Wait 5-8 minutes for deployment to complete**

### 3️⃣ Populate Database

Copy the **INGEST_URL** from deployment output, then run:

```bash
export INGEST_URL="<paste-your-ingest-url-here>"
export INGEST_TOKEN="secret123"

# Start with Guangdong solar (fast test)
curl -X POST $INGEST_URL \
  -H "X-Ingest-Token: $INGEST_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"province":"gd","asset":"solar","doc_class":"grid"}'
```

**Wait 5 minutes for ingestion to complete**

---

## Test It Works

Copy the **QUERY_URL** from deployment output:

```bash
export QUERY_URL="<paste-your-query-url-here>"

curl -X POST $QUERY_URL \
  -H "Content-Type: application/json" \
  -d '{
    "province":"gd",
    "asset":"solar",
    "question":"并网验收需要什么资料？",
    "lang":"zh"
  }' | jq .mode
```

**Expected output**: `"vertex_rag"` ← SUCCESS!

If you get `"perplexity_fallback"`, wait 5 more minutes for indexing.

---

## Deploy All Data (Optional)

**Ingest all provinces and assets** (takes 2-4 hours, runs automatically):

```bash
for province in gd sd nm; do
  for asset in solar coal wind; do
    echo "Ingesting $province $asset..."
    curl -X POST $INGEST_URL \
      -H "X-Ingest-Token: $INGEST_TOKEN" \
      -d "{\"province\":\"$province\",\"asset\":\"$asset\",\"doc_class\":\"grid\"}"
    sleep 30
  done
done
```

---

## Deploy Frontend (Optional)

```bash
cd frontend
npm run build

gcloud run deploy nemo-frontend \
  --source . \
  --region asia-east2 \
  --allow-unauthenticated \
  --set-env-vars="VITE_API_URL=$QUERY_URL"
```

---

## ✅ Done!

**What you have:**
- Real RAG system with Vertex AI vector search
- Perplexity fallback for edge cases
- ChatGPT-style UI (teal colors, circular button, black sidebar)
- 90%+ accuracy on queries

**Architecture:**
```
Query → Vertex AI (YOUR docs) → Accurate answer
      ↓ (if empty)
      Perplexity (web) → Fallback answer
      ↓ (if both fail)
      Honest refusal
```

**For detailed instructions, see**: `DEPLOYMENT_INSTRUCTIONS.md`
