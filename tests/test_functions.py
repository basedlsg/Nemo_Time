"""
Unit tests for Cloud Function handlers
Tests query, ingest, and health function endpoints
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
import json
import sys
import os

# Add function directories to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'functions', 'query'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'functions', 'ingest'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'functions', 'health'))

from main import query_handler, ingest_handler, health_handler


class TestQueryFunction:
    """Test query Cloud Function handler"""
    
    def test_query_handler_valid_request(self):
        """Test query handler with valid request"""
        request_data = {
            'province': 'gd',
            'asset': 'solar',
            'doc_class': 'grid',
            'question': '光伏并网验收需要什么资料？',
            'lang': 'zh-CN'
        }
        
        mock_request = Mock()
        mock_request.get_json.return_value = request_data
        mock_request.method = 'POST'
        
        with patch('main.search_documents') as mock_search, \
             patch('main.compose_response') as mock_compose:
            
            mock_search.return_value = [
                {
                    'content': '验收需要提交核准文件',
                    'metadata': {'title': '验收办法', 'url': 'https://gd.gov.cn/doc'}
                }
            ]
            
            mock_compose.return_value = {
                'answer_zh': '验收需要提交核准文件',
                'citations': [{'title': '验收办法', 'url': 'https://gd.gov.cn/doc'}]
            }
            
            response = query_handler(mock_request)
        
        assert response[1] == 200  # Status code
        response_data = json.loads(response[0])
        assert 'answer_zh' in response_data
        assert 'citations' in response_data
        assert 'trace_id' in response_data
        assert 'elapsed_ms' in response_data
    
    def test_query_handler_missing_fields(self):
        """Test query handler with missing required fields"""
        request_data = {
            'province': 'gd',
            # Missing asset, doc_class, question
        }
        
        mock_request = Mock()
        mock_request.get_json.return_value = request_data
        mock_request.method = 'POST'
        
        response = query_handler(mock_request)
        
        assert response[1] == 400  # Bad request
        response_data = json.loads(response[0])
        assert 'error' in response_data
        assert 'trace_id' in response_data
    
    def test_query_handler_invalid_province(self):
        """Test query handler with invalid province"""
        request_data = {
            'province': 'invalid',
            'asset': 'solar',
            'doc_class': 'grid',
            'question': '测试问题'
        }
        
        mock_request = Mock()
        mock_request.get_json.return_value = request_data
        mock_request.method = 'POST'
        
        response = query_handler(mock_request)
        
        assert response[1] == 400
        response_data = json.loads(response[0])
        assert 'error' in response_data
    
    def test_query_handler_get_method(self):
        """Test query handler rejects GET requests"""
        mock_request = Mock()
        mock_request.method = 'GET'
        
        response = query_handler(mock_request)
        
        assert response[1] == 405  # Method not allowed
    
    def test_query_handler_internal_error(self):
        """Test query handler handles internal errors"""
        request_data = {
            'province': 'gd',
            'asset': 'solar',
            'doc_class': 'grid',
            'question': '测试问题'
        }
        
        mock_request = Mock()
        mock_request.get_json.return_value = request_data
        mock_request.method = 'POST'
        
        with patch('main.search_documents', side_effect=Exception("Internal error")):
            response = query_handler(mock_request)
        
        assert response[1] == 500
        response_data = json.loads(response[0])
        assert 'error' in response_data
        assert 'trace_id' in response_data


class TestIngestFunction:
    """Test ingest Cloud Function handler"""
    
    def test_ingest_handler_valid_request(self):
        """Test ingest handler with valid request and token"""
        request_data = {
            'province': 'gd',
            'asset': 'solar',
            'doc_class': 'grid'
        }
        
        mock_request = Mock()
        mock_request.get_json.return_value = request_data
        mock_request.method = 'POST'
        mock_request.headers = {'X-Ingest-Token': 'nemo-ingest-secure-token-2025'}
        
        with patch('main.discover_documents') as mock_discover, \
             patch('main.process_documents') as mock_process:
            
            mock_discover.return_value = [
                {'title': '测试文档', 'url': 'https://gd.gov.cn/test.pdf'}
            ]
            mock_process.return_value = {'processed': 1, 'errors': 0}
            
            response = ingest_handler(mock_request)
        
        assert response[1] == 202  # Accepted
        response_data = json.loads(response[0])
        assert response_data['accepted'] == True
        assert 'job_id' in response_data
    
    def test_ingest_handler_missing_token(self):
        """Test ingest handler rejects requests without token"""
        request_data = {
            'province': 'gd',
            'asset': 'solar',
            'doc_class': 'grid'
        }
        
        mock_request = Mock()
        mock_request.get_json.return_value = request_data
        mock_request.method = 'POST'
        mock_request.headers = {}  # No token
        
        response = ingest_handler(mock_request)
        
        assert response[1] == 403  # Forbidden
        response_data = json.loads(response[0])
        assert 'error' in response_data
    
    def test_ingest_handler_invalid_token(self):
        """Test ingest handler rejects invalid token"""
        request_data = {
            'province': 'gd',
            'asset': 'solar',
            'doc_class': 'grid'
        }
        
        mock_request = Mock()
        mock_request.get_json.return_value = request_data
        mock_request.method = 'POST'
        mock_request.headers = {'X-Ingest-Token': 'invalid-token'}
        
        response = ingest_handler(mock_request)
        
        assert response[1] == 403
    
    def test_ingest_handler_missing_fields(self):
        """Test ingest handler with missing required fields"""
        request_data = {
            'province': 'gd'
            # Missing asset, doc_class
        }
        
        mock_request = Mock()
        mock_request.get_json.return_value = request_data
        mock_request.method = 'POST'
        mock_request.headers = {'X-Ingest-Token': 'nemo-ingest-secure-token-2025'}
        
        response = ingest_handler(mock_request)
        
        assert response[1] == 400
        response_data = json.loads(response[0])
        assert 'error' in response_data


class TestHealthFunction:
    """Test health Cloud Function handler"""
    
    def test_health_handler_success(self):
        """Test health handler returns system status"""
        mock_request = Mock()
        mock_request.method = 'GET'
        
        with patch.dict(os.environ, {
            'REGION': 'asia-east2',
            'COMMIT_HASH': 'abc123',
            'GOOGLE_CLOUD_PROJECT': 'test-project'
        }):
            response = health_handler(mock_request)
        
        assert response[1] == 200
        response_data = json.loads(response[0])
        assert 'status' in response_data
        assert 'timestamp' in response_data
        assert 'commit' in response_data
        assert 'region' in response_data
        assert response_data['commit'] == 'abc123'
        assert response_data['region'] == 'asia-east2'
    
    def test_health_handler_post_method(self):
        """Test health handler accepts POST requests too"""
        mock_request = Mock()
        mock_request.method = 'POST'
        
        response = health_handler(mock_request)
        
        assert response[1] == 200
        response_data = json.loads(response[0])
        assert 'status' in response_data
    
    @patch('main.check_vertex_ai_connectivity')
    def test_health_handler_vertex_ai_check(self, mock_vertex_check):
        """Test health handler checks Vertex AI connectivity"""
        mock_request = Mock()
        mock_request.method = 'GET'
        mock_vertex_check.return_value = True
        
        response = health_handler(mock_request)
        
        assert response[1] == 200
        response_data = json.loads(response[0])
        assert response_data['status'] in ['ok', 'degraded']
    
    @patch('main.check_vertex_ai_connectivity')
    def test_health_handler_vertex_ai_failure(self, mock_vertex_check):
        """Test health handler handles Vertex AI connectivity issues"""
        mock_request = Mock()
        mock_request.method = 'GET'
        mock_vertex_check.return_value = False
        
        response = health_handler(mock_request)
        
        assert response[1] == 200  # Still returns 200 but with degraded status
        response_data = json.loads(response[0])
        assert response_data['status'] == 'degraded'
    
    def test_health_handler_missing_env_vars(self):
        """Test health handler with missing environment variables"""
        mock_request = Mock()
        mock_request.method = 'GET'
        
        with patch.dict(os.environ, {}, clear=True):
            response = health_handler(mock_request)
        
        assert response[1] == 200
        response_data = json.loads(response[0])
        assert 'status' in response_data
        # Should still work with defaults


if __name__ == "__main__":
    pytest.main([__file__, "-v"])