"""
Production RAG-Anything System
Complete production-ready implementation with monitoring, backup, and recovery
"""

from .config.production_config import ProductionConfig, load_production_config
from .core.production_rag_engine import ProductionRAGEngine
from .deployment.production_deployment import ProductionDeployment, deploy_production_system
from .monitoring.metrics_collector import MetricsCollector
from .backup.backup_manager import BackupManager
from .monitoring.dashboards import create_monitoring_setup

__version__ = "1.0.0"
__all__ = [
    "ProductionConfig",
    "load_production_config", 
    "ProductionRAGEngine",
    "ProductionDeployment",
    "deploy_production_system",
    "MetricsCollector",
    "BackupManager",
    "create_monitoring_setup"
]