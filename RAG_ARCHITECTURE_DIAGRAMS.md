# RAG ARCHITECTURE VISUAL DIAGRAMS

## 1. CURRENT SYSTEM ARCHITECTURE (Perplexity-First)

```
┌──────────────────────────────────────────────────────────────────────┐
│                     USER QUERY FLOW (CURRENT)                        │
└──────────────────────────────────────────────────────────────────────┘

User Query: "广东光伏并网需要什么资料？"
   │
   │ POST /query
   ↓
┌─────────────────────────────────┐
│   Cloud Function: nemo-query    │
│   (functions/query/main.py)     │
└─────────────────────────────────┘
   │
   ├─→ Step 1: normalize_query()
   │   │
   │   └─→ "广东光伏并网需要什么资料"
   │
   ├─→ Step 2: answer_with_perplexity() ⭐ PRIMARY PATH
   │   │
   │   ├─→ Perplexity API Request
   │   │   ├─ Model: sonar-pro
   │   │   ├─ Domain filter: [gd.gov.cn, nea.gov.cn, ndrc.gov.cn, ...]
   │   │   ├─ Search recency: 1 year
   │   │   └─ Return citations: true
   │   │
   │   ├─→ Perplexity searches LIVE WEB
   │   │   ├─ Finds: https://gd.gov.cn/some-policy.html
   │   │   ├─ Finds: https://ndrc.gov.cn/renewable-rules.pdf
   │   │   └─ Extracts answer from web pages
   │   │
   │   └─→ SUCCESS ✅
   │       ├─ answer_zh: "根据广东省规定，光伏并网需要..."
   │       ├─ citations: [{title: "...", url: "gd.gov.cn/..."}]
   │       └─ mode: "perplexity_qa"
   │
   └─→ RETURN Response
       │
       └─→ {
             "answer_zh": "根据广东省规定，光伏并网需要...",
             "citations": [...],
             "mode": "perplexity_qa",  ⬅️ ALWAYS THIS MODE
             "elapsed_ms": 2500
           }

┌─────────────────────────────────────────────────────────────────────┐
│  FALLBACK PATH (NEVER REACHED)                                      │
└─────────────────────────────────────────────────────────────────────┘

If Perplexity fails:
   │
   ├─→ Step 3: embed_query()
   │   └─→ query_vector: [0.123, -0.456, ..., 0.789]  (768 dims)
   │
   ├─→ Step 4: search_documents(query_vector, filters)
   │   │
   │   ├─→ Vertex AI Vector Search
   │   │   ├─ Index: nemo-compliance-index
   │   │   ├─ Endpoint: nemo-compliance-endpoint
   │   │   ├─ Filters: {province: 'gd', asset: 'solar', doc_class: 'grid'}
   │   │   └─ Top-K: 12
   │   │
   │   └─→ EMPTY RESULTS ❌ (No documents in database)
   │       └─ candidates: []
   │
   └─→ Step 5: Refusal Response
       └─→ {
             "mode": "vertex_rag",
             "refusal": "未找到相关的一手资料。",
             "tips": ["请指定省份与资产类型", ...],
             "elapsed_ms": 500
           }

════════════════════════════════════════════════════════════════════════
PROBLEM: This is NOT RAG - it's web search with domain filtering
════════════════════════════════════════════════════════════════════════
```

---

## 2. INTENDED RAG ARCHITECTURE (What We Need)

```
┌──────────────────────────────────────────────────────────────────────┐
│                  OFFLINE INGESTION PIPELINE (NEEDED)                 │
└──────────────────────────────────────────────────────────────────────┘

Cloud Scheduler (Daily 2am)
   │
   │ Triggers
   ↓
┌─────────────────────────────────┐
│  Cloud Function: nemo-ingest    │
│  (functions/ingest/main.py)     │
└─────────────────────────────────┘
   │
   ├─→ Step 1: discover_documents() ❌ MISSING MODULE
   │   │
   │   ├─→ lib/cse.py (DOES NOT EXIST)
   │   │   │
   │   │   ├─ Google Custom Search API
   │   │   ├─ Query: "site:gd.gov.cn 光伏 并网 filetype:pdf"
   │   │   ├─ Filter: .gov.cn domains only
   │   │   └─ Returns: [url1, url2, url3, ...]
   │   │
   │   └─→ discovered_urls: [] ⬅️ ALWAYS EMPTY (cse.py missing)
   │
   ├─→ Step 2: process_document(url) ✅ Ready but no input
   │   │
   │   ├─→ docai.py
   │   │   ├─ Download PDF/DOCX
   │   │   ├─ Store in GCS /raw/
   │   │   ├─ OCR with Document AI
   │   │   ├─ Extract text + metadata
   │   │   └─ Store in GCS /clean/
   │   │
   │   └─→ doc_data: {title, url, text, effective_date, ...}
   │
   ├─→ Step 3: create_chunks(doc_data) ✅ Ready
   │   │
   │   ├─→ chunker.py
   │   │   ├─ Split text into sentences
   │   │   ├─ Group into 800-token chunks
   │   │   ├─ 100-token overlap
   │   │   └─ Preserve metadata
   │   │
   │   └─→ chunks: [{text, metadata, chunk_index}, ...]
   │
   ├─→ Step 4: embed_text(chunk) ✅ Ready
   │   │
   │   ├─→ vertex_index.py
   │   │   ├─ Vertex AI text-embedding-004
   │   │   ├─ Input: Chinese text (800 tokens)
   │   │   └─ Output: 768-dim vector
   │   │
   │   └─→ embedding: [0.123, -0.456, ..., 0.789]
   │
   └─→ Step 5: upsert_chunks(chunks) ✅ Ready
       │
       ├─→ vertex_index.py
       │   ├─ Batch upload to Vertex AI Vector Search
       │   ├─ Metadata: {province, asset, doc_class, title, url, date}
       │   └─ Index: nemo-compliance-index
       │
       └─→ Stored in GCS: gs://.../contents/

RESULT: Vector database populated with searchable document chunks ❌ NEVER HAPPENS


┌──────────────────────────────────────────────────────────────────────┐
│                    ONLINE QUERY PIPELINE (NEEDED)                    │
└──────────────────────────────────────────────────────────────────────┘

User Query: "广东光伏并网需要什么资料？"
   │
   │ POST /query
   ↓
┌─────────────────────────────────┐
│   Cloud Function: nemo-query    │
└─────────────────────────────────┘
   │
   ├─→ Step 1: normalize_query()
   │   └─→ "广东光伏并网需要什么资料"
   │
   ├─→ Step 2: embed_query() ⭐ PRIMARY PATH (RAG)
   │   │
   │   ├─→ Vertex AI text-embedding-004
   │   └─→ query_vector: [0.123, -0.456, ..., 0.789]
   │
   ├─→ Step 3: search_documents(query_vector, filters)
   │   │
   │   ├─→ Vertex AI Vector Search
   │   │   ├─ Index: nemo-compliance-index
   │   │   ├─ Filters: {province: 'gd', asset: 'solar', doc_class: 'grid'}
   │   │   ├─ Top-K: 12
   │   │   └─ Similarity: DOT_PRODUCT_DISTANCE
   │   │
   │   └─→ SUCCESS ✅
   │       └─ candidates: [
   │            {
   │              text: "光伏并网申请需提交以下资料：1) 项目备案文件...",
   │              metadata: {
   │                title: "广东省光伏发电并网管理办法",
   │                url: "https://gd.gov.cn/policies/solar-2024.pdf",
   │                effective_date: "2024-06-01",
   │                province: "gd",
   │                asset: "solar"
   │              },
   │              score: 0.89
   │            },
   │            {...},  // 11 more results
   │          ]
   │
   ├─→ Step 4: compose_response(candidates, question)
   │   │
   │   ├─→ composer.py
   │   │   ├─ Extract verbatim quotes matching keywords
   │   │   ├─ Format with Chinese bullets
   │   │   ├─ Add citations with effective dates
   │   │   └─ Generate answer
   │   │
   │   └─→ response: {
   │          answer_zh: "并网要点（广东 / 光伏）\n- 相关规定：\n • 光伏并网...",
   │          citations: [{title, url, effective_date}, ...],
   │          mode: "vertex_rag"
   │       }
   │
   └─→ RETURN Response
       └─→ {
             "answer_zh": "并网要点（广东 / 光伏）...",
             "citations": [...],
             "mode": "vertex_rag",  ⬅️ THIS IS REAL RAG
             "elapsed_ms": 400
           }

Fallback (only if vector search fails):
   └─→ answer_with_perplexity() ⬅️ Used <10% of time

════════════════════════════════════════════════════════════════════════
SUCCESS: This IS RAG - retrieval from curated document database
════════════════════════════════════════════════════════════════════════
```

---

## 3. COMPONENT READINESS MAP

```
┌────────────────────────────────────────────────────────────────────┐
│                      INGESTION PIPELINE                            │
├────────────────────────────────────────────────────────────────────┤
│                                                                    │
│  ┌──────────────────┐                                             │
│  │ Document         │  ❌ MISSING (cse.py does not exist)         │
│  │ Discovery        │  ← BLOCKING THE ENTIRE PIPELINE             │
│  │ (CSE API)        │                                             │
│  └────────┬─────────┘                                             │
│           │ URLs                                                  │
│           ↓                                                       │
│  ┌──────────────────┐                                             │
│  │ Document         │  ✅ READY (docai.py)                        │
│  │ Download         │  - HTTP fetcher working                     │
│  │ & OCR            │  - Document AI integration done             │
│  └────────┬─────────┘  - GCS storage configured                  │
│           │ Text + Metadata                                       │
│           ↓                                                       │
│  ┌──────────────────┐                                             │
│  │ Text             │  ✅ READY (sanitize.py)                     │
│  │ Normalization    │  - Chinese text cleanup                     │
│  │ & Metadata       │  - Date extraction                          │
│  └────────┬─────────┘  - Title extraction                        │
│           │ Clean text                                            │
│           ↓                                                       │
│  ┌──────────────────┐                                             │
│  │ Chunking         │  ✅ READY (chunker.py)                      │
│  │ (800 tokens)     │  - Sentence-aware splitting                 │
│  │                  │  - 100-token overlap                        │
│  └────────┬─────────┘  - Metadata preservation                   │
│           │ Chunks                                                │
│           ↓                                                       │
│  ┌──────────────────┐                                             │
│  │ Embedding        │  ✅ READY (vertex_index.py)                 │
│  │ Generation       │  - text-embedding-004                       │
│  │                  │  - 768 dimensions                           │
│  └────────┬─────────┘  - Batch processing                        │
│           │ Vectors                                               │
│           ↓                                                       │
│  ┌──────────────────┐                                             │
│  │ Vector Database  │  ⚠️  EMPTY (no documents ingested)          │
│  │ Upload           │  - Upsert code ready                        │
│  │ (Vertex AI)      │  - Index configured                         │
│  └──────────────────┘  - Waiting for documents                   │
│                                                                    │
└────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────┐
│                       QUERY PIPELINE                               │
├────────────────────────────────────────────────────────────────────┤
│                                                                    │
│  ┌──────────────────┐                                             │
│  │ User Query       │  ✅ Working                                  │
│  │ Input            │  - JSON validation                          │
│  │                  │  - Province/asset filtering                 │
│  └────────┬─────────┘                                             │
│           │ Normalized query                                      │
│           ↓                                                       │
│  ┌──────────────────┐                                             │
│  │ Query            │  ✅ READY (vertex_index.py)                 │
│  │ Embedding        │  - Same model as ingestion                  │
│  │                  │  - text-embedding-004                       │
│  └────────┬─────────┘                                             │
│           │ Query vector                                          │
│           ↓                                                       │
│  ┌──────────────────┐                                             │
│  │ Vector Search    │  ⚠️  Returns EMPTY (no documents)           │
│  │ (Vertex AI)      │  - Code working                             │
│  │                  │  - Metadata filters working                 │
│  └────────┬─────────┘  - Database is empty                       │
│           │ Candidates (empty)                                    │
│           ↓                                                       │
│  ┌──────────────────┐                                             │
│  │ Response         │  ✅ READY (composer.py)                     │
│  │ Composition      │  - Never executed (no candidates)           │
│  │                  │  - Verbatim quote extraction ready          │
│  └────────┬─────────┘  - Chinese formatting ready                │
│           │ Formatted answer                                      │
│           ↓                                                       │
│  ┌──────────────────┐                                             │
│  │ Fallback:        │  ✅ WORKING (perplexity.py)                 │
│  │ Perplexity       │  - Currently handles 100% of queries        │
│  │ Web Search       │  - Should handle <10%                       │
│  └──────────────────┘  - Domain filtering active                 │
│                                                                    │
└────────────────────────────────────────────────────────────────────┘
```

---

## 4. DATA FLOW COMPARISON

### CURRENT: Perplexity Web Search (Not RAG)

```
┌─────────────────────────────────────────────────────────────────┐
│                       DATA SOURCE                               │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ Search request
                              ↓
               ┌──────────────────────────┐
               │   Perplexity API         │
               │   (External Service)     │
               └──────────────────────────┘
                              │
                              │ Searches
                              ↓
          ┌────────────────────────────────────┐
          │  THE ENTIRE INTERNET               │
          │  (Filtered to .gov.cn domains)     │
          │                                    │
          │  ┌──────────────┐                  │
          │  │ gd.gov.cn    │  Changes daily   │
          │  └──────────────┘                  │
          │  ┌──────────────┐                  │
          │  │ ndrc.gov.cn  │  No control      │
          │  └──────────────┘                  │
          │  ┌──────────────┐                  │
          │  │ nea.gov.cn   │  Rate limits     │
          │  └──────────────┘                  │
          │  ┌──────────────┐                  │
          │  │ ...many more │  Unpredictable   │
          │  └──────────────┘                  │
          └────────────────────────────────────┘
                              │
                              │ Returns web pages
                              ↓
                    Answer + Citations
                    (No guarantee same docs next time)
```

### NEEDED: RAG Document Database

```
┌─────────────────────────────────────────────────────────────────┐
│                    CURATED DATABASE                             │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │
                              ↓
          ┌────────────────────────────────────┐
          │  PRIVATE VECTOR DATABASE           │
          │  (Vertex AI Vector Search)         │
          │                                    │
          │  ┌──────────────────────────────┐  │
          │  │ Document Collection:         │  │
          │  │                              │  │
          │  │ ├─ GD Solar Grid (50 docs)  │  │
          │  │ ├─ GD Coal Grid (30 docs)   │  │
          │  │ ├─ GD Wind Grid (40 docs)   │  │
          │  │ ├─ SD Solar Grid (45 docs)  │  │
          │  │ ├─ SD Coal Grid (35 docs)   │  │
          │  │ ├─ SD Wind Grid (50 docs)   │  │
          │  │ ├─ NM Solar Grid (40 docs)  │  │
          │  │ ├─ NM Coal Grid (60 docs)   │  │
          │  │ └─ NM Wind Grid (55 docs)   │  │
          │  │                              │  │
          │  │ Total: ~405 documents        │  │
          │  │ Total: ~4,050 chunks         │  │
          │  │ Total: ~4,050 vectors        │  │
          │  └──────────────────────────────┘  │
          │                                    │
          │  Features:                         │
          │  ✓ Static (updates on schedule)   │
          │  ✓ Full control                   │
          │  ✓ Reproducible results           │
          │  ✓ Auditable sources              │
          │  ✓ Fast (<500ms)                  │
          │  ✓ Cost-effective                 │
          └────────────────────────────────────┘
                              │
                              │ Vector search
                              ↓
                    Relevant Document Chunks
                    (Same docs every time)
```

---

## 5. THE MISSING LINK: CSE Module

```
┌─────────────────────────────────────────────────────────────────┐
│          DOCUMENT DISCOVERY WORKFLOW (MISSING)                  │
└─────────────────────────────────────────────────────────────────┘

Input: discover_documents('gd', 'solar', 'grid')
  │
  ├─→ Step 1: Build search query
  │   │
  │   ├─ site:gd.gov.cn
  │   ├─ Keywords: 光伏 并网
  │   ├─ Filetypes: pdf OR doc OR docx
  │   │
  │   └─→ "site:gd.gov.cn 光伏 并网 filetype:pdf OR filetype:doc"
  │
  ├─→ Step 2: Call Google Custom Search API
  │   │
  │   ├─ API: https://www.googleapis.com/customsearch/v1
  │   ├─ Params: {key, cx, q, num: 10}
  │   │
  │   └─→ JSON Response: {
  │         items: [
  │           {
  │             title: "广东省光伏发电并网管理办法",
  │             link: "https://gd.gov.cn/policies/solar-grid-2024.pdf",
  │             snippet: "..."
  │           },
  │           {...},
  │           ...
  │         ]
  │       }
  │
  ├─→ Step 3: Validate domains
  │   │
  │   ├─ Filter to .gov.cn only
  │   ├─ Remove duplicates
  │   ├─ Check accessibility
  │   │
  │   └─→ Valid URLs: [url1, url2, url3, ...]
  │
  └─→ Output: List of document URLs
      │
      └─→ [
            "https://gd.gov.cn/policies/solar-grid-2024.pdf",
            "https://gd.gov.cn/regulations/renewable-connection.pdf",
            "https://gd.gov.cn/guidelines/distributed-solar.pdf",
            ...
          ]

⚠️  CURRENT STATUS: This module does not exist (lib/cse.py missing)
⚠️  IMPACT: Zero documents discovered → Zero documents ingested
```

---

## 6. COMPLETION PERCENTAGE

```
┌─────────────────────────────────────────────────────────────────┐
│                   RAG SYSTEM COMPLETION                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Infrastructure:          [████████████████████████] 100%  ✅   │
│  ├─ Vertex AI Index       [████████████████████████] 100%      │
│  ├─ Vertex AI Endpoint    [████████████████████████] 100%      │
│  ├─ GCS Buckets           [████████████████████████] 100%      │
│  └─ Cloud Functions       [████████████████████████] 100%      │
│                                                                 │
│  Ingestion Code:          [██████████████████████░░]  95%  ⚠️   │
│  ├─ Document Discovery    [░░░░░░░░░░░░░░░░░░░░░░░░]   0%  ❌   │
│  ├─ Document Download     [████████████████████████] 100%      │
│  ├─ Document AI (OCR)     [████████████████████████] 100%      │
│  ├─ Text Normalization    [████████████████████████] 100%      │
│  ├─ Chunking              [████████████████████████] 100%      │
│  ├─ Embedding             [████████████████████████] 100%      │
│  └─ Vector Upload         [████████████████████████] 100%      │
│                                                                 │
│  Query Code:              [████████████████████████] 100%  ✅   │
│  ├─ Query Embedding       [████████████████████████] 100%      │
│  ├─ Vector Search         [████████████████████████] 100%      │
│  ├─ Response Composer     [████████████████████████] 100%      │
│  └─ Perplexity Fallback   [████████████████████████] 100%      │
│                                                                 │
│  Vector Database:         [░░░░░░░░░░░░░░░░░░░░░░░░]   0%  ❌   │
│  └─ Documents Ingested    0 / ~405 target documents            │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│  OVERALL PROGRESS:        [███████████████████░░░░░]  95%       │
│                                                                 │
│  Missing 5%: Document discovery (CSE module)                    │
│  Impact: System works but uses web search, not RAG              │
└─────────────────────────────────────────────────────────────────┘
```

---

## 7. ACTION ITEMS TO ACHIEVE REAL RAG

```
┌─────────────────────────────────────────────────────────────────┐
│                     IMPLEMENTATION ROADMAP                      │
└─────────────────────────────────────────────────────────────────┘

PHASE 1: Document Discovery (4 hours)
┌─────────────────────────────────────────────────────────────────┐
│ Task 1.1: Create lib/cse.py                         [2 hours]  │
│   ├─ implement discover_documents()                            │
│   ├─ implement build_search_query()                            │
│   ├─ implement validate_government_domain()                    │
│   └─ implement fetch_document()                                │
│                                                                 │
│ Task 1.2: Set up Google Custom Search                          │
│   ├─ Create CSE with .gov.cn allowlist              [1 hour]   │
│   ├─ Generate API key                                          │
│   └─ Update config/environment.yaml                            │
│                                                                 │
│ Task 1.3: Test CSE integration                      [1 hour]   │
│   └─ Run: discover_documents('gd', 'solar', 'grid')            │
└─────────────────────────────────────────────────────────────────┘

PHASE 2: Initial Ingestion (2 hours)
┌─────────────────────────────────────────────────────────────────┐
│ Task 2.1: Deploy ingest function                    [30 min]   │
│   └─ gcloud functions deploy nemo-ingest                       │
│                                                                 │
│ Task 2.2: Run test ingestion                        [1 hour]   │
│   ├─ Trigger: gd/solar/grid                                    │
│   ├─ Monitor logs                                              │
│   └─ Verify documents in GCS                                   │
│                                                                 │
│ Task 2.3: Verify vector database                    [30 min]   │
│   └─ Check: indexedItemCount > 0                               │
└─────────────────────────────────────────────────────────────────┘

PHASE 3: Switch to RAG-First (1 hour)
┌─────────────────────────────────────────────────────────────────┐
│ Task 3.1: Modify query flow                         [30 min]   │
│   ├─ functions/query/main.py                                   │
│   ├─ Change: Vector search → PRIMARY                           │
│   └─ Change: Perplexity → FALLBACK                             │
│                                                                 │
│ Task 3.2: Deploy query function                     [15 min]   │
│   └─ gcloud functions deploy nemo-query                        │
│                                                                 │
│ Task 3.3: Test end-to-end                           [15 min]   │
│   └─ Verify: response.mode == "vertex_rag"                     │
└─────────────────────────────────────────────────────────────────┘

PHASE 4: Full Dataset Ingestion (4 hours)
┌─────────────────────────────────────────────────────────────────┐
│ Task 4.1: Ingest all provinces/assets               [3 hours]  │
│   ├─ gd/solar, gd/coal, gd/wind                                │
│   ├─ sd/solar, sd/coal, sd/wind                                │
│   └─ nm/solar, nm/coal, nm/wind                                │
│                                                                 │
│ Task 4.2: Quality check                             [1 hour]   │
│   ├─ Verify document counts                                    │
│   ├─ Spot-check search results                                 │
│   └─ Test edge cases                                           │
└─────────────────────────────────────────────────────────────────┘

════════════════════════════════════════════════════════════════════
TOTAL TIME: ~11 hours (1.5 days)
CRITICAL PATH: CSE module (4 hours) → Test ingestion (2 hours)
════════════════════════════════════════════════════════════════════
```

---

*Diagrams created by Committee 2: RAG Architecture Review*
*Date: 2025-11-22*
