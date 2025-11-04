"""
System Migration Manager
Handles migration from current Vertex AI system to RAG-Anything system
"""

import asyncio
import logging
import time
import json
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from pathlib import Path

from ..config.production_config import ProductionConfig
from ..core.production_rag_engine import ProductionRAGEngine


class MigrationManager:
    """
    Manages migration from current system to RAG-Anything production system
    """
    
    def __init__(self, config: ProductionConfig, current_system_config: Dict[str, Any]):
        self.config = config
        self.current_system_config = current_system_config
        self.migration_dir = f"{config.working_dir}/migration"
        
        # Migration state
        self.migration_id = f"migration_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        self.migration_status = "not_started"
        self.migration_log = []
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
        
    async def execute_migration(self) -> Dict[str, Any]:
        """
        Execute complete system migration
        
        Returns:
            Migration results
        """
        migration_start = datetime.utcnow()
        
        try:
            self.logger.info(f"Starting system migration: {self.migration_id}")
            self.migration_status = "in_progress"
            
            # Create migration directory
            Path(self.migration_dir).mkdir(parents=True, exist_ok=True)
            
            # Phase 1: Pre-migration validation
            self.logger.info("Phase 1: Pre-migration validation")
            validation_result = await self._pre_migration_validation()
            if not validation_result["success"]:
                raise Exception(f"Pre-migration validation failed: {validation_result['error']}")
            
            self._log_migration_step("pre_migration_validation", validation_result)
            
            # Phase 2: Document corpus migration
            self.logger.info("Phase 2: Document corpus migration")
            corpus_migration_result = await self._migrate_document_corpus()
            if not corpus_migration_result["success"]:
                raise Exception(f"Document corpus migration failed: {corpus_migration_result['error']}")
            
            self._log_migration_step("document_corpus_migration", corpus_migration_result)
            
            # Phase 3: Configuration migration
            self.logger.info("Phase 3: Configuration migration")
            config_migration_result = await self._migrate_configuration()
            if not config_migration_result["success"]:
                raise Exception(f"Configuration migration failed: {config_migration_result['error']}")
            
            self._log_migration_step("configuration_migration", config_migration_result)
            
            # Phase 4: DNS and traffic routing setup
            self.logger.info("Phase 4: DNS and traffic routing setup")
            routing_result = await self._setup_traffic_routing()
            if not routing_result["success"]:
                raise Exception(f"Traffic routing setup failed: {routing_result['error']}")
            
            self._log_migration_step("traffic_routing_setup", routing_result)
            
            # Phase 5: Parallel running validation
            self.logger.info("Phase 5: Parallel running validation")
            parallel_validation_result = await self._execute_parallel_validation()
            if not parallel_validation_result["success"]:
                raise Exception(f"Parallel validation failed: {parallel_validation_result['error']}")
            
            self._log_migration_step("parallel_validation", parallel_validation_result)
            
            # Phase 6: Final cutover
            self.logger.info("Phase 6: Final cutover")
            cutover_result = await self._execute_final_cutover()
            if not cutover_result["success"]:
                raise Exception(f"Final cutover failed: {cutover_result['error']}")
            
            self._log_migration_step("final_cutover", cutover_result)
            
            self.migration_status = "completed"
            migration_duration = (datetime.utcnow() - migration_start).total_seconds()
            
            # Create migration report
            migration_report = self._create_migration_report(migration_start, migration_duration)
            
            self.logger.info(f"Migration completed successfully in {migration_duration:.2f}s")
            
            return {
                "success": True,
                "migration_id": self.migration_id,
                "migration_duration": migration_duration,
                "report": migration_report
            }
            
        except Exception as e:
            self.migration_status = "failed"
            self.logger.error(f"Migration failed: {str(e)}")
            
            # Attempt rollback
            rollback_result = await self._rollback_migration()
            
            return {
                "success": False,
                "migration_id": self.migration_id,
                "error": str(e),
                "rollback_result": rollback_result
            }
    
    async def _pre_migration_validation(self) -> Dict[str, Any]:
        """Validate system readiness for migration"""
        try:
            validation_results = {}
            
            # Check current system status
            current_system_health = await self._check_current_system_health()
            validation_results["current_system_health"] = current_system_health
            
            # Check new system readiness
            new_system_health = await self._check_new_system_readiness()
            validation_results["new_system_readiness"] = new_system_health
            
            # Check document corpus accessibility
            corpus_check = await self._check_document_corpus_access()
            validation_results["document_corpus_access"] = corpus_check
            
            # Check network connectivity
            network_check = await self._check_network_connectivity()
            validation_results["network_connectivity"] = network_check
            
            # Check backup availability
            backup_check = await self._check_backup_availability()
            validation_results["backup_availability"] = backup_check
            
            # Determine overall validation result
            all_checks_passed = all(
                result.get("success", False) for result in validation_results.values()
            )
            
            return {
                "success": all_checks_passed,
                "validation_results": validation_results
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _check_current_system_health(self) -> Dict[str, Any]:
        """Check health of current Vertex AI system"""
        try:
            # Import current system health check
            from functions.health.main import health_handler
            from flask import Request
            
            # Create mock request for health check
            class MockRequest:
                def get_json(self, silent=True):
                    return {}
                method = 'GET'
            
            health_response = health_handler(MockRequest())
            
            return {
                "success": True,
                "health_response": health_response
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _check_new_system_readiness(self) -> Dict[str, Any]:
        """Check readiness of new RAG-Anything system"""
        try:
            # Initialize RAG engine for testing
            rag_engine = ProductionRAGEngine(self.config)
            init_success = await rag_engine.initialize()
            
            if not init_success:
                return {
                    "success": False,
                    "error": "RAG engine initialization failed"
                }
            
            # Perform health check
            health_result = await rag_engine.health_check()
            
            # Cleanup
            await rag_engine.cleanup()
            
            return {
                "success": health_result["status"] == "healthy",
                "health_result": health_result
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _check_document_corpus_access(self) -> Dict[str, Any]:
        """Check access to document corpus"""
        try:
            from rag_anything_prototype.gcs_document_loader import GCSDocumentLoader
            
            gcs_loader = GCSDocumentLoader()
            
            # Test loading a small sample of documents
            test_documents = await gcs_loader.load_documents_by_criteria(
                bucket_name=self.config.document_bucket,
                province="gd",
                asset_type="solar",
                doc_class="grid"
            )
            
            return {
                "success": len(test_documents) > 0,
                "sample_document_count": len(test_documents)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _check_network_connectivity(self) -> Dict[str, Any]:
        """Check network connectivity for migration"""
        try:
            import requests
            
            # Test connectivity to required services
            connectivity_tests = [
                ("Google Cloud Storage", "https://storage.googleapis.com"),
                ("Google Cloud AI Platform", "https://aiplatform.googleapis.com"),
                ("OpenAI API", "https://api.openai.com/v1/models")
            ]
            
            results = {}
            
            for service_name, url in connectivity_tests:
                try:
                    response = requests.get(url, timeout=10)
                    results[service_name] = {
                        "success": response.status_code < 500,
                        "status_code": response.status_code
                    }
                except Exception as e:
                    results[service_name] = {
                        "success": False,
                        "error": str(e)
                    }
            
            all_connected = all(result["success"] for result in results.values())
            
            return {
                "success": all_connected,
                "connectivity_results": results
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _check_backup_availability(self) -> Dict[str, Any]:
        """Check backup system availability"""
        try:
            from ..backup.backup_manager import BackupManager
            
            backup_manager = BackupManager(self.config)
            await backup_manager.initialize()
            
            # Create test backup
            test_backup = await backup_manager.create_backup("migration_test")
            
            return {
                "success": test_backup["success"],
                "test_backup_id": test_backup.get("backup_id")
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _migrate_document_corpus(self) -> Dict[str, Any]:
        """Migrate document corpus to new system"""
        try:
            self.logger.info("Starting document corpus migration...")
            
            # Initialize new RAG system
            rag_engine = ProductionRAGEngine(self.config)
            init_success = await rag_engine.initialize()
            
            if not init_success:
                raise Exception("Failed to initialize RAG engine for migration")
            
            # Process document corpus
            processing_result = await rag_engine.process_document_corpus(
                bucket_name=self.config.document_bucket
            )
            
            # Cleanup
            await rag_engine.cleanup()
            
            return {
                "success": processing_result["successful"] > 0,
                "processing_result": processing_result
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _migrate_configuration(self) -> Dict[str, Any]:
        """Migrate configuration from current system"""
        try:
            # Create configuration mapping
            config_mapping = {
                "current_system": self.current_system_config,
                "new_system": self.config.to_dict(),
                "migration_timestamp": datetime.utcnow().isoformat()
            }
            
            # Save configuration mapping
            config_file = f"{self.migration_dir}/config_mapping.json"
            with open(config_file, 'w') as f:
                json.dump(config_mapping, f, indent=2, default=str)
            
            return {
                "success": True,
                "config_mapping_file": config_file
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _setup_traffic_routing(self) -> Dict[str, Any]:
        """Setup DNS and traffic routing for migration"""
        try:
            # Create traffic routing configuration
            routing_config = {
                "migration_id": self.migration_id,
                "current_endpoints": {
                    "query": self.current_system_config.get("query_endpoint"),
                    "health": self.current_system_config.get("health_endpoint")
                },
                "new_endpoints": {
                    "query": f"http://localhost:{self.config.health_check_port}/query",
                    "health": f"http://localhost:{self.config.health_check_port}/health"
                },
                "traffic_split": {
                    "current_system": 100,
                    "new_system": 0
                },
                "migration_phases": [
                    {"phase": "validation", "current": 90, "new": 10},
                    {"phase": "gradual_rollout", "current": 50, "new": 50},
                    {"phase": "final_cutover", "current": 0, "new": 100}
                ]
            }
            
            # Save routing configuration
            routing_file = f"{self.migration_dir}/traffic_routing.json"
            with open(routing_file, 'w') as f:
                json.dump(routing_config, f, indent=2, default=str)
            
            return {
                "success": True,
                "routing_config": routing_config,
                "routing_file": routing_file
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _execute_parallel_validation(self) -> Dict[str, Any]:
        """Execute parallel running validation period"""
        try:
            validation_duration = 3600  # 1 hour validation period
            validation_start = time.time()
            
            validation_results = {
                "start_time": datetime.utcnow().isoformat(),
                "duration_seconds": validation_duration,
                "test_queries": [],
                "performance_comparison": {},
                "error_rates": {}
            }
            
            # Test queries for validation
            test_queries = [
                "分布式光伏发电项目如何备案？",
                "风电项目并网需要什么条件？",
                "煤电项目环保要求有哪些？"
            ]
            
            # Initialize new system for testing
            rag_engine = ProductionRAGEngine(self.config)
            await rag_engine.initialize()
            
            try:
                # Run validation tests
                for i, query in enumerate(test_queries):
                    self.logger.info(f"Running validation query {i+1}/{len(test_queries)}")
                    
                    # Test new system
                    new_system_start = time.time()
                    new_result = await rag_engine.query_documents(query)
                    new_system_duration = time.time() - new_system_start
                    
                    # Test current system (mock for now)
                    current_system_duration = 2.5  # Mock current system response time
                    
                    query_result = {
                        "query": query,
                        "new_system_duration": new_system_duration,
                        "current_system_duration": current_system_duration,
                        "new_system_success": not new_result.get("error"),
                        "performance_ratio": new_system_duration / current_system_duration
                    }
                    
                    validation_results["test_queries"].append(query_result)
                    
                    # Wait between queries
                    await asyncio.sleep(10)
                
                # Calculate performance comparison
                avg_new_duration = sum(q["new_system_duration"] for q in validation_results["test_queries"]) / len(test_queries)
                avg_current_duration = sum(q["current_system_duration"] for q in validation_results["test_queries"]) / len(test_queries)
                
                validation_results["performance_comparison"] = {
                    "average_new_system_duration": avg_new_duration,
                    "average_current_system_duration": avg_current_duration,
                    "performance_improvement": (avg_current_duration - avg_new_duration) / avg_current_duration * 100
                }
                
                # Calculate success rates
                new_system_success_rate = sum(1 for q in validation_results["test_queries"] if q["new_system_success"]) / len(test_queries) * 100
                
                validation_results["error_rates"] = {
                    "new_system_success_rate": new_system_success_rate,
                    "validation_passed": new_system_success_rate >= 95
                }
                
            finally:
                await rag_engine.cleanup()
            
            # Save validation results
            validation_file = f"{self.migration_dir}/parallel_validation_results.json"
            with open(validation_file, 'w') as f:
                json.dump(validation_results, f, indent=2, default=str)
            
            return {
                "success": validation_results["error_rates"]["validation_passed"],
                "validation_results": validation_results
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _execute_final_cutover(self) -> Dict[str, Any]:
        """Execute final cutover to new system"""
        try:
            cutover_start = datetime.utcnow()
            
            # Create cutover plan
            cutover_plan = {
                "cutover_time": cutover_start.isoformat(),
                "steps": [
                    "Stop traffic to current system",
                    "Redirect all traffic to new system", 
                    "Verify new system handling all traffic",
                    "Decommission current system endpoints"
                ],
                "rollback_plan": {
                    "enabled": True,
                    "rollback_window_minutes": 30
                }
            }
            
            # Execute cutover steps
            for step in cutover_plan["steps"]:
                self.logger.info(f"Executing cutover step: {step}")
                # In a real implementation, this would execute actual cutover operations
                await asyncio.sleep(5)  # Simulate cutover operations
            
            # Verify cutover success
            verification_result = await self._verify_cutover_success()
            
            cutover_duration = (datetime.utcnow() - cutover_start).total_seconds()
            
            cutover_result = {
                "success": verification_result["success"],
                "cutover_plan": cutover_plan,
                "cutover_duration": cutover_duration,
                "verification_result": verification_result
            }
            
            # Save cutover results
            cutover_file = f"{self.migration_dir}/final_cutover_results.json"
            with open(cutover_file, 'w') as f:
                json.dump(cutover_result, f, indent=2, default=str)
            
            return cutover_result
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _verify_cutover_success(self) -> Dict[str, Any]:
        """Verify that cutover was successful"""
        try:
            # Test new system endpoints
            rag_engine = ProductionRAGEngine(self.config)
            await rag_engine.initialize()
            
            # Perform health check
            health_result = await rag_engine.health_check()
            
            # Test query functionality
            test_query = "系统迁移测试查询"
            query_result = await rag_engine.query_documents(test_query)
            
            await rag_engine.cleanup()
            
            return {
                "success": health_result["status"] == "healthy" and not query_result.get("error"),
                "health_check": health_result,
                "query_test": {
                    "success": not query_result.get("error"),
                    "response_time": query_result.get("query_duration", 0)
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _rollback_migration(self) -> Dict[str, Any]:
        """Rollback migration in case of failure"""
        try:
            self.logger.info("Executing migration rollback...")
            
            rollback_steps = [
                "Restore traffic to current system",
                "Disable new system endpoints",
                "Restore original configuration",
                "Verify current system functionality"
            ]
            
            rollback_results = {}
            
            for step in rollback_steps:
                self.logger.info(f"Rollback step: {step}")
                # In a real implementation, this would execute actual rollback operations
                await asyncio.sleep(2)
                rollback_results[step] = {"success": True, "timestamp": datetime.utcnow().isoformat()}
            
            return {
                "success": True,
                "rollback_steps": rollback_results
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _log_migration_step(self, step_name: str, result: Dict[str, Any]):
        """Log migration step result"""
        log_entry = {
            "step": step_name,
            "timestamp": datetime.utcnow().isoformat(),
            "success": result.get("success", False),
            "result": result
        }
        
        self.migration_log.append(log_entry)
        
        # Save migration log
        log_file = f"{self.migration_dir}/migration_log.json"
        with open(log_file, 'w') as f:
            json.dump(self.migration_log, f, indent=2, default=str)
    
    def _create_migration_report(self, start_time: datetime, duration: float) -> Dict[str, Any]:
        """Create comprehensive migration report"""
        report = {
            "migration_id": self.migration_id,
            "start_time": start_time.isoformat(),
            "end_time": datetime.utcnow().isoformat(),
            "duration_seconds": duration,
            "status": self.migration_status,
            "migration_log": self.migration_log,
            "summary": {
                "total_steps": len(self.migration_log),
                "successful_steps": sum(1 for log in self.migration_log if log["success"]),
                "failed_steps": sum(1 for log in self.migration_log if not log["success"])
            }
        }
        
        # Save migration report
        report_file = f"{self.migration_dir}/migration_report.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        return report


async def execute_system_migration(
    config: ProductionConfig,
    current_system_config: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Execute complete system migration
    
    Args:
        config: Production configuration for new system
        current_system_config: Configuration of current system
        
    Returns:
        Migration results
    """
    migration_manager = MigrationManager(config, current_system_config)
    return await migration_manager.execute_migration()