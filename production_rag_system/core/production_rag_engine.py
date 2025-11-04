"""
Production RAG-Anything Engine
Core production implementation with monitoring, backup, and recovery
"""

import asyncio
import logging
import time
from typing import Dict, Any, List, Optional
from pathlib import Path
from datetime import datetime
import json

# RAG-Anything imports
from raganything import RAGAnything, RAGAnythingConfig

# Local imports
from ..config.production_config import ProductionConfig, RAGAnythingProductionConfig


class ProductionRAGEngine:
    """
    Production-ready RAG-Anything engine with full monitoring and operational features
    """
    
    def __init__(self, config: ProductionConfig):
        self.config = config
        self.rag_config = RAGAnythingProductionConfig()
        
        # Core components
        self.rag_anything = None
        
        # State tracking
        self.is_initialized = False
        self.initialization_time = None
        self.last_health_check = None
        
        # Setup logging
        self._setup_logging()
        
    def _setup_logging(self):
        """Setup production logging"""
        logging.basicConfig(
            level=getattr(logging, self.config.log_level),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler(f"{self.config.working_dir}/logs/rag_engine.log")
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    async def initialize(self) -> bool:
        """
        Initialize the production RAG system
        
        Returns:
            True if initialization successful
        """
        start_time = time.time()
        
        try:
            self.logger.info("Initializing production RAG-Anything system...")
            
            # Create working directories
            self._create_directories()
            
            # Create RAG-Anything configuration
            rag_config = self._create_rag_config()
            
            # Create model functions
            llm_model_func = self._create_llm_model_func()
            embedding_func = self._create_embedding_func()
            vision_model_func = self._create_vision_model_func()
            
            # Create LightRAG kwargs
            lightrag_kwargs = self.rag_config.to_lightrag_kwargs(self.config)
            
            # Initialize RAG-Anything
            self.rag_anything = RAGAnything(
                config=rag_config,
                llm_model_func=llm_model_func,
                embedding_func=embedding_func,
                vision_model_func=vision_model_func,
                lightrag_kwargs=lightrag_kwargs
            )
            
            # Initialize the system
            init_result = await self.rag_anything._ensure_lightrag_initialized()
            
            if not init_result.get('success', False):
                raise Exception(f"Failed to initialize RAG system: {init_result.get('error')}")
            
            # Test system functionality
            test_result = await self._test_system_functionality()
            if not test_result['success']:
                raise Exception(f"System test failed: {test_result['error']}")
            
            self.is_initialized = True
            self.initialization_time = datetime.utcnow()
            
            initialization_duration = time.time() - start_time
            self.logger.info(f"RAG system initialized successfully in {initialization_duration:.2f}s")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error initializing RAG system: {str(e)}")
            return False
    
    def _create_directories(self):
        """Create necessary production directories"""
        directories = [
            self.config.working_dir,
            f"{self.config.working_dir}/parsed",
            f"{self.config.working_dir}/logs",
            f"{self.config.working_dir}/backups",
            f"{self.config.working_dir}/temp",
            f"{self.config.working_dir}/metrics"
        ]
        
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
    
    def _create_rag_config(self) -> RAGAnythingConfig:
        """Create production RAG-Anything configuration"""
        return RAGAnythingConfig(
            working_dir=self.config.working_dir,
            parser_output_dir=f"{self.config.working_dir}/parsed",
            parser=self.config.parser_type,
            parse_method="auto",
            enable_image_processing=self.rag_config.enable_image_processing,
            enable_table_processing=self.rag_config.enable_table_processing,
            enable_equation_processing=self.rag_config.enable_equation_processing,
            context_window=self.rag_config.context_window,
            context_mode=self.rag_config.context_mode,
            max_context_tokens=self.rag_config.max_context_tokens,
            include_headers=self.rag_config.include_headers,
            include_captions=self.rag_config.include_captions,
            max_concurrent_files=self.config.max_concurrent_files,
            recursive_folder_processing=True,
            content_format=self.rag_config.content_format,
            display_content_stats=True
        )
    
    def _create_llm_model_func(self):
        """Create LLM model function based on provider"""
        # Import model functions from prototype
        from rag_anything_prototype.model_functions import create_llm_model_func
        return create_llm_model_func(self.config.llm_provider)
    
    def _create_embedding_func(self):
        """Create embedding function based on provider"""
        from rag_anything_prototype.model_functions import create_embedding_func
        return create_embedding_func(self.config.embedding_provider)
    
    def _create_vision_model_func(self):
        """Create vision model function based on provider"""
        from rag_anything_prototype.model_functions import create_vision_model_func
        return create_vision_model_func(self.config.llm_provider)
    
    async def _test_system_functionality(self) -> Dict[str, Any]:
        """Test basic functionality of the RAG system"""
        try:
            # Test document insertion
            test_text = """
            第一条 为规范分布式光伏发电项目管理，促进分布式光伏发电健康有序发展，
            根据《可再生能源法》、《电力法》等法律法规，结合本省实际，制定本办法。
            """
            
            await self.rag_anything.ainsert(test_text)
            
            # Test query
            test_query = "分布式光伏发电项目如何管理？"
            result = await self.rag_anything.aquery(test_query)
            
            return {
                "success": True,
                "test_insertion": "completed",
                "test_query": test_query,
                "query_result_length": len(result) if result else 0
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def process_document_corpus(self, bucket_name: str, max_documents: Optional[int] = None) -> Dict[str, Any]:
        """
        Process full document corpus for production
        
        Args:
            bucket_name: GCS bucket containing documents
            max_documents: Maximum number of documents to process
            
        Returns:
            Processing results
        """
        if not self.is_initialized:
            raise RuntimeError("RAG engine not initialized")
        
        start_time = time.time()
        
        try:
            self.logger.info(f"Starting document corpus processing from bucket: {bucket_name}")
            
            # Use existing GCS loader from prototype
            from rag_anything_prototype.gcs_document_loader import GCSDocumentLoader
            gcs_loader = GCSDocumentLoader()
            
            # Load all documents
            documents_data = await gcs_loader.load_all_documents(bucket_name)
            
            if max_documents:
                documents_data = documents_data[:max_documents]
            
            total_documents = len(documents_data)
            processed = 0
            successful = 0
            failed = 0
            
            self.logger.info(f"Processing {total_documents} documents")
            
            # Process documents in batches
            batch_size = self.config.max_concurrent_files
            
            for i in range(0, total_documents, batch_size):
                batch = documents_data[i:i + batch_size]
                batch_results = await self._process_document_batch(batch)
                
                for result in batch_results:
                    processed += 1
                    if result['success']:
                        successful += 1
                    else:
                        failed += 1
                        self.logger.error(f"Document processing failed: {result.get('error')}")
                
                self.logger.info(f"Processed {processed}/{total_documents} documents")
            
            processing_duration = time.time() - start_time
            
            results = {
                "total_documents": total_documents,
                "processed": processed,
                "successful": successful,
                "failed": failed,
                "processing_duration": processing_duration,
                "documents_per_second": processed / processing_duration if processing_duration > 0 else 0
            }
            
            self.logger.info(f"Document corpus processing completed: {successful}/{total_documents} successful in {processing_duration:.2f}s")
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error processing document corpus: {str(e)}")
            raise
    
    async def _process_document_batch(self, documents_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process a batch of documents"""
        tasks = []
        
        for doc_data in documents_data:
            task = self._process_single_document(doc_data)
            tasks.append(task)
        
        return await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _process_single_document(self, doc_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process a single document"""
        try:
            content = doc_data.get('text', '')
            if not content:
                return {"success": False, "error": "No content found"}
            
            # Insert document into RAG system
            await self.rag_anything.ainsert(content)
            
            return {"success": True, "document_id": doc_data.get('checksum')}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def query_documents(self, question: str, **kwargs) -> Dict[str, Any]:
        """
        Query the document corpus with enhanced production features
        
        Args:
            question: User question
            **kwargs: Additional query parameters
            
        Returns:
            Query response with metadata
        """
        if not self.is_initialized:
            raise RuntimeError("RAG engine not initialized")
        
        start_time = time.time()
        
        try:
            # Use RAG-Anything for query
            rag_result = await self.rag_anything.aquery(question)
            query_duration = time.time() - start_time
            
            result = {
                'answer': rag_result,
                'mode': 'rag_anything',
                'query_duration': query_duration,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error processing query: {str(e)}")
            raise
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform comprehensive health check"""
        health_status = {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "initialized": self.is_initialized,
            "initialization_time": self.initialization_time.isoformat() if self.initialization_time else None,
            "components": {}
        }
        
        try:
            # Check RAG system
            if self.rag_anything:
                test_result = await self._test_system_functionality()
                health_status["components"]["rag_system"] = {
                    "status": "healthy" if test_result['success'] else "unhealthy",
                    "details": test_result
                }
            else:
                health_status["components"]["rag_system"] = {
                    "status": "not_initialized"
                }
            
            self.last_health_check = datetime.utcnow()
            
        except Exception as e:
            health_status["status"] = "unhealthy"
            health_status["error"] = str(e)
            self.logger.error(f"Health check failed: {str(e)}")
        
        return health_status
    
    async def cleanup(self):
        """Clean up system resources"""
        try:
            if self.rag_anything:
                await self.rag_anything.finalize_storages()
            
            self.logger.info("Production RAG engine cleanup completed")
            
        except Exception as e:
            self.logger.error(f"Error during cleanup: {str(e)}")