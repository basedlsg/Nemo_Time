"""
GCS Document Loader
Handles loading documents from Google Cloud Storage buckets
"""

import json
import asyncio
from typing import Dict, Any, Optional, List
from google.cloud import storage
from google.api_core import exceptions


class GCSDocumentLoader:
    """
    Loader for documents stored in Google Cloud Storage
    Handles both raw and processed documents
    """
    
    def __init__(self):
        self.client = storage.Client()
        
        # Cache for bucket objects
        self._bucket_cache = {}
    
    async def load_document(self, gcs_path: str) -> Optional[Dict[str, Any]]:
        """
        Load a document from GCS
        
        Args:
            gcs_path: Full GCS path (gs://bucket/path/to/file)
            
        Returns:
            Document data dictionary or None if not found
        """
        try:
            # Parse GCS path
            if not gcs_path.startswith('gs://'):
                raise ValueError(f"Invalid GCS path format: {gcs_path}")
            
            path_parts = gcs_path[5:].split('/', 1)
            bucket_name = path_parts[0]
            blob_path = path_parts[1]
            
            # Get bucket
            bucket = self._get_bucket(bucket_name)
            if not bucket:
                print(f"Bucket not found: {bucket_name}")
                return None
            
            # Get blob
            blob = bucket.blob(blob_path)
            
            if not blob.exists():
                print(f"Document not found: {gcs_path}")
                return None
            
            # Download content
            content = blob.download_as_text(encoding='utf-8')
            
            # Parse based on file extension
            if blob_path.endswith('.json'):
                return json.loads(content)
            else:
                # Assume plain text
                return {
                    'text': content,
                    'gcs_path': gcs_path,
                    'content_type': blob.content_type,
                    'size': blob.size,
                    'updated': blob.updated.isoformat() if blob.updated else None
                }
                
        except Exception as e:
            print(f"Error loading document from GCS {gcs_path}: {str(e)}")
            return None
    
    async def load_documents_from_bucket(
        self,
        bucket_name: str,
        prefix: str = "",
        file_extension: str = ".json"
    ) -> List[Dict[str, Any]]:
        """
        Load multiple documents from a GCS bucket
        
        Args:
            bucket_name: Name of the GCS bucket
            prefix: Prefix to filter files (e.g., "clean/gd/")
            file_extension: File extension to filter (e.g., ".json")
            
        Returns:
            List of document data dictionaries
        """
        try:
            bucket = self._get_bucket(bucket_name)
            if not bucket:
                print(f"Bucket not found: {bucket_name}")
                return []
            
            # List blobs with prefix
            blobs = bucket.list_blobs(prefix=prefix)
            
            documents = []
            for blob in blobs:
                if blob.name.endswith(file_extension):
                    gcs_path = f"gs://{bucket_name}/{blob.name}"
                    doc_data = await self.load_document(gcs_path)
                    if doc_data:
                        documents.append(doc_data)
            
            print(f"Loaded {len(documents)} documents from {bucket_name}/{prefix}")
            return documents
            
        except Exception as e:
            print(f"Error loading documents from bucket {bucket_name}: {str(e)}")
            return []
    
    async def load_documents_by_criteria(
        self,
        bucket_name: str,
        province: Optional[str] = None,
        asset_type: Optional[str] = None,
        doc_class: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Load documents matching specific criteria
        
        Args:
            bucket_name: GCS bucket name
            province: Province filter (gd, sd, nm)
            asset_type: Asset type filter (solar, coal, wind)
            doc_class: Document class filter (grid, permit, etc.)
            
        Returns:
            List of matching documents
        """
        try:
            # Build prefix based on criteria
            prefix_parts = ["clean"]
            
            if province:
                prefix_parts.append(province)
            
            prefix = "/".join(prefix_parts) + "/"
            
            # Load all documents with prefix
            documents = await self.load_documents_from_bucket(
                bucket_name, prefix, ".json"
            )
            
            # Filter by additional criteria
            filtered_documents = []
            for doc in documents:
                if self._matches_criteria(doc, asset_type, doc_class):
                    filtered_documents.append(doc)
            
            print(f"Found {len(filtered_documents)} documents matching criteria")
            return filtered_documents
            
        except Exception as e:
            print(f"Error loading documents by criteria: {str(e)}")
            return []
    
    def _get_bucket(self, bucket_name: str) -> Optional[storage.Bucket]:
        """Get bucket object with caching"""
        
        if bucket_name in self._bucket_cache:
            return self._bucket_cache[bucket_name]
        
        try:
            bucket = self.client.bucket(bucket_name)
            
            # Test bucket access
            bucket.reload()
            
            self._bucket_cache[bucket_name] = bucket
            return bucket
            
        except exceptions.NotFound:
            print(f"Bucket not found: {bucket_name}")
            return None
        except exceptions.Forbidden:
            print(f"Access denied to bucket: {bucket_name}")
            return None
        except Exception as e:
            print(f"Error accessing bucket {bucket_name}: {str(e)}")
            return None
    
    def _matches_criteria(
        self,
        document: Dict[str, Any],
        asset_type: Optional[str] = None,
        doc_class: Optional[str] = None
    ) -> bool:
        """Check if document matches filtering criteria"""
        
        # Check asset type
        if asset_type:
            doc_asset = document.get('asset', '').lower()
            if doc_asset != asset_type.lower():
                return False
        
        # Check document class
        if doc_class:
            doc_class_value = document.get('doc_class', '').lower()
            if doc_class_value != doc_class.lower():
                return False
        
        return True
    
    async def get_bucket_statistics(self, bucket_name: str) -> Dict[str, Any]:
        """Get statistics about documents in a bucket"""
        
        try:
            bucket = self._get_bucket(bucket_name)
            if not bucket:
                return {}
            
            # Count documents by type and location
            stats = {
                'total_files': 0,
                'json_files': 0,
                'provinces': {},
                'asset_types': {},
                'doc_classes': {},
                'total_size_bytes': 0
            }
            
            blobs = bucket.list_blobs()
            
            for blob in blobs:
                stats['total_files'] += 1
                stats['total_size_bytes'] += blob.size or 0
                
                if blob.name.endswith('.json'):
                    stats['json_files'] += 1
                    
                    # Try to extract metadata from path
                    path_parts = blob.name.split('/')
                    if len(path_parts) >= 2:
                        if path_parts[0] == 'clean' and len(path_parts) >= 3:
                            province = path_parts[1]
                            stats['provinces'][province] = stats['provinces'].get(province, 0) + 1
            
            return stats
            
        except Exception as e:
            print(f"Error getting bucket statistics: {str(e)}")
            return {}
    
    async def check_document_exists(self, gcs_path: str) -> bool:
        """Check if a document exists in GCS"""
        
        try:
            # Parse GCS path
            if not gcs_path.startswith('gs://'):
                return False
            
            path_parts = gcs_path[5:].split('/', 1)
            bucket_name = path_parts[0]
            blob_path = path_parts[1]
            
            bucket = self._get_bucket(bucket_name)
            if not bucket:
                return False
            
            blob = bucket.blob(blob_path)
            return blob.exists()
            
        except Exception as e:
            print(f"Error checking document existence: {str(e)}")
            return False
    
    async def save_document(
        self,
        gcs_path: str,
        document_data: Dict[str, Any],
        content_type: str = "application/json"
    ) -> bool:
        """
        Save a document to GCS
        
        Args:
            gcs_path: Full GCS path where to save
            document_data: Document data to save
            content_type: Content type for the blob
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Parse GCS path
            if not gcs_path.startswith('gs://'):
                raise ValueError(f"Invalid GCS path format: {gcs_path}")
            
            path_parts = gcs_path[5:].split('/', 1)
            bucket_name = path_parts[0]
            blob_path = path_parts[1]
            
            bucket = self._get_bucket(bucket_name)
            if not bucket:
                return False
            
            blob = bucket.blob(blob_path)
            
            # Convert to JSON if needed
            if content_type == "application/json":
                content = json.dumps(document_data, ensure_ascii=False, indent=2)
            else:
                content = str(document_data)
            
            # Upload
            blob.upload_from_string(content, content_type=content_type)
            
            print(f"Saved document to: {gcs_path}")
            return True
            
        except Exception as e:
            print(f"Error saving document to GCS: {str(e)}")
            return False