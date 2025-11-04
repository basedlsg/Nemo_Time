"""
Nemo Compliance MVP - Health Check Cloud Function
Provides system status and connectivity validation
"""

import os
import json
import time
from datetime import datetime
from typing import Dict, Any
import functions_framework
from flask import Request, make_response

# Import shared libraries for connectivity checks
import sys
sys.path.append('../../lib')


@functions_framework.http
def health_handler(request: Request) -> Dict[str, Any]:
    """
    Health check endpoint that validates system components
    
    Returns system status, timestamp, commit hash, and service connectivity
    """
    
    try:
        # CORS preflight
        if request.method == 'OPTIONS':
            return _cors_response({}, 204)
        # Basic system info
        health_data = {
            'status': 'ok',
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'commit': os.environ.get('COMMIT_HASH', 'unknown'),
            'region': os.environ.get('REGION', 'unknown')
        }
        
        # Check Vertex AI connectivity
        try:
            vertex_status = _check_vertex_ai()
            health_data['vertex_index_status'] = vertex_status
        except Exception as e:
            health_data['vertex_index_status'] = f'error: {str(e)}'
            health_data['status'] = 'degraded'
            
        # Check GCS connectivity
        try:
            gcs_status = _check_gcs_buckets()
            health_data['gcs_status'] = gcs_status
        except Exception as e:
            health_data['gcs_status'] = f'error: {str(e)}'
            health_data['status'] = 'degraded'
            
        # Check Secret Manager
        try:
            secrets_status = _check_secret_manager()
            health_data['secrets_status'] = secrets_status
        except Exception as e:
            health_data['secrets_status'] = f'error: {str(e)}'
            health_data['status'] = 'degraded'
            
        return _cors_response(health_data, 200)
        
    except Exception as e:
        return _cors_response({
            'status': 'error',
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'error': str(e)
        }, 200)


def _check_vertex_ai() -> str:
    """Check Vertex AI Vector Search connectivity"""
    
    try:
        # Import here to avoid startup delays
        from vertex_index import get_index_status
        
        index_id = os.environ.get('VERTEX_INDEX_ID')
        endpoint_id = os.environ.get('VERTEX_ENDPOINT_ID')
        
        if not index_id or not endpoint_id:
            return 'not_configured'
            
        # Check if index is accessible
        status = get_index_status(index_id, endpoint_id)
        return status
        
    except ImportError:
        return 'module_not_available'
    except Exception as e:
        return f'error: {str(e)}'


def _cors_response(data: Dict[str, Any], status: int = 200):
    body = json.dumps(data, ensure_ascii=False)
    resp = make_response(body, status)
    resp.headers['Content-Type'] = 'application/json; charset=utf-8'
    resp.headers['Access-Control-Allow-Origin'] = '*'
    resp.headers['Access-Control-Allow-Methods'] = 'GET,POST,OPTIONS'
    resp.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization,X-Ingest-Token'
    resp.headers['Access-Control-Max-Age'] = '3600'
    return resp


def _check_gcs_buckets() -> str:
    """Check GCS bucket accessibility"""
    
    try:
        from google.cloud import storage
        
        client = storage.Client()
        
        raw_bucket = os.environ.get('BUCKET_RAW')
        clean_bucket = os.environ.get('BUCKET_CLEAN')
        
        if not raw_bucket or not clean_bucket:
            return 'not_configured'
            
        # Test bucket access
        raw_bucket_obj = client.bucket(raw_bucket)
        clean_bucket_obj = client.bucket(clean_bucket)
        
        # Simple existence check
        raw_exists = raw_bucket_obj.exists()
        clean_exists = clean_bucket_obj.exists()
        
        if raw_exists and clean_exists:
            return 'healthy'
        else:
            return f'buckets_missing: raw={raw_exists}, clean={clean_exists}'
            
    except Exception as e:
        return f'error: {str(e)}'


def _check_secret_manager() -> str:
    """Check Secret Manager connectivity"""
    
    try:
        from google.cloud import secretmanager
        
        client = secretmanager.SecretManagerServiceClient()
        
        # Test basic connectivity by listing secrets (limited to project)
        project_id = os.environ.get('GOOGLE_CLOUD_PROJECT')
        if not project_id:
            return 'project_not_configured'
            
        parent = f"projects/{project_id}"
        
        # This will fail if no access, confirming connectivity
        response = client.list_secrets(request={"parent": parent})
        
        # Just check if we can iterate (don't need to count)
        try:
            next(iter(response))
        except StopIteration:
            pass  # Empty is fine
            
        return 'healthy'
        
    except Exception as e:
        return f'error: {str(e)}'
