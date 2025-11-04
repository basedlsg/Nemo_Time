"""
RAG-Anything Document Processing Pipeline
Main pipeline for processing Chinese regulatory documents
"""

import asyncio
import os
from typing import Dict, Any, List, Optional
from pathlib import Path
from datetime import datetime

# Local imports
from .document_processor import DocumentProcessor, DocumentProcessingConfig
from .document_models import Document, DocumentMetadata, ProcessingResult, BatchProcessingStatus
from .rag_config import RAGAnythingSetup
from .gcs_document_loader import GCSDocumentLoader


class RAGAnythingPipeline:
    """
    Complete pipeline for processing Chinese regulatory documents with RAG-Anything
    """
    
    def __init__(
        self,
        working_dir: str = "./rag_storage",
        config_overrides: Optional[Dict[str, Any]] = None
    ):
        self.working_dir = working_dir
        self.config_overrides = config_overrides or {}
        
        # Components
        self.rag_setup = None
        self.rag_anything = None
        self.document_processor = None
        self.gcs_loader = GCSDocumentLoader()
        
        # Processing state
        self.is_initialized = False
        self.processing_status = None
        
    async def initialize(
        self,
        llm_provider: str = "openai",
        embedding_provider: str = "openai"
    ) -> bool:
        """
        Initialize the complete pipeline
        
        Args:
            llm_provider: LLM provider to use
            embedding_provider: Embedding provider to use
            
        Returns:
            True if initialization successful
        """
        try:
            print("Initializing RAG-Anything pipeline...")
            
            # Create working directory
            Path(self.working_dir).mkdir(parents=True, exist_ok=True)
            
            # Initialize RAG system
            self.rag_setup = RAGAnythingSetup(self.config_overrides)
            self.rag_anything = await self.rag_setup.initialize_rag_system(
                working_dir=self.working_dir,
                llm_provider=llm_provider,
                embedding_provider=embedding_provider
            )
            
            # Initialize document processor
            processing_config = DocumentProcessingConfig(
                working_dir=self.working_dir,
                **self.config_overrides.get('processing', {})
            )
            
            self.document_processor = DocumentProcessor(
                rag_anything=self.rag_anything,
                config=processing_config
            )
            
            # Test system functionality
            test_result = await self.rag_setup.test_system_functionality()
            if not test_result.get('success', False):
                raise Exception(f"System test failed: {test_result.get('error')}")
            
            self.is_initialized = True
            print("Pipeline initialization completed successfully")
            return True
            
        except Exception as e:
            print(f"Error initializing pipeline: {str(e)}")
            return False
    
    async def process_documents_from_gcs(
        self,
        bucket_name: str,
        province: Optional[str] = None,
        asset_type: Optional[str] = None,
        doc_class: Optional[str] = None,
        max_documents: Optional[int] = None
    ) -> BatchProcessingStatus:
        """
        Process documents from GCS bucket
        
        Args:
            bucket_name: GCS bucket name
            province: Filter by province (gd, sd, nm)
            asset_type: Filter by asset type (solar, coal, wind)
            doc_class: Filter by document class (grid, permit, etc.)
            max_documents: Maximum number of documents to process
            
        Returns:
            BatchProcessingStatus with results
        """
        if not self.is_initialized:
            raise RuntimeError("Pipeline not initialized. Call initialize() first.")
        
        try:
            print(f"Loading documents from GCS bucket: {bucket_name}")
            
            # Load documents from GCS
            documents_data = await self.gcs_loader.load_documents_by_criteria(
                bucket_name=bucket_name,
                province=province,
                asset_type=asset_type,
                doc_class=doc_class
            )
            
            if not documents_data:
                print("No documents found matching criteria")
                return BatchProcessingStatus(
                    total_documents=0,
                    processed=0,
                    successful=0,
                    failed=0,
                    skipped=0
                )
            
            # Limit documents if specified
            if max_documents:
                documents_data = documents_data[:max_documents]
            
            print(f"Found {len(documents_data)} documents to process")
            
            # Convert to Document objects
            documents = []
            for doc_data in documents_data:
                try:
                    metadata = DocumentMetadata(
                        province=doc_data.get('province', province or 'unknown'),
                        asset_type=doc_data.get('asset', asset_type or 'unknown'),
                        doc_class=doc_data.get('doc_class', doc_class or 'unknown'),
                        title=doc_data.get('title'),
                        effective_date=doc_data.get('effective_date'),
                        doc_type=doc_data.get('doc_type'),
                        ingested_at=doc_data.get('ingested_at')
                    )
                    
                    document = Document(
                        id=doc_data.get('checksum', f"doc_{len(documents)}"),
                        title=doc_data.get('title', 'Untitled Document'),
                        content=doc_data.get('text', ''),
                        metadata=metadata,
                        source_url=doc_data.get('url'),
                        checksum=doc_data.get('checksum'),
                        raw_content=doc_data
                    )
                    
                    documents.append(document)
                    
                except Exception as e:
                    print(f"Error creating document object: {str(e)}")
                    continue
            
            # Initialize processing status
            self.processing_status = BatchProcessingStatus(
                total_documents=len(documents),
                processed=0,
                successful=0,
                failed=0,
                skipped=0
            )
            
            # Process documents
            results = await self.document_processor.process_document_batch(documents)
            
            # Update status based on results
            for result in results:
                if result.success:
                    self.processing_status.successful += 1
                else:
                    self.processing_status.failed += 1
                    if result.error:
                        self.processing_status.recent_errors.append(result.error)
                
                self.processing_status.processed += 1
            
            print(f"Batch processing completed: {self.processing_status.successful}/{len(documents)} successful")
            return self.processing_status
            
        except Exception as e:
            print(f"Error processing documents from GCS: {str(e)}")
            if self.processing_status:
                self.processing_status.recent_errors.append(str(e))
            raise
    
    async def process_single_document(
        self,
        gcs_path: str,
        province: str,
        asset_type: str,
        doc_class: str
    ) -> ProcessingResult:
        """
        Process a single document from GCS
        
        Args:
            gcs_path: GCS path to document
            province: Province code
            asset_type: Asset type
            doc_class: Document class
            
        Returns:
            ProcessingResult
        """
        if not self.is_initialized:
            raise RuntimeError("Pipeline not initialized. Call initialize() first.")
        
        metadata = DocumentMetadata(
            province=province,
            asset_type=asset_type,
            doc_class=doc_class
        )
        
        return await self.document_processor.process_document_from_gcs(
            gcs_path=gcs_path,
            metadata=metadata
        )
    
    async def query_documents(
        self,
        question: str,
        province: Optional[str] = None,
        asset_type: Optional[str] = None,
        doc_class: Optional[str] = None,
        max_results: int = 10
    ) -> str:
        """
        Query the processed documents
        
        Args:
            question: Question to ask
            province: Filter by province
            asset_type: Filter by asset type
            doc_class: Filter by document class
            max_results: Maximum number of results
            
        Returns:
            Query response
        """
        if not self.is_initialized:
            raise RuntimeError("Pipeline not initialized. Call initialize() first.")
        
        try:
            # For now, use basic RAG-Anything query
            # TODO: Implement filtering by metadata
            result = await self.rag_anything.aquery(question)
            return result
            
        except Exception as e:
            print(f"Error querying documents: {str(e)}")
            return f"Error processing query: {str(e)}"
    
    async def get_pipeline_status(self) -> Dict[str, Any]:
        """Get current pipeline status and statistics"""
        
        status = {
            "initialized": self.is_initialized,
            "working_directory": self.working_dir
        }
        
        if self.rag_setup:
            system_info = await self.rag_setup.get_system_info()
            status["rag_system"] = system_info
        
        if self.document_processor:
            processing_stats = self.document_processor.get_processing_stats()
            status["processing_stats"] = processing_stats
        
        if self.processing_status:
            status["current_batch"] = self.processing_status.to_dict()
        
        return status
    
    async def cleanup(self):
        """Clean up pipeline resources"""
        try:
            if self.rag_setup:
                await self.rag_setup.cleanup()
            
            print("Pipeline cleanup completed")
            
        except Exception as e:
            print(f"Error during pipeline cleanup: {str(e)}")


# Convenience functions for quick setup

async def create_pipeline(
    working_dir: str = "./rag_storage",
    llm_provider: str = "openai",
    embedding_provider: str = "openai",
    config_overrides: Optional[Dict[str, Any]] = None
) -> RAGAnythingPipeline:
    """
    Create and initialize a RAG-Anything pipeline
    
    Args:
        working_dir: Working directory for storage
        llm_provider: LLM provider
        embedding_provider: Embedding provider
        config_overrides: Configuration overrides
        
    Returns:
        Initialized RAGAnythingPipeline
    """
    pipeline = RAGAnythingPipeline(
        working_dir=working_dir,
        config_overrides=config_overrides
    )
    
    success = await pipeline.initialize(
        llm_provider=llm_provider,
        embedding_provider=embedding_provider
    )
    
    if not success:
        raise RuntimeError("Failed to initialize pipeline")
    
    return pipeline


async def quick_process_gcs_documents(
    bucket_name: str,
    province: Optional[str] = None,
    asset_type: Optional[str] = None,
    doc_class: Optional[str] = None,
    max_documents: Optional[int] = None,
    working_dir: str = "./rag_storage"
) -> BatchProcessingStatus:
    """
    Quick function to process documents from GCS
    
    Args:
        bucket_name: GCS bucket name
        province: Province filter
        asset_type: Asset type filter
        doc_class: Document class filter
        max_documents: Maximum documents to process
        working_dir: Working directory
        
    Returns:
        BatchProcessingStatus
    """
    pipeline = await create_pipeline(working_dir=working_dir)
    
    try:
        return await pipeline.process_documents_from_gcs(
            bucket_name=bucket_name,
            province=province,
            asset_type=asset_type,
            doc_class=doc_class,
            max_documents=max_documents
        )
    finally:
        await pipeline.cleanup()