"""
Production Monitoring Dashboards
Creates monitoring dashboards and alerting for RAG-Anything system
"""

import json
import yaml
from typing import Dict, Any, List
from pathlib import Path

from ..config.production_config import ProductionConfig


class MonitoringDashboards:
    """
    Creates and manages monitoring dashboards for production system
    """
    
    def __init__(self, config: ProductionConfig):
        self.config = config
        self.dashboards_dir = f"{config.working_dir}/monitoring"
        
    def create_all_dashboards(self):
        """Create all monitoring dashboards and configurations"""
        Path(self.dashboards_dir).mkdir(parents=True, exist_ok=True)
        
        # Create Grafana dashboard
        self._create_grafana_dashboard()
        
        # Create alerting rules
        self._create_alerting_rules()
        
        # Create Cloud Monitoring policies
        self._create_cloud_monitoring_policies()
        
        # Create health check configuration
        self._create_health_check_config()
    
    def _create_grafana_dashboard(self):
        """Create Grafana dashboard configuration"""
        dashboard = {
            "dashboard": {
                "id": None,
                "title": "RAG-Anything Production System",
                "tags": ["rag", "production", "nemo"],
                "timezone": "UTC",
                "panels": [
                    {
                        "id": 1,
                        "title": "System Health",
                        "type": "stat",
                        "targets": [
                            {
                                "expr": "rag_system_health_status",
                                "legendFormat": "System Status"
                            }
                        ],
                        "fieldConfig": {
                            "defaults": {
                                "color": {
                                    "mode": "thresholds"
                                },
                                "thresholds": {
                                    "steps": [
                                        {"color": "red", "value": 0},
                                        {"color": "yellow", "value": 1},
                                        {"color": "green", "value": 2}
                                    ]
                                }
                            }
                        },
                        "gridPos": {"h": 8, "w": 12, "x": 0, "y": 0}
                    },
                    {
                        "id": 2,
                        "title": "Query Response Time",
                        "type": "graph",
                        "targets": [
                            {
                                "expr": "rate(rag_query_duration_seconds_sum[5m]) / rate(rag_query_duration_seconds_count[5m])",
                                "legendFormat": "Average Response Time"
                            }
                        ],
                        "yAxes": [
                            {
                                "label": "Seconds",
                                "min": 0
                            }
                        ],
                        "gridPos": {"h": 8, "w": 12, "x": 12, "y": 0}
                    },
                    {
                        "id": 3,
                        "title": "Query Success Rate",
                        "type": "graph",
                        "targets": [
                            {
                                "expr": "rate(rag_queries_successful_total[5m]) / rate(rag_queries_total[5m]) * 100",
                                "legendFormat": "Success Rate %"
                            }
                        ],
                        "yAxes": [
                            {
                                "label": "Percentage",
                                "min": 0,
                                "max": 100
                            }
                        ],
                        "gridPos": {"h": 8, "w": 12, "x": 0, "y": 8}
                    },
                    {
                        "id": 4,
                        "title": "Document Processing Rate",
                        "type": "graph",
                        "targets": [
                            {
                                "expr": "rate(rag_documents_processed_total[5m])",
                                "legendFormat": "Documents/sec"
                            }
                        ],
                        "yAxes": [
                            {
                                "label": "Documents per second",
                                "min": 0
                            }
                        ],
                        "gridPos": {"h": 8, "w": 12, "x": 12, "y": 8}
                    },
                    {
                        "id": 5,
                        "title": "System Resources",
                        "type": "graph",
                        "targets": [
                            {
                                "expr": "rag_memory_usage_percent",
                                "legendFormat": "Memory Usage %"
                            },
                            {
                                "expr": "rag_cpu_usage_percent",
                                "legendFormat": "CPU Usage %"
                            },
                            {
                                "expr": "rag_disk_usage_percent",
                                "legendFormat": "Disk Usage %"
                            }
                        ],
                        "yAxes": [
                            {
                                "label": "Percentage",
                                "min": 0,
                                "max": 100
                            }
                        ],
                        "gridPos": {"h": 8, "w": 24, "x": 0, "y": 16}
                    },
                    {
                        "id": 6,
                        "title": "Error Rate",
                        "type": "graph",
                        "targets": [
                            {
                                "expr": "rate(rag_errors_total[5m])",
                                "legendFormat": "Errors/sec"
                            }
                        ],
                        "yAxes": [
                            {
                                "label": "Errors per second",
                                "min": 0
                            }
                        ],
                        "gridPos": {"h": 8, "w": 12, "x": 0, "y": 24}
                    },
                    {
                        "id": 7,
                        "title": "Backup Status",
                        "type": "table",
                        "targets": [
                            {
                                "expr": "rag_backup_last_success_timestamp",
                                "legendFormat": "Last Backup"
                            }
                        ],
                        "gridPos": {"h": 8, "w": 12, "x": 12, "y": 24}
                    }
                ],
                "time": {
                    "from": "now-1h",
                    "to": "now"
                },
                "refresh": "30s"
            }
        }
        
        dashboard_file = f"{self.dashboards_dir}/grafana_dashboard.json"
        with open(dashboard_file, 'w') as f:
            json.dump(dashboard, f, indent=2)
    
    def _create_alerting_rules(self):
        """Create Prometheus alerting rules"""
        alerting_rules = {
            "groups": [
                {
                    "name": "rag_system_alerts",
                    "rules": [
                        {
                            "alert": "RAGSystemDown",
                            "expr": "rag_system_health_status == 0",
                            "for": "5m",
                            "labels": {
                                "severity": "critical"
                            },
                            "annotations": {
                                "summary": "RAG-Anything system is down",
                                "description": "The RAG-Anything system has been unhealthy for more than 5 minutes"
                            }
                        },
                        {
                            "alert": "HighQueryLatency",
                            "expr": "rate(rag_query_duration_seconds_sum[5m]) / rate(rag_query_duration_seconds_count[5m]) > 10",
                            "for": "10m",
                            "labels": {
                                "severity": "warning"
                            },
                            "annotations": {
                                "summary": "High query response time",
                                "description": "Average query response time is above 10 seconds for more than 10 minutes"
                            }
                        },
                        {
                            "alert": "LowQuerySuccessRate",
                            "expr": "rate(rag_queries_successful_total[5m]) / rate(rag_queries_total[5m]) < 0.95",
                            "for": "15m",
                            "labels": {
                                "severity": "warning"
                            },
                            "annotations": {
                                "summary": "Low query success rate",
                                "description": "Query success rate is below 95% for more than 15 minutes"
                            }
                        },
                        {
                            "alert": "HighErrorRate",
                            "expr": "rate(rag_errors_total[5m]) > 1",
                            "for": "5m",
                            "labels": {
                                "severity": "warning"
                            },
                            "annotations": {
                                "summary": "High error rate",
                                "description": "Error rate is above 1 error per second for more than 5 minutes"
                            }
                        },
                        {
                            "alert": "HighMemoryUsage",
                            "expr": "rag_memory_usage_percent > 90",
                            "for": "10m",
                            "labels": {
                                "severity": "warning"
                            },
                            "annotations": {
                                "summary": "High memory usage",
                                "description": "Memory usage is above 90% for more than 10 minutes"
                            }
                        },
                        {
                            "alert": "HighDiskUsage",
                            "expr": "rag_disk_usage_percent > 85",
                            "for": "30m",
                            "labels": {
                                "severity": "warning"
                            },
                            "annotations": {
                                "summary": "High disk usage",
                                "description": "Disk usage is above 85% for more than 30 minutes"
                            }
                        },
                        {
                            "alert": "BackupFailed",
                            "expr": "time() - rag_backup_last_success_timestamp > 86400 * 2",
                            "for": "1h",
                            "labels": {
                                "severity": "warning"
                            },
                            "annotations": {
                                "summary": "Backup system failure",
                                "description": "No successful backup in the last 2 days"
                            }
                        }
                    ]
                }
            ]
        }
        
        rules_file = f"{self.dashboards_dir}/alerting_rules.yml"
        with open(rules_file, 'w') as f:
            yaml.dump(alerting_rules, f, default_flow_style=False)
    
    def _create_cloud_monitoring_policies(self):
        """Create Google Cloud Monitoring alerting policies"""
        policies = [
            {
                "displayName": "RAG System Health Check",
                "documentation": {
                    "content": "Alert when RAG-Anything system health check fails"
                },
                "conditions": [
                    {
                        "displayName": "Health check failure",
                        "conditionThreshold": {
                            "filter": f'resource.type="gce_instance" AND metric.type="custom.googleapis.com/rag/health_status"',
                            "comparison": "COMPARISON_LESS_THAN",
                            "thresholdValue": 1,
                            "duration": "300s"
                        }
                    }
                ],
                "alertStrategy": {
                    "autoClose": "1800s"
                },
                "combiner": "OR",
                "enabled": True,
                "notificationChannels": []
            },
            {
                "displayName": "RAG Query Latency",
                "documentation": {
                    "content": "Alert when query response time is too high"
                },
                "conditions": [
                    {
                        "displayName": "High query latency",
                        "conditionThreshold": {
                            "filter": f'resource.type="gce_instance" AND metric.type="custom.googleapis.com/rag/query_duration"',
                            "comparison": "COMPARISON_GREATER_THAN",
                            "thresholdValue": 10,
                            "duration": "600s",
                            "aggregations": [
                                {
                                    "alignmentPeriod": "300s",
                                    "perSeriesAligner": "ALIGN_MEAN"
                                }
                            ]
                        }
                    }
                ],
                "alertStrategy": {
                    "autoClose": "1800s"
                },
                "combiner": "OR",
                "enabled": True,
                "notificationChannels": []
            }
        ]
        
        policies_file = f"{self.dashboards_dir}/cloud_monitoring_policies.json"
        with open(policies_file, 'w') as f:
            json.dump(policies, f, indent=2)
    
    def _create_health_check_config(self):
        """Create health check configuration"""
        health_check_config = {
            "health_checks": [
                {
                    "name": "rag_system_health",
                    "endpoint": f"http://localhost:{self.config.health_check_port}/health",
                    "interval": "30s",
                    "timeout": "10s",
                    "healthy_threshold": 2,
                    "unhealthy_threshold": 3
                },
                {
                    "name": "rag_metrics_endpoint",
                    "endpoint": f"http://localhost:{self.config.metrics_port}/metrics",
                    "interval": "60s",
                    "timeout": "15s",
                    "healthy_threshold": 2,
                    "unhealthy_threshold": 3
                }
            ],
            "notification_channels": [
                {
                    "type": "email",
                    "config": {
                        "recipients": ["ops-team@company.com"],
                        "subject_template": "RAG System Alert: {{.AlertName}}"
                    }
                },
                {
                    "type": "slack",
                    "config": {
                        "webhook_url": "https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK",
                        "channel": "#rag-alerts"
                    }
                }
            ]
        }
        
        health_config_file = f"{self.dashboards_dir}/health_check_config.yml"
        with open(health_config_file, 'w') as f:
            yaml.dump(health_check_config, f, default_flow_style=False)
    
    def create_kubernetes_monitoring(self):
        """Create Kubernetes monitoring configuration"""
        k8s_monitoring = {
            "apiVersion": "v1",
            "kind": "ConfigMap",
            "metadata": {
                "name": "rag-monitoring-config",
                "namespace": "default"
            },
            "data": {
                "prometheus.yml": yaml.dump({
                    "global": {
                        "scrape_interval": "15s"
                    },
                    "scrape_configs": [
                        {
                            "job_name": "rag-system",
                            "static_configs": [
                                {
                                    "targets": [f"rag-system:{self.config.metrics_port}"]
                                }
                            ],
                            "scrape_interval": "30s",
                            "metrics_path": "/metrics"
                        }
                    ]
                })
            }
        }
        
        k8s_file = f"{self.dashboards_dir}/kubernetes_monitoring.yml"
        with open(k8s_file, 'w') as f:
            yaml.dump(k8s_monitoring, f, default_flow_style=False)
    
    def create_docker_compose_monitoring(self):
        """Create Docker Compose monitoring stack"""
        docker_compose = {
            "version": "3.8",
            "services": {
                "prometheus": {
                    "image": "prom/prometheus:latest",
                    "ports": ["9090:9090"],
                    "volumes": [
                        "./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml",
                        "./monitoring/alerting_rules.yml:/etc/prometheus/alerting_rules.yml"
                    ],
                    "command": [
                        "--config.file=/etc/prometheus/prometheus.yml",
                        "--storage.tsdb.path=/prometheus",
                        "--web.console.libraries=/etc/prometheus/console_libraries",
                        "--web.console.templates=/etc/prometheus/consoles",
                        "--web.enable-lifecycle"
                    ]
                },
                "grafana": {
                    "image": "grafana/grafana:latest",
                    "ports": ["3000:3000"],
                    "environment": {
                        "GF_SECURITY_ADMIN_PASSWORD": "admin"
                    },
                    "volumes": [
                        "grafana-storage:/var/lib/grafana",
                        "./monitoring/grafana_dashboard.json:/var/lib/grafana/dashboards/rag_dashboard.json"
                    ]
                },
                "alertmanager": {
                    "image": "prom/alertmanager:latest",
                    "ports": ["9093:9093"],
                    "volumes": [
                        "./monitoring/alertmanager.yml:/etc/alertmanager/alertmanager.yml"
                    ]
                }
            },
            "volumes": {
                "grafana-storage": {}
            }
        }
        
        compose_file = f"{self.dashboards_dir}/docker-compose.monitoring.yml"
        with open(compose_file, 'w') as f:
            yaml.dump(docker_compose, f, default_flow_style=False)


def create_monitoring_setup(config: ProductionConfig):
    """Create complete monitoring setup"""
    dashboards = MonitoringDashboards(config)
    
    # Create all monitoring components
    dashboards.create_all_dashboards()
    dashboards.create_kubernetes_monitoring()
    dashboards.create_docker_compose_monitoring()
    
    return dashboards