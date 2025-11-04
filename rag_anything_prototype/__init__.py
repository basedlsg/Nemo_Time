"""
RAG-Anything Prototype for Chinese Regulatory Documents
Document processing pipeline using RAG-Anything framework
"""

from .pipeline import RAGAnythingPipeline, create_pipeline, quick_process_gcs_documents
from .document_processor import DocumentProcessor, DocumentProcessingConfig
from .document_models import (
    Document, 
    DocumentMetadata, 
    ProcessingResult, 
    QueryContext, 
    QueryResult, 
    Citation,
    BatchProcessingStatus
)
from .rag_config import RAGAnythingSetup, create_default_rag_setup, quick_setup_rag_system
from .chinese_text_processor import ChineseTextProcessor
from .gcs_document_loader import GCSDocumentLoader
from .model_functions import (
    create_llm_model_func,
    create_embedding_func,
    create_vision_model_func,
    get_available_providers,
    validate_model_configuration
)

__version__ = "0.1.0"
__author__ = "RAG-Anything Evaluation Team"

# Main exports for easy import
__all__ = [
    # Main pipeline
    "RAGAnythingPipeline",
    "create_pipeline",
    "quick_process_gcs_documents",
    
    # Document processing
    "DocumentProcessor",
    "DocumentProcessingConfig",
    
    # Data models
    "Document",
    "DocumentMetadata", 
    "ProcessingResult",
    "QueryContext",
    "QueryResult",
    "Citation",
    "BatchProcessingStatus",
    
    # RAG system setup
    "RAGAnythingSetup",
    "create_default_rag_setup",
    "quick_setup_rag_system",
    
    # Text processing
    "ChineseTextProcessor",
    
    # Document loading
    "GCSDocumentLoader",
    
    # Model functions
    "create_llm_model_func",
    "create_embedding_func", 
    "create_vision_model_func",
    "get_available_providers",
    "validate_model_configuration"
]