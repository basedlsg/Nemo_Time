"""
Production RAG-Anything System Main Entry Point
Handles deployment, operation, and management of the production system
"""

import asyncio
import argparse
import logging
import sys
from typing import Dict, Any, Optional

from .deployment.production_deployment import deploy_production_system
from .config.production_config import load_production_config
from .monitoring.dashboards import create_monitoring_setup


async def main():
    """Main entry point for production RAG system"""
    parser = argparse.ArgumentParser(description="Production RAG-Anything System")
    parser.add_argument("command", choices=["deploy", "process", "query", "backup", "restore", "health", "metrics", "setup-monitoring"])
    parser.add_argument("--bucket", help="GCS bucket name for document processing")
    parser.add_argument("--max-docs", type=int, help="Maximum number of documents to process")
    parser.add_argument("--question", help="Question to query")
    parser.add_argument("--backup-id", help="Backup ID for restore operation")
    parser.add_argument("--config-file", help="Path to configuration file")
    parser.add_argument("--log-level", default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR"])
    
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)
    
    try:
        if args.command == "deploy":
            logger.info("Deploying production RAG system...")
            deployment = await deploy_production_system()
            logger.info("Deployment completed successfully")
            
            # Keep system running
            logger.info("Production system is running. Press Ctrl+C to shutdown.")
            try:
                while True:
                    await asyncio.sleep(60)
                    # Perform periodic health checks
                    health = await deployment.health_check()
                    if health["status"] != "healthy":
                        logger.warning(f"System health check: {health['status']}")
            except KeyboardInterrupt:
                logger.info("Shutting down...")
                await deployment.shutdown()
        
        elif args.command == "process":
            if not args.bucket:
                logger.error("--bucket is required for process command")
                sys.exit(1)
            
            logger.info(f"Processing documents from bucket: {args.bucket}")
            deployment = await deploy_production_system()
            
            results = await deployment.process_document_corpus(
                bucket_name=args.bucket,
                max_documents=args.max_docs
            )
            
            logger.info(f"Processing completed: {results['successful']}/{results['total_documents']} successful")
            print(f"Processing Results: {results}")
            
            await deployment.shutdown()
        
        elif args.command == "query":
            if not args.question:
                logger.error("--question is required for query command")
                sys.exit(1)
            
            logger.info(f"Querying: {args.question}")
            deployment = await deploy_production_system()
            
            result = await deployment.query_documents(args.question)
            
            print(f"Query Result: {result}")
            
            await deployment.shutdown()
        
        elif args.command == "backup":
            logger.info("Creating system backup...")
            deployment = await deploy_production_system()
            
            backup_result = await deployment.create_backup("manual")
            
            logger.info(f"Backup created: {backup_result.get('backup_id')}")
            print(f"Backup Result: {backup_result}")
            
            await deployment.shutdown()
        
        elif args.command == "restore":
            if not args.backup_id:
                logger.error("--backup-id is required for restore command")
                sys.exit(1)
            
            logger.info(f"Restoring from backup: {args.backup_id}")
            deployment = await deploy_production_system()
            
            restore_result = await deployment.restore_backup(args.backup_id)
            
            logger.info(f"Restore completed: {restore_result.get('success')}")
            print(f"Restore Result: {restore_result}")
            
            await deployment.shutdown()
        
        elif args.command == "health":
            logger.info("Checking system health...")
            deployment = await deploy_production_system()
            
            health = await deployment.health_check()
            
            print(f"Health Status: {health}")
            
            await deployment.shutdown()
        
        elif args.command == "metrics":
            logger.info("Getting system metrics...")
            deployment = await deploy_production_system()
            
            metrics = await deployment.get_system_metrics()
            
            print(f"System Metrics: {metrics}")
            
            await deployment.shutdown()
        
        elif args.command == "setup-monitoring":
            logger.info("Setting up monitoring dashboards...")
            config = load_production_config()
            
            monitoring_setup = create_monitoring_setup(config)
            
            logger.info("Monitoring setup completed")
            print("Monitoring dashboards and configurations created in monitoring directory")
    
    except Exception as e:
        logger.error(f"Command failed: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())