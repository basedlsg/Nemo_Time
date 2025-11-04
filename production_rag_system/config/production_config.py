"""
Production Configuration for RAG-Anything System
Handles all production settings, environment variables, and deployment configuration
"""

import os
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class ProductionConfig:
    """Production configuration for RAG-Anything system"""
    
    # Project Configuration
    project_id: str = field(default_factory=lambda: os.getenv('GOOGLE_CLOUD_PROJECT', 'nemo-compliance-prod'))
    region: str = field(default_factory=lambda: os.getenv('REGION', 'asia-east2'))
    environment: str = field(default_factory=lambda: os.getenv('ENVIRONMENT', 'production'))
    
    # Storage Configuration
    working_dir: str = field(default_factory=lambda: os.getenv('RAG_WORKING_DIR', '/app/rag_storage'))
    backup_bucket: str = field(default_factory=lambda: os.getenv('BACKUP_BUCKET', 'nemo-rag-backups'))
    document_bucket: str = field(default_factory=lambda: os.getenv('DOCUMENT_BUCKET', 'nemo-documents'))
    
    # RAG-Anything Configuration
    llm_provider: str = field(default_factory=lambda: os.getenv('LLM_PROVIDER', 'openai'))
    embedding_provider: str = field(default_factory=lambda: os.getenv('EMBEDDING_PROVIDER', 'openai'))
    parser_type: str = field(default_factory=lambda: os.getenv('PARSER_TYPE', 'mineru'))
    
    # Performance Configuration
    max_concurrent_files: int = field(default_factory=lambda: int(os.getenv('MAX_CONCURRENT_FILES', '4')))
    chunk_token_size: int = field(default_factory=lambda: int(os.getenv('CHUNK_TOKEN_SIZE', '800')))
    chunk_overlap_tokens: int = field(default_factory=lambda: int(os.getenv('CHUNK_OVERLAP_TOKENS', '100')))
    top_k_results: int = field(default_factory=lambda: int(os.getenv('TOP_K_RESULTS', '20')))
    
    # Monitoring Configuration
    enable_monitoring: bool = field(default_factory=lambda: os.getenv('ENABLE_MONITORING', 'true').lower() == 'true')
    log_level: str = field(default_factory=lambda: os.getenv('LOG_LEVEL', 'INFO'))
    metrics_port: int = field(default_factory=lambda: int(os.getenv('METRICS_PORT', '8080')))
    health_check_port: int = field(default_factory=lambda: int(os.getenv('HEALTH_CHECK_PORT', '8081')))
    
    # Security Configuration
    api_key_secret: str = field(default_factory=lambda: os.getenv('API_KEY_SECRET', 'rag-api-key'))
    allowed_origins: List[str] = field(default_factory=lambda: os.getenv('ALLOWED_ORIGINS', '*').split(','))
    
    # Perplexity Integration
    enable_perplexity: bool = field(default_factory=lambda: os.getenv('ENABLE_PERPLEXITY', 'true').lower() == 'true')
    perplexity_api_key_secret: str = field(default_factory=lambda: os.getenv('PERPLEXITY_API_KEY_SECRET', 'perplexity-api-key'))
    
    # Backup Configuration
    backup_schedule: str = field(default_factory=lambda: os.getenv('BACKUP_SCHEDULE', '0 2 * * *'))  # Daily at 2 AM
    backup_retention_days: int = field(default_factory=lambda: int(os.getenv('BACKUP_RETENTION_DAYS', '30')))
    
    # Resource Limits
    memory_limit: str = field(default_factory=lambda: os.getenv('MEMORY_LIMIT', '4Gi'))
    cpu_limit: str = field(default_factory=lambda: os.getenv('CPU_LIMIT', '2'))
    disk_size: str = field(default_factory=lambda: os.getenv('DISK_SIZE', '20Gi'))
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        return {
            'project_id': self.project_id,
            'region': self.region,
            'environment': self.environment,
            'working_dir': self.working_dir,
            'backup_bucket': self.backup_bucket,
            'document_bucket': self.document_bucket,
            'llm_provider': self.llm_provider,
            'embedding_provider': self.embedding_provider,
            'parser_type': self.parser_type,
            'max_concurrent_files': self.max_concurrent_files,
            'chunk_token_size': self.chunk_token_size,
            'chunk_overlap_tokens': self.chunk_overlap_tokens,
            'top_k_results': self.top_k_results,
            'enable_monitoring': self.enable_monitoring,
            'log_level': self.log_level,
            'metrics_port': self.metrics_port,
            'health_check_port': self.health_check_port,
            'api_key_secret': self.api_key_secret,
            'allowed_origins': self.allowed_origins,
            'enable_perplexity': self.enable_perplexity,
            'perplexity_api_key_secret': self.perplexity_api_key_secret,
            'backup_schedule': self.backup_schedule,
            'backup_retention_days': self.backup_retention_days,
            'memory_limit': self.memory_limit,
            'cpu_limit': self.cpu_limit,
            'disk_size': self.disk_size
        }
    
    def validate(self) -> List[str]:
        """Validate configuration and return list of errors"""
        errors = []
        
        if not self.project_id or self.project_id == 'your-project-id':
            errors.append("GOOGLE_CLOUD_PROJECT must be set to a valid project ID")
        
        if not self.working_dir:
            errors.append("RAG_WORKING_DIR must be set")
        
        if self.max_concurrent_files < 1:
            errors.append("MAX_CONCURRENT_FILES must be at least 1")
        
        if self.chunk_token_size < 100:
            errors.append("CHUNK_TOKEN_SIZE must be at least 100")
        
        if self.top_k_results < 1:
            errors.append("TOP_K_RESULTS must be at least 1")
        
        if self.log_level not in ['DEBUG', 'INFO', 'WARNING', 'ERROR']:
            errors.append("LOG_LEVEL must be one of: DEBUG, INFO, WARNING, ERROR")
        
        return errors


@dataclass
class RAGAnythingProductionConfig:
    """RAG-Anything specific production configuration"""
    
    # Parser Configuration
    enable_image_processing: bool = True
    enable_table_processing: bool = True
    enable_equation_processing: bool = True
    
    # Context Configuration
    context_window: int = 2
    context_mode: str = "page"
    max_context_tokens: int = 2000
    include_headers: bool = True
    include_captions: bool = True
    
    # Content Format
    content_format: str = "minerU"
    
    # LightRAG Configuration
    max_entity_tokens: int = 32
    max_relation_tokens: int = 64
    max_total_tokens: int = 4000
    cosine_threshold: float = 0.7
    related_chunk_number: int = 5
    
    # Performance Settings
    embedding_batch_num: int = 16
    embedding_func_max_async: int = 8
    llm_model_max_async: int = 4
    max_parallel_insert: int = 2
    
    # Graph Settings
    max_graph_nodes: int = 1000
    
    # Caching
    enable_llm_cache: bool = True
    
    # Chinese Language Settings
    language: str = "zh-CN"
    domain: str = "regulatory"
    enable_chinese_segmentation: bool = True
    
    def to_lightrag_kwargs(self, base_config: ProductionConfig) -> Dict[str, Any]:
        """Convert to LightRAG kwargs"""
        return {
            "chunk_token_size": base_config.chunk_token_size,
            "chunk_overlap_token_size": base_config.chunk_overlap_tokens,
            "top_k": base_config.top_k_results,
            "chunk_top_k": min(base_config.top_k_results // 2, 10),
            "max_entity_tokens": self.max_entity_tokens,
            "max_relation_tokens": self.max_relation_tokens,
            "max_total_tokens": self.max_total_tokens,
            "cosine_threshold": self.cosine_threshold,
            "related_chunk_number": self.related_chunk_number,
            "embedding_batch_num": self.embedding_batch_num,
            "embedding_func_max_async": self.embedding_func_max_async,
            "llm_model_max_async": self.llm_model_max_async,
            "max_parallel_insert": self.max_parallel_insert,
            "max_graph_nodes": self.max_graph_nodes,
            "enable_llm_cache": self.enable_llm_cache,
            "addon_params": {
                "language": self.language,
                "domain": self.domain,
                "enable_chinese_segmentation": self.enable_chinese_segmentation
            }
        }


def load_production_config() -> ProductionConfig:
    """Load production configuration from environment"""
    config = ProductionConfig()
    
    # Validate configuration
    errors = config.validate()
    if errors:
        raise ValueError(f"Configuration validation failed: {'; '.join(errors)}")
    
    return config


def load_rag_config() -> RAGAnythingProductionConfig:
    """Load RAG-Anything production configuration"""
    return RAGAnythingProductionConfig()


def create_production_directories(config: ProductionConfig) -> None:
    """Create necessary production directories"""
    directories = [
        config.working_dir,
        f"{config.working_dir}/parsed",
        f"{config.working_dir}/logs",
        f"{config.working_dir}/backups",
        f"{config.working_dir}/temp"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)