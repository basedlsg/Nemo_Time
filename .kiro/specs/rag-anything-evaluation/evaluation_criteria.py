#!/usr/bin/env python3
"""
Evaluation criteria and test datasets for RAG-Anything vs Current System comparison.
Extracted from current system testing and pain point analysis.
"""

import json
import time
from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Optional
from enum import Enum


class MetricType(Enum):
    """Types of evaluation metrics"""
    ACCURACY = "accuracy"
    PERFORMANCE = "performance"
    COMPLEXITY = "complexity"
    OPERATIONAL = "operational"


@dataclass
class EvaluationMetric:
    """Definition of an evaluation metric"""
    name: str
    type: MetricType
    description: str
    target_value: float
    measurement_unit: str
    weight: float  # Importance weight (0.0-1.0)
    current_system_baseline: Optional[float] = None


@dataclass
class TestQuery:
    """Test query with expected results"""
    id: str
    province: str
    asset: str
    doc_class: str
    question: str
    expected_keywords: List[str]
    expected_citation_count: int
    complexity_level: str  # "simple", "medium", "complex"
    description: str


@dataclass
class TestDocument:
    """Test document for processing evaluation"""
    id: str
    title: str
    content_type: str  # "text", "table", "formula", "mixed"
    language: str
    size_kb: int
    complexity_features: List[str]  # ["chinese_text", "tables", "formulas", "images"]
    expected_chunks: int
    description: str


@dataclass
class EvaluationResult:
    """Result of a single evaluation test"""
    test_id: str
    system_name: str  # "current" or "rag_anything"
    metric_name: str
    value: float
    timestamp: float
    details: Dict[str, Any]


class EvaluationCriteria:
    """Comprehensive evaluation criteria for RAG-Anything assessment"""
    
    def __init__(self):
        self.accuracy_metrics = self._define_accuracy_metrics()
        self.performance_metrics = self._define_performance_metrics()
        self.complexity_metrics = self._define_complexity_metrics()
        self.operational_metrics = self._define_operational_metrics()
        
        self.golden_query_set = self._create_golden_query_set()
        self.test_documents = self._create_test_document_set()
        
    def _define_accuracy_metrics(self) -> List[EvaluationMetric]:
        """Define accuracy evaluation metrics"""
        return [
            EvaluationMetric(
                name="retrieval_precision_at_5",
                type=MetricType.ACCURACY,
                description="Precision of top 5 retrieved documents for relevance",
                target_value=0.90,
                measurement_unit="ratio",
                weight=0.25,
                current_system_baseline=0.75  # Estimated from golden set tests
            ),
            EvaluationMetric(
                name="chinese_keyword_coverage",
                type=MetricType.ACCURACY,
                description="Coverage of expected Chinese regulatory keywords in responses",
                target_value=0.80,
                measurement_unit="ratio",
                weight=0.20,
                current_system_baseline=0.65
            ),
            EvaluationMetric(
                name="citation_accuracy",
                type=MetricType.ACCURACY,
                description="Accuracy of citations with valid government URLs",
                target_value=0.95,
                measurement_unit="ratio",
                weight=0.20,
                current_system_baseline=0.85
            ),
            EvaluationMetric(
                name="regulatory_terminology_precision",
                type=MetricType.ACCURACY,
                description="Correct usage of Chinese regulatory terminology",
                target_value=0.85,
                measurement_unit="ratio",
                weight=0.15,
                current_system_baseline=0.70
            ),
            EvaluationMetric(
                name="no_hallucination_rate",
                type=MetricType.ACCURACY,
                description="Rate of responses without fabricated information",
                target_value=1.0,
                measurement_unit="ratio",
                weight=0.20,
                current_system_baseline=0.95
            )
        ]
    
    def _define_performance_metrics(self) -> List[EvaluationMetric]:
        """Define performance evaluation metrics"""
        return [
            EvaluationMetric(
                name="response_time_p95",
                type=MetricType.PERFORMANCE,
                description="95th percentile response time for queries",
                target_value=2000.0,
                measurement_unit="milliseconds",
                weight=0.30,
                current_system_baseline=1800.0
            ),
            EvaluationMetric(
                name="document_processing_speed",
                type=MetricType.PERFORMANCE,
                description="Documents processed per minute during ingestion",
                target_value=10.0,
                measurement_unit="docs/minute",
                weight=0.25,
                current_system_baseline=5.0
            ),
            EvaluationMetric(
                name="concurrent_query_capacity",
                type=MetricType.PERFORMANCE,
                description="Maximum concurrent queries without degradation",
                target_value=50.0,
                measurement_unit="queries",
                weight=0.20,
                current_system_baseline=20.0
            ),
            EvaluationMetric(
                name="memory_efficiency",
                type=MetricType.PERFORMANCE,
                description="Memory usage per processed document",
                target_value=50.0,
                measurement_unit="MB/document",
                weight=0.15,
                current_system_baseline=100.0
            ),
            EvaluationMetric(
                name="cold_start_time",
                type=MetricType.PERFORMANCE,
                description="Time to first response after system start",
                target_value=30.0,
                measurement_unit="seconds",
                weight=0.10,
                current_system_baseline=120.0
            )
        ]
    
    def _define_complexity_metrics(self) -> List[EvaluationMetric]:
        """Define deployment and operational complexity metrics"""
        return [
            EvaluationMetric(
                name="deployment_steps_count",
                type=MetricType.COMPLEXITY,
                description="Number of manual steps required for deployment",
                target_value=5.0,
                measurement_unit="steps",
                weight=0.25,
                current_system_baseline=12.0  # From deployment guide analysis
            ),
            EvaluationMetric(
                name="iam_permissions_required",
                type=MetricType.COMPLEXITY,
                description="Number of IAM permissions/roles required",
                target_value=3.0,
                measurement_unit="permissions",
                weight=0.20,
                current_system_baseline=8.0
            ),
            EvaluationMetric(
                name="service_dependencies_count",
                type=MetricType.COMPLEXITY,
                description="Number of external service dependencies",
                target_value=2.0,
                measurement_unit="services",
                weight=0.20,
                current_system_baseline=8.0  # GCF, Vertex AI, Document AI, etc.
            ),
            EvaluationMetric(
                name="configuration_files_count",
                type=MetricType.COMPLEXITY,
                description="Number of configuration files to manage",
                target_value=3.0,
                measurement_unit="files",
                weight=0.15,
                current_system_baseline=7.0
            ),
            EvaluationMetric(
                name="deployment_success_rate",
                type=MetricType.COMPLEXITY,
                description="Success rate of clean deployments without manual intervention",
                target_value=0.95,
                measurement_unit="ratio",
                weight=0.20,
                current_system_baseline=0.60  # Based on error reports
            )
        ]
    
    def _define_operational_metrics(self) -> List[EvaluationMetric]:
        """Define operational overhead metrics"""
        return [
            EvaluationMetric(
                name="monitoring_setup_complexity",
                type=MetricType.OPERATIONAL,
                description="Complexity score for monitoring setup (1-10 scale)",
                target_value=3.0,
                measurement_unit="complexity_score",
                weight=0.25,
                current_system_baseline=8.0
            ),
            EvaluationMetric(
                name="troubleshooting_time_mttr",
                type=MetricType.OPERATIONAL,
                description="Mean time to resolution for common issues",
                target_value=30.0,
                measurement_unit="minutes",
                weight=0.25,
                current_system_baseline=120.0
            ),
            EvaluationMetric(
                name="maintenance_tasks_per_month",
                type=MetricType.OPERATIONAL,
                description="Number of routine maintenance tasks required monthly",
                target_value=2.0,
                measurement_unit="tasks",
                weight=0.20,
                current_system_baseline=8.0
            ),
            EvaluationMetric(
                name="error_message_clarity",
                type=MetricType.OPERATIONAL,
                description="Clarity score of error messages (1-10 scale)",
                target_value=8.0,
                measurement_unit="clarity_score",
                weight=0.15,
                current_system_baseline=4.0
            ),
            EvaluationMetric(
                name="documentation_completeness",
                type=MetricType.OPERATIONAL,
                description="Completeness score of operational documentation (1-10 scale)",
                target_value=9.0,
                measurement_unit="completeness_score",
                weight=0.15,
                current_system_baseline=6.0
            )
        ]
    
    def _create_golden_query_set(self) -> List[TestQuery]:
        """Create golden query set extracted from current system testing"""
        return [
            # Simple queries - basic regulatory information
            TestQuery(
                id="gq_001",
                province="gd",
                asset="solar",
                doc_class="grid",
                question="光伏并网验收需要哪些资料？",
                expected_keywords=["资料", "验收", "并网", "光伏", "申请"],
                expected_citation_count=2,
                complexity_level="simple",
                description="Basic grid connection documentation requirements for solar"
            ),
            TestQuery(
                id="gq_002",
                province="sd",
                asset="wind",
                doc_class="grid",
                question="风电项目并网技术要求",
                expected_keywords=["风电", "技术", "要求", "并网", "标准"],
                expected_citation_count=3,
                complexity_level="simple",
                description="Technical requirements for wind power grid connection"
            ),
            TestQuery(
                id="gq_003",
                province="nm",
                asset="coal",
                doc_class="grid",
                question="煤电并网管理规定",
                expected_keywords=["煤电", "管理", "规定", "并网", "程序"],
                expected_citation_count=2,
                complexity_level="simple",
                description="Coal power grid connection management regulations"
            ),
            
            # Medium complexity queries - specific technical details
            TestQuery(
                id="gq_004",
                province="gd",
                asset="solar",
                doc_class="permit",
                question="分布式光伏发电项目备案需要什么条件和材料？",
                expected_keywords=["分布式", "光伏", "备案", "条件", "材料", "项目"],
                expected_citation_count=4,
                complexity_level="medium",
                description="Distributed solar project registration requirements"
            ),
            TestQuery(
                id="gq_005",
                province="sd",
                asset="wind",
                doc_class="technical",
                question="海上风电场电压等级和保护装置配置要求",
                expected_keywords=["海上", "风电", "电压", "保护", "装置", "配置"],
                expected_citation_count=3,
                complexity_level="medium",
                description="Offshore wind farm voltage and protection requirements"
            ),
            TestQuery(
                id="gq_006",
                province="nm",
                asset="coal",
                doc_class="environmental",
                question="燃煤电厂环保设施验收标准和程序",
                expected_keywords=["燃煤", "环保", "设施", "验收", "标准", "程序"],
                expected_citation_count=5,
                complexity_level="medium",
                description="Coal plant environmental facility acceptance standards"
            ),
            
            # Complex queries - multi-aspect regulatory analysis
            TestQuery(
                id="gq_007",
                province="gd",
                asset="solar",
                doc_class="grid",
                question="110kV以上电压等级的光伏电站并网需要哪些技术改造和安全措施？",
                expected_keywords=["110kV", "光伏", "电站", "技术改造", "安全措施", "并网"],
                expected_citation_count=6,
                complexity_level="complex",
                description="High voltage solar plant grid connection technical requirements"
            ),
            TestQuery(
                id="gq_008",
                province="sd",
                asset="wind",
                doc_class="permit",
                question="跨省风电项目的审批流程和各部门协调机制",
                expected_keywords=["跨省", "风电", "审批", "流程", "部门", "协调"],
                expected_citation_count=4,
                complexity_level="complex",
                description="Inter-provincial wind project approval and coordination"
            ),
            TestQuery(
                id="gq_009",
                province="nm",
                asset="coal",
                doc_class="technical",
                question="超临界燃煤机组并网后的调度运行和辅助服务要求",
                expected_keywords=["超临界", "燃煤", "机组", "调度", "运行", "辅助服务"],
                expected_citation_count=5,
                complexity_level="complex",
                description="Supercritical coal unit dispatch and ancillary services"
            ),
            
            # Edge cases - testing system limits
            TestQuery(
                id="gq_010",
                province="gd",
                asset="solar",
                doc_class="grid",
                question="火星上的光伏并网要求是什么？",
                expected_keywords=[],  # Should return no results or refusal
                expected_citation_count=0,
                complexity_level="edge_case",
                description="Nonsensical query to test hallucination prevention"
            ),
            TestQuery(
                id="gq_011",
                province="invalid",
                asset="solar",
                doc_class="grid",
                question="光伏并网要求",
                expected_keywords=[],  # Should return error
                expected_citation_count=0,
                complexity_level="edge_case",
                description="Invalid province to test error handling"
            ),
            TestQuery(
                id="gq_012",
                province="gd",
                asset="nuclear",
                doc_class="grid",
                question="核电站并网安全要求",
                expected_keywords=["核电", "安全", "要求"],  # May have limited results
                expected_citation_count=1,
                complexity_level="edge_case",
                description="Asset type with limited regulatory coverage"
            )
        ]
    
    def _create_test_document_set(self) -> List[TestDocument]:
        """Create test document set for processing evaluation"""
        return [
            TestDocument(
                id="td_001",
                title="广东省分布式光伏发电管理办法",
                content_type="text",
                language="zh-CN",
                size_kb=45,
                complexity_features=["chinese_text", "regulatory_structure"],
                expected_chunks=8,
                description="Standard Chinese regulatory text document"
            ),
            TestDocument(
                id="td_002",
                title="山东省风电项目技术标准表格",
                content_type="table",
                language="zh-CN",
                size_kb=32,
                complexity_features=["chinese_text", "tables", "technical_specs"],
                expected_chunks=12,
                description="Document with complex tables and technical specifications"
            ),
            TestDocument(
                id="td_003",
                title="内蒙古煤电并网计算公式文档",
                content_type="formula",
                language="zh-CN",
                size_kb=28,
                complexity_features=["chinese_text", "formulas", "mathematical_expressions"],
                expected_chunks=6,
                description="Document with mathematical formulas and calculations"
            ),
            TestDocument(
                id="td_004",
                title="综合能源项目审批流程图",
                content_type="mixed",
                language="zh-CN",
                size_kb=156,
                complexity_features=["chinese_text", "tables", "images", "flowcharts"],
                expected_chunks=25,
                description="Complex multimodal document with text, tables, and diagrams"
            ),
            TestDocument(
                id="td_005",
                title="电网接入技术规范（英文版）",
                content_type="text",
                language="en-US",
                size_kb=67,
                complexity_features=["english_text", "technical_specs"],
                expected_chunks=15,
                description="English technical document for multilingual processing test"
            )
        ]
    
    def get_all_metrics(self) -> List[EvaluationMetric]:
        """Get all evaluation metrics"""
        return (self.accuracy_metrics + 
                self.performance_metrics + 
                self.complexity_metrics + 
                self.operational_metrics)
    
    def calculate_weighted_score(self, results: List[EvaluationResult], 
                               metric_type: Optional[MetricType] = None) -> float:
        """Calculate weighted score for a set of results"""
        metrics = self.get_all_metrics()
        if metric_type:
            metrics = [m for m in metrics if m.type == metric_type]
        
        total_weight = sum(m.weight for m in metrics)
        weighted_sum = 0.0
        
        for result in results:
            metric = next((m for m in metrics if m.name == result.metric_name), None)
            if metric:
                # Normalize score based on target value
                normalized_score = min(result.value / metric.target_value, 1.0)
                weighted_sum += normalized_score * metric.weight
        
        return weighted_sum / total_weight if total_weight > 0 else 0.0
    
    def export_to_json(self, filepath: str):
        """Export evaluation criteria to JSON file"""
        def convert_metric(metric):
            """Convert metric to JSON-serializable dict"""
            metric_dict = asdict(metric)
            metric_dict['type'] = metric.type.value  # Convert enum to string
            return metric_dict
        
        data = {
            "metrics": {
                "accuracy": [convert_metric(m) for m in self.accuracy_metrics],
                "performance": [convert_metric(m) for m in self.performance_metrics],
                "complexity": [convert_metric(m) for m in self.complexity_metrics],
                "operational": [convert_metric(m) for m in self.operational_metrics]
            },
            "golden_queries": [asdict(q) for q in self.golden_query_set],
            "test_documents": [asdict(d) for d in self.test_documents],
            "export_timestamp": time.time()
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)


def main():
    """Generate and export evaluation criteria"""
    criteria = EvaluationCriteria()
    
    print("RAG-Anything Evaluation Criteria")
    print("=" * 50)
    
    print(f"\nAccuracy Metrics: {len(criteria.accuracy_metrics)}")
    for metric in criteria.accuracy_metrics:
        print(f"  - {metric.name}: target {metric.target_value} {metric.measurement_unit}")
    
    print(f"\nPerformance Metrics: {len(criteria.performance_metrics)}")
    for metric in criteria.performance_metrics:
        print(f"  - {metric.name}: target {metric.target_value} {metric.measurement_unit}")
    
    print(f"\nComplexity Metrics: {len(criteria.complexity_metrics)}")
    for metric in criteria.complexity_metrics:
        print(f"  - {metric.name}: target {metric.target_value} {metric.measurement_unit}")
    
    print(f"\nOperational Metrics: {len(criteria.operational_metrics)}")
    for metric in criteria.operational_metrics:
        print(f"  - {metric.name}: target {metric.target_value} {metric.measurement_unit}")
    
    print(f"\nGolden Query Set: {len(criteria.golden_query_set)} queries")
    for query in criteria.golden_query_set:
        print(f"  - {query.id}: {query.question[:50]}... ({query.complexity_level})")
    
    print(f"\nTest Document Set: {len(criteria.test_documents)} documents")
    for doc in criteria.test_documents:
        print(f"  - {doc.id}: {doc.title} ({doc.content_type})")
    
    # Export to JSON
    criteria.export_to_json('.kiro/specs/rag-anything-evaluation/evaluation_criteria.json')
    print(f"\n✅ Exported evaluation criteria to evaluation_criteria.json")


if __name__ == "__main__":
    main()