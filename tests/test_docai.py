"""
Unit tests for Document AI integration module
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import os
import json
from lib.docai import (
    process_document, _download_document, _store_raw_document,
    _extract_text_with_docai, _store_clean_document, validate_document_quality,
    get_document_from_gcs, check_document_exists, _get_current_timestamp
)


class TestProcessDocument:
    """Test main document processing functionality"""
    
    @patch('lib.docai._download_document')
    @patch('lib.docai._store_raw_document')
    @patch('lib.docai._extract_text_with_docai')
    @patch('lib.docai._store_clean_document')
    @patch('lib.docai.normalize_text')
    @patch('lib.docai.extract_title_from_text')
    @patch('lib.docai.extract_effective_date')
    def test_process_document_success(self, mock_extract_date, mock_extract_title,
                                    mock_normalize, mock_store_clean, mock_extract_text,
                                    mock_store_raw, mock_download):
        """Test successful document processing"""
        
        # Mock the pipeline
        mock_download.return_value = (b'fake pdf content', 'application/pdf')
        mock_store_raw.return_value = 'gs://bucket/raw/doc.pdf'
        mock_extract_text.return_value = '广东省光伏并网管理办法第一条...'
        mock_normalize.return_value = '广东省光伏并网管理办法第一条...'
        mock_extract_title.return_value = '广东省光伏并网管理办法'
        mock_extract_date.return_value = '2024-06-01'
        mock_store_clean.return_value = 'gs://bucket/clean/doc.json'
        
        result = process_document(
            url='https://gd.gov.cn/test.pdf',
            province='gd',
            asset='solar',
            doc_class='grid'
        )
        
        assert result is not None
        assert result['title'] == '广东省光伏并网管理办法'
        assert result['effective_date'] == '2024-06-01'
        assert result['province'] == 'gd'
        assert result['asset'] == 'solar'
        assert result['doc_class'] == 'grid'
        assert 'checksum' in result
        
    @patch('lib.docai._download_document')
    def test_process_document_download_failure(self, mock_download):
        """Test handling of download failure"""
        mock_download.return_value = (None, None)
        
        result = process_document(
            url='https://invalid-url.com/doc.pdf',
            province='gd',
            asset='solar',
            doc_class='grid'
        )
        
        assert result is None
        
    @patch('lib.docai._download_document')
    @patch('lib.docai._store_raw_document')
    @patch('lib.docai._extract_text_with_docai')
    def test_process_document_extraction_failure(self, mock_extract_text,
                                               mock_store_raw, mock_download):
        """Test handling of text extraction failure"""
        mock_download.return_value = (b'fake content', 'application/pdf')
        mock_store_raw.return_value = 'gs://bucket/raw/doc.pdf'
        mock_extract_text.return_value = None  # Extraction failed
        
        result = process_document(
            url='https://gd.gov.cn/test.pdf',
            province='gd',
            asset='solar',
            doc_class='grid'
        )
        
        assert result is None


class TestDownloadDocument:
    """Test document downloading functionality"""
    
    @patch('requests.get')
    def test_download_success(self, mock_get):
        """Test successful document download"""
        mock_response = Mock()
        mock_response.content = b'fake pdf content'
        mock_response.headers = {'content-type': 'application/pdf'}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        content, mime_type = _download_document('https://test.gov.cn/doc.pdf')
        
        assert content == b'fake pdf content'
        assert mime_type == 'application/pdf'
        
    @patch('requests.get')
    def test_download_unsupported_mime_type(self, mock_get):
        """Test handling of unsupported MIME type"""
        mock_response = Mock()
        mock_response.content = b'fake content'
        mock_response.headers = {'content-type': 'image/jpeg'}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        content, mime_type = _download_document('https://test.gov.cn/image.jpg')
        
        assert content is None
        assert mime_type is None
        
    @patch('requests.get')
    def test_download_too_large(self, mock_get):
        """Test handling of documents that are too large"""
        mock_response = Mock()
        mock_response.headers = {'content-length': str(100 * 1024 * 1024)}  # 100MB
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        content, mime_type = _download_document('https://test.gov.cn/large.pdf')
        
        assert content is None
        assert mime_type is None
        
    @patch('requests.get')
    def test_download_network_error(self, mock_get):
        """Test handling of network errors"""
        mock_get.side_effect = requests.RequestException("Network error")
        
        content, mime_type = _download_document('https://invalid-url.com/doc.pdf')
        
        assert content is None
        assert mime_type is None


class TestStoreRawDocument:
    """Test raw document storage functionality"""
    
    @patch('lib.docai.storage.Client')
    def test_store_raw_success(self, mock_storage_client):
        """Test successful raw document storage"""
        # Mock GCS client
        mock_client = Mock()
        mock_bucket = Mock()
        mock_blob = Mock()
        
        mock_blob.exists.return_value = False
        mock_blob.upload_from_string.return_value = None
        mock_bucket.blob.return_value = mock_blob
        mock_client.bucket.return_value = mock_bucket
        mock_storage_client.return_value = mock_client
        
        os.environ['BUCKET_RAW'] = 'test-bucket-raw'
        
        result = _store_raw_document(
            content=b'fake pdf content',
            checksum='abc123',
            mime_type='application/pdf',
            province='gd'
        )
        
        assert result is not None
        assert result.startswith('gs://test-bucket-raw/raw/gd/')
        assert result.endswith('abc123.pdf')
        
    @patch('lib.docai.storage.Client')
    def test_store_raw_already_exists(self, mock_storage_client):
        """Test handling when document already exists"""
        mock_client = Mock()
        mock_bucket = Mock()
        mock_blob = Mock()
        
        mock_blob.exists.return_value = True  # Already exists
        mock_bucket.blob.return_value = mock_blob
        mock_client.bucket.return_value = mock_bucket
        mock_storage_client.return_value = mock_client
        
        os.environ['BUCKET_RAW'] = 'test-bucket-raw'
        
        result = _store_raw_document(
            content=b'fake content',
            checksum='abc123',
            mime_type='application/pdf',
            province='gd'
        )
        
        assert result is not None
        # Should not call upload since it already exists
        mock_blob.upload_from_string.assert_not_called()
        
    def test_store_raw_missing_bucket(self):
        """Test handling when bucket environment variable is missing"""
        if 'BUCKET_RAW' in os.environ:
            del os.environ['BUCKET_RAW']
            
        result = _store_raw_document(
            content=b'fake content',
            checksum='abc123',
            mime_type='application/pdf',
            province='gd'
        )
        
        assert result is None


class TestExtractTextWithDocAI:
    """Test Document AI text extraction"""
    
    @patch('lib.docai.documentai.DocumentProcessorServiceClient')
    def test_extract_text_success(self, mock_client_class):
        """Test successful text extraction"""
        # Mock Document AI client and response
        mock_client = Mock()
        mock_document = Mock()
        mock_document.text = '广东省光伏并网管理办法第一条为规范光伏发电项目并网管理...'
        
        mock_result = Mock()
        mock_result.document = mock_document
        
        mock_client.process_document.return_value = mock_result
        mock_client_class.return_value = mock_client
        
        # Set environment variables
        os.environ['GOOGLE_CLOUD_PROJECT'] = 'test-project'
        os.environ['DOCAI_PROCESSOR_ID'] = 'test-processor'
        
        result = _extract_text_with_docai(
            gcs_path='gs://bucket/raw/doc.pdf',
            mime_type='application/pdf'
        )
        
        assert result == '广东省光伏并网管理办法第一条为规范光伏发电项目并网管理...'
        
    @patch('lib.docai.documentai.DocumentProcessorServiceClient')
    def test_extract_text_empty_result(self, mock_client_class):
        """Test handling of empty extraction result"""
        mock_client = Mock()
        mock_document = Mock()
        mock_document.text = ''  # Empty text
        
        mock_result = Mock()
        mock_result.document = mock_document
        
        mock_client.process_document.return_value = mock_result
        mock_client_class.return_value = mock_client
        
        os.environ['GOOGLE_CLOUD_PROJECT'] = 'test-project'
        os.environ['DOCAI_PROCESSOR_ID'] = 'test-processor'
        
        result = _extract_text_with_docai(
            gcs_path='gs://bucket/raw/doc.pdf',
            mime_type='application/pdf'
        )
        
        assert result is None
        
    def test_extract_text_missing_config(self):
        """Test handling of missing configuration"""
        # Clear environment variables
        for var in ['GOOGLE_CLOUD_PROJECT', 'DOCAI_PROCESSOR_ID']:
            if var in os.environ:
                del os.environ[var]
                
        result = _extract_text_with_docai(
            gcs_path='gs://bucket/raw/doc.pdf',
            mime_type='application/pdf'
        )
        
        assert result is None


class TestStoreCleanDocument:
    """Test clean document storage functionality"""
    
    @patch('lib.docai.storage.Client')
    def test_store_clean_success(self, mock_storage_client):
        """Test successful clean document storage"""
        mock_client = Mock()
        mock_bucket = Mock()
        mock_blob = Mock()
        
        mock_blob.upload_from_string.return_value = None
        mock_bucket.blob.return_value = mock_blob
        mock_client.bucket.return_value = mock_bucket
        mock_storage_client.return_value = mock_client
        
        os.environ['BUCKET_CLEAN'] = 'test-bucket-clean'
        
        doc_data = {
            'title': '测试文档',
            'text': '文档内容',
            'province': 'gd'
        }
        
        result = _store_clean_document(doc_data, 'abc123', 'gd')
        
        assert result == 'gs://test-bucket-clean/clean/gd/abc123.json'
        mock_blob.upload_from_string.assert_called_once()
        
        # Check that JSON was properly formatted
        call_args = mock_blob.upload_from_string.call_args
        json_content = call_args[0][0]
        parsed_data = json.loads(json_content)
        assert parsed_data['title'] == '测试文档'


class TestValidateDocumentQuality:
    """Test document quality validation"""
    
    @patch('lib.docai.validate_chinese_content_quality')
    def test_validate_quality_success(self, mock_validate_chinese):
        """Test successful quality validation"""
        mock_validate_chinese.return_value = {'is_valid': True}
        
        doc_data = {
            'text': '这是一个足够长的中文文档内容，包含了足够的信息用于验证文档质量。' * 5,
            'title': '测试文档',
            'url': 'https://test.gov.cn',
            'province': 'gd',
            'asset': 'solar',
            'doc_class': 'grid'
        }
        
        result = validate_document_quality(doc_data)
        assert result is True
        
    def test_validate_quality_too_short(self):
        """Test validation failure for short documents"""
        doc_data = {
            'text': '短文档',  # Too short
            'title': '测试文档',
            'url': 'https://test.gov.cn',
            'province': 'gd',
            'asset': 'solar',
            'doc_class': 'grid'
        }
        
        result = validate_document_quality(doc_data)
        assert result is False
        
    @patch('lib.docai.validate_chinese_content_quality')
    def test_validate_quality_poor_chinese(self, mock_validate_chinese):
        """Test validation failure for poor Chinese content"""
        mock_validate_chinese.return_value = {'is_valid': False}
        
        doc_data = {
            'text': 'This is mostly English content with very little Chinese content.' * 10,
            'title': '测试文档',
            'url': 'https://test.gov.cn',
            'province': 'gd',
            'asset': 'solar',
            'doc_class': 'grid'
        }
        
        result = validate_document_quality(doc_data)
        assert result is False
        
    def test_validate_quality_missing_fields(self):
        """Test validation failure for missing required fields"""
        doc_data = {
            'text': '这是一个足够长的中文文档内容。' * 10,
            'title': '测试文档',
            # Missing url, province, asset, doc_class
        }
        
        result = validate_document_quality(doc_data)
        assert result is False


class TestGetDocumentFromGCS:
    """Test document retrieval from GCS"""
    
    @patch('lib.docai.storage.Client')
    def test_get_document_success(self, mock_storage_client):
        """Test successful document retrieval"""
        mock_client = Mock()
        mock_bucket = Mock()
        mock_blob = Mock()
        
        doc_data = {'title': '测试文档', 'text': '文档内容'}
        json_content = json.dumps(doc_data, ensure_ascii=False)
        
        mock_blob.exists.return_value = True
        mock_blob.download_as_text.return_value = json_content
        mock_bucket.blob.return_value = mock_blob
        mock_client.bucket.return_value = mock_bucket
        mock_storage_client.return_value = mock_client
        
        result = get_document_from_gcs('gs://test-bucket/clean/doc.json')
        
        assert result == doc_data
        
    @patch('lib.docai.storage.Client')
    def test_get_document_not_found(self, mock_storage_client):
        """Test handling when document is not found"""
        mock_client = Mock()
        mock_bucket = Mock()
        mock_blob = Mock()
        
        mock_blob.exists.return_value = False
        mock_bucket.blob.return_value = mock_blob
        mock_client.bucket.return_value = mock_bucket
        mock_storage_client.return_value = mock_client
        
        result = get_document_from_gcs('gs://test-bucket/clean/doc.json')
        
        assert result is None
        
    def test_get_document_invalid_path(self):
        """Test handling of invalid GCS path"""
        result = get_document_from_gcs('invalid-path')
        assert result is None


class TestCheckDocumentExists:
    """Test document existence checking"""
    
    @patch('lib.docai.storage.Client')
    def test_check_exists_true(self, mock_storage_client):
        """Test when document exists"""
        mock_client = Mock()
        mock_bucket = Mock()
        mock_blob = Mock()
        
        mock_blob.exists.return_value = True
        mock_bucket.blob.return_value = mock_blob
        mock_client.bucket.return_value = mock_bucket
        mock_storage_client.return_value = mock_client
        
        os.environ['BUCKET_CLEAN'] = 'test-bucket'
        
        result = check_document_exists('abc123', 'gd')
        assert result is True
        
    @patch('lib.docai.storage.Client')
    def test_check_exists_false(self, mock_storage_client):
        """Test when document does not exist"""
        mock_client = Mock()
        mock_bucket = Mock()
        mock_blob = Mock()
        
        mock_blob.exists.return_value = False
        mock_bucket.blob.return_value = mock_blob
        mock_client.bucket.return_value = mock_bucket
        mock_storage_client.return_value = mock_client
        
        os.environ['BUCKET_CLEAN'] = 'test-bucket'
        
        result = check_document_exists('abc123', 'gd')
        assert result is False
        
    def test_check_exists_missing_bucket(self):
        """Test when bucket environment variable is missing"""
        if 'BUCKET_CLEAN' in os.environ:
            del os.environ['BUCKET_CLEAN']
            
        result = check_document_exists('abc123', 'gd')
        assert result is False


class TestGetCurrentTimestamp:
    """Test timestamp generation"""
    
    def test_timestamp_format(self):
        """Test that timestamp is in correct ISO format"""
        timestamp = _get_current_timestamp()
        
        # Should be in format: 2024-06-01T12:34:56.789Z
        assert timestamp.endswith('Z')
        assert 'T' in timestamp
        
        # Should be parseable as ISO format
        from datetime import datetime
        parsed = datetime.fromisoformat(timestamp.rstrip('Z'))
        assert parsed is not None


if __name__ == "__main__":
    pytest.main([__file__])