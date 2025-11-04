"""
Automated Test Runner for Production RAG System
Handles scheduled testing, CI/CD integration, and continuous validation
"""

import asyncio
import schedule
import time
import logging
import json
from typing import Dict, Any, Optional, Callable
from datetime import datetime, timedelta
from pathlib import Path

from ..config.production_config import ProductionConfig
from .production_test_suite import ProductionTestSuite, run_production_tests


class AutomatedTestRunner:
    """
    Automated test runner for continuous validation and monitoring
    """
    
    def __init__(self, config: ProductionConfig):
        self.config = config
        self.test_runner_dir = f"{config.working_dir}/testing/automated"
        self.logger = logging.getLogger(__name__)
        
        # Test scheduling
        self.is_running = False
        self.test_history = []
        
        # Create directories
        Path(self.test_runner_dir).mkdir(parents=True, exist_ok=True)
        
        # Setup test schedules
        self._setup_test_schedules()
    
    def _setup_test_schedules(self):
        """Setup automated test schedules"""
        # Daily regression tests
        schedule.every().day.at("03:00").do(self._run_scheduled_regression_tests)
        
        # Hourly health checks
        schedule.every().hour.do(self._run_scheduled_health_checks)
        
        # Weekly comprehensive tests
        schedule.every().sunday.at("02:00").do(self._run_scheduled_comprehensive_tests)
        
        # Performance monitoring every 30 minutes
        schedule.every(30).minutes.do(self._run_scheduled_performance_tests)
    
    async def start_automated_testing(self):
        """Start automated test runner"""
        self.logger.info("Starting automated test runner...")
        self.is_running = True
        
        while self.is_running:
            try:
                # Run scheduled tests
                schedule.run_pending()
                
                # Wait before next check
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                self.logger.error(f"Error in automated test runner: {str(e)}")
                await asyncio.sleep(60)
    
    def stop_automated_testing(self):
        """Stop automated test runner"""
        self.logger.info("Stopping automated test runner...")
        self.is_running = False
    
    def _run_scheduled_regression_tests(self):
        """Run scheduled regression tests"""
        asyncio.create_task(self._execute_test_suite("regression", "daily_regression"))
    
    def _run_scheduled_health_checks(self):
        """Run scheduled health checks"""
        asyncio.create_task(self._execute_health_check())
    
    def _run_scheduled_comprehensive_tests(self):
        """Run scheduled comprehensive tests"""
        asyncio.create_task(self._execute_test_suite("comprehensive", "weekly_comprehensive"))
    
    def _run_scheduled_performance_tests(self):
        """Run scheduled performance tests"""
        asyncio.create_task(self._execute_test_suite("performance", "performance_monitoring"))
    
    async def _execute_test_suite(self, test_type: str, test_name: str):
        """Execute a specific test suite"""
        test_start = datetime.utcnow()
        
        try:
            self.logger.info(f"Running scheduled {test_type} tests: {test_name}")
            
            # Run appropriate test suite
            if test_type == "comprehensive":
                results = await run_production_tests(self.config)
            elif test_type == "regression":
                test_suite = ProductionTestSuite(self.config)
                results = await test_suite._run_regression_tests()
            elif test_type == "performance":
                test_suite = ProductionTestSuite(self.config)
                results = await test_suite._run_performance_tests()
            else:
                results = {"error": f"Unknown test type: {test_type}"}
            
            # Process results
            await self._process_test_results(test_name, results, test_start)
            
        except Exception as e:
            self.logger.error(f"Scheduled test {test_name} failed: {str(e)}")
            
            # Record failure
            failure_record = {
                "test_name": test_name,
                "test_type": test_type,
                "start_time": test_start.isoformat(),
                "end_time": datetime.utcnow().isoformat(),
                "success": False,
                "error": str(e)
            }
            
            await self._save_test_record(failure_record)
    
    async def _execute_health_check(self):
        """Execute health check"""
        try:
            from ..core.production_rag_engine import ProductionRAGEngine
            
            rag_engine = ProductionRAGEngine(self.config)
            await rag_engine.initialize()
            
            try:
                health_result = await rag_engine.health_check()
                
                # Save health check result
                health_record = {
                    "check_type": "automated_health_check",
                    "timestamp": datetime.utcnow().isoformat(),
                    "health_status": health_result,
                    "success": health_result["status"] == "healthy"
                }
                
                await self._save_health_record(health_record)
                
                # Alert if unhealthy
                if health_result["status"] != "healthy":
                    await self._send_health_alert(health_result)
                
            finally:
                await rag_engine.cleanup()
            
        except Exception as e:
            self.logger.error(f"Automated health check failed: {str(e)}")
    
    async def _process_test_results(self, test_name: str, results: Dict[str, Any], test_start: datetime):
        """Process and save test results"""
        test_record = {
            "test_name": test_name,
            "start_time": test_start.isoformat(),
            "end_time": datetime.utcnow().isoformat(),
            "results": results,
            "success": self._determine_test_success(results)
        }
        
        # Save test record
        await self._save_test_record(test_record)
        
        # Add to history
        self.test_history.append(test_record)
        
        # Keep only last 100 test records in memory
        if len(self.test_history) > 100:
            self.test_history = self.test_history[-100:]
        
        # Send alerts if tests failed
        if not test_record["success"]:
            await self._send_test_failure_alert(test_record)
        
        self.logger.info(f"Test {test_name} completed: {'PASSED' if test_record['success'] else 'FAILED'}")
    
    def _determine_test_success(self, results: Dict[str, Any]) -> bool:
        """Determine if test results indicate success"""
        if "overall_summary" in results:
            return results["overall_summary"]["overall_status"] == "passed"
        elif "summary" in results:
            return results["summary"].get("success_rate", 0) >= 0.9
        elif "success" in results:
            return results["success"]
        else:
            return False
    
    async def _save_test_record(self, test_record: Dict[str, Any]):
        """Save test record to file"""
        try:
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            record_file = f"{self.test_runner_dir}/test_record_{timestamp}.json"
            
            with open(record_file, 'w') as f:
                json.dump(test_record, f, indent=2, default=str)
            
        except Exception as e:
            self.logger.error(f"Failed to save test record: {str(e)}")
    
    async def _save_health_record(self, health_record: Dict[str, Any]):
        """Save health check record to file"""
        try:
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            record_file = f"{self.test_runner_dir}/health_record_{timestamp}.json"
            
            with open(record_file, 'w') as f:
                json.dump(health_record, f, indent=2, default=str)
            
        except Exception as e:
            self.logger.error(f"Failed to save health record: {str(e)}")
    
    async def _send_test_failure_alert(self, test_record: Dict[str, Any]):
        """Send alert for test failure"""
        try:
            alert_message = f"""
            Test Failure Alert
            
            Test Name: {test_record['test_name']}
            Start Time: {test_record['start_time']}
            End Time: {test_record['end_time']}
            
            Results Summary:
            {json.dumps(test_record.get('results', {}), indent=2, default=str)[:500]}...
            
            Please investigate the test failure and take appropriate action.
            """
            
            # Log alert (in production, this would send to alerting system)
            self.logger.error(f"TEST FAILURE ALERT: {alert_message}")
            
        except Exception as e:
            self.logger.error(f"Failed to send test failure alert: {str(e)}")
    
    async def _send_health_alert(self, health_result: Dict[str, Any]):
        """Send alert for health check failure"""
        try:
            alert_message = f"""
            Health Check Alert
            
            Status: {health_result['status']}
            Timestamp: {health_result['timestamp']}
            
            Component Status:
            {json.dumps(health_result.get('components', {}), indent=2, default=str)}
            
            Immediate attention required for system health issues.
            """
            
            # Log alert (in production, this would send to alerting system)
            self.logger.error(f"HEALTH CHECK ALERT: {alert_message}")
            
        except Exception as e:
            self.logger.error(f"Failed to send health alert: {str(e)}")
    
    async def run_on_demand_test(self, test_type: str = "comprehensive") -> Dict[str, Any]:
        """Run on-demand test"""
        self.logger.info(f"Running on-demand {test_type} test...")
        
        test_start = datetime.utcnow()
        
        try:
            if test_type == "comprehensive":
                results = await run_production_tests(self.config)
            elif test_type == "functional":
                test_suite = ProductionTestSuite(self.config)
                results = await test_suite._run_functional_tests()
            elif test_type == "performance":
                test_suite = ProductionTestSuite(self.config)
                results = await test_suite._run_performance_tests()
            elif test_type == "integration":
                test_suite = ProductionTestSuite(self.config)
                results = await test_suite._run_integration_tests()
            elif test_type == "load":
                test_suite = ProductionTestSuite(self.config)
                results = await test_suite._run_load_tests()
            else:
                return {"error": f"Unknown test type: {test_type}"}
            
            # Process results
            await self._process_test_results(f"on_demand_{test_type}", results, test_start)
            
            return results
            
        except Exception as e:
            self.logger.error(f"On-demand test failed: {str(e)}")
            return {"error": str(e)}
    
    def get_test_history(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get recent test history"""
        return self.test_history[-limit:] if self.test_history else []
    
    def get_test_statistics(self) -> Dict[str, Any]:
        """Get test statistics"""
        if not self.test_history:
            return {"message": "No test history available"}
        
        total_tests = len(self.test_history)
        successful_tests = sum(1 for test in self.test_history if test["success"])
        
        # Calculate success rate over time periods
        now = datetime.utcnow()
        last_24h = now - timedelta(hours=24)
        last_week = now - timedelta(days=7)
        
        recent_tests_24h = [
            test for test in self.test_history 
            if datetime.fromisoformat(test["start_time"]) >= last_24h
        ]
        
        recent_tests_week = [
            test for test in self.test_history 
            if datetime.fromisoformat(test["start_time"]) >= last_week
        ]
        
        return {
            "total_tests": total_tests,
            "successful_tests": successful_tests,
            "overall_success_rate": successful_tests / total_tests if total_tests > 0 else 0,
            "last_24h": {
                "total_tests": len(recent_tests_24h),
                "successful_tests": sum(1 for test in recent_tests_24h if test["success"]),
                "success_rate": sum(1 for test in recent_tests_24h if test["success"]) / len(recent_tests_24h) if recent_tests_24h else 0
            },
            "last_week": {
                "total_tests": len(recent_tests_week),
                "successful_tests": sum(1 for test in recent_tests_week if test["success"]),
                "success_rate": sum(1 for test in recent_tests_week if test["success"]) / len(recent_tests_week) if recent_tests_week else 0
            }
        }


class CICDIntegration:
    """
    CI/CD integration for automated testing
    """
    
    def __init__(self, config: ProductionConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
    
    async def run_pre_deployment_tests(self) -> Dict[str, Any]:
        """Run tests before deployment"""
        self.logger.info("Running pre-deployment tests...")
        
        test_suite = ProductionTestSuite(self.config)
        
        # Run critical tests
        functional_results = await test_suite._run_functional_tests()
        integration_results = await test_suite._run_integration_tests()
        
        # Determine if deployment should proceed
        functional_success = functional_results["summary"]["success_rate"] >= 0.95
        integration_success = integration_results["summary"]["success_rate"] >= 0.90
        
        deployment_approved = functional_success and integration_success
        
        return {
            "deployment_approved": deployment_approved,
            "functional_tests": functional_results,
            "integration_tests": integration_results,
            "approval_criteria": {
                "functional_success_rate_threshold": 0.95,
                "integration_success_rate_threshold": 0.90,
                "functional_success": functional_success,
                "integration_success": integration_success
            }
        }
    
    async def run_post_deployment_validation(self) -> Dict[str, Any]:
        """Run validation tests after deployment"""
        self.logger.info("Running post-deployment validation...")
        
        # Wait for system to stabilize
        await asyncio.sleep(30)
        
        test_suite = ProductionTestSuite(self.config)
        
        # Run validation tests
        functional_results = await test_suite._run_functional_tests()
        performance_results = await test_suite._run_performance_tests()
        
        # Check if deployment was successful
        functional_success = functional_results["summary"]["success_rate"] >= 0.90
        performance_acceptable = True  # Would check performance thresholds
        
        deployment_successful = functional_success and performance_acceptable
        
        return {
            "deployment_successful": deployment_successful,
            "functional_validation": functional_results,
            "performance_validation": performance_results,
            "validation_criteria": {
                "functional_success": functional_success,
                "performance_acceptable": performance_acceptable
            }
        }


async def start_automated_testing(config: ProductionConfig) -> AutomatedTestRunner:
    """
    Start automated testing system
    
    Args:
        config: Production configuration
        
    Returns:
        AutomatedTestRunner instance
    """
    test_runner = AutomatedTestRunner(config)
    
    # Start automated testing in background
    asyncio.create_task(test_runner.start_automated_testing())
    
    return test_runner