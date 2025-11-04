"""
Production Backup Manager
Handles automated backup and recovery for RAG-Anything system
"""

import os
import shutil
import tarfile
import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from pathlib import Path
import json

from ..config.production_config import ProductionConfig


class BackupManager:
    """
    Manages automated backup and recovery for production RAG system
    """
    
    def __init__(self, config: ProductionConfig):
        self.config = config
        self.backup_dir = f"{config.working_dir}/backups"
        self.logger = logging.getLogger(__name__)
        
        # Backup metadata
        self.backup_metadata_file = f"{self.backup_dir}/backup_metadata.json"
        self.backup_metadata = {
            "backups": [],
            "last_backup": None,
            "total_backups": 0
        }
        
    async def initialize(self):
        """Initialize backup manager"""
        try:
            # Create backup directory
            Path(self.backup_dir).mkdir(parents=True, exist_ok=True)
            
            # Load existing backup metadata
            await self._load_backup_metadata()
            
            # Clean up old backups
            await self._cleanup_old_backups()
            
            self.logger.info("Backup manager initialized")
            
        except Exception as e:
            self.logger.error(f"Error initializing backup manager: {str(e)}")
    
    async def _load_backup_metadata(self):
        """Load backup metadata from file"""
        try:
            if Path(self.backup_metadata_file).exists():
                with open(self.backup_metadata_file, 'r') as f:
                    self.backup_metadata = json.load(f)
        except Exception as e:
            self.logger.warning(f"Could not load backup metadata: {str(e)}")
    
    async def _save_backup_metadata(self):
        """Save backup metadata to file"""
        try:
            with open(self.backup_metadata_file, 'w') as f:
                json.dump(self.backup_metadata, f, indent=2, default=str)
        except Exception as e:
            self.logger.error(f"Error saving backup metadata: {str(e)}")
    
    async def create_backup(self, backup_type: str = "manual") -> Dict[str, Any]:
        """
        Create a complete system backup
        
        Args:
            backup_type: Type of backup (manual, scheduled, pre_migration)
            
        Returns:
            Backup creation results
        """
        backup_id = f"backup_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        backup_path = f"{self.backup_dir}/{backup_id}"
        
        try:
            self.logger.info(f"Creating backup: {backup_id}")
            
            # Create backup directory
            Path(backup_path).mkdir(parents=True, exist_ok=True)
            
            # Backup components
            backup_results = {}
            
            # 1. Backup RAG storage
            rag_backup_result = await self._backup_rag_storage(backup_path)
            backup_results["rag_storage"] = rag_backup_result
            
            # 2. Backup configuration
            config_backup_result = await self._backup_configuration(backup_path)
            backup_results["configuration"] = config_backup_result
            
            # 3. Backup logs
            logs_backup_result = await self._backup_logs(backup_path)
            backup_results["logs"] = logs_backup_result
            
            # 4. Backup metrics
            metrics_backup_result = await self._backup_metrics(backup_path)
            backup_results["metrics"] = metrics_backup_result
            
            # Create backup manifest
            manifest = {
                "backup_id": backup_id,
                "backup_type": backup_type,
                "timestamp": datetime.utcnow().isoformat(),
                "config": self.config.to_dict(),
                "components": backup_results,
                "size_bytes": self._calculate_backup_size(backup_path)
            }
            
            # Save manifest
            manifest_file = f"{backup_path}/backup_manifest.json"
            with open(manifest_file, 'w') as f:
                json.dump(manifest, f, indent=2, default=str)
            
            # Create compressed archive
            archive_path = f"{backup_path}.tar.gz"
            await self._create_archive(backup_path, archive_path)
            
            # Remove uncompressed backup directory
            shutil.rmtree(backup_path)
            
            # Update backup metadata
            backup_record = {
                "backup_id": backup_id,
                "backup_type": backup_type,
                "timestamp": datetime.utcnow().isoformat(),
                "archive_path": archive_path,
                "size_bytes": Path(archive_path).stat().st_size,
                "components": list(backup_results.keys())
            }
            
            self.backup_metadata["backups"].append(backup_record)
            self.backup_metadata["last_backup"] = backup_record
            self.backup_metadata["total_backups"] += 1
            
            await self._save_backup_metadata()
            
            self.logger.info(f"Backup created successfully: {backup_id}")
            
            return {
                "success": True,
                "backup_id": backup_id,
                "archive_path": archive_path,
                "size_bytes": backup_record["size_bytes"],
                "components": backup_results
            }
            
        except Exception as e:
            self.logger.error(f"Error creating backup: {str(e)}")
            
            # Clean up failed backup
            if Path(backup_path).exists():
                shutil.rmtree(backup_path)
            
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _backup_rag_storage(self, backup_path: str) -> Dict[str, Any]:
        """Backup RAG storage directory"""
        try:
            rag_storage_path = self.config.working_dir
            backup_rag_path = f"{backup_path}/rag_storage"
            
            # Copy RAG storage (excluding logs and backups)
            def ignore_patterns(dir, files):
                return [f for f in files if f in ['logs', 'backups', 'temp']]
            
            shutil.copytree(rag_storage_path, backup_rag_path, ignore=ignore_patterns)
            
            size = self._calculate_directory_size(backup_rag_path)
            
            return {
                "success": True,
                "size_bytes": size,
                "path": backup_rag_path
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _backup_configuration(self, backup_path: str) -> Dict[str, Any]:
        """Backup system configuration"""
        try:
            config_backup_path = f"{backup_path}/configuration"
            Path(config_backup_path).mkdir(parents=True, exist_ok=True)
            
            # Save current configuration
            config_file = f"{config_backup_path}/production_config.json"
            with open(config_file, 'w') as f:
                json.dump(self.config.to_dict(), f, indent=2, default=str)
            
            # Copy any configuration files from the project
            config_files = [
                "config/environment.yaml",
                "config/secrets.yaml"
            ]
            
            for config_file_path in config_files:
                if Path(config_file_path).exists():
                    shutil.copy2(config_file_path, config_backup_path)
            
            size = self._calculate_directory_size(config_backup_path)
            
            return {
                "success": True,
                "size_bytes": size,
                "path": config_backup_path
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _backup_logs(self, backup_path: str) -> Dict[str, Any]:
        """Backup system logs"""
        try:
            logs_source = f"{self.config.working_dir}/logs"
            logs_backup_path = f"{backup_path}/logs"
            
            if Path(logs_source).exists():
                shutil.copytree(logs_source, logs_backup_path)
                size = self._calculate_directory_size(logs_backup_path)
            else:
                Path(logs_backup_path).mkdir(parents=True, exist_ok=True)
                size = 0
            
            return {
                "success": True,
                "size_bytes": size,
                "path": logs_backup_path
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _backup_metrics(self, backup_path: str) -> Dict[str, Any]:
        """Backup system metrics"""
        try:
            metrics_source = f"{self.config.working_dir}/metrics"
            metrics_backup_path = f"{backup_path}/metrics"
            
            if Path(metrics_source).exists():
                shutil.copytree(metrics_source, metrics_backup_path)
                size = self._calculate_directory_size(metrics_backup_path)
            else:
                Path(metrics_backup_path).mkdir(parents=True, exist_ok=True)
                size = 0
            
            return {
                "success": True,
                "size_bytes": size,
                "path": metrics_backup_path
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _create_archive(self, source_path: str, archive_path: str):
        """Create compressed archive of backup"""
        with tarfile.open(archive_path, 'w:gz') as tar:
            tar.add(source_path, arcname=Path(source_path).name)
    
    def _calculate_backup_size(self, backup_path: str) -> int:
        """Calculate total size of backup directory"""
        return self._calculate_directory_size(backup_path)
    
    def _calculate_directory_size(self, directory: str) -> int:
        """Calculate total size of directory"""
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(directory):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                if os.path.exists(filepath):
                    total_size += os.path.getsize(filepath)
        return total_size
    
    async def restore_backup(self, backup_id: str) -> Dict[str, Any]:
        """
        Restore system from backup
        
        Args:
            backup_id: ID of backup to restore
            
        Returns:
            Restoration results
        """
        try:
            self.logger.info(f"Restoring from backup: {backup_id}")
            
            # Find backup record
            backup_record = None
            for backup in self.backup_metadata["backups"]:
                if backup["backup_id"] == backup_id:
                    backup_record = backup
                    break
            
            if not backup_record:
                raise ValueError(f"Backup not found: {backup_id}")
            
            archive_path = backup_record["archive_path"]
            if not Path(archive_path).exists():
                raise FileNotFoundError(f"Backup archive not found: {archive_path}")
            
            # Create temporary extraction directory
            temp_extract_path = f"{self.backup_dir}/temp_restore_{backup_id}"
            Path(temp_extract_path).mkdir(parents=True, exist_ok=True)
            
            try:
                # Extract archive
                with tarfile.open(archive_path, 'r:gz') as tar:
                    tar.extractall(temp_extract_path)
                
                # Find extracted backup directory
                extracted_dirs = [d for d in Path(temp_extract_path).iterdir() if d.is_dir()]
                if not extracted_dirs:
                    raise ValueError("No backup directory found in archive")
                
                backup_content_path = extracted_dirs[0]
                
                # Load backup manifest
                manifest_file = backup_content_path / "backup_manifest.json"
                with open(manifest_file, 'r') as f:
                    manifest = json.load(f)
                
                # Restore components
                restore_results = {}
                
                # 1. Restore RAG storage
                if "rag_storage" in manifest["components"]:
                    rag_restore_result = await self._restore_rag_storage(backup_content_path)
                    restore_results["rag_storage"] = rag_restore_result
                
                # 2. Restore configuration
                if "configuration" in manifest["components"]:
                    config_restore_result = await self._restore_configuration(backup_content_path)
                    restore_results["configuration"] = config_restore_result
                
                self.logger.info(f"Backup restored successfully: {backup_id}")
                
                return {
                    "success": True,
                    "backup_id": backup_id,
                    "manifest": manifest,
                    "restore_results": restore_results
                }
                
            finally:
                # Clean up temporary extraction directory
                if Path(temp_extract_path).exists():
                    shutil.rmtree(temp_extract_path)
            
        except Exception as e:
            self.logger.error(f"Error restoring backup: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _restore_rag_storage(self, backup_content_path: Path) -> Dict[str, Any]:
        """Restore RAG storage from backup"""
        try:
            rag_backup_path = backup_content_path / "rag_storage"
            rag_storage_path = self.config.working_dir
            
            # Create backup of current storage
            current_backup_path = f"{rag_storage_path}_backup_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
            if Path(rag_storage_path).exists():
                shutil.move(rag_storage_path, current_backup_path)
            
            # Restore from backup
            shutil.copytree(rag_backup_path, rag_storage_path)
            
            return {
                "success": True,
                "current_backup_path": current_backup_path
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _restore_configuration(self, backup_content_path: Path) -> Dict[str, Any]:
        """Restore configuration from backup"""
        try:
            config_backup_path = backup_content_path / "configuration"
            
            # Load backed up configuration
            config_file = config_backup_path / "production_config.json"
            if config_file.exists():
                with open(config_file, 'r') as f:
                    backed_up_config = json.load(f)
                
                return {
                    "success": True,
                    "backed_up_config": backed_up_config
                }
            else:
                return {
                    "success": False,
                    "error": "No configuration found in backup"
                }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def list_backups(self) -> List[Dict[str, Any]]:
        """List all available backups"""
        return self.backup_metadata["backups"]
    
    async def _cleanup_old_backups(self):
        """Clean up old backups based on retention policy"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=self.config.backup_retention_days)
            
            backups_to_remove = []
            for backup in self.backup_metadata["backups"]:
                backup_date = datetime.fromisoformat(backup["timestamp"])
                if backup_date < cutoff_date:
                    backups_to_remove.append(backup)
            
            for backup in backups_to_remove:
                # Remove archive file
                archive_path = backup["archive_path"]
                if Path(archive_path).exists():
                    Path(archive_path).unlink()
                
                # Remove from metadata
                self.backup_metadata["backups"].remove(backup)
                
                self.logger.info(f"Removed old backup: {backup['backup_id']}")
            
            if backups_to_remove:
                await self._save_backup_metadata()
            
        except Exception as e:
            self.logger.error(f"Error cleaning up old backups: {str(e)}")
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check for backup system"""
        try:
            # Check backup directory
            if not Path(self.backup_dir).exists():
                return {
                    "status": "unhealthy",
                    "error": "Backup directory does not exist"
                }
            
            # Check available space
            disk_usage = shutil.disk_usage(self.backup_dir)
            free_space_gb = disk_usage.free / (1024**3)
            
            if free_space_gb < 1:  # Less than 1GB free
                return {
                    "status": "degraded",
                    "warning": f"Low disk space: {free_space_gb:.2f}GB free"
                }
            
            return {
                "status": "healthy",
                "backup_directory": self.backup_dir,
                "total_backups": len(self.backup_metadata["backups"]),
                "last_backup": self.backup_metadata.get("last_backup"),
                "free_space_gb": free_space_gb
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            }
    
    async def cleanup(self):
        """Clean up backup manager"""
        try:
            await self._save_backup_metadata()
            self.logger.info("Backup manager cleanup completed")
        except Exception as e:
            self.logger.error(f"Error during backup cleanup: {str(e)}")