"""
Production Metrics Collection
Comprehensive monitoring and metrics for RAG-Anything system
"""

import time
import json
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from pathlib import Path
import logging

from ..config.production_config import ProductionConfig


class MetricsCollector:
    """
    Collects and manages production metrics for RAG-Anything system
    """
    
    def __init__(self, config: ProductionConfig):
        self.config = config
        self.metrics_file = f"{config.working_dir}/metrics/metrics.json"
        self.logger = logging.getLogger(__name__)
        
        # Metrics storage
        self.metrics = {
            "system": {
                "initialization_count": 0,
                "total_uptime": 0,
                "last_startup": None
            },
            "queries": {
                "total_queries": 0,
                "successful_queries": 0,
                "failed_queries": 0,
                "average_response_time": 0,
                "query_history": []
            },
            "processing": {
                "total_documents_processed": 0,
                "successful_documents": 0,
                "failed_documents": 0,
                "average_processing_time": 0,
                "processing_history": []
            },
            "errors": {
                "total_errors": 0,
                "error_types": {},
                "recent_errors": []
            },
            "performance": {
                "memory_usage": [],
                "cpu_usage": [],
                "disk_usage": []
            }
        }
        
        self.startup_time = datetime.utcnow()
        
    async def initialize(self):
        """Initialize metrics collection"""
        try:
            # Load existing metrics if available
            await self._load_metrics()
            
            # Record initialization
            self.metrics["system"]["initialization_count"] += 1
            self.metrics["system"]["last_startup"] = self.startup_time.isoformat()
            
            # Save updated metrics
            await self._save_metrics()
            
            self.logger.info("Metrics collector initialized")
            
        except Exception as e:
            self.logger.error(f"Error initializing metrics collector: {str(e)}")
    
    async def _load_metrics(self):
        """Load existing metrics from file"""
        try:
            if Path(self.metrics_file).exists():
                with open(self.metrics_file, 'r') as f:
                    saved_metrics = json.load(f)
                    # Merge with default structure
                    self._merge_metrics(saved_metrics)
        except Exception as e:
            self.logger.warning(f"Could not load existing metrics: {str(e)}")
    
    def _merge_metrics(self, saved_metrics: Dict[str, Any]):
        """Merge saved metrics with current structure"""
        for category, data in saved_metrics.items():
            if category in self.metrics:
                if isinstance(data, dict):
                    self.metrics[category].update(data)
                else:
                    self.metrics[category] = data
    
    async def _save_metrics(self):
        """Save metrics to file"""
        try:
            Path(self.metrics_file).parent.mkdir(parents=True, exist_ok=True)
            with open(self.metrics_file, 'w') as f:
                json.dump(self.metrics, f, indent=2, default=str)
        except Exception as e:
            self.logger.error(f"Error saving metrics: {str(e)}")
    
    async def record_initialization(self, duration: float):
        """Record system initialization metrics"""
        self.metrics["system"]["initialization_duration"] = duration
        await self._save_metrics()
        self.logger.info(f"Recorded initialization: {duration:.2f}s")
    
    async def record_query(self, question: str, result: Dict[str, Any], duration: float):
        """Record query metrics"""
        self.metrics["queries"]["total_queries"] += 1
        
        if result.get('error'):
            self.metrics["queries"]["failed_queries"] += 1
        else:
            self.metrics["queries"]["successful_queries"] += 1
        
        # Update average response time
        total_queries = self.metrics["queries"]["total_queries"]
        current_avg = self.metrics["queries"]["average_response_time"]
        new_avg = ((current_avg * (total_queries - 1)) + duration) / total_queries
        self.metrics["queries"]["average_response_time"] = new_avg
        
        # Add to query history (keep last 100)
        query_record = {
            "timestamp": datetime.utcnow().isoformat(),
            "question_hash": hash(question),
            "duration": duration,
            "mode": result.get('mode', 'unknown'),
            "success": not result.get('error')
        }
        
        self.metrics["queries"]["query_history"].append(query_record)
        if len(self.metrics["queries"]["query_history"]) > 100:
            self.metrics["queries"]["query_history"] = self.metrics["queries"]["query_history"][-100:]
        
        await self._save_metrics()
    
    async def record_processing_progress(self, processed: int, total: int):
        """Record document processing progress"""
        progress_record = {
            "timestamp": datetime.utcnow().isoformat(),
            "processed": processed,
            "total": total,
            "progress_percentage": (processed / total) * 100 if total > 0 else 0
        }
        
        # Keep only recent progress records
        if "progress_history" not in self.metrics["processing"]:
            self.metrics["processing"]["progress_history"] = []
        
        self.metrics["processing"]["progress_history"].append(progress_record)
        if len(self.metrics["processing"]["progress_history"]) > 50:
            self.metrics["processing"]["progress_history"] = self.metrics["processing"]["progress_history"][-50:]
        
        await self._save_metrics()
    
    async def record_corpus_processing(self, results: Dict[str, Any]):
        """Record document corpus processing results"""
        self.metrics["processing"]["total_documents_processed"] += results["total_documents"]
        self.metrics["processing"]["successful_documents"] += results["successful"]
        self.metrics["processing"]["failed_documents"] += results["failed"]
        
        # Update average processing time
        if results["processing_duration"] > 0:
            processing_record = {
                "timestamp": datetime.utcnow().isoformat(),
                "total_documents": results["total_documents"],
                "successful": results["successful"],
                "failed": results["failed"],
                "duration": results["processing_duration"],
                "documents_per_second": results["documents_per_second"]
            }
            
            self.metrics["processing"]["processing_history"].append(processing_record)
            if len(self.metrics["processing"]["processing_history"]) > 20:
                self.metrics["processing"]["processing_history"] = self.metrics["processing"]["processing_history"][-20:]
        
        await self._save_metrics()
    
    async def record_error(self, error_type: str, error_message: str):
        """Record error metrics"""
        self.metrics["errors"]["total_errors"] += 1
        
        # Count error types
        if error_type not in self.metrics["errors"]["error_types"]:
            self.metrics["errors"]["error_types"][error_type] = 0
        self.metrics["errors"]["error_types"][error_type] += 1
        
        # Add to recent errors (keep last 50)
        error_record = {
            "timestamp": datetime.utcnow().isoformat(),
            "type": error_type,
            "message": error_message[:500]  # Truncate long messages
        }
        
        self.metrics["errors"]["recent_errors"].append(error_record)
        if len(self.metrics["errors"]["recent_errors"]) > 50:
            self.metrics["errors"]["recent_errors"] = self.metrics["errors"]["recent_errors"][-50:]
        
        await self._save_metrics()
        self.logger.warning(f"Recorded error: {error_type} - {error_message}")
    
    async def record_performance_metrics(self):
        """Record system performance metrics"""
        try:
            import psutil
            
            # Memory usage
            memory = psutil.virtual_memory()
            memory_record = {
                "timestamp": datetime.utcnow().isoformat(),
                "total": memory.total,
                "available": memory.available,
                "percent": memory.percent,
                "used": memory.used
            }
            
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_record = {
                "timestamp": datetime.utcnow().isoformat(),
                "percent": cpu_percent,
                "count": psutil.cpu_count()
            }
            
            # Disk usage
            disk = psutil.disk_usage(self.config.working_dir)
            disk_record = {
                "timestamp": datetime.utcnow().isoformat(),
                "total": disk.total,
                "used": disk.used,
                "free": disk.free,
                "percent": (disk.used / disk.total) * 100
            }
            
            # Add to performance metrics (keep last 100 records)
            self.metrics["performance"]["memory_usage"].append(memory_record)
            self.metrics["performance"]["cpu_usage"].append(cpu_record)
            self.metrics["performance"]["disk_usage"].append(disk_record)
            
            for metric_type in ["memory_usage", "cpu_usage", "disk_usage"]:
                if len(self.metrics["performance"][metric_type]) > 100:
                    self.metrics["performance"][metric_type] = self.metrics["performance"][metric_type][-100:]
            
            await self._save_metrics()
            
        except ImportError:
            self.logger.warning("psutil not available for performance monitoring")
        except Exception as e:
            self.logger.error(f"Error recording performance metrics: {str(e)}")
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Get comprehensive metrics report"""
        # Calculate uptime
        current_uptime = (datetime.utcnow() - self.startup_time).total_seconds()
        self.metrics["system"]["current_uptime"] = current_uptime
        
        # Calculate success rates
        total_queries = self.metrics["queries"]["total_queries"]
        if total_queries > 0:
            success_rate = (self.metrics["queries"]["successful_queries"] / total_queries) * 100
            self.metrics["queries"]["success_rate"] = success_rate
        
        total_docs = self.metrics["processing"]["total_documents_processed"]
        if total_docs > 0:
            processing_success_rate = (self.metrics["processing"]["successful_documents"] / total_docs) * 100
            self.metrics["processing"]["success_rate"] = processing_success_rate
        
        # Add summary statistics
        summary = {
            "system_health": "healthy" if self.metrics["errors"]["total_errors"] < 10 else "degraded",
            "uptime_hours": current_uptime / 3600,
            "query_success_rate": self.metrics["queries"].get("success_rate", 0),
            "processing_success_rate": self.metrics["processing"].get("success_rate", 0),
            "average_query_time": self.metrics["queries"]["average_response_time"],
            "total_errors": self.metrics["errors"]["total_errors"]
        }
        
        return {
            "summary": summary,
            "detailed_metrics": self.metrics,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check for metrics system"""
        try:
            # Check if metrics file is writable
            test_file = f"{self.config.working_dir}/metrics/test_write.tmp"
            Path(test_file).parent.mkdir(parents=True, exist_ok=True)
            
            with open(test_file, 'w') as f:
                f.write("test")
            
            Path(test_file).unlink()
            
            return {
                "status": "healthy",
                "metrics_file": self.metrics_file,
                "total_queries": self.metrics["queries"]["total_queries"],
                "total_errors": self.metrics["errors"]["total_errors"]
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            }
    
    async def cleanup(self):
        """Clean up metrics collector"""
        try:
            # Save final metrics
            await self._save_metrics()
            self.logger.info("Metrics collector cleanup completed")
        except Exception as e:
            self.logger.error(f"Error during metrics cleanup: {str(e)}")


async def start_performance_monitoring(metrics_collector: MetricsCollector, interval: int = 60):
    """Start background performance monitoring"""
    while True:
        try:
            await metrics_collector.record_performance_metrics()
            await asyncio.sleep(interval)
        except Exception as e:
            logging.getLogger(__name__).error(f"Performance monitoring error: {str(e)}")
            await asyncio.sleep(interval)