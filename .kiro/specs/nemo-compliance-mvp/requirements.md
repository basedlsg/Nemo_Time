# Requirements Document

## Introduction

The Nemo Compliance MVP is a regulation-grade document retrieval system for Chinese energy projects (Solar, Coal, Wind) that provides verified, quote-first Chinese answers with perfect citations and effective dates. The system uses Google Cloud services exclusively to deliver reliable, deterministic responses from a curated corpus of government documents, eliminating the unreliability of live web searches at query time.

## Requirements

### Requirement 1

**User Story:** As a Chinese-speaking analyst/engineer at energy development companies, I want to select a province and ask questions about energy project regulations, so that I can receive verified regulatory information with exact citations.

#### Acceptance Criteria

1. WHEN a user selects a province from dropdown (Guangdong, Shandong, Inner Mongolia) THEN the system SHALL accept the province selection
2. WHEN a user selects an asset type (Solar, Coal, Wind) THEN the system SHALL filter results to that asset type
3. WHEN a user enters a question about energy project regulations THEN the system SHALL process the query in Chinese
4. WHEN a user submits a query THEN the system SHALL return results within 2 seconds (p95)
5. WHEN results are returned THEN the system SHALL display answers in Chinese with verbatim quotes only
6. WHEN results include citations THEN each citation SHALL include title, effective date in format 〔《标题》，生效：YYYY-MM-DD〕, and clickable source links to government portals

### Requirement 2

**User Story:** As a system administrator, I want an offline ingestion process that curates regulatory documents, so that query responses are deterministic and reliable without live web dependencies.

#### Acceptance Criteria

1. WHEN the ingestion process runs THEN the system SHALL discover documents only from allowlisted government domains (.gov.cn)
2. WHEN documents are discovered THEN the system SHALL fetch and store originals in GCS /raw/ with proper metadata
3. WHEN documents are processed THEN the system SHALL use Document AI for OCR and normalize to UTF-8
4. WHEN documents are chunked THEN the system SHALL create 800-token chunks with 100-token overlap
5. WHEN documents are indexed THEN the system SHALL embed using Vertex AI text-embedding-004
6. WHEN documents are stored THEN the system SHALL include metadata filters for province, asset, doc_class, effective_date, title, url, checksum

### Requirement 3

**User Story:** As a user querying the system, I want to receive only verified government documents with no mock data, so that I can trust the regulatory information for compliance decisions.

#### Acceptance Criteria

1. WHEN no relevant documents exist for a query THEN the system SHALL return an honest refusal message in Chinese
2. WHEN the system processes queries THEN it SHALL never return mock, demo, or fabricated data
3. WHEN documents are retrieved THEN they SHALL come only from the curated corpus, never from live web searches
4. WHEN citations are provided THEN they SHALL link only to original government portal sources
5. WHEN effective dates are shown THEN they SHALL be extracted from documents or left blank if unknown

### Requirement 4

**User Story:** As a developer maintaining the system, I want comprehensive logging and health monitoring, so that I can quickly diagnose and resolve issues.

#### Acceptance Criteria

1. WHEN any request is processed THEN the system SHALL generate a unique trace_id
2. WHEN errors occur THEN the system SHALL log structured error information with trace_id
3. WHEN the /health endpoint is called THEN it SHALL return system status, timestamp, commit hash, and region
4. WHEN query performance degrades THEN the system SHALL log stage timings for vector search and reranking
5. WHEN ingestion runs THEN the system SHALL log discovered URLs, parsing results, and indexing status

### Requirement 5

**User Story:** As a system operator, I want serverless Google Cloud deployment with no Docker dependencies, so that the system is easy to deploy and maintain.

#### Acceptance Criteria

1. WHEN deploying the system THEN it SHALL use only Google Cloud Functions (2nd gen) for compute
2. WHEN storing documents THEN it SHALL use Google Cloud Storage for raw and processed files
3. WHEN performing vector search THEN it SHALL use Vertex AI Vector Search managed service
4. WHEN processing documents THEN it SHALL use Document AI for OCR and text extraction
5. WHEN scheduling ingestion THEN it SHALL use Cloud Scheduler for nightly runs
6. WHEN the system is deployed THEN it SHALL require no Docker containers or custom infrastructure

### Requirement 6

**User Story:** As a compliance officer, I want the system to focus on grid connection regulations initially, so that we can validate the approach with the most critical regulatory area.

#### Acceptance Criteria

1. WHEN the MVP is deployed THEN it SHALL support only Grid Connection (并网) document class
2. WHEN users query the system THEN it SHALL filter results to grid connection regulations
3. WHEN documents are ingested THEN they SHALL be classified as grid connection related
4. WHEN the system expands THEN additional document classes can be added without architectural changes
5. WHEN queries are processed THEN they SHALL return grid connection specific regulatory guidance

### Requirement 7

**User Story:** As a quality assurance engineer, I want the system to meet specific accuracy and performance benchmarks, so that it delivers production-ready reliability.

#### Acceptance Criteria

1. WHEN testing with golden queries THEN the system SHALL achieve ≥90% precision with at least 1 correct citation
2. WHEN measuring response time THEN /query endpoint SHALL respond in <2.0s at p95 with rerank disabled
3. WHEN running stability tests THEN the system SHALL have 0 crash loops over 500 test queries
4. WHEN evaluating output quality THEN 100% of bullets SHALL be in Chinese with verbatim quotes
5. WHEN checking data integrity THEN the system SHALL contain 0% mock data verified by code scan