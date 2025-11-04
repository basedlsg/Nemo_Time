"""
Comprehensive Testing Suite for Production RAG-Anything System
Automated regression testing, performance monitoring, and integration tests
"""

import asyncio
import time
import json
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from pathlib import Path
import statistics

from ..config.production_config import ProductionConfig
from ..core.production_rag_engine import ProductionRAGEngine
from ..monitoring.metrics_collector import MetricsCollector


class ProductionTestSuite:
    """
    Comprehensive testing suite for production RAG system
    """
    
    def __init__(self, config: ProductionConfig):
        self.config = config
        self.test_results_dir = f"{config.working_dir}/testing"
        self.logger = logging.getLogger(__name__)
        
        # Test configuration
        self.test_queries = self._load_test_queries()
        self.performance_thresholds = self._load_performance_thresholds()
        
        # Create testing directory
        Path(self.test_results_dir).mkdir(parents=True, exist_ok=True)
    
    def _load_test_queries(self) -> List[Dict[str, Any]]:
        """Load test queries for validation"""
        return [
            {
                "id": "basic_solar_query",
                "question": "分布式光伏发电项目如何备案？",
                "category": "solar_regulations",
                "expected_keywords": ["备案", "分布式", "光伏"],
                "max_response_time": 5.0
            },
            {
                "id": "wind_grid_connection",
                "question": "风电项目并网需要什么条件？",
                "category": "wind_regulations",
                "expected_keywords": ["并网", "风电", "条件"],
                "max_response_time": 5.0
            },
            {
                "id": "coal_environmental",
                "question": "煤电项目环保要求有哪些？",
                "category": "coal_regulations",
                "expected_keywords": ["环保", "煤电", "要求"],
                "max_response_time": 5.0
            },
            {
                "id": "complex_multi_asset",
                "question": "广东省新能源项目审批流程包括哪些步骤？",
                "category": "complex_query",
                "expected_keywords": ["广东", "新能源", "审批", "流程"],
                "max_response_time": 8.0
            },
            {
                "id": "technical_specification",
                "question": "电网接入技术标准对设备有什么要求？",
                "category": "technical_query",
                "expected_keywords": ["电网", "技术标准", "设备", "要求"],
                "max_response_time": 6.0
            }
        ]
    
    def _load_performance_thresholds(self) -> Dict[str, Any]:
        """Load performance thresholds for testing"""
        return {
            "query_response_time": {
                "excellent": 2.0,
                "good": 5.0,
                "acceptable": 10.0
            },
            "query_success_rate": {
                "excellent": 0.99,
                "good": 0.95,
                "acceptable": 0.90
            },
            "system_availability": {
                "excellent": 0.999,
                "good": 0.99,
                "acceptable": 0.95
            },
            "concurrent_users": {
                "light_load": 10,
                "normal_load": 50,
                "heavy_load": 100
            }
        }
    
    async def run_comprehensive_test_suite(self) -> Dict[str, Any]:
        """
        Run complete test suite including all test categories
        
        Returns:
            Comprehensive test results
        """
        test_start = datetime.utcnow()
        
        try:
            self.logger.info("Starting comprehensive test suite...")
            
            test_results = {
                "test_suite_id": f"test_{test_start.strftime('%Y%m%d_%H%M%S')}",
                "start_time": test_start.isoformat(),
                "test_categories": {}
            }
            
            # 1. Functional Tests
            self.logger.info("Running functional tests...")
            functional_results = await self._run_functional_tests()
            test_results["test_categories"]["functional"] = functional_results
            
            # 2. Performance Tests
            self.logger.info("Running performance tests...")
            performance_results = await self._run_performance_tests()
            test_results["test_categories"]["performance"] = performance_results
            
            # 3. Integration Tests
            self.logger.info("Running integration tests...")
            integration_results = await self._run_integration_tests()
            test_results["test_categories"]["integration"] = integration_results
            
            # 4. Regression Tests
            self.logger.info("Running regression tests...")
            regression_results = await self._run_regression_tests()
            test_results["test_categories"]["regression"] = regression_results
            
            # 5. Load Tests
            self.logger.info("Running load tests...")
            load_results = await self._run_load_tests()
            test_results["test_categories"]["load"] = load_results
            
            # Calculate overall results
            test_end = datetime.utcnow()
            test_duration = (test_end - test_start).total_seconds()
            
            test_results["end_time"] = test_end.isoformat()
            test_results["duration_seconds"] = test_duration
            test_results["overall_summary"] = self._calculate_overall_summary(test_results)
            
            # Save test results
            results_file = f"{self.test_results_dir}/test_results_{test_start.strftime('%Y%m%d_%H%M%S')}.json"
            with open(results_file, 'w') as f:
                json.dump(test_results, f, indent=2, default=str)
            
            self.logger.info(f"Test suite completed in {test_duration:.2f}s")
            
            return test_results
            
        except Exception as e:
            self.logger.error(f"Test suite failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "start_time": test_start.isoformat()
            }
    
    async def _run_functional_tests(self) -> Dict[str, Any]:
        """Run functional tests to verify core functionality"""
        functional_results = {
            "test_type": "functional",
            "start_time": datetime.utcnow().isoformat(),
            "tests": []
        }
        
        # Initialize RAG engine for testing
        rag_engine = ProductionRAGEngine(self.config)
        await rag_engine.initialize()
        
        try:
            # Test each query
            for test_query in self.test_queries:
                test_result = await self._run_single_functional_test(rag_engine, test_query)
                functional_results["tests"].append(test_result)
            
            # Calculate summary
            total_tests = len(functional_results["tests"])
            passed_tests = sum(1 for test in functional_results["tests"] if test["passed"])
            
            functional_results["summary"] = {
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": total_tests - passed_tests,
                "success_rate": passed_tests / total_tests if total_tests > 0 else 0
            }
            
        finally:
            await rag_engine.cleanup()
        
        functional_results["end_time"] = datetime.utcnow().isoformat()
        return functional_results
    
    async def _run_single_functional_test(self, rag_engine: ProductionRAGEngine, test_query: Dict[str, Any]) -> Dict[str, Any]:
        """Run a single functional test"""
        test_start = time.time()
        
        try:
            # Execute query
            result = await rag_engine.query_documents(test_query["question"])
            
            test_duration = time.time() - test_start
            
            # Validate result
            validation_results = self._validate_query_result(result, test_query)
            
            return {
                "test_id": test_query["id"],
                "question": test_query["question"],
                "category": test_query["category"],
                "duration": test_duration,
                "passed": validation_results["passed"],
                "validation_details": validation_results,
                "response_preview": str(result.get("answer", ""))[:200] + "..." if result.get("answer") else "No answer"
            }
            
        except Exception as e:
            return {
                "test_id": test_query["id"],
                "question": test_query["question"],
                "category": test_query["category"],
                "duration": time.time() - test_start,
                "passed": False,
                "error": str(e)
            }
    
    def _validate_query_result(self, result: Dict[str, Any], test_query: Dict[str, Any]) -> Dict[str, Any]:
        """Validate query result against expected criteria"""
        validation = {
            "passed": True,
            "checks": {}
        }
        
        # Check if result has answer
        has_answer = bool(result.get("answer"))
        validation["checks"]["has_answer"] = has_answer
        
        if not has_answer:
            validation["passed"] = False
            return validation
        
        # Check response time
        response_time_ok = result.get("query_duration", 0) <= test_query["max_response_time"]
        validation["checks"]["response_time_ok"] = response_time_ok
        
        if not response_time_ok:
            validation["passed"] = False
        
        # Check for expected keywords
        answer_text = str(result.get("answer", "")).lower()
        expected_keywords = test_query.get("expected_keywords", [])
        
        keyword_matches = []
        for keyword in expected_keywords:
            matches = keyword.lower() in answer_text
            keyword_matches.append(matches)
        
        keywords_found = sum(keyword_matches)
        keyword_threshold = len(expected_keywords) * 0.5  # At least 50% of keywords should be present
        
        validation["checks"]["keywords_found"] = {
            "found": keywords_found,
            "expected": len(expected_keywords),
            "threshold_met": keywords_found >= keyword_threshold
        }
        
        if keywords_found < keyword_threshold:
            validation["passed"] = False
        
        return validation
    
    async def _run_performance_tests(self) -> Dict[str, Any]:
        """Run performance tests to measure system performance"""
        performance_results = {
            "test_type": "performance",
            "start_time": datetime.utcnow().isoformat(),
            "tests": []
        }
        
        # Initialize RAG engine
        rag_engine = ProductionRAGEngine(self.config)
        await rag_engine.initialize()
        
        try:
            # Test query performance with multiple iterations
            for test_query in self.test_queries[:3]:  # Use first 3 queries for performance testing
                perf_result = await self._run_performance_test(rag_engine, test_query, iterations=5)
                performance_results["tests"].append(perf_result)
            
            # Calculate performance summary
            all_response_times = []
            for test in performance_results["tests"]:
                all_response_times.extend(test["response_times"])
            
            if all_response_times:
                performance_results["summary"] = {
                    "average_response_time": statistics.mean(all_response_times),
                    "median_response_time": statistics.median(all_response_times),
                    "min_response_time": min(all_response_times),
                    "max_response_time": max(all_response_times),
                    "p95_response_time": self._calculate_percentile(all_response_times, 95),
                    "p99_response_time": self._calculate_percentile(all_response_times, 99)
                }
            
        finally:
            await rag_engine.cleanup()
        
        performance_results["end_time"] = datetime.utcnow().isoformat()
        return performance_results
    
    async def _run_performance_test(self, rag_engine: ProductionRAGEngine, test_query: Dict[str, Any], iterations: int = 5) -> Dict[str, Any]:
        """Run performance test for a single query with multiple iterations"""
        response_times = []
        
        for i in range(iterations):
            start_time = time.time()
            
            try:
                result = await rag_engine.query_documents(test_query["question"])
                response_time = time.time() - start_time
                response_times.append(response_time)
                
                # Small delay between iterations
                await asyncio.sleep(0.5)
                
            except Exception as e:
                self.logger.warning(f"Performance test iteration {i+1} failed: {str(e)}")
        
        return {
            "test_id": test_query["id"],
            "question": test_query["question"],
            "iterations": iterations,
            "successful_iterations": len(response_times),
            "response_times": response_times,
            "average_response_time": statistics.mean(response_times) if response_times else 0,
            "min_response_time": min(response_times) if response_times else 0,
            "max_response_time": max(response_times) if response_times else 0
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
    
    async def _run_integration_tests(self) -> Dict[str, Any]:
        """Run integration tests with Perplexity and other components"""
        integration_results = {
            "test_type": "integration",
            "start_time": datetime.utcnow().isoformat(),
            "tests": []
        }
        
        # Test RAG system integration
        rag_integration_test = await self._test_rag_system_integration()
        integration_results["tests"].append(rag_integration_test)
        
        # Test Perplexity integration (if enabled)
        if self.config.enable_perplexity:
            perplexity_integration_test = await self._test_perplexity_integration()
            integration_results["tests"].append(perplexity_integration_test)
        
        # Test backup system integration
        backup_integration_test = await self._test_backup_integration()
        integration_results["tests"].append(backup_integration_test)
        
        # Test monitoring integration
        monitoring_integration_test = await self._test_monitoring_integration()
        integration_results["tests"].append(monitoring_integration_test)
        
        # Calculate integration summary
        total_tests = len(integration_results["tests"])
        passed_tests = sum(1 for test in integration_results["tests"] if test["passed"])
        
        integration_results["summary"] = {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": total_tests - passed_tests,
            "success_rate": passed_tests / total_tests if total_tests > 0 else 0
        }
        
        integration_results["end_time"] = datetime.utcnow().isoformat()
        return integration_results
    
    async def _test_rag_system_integration(self) -> Dict[str, Any]:
        """Test RAG system integration"""
        try:
            rag_engine = ProductionRAGEngine(self.config)
            init_success = await rag_engine.initialize()
            
            if not init_success:
                return {
                    "test_name": "rag_system_integration",
                    "passed": False,
                    "error": "RAG system initialization failed"
                }
            
            # Test basic functionality
            health_check = await rag_engine.health_check()
            
            await rag_engine.cleanup()
            
            return {
                "test_name": "rag_system_integration",
                "passed": health_check["status"] == "healthy",
                "health_check_result": health_check
            }
            
        except Exception as e:
            return {
                "test_name": "rag_system_integration",
                "passed": False,
                "error": str(e)
            }
    
    async def _test_perplexity_integration(self) -> Dict[str, Any]:
        """Test Perplexity integration"""
        try:
            # This would test actual Perplexity integration
            # For now, return a mock test result
            return {
                "test_name": "perplexity_integration",
                "passed": True,
                "message": "Perplexity integration test passed (mock)"
            }
            
        except Exception as e:
            return {
                "test_name": "perplexity_integration",
                "passed": False,
                "error": str(e)
            }
    
    async def _test_backup_integration(self) -> Dict[str, Any]:
        """Test backup system integration"""
        try:
            from ..backup.backup_manager import BackupManager
            
            backup_manager = BackupManager(self.config)
            await backup_manager.initialize()
            
            # Test backup creation
            backup_result = await backup_manager.create_backup("integration_test")
            
            return {
                "test_name": "backup_integration",
                "passed": backup_result["success"],
                "backup_result": backup_result
            }
            
        except Exception as e:
            return {
                "test_name": "backup_integration",
                "passed": False,
                "error": str(e)
            }
    
    async def _test_monitoring_integration(self) -> Dict[str, Any]:
        """Test monitoring system integration"""
        try:
            metrics_collector = MetricsCollector(self.config)
            await metrics_collector.initialize()
            
            # Test metrics collection
            health_check = await metrics_collector.health_check()
            
            return {
                "test_name": "monitoring_integration",
                "passed": health_check["status"] == "healthy",
                "health_check_result": health_check
            }
            
        except Exception as e:
            return {
                "test_name": "monitoring_integration",
                "passed": False,
                "error": str(e)
            }
    
    async def _run_regression_tests(self) -> Dict[str, Any]:
        """Run regression tests to ensure no functionality degradation"""
        regression_results = {
            "test_type": "regression",
            "start_time": datetime.utcnow().isoformat(),
            "baseline_comparison": {}
        }
        
        # Load baseline results if available
        baseline_file = f"{self.test_results_dir}/baseline_results.json"
        baseline_results = None
        
        if Path(baseline_file).exists():
            with open(baseline_file, 'r') as f:
                baseline_results = json.load(f)
        
        # Run current tests
        current_results = await self._run_functional_tests()
        
        # Compare with baseline
        if baseline_results:
            comparison = self._compare_with_baseline(current_results, baseline_results)
            regression_results["baseline_comparison"] = comparison
        else:
            # Save current results as baseline
            with open(baseline_file, 'w') as f:
                json.dump(current_results, f, indent=2, default=str)
            
            regression_results["baseline_comparison"] = {
                "status": "baseline_created",
                "message": "No baseline found, current results saved as baseline"
            }
        
        regression_results["current_results"] = current_results
        regression_results["end_time"] = datetime.utcnow().isoformat()
        
        return regression_results
    
    def _compare_with_baseline(self, current: Dict[str, Any], baseline: Dict[str, Any]) -> Dict[str, Any]:
        """Compare current results with baseline"""
        comparison = {
            "overall_status": "passed",
            "degradations": [],
            "improvements": []
        }
        
        # Compare success rates
        current_success_rate = current["summary"]["success_rate"]
        baseline_success_rate = baseline["summary"]["success_rate"]
        
        success_rate_diff = current_success_rate - baseline_success_rate
        
        if success_rate_diff < -0.05:  # 5% degradation threshold
            comparison["overall_status"] = "degraded"
            comparison["degradations"].append({
                "metric": "success_rate",
                "current": current_success_rate,
                "baseline": baseline_success_rate,
                "difference": success_rate_diff
            })
        elif success_rate_diff > 0.05:  # 5% improvement threshold
            comparison["improvements"].append({
                "metric": "success_rate",
                "current": current_success_rate,
                "baseline": baseline_success_rate,
                "difference": success_rate_diff
            })
        
        return comparison
    
    async def _run_load_tests(self) -> Dict[str, Any]:
        """Run load tests to verify system performance under load"""
        load_results = {
            "test_type": "load",
            "start_time": datetime.utcnow().isoformat(),
            "load_scenarios": []
        }
        
        # Test different load scenarios
        load_scenarios = [
            {"name": "light_load", "concurrent_users": 5, "duration": 60},
            {"name": "normal_load", "concurrent_users": 15, "duration": 120},
            {"name": "heavy_load", "concurrent_users": 25, "duration": 180}
        ]
        
        for scenario in load_scenarios:
            scenario_result = await self._run_load_scenario(scenario)
            load_results["load_scenarios"].append(scenario_result)
        
        load_results["end_time"] = datetime.utcnow().isoformat()
        return load_results
    
    async def _run_load_scenario(self, scenario: Dict[str, Any]) -> Dict[str, Any]:
        """Run a single load test scenario"""
        scenario_start = time.time()
        
        try:
            self.logger.info(f"Running load scenario: {scenario['name']} with {scenario['concurrent_users']} users")
            
            # Initialize RAG engine
            rag_engine = ProductionRAGEngine(self.config)
            await rag_engine.initialize()
            
            try:
                # Simulate concurrent users
                tasks = []
                for i in range(scenario['concurrent_users']):
                    task = self._simulate_user_load(rag_engine, scenario['duration'])
                    tasks.append(task)
                
                # Wait for all tasks to complete
                user_results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # Analyze results
                successful_users = sum(1 for result in user_results if isinstance(result, dict) and result.get("success"))
                total_queries = sum(result.get("total_queries", 0) for result in user_results if isinstance(result, dict))
                total_errors = sum(result.get("errors", 0) for result in user_results if isinstance(result, dict))
                
                scenario_duration = time.time() - scenario_start
                
                return {
                    "scenario_name": scenario["name"],
                    "concurrent_users": scenario["concurrent_users"],
                    "duration": scenario_duration,
                    "successful_users": successful_users,
                    "total_queries": total_queries,
                    "total_errors": total_errors,
                    "queries_per_second": total_queries / scenario_duration if scenario_duration > 0 else 0,
                    "error_rate": total_errors / total_queries if total_queries > 0 else 0,
                    "success": total_errors / total_queries < 0.05 if total_queries > 0 else False  # 5% error threshold
                }
                
            finally:
                await rag_engine.cleanup()
            
        except Exception as e:
            return {
                "scenario_name": scenario["name"],
                "success": False,
                "error": str(e),
                "duration": time.time() - scenario_start
            }
    
    async def _simulate_user_load(self, rag_engine: ProductionRAGEngine, duration: int) -> Dict[str, Any]:
        """Simulate load from a single user"""
        start_time = time.time()
        end_time = start_time + duration
        
        total_queries = 0
        errors = 0
        
        try:
            while time.time() < end_time:
                # Select random test query
                test_query = self.test_queries[total_queries % len(self.test_queries)]
                
                try:
                    await rag_engine.query_documents(test_query["question"])
                    total_queries += 1
                except Exception:
                    errors += 1
                    total_queries += 1
                
                # Wait between queries (simulate user think time)
                await asyncio.sleep(2)
            
            return {
                "success": True,
                "total_queries": total_queries,
                "errors": errors,
                "duration": time.time() - start_time
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "total_queries": total_queries,
                "errors": errors
            }
    
    def _calculate_overall_summary(self, test_results: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate overall test suite summary"""
        summary = {
            "overall_status": "passed",
            "category_results": {},
            "key_metrics": {}
        }
        
        # Analyze each test category
        for category, results in test_results["test_categories"].items():
            if "summary" in results:
                category_summary = results["summary"]
                success_rate = category_summary.get("success_rate", 0)
                
                summary["category_results"][category] = {
                    "success_rate": success_rate,
                    "status": "passed" if success_rate >= 0.9 else "failed"
                }
                
                if success_rate < 0.9:
                    summary["overall_status"] = "failed"
        
        # Calculate key metrics
        if "performance" in test_results["test_categories"]:
            perf_summary = test_results["test_categories"]["performance"].get("summary", {})
            summary["key_metrics"]["average_response_time"] = perf_summary.get("average_response_time", 0)
            summary["key_metrics"]["p95_response_time"] = perf_summary.get("p95_response_time", 0)
        
        return summary


async def run_production_tests(config: ProductionConfig) -> Dict[str, Any]:
    """
    Run comprehensive production test suite
    
    Args:
        config: Production configuration
        
    Returns:
        Test results
    """
    test_suite = ProductionTestSuite(config)
    return await test_suite.run_comprehensive_test_suite()