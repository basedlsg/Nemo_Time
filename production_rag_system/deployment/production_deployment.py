"""
Production Deployment Configuration
Handles deployment setup, monitoring, and operational procedures
"""

import os
import yaml
import json
import asyncio
import logging
from typing import Dict, Any, List, Optional
from pathlib import Path
from datetime import datetime

from ..config.production_config import ProductionConfig, load_production_config
from ..core.production_rag_engine import ProductionRAGEngine
from ..monitoring.metrics_collector import MetricsCollector, start_performance_monitoring
from ..backup.backup_manager import BackupManager


class ProductionDeployment:
    """
    Manages production deployment of RAG-Anything system
    """
    
    def __init__(self, config_overrides: Optional[Dict[str, Any]] = None):
        self.config_overrides = config_overrides or {}
        self.config = None
        self.rag_engine = None
        self.metrics_collector = None
        self.backup_manager = None
        
        # Deployment state
        self.is_deployed = False
        self.deployment_time = None
        
        # Setup logging
        self._setup_logging()
        
    def _setup_logging(self):
        """Setup deployment logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    async def deploy(self) -> Dict[str, Any]:
        """
        Deploy the production RAG-Anything system
        
        Returns:
            Deployment results
        """
        deployment_start = datetime.utcnow()
        
        try:
            self.logger.info("Starting production deployment...")
            
            # 1. Load and validate configuration
            self.logger.info("Loading production configuration...")
            self.config = load_production_config()
            
            # Apply any overrides
            for key, value in self.config_overrides.items():
                if hasattr(self.config, key):
                    setattr(self.config, key, value)
            
            # Validate configuration
            config_errors = self.config.validate()
            if config_errors:
                raise ValueError(f"Configuration validation failed: {'; '.join(config_errors)}")
            
            # 2. Create production directories
            self.logger.info("Creating production directories...")
            self._create_production_directories()
            
            # 3. Initialize monitoring
            if self.config.enable_monitoring:
                self.logger.info("Initializing monitoring...")
                self.metrics_collector = MetricsCollector(self.config)
                await self.metrics_collector.initialize()
            
            # 4. Initialize backup manager
            self.logger.info("Initializing backup manager...")
            self.backup_manager = BackupManager(self.config)
            await self.backup_manager.initialize()
            
            # 5. Initialize RAG engine
            self.logger.info("Initializing RAG engine...")
            self.rag_engine = ProductionRAGEngine(self.config)
            
            # Add monitoring to RAG engine if available
            if self.metrics_collector:
                self.rag_engine.metrics_collector = self.metrics_collector
            
            if self.backup_manager:
                self.rag_engine.backup_manager = self.backup_manager
            
            # Initialize the engine
            engine_init_success = await self.rag_engine.initialize()
            if not engine_init_success:
                raise RuntimeError("Failed to initialize RAG engine")
            
            # 6. Start background monitoring
            if self.metrics_collector:
                self.logger.info("Starting performance monitoring...")
                asyncio.create_task(start_performance_monitoring(self.metrics_collector))
            
            # 7. Create initial backup
            self.logger.info("Creating initial deployment backup...")
            initial_backup = await self.backup_manager.create_backup("deployment")
            
            # 8. Generate deployment manifest
            deployment_manifest = self._create_deployment_manifest(deployment_start)
            
            self.is_deployed = True
            self.deployment_time = deployment_start
            
            deployment_duration = (datetime.utcnow() - deployment_start).total_seconds()
            
            self.logger.info(f"Production deployment completed successfully in {deployment_duration:.2f}s")
            
            return {
                "success": True,
                "deployment_time": deployment_start.isoformat(),
                "deployment_duration": deployment_duration,
                "config": self.config.to_dict(),
                "initial_backup": initial_backup,
                "manifest": deployment_manifest
            }
            
        except Exception as e:
            self.logger.error(f"Deployment failed: {str(e)}")
            
            # Attempt cleanup on failure
            await self._cleanup_failed_deployment()
            
            return {
                "success": False,
                "error": str(e),
                "deployment_time": deployment_start.isoformat()
            }
    
    def _create_production_directories(self):
        """Create all necessary production directories"""
        directories = [
            self.config.working_dir,
            f"{self.config.working_dir}/parsed",
            f"{self.config.working_dir}/logs",
            f"{self.config.working_dir}/backups",
            f"{self.config.working_dir}/temp",
            f"{self.config.working_dir}/metrics",
            f"{self.config.working_dir}/deployment"
        ]
        
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
            self.logger.info(f"Created directory: {directory}")
    
    def _create_deployment_manifest(self, deployment_start: datetime) -> Dict[str, Any]:
        """Create deployment manifest with all deployment information"""
        manifest = {
            "deployment_id": f"prod_deploy_{deployment_start.strftime('%Y%m%d_%H%M%S')}",
            "deployment_time": deployment_start.isoformat(),
            "config": self.config.to_dict(),
            "components": {
                "rag_engine": {
                    "initialized": self.rag_engine.is_initialized if self.rag_engine else False,
                    "initialization_time": self.rag_engine.initialization_time.isoformat() if self.rag_engine and self.rag_engine.initialization_time else None
                },
                "monitoring": {
                    "enabled": self.config.enable_monitoring,
                    "metrics_collector": self.metrics_collector is not None
                },
                "backup": {
                    "backup_manager": self.backup_manager is not None,
                    "backup_schedule": self.config.backup_schedule
                }
            },
            "environment": {
                "python_version": os.sys.version,
                "working_directory": self.config.working_dir,
                "project_id": self.config.project_id,
                "region": self.config.region
            }
        }
        
        # Save manifest to file
        manifest_file = f"{self.config.working_dir}/deployment/deployment_manifest.json"
        with open(manifest_file, 'w') as f:
            json.dump(manifest, f, indent=2, default=str)
        
        return manifest
    
    async def process_document_corpus(self, bucket_name: str, max_documents: Optional[int] = None) -> Dict[str, Any]:
        """
        Process document corpus in production
        
        Args:
            bucket_name: GCS bucket containing documents
            max_documents: Maximum number of documents to process
            
        Returns:
            Processing results
        """
        if not self.is_deployed or not self.rag_engine:
            raise RuntimeError("System not deployed or RAG engine not available")
        
        self.logger.info(f"Starting document corpus processing: bucket={bucket_name}, max_docs={max_documents}")
        
        # Create pre-processing backup
        if self.backup_manager:
            pre_processing_backup = await self.backup_manager.create_backup("pre_processing")
            self.logger.info(f"Created pre-processing backup: {pre_processing_backup.get('backup_id')}")
        
        try:
            # Process documents
            results = await self.rag_engine.process_document_corpus(bucket_name, max_documents)
            
            # Create post-processing backup
            if self.backup_manager:
                post_processing_backup = await self.backup_manager.create_backup("post_processing")
                results["post_processing_backup"] = post_processing_backup
            
            self.logger.info(f"Document corpus processing completed: {results['successful']}/{results['total_documents']} successful")
            
            return results
            
        except Exception as e:
            self.logger.error(f"Document corpus processing failed: {str(e)}")
            raise
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform comprehensive production health check"""
        if not self.is_deployed:
            return {
                "status": "not_deployed",
                "timestamp": datetime.utcnow().isoformat()
            }
        
        health_status = {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "deployment_time": self.deployment_time.isoformat() if self.deployment_time else None,
            "components": {}
        }
        
        try:
            # Check RAG engine
            if self.rag_engine:
                rag_health = await self.rag_engine.health_check()
                health_status["components"]["rag_engine"] = rag_health
            
            # Check metrics collector
            if self.metrics_collector:
                metrics_health = await self.metrics_collector.health_check()
                health_status["components"]["metrics"] = metrics_health
            
            # Check backup manager
            if self.backup_manager:
                backup_health = await self.backup_manager.health_check()
                health_status["components"]["backup"] = backup_health
            
            # Determine overall status
            component_statuses = [comp.get("status") for comp in health_status["components"].values()]
            if any(status == "unhealthy" for status in component_statuses):
                health_status["status"] = "unhealthy"
            elif any(status == "degraded" for status in component_statuses):
                health_status["status"] = "degraded"
            
        except Exception as e:
            health_status["status"] = "unhealthy"
            health_status["error"] = str(e)
        
        return health_status
    
    async def get_system_metrics(self) -> Dict[str, Any]:
        """Get comprehensive system metrics"""
        if not self.metrics_collector:
            return {"error": "Metrics collection not enabled"}
        
        return await self.metrics_collector.get_metrics()
    
    async def create_backup(self, backup_type: str = "manual") -> Dict[str, Any]:
        """Create system backup"""
        if not self.backup_manager:
            raise RuntimeError("Backup manager not available")
        
        return await self.backup_manager.create_backup(backup_type)
    
    async def restore_backup(self, backup_id: str) -> Dict[str, Any]:
        """Restore system from backup"""
        if not self.backup_manager:
            raise RuntimeError("Backup manager not available")
        
        return await self.backup_manager.restore_backup(backup_id)
    
    async def query_documents(self, question: str, **kwargs) -> Dict[str, Any]:
        """Query documents through production system"""
        if not self.rag_engine:
            raise RuntimeError("RAG engine not available")
        
        return await self.rag_engine.query_documents(question, **kwargs)
    
    async def _cleanup_failed_deployment(self):
        """Clean up resources after failed deployment"""
        try:
            if self.rag_engine:
                await self.rag_engine.cleanup()
            
            if self.metrics_collector:
                await self.metrics_collector.cleanup()
            
            if self.backup_manager:
                await self.backup_manager.cleanup()
            
            self.logger.info("Failed deployment cleanup completed")
            
        except Exception as e:
            self.logger.error(f"Error during failed deployment cleanup: {str(e)}")
    
    async def shutdown(self):
        """Gracefully shutdown the production system"""
        try:
            self.logger.info("Shutting down production system...")
            
            # Create shutdown backup
            if self.backup_manager:
                shutdown_backup = await self.backup_manager.create_backup("shutdown")
                self.logger.info(f"Created shutdown backup: {shutdown_backup.get('backup_id')}")
            
            # Cleanup components
            if self.rag_engine:
                await self.rag_engine.cleanup()
            
            if self.metrics_collector:
                await self.metrics_collector.cleanup()
            
            if self.backup_manager:
                await self.backup_manager.cleanup()
            
            self.is_deployed = False
            
            self.logger.info("Production system shutdown completed")
            
        except Exception as e:
            self.logger.error(f"Error during shutdown: {str(e)}")


async def deploy_production_system(config_overrides: Optional[Dict[str, Any]] = None) -> ProductionDeployment:
    """
    Deploy production RAG-Anything system
    
    Args:
        config_overrides: Configuration overrides
        
    Returns:
        Deployed ProductionDeployment instance
    """
    deployment = ProductionDeployment(config_overrides)
    
    deploy_result = await deployment.deploy()
    
    if not deploy_result["success"]:
        raise RuntimeError(f"Deployment failed: {deploy_result.get('error')}")
    
    return deployment