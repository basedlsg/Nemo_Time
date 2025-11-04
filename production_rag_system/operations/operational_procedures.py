"""
Operational Procedures for Production RAG-Anything System
Comprehensive operational procedures, monitoring, and maintenance
"""

import asyncio
import logging
import json
import yaml
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from pathlib import Path

from ..config.production_config import ProductionConfig
from ..core.production_rag_engine import ProductionRAGEngine
from ..monitoring.metrics_collector import MetricsCollector
from ..backup.backup_manager import BackupManager


class OperationalProcedures:
    """
    Manages operational procedures for production RAG system
    """
    
    def __init__(self, config: ProductionConfig):
        self.config = config
        self.procedures_dir = f"{config.working_dir}/operations"
        self.logger = logging.getLogger(__name__)
        
        # Create operations directory
        Path(self.procedures_dir).mkdir(parents=True, exist_ok=True)
    
    def create_all_procedures(self):
        """Create all operational procedures and documentation"""
        self.logger.info("Creating operational procedures...")
        
        # Create monitoring procedures
        self._create_monitoring_procedures()
        
        # Create maintenance procedures
        self._create_maintenance_procedures()
        
        # Create troubleshooting procedures
        self._create_troubleshooting_procedures()
        
        # Create alerting procedures
        self._create_alerting_procedures()
        
        # Create backup and recovery procedures
        self._create_backup_recovery_procedures()
        
        # Create team training materials
        self._create_training_materials()
        
        self.logger.info("All operational procedures created")
    
    def _create_monitoring_procedures(self):
        """Create monitoring procedures and dashboards"""
        monitoring_procedures = {
            "overview": {
                "purpose": "Monitor production RAG-Anything system health and performance",
                "responsible_team": "Operations Team",
                "escalation_contact": "ops-team@company.com"
            },
            "monitoring_dashboards": {
                "primary_dashboard": {
                    "name": "RAG System Overview",
                    "url": "http://grafana.company.com/d/rag-overview",
                    "refresh_interval": "30s",
                    "key_metrics": [
                        "System Health Status",
                        "Query Response Time",
                        "Query Success Rate",
                        "Document Processing Rate",
                        "Error Rate",
                        "Resource Utilization"
                    ]
                },
                "detailed_dashboards": [
                    {
                        "name": "Performance Metrics",
                        "url": "http://grafana.company.com/d/rag-performance",
                        "focus": "Response times, throughput, resource usage"
                    },
                    {
                        "name": "Error Analysis",
                        "url": "http://grafana.company.com/d/rag-errors",
                        "focus": "Error rates, error types, failure patterns"
                    },
                    {
                        "name": "System Resources",
                        "url": "http://grafana.company.com/d/rag-resources",
                        "focus": "CPU, memory, disk, network utilization"
                    }
                ]
            },
            "monitoring_schedule": {
                "continuous_monitoring": {
                    "automated_alerts": "24/7 automated monitoring with immediate alerts",
                    "dashboard_checks": "Automated dashboard health checks every 5 minutes"
                },
                "manual_checks": {
                    "daily": [
                        "Review overnight alerts and system status",
                        "Check backup completion status",
                        "Verify document processing pipeline health"
                    ],
                    "weekly": [
                        "Review performance trends and capacity planning",
                        "Analyze error patterns and optimization opportunities",
                        "Update monitoring thresholds based on usage patterns"
                    ],
                    "monthly": [
                        "Comprehensive system health review",
                        "Monitoring system maintenance and updates",
                        "Review and update operational procedures"
                    ]
                }
            },
            "key_metrics_thresholds": {
                "system_health": {
                    "healthy": "All components operational",
                    "degraded": "One or more components showing issues",
                    "unhealthy": "Critical components failing"
                },
                "query_response_time": {
                    "good": "< 2 seconds average",
                    "warning": "2-5 seconds average",
                    "critical": "> 5 seconds average"
                },
                "query_success_rate": {
                    "good": "> 99%",
                    "warning": "95-99%",
                    "critical": "< 95%"
                },
                "error_rate": {
                    "good": "< 0.1%",
                    "warning": "0.1-1%",
                    "critical": "> 1%"
                },
                "resource_utilization": {
                    "cpu": {"warning": "> 70%", "critical": "> 90%"},
                    "memory": {"warning": "> 80%", "critical": "> 95%"},
                    "disk": {"warning": "> 80%", "critical": "> 90%"}
                }
            }
        }
        
        # Save monitoring procedures
        procedures_file = f"{self.procedures_dir}/monitoring_procedures.yaml"
        with open(procedures_file, 'w') as f:
            yaml.dump(monitoring_procedures, f, default_flow_style=False)
    
    def _create_maintenance_procedures(self):
        """Create system maintenance procedures"""
        maintenance_procedures = {
            "overview": {
                "purpose": "Ensure optimal performance and reliability of RAG system",
                "maintenance_window": "Sunday 02:00-04:00 UTC",
                "notification_lead_time": "48 hours"
            },
            "routine_maintenance": {
                "daily": {
                    "automated_tasks": [
                        "System health checks",
                        "Automated backups",
                        "Log rotation",
                        "Temporary file cleanup"
                    ],
                    "manual_tasks": [
                        "Review system alerts",
                        "Check backup completion",
                        "Monitor resource usage trends"
                    ]
                },
                "weekly": {
                    "automated_tasks": [
                        "Full system backup",
                        "Performance metrics analysis",
                        "Security scan"
                    ],
                    "manual_tasks": [
                        "Review and analyze performance trends",
                        "Update system documentation",
                        "Check for software updates"
                    ]
                },
                "monthly": {
                    "automated_tasks": [
                        "Comprehensive system audit",
                        "Backup retention cleanup",
                        "Performance optimization analysis"
                    ],
                    "manual_tasks": [
                        "System performance review",
                        "Capacity planning assessment",
                        "Update operational procedures",
                        "Team training updates"
                    ]
                }
            },
            "preventive_maintenance": {
                "system_updates": {
                    "frequency": "Monthly during maintenance window",
                    "procedure": [
                        "Create pre-update backup",
                        "Test updates in staging environment",
                        "Apply updates during maintenance window",
                        "Verify system functionality post-update",
                        "Monitor system for 24 hours post-update"
                    ]
                },
                "performance_optimization": {
                    "frequency": "Quarterly",
                    "activities": [
                        "Analyze query performance patterns",
                        "Optimize document processing pipeline",
                        "Review and tune system parameters",
                        "Update caching strategies",
                        "Optimize resource allocation"
                    ]
                },
                "security_maintenance": {
                    "frequency": "Monthly",
                    "activities": [
                        "Security patch updates",
                        "Access control review",
                        "API key rotation",
                        "Security audit",
                        "Vulnerability assessment"
                    ]
                }
            },
            "emergency_maintenance": {
                "triggers": [
                    "Critical security vulnerability",
                    "System performance degradation > 50%",
                    "Data corruption detected",
                    "Hardware failure"
                ],
                "procedure": [
                    "Assess severity and impact",
                    "Notify stakeholders immediately",
                    "Create emergency backup if possible",
                    "Implement fix or workaround",
                    "Verify system functionality",
                    "Document incident and resolution"
                ]
            }
        }
        
        # Save maintenance procedures
        procedures_file = f"{self.procedures_dir}/maintenance_procedures.yaml"
        with open(procedures_file, 'w') as f:
            yaml.dump(maintenance_procedures, f, default_flow_style=False)
    
    def _create_troubleshooting_procedures(self):
        """Create troubleshooting procedures and runbooks"""
        troubleshooting_procedures = {
            "overview": {
                "purpose": "Systematic approach to diagnosing and resolving system issues",
                "escalation_levels": [
                    "Level 1: Operations Team (immediate response)",
                    "Level 2: Engineering Team (within 2 hours)",
                    "Level 3: Senior Engineering/Architecture (within 4 hours)"
                ]
            },
            "common_issues": {
                "high_query_latency": {
                    "symptoms": [
                        "Query response time > 5 seconds",
                        "User complaints about slow responses",
                        "Dashboard showing latency alerts"
                    ],
                    "diagnosis_steps": [
                        "Check system resource utilization (CPU, memory, disk)",
                        "Review recent query patterns and volume",
                        "Check RAG system component health",
                        "Analyze slow query logs",
                        "Verify external API connectivity (OpenAI, etc.)"
                    ],
                    "resolution_steps": [
                        "Restart RAG engine if resource issues detected",
                        "Scale up resources if utilization is high",
                        "Optimize query processing if pattern issues found",
                        "Clear caches and restart services",
                        "Escalate to Level 2 if issue persists"
                    ]
                },
                "query_failures": {
                    "symptoms": [
                        "Query success rate < 95%",
                        "Error responses from query endpoint",
                        "Exception logs in system"
                    ],
                    "diagnosis_steps": [
                        "Check error logs for specific error messages",
                        "Verify RAG system initialization status",
                        "Test document corpus accessibility",
                        "Check API key validity and quotas",
                        "Verify network connectivity"
                    ],
                    "resolution_steps": [
                        "Restart RAG engine if initialization issues",
                        "Restore from backup if data corruption suspected",
                        "Update API keys if authentication issues",
                        "Fix network connectivity issues",
                        "Escalate if underlying system issues"
                    ]
                },
                "system_unavailable": {
                    "symptoms": [
                        "Health check endpoints returning errors",
                        "Complete system unresponsiveness",
                        "All queries failing"
                    ],
                    "diagnosis_steps": [
                        "Check system process status",
                        "Verify system resources availability",
                        "Check for recent deployments or changes",
                        "Review system logs for crash information",
                        "Verify infrastructure status"
                    ],
                    "resolution_steps": [
                        "Restart system services",
                        "Restore from recent backup if needed",
                        "Rollback recent changes if applicable",
                        "Scale up infrastructure if resource issues",
                        "Implement emergency procedures if critical"
                    ]
                },
                "backup_failures": {
                    "symptoms": [
                        "Backup completion alerts not received",
                        "Backup verification failures",
                        "Storage space issues"
                    ],
                    "diagnosis_steps": [
                        "Check backup system logs",
                        "Verify backup storage accessibility",
                        "Check available storage space",
                        "Test backup system functionality"
                    ],
                    "resolution_steps": [
                        "Clear old backups if storage full",
                        "Fix backup system configuration issues",
                        "Manually trigger backup if needed",
                        "Escalate if backup system failure"
                    ]
                }
            },
            "diagnostic_tools": {
                "system_health_check": {
                    "command": "python -m production_rag_system.main health",
                    "purpose": "Get comprehensive system health status"
                },
                "system_metrics": {
                    "command": "python -m production_rag_system.main metrics",
                    "purpose": "Get detailed system performance metrics"
                },
                "log_analysis": {
                    "locations": [
                        f"{self.config.working_dir}/logs/rag_engine.log",
                        f"{self.config.working_dir}/logs/metrics.log",
                        f"{self.config.working_dir}/logs/backup.log"
                    ],
                    "tools": ["grep", "tail", "less"]
                }
            },
            "escalation_procedures": {
                "level_1_criteria": [
                    "System performance degradation < 25%",
                    "Non-critical component failures",
                    "Routine operational issues"
                ],
                "level_2_criteria": [
                    "System performance degradation 25-50%",
                    "Query success rate < 95%",
                    "Critical component failures"
                ],
                "level_3_criteria": [
                    "System performance degradation > 50%",
                    "Complete system unavailability",
                    "Data corruption or loss",
                    "Security incidents"
                ]
            }
        }
        
        # Save troubleshooting procedures
        procedures_file = f"{self.procedures_dir}/troubleshooting_procedures.yaml"
        with open(procedures_file, 'w') as f:
            yaml.dump(troubleshooting_procedures, f, default_flow_style=False)
    
    def _create_alerting_procedures(self):
        """Create alerting and notification procedures"""
        alerting_procedures = {
            "overview": {
                "purpose": "Ensure timely notification and response to system issues",
                "notification_channels": [
                    "Email: ops-team@company.com",
                    "Slack: #rag-alerts",
                    "PagerDuty: RAG System Incidents"
                ]
            },
            "alert_severity_levels": {
                "critical": {
                    "description": "System down or major functionality impaired",
                    "response_time": "Immediate (< 15 minutes)",
                    "notification": "PagerDuty + Slack + Email",
                    "examples": [
                        "System health status = unhealthy",
                        "Query success rate < 90%",
                        "Complete system unavailability"
                    ]
                },
                "warning": {
                    "description": "Performance degradation or minor issues",
                    "response_time": "Within 1 hour",
                    "notification": "Slack + Email",
                    "examples": [
                        "Query response time > 5 seconds",
                        "Resource utilization > 80%",
                        "Backup failures"
                    ]
                },
                "info": {
                    "description": "Informational alerts and status updates",
                    "response_time": "Next business day",
                    "notification": "Email only",
                    "examples": [
                        "Scheduled maintenance notifications",
                        "System performance reports",
                        "Capacity planning alerts"
                    ]
                }
            },
            "alert_response_procedures": {
                "immediate_response": [
                    "Acknowledge alert within 15 minutes",
                    "Assess severity and impact",
                    "Begin initial diagnosis",
                    "Notify team lead if critical"
                ],
                "investigation": [
                    "Follow troubleshooting procedures",
                    "Document findings and actions taken",
                    "Escalate if resolution not found within SLA",
                    "Keep stakeholders updated on progress"
                ],
                "resolution": [
                    "Implement fix or workaround",
                    "Verify system functionality restored",
                    "Monitor system for stability",
                    "Document resolution and lessons learned"
                ]
            },
            "alert_configuration": {
                "system_health_alerts": {
                    "metric": "rag_system_health_status",
                    "threshold": "< 1 (unhealthy)",
                    "duration": "5 minutes",
                    "severity": "critical"
                },
                "query_latency_alerts": {
                    "metric": "avg_query_response_time",
                    "threshold": "> 5 seconds",
                    "duration": "10 minutes",
                    "severity": "warning"
                },
                "error_rate_alerts": {
                    "metric": "query_error_rate",
                    "threshold": "> 5%",
                    "duration": "5 minutes",
                    "severity": "warning"
                },
                "resource_alerts": {
                    "cpu_usage": {"threshold": "> 90%", "duration": "10 minutes", "severity": "warning"},
                    "memory_usage": {"threshold": "> 95%", "duration": "5 minutes", "severity": "critical"},
                    "disk_usage": {"threshold": "> 90%", "duration": "30 minutes", "severity": "warning"}
                }
            }
        }
        
        # Save alerting procedures
        procedures_file = f"{self.procedures_dir}/alerting_procedures.yaml"
        with open(procedures_file, 'w') as f:
            yaml.dump(alerting_procedures, f, default_flow_style=False)
    
    def _create_backup_recovery_procedures(self):
        """Create backup and recovery procedures"""
        backup_recovery_procedures = {
            "overview": {
                "purpose": "Ensure data protection and system recovery capabilities",
                "backup_schedule": {
                    "automated_daily": "02:00 UTC daily",
                    "automated_weekly": "Sunday 01:00 UTC",
                    "manual_on_demand": "Before major changes or deployments"
                },
                "retention_policy": {
                    "daily_backups": "30 days",
                    "weekly_backups": "12 weeks",
                    "monthly_backups": "12 months"
                }
            },
            "backup_procedures": {
                "automated_backup": {
                    "schedule": "Daily at 02:00 UTC",
                    "components": [
                        "RAG system storage",
                        "Configuration files",
                        "System logs",
                        "Metrics data"
                    ],
                    "verification": [
                        "Backup completion notification",
                        "Backup integrity check",
                        "Size validation",
                        "Restore test (weekly)"
                    ]
                },
                "manual_backup": {
                    "command": "python -m production_rag_system.main backup",
                    "when_to_use": [
                        "Before system updates",
                        "Before configuration changes",
                        "Before major deployments",
                        "Emergency situations"
                    ],
                    "verification_steps": [
                        "Confirm backup completion",
                        "Verify backup size and contents",
                        "Test backup accessibility"
                    ]
                }
            },
            "recovery_procedures": {
                "full_system_recovery": {
                    "when_needed": [
                        "Complete system failure",
                        "Data corruption",
                        "Hardware failure",
                        "Disaster recovery"
                    ],
                    "steps": [
                        "Assess damage and determine recovery scope",
                        "Identify most recent valid backup",
                        "Prepare recovery environment",
                        "Execute backup restoration",
                        "Verify system functionality",
                        "Resume normal operations"
                    ],
                    "command": "python -m production_rag_system.main restore --backup-id <backup_id>",
                    "estimated_time": "2-4 hours depending on data size"
                },
                "partial_recovery": {
                    "when_needed": [
                        "Configuration corruption",
                        "Specific component failure",
                        "Data inconsistency"
                    ],
                    "steps": [
                        "Identify affected components",
                        "Create current state backup",
                        "Restore specific components from backup",
                        "Verify component functionality",
                        "Test system integration"
                    ]
                }
            },
            "disaster_recovery": {
                "rto_target": "4 hours (Recovery Time Objective)",
                "rpo_target": "24 hours (Recovery Point Objective)",
                "disaster_scenarios": [
                    "Data center outage",
                    "Regional service disruption",
                    "Complete infrastructure failure"
                ],
                "recovery_sites": {
                    "primary": "asia-east2 (Hong Kong)",
                    "secondary": "us-central1 (Iowa)",
                    "backup_storage": "Multi-region GCS buckets"
                },
                "activation_criteria": [
                    "Primary site unavailable > 2 hours",
                    "Data corruption affecting > 50% of system",
                    "Security incident requiring system isolation"
                ]
            }
        }
        
        # Save backup and recovery procedures
        procedures_file = f"{self.procedures_dir}/backup_recovery_procedures.yaml"
        with open(procedures_file, 'w') as f:
            yaml.dump(backup_recovery_procedures, f, default_flow_style=False)
    
    def _create_training_materials(self):
        """Create team training materials"""
        training_materials = {
            "overview": {
                "purpose": "Ensure team members are trained on RAG system operations",
                "training_schedule": {
                    "initial_training": "Before system deployment",
                    "refresher_training": "Quarterly",
                    "update_training": "After major system changes"
                }
            },
            "training_modules": {
                "system_overview": {
                    "duration": "2 hours",
                    "topics": [
                        "RAG-Anything architecture and components",
                        "System capabilities and limitations",
                        "Integration with current infrastructure",
                        "Performance characteristics"
                    ],
                    "materials": [
                        "System architecture diagrams",
                        "Component interaction flows",
                        "Performance benchmarks"
                    ]
                },
                "monitoring_and_alerting": {
                    "duration": "3 hours",
                    "topics": [
                        "Monitoring dashboard navigation",
                        "Key metrics interpretation",
                        "Alert response procedures",
                        "Escalation protocols"
                    ],
                    "hands_on_exercises": [
                        "Dashboard navigation practice",
                        "Alert simulation and response",
                        "Metric analysis scenarios"
                    ]
                },
                "troubleshooting": {
                    "duration": "4 hours",
                    "topics": [
                        "Common issues and symptoms",
                        "Diagnostic tools and techniques",
                        "Resolution procedures",
                        "When to escalate"
                    ],
                    "practical_scenarios": [
                        "High latency troubleshooting",
                        "Query failure diagnosis",
                        "System unavailability response",
                        "Backup failure resolution"
                    ]
                },
                "maintenance_procedures": {
                    "duration": "2 hours",
                    "topics": [
                        "Routine maintenance tasks",
                        "System update procedures",
                        "Backup and recovery operations",
                        "Performance optimization"
                    ],
                    "hands_on_practice": [
                        "Manual backup creation",
                        "System health checks",
                        "Log analysis",
                        "Configuration updates"
                    ]
                }
            },
            "certification_requirements": {
                "level_1_operator": {
                    "requirements": [
                        "Complete system overview training",
                        "Pass monitoring and alerting assessment",
                        "Demonstrate basic troubleshooting skills"
                    ],
                    "responsibilities": [
                        "Monitor system dashboards",
                        "Respond to Level 1 alerts",
                        "Perform routine maintenance tasks"
                    ]
                },
                "level_2_specialist": {
                    "requirements": [
                        "Level 1 certification",
                        "Complete troubleshooting training",
                        "Pass advanced scenarios assessment"
                    ],
                    "responsibilities": [
                        "Handle Level 2 escalations",
                        "Perform system diagnostics",
                        "Execute recovery procedures"
                    ]
                }
            },
            "reference_materials": {
                "quick_reference_guides": [
                    "Common commands cheat sheet",
                    "Alert response flowchart",
                    "Troubleshooting decision tree"
                ],
                "detailed_documentation": [
                    "System architecture documentation",
                    "API reference guide",
                    "Configuration management guide"
                ],
                "contact_information": {
                    "operations_team": "ops-team@company.com",
                    "engineering_team": "eng-team@company.com",
                    "emergency_contact": "+1-555-0123"
                }
            }
        }
        
        # Save training materials
        procedures_file = f"{self.procedures_dir}/training_materials.yaml"
        with open(procedures_file, 'w') as f:
            yaml.dump(training_materials, f, default_flow_style=False)


async def setup_operational_procedures(config: ProductionConfig) -> OperationalProcedures:
    """
    Setup complete operational procedures for production system
    
    Args:
        config: Production configuration
        
    Returns:
        OperationalProcedures instance
    """
    procedures = OperationalProcedures(config)
    procedures.create_all_procedures()
    
    return procedures