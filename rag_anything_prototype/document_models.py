"""
Document models for RAG-Anything integration
Defines data structures for Chinese regulatory documents
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List
from datetime import datetime


@dataclass
class DocumentMetadata:
    """Metadata for Chinese regulatory documents"""
    
    # Core classification
    province: str  # gd, sd, nm
    asset_type: str  # solar, coal, wind
    doc_class: str  # grid, permit, technical, etc.
    
    # Document information
    title: Optional[str] = None
    effective_date: Optional[str] = None
    doc_type: Optional[str] = None
    language: str = "zh-CN"
    
    # Processing metadata
    ingested_at: Optional[str] = None
    processed_at: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage"""
        return {
            'province': self.province,
            'asset_type': self.asset_type,
            'doc_class': self.doc_class,
            'title': self.title,
            'effective_date': self.effective_date,
            'doc_type': self.doc_type,
            'language': self.language,
            'ingested_at': self.ingested_at,
            'processed_at': self.processed_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DocumentMetadata':
        """Create from dictionary"""
        return cls(
            province=data['province'],
            asset_type=data['asset_type'],
            doc_class=data['doc_class'],
            title=data.get('title'),
            effective_date=data.get('effective_date'),
            doc_type=data.get('doc_type'),
            language=data.get('language', 'zh-CN'),
            ingested_at=data.get('ingested_at'),
            processed_at=data.get('processed_at')
        )


@dataclass
class Document:
    """Document representation for processing"""
    
    id: str
    title: str
    content: str
    metadata: DocumentMetadata
    
    # Source information
    source_url: Optional[str] = None
    checksum: Optional[str] = None
    
    # Raw data for reference
    raw_content: Optional[Dict[str, Any]] = None
    
    # Processing state
    processed: bool = False
    processing_error: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage"""
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'metadata': self.metadata.to_dict(),
            'source_url': self.source_url,
            'checksum': self.checksum,
            'processed': self.processed,
            'processing_error': self.processing_error
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Document':
        """Create from dictionary"""
        return cls(
            id=data['id'],
            title=data['title'],
            content=data['content'],
            metadata=DocumentMetadata.from_dict(data['metadata']),
            source_url=data.get('source_url'),
            checksum=data.get('checksum'),
            processed=data.get('processed', False),
            processing_error=data.get('processing_error')
        )


@dataclass
class ProcessingResult:
    """Result of document processing operation"""
    
    success: bool
    document_id: str
    
    # Success details
    chunk_count: Optional[int] = None
    processing_time_ms: Optional[int] = None
    message: Optional[str] = None
    
    # Error details
    error: Optional[str] = None
    error_code: Optional[str] = None
    
    # Metadata
    processed_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'success': self.success,
            'document_id': self.document_id,
            'chunk_count': self.chunk_count,
            'processing_time_ms': self.processing_time_ms,
            'message': self.message,
            'error': self.error,
            'error_code': self.error_code,
            'processed_at': self.processed_at
        }


@dataclass
class QueryContext:
    """Context for regulatory document queries"""
    
    question: str
    
    # Filtering criteria
    province: Optional[str] = None
    asset_type: Optional[str] = None
    doc_class: Optional[str] = None
    
    # Query parameters
    max_results: int = 10
    include_perplexity: bool = True
    language: str = "zh-CN"
    
    # Processing options
    enable_reranking: bool = True
    confidence_threshold: float = 0.5
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'question': self.question,
            'province': self.province,
            'asset_type': self.asset_type,
            'doc_class': self.doc_class,
            'max_results': self.max_results,
            'include_perplexity': self.include_perplexity,
            'language': self.language,
            'enable_reranking': self.enable_reranking,
            'confidence_threshold': self.confidence_threshold
        }


@dataclass
class Citation:
    """Citation from regulatory document"""
    
    title: str
    url: str
    excerpt: str
    
    # Document metadata
    province: Optional[str] = None
    asset_type: Optional[str] = None
    doc_class: Optional[str] = None
    effective_date: Optional[str] = None
    
    # Relevance information
    confidence_score: float = 0.0
    page_number: Optional[int] = None
    section: Optional[str] = None
    
    # Source information
    source_type: str = "rag"  # "rag" or "perplexity"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'title': self.title,
            'url': self.url,
            'excerpt': self.excerpt,
            'province': self.province,
            'asset_type': self.asset_type,
            'doc_class': self.doc_class,
            'effective_date': self.effective_date,
            'confidence_score': self.confidence_score,
            'page_number': self.page_number,
            'section': self.section,
            'source_type': self.source_type
        }


@dataclass
class QueryResult:
    """Result of regulatory document query"""
    
    answer: str
    citations: List[Citation]
    
    # Query information
    query_context: QueryContext
    confidence_score: float = 0.0
    
    # Performance metrics
    processing_time_ms: int = 0
    total_documents_searched: int = 0
    
    # Source breakdown
    rag_citations: int = 0
    perplexity_citations: int = 0
    
    # Processing metadata
    trace_id: Optional[str] = None
    processed_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'answer': self.answer,
            'citations': [citation.to_dict() for citation in self.citations],
            'query_context': self.query_context.to_dict(),
            'confidence_score': self.confidence_score,
            'processing_time_ms': self.processing_time_ms,
            'total_documents_searched': self.total_documents_searched,
            'rag_citations': self.rag_citations,
            'perplexity_citations': self.perplexity_citations,
            'trace_id': self.trace_id,
            'processed_at': self.processed_at
        }


@dataclass
class BatchProcessingStatus:
    """Status of batch document processing"""
    
    total_documents: int
    processed: int
    successful: int
    failed: int
    skipped: int
    
    # Current processing
    current_document: Optional[str] = None
    
    # Timing
    started_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    estimated_completion: Optional[str] = None
    
    # Error tracking
    recent_errors: List[str] = field(default_factory=list)
    
    @property
    def progress_percentage(self) -> float:
        """Calculate progress percentage"""
        if self.total_documents == 0:
            return 0.0
        return (self.processed / self.total_documents) * 100
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate"""
        if self.processed == 0:
            return 0.0
        return (self.successful / self.processed) * 100
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'total_documents': self.total_documents,
            'processed': self.processed,
            'successful': self.successful,
            'failed': self.failed,
            'skipped': self.skipped,
            'current_document': self.current_document,
            'started_at': self.started_at,
            'estimated_completion': self.estimated_completion,
            'progress_percentage': self.progress_percentage,
            'success_rate': self.success_rate,
            'recent_errors': self.recent_errors[-5:]  # Last 5 errors
        }