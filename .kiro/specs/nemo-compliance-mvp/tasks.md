# Implementation Plan

- [x] 1. Set up project structure and core configuration
  - Create directory structure for Cloud Functions: `/functions/query/`, `/functions/ingest/`, `/functions/health/`
  - Create shared library directory: `/lib/` with modules for vertex_index, docai, sanitize, chunker, cse, composer
  - Set up requirements.txt files for each function with Google Cloud dependencies
  - Create environment configuration files and Secret Manager integration
  - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6_

- [x] 2. Implement core utility libraries
- [x] 2.1 Create text sanitization and normalization module
  - Write `normalize_text()` function to clean Chinese text and standardize punctuation
  - Implement `extract_effective_date()` function with regex patterns for Chinese date formats
  - Create unit tests for text processing edge cases
  - _Requirements: 2.3, 2.4_

- [x] 2.2 Implement document chunking logic
  - Write `create_chunks()` function for 800-token chunks with 100-token overlap
  - Add metadata preservation during chunking process
  - Create tests for chunk boundary handling and overlap validation
  - _Requirements: 2.4_

- [x] 2.3 Create Vertex AI integration module
  - Implement `embed_text()` function using text-embedding-004 model
  - Write `upsert_chunks()` function for Vertex Vector Search indexing
  - Implement `search_documents()` function with metadata filtering
  - Add error handling and retry logic for Vertex AI API calls
  - _Requirements: 2.5, 3.3_

- [x] 3. Implement Document AI processing pipeline
- [x] 3.1 Create Document AI OCR integration
  - Write `process_document()` function to handle PDF/DOCX OCR
  - Implement text extraction and metadata parsing from Document AI response
  - Add support for Chinese document layout detection
  - Create error handling for unsupported document formats
  - _Requirements: 2.2, 2.3_

- [x] 3.2 Implement document metadata extraction
  - Write functions to extract title, effective date, and classification from documents
  - Create province and asset type detection logic
  - Implement document checksum calculation for deduplication
  - Add validation for required metadata fields
  - _Requirements: 2.6, 3.4_

- [x] 4. Create Google Custom Search integration
- [x] 4.1 Implement document discovery module
  - Write `discover_documents()` function using Google CSE API
  - Create allowlist validation for government domains (.gov.cn)
  - Implement search query templates for different asset types and provinces
  - Add duplicate URL detection and filtering
  - _Requirements: 2.1_

- [x] 4.2 Create document fetching and storage
  - Implement secure document download with proper headers and timeouts
  - Write GCS upload functions for raw documents with metadata
  - Add file type validation and size limits
  - Create retry logic for failed downloads
  - _Requirements: 2.2_

- [x] 5. Implement ingestion Cloud Function
- [x] 5.1 Create main ingestion handler
  - Write `ingest_handler()` function with request validation and authentication
  - Implement end-to-end pipeline: discover → fetch → process → chunk → embed → index
  - Add comprehensive logging with trace IDs for each pipeline stage
  - Create error handling that continues processing on individual document failures
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 4.2, 4.3, 4.4_

- [x] 5.2 Add ingestion job scheduling and monitoring
  - Implement job status tracking and progress reporting
  - Create metrics collection for ingestion performance
  - Add validation for ingested document quality and completeness
  - Write cleanup logic for failed or incomplete ingestion runs
  - _Requirements: 4.5_

- [x] 6. Implement query processing pipeline
- [x] 6.1 Create query normalization and embedding
  - Write query preprocessing to handle Chinese text input
  - Implement query embedding using same model as documents
  - Add keyword extraction and query expansion logic
  - Create input validation for province, asset, and doc_class parameters
  - _Requirements: 1.3, 1.4_

- [x] 6.2 Implement response composition module
  - Write `compose_response()` function to format Chinese answers with verbatim quotes
  - Implement `extract_verbatim_quotes()` function to find relevant text spans
  - Create citation formatting with title, effective date, and source URL
  - Add response validation to ensure no mock data is included
  - _Requirements: 1.5, 1.6, 3.1, 3.4_

- [x] 6.3 Add optional Gemini reranking capability
  - Implement Gemini 1.5 Pro integration for result reranking
  - Create toggle mechanism to enable/disable reranking via environment variable
  - Add performance monitoring for reranking latency impact
  - Write fallback logic when reranking service is unavailable
  - _Requirements: 1.4_

- [x] 7. Implement query Cloud Function
- [x] 7.1 Create main query handler
  - Write `query_handler()` function with request parsing and validation
  - Implement complete query pipeline: embed → search → rerank → compose
  - Add comprehensive error handling with structured JSON responses
  - Create performance logging with stage-by-stage timing
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 3.1, 3.2, 3.3, 4.1, 4.2_

- [x] 7.2 Add query performance optimization
  - Implement response caching for identical queries (optional)
  - Add request deduplication to prevent concurrent identical queries
  - Create timeout handling with partial result fallbacks
  - Write performance metrics collection and monitoring
  - _Requirements: 1.4, 7.2_

- [x] 8. Implement health monitoring Cloud Function
- [x] 8.1 Create health check handler
  - Write `health_handler()` function returning system status, timestamp, commit hash
  - Implement Vertex AI service connectivity checks
  - Add GCS bucket accessibility validation
  - Create structured health response format
  - _Requirements: 4.1, 4.3_

- [x] 8.2 Add comprehensive system monitoring
  - Implement detailed logging for all function invocations with trace IDs
  - Create performance metrics collection for latency and error rates
  - Add alerting configuration for system health degradation
  - Write operational dashboards configuration for Cloud Logging
  - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5_

- [x] 9. Create deployment and infrastructure code
- [x] 9.1 Write Cloud Function deployment scripts
  - Create deployment scripts for all three functions with proper environment variables
  - Implement Secret Manager integration for API keys (Gemini, Perplexity CSE)
  - Add GCS bucket creation and configuration
  - Write Vertex AI Vector Search index setup and configuration
  - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6_

- [x] 9.2 Configure Cloud Scheduler for automated ingestion
  - Create Cloud Scheduler job for nightly ingestion runs
  - Implement proper service account permissions and authentication
  - Add job monitoring and failure notification setup
  - Write backup and recovery procedures for ingestion failures
  - _Requirements: 5.6_

- [x] 10. Implement comprehensive testing suite
- [x] 10.1 Create unit tests for all core modules
  - Write tests for text sanitization, chunking, and metadata extraction functions
  - Create tests for Vertex AI integration with mock responses
  - Implement tests for query processing and response composition
  - Add tests for error handling and edge cases
  - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5_

- [x] 10.2 Create integration tests with staging environment
  - Set up staging Vertex Vector Search index with test document corpus
  - Write end-to-end tests for ingestion pipeline with sample documents
  - Create integration tests for query pipeline with known queries and expected results
  - Implement performance tests to validate latency requirements
  - _Requirements: 7.2, 7.3_

- [x] 10.3 Implement golden set evaluation system
  - Create golden query dataset covering all province/asset combinations
  - Write automated evaluation scripts for precision and coverage metrics
  - Implement human evaluation workflow for citation accuracy
  - Add regression testing to detect quality degradation
  - _Requirements: 7.3, 7.4, 7.5_

- [x] 11. Create frontend interface
- [x] 11.1 Build basic query interface
  - Create HTML form with province dropdown (Guangdong, Shandong, Inner Mongolia)
  - Implement asset type selection buttons (Solar, Coal, Wind)
  - Add question input field with Chinese text support
  - Create language toggle between Chinese and English
  - _Requirements: 1.1, 1.2, 1.3_

- [x] 11.2 Implement results display and citation handling
  - Create results display showing Chinese bullets with verbatim quotes
  - Implement citation formatting with title, effective date, and clickable source links
  - Add trace ID display for debugging support
  - Create error message display for refusal cases
  - _Requirements: 1.5, 1.6, 3.1, 4.1_

- [x] 11.3 Add frontend performance and accessibility features
  - Implement responsive design for mobile and desktop
  - Add loading states and progress indicators
  - Create accessible Chinese font rendering and text sizing
  - Add keyboard navigation and screen reader support
  - _Requirements: 1.4_

- [x] 12. Final integration and deployment validation
- [x] 12.1 Perform end-to-end system validation
  - Test complete user workflow from query to citation display
  - Validate all API endpoints meet performance requirements (p95 < 2s)
  - Verify no mock data is present in any code path
  - Test error handling and recovery scenarios
  - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5_

- [x] 12.2 Complete production deployment and monitoring setup
  - Deploy all Cloud Functions to production environment
  - Configure production monitoring, alerting, and logging
  - Set up automated ingestion schedule and validate first run
  - Create operational runbooks and troubleshooting guides
  - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 5.1, 5.2, 5.3, 5.4, 5.5, 5.6_