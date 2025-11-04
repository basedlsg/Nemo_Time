"""
RAG-Anything Document Processing Pipeline
Handles Chinese regulatory document ingestion and processing
"""

import os
import asyncio
import hashlib
import json
from typing import Dict, Any, List, Optional
from pathlib import Path
from dataclasses import dataclass
from datetime import datetime

# RAG-Anything imports
from raganything import RAGAnything, RAGAnythingConfig

# Local imports for document handling
from .document_models import Document, DocumentMetadata, ProcessingResult
from .chinese_text_processor import ChineseTextProcessor
from .gcs_document_loader import GCSDocumentLoader


@dataclass
class DocumentProcessingConfig:
    """Configuration for document processing pipeline"""
    
    # RAG-Anything configuration
    working_dir: str = "./rag_storage"
    chunk_size: int = 800
    chunk_overlap: int = 100
    
    # Chinese text processing
    enable_chinese_optimization: bool = True
    min_chinese_ratio: float = 0.5
    
    # Document filtering
    min_document_length: int = 100
    max_document_length: int = 100000
    
    # Processing limits
    max_concurrent_documents: int = 3
    batch_size: int = 10


class DocumentProcessor:
    """
    Main document processing pipeline for RAG-Anything integration
    """
    
    def __init__(
        self,
        rag_anything: RAGAnything,
        config: Optional[DocumentProcessingConfig] = None
    ):
        self.rag_anything = rag_anything
        self.config = config or DocumentProcessingConfig()
        
        # Initialize components
        self.text_processor = ChineseTextProcessor()
        self.gcs_loader = GCSDocumentLoader()
        
        # Processing state
        self.processed_documents = {}
        self.processing_stats = {
            'total_processed': 0,
            'successful': 0,
            'failed': 0,
            'skipped': 0
        }
        
    async def process_document_from_gcs(
        self, 
        gcs_path: str,
        metadata: DocumentMetadata
    ) -> ProcessingResult:
        """
        Process a single document from GCS bucket
        
        Args:
            gcs_path: GCS path to the document
            metadata: Document metadata (province, asset, doc_class, etc.)
            
        Returns:
            ProcessingResult with success status and details
        """
        try:
            print(f"Processing document from GCS: {gcs_path}")
            
            # Load document from GCS
            document_data = await self.gcs_loader.load_document(gcs_path)
            if not document_data:
                return ProcessingResult(
                    success=False,
                    error="Failed to load document from GCS",
                    document_id=gcs_path
                )
            
            # Create document object
            document = Document(
                id=self._generate_document_id(gcs_path),
                title=document_data.get('title', ''),
                content=document_data.get('text', ''),
                metadata=metadata,
                source_url=document_data.get('url', ''),
                checksum=document_data.get('checksum', ''),
                raw_content=document_data
            )
            
            # Process the document
            return await self.process_document(document)
            
        except Exception as e:
            print(f"Error processing document from GCS {gcs_path}: {str(e)}")
            return ProcessingResult(
                success=False,
                error=str(e),
                document_id=gcs_path
            )
    
    async def process_document(self, document: Document) -> ProcessingResult:
        """
        Process a single document through the RAG-Anything pipeline
        
        Args:
            document: Document object to process
            
        Returns:
            ProcessingResult with success status and details
        """
        try:
            # Validate document
            validation_result = self._validate_document(document)
            if not validation_result.is_valid:
                return ProcessingResult(
                    success=False,
                    error=f"Document validation failed: {validation_result.error}",
                    document_id=document.id
                )
            
            # Check if already processed
            if document.checksum in self.processed_documents:
                print(f"Document already processed: {document.id}")
                return ProcessingResult(
                    success=True,
                    document_id=document.id,
                    message="Document already processed (duplicate)"
                )
            
            # Process Chinese text
            processed_content = self.text_processor.process_text(
                document.content,
                document.metadata
            )
            
            if not processed_content:
                return ProcessingResult(
                    success=False,
                    error="Text processing failed - no valid content",
                    document_id=document.id
                )
            
            # Create chunks optimized for Chinese regulatory content
            chunks = self._create_regulatory_chunks(
                processed_content,
                document.metadata
            )
            
            if not chunks:
                return ProcessingResult(
                    success=False,
                    error="No valid chunks created",
                    document_id=document.id
                )
            
            # Insert into RAG-Anything
            insertion_result = await self._insert_document_chunks(
                document,
                chunks
            )
            
            if insertion_result:
                # Track successful processing
                self.processed_documents[document.checksum] = {
                    'document_id': document.id,
                    'processed_at': datetime.utcnow().isoformat(),
                    'chunk_count': len(chunks),
                    'metadata': document.metadata.__dict__
                }
                
                self.processing_stats['successful'] += 1
                
                return ProcessingResult(
                    success=True,
                    document_id=document.id,
                    chunk_count=len(chunks),
                    message=f"Successfully processed {len(chunks)} chunks"
                )
            else:
                return ProcessingResult(
                    success=False,
                    error="Failed to insert chunks into RAG system",
                    document_id=document.id
                )
                
        except Exception as e:
            print(f"Error processing document {document.id}: {str(e)}")
            self.processing_stats['failed'] += 1
            return ProcessingResult(
                success=False,
                error=str(e),
                document_id=document.id
            )
        finally:
            self.processing_stats['total_processed'] += 1
    
    async def process_document_batch(
        self,
        documents: List[Document]
    ) -> List[ProcessingResult]:
        """
        Process multiple documents concurrently
        
        Args:
            documents: List of documents to process
            
        Returns:
            List of ProcessingResults
        """
        print(f"Processing batch of {len(documents)} documents")
        
        # Process in batches to avoid overwhelming the system
        results = []
        
        for i in range(0, len(documents), self.config.batch_size):
            batch = documents[i:i + self.config.batch_size]
            
            # Process batch concurrently with limited concurrency
            semaphore = asyncio.Semaphore(self.config.max_concurrent_documents)
            
            async def process_with_semaphore(doc):
                async with semaphore:
                    return await self.process_document(doc)
            
            batch_results = await asyncio.gather(
                *[process_with_semaphore(doc) for doc in batch],
                return_exceptions=True
            )
            
            # Handle any exceptions
            for j, result in enumerate(batch_results):
                if isinstance(result, Exception):
                    results.append(ProcessingResult(
                        success=False,
                        error=str(result),
                        document_id=batch[j].id
                    ))
                else:
                    results.append(result)
        
        return results
    
    def _validate_document(self, document: Document) -> 'ValidationResult':
        """Validate document before processing"""
        
        # Check content length
        if len(document.content) < self.config.min_document_length:
            return ValidationResult(
                is_valid=False,
                error=f"Document too short: {len(document.content)} chars"
            )
        
        if len(document.content) > self.config.max_document_length:
            return ValidationResult(
                is_valid=False,
                error=f"Document too long: {len(document.content)} chars"
            )
        
        # Check Chinese content ratio if enabled
        if self.config.enable_chinese_optimization:
            chinese_ratio = self._calculate_chinese_ratio(document.content)
            if chinese_ratio < self.config.min_chinese_ratio:
                return ValidationResult(
                    is_valid=False,
                    error=f"Insufficient Chinese content: {chinese_ratio:.2f}"
                )
        
        # Check required metadata
        if not document.metadata.province:
            return ValidationResult(
                is_valid=False,
                error="Missing province in metadata"
            )
        
        return ValidationResult(is_valid=True)
    
    def _calculate_chinese_ratio(self, text: str) -> float:
        """Calculate ratio of Chinese characters in text"""
        if not text:
            return 0.0
        
        chinese_chars = sum(1 for char in text if '\u4e00' <= char <= '\u9fff')
        total_chars = len([c for c in text if c.strip()])
        
        return chinese_chars / total_chars if total_chars > 0 else 0.0
    
    def _create_regulatory_chunks(
        self,
        content: str,
        metadata: DocumentMetadata
    ) -> List[Dict[str, Any]]:
        """
        Create chunks optimized for Chinese regulatory content
        """
        # Use Chinese-aware sentence splitting
        sentences = self.text_processor.split_into_sentences(content)
        
        chunks = []
        current_chunk = ""
        current_length = 0
        
        # Estimate target characters (Chinese chars ≈ 1.5 tokens)
        target_chars = int(self.config.chunk_size / 1.5)
        overlap_chars = int(self.config.chunk_overlap / 1.5)
        
        for sentence in sentences:
            sentence_length = len(sentence)
            
            # Check if we should finalize current chunk
            if current_length + sentence_length > target_chars and current_chunk:
                # Create chunk with regulatory metadata
                chunk = self._create_chunk_dict(
                    text=current_chunk.strip(),
                    metadata=metadata,
                    chunk_index=len(chunks)
                )
                chunks.append(chunk)
                
                # Start new chunk with overlap
                overlap_text = self._get_overlap_text(current_chunk, overlap_chars)
                current_chunk = overlap_text + sentence
                current_length = len(current_chunk)
            else:
                current_chunk += sentence
                current_length += sentence_length
        
        # Add final chunk
        if current_chunk.strip():
            chunk = self._create_chunk_dict(
                text=current_chunk.strip(),
                metadata=metadata,
                chunk_index=len(chunks)
            )
            chunks.append(chunk)
        
        # Filter out invalid chunks
        valid_chunks = [
            chunk for chunk in chunks
            if self._is_valid_chunk(chunk['text'])
        ]
        
        print(f"Created {len(valid_chunks)} valid chunks from {len(chunks)} total")
        return valid_chunks
    
    def _create_chunk_dict(
        self,
        text: str,
        metadata: DocumentMetadata,
        chunk_index: int
    ) -> Dict[str, Any]:
        """Create chunk dictionary with regulatory metadata"""
        return {
            'text': text,
            'chunk_index': chunk_index,
            'metadata': {
                'province': metadata.province,
                'asset_type': metadata.asset_type,
                'doc_class': metadata.doc_class,
                'effective_date': metadata.effective_date,
                'title': metadata.title,
                'language': 'zh-CN',
                'content_type': 'regulatory_text'
            }
        }
    
    def _get_overlap_text(self, text: str, overlap_chars: int) -> str:
        """Get overlap text with sentence boundary awareness"""
        if len(text) <= overlap_chars:
            return text
        
        overlap_text = text[-overlap_chars:]
        
        # Find sentence boundary in overlap
        sentence_endings = ['。', '！', '？', '；']
        for ending in sentence_endings:
            pos = overlap_text.rfind(ending)
            if pos > 0:
                return overlap_text[pos + 1:]
        
        return overlap_text
    
    def _is_valid_chunk(self, text: str) -> bool:
        """Validate chunk quality"""
        # Minimum length check
        if len(text) < 50:
            return False
        
        # Maximum length check
        if len(text) > 2000:
            return False
        
        # Chinese content check
        if self.config.enable_chinese_optimization:
            chinese_ratio = self._calculate_chinese_ratio(text)
            if chinese_ratio < self.config.min_chinese_ratio:
                return False
        
        return True
    
    async def _insert_document_chunks(
        self,
        document: Document,
        chunks: List[Dict[str, Any]]
    ) -> bool:
        """Insert document chunks into RAG-Anything system"""
        try:
            # Prepare text content for insertion
            full_text = document.content
            
            # Add document to RAG-Anything
            # Note: RAG-Anything handles chunking internally, but we can provide
            # our pre-processed content with metadata
            await self.rag_anything.ainsert(full_text)
            
            print(f"Successfully inserted document {document.id} into RAG system")
            return True
            
        except Exception as e:
            print(f"Error inserting document chunks: {str(e)}")
            return False
    
    def _generate_document_id(self, source: str) -> str:
        """Generate unique document ID"""
        return hashlib.md5(source.encode()).hexdigest()[:12]
    
    def get_processing_stats(self) -> Dict[str, Any]:
        """Get processing statistics"""
        return {
            **self.processing_stats,
            'processed_documents': len(self.processed_documents),
            'success_rate': (
                self.processing_stats['successful'] / 
                max(1, self.processing_stats['total_processed'])
            )
        }


@dataclass
class ValidationResult:
    """Result of document validation"""
    is_valid: bool
    error: Optional[str] = None