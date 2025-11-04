"""
RAG-Anything Configuration and Setup
Handles initialization and configuration for Chinese regulatory documents
"""

import os
import asyncio
from typing import Dict, Any, Optional, Callable
from pathlib import Path

# RAG-Anything imports
from raganything import RAGAnything, RAGAnythingConfig

# Model function imports (these would be implemented based on your LLM setup)
from .model_functions import (
    create_llm_model_func,
    create_embedding_func,
    create_vision_model_func
)


class RAGAnythingSetup:
    """
    Setup and configuration manager for RAG-Anything with Chinese regulatory documents
    """
    
    def __init__(self, config_overrides: Optional[Dict[str, Any]] = None):
        self.config_overrides = config_overrides or {}
        self.rag_anything = None
        
    async def initialize_rag_system(
        self,
        working_dir: str = "./rag_storage",
        llm_provider: str = "openai",
        embedding_provider: str = "openai"
    ) -> RAGAnything:
        """
        Initialize RAG-Anything system with Chinese language optimization
        
        Args:
            working_dir: Directory for RAG storage
            llm_provider: LLM provider (openai, anthropic, etc.)
            embedding_provider: Embedding provider
            
        Returns:
            Configured RAGAnything instance
        """
        try:
            print("Initializing RAG-Anything system for Chinese regulatory documents...")
            
            # Create working directory
            Path(working_dir).mkdir(parents=True, exist_ok=True)
            
            # Create RAG-Anything configuration
            rag_config = self._create_rag_config(working_dir)
            
            # Create model functions
            llm_model_func = create_llm_model_func(llm_provider)
            embedding_func = create_embedding_func(embedding_provider)
            vision_model_func = create_vision_model_func(llm_provider)
            
            # Create LightRAG kwargs for Chinese optimization
            lightrag_kwargs = self._create_lightrag_kwargs()
            
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
            
            print("RAG-Anything system initialized successfully")
            return self.rag_anything
            
        except Exception as e:
            print(f"Error initializing RAG system: {str(e)}")
            raise
    
    def _create_rag_config(self, working_dir: str) -> RAGAnythingConfig:
        """Create RAG-Anything configuration optimized for Chinese documents"""
        
        config = RAGAnythingConfig(
            # Directory settings
            working_dir=working_dir,
            parser_output_dir=f"{working_dir}/parsed",
            
            # Parser settings - use mineru for better Chinese support
            parser="mineru",
            parse_method="auto",
            
            # Multimodal processing - enable for regulatory documents with images/tables
            enable_image_processing=True,
            enable_table_processing=True,
            enable_equation_processing=True,
            
            # Context extraction optimized for Chinese regulatory structure
            context_window=2,  # Include surrounding context
            context_mode="page",
            max_context_tokens=2000,
            include_headers=True,
            include_captions=True,
            
            # Batch processing settings
            max_concurrent_files=2,  # Conservative for stability
            recursive_folder_processing=True,
            
            # Content format
            content_format="minerU",
            
            # Display settings
            display_content_stats=True
        )
        
        # Apply any overrides
        for key, value in self.config_overrides.items():
            if hasattr(config, key):
                setattr(config, key, value)
        
        return config
    
    def _create_lightrag_kwargs(self) -> Dict[str, Any]:
        """Create LightRAG configuration optimized for Chinese regulatory documents"""
        
        return {
            # Chunking settings optimized for Chinese text
            "chunk_token_size": 800,  # Smaller chunks for Chinese
            "chunk_overlap_token_size": 100,
            
            # Retrieval settings
            "top_k": 20,  # More candidates for better Chinese matching
            "chunk_top_k": 10,
            
            # Entity and relation extraction (important for regulatory structure)
            "max_entity_tokens": 32,
            "max_relation_tokens": 64,
            "max_total_tokens": 4000,
            
            # Similarity thresholds
            "cosine_threshold": 0.7,  # Slightly lower for Chinese semantic matching
            "related_chunk_number": 5,
            
            # Performance settings
            "embedding_batch_num": 16,
            "embedding_func_max_async": 8,
            "llm_model_max_async": 4,
            "max_parallel_insert": 2,
            
            # Graph settings for regulatory document relationships
            "max_graph_nodes": 1000,
            
            # Enable caching for better performance
            "enable_llm_cache": True,
            
            # Additional parameters for Chinese language processing
            "addon_params": {
                "language": "zh-CN",
                "domain": "regulatory",
                "enable_chinese_segmentation": True
            }
        }
    
    async def test_system_functionality(self) -> Dict[str, Any]:
        """
        Test basic functionality of the RAG system
        
        Returns:
            Test results dictionary
        """
        if not self.rag_anything:
            return {"success": False, "error": "RAG system not initialized"}
        
        try:
            # Test document insertion
            test_text = """
            第一条 为规范分布式光伏发电项目管理，促进分布式光伏发电健康有序发展，
            根据《可再生能源法》、《电力法》等法律法规，结合本省实际，制定本办法。
            
            第二条 本办法适用于在广东省行政区域内建设的分布式光伏发电项目的备案、
            并网、运营等管理活动。
            """
            
            # Insert test document
            await self.rag_anything.ainsert(test_text)
            
            # Test query
            test_query = "分布式光伏发电项目如何备案？"
            result = await self.rag_anything.aquery(test_query)
            
            return {
                "success": True,
                "test_insertion": "completed",
                "test_query": test_query,
                "query_result_length": len(result) if result else 0,
                "system_status": "functional"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "system_status": "error"
            }
    
    async def get_system_info(self) -> Dict[str, Any]:
        """Get information about the RAG system configuration"""
        
        if not self.rag_anything:
            return {"status": "not_initialized"}
        
        try:
            config_info = self.rag_anything.get_config_info()
            processor_info = self.rag_anything.get_processor_info()
            
            return {
                "status": "initialized",
                "config": config_info,
                "processors": processor_info,
                "working_directory": self.rag_anything.working_dir,
                "lightrag_initialized": self.rag_anything.lightrag is not None
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def cleanup(self):
        """Clean up resources"""
        if self.rag_anything:
            try:
                await self.rag_anything.finalize_storages()
                print("RAG system cleanup completed")
            except Exception as e:
                print(f"Error during cleanup: {str(e)}")


def create_default_rag_setup(
    working_dir: str = "./rag_storage",
    config_overrides: Optional[Dict[str, Any]] = None
) -> RAGAnythingSetup:
    """
    Create a default RAG setup for Chinese regulatory documents
    
    Args:
        working_dir: Working directory for RAG storage
        config_overrides: Configuration overrides
        
    Returns:
        RAGAnythingSetup instance
    """
    return RAGAnythingSetup(config_overrides)


async def quick_setup_rag_system(
    working_dir: str = "./rag_storage",
    llm_provider: str = "openai",
    embedding_provider: str = "openai"
) -> RAGAnything:
    """
    Quick setup function for RAG-Anything system
    
    Args:
        working_dir: Working directory
        llm_provider: LLM provider
        embedding_provider: Embedding provider
        
    Returns:
        Initialized RAGAnything instance
    """
    setup = create_default_rag_setup(working_dir)
    return await setup.initialize_rag_system(
        working_dir=working_dir,
        llm_provider=llm_provider,
        embedding_provider=embedding_provider
    )