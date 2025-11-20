# Nemo Compliance MVP - Complete Architecture Analysis

**Committee 4 Report: Current Codebase Architecture Analysis**
**Date**: November 2024
**Scope**: Full system architecture, API integration, deployment infrastructure

---

## Executive Summary

The Nemo Compliance MVP is a **serverless, Google Cloud-native RAG system** that delivers verified regulatory information for Chinese energy projects (Solar, Coal, Wind) with citation-backed answers. The system consists of:

- **3 Cloud Functions** (Query, Ingest, Health)
- **Multiple AI/ML Services** (Vertex AI, Document AI, Perplexity API, Gemini)
- **Web Frontend** (Single-page HTML with vanilla JS)
- **Data Pipeline** (Document discovery, OCR, chunking, embedding, indexing)

**Key Characteristics**:
- Zero mock data policy
- Serverless (no Docker/containers)
- CORS-enabled for web frontend
- Token-authenticated ingestion
- Distributed request tracing

---

## Part 1: Project Structure Overview

### Directory Layout

```
/home/user/Nemo_Time/
├── functions/                    # Cloud Functions (entry points)
│   ├── query/                    # Query processing (MAIN API)
│   │   ├── main.py              # Query handler (HTTP entry point)
│   │   ├── perplexity.py         # Perplexity API integration
│   │   ├── vertex_index.py       # Vertex AI vector search
│   │   ├── composer.py           # Response formatting
│   │   ├── cse.py                # Google Custom Search
│   │   ├── chunker.py            # Document chunking
│   │   ├── sanitize.py           # Text normalization
│   │   ├── docai.py              # Document AI integration
│   │   ├── metadata_extractor.py # Metadata parsing
│   │   ├── gemini_rerank.py      # Gemini reranking
│   │   ├── intent_detection.py   # Query intent analysis
│   │   ├── requirements.txt       # Python dependencies
│   │   └── .venv/                # Virtual environment
│   ├── health/                   # Health check endpoint
│   │   ├── main.py              # Health handler
│   │   └── requirements.txt
│   └── ingest/                   # Document ingestion pipeline
│       ├── main.py              # Ingest handler
│       └── requirements.txt
├── lib/                          # Shared libraries (copies in functions/)
│   ├── vertex_index.py          # Vertex AI client
│   ├── sanitize.py              # Text processing utilities
│   ├── chunker.py               # Chunking algorithms
│   ├── composer.py              # Response composition
│   ├── docai.py                 # Document AI client
│   ├── cse.py                   # CSE discovery
│   ├── metadata_extractor.py    # Metadata extraction
│   ├── gemini_rerank.py         # Gemini reranking client
│   ├── intent_detection.py      # Intent classification
│   └── perplexity.py            # Perplexity client
├── frontend/                     # Web UI
│   ├── index.html               # Main UI (vanilla HTML/CSS/JS)
│   ├── dev-proxy.js             # Local development proxy
│   ├── favicon.ico
│   └── api/                      # API endpoint definitions
├── tests/                        # Test suite
│   ├── test_functions.py         # Cloud Function tests
│   ├── test_composer.py          # Response formatting tests
│   ├── test_chunker.py           # Chunking algorithm tests
│   ├── test_sanitize.py          # Text processing tests
│   ├── test_vertex_index.py      # Vector search tests
│   ├── test_cse.py               # CSE discovery tests
│   ├── test_docai.py             # Document AI tests
│   ├── test_metadata_extractor.py
│   ├── test_gemini_rerank.py
│   └── integration/
│       └── test_end_to_end.py    # End-to-end tests
├── deploy/                       # Deployment scripts
│   ├── deploy-function-tolerate-iam.sh
│   ├── deploy-query-function.sh  # Query function deployment
│   ├── setup-vertex-ai.sh        # Vertex AI setup
│   ├── setup-scheduler.sh        # Cloud Scheduler setup
│   ├── grant-permissions.sh      # IAM role assignments
│   ├── grant-cloud-build-permissions.sh
│   ├── grant-gcf-service-agent-permissions.sh
│   ├── grant-run-admin-serverless-robot.sh
│   ├── verify-cloud-build-permissions.sh
│   ├── grant-bucket-access.sh
│   └── index_metadata.json       # Vector index metadata
├── config/                       # Configuration
│   └── environment.yaml          # Environment variables template
├── docs/                         # Documentation
│   ├── DEPLOYMENT_GUIDE.md
│   ├── DEPLOYMENT_CHECKLIST.md
│   ├── DEPLOYMENT_WORKLOG.md
│   ├── COMMITTEE_STRUCTURE.md
│   └── runbooks/
├── evaluation_results/           # Test results archive
├── verification_results/         # Verification reports
├── .github/                      # Git configuration
├── README.md                     # Project overview
├── DEPLOYMENT_GUIDE.md          # Main deployment guide
└── deploy-*.sh                  # Quick deployment scripts
```

### Key Files at a Glance

| File | Purpose | Type | Lines |
|------|---------|------|-------|
| functions/query/main.py | Query handler (HTTP entry point) | Python | 223 |
| functions/query/perplexity.py | Perplexity API wrapper | Python | 316 |
| functions/health/main.py | Health check endpoint | Python | 166 |
| functions/ingest/main.py | Ingestion pipeline | Python | 184 |
| frontend/index.html | Web UI | HTML/JS | 623 |
| functions/query/composer.py | Response formatting | Python | 207 |
| lib/vertex_index.py | Vector search client | Python | 320+ |
| lib/sanitize.py | Text processing | Python | 400+ |
| config/environment.yaml | Configuration template | YAML | 47 |

---

## Part 2: Cloud Functions Architecture

### Overview: Three Cloud Functions

The system uses **Google Cloud Functions (2nd Gen runtime)** with HTTP triggers:

```
User Request
    ↓
Frontend (index.html) sends POST
    ↓
Load Balancer (Cloud Functions routing)
    ├── /api/query    → nemo-query function
    ├── /api/health   → nemo-health function
    └── /api/ingest   → nemo-ingest function
    ↓
Response with CORS headers
```

---

## Part 3: Query Function - Complete API Documentation

### Endpoint: POST /query

**Location**: `functions/query/main.py::query_handler()`

**Purpose**: Process user questions and return verified regulatory answers with citations

#### Request Format

```json
{
  "province": "gd|sd|nm",           // Required: Guangdong, Shandong, Inner Mongolia
  "asset": "solar|coal|wind",       // Required: Energy asset type
  "doc_class": "grid",              // Required: Always "grid" for MVP
  "question": "string",             // Required: User question (typically Chinese)
  "lang": "zh-CN|en"                // Optional: Response language (default: zh-CN)
}
```

**Field Validation**:
- `province`: Must be in ["gd", "sd", "nm"]
- `asset`: Must be in ["solar", "coal", "wind"]
- `doc_class`: Must be "grid" (hardcoded for MVP)
- `question`: Non-empty string (normalized internally)
- `lang`: Defaults to "zh-CN" if omitted

**Example Request**:
```bash
curl -X POST "https://[REGION]-[PROJECT].cloudfunctions.net/nemo-query" \
  -H "Content-Type: application/json" \
  -d '{
    "province": "gd",
    "asset": "solar",
    "doc_class": "grid",
    "question": "光伏发电项目并网验收需要哪些资料？",
    "lang": "zh-CN"
  }'
```

#### Response Formats

**Success Response (200 OK)**:
```json
{
  "answer_zh": "并网要点（广东 / 光伏）\n- 相关规定：\n • 需要提交企业资质证书\n • 需要提交项目评估报告\n ...",
  "citations": [
    {
      "title": "广东省分布式光伏发电管理办法",
      "url": "https://gd.gov.cn/...",
      "effective_date": "2023-01-15"  // Optional
    },
    {
      "title": "电网企业分布式光伏接入服务流程",
      "url": "https://gdwenergy.gov.cn/...",
      "effective_date": "2022-06-01"
    }
  ],
  "trace_id": "gaea-abc123def456",
  "mode": "perplexity_qa|vertex_rag|cse_fallback",
  "elapsed_ms": 1250
}
```

**Refusal Response (200 OK, no documents found)**:
```json
{
  "refusal": "未找到相关的一手资料。",  // OR "No directly relevant primary sources were found."
  "tips": [
    "请指定省份与资产类型",
    "尝试更具体的关键词，例如'并网验收资料清单'"
  ],
  "trace_id": "gaea-abc123def456",
  "mode": "vertex_rag",
  "elapsed_ms": 450
}
```

**Error Response (4xx/5xx)**:
```json
{
  "error": true,
  "message": "Missing required field: province",
  "trace_id": "gaea-abc123def456",
  "status_code": 400
}
```

#### HTTP Status Codes

| Status | Meaning | When |
|--------|---------|------|
| 200 | OK | Valid request processed (success or refusal) |
| 204 | No Content | CORS preflight OPTIONS request |
| 400 | Bad Request | Missing fields, invalid enums, invalid JSON |
| 405 | Method Not Allowed | Non-POST request (except OPTIONS) |
| 500 | Internal Server Error | Unhandled exception in processing |

#### CORS Headers

All responses include CORS headers for browser compatibility:
```
Access-Control-Allow-Origin: *
Access-Control-Allow-Methods: GET,POST,OPTIONS
Access-Control-Allow-Headers: Content-Type,Authorization,X-Ingest-Token
Access-Control-Max-Age: 3600
```

---

## Part 4: Query Processing Pipeline

### Query Handler Execution Flow

```
query_handler() receives request
    ↓
1. VALIDATE REQUEST
   - Check method (POST required)
   - Parse JSON
   - Validate required fields
   - Validate enum values
   - Generate trace_id
    ↓
2. NORMALIZE QUERY
   - Remove whitespace
   - Simplify punctuation
   - Extract keywords
    ↓
3. TRY PERPLEXITY API (Mode: perplexity_qa)
   - Call answer_with_perplexity()
   - If citations found → RETURN immediately (highest quality)
   - If no citations → continue to vector search
    ↓
4. VERTEX AI VECTOR SEARCH (Mode: vertex_rag)
   - Embed normalized question
   - Search vector index with filters (province, asset, doc_class)
   - Return top-12 candidates
   - Optional: Rerank with Gemini (if RERANK=true)
    ↓
5. COMPOSE RESPONSE (if candidates found)
   - Extract verbatim spans from candidates
   - Format as bulleted Chinese text
   - Deduplicate citations by URL
   - Return answer + citations
    ↓
6. FALLBACK (if no candidates)
   - If CSE fallback enabled → discover_documents()
   - Fetch page titles for discovered URLs
   - Return URLs only (no verbatim quotes)
    ↓
7. REFUSAL
   - If nothing found → return refusal message + tips
    ↓
Response with trace_id and elapsed_ms
```

### Key Modules in Query Function

#### perplexity.py (316 lines)

**Purpose**: Perplexity API integration for citation-backed QA

**Key Functions**:

1. **answer_with_perplexity()**
   - Input: question, province, asset, lang, doc_class
   - Calls: Perplexity API (https://api.perplexity.ai/chat/completions)
   - Parameters:
     - `model`: "sonar-pro" (configurable)
     - `search_domain_filter`: List of allowed domains (MAX 20)
     - `search_recency_filter`: "year" (2024 documents only)
     - `return_citations`: true
   - Output: `{"answer_zh": str, "citations": [{"title": str, "url": str}, ...]}`
   - Returns: None if no API key or no citations found

2. **_build_domain_filter(province, topic)**
   - Creates allowlist for Perplexity search
   - Core domains: gov.cn, ndrc.gov.cn, nea.gov.cn, mnr.gov.cn, mee.gov.cn, mohurd.gov.cn
   - Province-specific: gd.gov.cn, sd.gov.cn, nmg.gov.cn
   - Topic-specific: 
     - Grid connection: gdwenergy.gov.cn
     - Land survey: mnr.gov.cn, mee.gov.cn
     - Rail freight: mot.gov.cn, nra.gov.cn
   - Limit: 20 domains max (API constraint)

3. **_infer_topic(question, asset, doc_class)**
   - Classifies query into topic for better domain filtering
   - Topics: grid_connection, rail_freight, land_survey, renewables, general

4. **_is_allowed(url, allowlist)**
   - Validates URL against allowlist domains
   - Supports both exact matches (e.g., gd.gov.cn) and wildcard matches (e.g., .gov.cn)

5. **_prioritize_relevance(urls, question, asset, topic)**
   - Sorts URLs by relevance to query
   - Topic-aware scoring

6. **_perplexity_urls_only()**
   - Fallback function to get URLs only if content retrieval fails

**Environment Variables**:
- `PERPLEXITY_API_KEY`: API key from Secret Manager
- `PERPLEXITY_MODEL`: Model name (default: "sonar-pro")
- `PERPLEXITY_ALLOWLIST`: Additional allowed domains (comma-separated)

**Request Format to Perplexity API**:
```python
{
    "model": "sonar-pro",
    "messages": [
        {"role": "system", "content": "compliance assistant prompt"},
        {"role": "user", "content": "query with context"}
    ],
    "search_domain_filter": ["gov.cn", "gd.gov.cn", ...],  # ✅ KEY FIX
    "search_recency_filter": "year",
    "return_citations": True
}
```

**Citation Extraction**:
- Perplexity returns both citations array and URLs embedded in response text
- Nemo merges both sources, filters by allowlist, deduplicates, returns top 6

#### vertex_index.py (320+ lines)

**Purpose**: Vertex AI Vector Search integration

**Key Functions**:

1. **search_documents(query_vector, filters, top_k=12)**
   - Input: Vector embedding, metadata filters
   - Filters structure:
     ```python
     {
       'province': 'gd',
       'asset': 'solar',
       'doc_class': 'grid'
     }
     ```
   - Output: List of candidates with text and metadata
   - Returns top-k most similar documents

2. **embed_query(question_text)**
   - Embeds question text into vector space
   - Model: `text-embedding-004` (configurable)
   - Returns: Vector (768 dimensions typical)

3. **embed_text(chunk_text)**
   - Embeds document chunk
   - Batch processing supported

4. **upsert_chunks(chunks)**
   - Adds/updates chunks in vector index
   - Called during ingestion

5. **get_index_status(index_id, endpoint_id)**
   - Returns health status of vector index
   - Used by health check endpoint

**Environment Variables**:
- `VERTEX_INDEX_ID`: Vector index ID
- `VERTEX_ENDPOINT_ID`: Index endpoint ID
- `GOOGLE_CLOUD_PROJECT`: GCP project ID
- `REGION`: Deployment region

**Vector Index Metadata Schema**:
```python
{
  'text': 'chunk content (400-800 tokens)',
  'metadata': {
    'title': 'document title',
    'url': 'source URL',
    'province': 'gd|sd|nm',
    'asset': 'solar|coal|wind',
    'doc_class': 'grid',
    'effective_date': '2023-01-15',
    'source_type': 'government|regulation|guidance',
    'chunk_index': 0
  },
  'embedding': [0.123, 0.456, ...]  # 768-dim vector
}
```

#### composer.py (207 lines)

**Purpose**: Format responses with verbatim quotes and citations

**Key Functions**:

1. **compose_response(candidates, question, lang='zh-CN')**
   - Input: Vector search results, original question, language
   - Output: Formatted response dict
   - Process:
     - Extract keywords from question
     - Pick verbatim spans (20+ chars) from top-5 candidates
     - Format as bulleted Chinese text
     - Deduplicate citations by URL
     - Include effective dates if available

2. **_extract_keywords(question)**
   - Extracts regulatory keywords from question
   - Prioritizes terms like: 并网, 验收, 资料, 清单, 要求, 条件, 程序, 流程, ...
   - Returns list of up to 8 keywords

3. **pick_verbatim_spans(text, keywords, max_spans=2)**
   - Finds verbatim text spans matching keywords
   - Extracts up to 2 meaningful spans per chunk
   - Min length: 20 characters

4. **format_citation(metadata)**
   - Converts metadata to citation format

5. **validate_response(response)**
   - Validates response has required fields and format

**Output Format Example**:
```python
{
  'answer_zh': '''并网要点（广东 / 光伏）
- 相关规定：
 • 需要提交企业资质证书、营业执照复印件〔《广东省分布式光伏发电管理办法》，生效：2023-01-15〕
 • 需要提交项目建设地规划许可证、用地证明〔《广东省分布式光伏发电管理办法》〕
 • 完成接网评审，提交接网评审报告〔《电网企业分布式光伏接入服务流程》，生效：2022-06-01〕
 • 需要缴纳并网费用〔《广东省分布式光伏发电管理办法》〕''',
  'citations': [
    {
      'title': '广东省分布式光伏发电管理办法',
      'url': 'https://gd.gov.cn/...',
      'effective_date': '2023-01-15'
    },
    ...
  ]
}
```

#### cse.py (19KB)

**Purpose**: Google Custom Search Engine integration for document discovery

**Key Functions**:

1. **discover_documents(province, asset, doc_class, question)**
   - Discovers relevant document URLs from allowlisted domains
   - Input: province, asset, document class, optional question
   - Queries CSE with domain filters
   - Returns: List of URLs

2. **_search_query(query_text)**
   - Executes CSE API call
   - Filters to allowlisted domains

**Environment Variables**:
- `GOOGLE_CSE_API_KEY`: CSE API key
- `GOOGLE_CSE_ENGINE_ID`: CSE engine ID

**Used For**:
- Ingestion: Find all documents for province/asset combination
- Fallback: When vector search returns no results

#### Additional Modules

**sanitize.py**:
- `normalize_query()`: Removes whitespace, standardizes punctuation
- `normalize_text()`: Full text normalization for documents
- `extract_effective_date()`: Parses effective dates from text
- `pick_verbatim_spans()`: Extract verbatim text

**chunker.py**:
- `create_chunks()`: Splits documents into 400-800 token chunks
- Preserves sentence boundaries
- Includes overlap for context

**docai.py**:
- `process_document()`: OCR with Document AI
- Extracts text and layout from PDFs

**gemini_rerank.py** (optional):
- `rerank_candidates()`: Reranks vector search results with Gemini
- Enabled only if `RERANK=true`

**intent_detection.py**:
- `detect_intent()`: Classifies query intent
- Helps with response type selection

**metadata_extractor.py**:
- `extract_metadata()`: Parses document metadata
- Title, date, source type, etc.

---

## Part 5: Health Check Function

### Endpoint: GET /health

**Location**: `functions/health/main.py::health_handler()`

**Purpose**: Monitor system component health and connectivity

**Response (200 OK)**:
```json
{
  "status": "ok|degraded|error",
  "timestamp": "2024-11-20T12:34:56.789Z",
  "commit": "abc123def456",
  "region": "asia-east2",
  "vertex_index_status": "healthy|not_configured|error: ...",
  "gcs_status": "healthy|not_configured|buckets_missing: ...",
  "secrets_status": "healthy|project_not_configured|error: ..."
}
```

**Status Logic**:
- `status = "ok"` if all components healthy
- `status = "degraded"` if any component has error
- `status = "error"` if handler exception

**Components Checked**:
1. **Vertex AI**: Index and endpoint connectivity
2. **GCS Buckets**: Raw and clean document buckets exist
3. **Secret Manager**: Can list secrets (basic connectivity)

**Environment Variables**:
- `COMMIT_HASH`: Git commit hash (set during deployment)
- `REGION`: Deployment region
- `GOOGLE_CLOUD_PROJECT`: GCP project ID
- `VERTEX_INDEX_ID`, `VERTEX_ENDPOINT_ID`: Vector index identifiers
- `BUCKET_RAW`, `BUCKET_CLEAN`: GCS bucket names

**Used By**:
- Frontend status indicator (shows green/red dot)
- Monitoring dashboards
- Deployment verification

---

## Part 6: Ingest Function

### Endpoint: POST /ingest

**Location**: `functions/ingest/main.py::ingest_handler()`

**Purpose**: Trigger document discovery, processing, and indexing pipeline

**Authentication**: Token-based (`X-Ingest-Token` header)

**Request Format**:
```json
{
  "province": "gd|sd|nm",           // Optional: if omitted, process all
  "asset": "solar|coal|wind",       // Optional: if omitted, process all
  "doc_class": "grid"               // Optional: defaults to grid
}
```

**Response (202 Accepted)**:
```json
{
  "accepted": true,
  "job_id": "ing-1700000000-abc123",
  "estimated_minutes": 3,
  "processed_documents": 45,
  "errors": 2
}
```

**Error Responses**:
- 403 Forbidden: Missing or invalid token
- 400 Bad Request: Invalid province/asset/doc_class
- 500 Internal Server Error: Processing failure

**Pipeline Steps**:

```
ingest_handler() receives request
    ↓
1. VALIDATE TOKEN
   - Check X-Ingest-Token header
   - Compare against INGEST_TOKEN env var
   - Return 403 if mismatch
    ↓
2. PARSE REQUEST
   - Extract province, asset, doc_class
   - Default to all if omitted
    ↓
3. FOR EACH (province, asset) COMBINATION:
    ├─ discover_documents()  → Get URLs from CSE
    │
    ├─ FOR EACH URL:
    │  ├─ fetch_document()        → Download from URL
    │  ├─ process_document()      → OCR with Document AI
    │  ├─ normalize_text()        → Clean and standardize
    │  ├─ extract_effective_date() → Parse dates
    │  ├─ create_chunks()         → Split into 400-800 token chunks
    │  ├─ embed_text()            → Generate vectors for each chunk
    │  └─ upsert_chunks()         → Add to Vertex AI index
    │
    └─ return (processed_count, error_count)
    ↓
4. RETURN JOB STATUS
```

**Environment Variables**:
- `INGEST_TOKEN`: Secure token (from Secret Manager)
- Other variables inherited from config

**Security**:
- Token-based access control (not identity-based)
- No public unauthenticated ingestion allowed
- Typically triggered by Cloud Scheduler, not direct users

**Scheduling**:
```bash
# Cloud Scheduler job (nightly)
gcloud scheduler jobs create http nightly-ingest \
  --schedule="0 21 * * *" \
  --uri="https://[region]-[project].cloudfunctions.net/nemo-ingest" \
  --http-method=POST \
  --headers="X-Ingest-Token=secure-token"
```

---

## Part 7: Frontend Architecture

### Single-Page Application: index.html

**Location**: `/frontend/index.html` (623 lines)

**Architecture**: Vanilla HTML/CSS/JavaScript (no frameworks)

**Components**:

1. **Header Section**
   - Title: "Nemo 合规 MVP"
   - Status indicator (green/red dot)
   - Language toggle (中文 / English)

2. **Query Form**
   - Province dropdown: gd, sd, nm
   - Asset type buttons: solar (光伏), coal (煤电), wind (风电)
   - Question textarea
   - Submit button

3. **Results Section**
   - Answer text (formatted with newlines preserved)
   - Citations list (with effective dates, clickable links)
   - Trace ID for debugging

4. **UI States**
   - Form visible → user can input
   - Loading visible → spinner + "正在查询相关法规文件..."
   - Results visible → answer + citations + trace_id
   - Error visible → red error message

### Frontend API Integration

**API Configuration**:
```javascript
const PROJECT_ID = 'day-planner-london-mvp';
const REGION = 'asia-east2';
const OVERRIDE = window.NEMO_API || {};
const API_BASE = OVERRIDE.QUERY_URL || 
  (window.location.hostname === 'localhost'
    ? 'http://localhost:8081'
    : '/api/query');
const HEALTH_URL = OVERRIDE.HEALTH_URL || 
  (window.location.hostname === 'localhost'
    ? 'http://localhost:8080'
    : '/api/health');
```

**Local Development**: 
- Query API: http://localhost:8081
- Health API: http://localhost:8080
- Uses dev-proxy.js to forward requests

**Production**:
- Query API: /api/query (proxied by hosting service)
- Health API: /api/health (proxied by hosting service)

### Frontend Request/Response Handling

**On Form Submit**:
```javascript
// Build request
const requestData = {
  province: province,
  asset: selectedAsset,
  doc_class: 'grid',
  question: question.trim(),
  lang: selectedLanguage
};

// Send to API
fetch(API_BASE, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(requestData)
});
```

**Response Handling**:
```javascript
if (response.ok) {
  displayResults(data);  // Show answer + citations
} else {
  displayError(data);    // Show error message
}
```

**Display Results**:
- If `data.answer_zh`: Show formatted answer with citations
- If `data.refusal`: Show warning message with tips
- Always show trace_id for debugging

### Frontend Bilingual Support

**Text Content**:
- All UI text has both Chinese and English versions
- Language toggle changes which version is displayed
- Dynamic replacement of:
  - Labels
  - Button text
  - Placeholders
  - Error messages
  - Loading text

**Language-Specific Features**:
- Chinese: Uses "并网要点（省份 / 资产）" title format
- English: Uses English descriptions
- Both: Support for mixed content (government names often bilingual)

### Frontend Local Development

**dev-proxy.js**:
- Simple HTTP proxy for development
- Forwards requests to local function servers
- Runs on port 8000 (static files) and 8001 (proxy)

**Usage**:
```bash
cd frontend
node dev-proxy.js
# Visit http://localhost:8000
```

---

## Part 8: Data Flow - Complete Journey

### End-to-End Query Flow

```
1. USER SUBMITS FORM (Frontend)
   ├─ Province: gd
   ├─ Asset: solar
   ├─ Question: "光伏发电项目并网验收需要哪些资料？"
   └─ Language: zh-CN

2. FRONTEND SENDS HTTP POST
   POST /api/query
   Content-Type: application/json
   {
     "province": "gd",
     "asset": "solar",
     "doc_class": "grid",
     "question": "光伏发电项目并网验收需要哪些资料？",
     "lang": "zh-CN"
   }

3. CLOUD FUNCTION RECEIVES REQUEST
   ├─ Generate trace_id: gaea-abc123def456
   ├─ Validate all fields
   └─ Normalize question

4. TRY PERPLEXITY API (Fast path)
   ├─ Call Perplexity with domain filter
   ├─ Search only .gov.cn domains (high precision)
   ├─ If citations found → RETURN (stops here, best quality)
   └─ If no citations → continue

5. VERTEX AI VECTOR SEARCH (RAG path)
   ├─ Embed question: "光伏发电项目并网验收需要哪些资料？"
   │  → Vector: [0.123, 0.456, ..., 0.789] (768 dims)
   │
   ├─ Search with filters:
   │  ├─ province: "gd"
   │  ├─ asset: "solar"
   │  └─ doc_class: "grid"
   │
   ├─ Return top-12 similar chunks:
   │  ├─ Chunk 1: "企业需提交营业执照、资质证书复印件..." (score: 0.95)
   │  ├─ Chunk 2: "需要提交项目环评报告..." (score: 0.92)
   │  ├─ Chunk 3: "接网评审需要..." (score: 0.88)
   │  └─ ... (9 more chunks)
   │
   └─ Optional: Rerank with Gemini (if RERANK=true)

6. COMPOSE RESPONSE
   ├─ Extract keywords from question:
   │  └─ ["光伏", "发电", "项目", "并网", "验收", "资料"]
   │
   ├─ For each top-5 chunk:
   │  ├─ Find verbatim spans matching keywords
   │  ├─ Extract: "企业需提交营业执照、资质证书复印件"
   │  ├─ Format bullet: " • 企业需提交营业执照、资质证书复印件〔《广东省...办法》，生效：2023-01-15〕"
   │  └─ Add to citations (deduplicate by URL)
   │
   ├─ Format answer_zh:
   │  ├─ Title: "并网要点（广东 / 光伏）"
   │  ├─ Section: "- 相关规定："
   │  └─ Bullets: 4 max formatted quotes
   │
   └─ Return response:
      {
        "answer_zh": "并网要点（广东 / 光伏）\n- 相关规定：\n • ...",
        "citations": [
          {
            "title": "广东省分布式光伏发电管理办法",
            "url": "https://gd.gov.cn/...",
            "effective_date": "2023-01-15"
          },
          ...
        ],
        "trace_id": "gaea-abc123def456",
        "mode": "vertex_rag",
        "elapsed_ms": 1250
      }

7. FALLBACK (if no candidates from vector search)
   ├─ Call CSE discover_documents()
   ├─ Get URLs: [url1, url2, url3, ...]
   ├─ Fetch title for each URL
   └─ Return citations only (no verbatim quotes)
      Mode: "cse_fallback"

8. REFUSAL (if nothing found)
   ├─ Return: "未找到相关的一手资料。"
   ├─ Tips: ["请指定省份与资产类型", "尝试更具体的关键词..."]
   └─ Mode: "vertex_rag"

9. ADD METADATA & RETURN
   ├─ Add trace_id: "gaea-abc123def456"
   ├─ Add elapsed_ms: 1250
   └─ Add mode: "perplexity_qa|vertex_rag|cse_fallback"

10. FRONTEND RECEIVES RESPONSE
    ├─ Parse JSON
    ├─ Extract answer_zh or refusal
    ├─ Display citations with links
    ├─ Show trace_id for debugging
    └─ Hide loading spinner

11. USER SEES RESULTS
    ├─ Question: "光伏发电项目并网验收需要哪些资料？"
    ├─ Answer: "并网要点（广东 / 光伏）\n- 相关规定：..."
    ├─ Citations: [Clickable links to government sources]
    └─ Trace ID: gaea-abc123def456
```

### Data Structures in Transit

**Question Normalization** (sanitize.normalize_query):
```
Input:  "光伏发电项目  并网验收  需要哪些资料？？？"
Output: "光伏发电项目 并网验收 需要哪些资料"
```

**Document Chunk Structure** (in Vector Index):
```python
{
  'id': 'doc-gd-solar-00001-chunk-3',
  'text': 'Chunk content (400-800 tokens)',
  'metadata': {
    'title': '广东省分布式光伏发电管理办法',
    'url': 'https://gd.gov.cn/...',
    'province': 'gd',
    'asset': 'solar',
    'doc_class': 'grid',
    'effective_date': '2023-01-15',
    'source_type': 'regulation',
    'chunk_index': 3,
    'doc_id': 'doc-gd-solar-00001'
  },
  'embedding': [0.123, 0.456, ..., 0.789]  # 768 dims
}
```

**Citation Object** (in Response):
```python
{
  'title': '广东省分布式光伏发电管理办法',
  'url': 'https://gd.gov.cn/...',
  'effective_date': '2023-01-15'  # Optional
}
```

---

## Part 9: Integration Points

### External Services Integrated

| Service | Purpose | Sync/Async | Auth | Used In |
|---------|---------|-----------|------|---------|
| **Perplexity API** | High-precision QA | Sync | API Key (Secret Mgr) | Query function |
| **Vertex AI** | Vector search | Sync | GCP IAM | Query + Ingest |
| **Document AI** | OCR/text extraction | Sync | GCP IAM | Ingest function |
| **Google CSE** | Document discovery | Sync | API Key + Engine ID | Query + Ingest |
| **Gemini API** | Reranking | Sync | API Key (Secret Mgr) | Query (optional) |
| **GCS** | Document storage | Sync | GCP IAM | Ingest function |
| **Secret Manager** | Credential storage | Sync | GCP IAM | All functions |
| **Cloud Logging** | Structured logs | Async | GCP IAM | All functions |

### Perplexity API Integration (Query Function)

**Endpoint**: https://api.perplexity.ai/chat/completions

**Authentication**: Bearer token in Authorization header

**Request Structure**:
```python
{
    "model": "sonar-pro",
    "messages": [
        {
            "role": "system",
            "content": "You are a Chinese compliance assistant..."
        },
        {
            "role": "user",
            "content": "问题：...\n范围与限制：...\n搜索提示：..."
        }
    ],
    "search_domain_filter": [  # ✅ KEY PARAMETER FOR .gov.cn FILTERING
        "gov.cn",
        "ndrc.gov.cn",
        "nea.gov.cn",
        "gd.gov.cn",
        ...
    ],  # Max 20 domains
    "search_recency_filter": "year",  # 2024 documents only
    "return_citations": true
}
```

**Response Structure**:
```python
{
    "choices": [
        {
            "message": {
                "content": "Chinese answer text with citations..."
            }
        }
    ],
    "citations": [
        "https://gd.gov.cn/doc1",
        "https://ndrc.gov.cn/doc2",
        ...
    ]
}
```

**Citation Filtering Logic**:
1. Extract citations array from response
2. Extract URLs from answer text (regex: `https?://[\w\-./%?&#=:+]+`)
3. Merge both sources, deduplicate
4. Filter URLs by allowlist (must be .gov.cn domain)
5. Sort by relevance (preferred domains first)
6. Return top-6

**Topic-Based Domain Selection**:
- Grid connection queries: Include gdwenergy.gov.cn
- Land survey queries: Include mnr.gov.cn, mee.gov.cn
- Rail freight queries: Include mot.gov.cn, nra.gov.cn
- All: Include core government domains

### Vertex AI Integration (Query + Ingest)

**Vector Index Structure**:
- Index type: Streaming (updated in real-time)
- Dimensions: 768
- Distance metric: Cosine similarity

**Index Endpoint**: Private VPC endpoint (not public)

**Upsert Operation** (Ingest):
```python
# For each chunk:
chunks = [
    {
        'id': 'unique-chunk-id',
        'text': 'chunk content',
        'metadata': {'province': 'gd', 'asset': 'solar', ...},
        'embedding': [0.123, 0.456, ...]
    },
    ...
]
upsert_chunks(chunks)  # Batch operation
```

**Search Operation** (Query):
```python
# Embed question
query_vector = embed_query("光伏发电项目并网验收需要什么资料？")

# Search with filters
filters = {
    'province': 'gd',
    'asset': 'solar',
    'doc_class': 'grid'
}
candidates = search_documents(query_vector, filters, top_k=12)

# Returns:
[
    {
        'text': 'chunk content',
        'metadata': {...},
        'distance': 0.15  # Lower = more similar
    },
    ...
]
```

### Document AI Integration (Ingest)

**Purpose**: Extract text and layout from PDF documents

**Process**:
1. Fetch document from URL
2. Upload to Document AI processor
3. Get OCR'd text and layout information
4. Extract key fields (title, date, etc.)

**Processor Configuration**:
- Type: Form parser or general document parser
- Language: Chinese (zh-CN)
- Output format: Structured JSON with text + coordinates

---

## Part 10: Deployment Infrastructure

### Cloud Functions Deployment

**Function Specifications**:

| Attribute | Value |
|-----------|-------|
| Runtime | Python 3.11 |
| Gen | 2 (Cloud Functions 2nd generation) |
| Region | asia-east2 (Hong Kong) |
| Memory | 2GB (query), 1GB (health), 1GB (ingest) |
| Timeout | 540s (query), 60s (health), 300s (ingest) |
| Max Instances | 10 (query), 5 (health), 5 (ingest) |
| Trigger | HTTP (all are HTTP-triggered) |
| Authentication | Unauthenticated (all allow public access) |

**Service Account**:
- Name: `nemo-query@[PROJECT_ID].iam.gserviceaccount.com`
- Permissions needed:
  - Vertex AI Vector Search: Read/search
  - Secret Manager: Access secrets
  - Document AI: Invoke processor
  - GCS: Read/write
  - Cloud Logging: Write logs

**Deployment Process**:

```bash
# 1. Deploy query function
gcloud functions deploy nemo-query \
  --gen2 \
  --runtime=python311 \
  --region=asia-east2 \
  --source=./functions/query \
  --entry-point=query_handler \
  --trigger-http \
  --allow-unauthenticated \
  --timeout=540s \
  --memory=2Gi \
  --max-instances=10 \
  --service-account=nemo-query@[PROJECT_ID].iam.gserviceaccount.com \
  --set-env-vars="PROJECT_ID=[PROJECT_ID],REGION=asia-east2,..." \
  --set-secrets="PERPLEXITY_API_KEY=PERPLEXITY_API_KEY:latest,..."

# 2. Deploy health function (similar)
# 3. Deploy ingest function (similar)
```

### GCS Storage Structure

**Raw Bucket** (`[project]-nemo-raw/`):
```
gs://[project]-nemo-raw/
├── gd/
│   ├── solar/
│   │   ├── doc-001.pdf
│   │   ├── doc-002.pdf
│   │   └── doc-003.pdf
│   └── coal/
│       └── ...
├── sd/
│   └── ...
└── nm/
    └── ...
```

**Clean Bucket** (`[project]-nemo-clean/`):
```
gs://[project]-nemo-clean/
├── gd/
│   ├── solar/
│   │   ├── doc-001-extracted.json
│   │   └── doc-002-extracted.json
│   └── coal/
│       └── ...
└── ...
```

### Vector Index Setup

**Create Index**:
```bash
gcloud ai indexes create \
  --display-name="nemo-compliance-index" \
  --description="Chinese regulatory documents with metadata filters" \
  --metadata-schema-uri="gs://google-cloud-aiplatform/schema/matchingengine/metadata/nearest_neighbor_search_1.0.0.yaml" \
  --region=asia-east2
```

**Create Endpoint**:
```bash
gcloud ai index-endpoints create \
  --display-name="nemo-compliance-endpoint" \
  --region=asia-east2
```

**Deploy Index to Endpoint**:
```bash
gcloud ai index-endpoints deploy-index \
  --index-endpoint=[ENDPOINT_ID] \
  --deployed-index-id=nemo-compliance-index-deployed \
  --index=[INDEX_ID] \
  --region=asia-east2
```

### Secret Manager Configuration

**Secrets to Create**:
```bash
# Perplexity API Key (REQUIRED)
echo 'your-perplexity-api-key' | \
  gcloud secrets create PERPLEXITY_API_KEY --data-file=-

# Google CSE Configuration
echo 'your-cse-api-key' | \
  gcloud secrets create GOOGLE_CSE_API_KEY --data-file=-
echo 'your-cse-engine-id' | \
  gcloud secrets create GOOGLE_CSE_ENGINE_ID --data-file=-

# Gemini API Key (optional, for reranking)
echo 'your-gemini-api-key' | \
  gcloud secrets create GEMINI_API_KEY --data-file=-

# Ingest Token
echo 'your-secure-random-token' | \
  gcloud secrets create INGEST_TOKEN --data-file=-
```

**Secret Mounting** (in deployment):
```bash
--set-secrets="PERPLEXITY_API_KEY=PERPLEXITY_API_KEY:latest,\
               GOOGLE_CSE_API_KEY=GOOGLE_CSE_API_KEY:latest,\
               GOOGLE_CSE_ENGINE_ID=GOOGLE_CSE_ENGINE_ID:latest,\
               GEMINI_API_KEY=GEMINI_API_KEY:latest,\
               INGEST_TOKEN=INGEST_TOKEN:latest"
```

### Cloud Scheduler for Ingestion

**Create Nightly Ingestion Job**:
```bash
gcloud scheduler jobs create http nightly-ingest \
  --location=asia-east2 \
  --schedule="0 21 * * *" \
  --uri="https://asia-east2-[project-id].cloudfunctions.net/nemo-ingest" \
  --http-method=POST \
  --headers="X-Ingest-Token=your-secure-token"
```

**Alternative**: Trigger manually for testing:
```bash
gcloud scheduler jobs run nightly-ingest --location=asia-east2
```

### Frontend Hosting

**Options**:
1. **Cloud Storage + Cloud CDN** (static files only)
   - Upload index.html, CSS, JS to GCS bucket
   - Configure bucket as public website
   - Add Cloud CDN for caching
   - Cost: ~$0.12/GB egress + CDN

2. **Cloud Run** (if need server-side logic)
   - Container with simple HTTP server
   - Serves static files
   - Can add API routing logic

3. **Firebase Hosting** (recommended for simplicity)
   - Push from git branch
   - Automatic SSL/HTTPS
   - Global CDN
   - Integrates with Cloud Functions

4. **External CDN** (e.g., Cloudflare)
   - Point DNS to Cloudflare
   - Cache static files
   - Origin: GCS bucket or Cloud Run

**Recommended Setup** (for ChatGPT-clone):
```
┌─────────────────┐
│   User Browser  │
└────────┬────────┘
         │
         ↓
   ┌─────────────┐
   │ CloudFlare  │ (DNS + Caching)
   └──────┬──────┘
          │
          ├─────→ Cloud Run (Frontend + API routing)
          │           ├─ Serves index.html
          │           └─ Routes /api/* to Cloud Functions
          │
          └─────→ Cloud Functions (Direct API calls)
                      ├─ /api/query
                      ├─ /api/health
                      └─ /api/ingest
```

---

## Part 11: Testing Infrastructure

### Test Structure

**Test Files**:
```
tests/
├── test_functions.py              # Cloud Function endpoint tests
├── test_composer.py               # Response formatting tests
├── test_chunker.py                # Document chunking tests
├── test_sanitize.py               # Text normalization tests
├── test_vertex_index.py           # Vector search tests
├── test_cse.py                    # CSE discovery tests
├── test_docai.py                  # Document AI tests
├── test_metadata_extractor.py     # Metadata extraction tests
├── test_gemini_rerank.py          # Reranking tests
└── integration/
    └── test_end_to_end.py         # End-to-end flow tests
```

### Running Tests

**Unit Tests**:
```bash
# Test a specific module
pytest tests/test_composer.py -v

# Test all
pytest tests/ -v

# With coverage
pytest tests/ --cov=lib --cov-report=html
```

**Integration Tests**:
```bash
# Run against real APIs (requires env vars)
export VERTEX_INDEX_ID=...
export VERTEX_ENDPOINT_ID=...
pytest tests/integration/ -v
```

**Local Function Testing**:
```bash
# Start function locally
cd functions/query
functions-framework --target=query_handler --debug --port=8081

# In another terminal, test
curl -X POST http://localhost:8081 \
  -H "Content-Type: application/json" \
  -d '{
    "province": "gd",
    "asset": "solar",
    "doc_class": "grid",
    "question": "并网需要什么资料？"
  }'
```

### Test Example (test_functions.py)

```python
def test_query_handler_valid_request(self):
    """Test query handler with valid request"""
    request_data = {
        'province': 'gd',
        'asset': 'solar',
        'doc_class': 'grid',
        'question': '光伏并网验收需要什么资料？',
        'lang': 'zh-CN'
    }
    
    mock_request = Mock()
    mock_request.get_json.return_value = request_data
    mock_request.method = 'POST'
    
    with patch('main.search_documents') as mock_search, \
         patch('main.compose_response') as mock_compose:
        
        mock_search.return_value = [...]  # Mock data
        mock_compose.return_value = {...}  # Expected response
        
        response = query_handler(mock_request)
    
    assert response[1] == 200
    response_data = json.loads(response[0])
    assert 'answer_zh' in response_data
    assert 'citations' in response_data
    assert 'trace_id' in response_data
```

---

## Part 12: Security & Access Control

### Authentication & Authorization

**Query Function**:
- Public: `--allow-unauthenticated`
- No API key required
- Relies on cloud function URL being hard to guess
- Rate limiting via Cloud Functions quotas

**Health Function**:
- Public: `--allow-unauthenticated`
- No sensitive data exposed

**Ingest Function**:
- Token-based: `X-Ingest-Token` header required
- Not identity-based (no Cloud IAM users needed)
- Token stored in Secret Manager
- Should only be called from Cloud Scheduler (internal trigger)

### Data Security

**In Transit**:
- All Cloud Functions HTTPS only
- TLS 1.2+ enforced
- CORS allows browser requests from any origin (necessary for frontend)

**At Rest**:
- GCS buckets: Encryption at rest (Google-managed keys)
- Secret Manager: Encrypted storage of API keys
- Vertex AI index: Managed by Google

**API Keys**:
- Never hardcoded in code
- Stored in Secret Manager
- Injected as environment variables at runtime
- Different keys for different environments (dev/prod)

### CORS Configuration

**Headers Sent**:
```
Access-Control-Allow-Origin: *
Access-Control-Allow-Methods: GET,POST,OPTIONS
Access-Control-Allow-Headers: Content-Type,Authorization,X-Ingest-Token
Access-Control-Max-Age: 3600
```

**Why Open CORS**:
- Browser requests come from different domain (frontend hosted separately)
- No sensitive user data (all queries are anonymous)
- System is designed for public compliance queries (no auth)

**Limiting Access**:
- Frontend can be IP-restricted at hosting level
- Or: Move frontend to same domain as functions (Cloud Run)
- Or: Add OAuth2 if user authentication needed later

### Audit & Logging

**All Requests Logged**:
```python
print(f"[{trace_id}] Query request: province={province}, asset={asset}")
print(f"[{trace_id}] Perplexity QA returned {len(citations)} citations")
print(f"[{trace_id}] Response composed in {compose_ms}ms, total: {elapsed_ms}ms")
```

**Trace ID Format**: `gaea-{uuid.hex[:12]}`
- Unique per request
- Embedded in response
- Can search logs by trace_id

**Log Destination**: Cloud Logging (GCP)
- Structured logging
- Queryable by trace_id, function, status
- Retention: 30 days default

---

## Part 13: Integration Recommendations for ChatGPT-Clone Frontend

### Architecture for New UI

```
Old Setup:
  Frontend (index.html) → Cloud Functions (HTTP endpoints)

New Setup for ChatGPT Clone:
  ChatGPT Clone UI → API Gateway OR Cloud Run
                      ├─ Routes /api/* → Cloud Functions
                      ├─ Handles auth/session management (optional)
                      └─ Serves static assets (optional)
```

### Option 1: Cloud Run Wrapper (Recommended)

**Benefits**:
- Single domain for frontend + API
- Can add session management
- Can add rate limiting
- Can add authentication layer

**Setup**:
```dockerfile
# Dockerfile
FROM node:18-slim
WORKDIR /app
COPY frontend/ /app/public/
RUN npm install express

# app.js - simple proxy
const express = require('express');
const app = express();

// Serve static files
app.use(express.static('public'));

// Proxy /api/* to Cloud Functions
app.post('/api/query', async (req, res) => {
  const response = await fetch(
    'https://asia-east2-[project].cloudfunctions.net/nemo-query',
    { method: 'POST', body: JSON.stringify(req.body) }
  );
  res.json(await response.json());
});

app.listen(8080);
```

**Deploy**:
```bash
gcloud run deploy nemo-frontend \
  --source . \
  --platform managed \
  --region asia-east2 \
  --allow-unauthenticated
```

### Option 2: API Gateway + Cloud Storage Frontend

**Benefits**:
- Separate frontend hosting (Cloud Storage + CDN)
- Simpler to version frontend independently
- Lower cost (no Cloud Run instance needed)

**Setup**:
1. Upload frontend to `gs://[project]-nemo-frontend/`
2. Create API Gateway:
   ```bash
   gcloud api-gateway apis create nemo-api
   gcloud api-gateway api-configs create nemo-config \
     --api=nemo-api \
     --backend-auth-service-account=nemo-query@[project].iam.gserviceaccount.com
   ```
3. Use Cloud DNS or external CDN to route both

### Option 3: Modify Frontend to Support Advanced Features

**For ChatGPT-Clone**, consider adding:

1. **Conversation History**:
   - Store in Firestore
   - Session ID in cookie
   - Multiple questions in one conversation

2. **User Accounts**:
   - Firebase Authentication
   - Per-user query history
   - Saved documents/citations

3. **Advanced Search**:
   - Document type filtering
   - Date range filtering
   - Relevance ranking control
   - Multiple question types

4. **Export/Share**:
   - PDF export of results
   - Share citations via link
   - Citation formatting (APA, Chicago, etc.)

### Frontend Code for New Features

**Conversation History Example**:
```javascript
let conversationHistory = [];

async function sendMessage(message) {
  // Add to history
  conversationHistory.push({
    role: 'user',
    content: message,
    timestamp: new Date()
  });

  // Send to API
  const response = await fetch('/api/query', {
    method: 'POST',
    body: JSON.stringify({
      province, asset, doc_class, question: message, lang
    })
  });

  const result = await response.json();
  
  // Add response to history
  conversationHistory.push({
    role: 'assistant',
    content: result.answer_zh,
    citations: result.citations,
    trace_id: result.trace_id,
    timestamp: new Date()
  });

  // Render conversation
  renderConversation();
}

function renderConversation() {
  conversationHistory.forEach(msg => {
    if (msg.role === 'user') {
      // Show user message
      renderUserMessage(msg.content);
    } else {
      // Show assistant response
      renderAssistantMessage(msg.content, msg.citations);
    }
  });
}
```

**Session Management Example**:
```javascript
async function initSession() {
  const sessionId = getOrCreateSessionId();
  
  // Create session in backend
  await fetch('/api/session', {
    method: 'POST',
    body: JSON.stringify({ sessionId })
  });
  
  // All subsequent requests include sessionId
  const response = await fetch('/api/query', {
    method: 'POST',
    body: JSON.stringify({
      sessionId,
      province, asset, question, lang
    })
  });
}

function getOrCreateSessionId() {
  let sessionId = localStorage.getItem('nemo_session_id');
  if (!sessionId) {
    sessionId = 'session-' + Date.now() + '-' + Math.random().hex(6);
    localStorage.setItem('nemo_session_id', sessionId);
  }
  return sessionId;
}
```

---

## Part 14: Deployment Strategy for New UI

### Step 1: Understand Current Deployment

**Current Status**:
- Query, Health, Ingest functions: Already deployed in asia-east2
- Frontend: Currently at `/frontend/index.html`
- Deployment scripts: `/deploy/deploy-query-function.sh` (uses Cloud Build)

### Step 2: Choose Hosting Approach

**Recommendation for ChatGPT-Clone**:
```
Option 1 (Simplest):
  Cloud Run (Node.js app)
    ├─ Serves frontend (new React/Vue app)
    └─ Proxy routes to existing Cloud Functions
  
  Cost: ~$0.025/hour + egress
  Time: 30 minutes setup
  Scalability: Automatic
```

### Step 3: Update API Integration

**If using Cloud Run as proxy**:
```javascript
// frontend/src/api.js
const API_BASE = window.location.origin + '/api';

export async function queryCompliance(request) {
  const response = await fetch(`${API_BASE}/query`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(request)
  });
  return response.json();
}
```

**If using Cloud Functions directly**:
```javascript
// frontend/src/api.js
const QUERY_URL = 'https://asia-east2-[project].cloudfunctions.net/nemo-query';

export async function queryCompliance(request) {
  const response = await fetch(QUERY_URL, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(request)
  });
  return response.json();
}
```

### Step 4: Environment Configuration

**For Production**:
```yaml
# config/production.yaml
QUERY_URL: https://asia-east2-[project].cloudfunctions.net/nemo-query
HEALTH_URL: https://asia-east2-[project].cloudfunctions.net/nemo-health
REGION: asia-east2
PROJECT_ID: day-planner-london-mvp
PERPLEXITY_MODEL: sonar-pro
```

**For Development**:
```yaml
# config/development.yaml
QUERY_URL: http://localhost:8081
HEALTH_URL: http://localhost:8080
REGION: asia-east2-dev
```

### Step 5: Deployment Pipeline

**Using Cloud Build** (CI/CD):
```yaml
# cloudbuild.yaml
steps:
  # Step 1: Build frontend
  - name: 'node:18'
    entrypoint: npm
    args: ['ci']
    dir: 'frontend'

  # Step 2: Run tests
  - name: 'node:18'
    entrypoint: npm
    args: ['test']
    dir: 'frontend'

  # Step 3: Build Docker image
  - name: 'gcr.io/cloud-builders/docker'
    args:
      - build
      - -t
      - gcr.io/$PROJECT_ID/nemo-frontend:$COMMIT_SHA
      - .

  # Step 4: Push to Container Registry
  - name: 'gcr.io/cloud-builders/docker'
    args:
      - push
      - gcr.io/$PROJECT_ID/nemo-frontend:$COMMIT_SHA

  # Step 5: Deploy to Cloud Run
  - name: 'gcr.io/cloud-builders/gke-deploy'
    args:
      - run
      - --filename=k8s/
      - --image=gcr.io/$PROJECT_ID/nemo-frontend:$COMMIT_SHA
      - --location=asia-east2
      - --cluster=nemo

images:
  - gcr.io/$PROJECT_ID/nemo-frontend:$COMMIT_SHA
```

---

## Part 15: File Structure Recommendations for ChatGPT-Clone

### Recommended Project Layout

```
/home/user/Nemo_Time/
├── functions/                    # Existing Cloud Functions (UNCHANGED)
│   ├── query/
│   ├── health/
│   └── ingest/
│
├── frontend/                     # New ChatGPT-clone frontend
│   ├── public/
│   │   ├── index.html
│   │   └── favicon.svg
│   ├── src/
│   │   ├── App.jsx              # Main app component
│   │   ├── components/
│   │   │   ├── ChatMessage.jsx   # Message bubble component
│   │   │   ├── SettingsPanel.jsx # Province/asset selector
│   │   │   ├── ChatInput.jsx     # Message input
│   │   │   ├── Citations.jsx     # Citation display
│   │   │   └── SessionHistory.jsx # Conversation history
│   │   ├── hooks/
│   │   │   ├── useChat.js        # Custom hook for chat logic
│   │   │   └── useSession.js     # Session management hook
│   │   ├── services/
│   │   │   ├── api.js            # API client
│   │   │   ├── storage.js        # Local storage management
│   │   │   └── analytics.js      # Optional telemetry
│   │   ├── styles/
│   │   │   ├── App.css
│   │   │   ├── variables.css
│   │   │   └── components.css
│   │   └── index.jsx             # React entry point
│   ├── .env.example
│   ├── package.json
│   ├── vite.config.js            # Or webpack.config.js
│   └── Dockerfile
│
├── deploy/                        # Deployment scripts (EXISTING)
│   ├── deploy-query-function.sh
│   ├── deploy-frontend.sh        # NEW: Frontend deployment
│   └── cloudbuild.yaml           # NEW: CI/CD configuration
│
├── docs/                         # Documentation (EXISTING)
│   ├── FRONTEND_ARCHITECTURE.md  # NEW: Frontend design doc
│   ├── API_INTEGRATION.md        # NEW: API integration guide
│   └── DEPLOYMENT_GUIDE.md       # UPDATED: Include frontend
│
├── tests/                        # Tests (EXISTING + NEW)
│   ├── backend/                  # Existing Python tests
│   └── frontend/                 # NEW: React component tests
│       ├── App.test.jsx
│       ├── components/
│       └── hooks/
│
├── README.md                     # UPDATED: Include frontend
└── NEMO_ARCHITECTURE_ANALYSIS.md # This file
```

### Key Files for New Frontend

**App.jsx** (Main component):
```jsx
import React, { useState, useEffect } from 'react';
import ChatMessage from './components/ChatMessage';
import SettingsPanel from './components/SettingsPanel';
import ChatInput from './components/ChatInput';
import { useChat } from './hooks/useChat';

export default function App() {
  const [province, setProvince] = useState('gd');
  const [asset, setAsset] = useState('solar');
  const [language, setLanguage] = useState('zh-CN');
  const [messages, setMessages] = useState([]);
  const { sendMessage, loading } = useChat({ province, asset, language });

  const handleSendMessage = async (text) => {
    setMessages([...messages, { role: 'user', content: text }]);
    const response = await sendMessage(text);
    setMessages(prev => [...prev, { role: 'assistant', ...response }]);
  };

  return (
    <div className="app">
      <SettingsPanel 
        province={province}
        asset={asset}
        language={language}
        onSettingsChange={{setProvince, setAsset, setLanguage}}
      />
      <div className="chat-container">
        {messages.map((msg, i) => (
          <ChatMessage key={i} message={msg} language={language} />
        ))}
      </div>
      <ChatInput onSendMessage={handleSendMessage} disabled={loading} />
    </div>
  );
}
```

**useChat.js** (Custom hook):
```jsx
import { useState } from 'react';
import { queryCompliance } from '../services/api';

export function useChat({ province, asset, language }) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const sendMessage = async (question) => {
    setLoading(true);
    setError(null);
    try {
      const response = await queryCompliance({
        province,
        asset,
        doc_class: 'grid',
        question,
        lang: language
      });
      return response;
    } catch (err) {
      setError(err.message);
      return { error: true, message: err.message };
    } finally {
      setLoading(false);
    }
  };

  return { sendMessage, loading, error };
}
```

**api.js** (API client):
```javascript
const API_BASE = process.env.REACT_APP_API_URL || '/api';

export async function queryCompliance(request) {
  const response = await fetch(`${API_BASE}/query`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(request)
  });

  if (!response.ok) {
    throw new Error(`API error: ${response.status}`);
  }

  return response.json();
}

export async function getHealth() {
  const response = await fetch(`${API_BASE}/health`);
  return response.json();
}
```

---

## Part 16: Security Considerations for Frontend

### Data Security

**No Sensitive Data Storage**:
- Don't store API keys in frontend code
- Don't store user identity (system is anonymous)
- Session ID only (not authentication token)

**HTTPS Only**:
- All API calls must use HTTPS
- Set secure cookie flag if using sessions

**CSP Headers** (if using Cloud Run):
```
Content-Security-Policy: 
  default-src 'self'; 
  script-src 'self' 'unsafe-inline'; 
  style-src 'self' 'unsafe-inline';
  connect-src 'self' https://api.perplexity.ai;
```

### Rate Limiting

**Client-side**:
- Debounce text input (500ms)
- Disable submit button while loading
- Show loading spinner

**Server-side** (Cloud Functions):
- Built-in quotas: 540s timeout
- Max 10 concurrent instances

**API Gateway** (if using):
- Rate limit by IP: 100 req/min
- Rate limit per API key: 1000 req/day

### XSS Prevention

**Sanitize User Input**:
```jsx
import DOMPurify from 'dompurify';

const sanitizedAnswer = DOMPurify.sanitize(response.answer_zh);
<div dangerouslySetInnerHTML={{ __html: sanitizedAnswer }} />
```

**Escape URLs**:
```javascript
const safeUrl = new URL(citation.url);  // Validate URL
<a href={safeUrl.href} target="_blank" rel="noopener noreferrer">
  {citation.title}
</a>
```

---

## Part 17: Performance Optimization

### Query Performance

**Current Baseline**:
- Perplexity API: 2-5 seconds
- Vector search: 200-500ms
- Response composition: 100-200ms
- Total: p95 < 2 seconds

### Optimization Opportunities

1. **Caching**:
   - Cache frequent queries (Redis/Memstore)
   - Cache embeddings for popular questions
   - TTL: 24 hours

2. **Parallelization**:
   - Search Vertex AI + call Perplexity in parallel
   - Use asyncio for concurrent operations

3. **Index Optimization**:
   - Shard vector index by province/asset
   - Use IVF (Inverted File) index structure
   - Configure appropriate batch size

4. **Frontend Optimization**:
   - Code splitting (lazy load components)
   - Minimize bundle size
   - Use compression (gzip)
   - Cache static assets (Cloud CDN)

### Monitoring Performance

**Metrics to Track**:
- P50, P95, P99 latency
- Error rate (< 1%)
- Throughput (queries/second)
- Cache hit rate

**Cloud Monitoring Dashboard**:
```bash
gcloud monitoring dashboards create --config-from-file=dashboard.json
```

---

## Part 18: Troubleshooting Guide

### Common Issues

**1. 404 Not Found on /api/query**
- Check Cloud Function deployment
- Verify URL in frontend matches actual function URL
- Check CORS headers are being sent

**2. 403 Forbidden on /ingest**
- Verify X-Ingest-Token header matches INGEST_TOKEN env var
- Check Secret Manager has the token
- Verify Cloud Scheduler permissions

**3. Vector search returns 0 results**
- Check index has documents (upserted successfully)
- Verify filters match document metadata
- Try increasing top_k parameter
- Check embedding model (should be consistent)

**4. Perplexity API returns no citations**
- Verify API key is valid
- Check domain_filter list (max 20 domains)
- Check search_recency_filter (year = 2024 only)
- Check rate limits not exceeded

**5. Frontend won't load**
- Check browser console for CORS errors
- Verify frontend is being served (check hosting service logs)
- Verify API_BASE URL is correct

**6. Slow query responses**
- Check Vertex AI index endpoint is ready
- Check Cloud Function memory is sufficient (2GB minimum)
- Profile with Cloud Trace to find bottleneck
- Consider enabling caching

### Debugging with Trace IDs

**Every response includes trace_id**:
```
trace_id: "gaea-abc123def456"
```

**Find logs**:
```bash
gcloud functions logs read nemo-query \
  --region=asia-east2 \
  | grep "gaea-abc123def456"
```

**Search Cloud Logging**:
```bash
gcloud logging read "resource.type=cloud_function AND \
  jsonPayload.trace_id=gaea-abc123def456" \
  --limit=50 \
  --format=json
```

---

## Part 19: Testing Checklist for New Frontend

### Unit Tests
- [ ] Chat message component renders correctly
- [ ] Settings panel updates state
- [ ] API client formats requests correctly
- [ ] Custom hooks manage state properly

### Integration Tests
- [ ] Frontend → Cloud Functions request/response
- [ ] Error handling for API failures
- [ ] Loading states during requests
- [ ] CORS headers present in responses

### End-to-End Tests
- [ ] Submit question in UI
- [ ] Receive and display answer
- [ ] Display citations with links
- [ ] Show trace ID for debugging
- [ ] Error message display

### Performance Tests
- [ ] Page load time < 2s
- [ ] Bundle size < 500KB gzipped
- [ ] Query response < 3s p95
- [ ] No memory leaks in conversation

### Security Tests
- [ ] XSS prevention (sanitize user input)
- [ ] CSRF token if stateful
- [ ] Secure headers present
- [ ] No sensitive data in localStorage
- [ ] HTTPS enforced

---

## Part 20: Migration Path from Old to New Frontend

### Phase 1: Development (Week 1-2)
1. Create new frontend codebase
2. Implement React components
3. Update API client to match Cloud Functions
4. Test locally with dev server

### Phase 2: Staging (Week 3)
1. Deploy new frontend to staging Cloud Run instance
2. Point staging traffic to production Cloud Functions
3. Run E2E tests against production API
4. Gather user feedback

### Phase 3: Canary Deployment (Week 4)
1. Deploy new frontend to production Cloud Run
2. Route 10% traffic to new frontend
3. Monitor error rates, latency, user behavior
4. If stable, increase to 50%, then 100%

### Phase 4: Cutover (Week 5)
1. 100% traffic to new frontend
2. Keep old HTML UI available at `/legacy/`
3. Monitor for issues
4. Clean up after 1 week

### Rollback Plan
```bash
# If issues, rollback to previous Cloud Run revision
gcloud run revisions list --service=nemo-frontend
gcloud run services update-traffic nemo-frontend \
  --to-revisions=[PREVIOUS_REVISION_HASH]=100
```

---

## Summary: Architecture Overview Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                     END USER BROWSER                             │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                    HTTPS Request
                           │
        ┌──────────────────┴──────────────────┐
        │                                     │
        ▼                                     ▼
    ┌────────┐                          ┌─────────┐
    │CloudRun│◄─┬─── (Option 1)         │CloudRun │
    │Frontend│  │  (Recommended)        │ Frontend│
    │  (React)  │                       │(Angular)│
    └────┬───┘  │                       └────┬────┘
         │      │ (Option 2)                 │
         │      └──► Cloud Storage           │
         │          + Cloud CDN              │
         └──────────────┬────────────────────┘
                        │
                /api/query | /api/health
                        │
                  API Gateway OR
              Direct Cloud Functions
                        │
        ┌───────────────┼───────────────┐
        │               │               │
        ▼               ▼               ▼
    ┌────────┐    ┌──────────┐    ┌────────┐
    │ Query  │    │ Health   │    │ Ingest │
    │Function│    │Function  │    │Function│
    └────┬───┘    └────┬─────┘    └────┬───┘
         │             │               │
    ┌────┴─────┬───────┴────┬──────────┴──────┐
    │           │           │                 │
    ▼           ▼           ▼                 ▼
 Perplexity  Vertex AI   GCS      Cloud
   API       Vector     Buckets   Logging
            Search      (raw,
             Index      clean)

External Services:
- Perplexity API (High-precision QA)
- Google Vertex AI (Vector search)
- Google CSE (Document discovery)
- Google Document AI (OCR)
- Google Gemini (Optional reranking)
```

---

## Conclusion

The Nemo Compliance MVP is a well-architected, production-ready RAG system for Chinese regulatory compliance. It integrates multiple Google Cloud services with a clean, modular design pattern.

**Key Strengths**:
1. Modular architecture (easy to extend)
2. Zero mock data (always reliable)
3. CORS-enabled (integrates with any frontend)
4. Token-traced (fully debuggable)
5. Scalable serverless (auto-scaling)

**For ChatGPT-Clone Integration**:
1. Keep Cloud Functions as-is (no changes needed)
2. Build new frontend (React/Vue)
3. Deploy on Cloud Run with proxy logic
4. Add session management and conversation history
5. Use same trace_id based debugging

**Next Steps**:
1. Review this architecture with team
2. Choose frontend technology (React recommended)
3. Plan migration from old to new frontend
4. Start development with staging environment
5. Test thoroughly before production deployment

---

**Document Prepared By**: Committee 4
**Date**: November 2024
**Status**: Complete Architecture Analysis Ready for Implementation
