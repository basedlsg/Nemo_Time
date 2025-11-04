"""
Unit tests for Google Custom Search Engine (CSE) module
Tests document discovery and URL validation
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add lib directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'lib'))

from cse import discover_documents, validate_government_domain, build_search_query, fetch_document


class TestCSE:
    """Test Google Custom Search Engine functionality"""
    
    def test_validate_government_domain_valid(self):
        """Test validation of valid government domains"""
        valid_urls = [
            'https://gd.gov.cn/document.pdf',
            'http://sd.gov.cn/policy/file.docx',
            'https://nmg.gov.cn/regulations/rule.pdf',
            'https://www.gd.gov.cn/subdir/file.pdf'
        ]
        
        for url in valid_urls:
            assert validate_government_domain(url) == True
    
    def test_validate_government_domain_invalid(self):
        """Test validation rejects non-government domains"""
        invalid_urls = [
            'https://example.com/document.pdf',
            'http://fake-gov.cn/file.pdf',
            'https://gd.com/document.pdf',  # Missing .gov
            'https://malicious.site/gd.gov.cn/fake.pdf',  # Domain spoofing
            'ftp://gd.gov.cn/file.pdf',  # Non-HTTP protocol
            ''  # Empty URL
        ]
        
        for url in invalid_urls:
            assert validate_government_domain(url) == False
    
    def test_build_search_query_guangdong_solar(self):
        """Test search query building for Guangdong solar projects"""
        query = build_search_query('gd', 'solar', 'grid')
        
        assert 'site:gd.gov.cn' in query
        assert '光伏' in query or 'solar' in query.lower()
        assert '并网' in query or 'grid' in query.lower()
        assert 'filetype:pdf OR filetype:doc OR filetype:docx' in query
    
    def test_build_search_query_shandong_wind(self):
        """Test search query building for Shandong wind projects"""
        query = build_search_query('sd', 'wind', 'grid')
        
        assert 'site:sd.gov.cn' in query
        assert '风电' in query or 'wind' in query.lower()
        assert '并网' in query or 'grid' in query.lower()
    
    def test_build_search_query_inner_mongolia_coal(self):
        """Test search query building for Inner Mongolia coal projects"""
        query = build_search_query('nm', 'coal', 'grid')
        
        assert 'site:nmg.gov.cn' in query
        assert '煤电' in query or 'coal' in query.lower()
        assert '并网' in query or 'grid' in query.lower()
    
    def test_build_search_query_invalid_province(self):
        """Test search query building with invalid province"""
        with pytest.raises(ValueError):
            build_search_query('invalid', 'solar', 'grid')
    
    def test_build_search_query_invalid_asset(self):
        """Test search query building with invalid asset type"""
        with pytest.raises(ValueError):
            build_search_query('gd', 'invalid', 'grid')
    
    @patch('requests.get')
    def test_discover_documents_success(self, mock_get):
        """Test successful document discovery"""
        # Mock CSE API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'items': [
                {
                    'title': '广东省光伏发电项目管理办法',
                    'link': 'https://gd.gov.cn/doc1.pdf',
                    'snippet': '光伏发电项目并网管理规定...'
                },
                {
                    'title': '分布式光伏并网技术要求',
                    'link': 'https://gd.gov.cn/doc2.pdf',
                    'snippet': '分布式光伏发电系统并网技术标准...'
                }
            ]
        }
        mock_get.return_value = mock_response
        
        # Mock environment variables
        with patch.dict(os.environ, {
            'GOOGLE_CSE_ID': 'test-cse-id',
            'GOOGLE_API_KEY': 'test-api-key'
        }):
            documents = discover_documents('gd', 'solar', 'grid')
        
        assert len(documents) == 2
        assert documents[0]['title'] == '广东省光伏发电项目管理办法'
        assert documents[0]['url'] == 'https://gd.gov.cn/doc1.pdf'
        assert 'snippet' in documents[0]
    
    @patch('requests.get')
    def test_discover_documents_filters_invalid_domains(self, mock_get):
        """Test that document discovery filters out invalid domains"""
        # Mock CSE API response with mixed valid/invalid domains
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'items': [
                {
                    'title': '合法政府文件',
                    'link': 'https://gd.gov.cn/valid.pdf',
                    'snippet': '正规政府文件内容...'
                },
                {
                    'title': '非政府网站文件',
                    'link': 'https://example.com/invalid.pdf',
                    'snippet': '非政府网站内容...'
                },
                {
                    'title': '另一个合法文件',
                    'link': 'https://gd.gov.cn/valid2.pdf',
                    'snippet': '另一个正规政府文件...'
                }
            ]
        }
        mock_get.return_value = mock_response
        
        with patch.dict(os.environ, {
            'GOOGLE_CSE_ID': 'test-cse-id',
            'GOOGLE_API_KEY': 'test-api-key'
        }):
            documents = discover_documents('gd', 'solar', 'grid')
        
        # Should only return valid government domain documents
        assert len(documents) == 2
        assert all('gd.gov.cn' in doc['url'] for doc in documents)
    
    @patch('requests.get')
    def test_discover_documents_api_error(self, mock_get):
        """Test document discovery handles API errors gracefully"""
        mock_response = Mock()
        mock_response.status_code = 403
        mock_response.json.return_value = {'error': 'API quota exceeded'}
        mock_get.return_value = mock_response
        
        with patch.dict(os.environ, {
            'GOOGLE_CSE_ID': 'test-cse-id',
            'GOOGLE_API_KEY': 'test-api-key'
        }):
            documents = discover_documents('gd', 'solar', 'grid')
        
        # Should return empty list on API error
        assert len(documents) == 0
    
    @patch('requests.get')
    def test_discover_documents_no_results(self, mock_get):
        """Test document discovery when no results found"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {}  # No 'items' key
        mock_get.return_value = mock_response
        
        with patch.dict(os.environ, {
            'GOOGLE_CSE_ID': 'test-cse-id',
            'GOOGLE_API_KEY': 'test-api-key'
        }):
            documents = discover_documents('gd', 'solar', 'grid')
        
        assert len(documents) == 0
    
    def test_discover_documents_missing_credentials(self):
        """Test document discovery fails gracefully without credentials"""
        with patch.dict(os.environ, {}, clear=True):
            documents = discover_documents('gd', 'solar', 'grid')
            assert len(documents) == 0
    
    @patch('requests.get')
    def test_fetch_document_success(self, mock_get):
        """Test successful document fetching"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b'PDF content here'
        mock_response.headers = {'content-type': 'application/pdf'}
        mock_get.return_value = mock_response
        
        content, content_type = fetch_document('https://gd.gov.cn/test.pdf')
        
        assert content == b'PDF content here'
        assert content_type == 'application/pdf'
    
    @patch('requests.get')
    def test_fetch_document_http_error(self, mock_get):
        """Test document fetching handles HTTP errors"""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response
        
        content, content_type = fetch_document('https://gd.gov.cn/missing.pdf')
        
        assert content is None
        assert content_type is None
    
    @patch('requests.get')
    def test_fetch_document_timeout(self, mock_get):
        """Test document fetching handles timeouts"""
        mock_get.side_effect = Exception("Connection timeout")
        
        content, content_type = fetch_document('https://gd.gov.cn/slow.pdf')
        
        assert content is None
        assert content_type is None
    
    def test_fetch_document_invalid_url(self):
        """Test document fetching rejects invalid URLs"""
        content, content_type = fetch_document('https://malicious.com/fake.pdf')
        
        assert content is None
        assert content_type is None
    
    @patch('requests.get')
    def test_discover_documents_deduplication(self, mock_get):
        """Test that duplicate URLs are filtered out"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'items': [
                {
                    'title': '文件1',
                    'link': 'https://gd.gov.cn/doc.pdf',
                    'snippet': '内容1...'
                },
                {
                    'title': '文件2',
                    'link': 'https://gd.gov.cn/doc.pdf',  # Duplicate URL
                    'snippet': '内容2...'
                },
                {
                    'title': '文件3',
                    'link': 'https://gd.gov.cn/other.pdf',
                    'snippet': '内容3...'
                }
            ]
        }
        mock_get.return_value = mock_response
        
        with patch.dict(os.environ, {
            'GOOGLE_CSE_ID': 'test-cse-id',
            'GOOGLE_API_KEY': 'test-api-key'
        }):
            documents = discover_documents('gd', 'solar', 'grid')
        
        # Should deduplicate URLs
        assert len(documents) == 2
        urls = [doc['url'] for doc in documents]
        assert len(set(urls)) == len(urls)  # All URLs should be unique


if __name__ == "__main__":
    pytest.main([__file__, "-v"])