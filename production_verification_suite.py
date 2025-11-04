"""
Comprehensive Production Verification Suite
Tests the complete RAG-Anything production system with 20 diverse queries
Includes Perplexity integration testing and accuracy scoring
"""

import asyncio
import time
import json
import logging
from typing import Dict, Any, List, Tuple
from datetime import datetime
from pathlib import Path
import statistics

# Import production system components
from production_rag_system.config.production_config import ProductionConfig, load_production_config
from production_rag_system.core.production_rag_engine import ProductionRAGEngine
from production_rag_system.deployment.production_deployment import ProductionDeployment

# Import current system components for comparison
from lib.composer import compose_response
from lib.sanitize import normalize_query
from lib.cse import discover_documents


class ProductionVerificationSuite:
    """
    Comprehensive verification suite for production RAG system
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.results_dir = Path("verification_results")
        self.results_dir.mkdir(exist_ok=True)
        
        # Test queries covering different categories and complexity levels
        self.test_queries = [
            {
                "id": "solar_basic_filing",
                "query": "分布式光伏发电项目如何备案？",
                "category": "solar_regulations",
                "complexity": "basic",
                "expected_topics": ["备案", "分布式光伏", "申请流程"],
                "province": "gd",
                "asset": "solar"
            },
            {
                "id": "wind_grid_connection",
                "query": "风电项目并网需要什么条件？",
                "category": "wind_regulations", 
                "complexity": "intermediate",
                "expected_topics": ["并网条件", "风电", "技术要求"],
                "province": "sd",
                "asset": "wind"
            },
            {
                "id": "coal_environmental_standards",
                "query": "煤电项目环保要求有哪些？",
                "category": "coal_regulations",
                "complexity": "intermediate",
                "expected_topics": ["环保要求", "煤电", "排放标准"],
                "province": "nm",
                "asset": "coal"
            },
            {
                "id": "guangdong_renewable_approval",
                "query": "广东省新能源项目审批流程包括哪些步骤？",
                "category": "provincial_procedures",
                "complexity": "complex",
                "expected_topics": ["广东省", "新能源", "审批流程", "步骤"],
                "province": "gd",
                "asset": "solar"
            },
            {
                "id": "grid_technical_standards",
                "query": "电网接入技术标准对设备有什么要求？",
                "category": "technical_standards",
                "complexity": "complex",
                "expected_topics": ["电网接入", "技术标准", "设备要求"],
                "province": "gd",
                "asset": "solar"
            },
            {
                "id": "solar_capacity_limits",
                "query": "分布式光伏装机容量有什么限制？",
                "category": "capacity_regulations",
                "complexity": "intermediate",
                "expected_topics": ["装机容量", "限制", "分布式光伏"],
                "province": "gd",
                "asset": "solar"
            },
            {
                "id": "wind_environmental_impact",
                "query": "风电项目环境影响评价需要哪些材料？",
                "category": "environmental_assessment",
                "complexity": "complex",
                "expected_topics": ["环境影响评价", "风电", "材料清单"],
                "province": "sd",
                "asset": "wind"
            },
            {
                "id": "coal_safety_requirements",
                "query": "煤电项目安全生产有什么规定？",
                "category": "safety_regulations",
                "complexity": "intermediate",
                "expected_topics": ["安全生产", "煤电", "规定"],
                "province": "nm",
                "asset": "coal"
            },
            {
                "id": "renewable_subsidy_policy",
                "query": "可再生能源补贴政策最新变化是什么？",
                "category": "policy_updates",
                "complexity": "complex",
                "expected_topics": ["可再生能源", "补贴政策", "变化"],
                "province": "gd",
                "asset": "solar"
            },
            {
                "id": "grid_connection_fees",
                "query": "电网接入费用如何计算？",
                "category": "financial_regulations",
                "complexity": "intermediate",
                "expected_topics": ["接入费用", "计算方法", "电网"],
                "province": "gd",
                "asset": "solar"
            },
            {
                "id": "shandong_wind_planning",
                "query": "山东省风电发展规划有哪些重点区域？",
                "category": "regional_planning",
                "complexity": "complex",
                "expected_topics": ["山东省", "风电", "发展规划", "重点区域"],
                "province": "sd",
                "asset": "wind"
            },
            {
                "id": "coal_emission_monitoring",
                "query": "煤电厂排放监测要求是什么？",
                "category": "monitoring_requirements",
                "complexity": "intermediate",
                "expected_topics": ["排放监测", "煤电厂", "要求"],
                "province": "nm",
                "asset": "coal"
            },
            {
                "id": "distributed_solar_metering",
                "query": "分布式光伏计量装置安装有什么标准？",
                "category": "metering_standards",
                "complexity": "complex",
                "expected_topics": ["计量装置", "安装标准", "分布式光伏"],
                "province": "gd",
                "asset": "solar"
            },
            {
                "id": "wind_noise_standards",
                "query": "风电项目噪声控制标准是多少？",
                "category": "noise_regulations",
                "complexity": "intermediate",
                "expected_topics": ["噪声控制", "标准", "风电"],
                "province": "sd",
                "asset": "wind"
            },
            {
                "id": "coal_water_usage",
                "query": "煤电项目用水指标有什么限制？",
                "category": "water_regulations",
                "complexity": "intermediate",
                "expected_topics": ["用水指标", "限制", "煤电"],
                "province": "nm",
                "asset": "coal"
            },
            {
                "id": "solar_land_use_policy",
                "query": "光伏项目土地使用政策有哪些变化？",
                "category": "land_use_policy",
                "complexity": "complex",
                "expected_topics": ["土地使用", "政策变化", "光伏项目"],
                "province": "gd",
                "asset": "solar"
            },
            {
                "id": "offshore_wind_permits",
                "query": "海上风电项目需要哪些许可证？",
                "category": "permit_requirements",
                "complexity": "complex",
                "expected_topics": ["海上风电", "许可证", "申请"],
                "province": "sd",
                "asset": "wind"
            },
            {
                "id": "coal_ash_disposal",
                "query": "煤电厂粉煤灰处置有什么规定？",
                "category": "waste_management",
                "complexity": "intermediate",
                "expected_topics": ["粉煤灰", "处置规定", "煤电厂"],
                "province": "nm",
                "asset": "coal"
            },
            {
                "id": "energy_storage_integration",
                "query": "储能系统与新能源项目如何配套？",
                "category": "energy_storage",
                "complexity": "complex",
                "expected_topics": ["储能系统", "配套", "新能源项目"],
                "province": "gd",
                "asset": "solar"
            },
            {
                "id": "cross_provincial_transmission",
                "query": "跨省电力输送项目审批程序是什么？",
                "category": "transmission_regulations",
                "complexity": "complex",
                "expected_topics": ["跨省输送", "审批程序", "电力项目"],
                "province": "gd",
                "asset": "solar"
            }
        ]
        
        # Accuracy scoring rubric
        self.scoring_rubric = {
            "relevance": {
                "weight": 0.3,
                "criteria": {
                    "high": 0.8,  # Directly addresses the question with specific information
                    "medium": 0.6,  # Partially addresses the question
                    "low": 0.3,  # Tangentially related
                    "none": 0.0   # Not relevant
                }
            },
            "accuracy": {
                "weight": 0.25,
                "criteria": {
                    "high": 0.9,   # Information is factually correct
                    "medium": 0.7,  # Mostly correct with minor issues
                    "low": 0.4,    # Some correct information mixed with errors
                    "none": 0.0    # Incorrect or no factual information
                }
            },
            "completeness": {
                "weight": 0.2,
                "criteria": {
                    "high": 0.85,  # Comprehensive answer covering all aspects
                    "medium": 0.65, # Covers main points but missing some details
                    "low": 0.35,   # Incomplete answer
                    "none": 0.0    # No meaningful information
                }
            },
            "specificity": {
                "weight": 0.15,
                "criteria": {
                    "high": 0.8,   # Specific to the province/asset type mentioned
                    "medium": 0.6,  # Generally applicable but some specificity
                    "low": 0.3,    # Generic information
                    "none": 0.0    # No specific information
                }
            },
            "clarity": {
                "weight": 0.1,
                "criteria": {
                    "high": 0.9,   # Clear, well-structured response
                    "medium": 0.7,  # Generally clear with minor issues
                    "low": 0.4,    # Somewhat unclear or poorly structured
                    "none": 0.0    # Unclear or incoherent
                }
            }
        }
    
    async def run_comprehensive_verification(self) -> Dict[str, Any]:
        """
        Run comprehensive verification of the production system
        """
        verification_start = datetime.utcnow()
        
        self.logger.info("Starting comprehensive production verification...")
        
        verification_results = {
            "verification_id": f"verification_{verification_start.strftime('%Y%m%d_%H%M%S')}",
            "start_time": verification_start.isoformat(),
            "system_tests": {},
            "query_tests": {},
            "perplexity_integration": {},
            "performance_analysis": {},
            "rollout_assessment": {}
        }
        
        try:
            # 1. System Component Tests
            self.logger.info("Testing system components...")
            verification_results["system_tests"] = await self._test_system_components()
            
            # 2. Query Response Tests (20 queries)
            self.logger.info("Testing query responses...")
            verification_results["query_tests"] = await self._test_query_responses()
            
            # 3. Perplexity Integration Tests
            self.logger.info("Testing Perplexity integration...")
            verification_results["perplexity_integration"] = await self._test_perplexity_integration()
            
            # 4. Performance Analysis
            self.logger.info("Analyzing performance...")
            verification_results["performance_analysis"] = await self._analyze_performance()
            
            # 5. Rollout Readiness Assessment
            self.logger.info("Assessing rollout readiness...")
            verification_results["rollout_assessment"] = self._assess_rollout_readiness(verification_results)
            
            verification_end = datetime.utcnow()
            verification_results["end_time"] = verification_end.isoformat()
            verification_results["duration_seconds"] = (verification_end - verification_start).total_seconds()
            
            # Save results
            results_file = self.results_dir / f"verification_results_{verification_start.strftime('%Y%m%d_%H%M%S')}.json"
            with open(results_file, 'w') as f:
                json.dump(verification_results, f, indent=2, default=str)
            
            # Generate report
            report = self._generate_verification_report(verification_results)
            report_file = self.results_dir / f"verification_report_{verification_start.strftime('%Y%m%d_%H%M%S')}.md"
            with open(report_file, 'w') as f:
                f.write(report)
            
            self.logger.info(f"Verification completed in {verification_results['duration_seconds']:.2f}s")
            
            return verification_results
            
        except Exception as e:
            self.logger.error(f"Verification failed: {str(e)}")
            verification_results["error"] = str(e)
            verification_results["success"] = False
            return verification_results
    
    async def _test_system_components(self) -> Dict[str, Any]:
        """Test all system components"""
        component_tests = {
            "production_config": await self._test_production_config(),
            "rag_engine": await self._test_rag_engine(),
            "monitoring": await self._test_monitoring_system(),
            "backup_system": await self._test_backup_system(),
            "health_endpoints": await self._test_health_endpoints()
        }
        
        # Calculate overall component health
        successful_components = sum(1 for test in component_tests.values() if test.get("success", False))
        total_components = len(component_tests)
        
        component_tests["summary"] = {
            "total_components": total_components,
            "successful_components": successful_components,
            "success_rate": successful_components / total_components if total_components > 0 else 0,
            "overall_status": "healthy" if successful_components == total_components else "degraded"
        }
        
        return component_tests
    
    async def _test_production_config(self) -> Dict[str, Any]:
        """Test production configuration"""
        try:
            config = load_production_config()
            validation_errors = config.validate()
            
            return {
                "success": len(validation_errors) == 0,
                "validation_errors": validation_errors,
                "config_summary": {
                    "project_id": config.project_id,
                    "region": config.region,
                    "environment": config.environment
                }
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _test_rag_engine(self) -> Dict[str, Any]:
        """Test RAG engine initialization and basic functionality"""
        try:
            config = load_production_config()
            rag_engine = ProductionRAGEngine(config)
            
            # Test initialization
            init_success = await rag_engine.initialize()
            
            if not init_success:
                return {
                    "success": False,
                    "error": "RAG engine initialization failed"
                }
            
            # Test health check
            health_result = await rag_engine.health_check()
            
            # Test basic query
            test_query = "测试查询"
            query_result = await rag_engine.query_documents(test_query)
            
            await rag_engine.cleanup()
            
            return {
                "success": True,
                "initialization": "successful",
                "health_status": health_result["status"],
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
    
    async def _test_monitoring_system(self) -> Dict[str, Any]:
        """Test monitoring system"""
        try:
            from production_rag_system.monitoring.metrics_collector import MetricsCollector
            
            config = load_production_config()
            metrics_collector = MetricsCollector(config)
            await metrics_collector.initialize()
            
            health_check = await metrics_collector.health_check()
            
            return {
                "success": health_check["status"] == "healthy",
                "health_check": health_check
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _test_backup_system(self) -> Dict[str, Any]:
        """Test backup system"""
        try:
            from production_rag_system.backup.backup_manager import BackupManager
            
            config = load_production_config()
            backup_manager = BackupManager(config)
            await backup_manager.initialize()
            
            health_check = await backup_manager.health_check()
            
            return {
                "success": health_check["status"] == "healthy",
                "health_check": health_check
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _test_health_endpoints(self) -> Dict[str, Any]:
        """Test health endpoints"""
        try:
            from production_rag_system.monitoring.health_endpoints import create_health_endpoints
            
            config = load_production_config()
            health_endpoints = create_health_endpoints(config)
            
            return {
                "success": True,
                "endpoints_created": True,
                "health_port": config.health_check_port,
                "metrics_port": config.metrics_port
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _test_query_responses(self) -> Dict[str, Any]:
        """Test all 20 queries and score their responses"""
        query_results = {
            "total_queries": len(self.test_queries),
            "query_responses": [],
            "accuracy_scores": {},
            "performance_metrics": {}
        }
        
        # Initialize systems for testing
        config = load_production_config()
        rag_engine = ProductionRAGEngine(config)
        await rag_engine.initialize()
        
        try:
            response_times = []
            accuracy_scores = []
            
            for query_data in self.test_queries:
                query_result = await self._test_single_query(rag_engine, query_data)
                query_results["query_responses"].append(query_result)
                
                if query_result.get("response_time"):
                    response_times.append(query_result["response_time"])
                
                if query_result.get("accuracy_score"):
                    accuracy_scores.append(query_result["accuracy_score"])
            
            # Calculate summary metrics
            query_results["accuracy_scores"] = {
                "individual_scores": accuracy_scores,
                "average_accuracy": statistics.mean(accuracy_scores) if accuracy_scores else 0,
                "median_accuracy": statistics.median(accuracy_scores) if accuracy_scores else 0,
                "min_accuracy": min(accuracy_scores) if accuracy_scores else 0,
                "max_accuracy": max(accuracy_scores) if accuracy_scores else 0
            }
            
            query_results["performance_metrics"] = {
                "response_times": response_times,
                "average_response_time": statistics.mean(response_times) if response_times else 0,
                "median_response_time": statistics.median(response_times) if response_times else 0,
                "p95_response_time": self._calculate_percentile(response_times, 95) if response_times else 0
            }
            
        finally:
            await rag_engine.cleanup()
        
        return query_results
    
    async def _test_single_query(self, rag_engine: ProductionRAGEngine, query_data: Dict[str, Any]) -> Dict[str, Any]:
        """Test a single query and score the response"""
        start_time = time.time()
        
        try:
            # Execute query
            result = await rag_engine.query_documents(query_data["query"])
            response_time = time.time() - start_time
            
            # Score the response
            accuracy_score = self._score_response(result, query_data)
            
            return {
                "query_id": query_data["id"],
                "query": query_data["query"],
                "category": query_data["category"],
                "complexity": query_data["complexity"],
                "response_time": response_time,
                "success": not result.get("error"),
                "response_preview": str(result.get("answer", ""))[:200] + "..." if result.get("answer") else "No answer",
                "accuracy_score": accuracy_score,
                "scoring_details": self._get_scoring_details(result, query_data)
            }
            
        except Exception as e:
            return {
                "query_id": query_data["id"],
                "query": query_data["query"],
                "category": query_data["category"],
                "complexity": query_data["complexity"],
                "response_time": time.time() - start_time,
                "success": False,
                "error": str(e),
                "accuracy_score": 0
            }
    
    def _score_response(self, result: Dict[str, Any], query_data: Dict[str, Any]) -> float:
        """Score response based on rubric"""
        if result.get("error") or not result.get("answer"):
            return 0.0
        
        answer = str(result.get("answer", "")).lower()
        expected_topics = query_data.get("expected_topics", [])
        
        # Calculate individual scores
        relevance_score = self._score_relevance(answer, expected_topics)
        accuracy_score = self._score_accuracy(answer, query_data)
        completeness_score = self._score_completeness(answer, expected_topics)
        specificity_score = self._score_specificity(answer, query_data)
        clarity_score = self._score_clarity(answer)
        
        # Calculate weighted total score
        total_score = (
            relevance_score * self.scoring_rubric["relevance"]["weight"] +
            accuracy_score * self.scoring_rubric["accuracy"]["weight"] +
            completeness_score * self.scoring_rubric["completeness"]["weight"] +
            specificity_score * self.scoring_rubric["specificity"]["weight"] +
            clarity_score * self.scoring_rubric["clarity"]["weight"]
        )
        
        return min(1.0, max(0.0, total_score))
    
    def _score_relevance(self, answer: str, expected_topics: List[str]) -> float:
        """Score relevance based on expected topics"""
        if not expected_topics:
            return 0.6  # Default medium score if no expected topics
        
        topic_matches = sum(1 for topic in expected_topics if topic.lower() in answer)
        match_ratio = topic_matches / len(expected_topics)
        
        if match_ratio >= 0.8:
            return self.scoring_rubric["relevance"]["criteria"]["high"]
        elif match_ratio >= 0.5:
            return self.scoring_rubric["relevance"]["criteria"]["medium"]
        elif match_ratio >= 0.2:
            return self.scoring_rubric["relevance"]["criteria"]["low"]
        else:
            return self.scoring_rubric["relevance"]["criteria"]["none"]
    
    def _score_accuracy(self, answer: str, query_data: Dict[str, Any]) -> float:
        """Score accuracy (simplified heuristic)"""
        # This is a simplified scoring - in production would use more sophisticated methods
        if len(answer) > 100 and any(topic.lower() in answer for topic in query_data.get("expected_topics", [])):
            return self.scoring_rubric["accuracy"]["criteria"]["high"]
        elif len(answer) > 50:
            return self.scoring_rubric["accuracy"]["criteria"]["medium"]
        elif len(answer) > 20:
            return self.scoring_rubric["accuracy"]["criteria"]["low"]
        else:
            return self.scoring_rubric["accuracy"]["criteria"]["none"]
    
    def _score_completeness(self, answer: str, expected_topics: List[str]) -> float:
        """Score completeness based on coverage of expected topics"""
        if not expected_topics:
            return 0.6
        
        covered_topics = sum(1 for topic in expected_topics if topic.lower() in answer)
        coverage_ratio = covered_topics / len(expected_topics)
        
        if coverage_ratio >= 0.8:
            return self.scoring_rubric["completeness"]["criteria"]["high"]
        elif coverage_ratio >= 0.6:
            return self.scoring_rubric["completeness"]["criteria"]["medium"]
        elif coverage_ratio >= 0.3:
            return self.scoring_rubric["completeness"]["criteria"]["low"]
        else:
            return self.scoring_rubric["completeness"]["criteria"]["none"]
    
    def _score_specificity(self, answer: str, query_data: Dict[str, Any]) -> float:
        """Score specificity to province/asset type"""
        province_terms = {
            "gd": ["广东", "粤"],
            "sd": ["山东", "鲁"],
            "nm": ["内蒙古", "蒙"]
        }
        
        asset_terms = {
            "solar": ["光伏", "太阳能"],
            "wind": ["风电", "风能"],
            "coal": ["煤电", "火电"]
        }
        
        province = query_data.get("province", "")
        asset = query_data.get("asset", "")
        
        province_match = any(term in answer for term in province_terms.get(province, []))
        asset_match = any(term in answer for term in asset_terms.get(asset, []))
        
        if province_match and asset_match:
            return self.scoring_rubric["specificity"]["criteria"]["high"]
        elif province_match or asset_match:
            return self.scoring_rubric["specificity"]["criteria"]["medium"]
        elif len(answer) > 50:
            return self.scoring_rubric["specificity"]["criteria"]["low"]
        else:
            return self.scoring_rubric["specificity"]["criteria"]["none"]
    
    def _score_clarity(self, answer: str) -> float:
        """Score clarity based on structure and length"""
        if len(answer) > 200 and "。" in answer:  # Has proper sentence structure
            return self.scoring_rubric["clarity"]["criteria"]["high"]
        elif len(answer) > 100:
            return self.scoring_rubric["clarity"]["criteria"]["medium"]
        elif len(answer) > 30:
            return self.scoring_rubric["clarity"]["criteria"]["low"]
        else:
            return self.scoring_rubric["clarity"]["criteria"]["none"]
    
    def _get_scoring_details(self, result: Dict[str, Any], query_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get detailed scoring breakdown"""
        if result.get("error") or not result.get("answer"):
            return {"error": "No valid response to score"}
        
        answer = str(result.get("answer", "")).lower()
        expected_topics = query_data.get("expected_topics", [])
        
        return {
            "relevance": self._score_relevance(answer, expected_topics),
            "accuracy": self._score_accuracy(answer, query_data),
            "completeness": self._score_completeness(answer, expected_topics),
            "specificity": self._score_specificity(answer, query_data),
            "clarity": self._score_clarity(answer),
            "expected_topics_found": [topic for topic in expected_topics if topic.lower() in answer],
            "response_length": len(result.get("answer", ""))
        }
    
    async def _test_perplexity_integration(self) -> Dict[str, Any]:
        """Test Perplexity integration"""
        perplexity_results = {
            "integration_available": False,
            "test_queries": [],
            "performance_comparison": {}
        }
        
        try:
            # Test if Perplexity integration is available
            from lib.perplexity import answer_with_perplexity
            
            perplexity_results["integration_available"] = True
            
            # Test a few queries with Perplexity
            test_queries = self.test_queries[:5]  # Test first 5 queries
            
            for query_data in test_queries:
                perplexity_start = time.time()
                
                try:
                    perplexity_result = answer_with_perplexity(
                        query_data["query"],
                        query_data["province"],
                        query_data["asset"],
                        lang="zh-CN",
                        doc_class="grid"
                    )
                    
                    perplexity_time = time.time() - perplexity_start
                    
                    perplexity_results["test_queries"].append({
                        "query_id": query_data["id"],
                        "query": query_data["query"],
                        "success": bool(perplexity_result and perplexity_result.get("citations")),
                        "response_time": perplexity_time,
                        "citations_count": len(perplexity_result.get("citations", [])) if perplexity_result else 0
                    })
                    
                except Exception as e:
                    perplexity_results["test_queries"].append({
                        "query_id": query_data["id"],
                        "query": query_data["query"],
                        "success": False,
                        "error": str(e),
                        "response_time": time.time() - perplexity_start
                    })
            
            # Calculate performance metrics
            successful_queries = [q for q in perplexity_results["test_queries"] if q["success"]]
            
            if successful_queries:
                response_times = [q["response_time"] for q in successful_queries]
                perplexity_results["performance_comparison"] = {
                    "success_rate": len(successful_queries) / len(perplexity_results["test_queries"]),
                    "average_response_time": statistics.mean(response_times),
                    "median_response_time": statistics.median(response_times)
                }
            
        except ImportError:
            perplexity_results["integration_available"] = False
            perplexity_results["error"] = "Perplexity integration not available"
        except Exception as e:
            perplexity_results["error"] = str(e)
        
        return perplexity_results
    
    async def _analyze_performance(self) -> Dict[str, Any]:
        """Analyze system performance"""
        performance_analysis = {
            "load_test": await self._run_load_test(),
            "memory_usage": self._analyze_memory_usage(),
            "response_time_analysis": {},
            "scalability_assessment": {}
        }
        
        return performance_analysis
    
    async def _run_load_test(self) -> Dict[str, Any]:
        """Run a basic load test"""
        try:
            config = load_production_config()
            rag_engine = ProductionRAGEngine(config)
            await rag_engine.initialize()
            
            # Simulate concurrent queries
            concurrent_users = 5
            test_duration = 30  # seconds
            
            async def simulate_user():
                queries_completed = 0
                errors = 0
                start_time = time.time()
                
                while time.time() - start_time < test_duration:
                    try:
                        query = self.test_queries[queries_completed % len(self.test_queries)]
                        await rag_engine.query_documents(query["query"])
                        queries_completed += 1
                    except Exception:
                        errors += 1
                    
                    await asyncio.sleep(1)  # 1 second between queries
                
                return {"queries_completed": queries_completed, "errors": errors}
            
            # Run concurrent users
            tasks = [simulate_user() for _ in range(concurrent_users)]
            user_results = await asyncio.gather(*tasks)
            
            await rag_engine.cleanup()
            
            total_queries = sum(result["queries_completed"] for result in user_results)
            total_errors = sum(result["errors"] for result in user_results)
            
            return {
                "success": True,
                "concurrent_users": concurrent_users,
                "test_duration": test_duration,
                "total_queries": total_queries,
                "total_errors": total_errors,
                "queries_per_second": total_queries / test_duration,
                "error_rate": total_errors / total_queries if total_queries > 0 else 0
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _analyze_memory_usage(self) -> Dict[str, Any]:
        """Analyze memory usage (simplified)"""
        try:
            import psutil
            
            memory = psutil.virtual_memory()
            
            return {
                "total_memory_gb": memory.total / (1024**3),
                "available_memory_gb": memory.available / (1024**3),
                "memory_usage_percent": memory.percent,
                "memory_status": "healthy" if memory.percent < 80 else "warning" if memory.percent < 90 else "critical"
            }
            
        except ImportError:
            return {
                "error": "psutil not available for memory analysis"
            }
    
    def _calculate_percentile(self, data: List[float], percentile: int) -> float:
        """Calculate percentile of data"""
        if not data:
            return 0
        
        sorted_data = sorted(data)
        index = (percentile / 100) * (len(sorted_data) - 1)
        
        if index.is_integer():
            return sorted_data[int(index)]
        else:
            lower_index = int(index)
            upper_index = lower_index + 1
            weight = index - lower_index
            return sorted_data[lower_index] * (1 - weight) + sorted_data[upper_index] * weight
    
    def _assess_rollout_readiness(self, verification_results: Dict[str, Any]) -> Dict[str, Any]:
        """Assess rollout readiness based on verification results"""
        assessment = {
            "overall_readiness": "not_ready",
            "readiness_score": 0.0,
            "critical_issues": [],
            "warnings": [],
            "recommendations": [],
            "go_no_go_decision": "NO_GO"
        }
        
        # Analyze system component health
        system_tests = verification_results.get("system_tests", {})
        component_success_rate = system_tests.get("summary", {}).get("success_rate", 0)
        
        # Analyze query performance
        query_tests = verification_results.get("query_tests", {})
        average_accuracy = query_tests.get("accuracy_scores", {}).get("average_accuracy", 0)
        average_response_time = query_tests.get("performance_metrics", {}).get("average_response_time", 0)
        
        # Analyze performance
        performance_analysis = verification_results.get("performance_analysis", {})
        load_test = performance_analysis.get("load_test", {})
        load_test_success = load_test.get("success", False)
        
        # Calculate readiness score
        readiness_factors = {
            "component_health": component_success_rate * 0.3,
            "query_accuracy": average_accuracy * 0.3,
            "response_time": min(1.0, 5.0 / max(average_response_time, 0.1)) * 0.2,  # Target <5s
            "load_test": (1.0 if load_test_success else 0.0) * 0.2
        }
        
        assessment["readiness_score"] = sum(readiness_factors.values())
        
        # Determine critical issues
        if component_success_rate < 1.0:
            assessment["critical_issues"].append("System components not fully operational")
        
        if average_accuracy < 0.7:
            assessment["critical_issues"].append(f"Query accuracy too low: {average_accuracy:.2f} (target: >0.7)")
        
        if average_response_time > 10.0:
            assessment["critical_issues"].append(f"Response time too high: {average_response_time:.2f}s (target: <10s)")
        
        if not load_test_success:
            assessment["critical_issues"].append("Load testing failed")
        
        # Determine warnings
        if average_accuracy < 0.8:
            assessment["warnings"].append(f"Query accuracy could be improved: {average_accuracy:.2f}")
        
        if average_response_time > 5.0:
            assessment["warnings"].append(f"Response time above optimal: {average_response_time:.2f}s")
        
        # Generate recommendations
        assessment["recommendations"] = self._generate_recommendations(verification_results)
        
        # Determine overall readiness
        if assessment["readiness_score"] >= 0.8 and len(assessment["critical_issues"]) == 0:
            assessment["overall_readiness"] = "ready"
            assessment["go_no_go_decision"] = "GO"
        elif assessment["readiness_score"] >= 0.6 and len(assessment["critical_issues"]) <= 1:
            assessment["overall_readiness"] = "ready_with_conditions"
            assessment["go_no_go_decision"] = "CONDITIONAL_GO"
        else:
            assessment["overall_readiness"] = "not_ready"
            assessment["go_no_go_decision"] = "NO_GO"
        
        return assessment
    
    def _generate_recommendations(self, verification_results: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on verification results"""
        recommendations = []
        
        # System component recommendations
        system_tests = verification_results.get("system_tests", {})
        if system_tests.get("summary", {}).get("success_rate", 0) < 1.0:
            recommendations.append("Fix failing system components before deployment")
        
        # Query accuracy recommendations
        query_tests = verification_results.get("query_tests", {})
        average_accuracy = query_tests.get("accuracy_scores", {}).get("average_accuracy", 0)
        
        if average_accuracy < 0.8:
            recommendations.append("Improve query accuracy through better document processing or model tuning")
        
        # Performance recommendations
        average_response_time = query_tests.get("performance_metrics", {}).get("average_response_time", 0)
        
        if average_response_time > 5.0:
            recommendations.append("Optimize response times through caching or resource scaling")
        
        # Perplexity integration recommendations
        perplexity_integration = verification_results.get("perplexity_integration", {})
        if not perplexity_integration.get("integration_available", False):
            recommendations.append("Implement Perplexity integration for enhanced query responses")
        
        # Load testing recommendations
        load_test = verification_results.get("performance_analysis", {}).get("load_test", {})
        if not load_test.get("success", False):
            recommendations.append("Improve system stability under load")
        
        # General recommendations
        recommendations.extend([
            "Implement comprehensive monitoring and alerting before production deployment",
            "Establish clear rollback procedures and test them",
            "Train operations team on new system before go-live",
            "Plan for gradual traffic migration with monitoring",
            "Set up automated backup and recovery procedures"
        ])
        
        return recommendations
    
    def _generate_verification_report(self, verification_results: Dict[str, Any]) -> str:
        """Generate comprehensive verification report"""
        rollout_assessment = verification_results.get("rollout_assessment", {})
        
        report = f"""# Production RAG-Anything System Verification Report

## Executive Summary

**Verification Date:** {verification_results.get('start_time', 'Unknown')}
**Duration:** {verification_results.get('duration_seconds', 0):.2f} seconds
**Overall Readiness:** {rollout_assessment.get('overall_readiness', 'Unknown').upper()}
**Go/No-Go Decision:** {rollout_assessment.get('go_no_go_decision', 'UNKNOWN')}
**Readiness Score:** {rollout_assessment.get('readiness_score', 0):.2f}/1.0

## System Component Analysis

"""
        
        # System components
        system_tests = verification_results.get("system_tests", {})
        component_summary = system_tests.get("summary", {})
        
        report += f"""### Component Health
- **Total Components:** {component_summary.get('total_components', 0)}
- **Successful Components:** {component_summary.get('successful_components', 0)}
- **Success Rate:** {component_summary.get('success_rate', 0):.2%}
- **Overall Status:** {component_summary.get('overall_status', 'Unknown').upper()}

"""
        
        # Query analysis
        query_tests = verification_results.get("query_tests", {})
        accuracy_scores = query_tests.get("accuracy_scores", {})
        performance_metrics = query_tests.get("performance_metrics", {})
        
        report += f"""## Query Response Analysis

### Accuracy Metrics
- **Total Queries Tested:** {query_tests.get('total_queries', 0)}
- **Average Accuracy Score:** {accuracy_scores.get('average_accuracy', 0):.3f}
- **Median Accuracy Score:** {accuracy_scores.get('median_accuracy', 0):.3f}
- **Min/Max Accuracy:** {accuracy_scores.get('min_accuracy', 0):.3f} / {accuracy_scores.get('max_accuracy', 0):.3f}

### Performance Metrics
- **Average Response Time:** {performance_metrics.get('average_response_time', 0):.2f}s
- **Median Response Time:** {performance_metrics.get('median_response_time', 0):.2f}s
- **95th Percentile Response Time:** {performance_metrics.get('p95_response_time', 0):.2f}s

"""
        
        # Top performing queries
        query_responses = query_tests.get("query_responses", [])
        if query_responses:
            top_queries = sorted(query_responses, key=lambda x: x.get("accuracy_score", 0), reverse=True)[:5]
            
            report += "### Top Performing Queries\n\n"
            for i, query in enumerate(top_queries, 1):
                report += f"{i}. **{query.get('query_id', 'Unknown')}** (Score: {query.get('accuracy_score', 0):.3f})\n"
                report += f"   - Query: {query.get('query', 'Unknown')}\n"
                report += f"   - Response Time: {query.get('response_time', 0):.2f}s\n\n"
        
        # Perplexity integration
        perplexity_integration = verification_results.get("perplexity_integration", {})
        
        report += f"""## Perplexity Integration Analysis

- **Integration Available:** {'Yes' if perplexity_integration.get('integration_available', False) else 'No'}
"""
        
        if perplexity_integration.get("integration_available", False):
            perf_comparison = perplexity_integration.get("performance_comparison", {})
            report += f"""- **Success Rate:** {perf_comparison.get('success_rate', 0):.2%}
- **Average Response Time:** {perf_comparison.get('average_response_time', 0):.2f}s
- **Median Response Time:** {perf_comparison.get('median_response_time', 0):.2f}s
"""
        
        # Performance analysis
        performance_analysis = verification_results.get("performance_analysis", {})
        load_test = performance_analysis.get("load_test", {})
        
        report += f"""
## Performance Analysis

### Load Testing Results
- **Test Success:** {'Yes' if load_test.get('success', False) else 'No'}
- **Concurrent Users:** {load_test.get('concurrent_users', 0)}
- **Test Duration:** {load_test.get('test_duration', 0)}s
- **Total Queries:** {load_test.get('total_queries', 0)}
- **Queries per Second:** {load_test.get('queries_per_second', 0):.2f}
- **Error Rate:** {load_test.get('error_rate', 0):.2%}

"""
        
        # Critical issues and recommendations
        critical_issues = rollout_assessment.get("critical_issues", [])
        warnings = rollout_assessment.get("warnings", [])
        recommendations = rollout_assessment.get("recommendations", [])
        
        if critical_issues:
            report += "## Critical Issues\n\n"
            for issue in critical_issues:
                report += f"- ❌ {issue}\n"
            report += "\n"
        
        if warnings:
            report += "## Warnings\n\n"
            for warning in warnings:
                report += f"- ⚠️ {warning}\n"
            report += "\n"
        
        report += "## Recommendations\n\n"
        for recommendation in recommendations:
            report += f"- 📋 {recommendation}\n"
        
        # Final assessment
        go_no_go = rollout_assessment.get("go_no_go_decision", "UNKNOWN")
        
        report += f"""
## Final Assessment

**Decision:** {go_no_go}

"""
        
        if go_no_go == "GO":
            report += "✅ **System is ready for production deployment.**\n\n"
            report += "The system has passed all critical tests and meets production readiness criteria. Proceed with deployment according to the migration plan.\n"
        elif go_no_go == "CONDITIONAL_GO":
            report += "⚠️ **System is ready for deployment with conditions.**\n\n"
            report += "The system meets most criteria but has some issues that should be addressed. Consider a phased rollout with close monitoring.\n"
        else:
            report += "❌ **System is not ready for production deployment.**\n\n"
            report += "Critical issues must be resolved before deployment. Address the issues listed above and re-run verification.\n"
        
        report += f"""
## Next Steps

Based on the verification results, the recommended next steps are:

1. **Address Critical Issues:** Resolve all critical issues identified in this report
2. **Implement Recommendations:** Follow the recommendations to improve system performance
3. **Re-run Verification:** After addressing issues, run verification again
4. **Plan Deployment:** If verification passes, proceed with deployment planning
5. **Monitor Closely:** Implement comprehensive monitoring during rollout

---

*Report generated on {datetime.utcnow().isoformat()}*
"""
        
        return report


async def main():
    """Run comprehensive verification"""
    logging.basicConfig(level=logging.INFO)
    
    verification_suite = ProductionVerificationSuite()
    results = await verification_suite.run_comprehensive_verification()
    
    print("\n" + "="*80)
    print("PRODUCTION VERIFICATION COMPLETE")
    print("="*80)
    
    rollout_assessment = results.get("rollout_assessment", {})
    print(f"Overall Readiness: {rollout_assessment.get('overall_readiness', 'Unknown').upper()}")
    print(f"Go/No-Go Decision: {rollout_assessment.get('go_no_go_decision', 'Unknown')}")
    print(f"Readiness Score: {rollout_assessment.get('readiness_score', 0):.2f}/1.0")
    
    critical_issues = rollout_assessment.get("critical_issues", [])
    if critical_issues:
        print(f"\nCritical Issues ({len(critical_issues)}):")
        for issue in critical_issues:
            print(f"  - {issue}")
    
    print(f"\nDetailed results saved to: verification_results/")
    print("="*80)


if __name__ == "__main__":
    asyncio.run(main())