# Design Document: RAG-Anything Evaluation and Implementation

## Overview

This design outlines the evaluation and potential implementation of a RAG-Anything based system to replace the current Nemo Compliance MVP. The focus is on creating a simpler, more effective system that solves the deployment complexity and document retrieval accuracy issues of the current implementation.

### Key Design Goals

1. **Simplified Deployment**: Eliminate complex IAM permission chains and Cloud Build failures
2. **Enhanced Accuracy**: Improve document retrieval precision for Chinese regulatory content
3. **Perplexity Integration**: Leverage existing Perplexity capabilities for comprehensive results
4. **Operational Reliability**: Build a system that works consistently without infrastructure fights

## Architecture

### High-Level Architecture Comparison

#### Current System Issues
- Complex Google Cloud Functions deployment with IAM permission dependencies
- Vertex AI Vector Search requiring extensive setup and configuration
- Document AI integration with processing bottlenecks
- Multiple service dependencies creating failure points

#### RAG-Anything Approach
- **Simplified Infrastructure**: Container-based deployment with minimal dependencies
- **Unified Processing**: Single framework handling multimodal inputs (text, images, documents)
- **Flexible Backends**: Support for multiple vector stores and LLM providers
- **Built-in Optimizations**: Automatic chunking, embedding, and retrieval strategies

### System Components

#### 1. Document Processing Pipeline
```
Raw Documents → RAG-Anything Processor → Vector Store → Query Interface
                      ↓
              Perplexity Enhancement → Citation Validation → Response Composition
```

#### 2. Core Components

**RAG-Anything Engine**
- Handles document ingestion and processing
- Manages vector embeddings and storage
- Provides unified query interface
- Supports Chinese text processing natively

**Perplexity Integration Layer**
- Enhances document discovery
- Provides fallback for limited RAG results
- Validates and filters government sources
- Merges results with RAG outputs

**Simplified Deployment Layer**
- Docker-based containerization
- Standard Kubernetes or Cloud Run deployment
- Minimal IAM requirements
- Built-in health checks and monitoring

## Components and Interfaces

### 1. RAG-Anything Core Engine

**Purpose**: Central processing engine for document ingestion, embedding, and retrieval

**Key Features**:
- Multimodal document processing (PDF, images, text)
- Chinese language optimization
- Automatic chunking strategies
- Vector similarity search
- Built-in reranking capabilities

**Interface**:
```python
class RAGAnythingEngine:
    def ingest_documents(self, documents: List[Document]) -> bool
    def query(self, question: str, filters: Dict) -> QueryResult
    def get_similar_chunks(self, query: str, top_k: int) -> List[Chunk]
    def health_check() -> HealthStatus
```

### 2. Perplexity Enhancement Service

**Purpose**: Augment RAG results with Perplexity-powered discovery and validation

**Key Features**:
- Government domain filtering
- Citation validation
- Result merging and deduplication
- Fallback query processing

**Interface**:
```python
class PerplexityEnhancer:
    def discover_additional_sources(self, query: str, province: str, asset: str) -> List[Source]
    def validate_citations(self, citations: List[Citation]) -> List[ValidatedCitation]
    def merge_results(self, rag_results: QueryResult, perplexity_results: QueryResult) -> QueryResult
    def fallback_query(self, query: str, context: QueryContext) -> QueryResult
```

### 3. Deployment Manager

**Purpose**: Simplified deployment and configuration management

**Key Features**:
- One-command deployment
- Automatic dependency resolution
- Configuration validation
- Health monitoring

**Interface**:
```python
class DeploymentManager:
    def deploy(self, config: DeploymentConfig) -> DeploymentResult
    def validate_config(self, config: DeploymentConfig) -> ValidationResult
    def monitor_health(self) -> HealthMetrics
    def update_system(self, update_config: UpdateConfig) -> UpdateResult
```

## Data Models

### Document Model
```python
@dataclass
class Document:
    id: str
    title: str
    content: str
    province: str
    asset_type: str
    doc_class: str
    effective_date: Optional[datetime]
    source_url: str
    checksum: str
    metadata: Dict[str, Any]
```

### Query Context
```python
@dataclass
class QueryContext:
    question: str
    province: str
    asset_type: str
    doc_class: str
    language: str = "zh-CN"
    max_results: int = 10
    include_perplexity: bool = True
```

### Query Result
```python
@dataclass
class QueryResult:
    answer: str
    citations: List[Citation]
    confidence_score: float
    processing_time_ms: int
    source_breakdown: Dict[str, int]  # rag vs perplexity counts
    trace_id: str
```

### Citation Model
```python
@dataclass
class Citation:
    title: str
    url: str
    excerpt: str
    page_number: Optional[int]
    effective_date: Optional[datetime]
    confidence: float
    source_type: str  # "rag" or "perplexity"
```

## Error Handling

### Deployment Error Handling
- **Configuration Validation**: Pre-deployment config checks
- **Dependency Resolution**: Automatic handling of missing dependencies
- **Rollback Capability**: Automatic rollback on deployment failures
- **Clear Error Messages**: Actionable error descriptions with resolution steps

### Runtime Error Handling
- **Graceful Degradation**: System continues with reduced functionality
- **Circuit Breakers**: Prevent cascade failures
- **Retry Logic**: Intelligent retry with exponential backoff
- **Fallback Mechanisms**: Perplexity fallback when RAG fails

### Data Quality Error Handling
- **Document Validation**: Check document integrity before processing
- **Encoding Detection**: Automatic Chinese text encoding handling
- **OCR Error Recovery**: Handle corrupted or poorly scanned documents
- **Citation Validation**: Verify government domain sources

## Testing Strategy

### 1. Comparative Evaluation
**Objective**: Compare RAG-Anything effectiveness against current system

**Approach**:
- Use identical test queries from current system
- Measure retrieval accuracy, relevance, and response time
- Compare deployment complexity and operational overhead
- Evaluate Chinese language processing quality

**Metrics**:
- Precision@K for document retrieval
- Response time (p95 < 2 seconds target)
- Deployment time and complexity score
- Citation accuracy rate

### 2. Prototype Testing
**Objective**: Validate RAG-Anything with subset of regulatory documents

**Approach**:
- Process 100-200 representative documents
- Test with golden query set
- Measure Perplexity integration effectiveness
- Validate deployment simplicity

**Test Cases**:
- Grid connection permit queries
- Technical standard lookups
- Multi-province regulation comparisons
- Edge cases (no results, ambiguous queries)

### 3. Integration Testing
**Objective**: Ensure seamless integration with existing infrastructure

**Approach**:
- Test with existing GCS document storage
- Validate Perplexity API integration
- Test deployment on Google Cloud Platform
- Verify monitoring and logging integration

### 4. Performance Testing
**Objective**: Validate system performance under load

**Approach**:
- Load testing with concurrent queries
- Memory and CPU usage profiling
- Vector search performance benchmarking
- End-to-end response time measurement

## Implementation Phases

### Phase 1: Research and Setup (Week 1-2)
- Deep dive into RAG-Anything framework capabilities
- Set up development environment
- Analyze current system pain points in detail
- Create evaluation criteria and test datasets

### Phase 2: Prototype Development (Week 3-4)
- Implement basic RAG-Anything integration
- Process subset of existing documents
- Implement Perplexity enhancement layer
- Create simplified deployment scripts

### Phase 3: Comparative Evaluation (Week 5-6)
- Run side-by-side comparison tests
- Measure accuracy, performance, and complexity metrics
- Document findings and recommendations
- Identify migration challenges and solutions

### Phase 4: Production-Ready Implementation (Week 7-8)
- Full system implementation if evaluation is positive
- Production deployment configuration
- Monitoring and alerting setup
- Documentation and handover

## Risk Assessment and Mitigation

### Technical Risks
1. **RAG-Anything Framework Limitations**
   - Risk: Framework may not handle Chinese regulatory content effectively
   - Mitigation: Early prototype testing with representative documents

2. **Performance Degradation**
   - Risk: New system may be slower than current implementation
   - Mitigation: Performance benchmarking and optimization in prototype phase

3. **Integration Complexity**
   - Risk: Unexpected integration issues with existing infrastructure
   - Mitigation: Incremental integration testing and fallback plans

### Operational Risks
1. **Migration Complexity**
   - Risk: Data migration and system transition challenges
   - Mitigation: Phased migration approach with parallel running systems

2. **Learning Curve**
   - Risk: Team unfamiliarity with new framework
   - Mitigation: Comprehensive documentation and training materials

### Business Risks
1. **Accuracy Regression**
   - Risk: New system may be less accurate than current system
   - Mitigation: Rigorous comparative testing and quality gates

2. **Timeline Overrun**
   - Risk: Evaluation and implementation taking longer than expected
   - Mitigation: Clear milestones and go/no-go decision points

## Success Criteria

### Evaluation Success Criteria
- RAG-Anything demonstrates ≥10% improvement in retrieval accuracy
- Deployment complexity reduced by ≥50% (measured by setup steps and dependencies)
- Response time maintains p95 < 2 seconds target
- Chinese language processing quality matches or exceeds current system

### Implementation Success Criteria
- Zero-downtime migration from current system
- All existing functionality preserved or improved
- Operational overhead reduced by ≥30%
- Team confidence in maintaining and extending the system

## Recommendation Framework

### Go Criteria
- Accuracy improvements demonstrated
- Deployment simplification achieved
- Clear migration path identified
- Team buy-in and confidence established

### No-Go Criteria
- Accuracy regression observed
- Deployment complexity not significantly reduced
- Major technical blockers identified
- Migration risks outweigh benefits

### Conditional Go Criteria
- Mixed results requiring targeted improvements
- Partial migration strategy (hybrid approach)
- Extended evaluation period needed
- Alternative framework consideration required