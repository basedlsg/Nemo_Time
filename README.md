# Nemo Compliance MVP

A serverless, Google Cloud-native system that provides verified regulatory information for Chinese energy projects (Solar, Coal, Wind) with quote-first Chinese answers and perfect citations.

## 🎯 Purpose

Build the smallest, most reliable system that returns **verified, regulation-grade documents** for Chinese energy projects with **verbatim Chinese quotes** and **clickable government portal citations** — using **Google Cloud services only**, with **zero mock data**.

## ✅ Implementation Status

**COMPLETE** - All 24 tasks across 12 major phases have been implemented:

- ✅ **Core Infrastructure** - Cloud Functions, shared libraries, configuration
- ✅ **Text Processing** - Chinese normalization, chunking, metadata extraction
- ✅ **Vector Search** - Vertex AI integration with embeddings and filtering
- ✅ **Document Processing** - Document AI OCR with quality validation
- ✅ **Search & Discovery** - Google CSE integration with government domain allowlisting
- ✅ **Query Processing** - Real-time search with optional Gemini reranking
- ✅ **Response Composition** - Verbatim Chinese quotes with proper citations
- ✅ **Comprehensive Testing** - Unit, integration, and golden set evaluation
- ✅ **Frontend Interface** - Responsive Chinese/English web interface
- ✅ **Production Deployment** - Automated deployment and monitoring setup

## 🏗️ Architecture

- **Offline Ingestion**: Curated document discovery, OCR processing, and vector indexing
- **Online Query**: Deterministic RAG from managed vector index (no live web search)
- **Serverless**: Cloud Functions (2nd gen) with Vertex AI and Document AI
- **No Docker**: Pure Google Cloud managed services

## 🚀 Quick Start

### Prerequisites

1. Google Cloud Project with billing enabled
2. `gcloud` CLI installed and authenticated
3. Required APIs will be enabled during deployment

### Deploy

```bash
# Clone and navigate to project
git clone <repository-url>
cd nemo-compliance-mvp

# Set your project ID
export GOOGLE_CLOUD_PROJECT="your-project-id"

# Deploy all functions and infrastructure
./deploy/deploy.sh
```

### Post-Deployment Setup

1. **Create Vertex AI Vector Search Index**:
   ```bash
   # Create index (replace with your values)
   gcloud ai indexes create \
     --display-name="nemo-compliance-index" \
     --description="Chinese regulatory documents" \
     --metadata-schema-uri="gs://google-cloud-aiplatform/schema/matchingengine/metadata/nearest_neighbor_search_1.0.0.yaml" \
     --region=asia-east2
   ```

2. **Update Function Environment Variables**:
   ```bash
   # Update query function with index/endpoint IDs
   gcloud functions deploy nemo-query \
     --update-env-vars VERTEX_INDEX_ID=your-index-id,VERTEX_ENDPOINT_ID=your-endpoint-id
   ```

3. **Set up Google Custom Search Engine**:
   - Create CSE at https://cse.google.com/
   - Add allowlisted domains: `gd.gov.cn`, `sd.gov.cn`, `nmg.gov.cn`
   - Update secrets with CSE ID and API key

4. **Configure Cloud Scheduler**:
   ```bash
   # Create nightly ingestion job
   gcloud scheduler jobs create http nightly-ingest \
     --schedule="0 21 * * *" \
     --uri="https://your-ingest-url" \
     --http-method=POST \
     --headers="X-Ingest-Token=your-token"
   ```

## 📡 API Endpoints

### Health Check
```bash
GET /health
```

### Query Documents
```bash
POST /query
Content-Type: application/json

{
  "province": "gd",
  "asset": "solar", 
  "doc_class": "grid",
  "question": "并网验收需要哪些资料？",
  "lang": "zh-CN"
}
```

### Trigger Ingestion (Secured)
```bash
POST /ingest
X-Ingest-Token: your-secure-token
Content-Type: application/json

{
  "province": "gd",
  "asset": "solar",
  "doc_class": "grid"
}
```

## 🧪 Testing

```bash
# Test health endpoint
curl https://your-health-url

# Test query endpoint
curl -X POST https://your-query-url \
  -H "Content-Type: application/json" \
  -d '{
    "province": "gd",
    "asset": "solar",
    "doc_class": "grid", 
    "question": "并网需要什么资料？"
  }'
```

## 📁 Project Structure

```
├── functions/
│   ├── query/          # Real-time query processing
│   ├── ingest/         # Document ingestion pipeline  
│   └── health/         # System health monitoring
├── lib/                # Shared libraries
│   ├── vertex_index.py # Vertex AI integration
│   ├── sanitize.py     # Text processing
│   ├── chunker.py      # Document chunking
│   ├── composer.py     # Response formatting
│   ├── docai.py        # Document AI integration
│   └── cse.py          # Google Custom Search
├── config/             # Configuration files
├── deploy/             # Deployment scripts
└── docs/               # Documentation
```

## 🔧 Configuration

### Environment Variables

Key environment variables (set during deployment):

- `GOOGLE_CLOUD_PROJECT`: Your GCP project ID
- `REGION`: Deployment region (default: asia-east2)
- `VERTEX_INDEX_ID`: Vector search index ID
- `VERTEX_ENDPOINT_ID`: Vector search endpoint ID
- `BUCKET_RAW`: Raw documents bucket
- `BUCKET_CLEAN`: Processed documents bucket
- `RERANK`: Enable/disable Gemini reranking (default: false)

### Secrets (Google Secret Manager)

- `gemini-api-key`: Gemini API key for reranking
- `perplexity-api-key`: Perplexity API key  
- `google-cse-id`: Google Custom Search Engine ID
- `google-api-key`: Google API key for CSE
- `ingest-token`: Secure token for ingestion endpoint

## 🎯 MVP Scope

- **Provinces**: Guangdong (gd), Shandong (sd), Inner Mongolia (nm)
- **Assets**: Solar, Coal, Wind
- **Document Class**: Grid Connection (并网) only
- **Languages**: Chinese (zh-CN) primary, English (en) optional

## 🚫 No Mock Data Policy

This system **never** returns mock data. If no relevant documents are found, it returns an honest refusal with actionable tips.

## 📊 Performance Targets

- **Query Response**: p95 < 2.0 seconds
- **Accuracy**: ≥90% precision with correct citations
- **Availability**: 99.9% uptime
- **Throughput**: 100 queries/second

## 🔍 Monitoring

- **Cloud Logging**: Structured logs with trace IDs
- **Performance Metrics**: Latency, error rates, ingestion volume
- **Health Checks**: Automated service connectivity validation
- **Alerts**: Error rate >2% or health check failures

## 🛠️ Development

### Local Development

```bash
# Install dependencies for a function
cd functions/query
pip install -r requirements.txt

# Run tests
python -m pytest tests/

# Local function testing
functions-framework --target=query_handler --debug
```

### Adding New Provinces/Assets

1. Update validation in function handlers
2. Add to allowlist domains configuration
3. Update province/asset name mappings in composer
4. Test with sample documents

## 📚 Documentation

- [Requirements](.kiro/specs/nemo-compliance-mvp/requirements.md) - Detailed requirements and acceptance criteria
- [Design](.kiro/specs/nemo-compliance-mvp/design.md) - Technical architecture and design decisions  
- [Tasks](.kiro/specs/nemo-compliance-mvp/tasks.md) - Implementation plan and progress tracking
- [Deployment Guide](docs/DEPLOYMENT_GUIDE.md) - Complete production deployment instructions

## 🤝 Contributing

1. Follow the no-mock-data policy strictly
2. All changes must include tests
3. Update documentation for user-visible changes
4. Use structured logging with trace IDs

## 📄 License

[Your License Here]

## 🆘 Support

For issues and support:

1. Check the [troubleshooting guide](docs/troubleshooting.md)
2. Search Cloud Logging with trace ID from error responses
3. Review function logs in Google Cloud Console
4. Create issue with trace ID and error details