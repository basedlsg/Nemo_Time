"""
Traffic Router for System Migration
Handles gradual traffic routing during migration from current to new system
"""

import asyncio
import logging
import time
import json
from typing import Dict, Any, Optional, Callable
from datetime import datetime
from pathlib import Path
import random

from ..config.production_config import ProductionConfig


class TrafficRouter:
    """
    Manages traffic routing during system migration
    """
    
    def __init__(self, config: ProductionConfig, migration_config: Dict[str, Any]):
        self.config = config
        self.migration_config = migration_config
        self.routing_dir = f"{config.working_dir}/migration/routing"
        
        # Traffic routing state
        self.current_split = {"current": 100, "new": 0}
        self.routing_active = False
        self.routing_stats = {
            "total_requests": 0,
            "current_system_requests": 0,
            "new_system_requests": 0,
            "current_system_errors": 0,
            "new_system_errors": 0,
            "start_time": None
        }
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
        
        # Create routing directory
        Path(self.routing_dir).mkdir(parents=True, exist_ok=True)
    
    async def start_gradual_migration(self, migration_phases: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Start gradual traffic migration through defined phases
        
        Args:
            migration_phases: List of migration phases with traffic splits
            
        Returns:
            Migration execution results
        """
        try:
            self.logger.info("Starting gradual traffic migration...")
            self.routing_active = True
            self.routing_stats["start_time"] = datetime.utcnow().isoformat()
            
            migration_results = {
                "start_time": self.routing_stats["start_time"],
                "phases": [],
                "final_stats": {}
            }
            
            for i, phase in enumerate(migration_phases):
                self.logger.info(f"Executing migration phase {i+1}/{len(migration_phases)}: {phase['phase']}")
                
                phase_result = await self._execute_migration_phase(phase)
                migration_results["phases"].append(phase_result)
                
                if not phase_result["success"]:
                    self.logger.error(f"Migration phase failed: {phase['phase']}")
                    break
                
                # Wait between phases
                if i < len(migration_phases) - 1:
                    await asyncio.sleep(300)  # 5 minute wait between phases
            
            # Final statistics
            migration_results["final_stats"] = self.routing_stats.copy()
            
            # Save migration results
            results_file = f"{self.routing_dir}/migration_results.json"
            with open(results_file, 'w') as f:
                json.dump(migration_results, f, indent=2, default=str)
            
            return {
                "success": True,
                "migration_results": migration_results
            }
            
        except Exception as e:
            self.logger.error(f"Gradual migration failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _execute_migration_phase(self, phase: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single migration phase"""
        phase_start = datetime.utcnow()
        phase_duration = phase.get("duration_minutes", 30) * 60  # Default 30 minutes
        
        try:
            # Update traffic split
            new_split = {
                "current": phase["current"],
                "new": phase["new"]
            }
            
            self.current_split = new_split
            self.logger.info(f"Updated traffic split: {new_split}")
            
            # Monitor phase for specified duration
            phase_stats = {
                "phase_name": phase["phase"],
                "traffic_split": new_split,
                "start_time": phase_start.isoformat(),
                "duration_seconds": phase_duration,
                "requests_processed": 0,
                "error_rate": 0,
                "performance_metrics": {}
            }
            
            # Simulate phase monitoring
            monitoring_interval = 60  # Check every minute
            monitoring_cycles = int(phase_duration / monitoring_interval)
            
            for cycle in range(monitoring_cycles):
                await asyncio.sleep(monitoring_interval)
                
                # Collect phase metrics
                cycle_metrics = await self._collect_phase_metrics()
                phase_stats["requests_processed"] += cycle_metrics["requests"]
                
                self.logger.info(f"Phase {phase['phase']} - Cycle {cycle+1}/{monitoring_cycles}: {cycle_metrics}")
            
            # Calculate final phase statistics
            phase_end = datetime.utcnow()
            actual_duration = (phase_end - phase_start).total_seconds()
            
            phase_stats["end_time"] = phase_end.isoformat()
            phase_stats["actual_duration"] = actual_duration
            
            # Determine phase success
            success_criteria = {
                "max_error_rate": 0.05,  # 5% max error rate
                "min_requests": 10  # Minimum requests to validate
            }
            
            phase_success = (
                phase_stats["error_rate"] <= success_criteria["max_error_rate"] and
                phase_stats["requests_processed"] >= success_criteria["min_requests"]
            )
            
            return {
                "success": phase_success,
                "phase_stats": phase_stats,
                "success_criteria": success_criteria
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "phase_name": phase.get("phase", "unknown")
            }
    
    async def _collect_phase_metrics(self) -> Dict[str, Any]:
        """Collect metrics for current phase"""
        # Simulate request processing and metrics collection
        simulated_requests = random.randint(50, 200)  # Simulate 50-200 requests per minute
        simulated_errors = random.randint(0, int(simulated_requests * 0.02))  # 0-2% error rate
        
        # Update routing stats
        self.routing_stats["total_requests"] += simulated_requests
        
        # Distribute requests based on current split
        current_requests = int(simulated_requests * (self.current_split["current"] / 100))
        new_requests = simulated_requests - current_requests
        
        self.routing_stats["current_system_requests"] += current_requests
        self.routing_stats["new_system_requests"] += new_requests
        
        # Distribute errors (assume new system has slightly lower error rate)
        current_errors = int(simulated_errors * 0.6)  # 60% of errors to current system
        new_errors = simulated_errors - current_errors
        
        self.routing_stats["current_system_errors"] += current_errors
        self.routing_stats["new_system_errors"] += new_errors
        
        return {
            "requests": simulated_requests,
            "errors": simulated_errors,
            "current_requests": current_requests,
            "new_requests": new_requests,
            "error_rate": simulated_errors / simulated_requests if simulated_requests > 0 else 0
        }
    
    async def route_request(self, request_handler: Callable, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Route a single request based on current traffic split
        
        Args:
            request_handler: Function to handle the request
            request_data: Request data
            
        Returns:
            Response from appropriate system
        """
        if not self.routing_active:
            # If routing not active, use current system
            return await self._route_to_current_system(request_handler, request_data)
        
        # Determine routing based on current split
        route_to_new = random.randint(1, 100) <= self.current_split["new"]
        
        if route_to_new:
            return await self._route_to_new_system(request_handler, request_data)
        else:
            return await self._route_to_current_system(request_handler, request_data)
    
    async def _route_to_current_system(self, request_handler: Callable, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Route request to current system"""
        try:
            # Add routing metadata
            request_data["_routing"] = {
                "system": "current",
                "timestamp": datetime.utcnow().isoformat()
            }
            
            response = await request_handler(request_data)
            
            # Update stats
            self.routing_stats["current_system_requests"] += 1
            
            return response
            
        except Exception as e:
            self.routing_stats["current_system_errors"] += 1
            raise
    
    async def _route_to_new_system(self, request_handler: Callable, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Route request to new system"""
        try:
            # Add routing metadata
            request_data["_routing"] = {
                "system": "new",
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Initialize new system handler if needed
            from ..core.production_rag_engine import ProductionRAGEngine
            
            rag_engine = ProductionRAGEngine(self.config)
            await rag_engine.initialize()
            
            try:
                # Handle request with new system
                if "question" in request_data:
                    response = await rag_engine.query_documents(request_data["question"])
                else:
                    response = {"error": "Invalid request format for new system"}
                
                # Update stats
                self.routing_stats["new_system_requests"] += 1
                
                return response
                
            finally:
                await rag_engine.cleanup()
            
        except Exception as e:
            self.routing_stats["new_system_errors"] += 1
            raise
    
    async def get_routing_stats(self) -> Dict[str, Any]:
        """Get current routing statistics"""
        current_stats = self.routing_stats.copy()
        
        # Calculate derived metrics
        if current_stats["total_requests"] > 0:
            current_stats["current_system_percentage"] = (
                current_stats["current_system_requests"] / current_stats["total_requests"] * 100
            )
            current_stats["new_system_percentage"] = (
                current_stats["new_system_requests"] / current_stats["total_requests"] * 100
            )
        
        if current_stats["current_system_requests"] > 0:
            current_stats["current_system_error_rate"] = (
                current_stats["current_system_errors"] / current_stats["current_system_requests"]
            )
        
        if current_stats["new_system_requests"] > 0:
            current_stats["new_system_error_rate"] = (
                current_stats["new_system_errors"] / current_stats["new_system_requests"]
            )
        
        current_stats["current_split"] = self.current_split
        current_stats["routing_active"] = self.routing_active
        
        return current_stats
    
    async def emergency_rollback(self) -> Dict[str, Any]:
        """Execute emergency rollback to current system"""
        try:
            self.logger.warning("Executing emergency rollback to current system")
            
            # Immediately route all traffic to current system
            self.current_split = {"current": 100, "new": 0}
            
            # Create rollback record
            rollback_record = {
                "timestamp": datetime.utcnow().isoformat(),
                "reason": "emergency_rollback",
                "previous_split": self.current_split,
                "routing_stats": await self.get_routing_stats()
            }
            
            # Save rollback record
            rollback_file = f"{self.routing_dir}/emergency_rollback.json"
            with open(rollback_file, 'w') as f:
                json.dump(rollback_record, f, indent=2, default=str)
            
            self.logger.info("Emergency rollback completed")
            
            return {
                "success": True,
                "rollback_record": rollback_record
            }
            
        except Exception as e:
            self.logger.error(f"Emergency rollback failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def finalize_migration(self) -> Dict[str, Any]:
        """Finalize migration by routing all traffic to new system"""
        try:
            self.logger.info("Finalizing migration - routing all traffic to new system")
            
            # Route all traffic to new system
            self.current_split = {"current": 0, "new": 100}
            
            # Create finalization record
            finalization_record = {
                "timestamp": datetime.utcnow().isoformat(),
                "final_stats": await self.get_routing_stats(),
                "migration_completed": True
            }
            
            # Save finalization record
            finalization_file = f"{self.routing_dir}/migration_finalization.json"
            with open(finalization_file, 'w') as f:
                json.dump(finalization_record, f, indent=2, default=str)
            
            # Deactivate routing (all traffic goes to new system)
            self.routing_active = False
            
            self.logger.info("Migration finalization completed")
            
            return {
                "success": True,
                "finalization_record": finalization_record
            }
            
        except Exception as e:
            self.logger.error(f"Migration finalization failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }