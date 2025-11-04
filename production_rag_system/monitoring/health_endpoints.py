"""
Health Check and Monitoring Endpoints
Provides HTTP endpoints for system health checks and metrics collection
"""

import asyncio
import json
import time
from typing import Dict, Any, Optional
from datetime import datetime
from flask import Flask, jsonify, request
import logging

from ..config.production_config import ProductionConfig
from ..core.production_rag_engine import ProductionRAGEngine
from ..monitoring.metrics_collector import MetricsCollector
from ..backup.backup_manager import BackupManager


class HealthEndpoints:
    """
    HTTP endpoints for health checks and monitoring
    """
    
    def __init__(self, config: ProductionConfig):
        self.config = config
        self.app = Flask(__name__)
        self.rag_engine = None
        self.metrics_collector = None
        self.backup_manager = None
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
        
        # Setup routes
        self._setup_routes()
    
    def _setup_routes(self):
        """Setup Flask routes for health and monitoring endpoints"""
        
        @self.app.route('/health', methods=['GET'])
        def health_check():
            """Basic health check endpoint"""
            try:
                health_status = asyncio.run(self._perform_health_check())
                
                status_code = 200 if health_status["status"] == "healthy" else 503
                
                return jsonify(health_status), status_code
                
            except Exception as e:
                self.logger.error(f"Health check failed: {str(e)}")
                return jsonify({
                    "status": "unhealthy",
                    "error": str(e),
                    "timestamp": datetime.utcnow().isoformat()
                }), 503
        
        @self.app.route('/health/detailed', methods=['GET'])
        def detailed_health_check():
            """Detailed health check with component status"""
            try:
                health_status = asyncio.run(self._perform_detailed_health_check())
                
                status_code = 200 if health_status["status"] == "healthy" else 503
                
                return jsonify(health_status), status_code
                
            except Exception as e:
                self.logger.error(f"Detailed health check failed: {str(e)}")
                return jsonify({
                    "status": "unhealthy",
                    "error": str(e),
                    "timestamp": datetime.utcnow().isoformat()
                }), 503
        
        @self.app.route('/metrics', methods=['GET'])
        def get_metrics():
            """Get system metrics in Prometheus format"""
            try:
                metrics = asyncio.run(self._get_prometheus_metrics())
                
                return metrics, 200, {'Content-Type': 'text/plain; charset=utf-8'}
                
            except Exception as e:
                self.logger.error(f"Metrics collection failed: {str(e)}")
                return f"# Error collecting metrics: {str(e)}", 500
        
        @self.app.route('/metrics/json', methods=['GET'])
        def get_metrics_json():
            """Get system metrics in JSON format"""
            try:
                if not self.metrics_collector:
                    return jsonify({"error": "Metrics collection not enabled"}), 503
                
                metrics = asyncio.run(self.metrics_collector.get_metrics())
                
                return jsonify(metrics), 200
                
            except Exception as e:
                self.logger.error(f"JSON metrics collection failed: {str(e)}")
                return jsonify({
                    "error": str(e),
                    "timestamp": datetime.utcnow().isoformat()
                }), 500
        
        @self.app.route('/status', methods=['GET'])
        def get_system_status():
            """Get comprehensive system status"""
            try:
                status = asyncio.run(self._get_system_status())
                
                return jsonify(status), 200
                
            except Exception as e:
                self.logger.error(f"System status check failed: {str(e)}")
                return jsonify({
                    "error": str(e),
                    "timestamp": datetime.utcnow().isoformat()
                }), 500
        
        @self.app.route('/query/test', methods=['POST'])
        def test_query():
            """Test query endpoint for health validation"""
            try:
                if not request.json or 'question' not in request.json:
                    return jsonify({"error": "Missing 'question' in request"}), 400
                
                question = request.json['question']
                
                if not self.rag_engine:
                    return jsonify({"error": "RAG engine not available"}), 503
                
                result = asyncio.run(self.rag_engine.query_documents(question))
                
                return jsonify({
                    "success": True,
                    "result": result,
                    "timestamp": datetime.utcnow().isoformat()
                }), 200
                
            except Exception as e:
                self.logger.error(f"Test query failed: {str(e)}")
                return jsonify({
                    "success": False,
                    "error": str(e),
                    "timestamp": datetime.utcnow().isoformat()
                }), 500
        
        @self.app.route('/backup/status', methods=['GET'])
        def backup_status():
            """Get backup system status"""
            try:
                if not self.backup_manager:
                    return jsonify({"error": "Backup manager not available"}), 503
                
                status = asyncio.run(self.backup_manager.health_check())
                backups = asyncio.run(self.backup_manager.list_backups())
                
                return jsonify({
                    "backup_system": status,
                    "recent_backups": backups[-5:] if backups else [],
                    "total_backups": len(backups),
                    "timestamp": datetime.utcnow().isoformat()
                }), 200
                
            except Exception as e:
                self.logger.error(f"Backup status check failed: {str(e)}")
                return jsonify({
                    "error": str(e),
                    "timestamp": datetime.utcnow().isoformat()
                }), 500
    
    async def _perform_health_check(self) -> Dict[str, Any]:
        """Perform basic health check"""
        health_status = {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "version": "1.0.0",
            "uptime": self._get_uptime()
        }
        
        # Check if RAG engine is available and healthy
        if self.rag_engine:
            rag_health = await self.rag_engine.health_check()
            if rag_health["status"] != "healthy":
                health_status["status"] = "unhealthy"
                health_status["rag_engine_status"] = rag_health["status"]
        else:
            health_status["status"] = "degraded"
            health_status["rag_engine_status"] = "not_initialized"
        
        return health_status
    
    async def _perform_detailed_health_check(self) -> Dict[str, Any]:
        """Perform detailed health check with all components"""
        health_status = {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "version": "1.0.0",
            "uptime": self._get_uptime(),
            "components": {}
        }
        
        # Check RAG engine
        if self.rag_engine:
            rag_health = await self.rag_engine.health_check()
            health_status["components"]["rag_engine"] = rag_health
        else:
            health_status["components"]["rag_engine"] = {
                "status": "not_initialized",
                "message": "RAG engine not available"
            }
        
        # Check metrics collector
        if self.metrics_collector:
            metrics_health = await self.metrics_collector.health_check()
            health_status["components"]["metrics"] = metrics_health
        else:
            health_status["components"]["metrics"] = {
                "status": "not_available",
                "message": "Metrics collection not enabled"
            }
        
        # Check backup manager
        if self.backup_manager:
            backup_health = await self.backup_manager.health_check()
            health_status["components"]["backup"] = backup_health
        else:
            health_status["components"]["backup"] = {
                "status": "not_available",
                "message": "Backup manager not available"
            }
        
        # Determine overall status
        component_statuses = [comp.get("status") for comp in health_status["components"].values()]
        if any(status == "unhealthy" for status in component_statuses):
            health_status["status"] = "unhealthy"
        elif any(status in ["degraded", "not_available"] for status in component_statuses):
            health_status["status"] = "degraded"
        
        return health_status
    
    async def _get_prometheus_metrics(self) -> str:
        """Get metrics in Prometheus format"""
        metrics_lines = []
        
        # Add basic system metrics
        metrics_lines.append("# HELP rag_system_info System information")
        metrics_lines.append("# TYPE rag_system_info gauge")
        metrics_lines.append(f'rag_system_info{{version="1.0.0"}} 1')
        
        # Add uptime metric
        uptime = self._get_uptime()
        metrics_lines.append("# HELP rag_system_uptime_seconds System uptime in seconds")
        metrics_lines.append("# TYPE rag_system_uptime_seconds counter")
        metrics_lines.append(f"rag_system_uptime_seconds {uptime}")
        
        # Add health status metric
        health_status = await self._perform_health_check()
        status_value = 2 if health_status["status"] == "healthy" else 1 if health_status["status"] == "degraded" else 0
        
        metrics_lines.append("# HELP rag_system_health_status System health status (2=healthy, 1=degraded, 0=unhealthy)")
        metrics_lines.append("# TYPE rag_system_health_status gauge")
        metrics_lines.append(f"rag_system_health_status {status_value}")
        
        # Add metrics from metrics collector if available
        if self.metrics_collector:
            try:
                detailed_metrics = await self.metrics_collector.get_metrics()
                
                # Query metrics
                query_metrics = detailed_metrics["detailed_metrics"]["queries"]
                
                metrics_lines.append("# HELP rag_queries_total Total number of queries processed")
                metrics_lines.append("# TYPE rag_queries_total counter")
                metrics_lines.append(f"rag_queries_total {query_metrics['total_queries']}")
                
                metrics_lines.append("# HELP rag_queries_successful_total Total number of successful queries")
                metrics_lines.append("# TYPE rag_queries_successful_total counter")
                metrics_lines.append(f"rag_queries_successful_total {query_metrics['successful_queries']}")
                
                metrics_lines.append("# HELP rag_queries_failed_total Total number of failed queries")
                metrics_lines.append("# TYPE rag_queries_failed_total counter")
                metrics_lines.append(f"rag_queries_failed_total {query_metrics['failed_queries']}")
                
                metrics_lines.append("# HELP rag_query_duration_seconds Average query duration in seconds")
                metrics_lines.append("# TYPE rag_query_duration_seconds gauge")
                metrics_lines.append(f"rag_query_duration_seconds {query_metrics['average_response_time']}")
                
                # Processing metrics
                processing_metrics = detailed_metrics["detailed_metrics"]["processing"]
                
                metrics_lines.append("# HELP rag_documents_processed_total Total number of documents processed")
                metrics_lines.append("# TYPE rag_documents_processed_total counter")
                metrics_lines.append(f"rag_documents_processed_total {processing_metrics['total_documents_processed']}")
                
                # Error metrics
                error_metrics = detailed_metrics["detailed_metrics"]["errors"]
                
                metrics_lines.append("# HELP rag_errors_total Total number of errors")
                metrics_lines.append("# TYPE rag_errors_total counter")
                metrics_lines.append(f"rag_errors_total {error_metrics['total_errors']}")
                
            except Exception as e:
                self.logger.warning(f"Could not collect detailed metrics: {str(e)}")
        
        return "\n".join(metrics_lines) + "\n"
    
    async def _get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        status = {
            "timestamp": datetime.utcnow().isoformat(),
            "uptime": self._get_uptime(),
            "version": "1.0.0",
            "configuration": {
                "project_id": self.config.project_id,
                "region": self.config.region,
                "environment": self.config.environment,
                "working_dir": self.config.working_dir
            }
        }
        
        # Add health status
        health = await self._perform_detailed_health_check()
        status["health"] = health
        
        # Add metrics summary if available
        if self.metrics_collector:
            try:
                metrics = await self.metrics_collector.get_metrics()
                status["metrics_summary"] = metrics["summary"]
            except Exception as e:
                status["metrics_error"] = str(e)
        
        return status
    
    def _get_uptime(self) -> float:
        """Get system uptime in seconds"""
        # This would be calculated from actual system start time
        # For now, return a placeholder
        return time.time() % 86400  # Seconds since midnight
    
    def set_rag_engine(self, rag_engine: ProductionRAGEngine):
        """Set RAG engine instance"""
        self.rag_engine = rag_engine
    
    def set_metrics_collector(self, metrics_collector: MetricsCollector):
        """Set metrics collector instance"""
        self.metrics_collector = metrics_collector
    
    def set_backup_manager(self, backup_manager: BackupManager):
        """Set backup manager instance"""
        self.backup_manager = backup_manager
    
    def run(self, host: str = "0.0.0.0", port: Optional[int] = None, debug: bool = False):
        """Run the health endpoints server"""
        if port is None:
            port = self.config.health_check_port
        
        self.logger.info(f"Starting health endpoints server on {host}:{port}")
        self.app.run(host=host, port=port, debug=debug)


def create_health_endpoints(config: ProductionConfig) -> HealthEndpoints:
    """
    Create health endpoints instance
    
    Args:
        config: Production configuration
        
    Returns:
        HealthEndpoints instance
    """
    return HealthEndpoints(config)