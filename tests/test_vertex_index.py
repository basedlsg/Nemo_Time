"""
Unit tests for Vertex AI integration module
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import os
from lib.vertex_index import (
    embed_text, embed_query, search_documents, upsert_chunks,
    batch_embed_texts, validate_embedding_vector, create_metadata_filters,
    get_index_status
)


class TestEmbedText:
    """Test text embedding functionality"""
    
    @patch('lib.vertex_index.aiplatform')
    def test_embed_text_success(self, mock_aiplatform):
        """Test successful text embedding"""
        # Mock the embedding model and response
        mock_model = Mock()
        mock_embedding = Mock()
        mock_embedding.values = [0.1, 0.2, 0.3, 0.4, 0.5]
        mock_model.get_embeddings.return_value = [mock_embedding]
        
        mock_aiplatform.init.return_value = None
        mock_aiplatform.TextEmbeddingModel.from_pretrained.return_value = mock_model
        
        # Set environment variables
        os.environ['GOOGLE_CLOUD_PROJECT'] = 'test-project'
        os.environ['REGION'] = 'us-central1'
        
        result = embed_text("测试文本")
        
        assert result == [0.1, 0.2, 0.3, 0.4, 0.5]
        mock_model.get_embeddings.assert_called_once_with(["测试文本"])
        
    def test_embed_empty_text(self):
        """Test embedding empty text raises error"""
        with pytest.raises(ValueError, match="Text cannot be empty"):
            embed_text("")
            
        with pytest.raises(ValueError, match="Text cannot be empty"):
            embed_text("   ")
            
    @patch('lib.vertex_index.aiplatform')
    def test_embed_long_text_truncation(self, mock_aiplatform):
        """Test that long text is truncated"""
        mock_model = Mock()
        mock_embedding = Mock()
        mock_embedding.values = [0.1, 0.2, 0.3]
        mock_model.get_embeddings.return_value = [mock_embedding]
        
        mock_aiplatform.init.return_value = None
        mock_aiplatform.TextEmbeddingModel.from_pretrained.return_value = mock_model
        
        os.environ['GOOGLE_CLOUD_PROJECT'] = 'test-project'
        
        # Create very long text
        long_text = "测试文本" * 2000
        result = embed_text(long_text)
        
        # Should truncate and still return embedding
        assert result == [0.1, 0.2, 0.3]
        
        # Check that the text passed to model was truncated
        call_args = mock_model.get_embeddings.call_args[0][0]
        assert len(call_args[0]) <= 6000
        
    def test_missing_project_id(self):
        """Test error when project ID is missing"""
        if 'GOOGLE_CLOUD_PROJECT' in os.environ:
            del os.environ['GOOGLE_CLOUD_PROJECT']
            
        with pytest.raises(ValueError, match="GOOGLE_CLOUD_PROJECT environment variable not set"):
            embed_text("测试文本")


class TestSearchDocuments:
    """Test document search functionality"""
    
    @patch('lib.vertex_index.aiplatform')
    @patch('lib.vertex_index.MatchingEngineIndexEndpoint')
    def test_search_documents_success(self, mock_endpoint_class, mock_aiplatform):
        """Test successful document search"""
        # Mock the search response
        mock_neighbor = Mock()
        mock_neighbor.id = "doc-1"
        mock_neighbor.distance = 0.2
        mock_neighbor.restricts = []
        
        mock_endpoint = Mock()
        mock_endpoint.find_neighbors.return_value = [[mock_neighbor]]
        mock_endpoint_class.return_value = mock_endpoint
        
        mock_aiplatform.init.return_value = None
        
        # Set environment variables
        os.environ['GOOGLE_CLOUD_PROJECT'] = 'test-project'
        os.environ['VERTEX_INDEX_ID'] = 'test-index'
        os.environ['VERTEX_ENDPOINT_ID'] = 'test-endpoint'
        
        query_vector = [0.1, 0.2, 0.3, 0.4, 0.5]
        filters = {'province': 'gd', 'asset': 'solar'}
        
        results = search_documents(query_vector, filters, top_k=5)
        
        assert len(results) == 1
        assert results[0]['id'] == "doc-1"
        assert results[0]['distance'] == 0.2
        assert results[0]['score'] == 0.8  # 1.0 - 0.2
        
    def test_search_empty_vector(self):
        """Test search with empty vector raises error"""
        with pytest.raises(ValueError, match="Query vector cannot be empty"):
            search_documents([], {})
            
    def test_search_invalid_top_k(self):
        """Test search with invalid top_k raises error"""
        query_vector = [0.1, 0.2, 0.3]
        
        with pytest.raises(ValueError, match="top_k must be between 1 and 100"):
            search_documents(query_vector, {}, top_k=0)
            
        with pytest.raises(ValueError, match="top_k must be between 1 and 100"):
            search_documents(query_vector, {}, top_k=101)
            
    def test_search_missing_env_vars(self):
        """Test search with missing environment variables"""
        # Clear environment variables
        for var in ['GOOGLE_CLOUD_PROJECT', 'VERTEX_INDEX_ID', 'VERTEX_ENDPOINT_ID']:
            if var in os.environ:
                del os.environ[var]
                
        query_vector = [0.1, 0.2, 0.3]
        
        with pytest.raises(ValueError, match="Missing required environment variables"):
            search_documents(query_vector, {})


class TestUpsertChunks:
    """Test chunk upserting functionality"""
    
    @patch('lib.vertex_index.aiplatform')
    @patch('lib.vertex_index.MatchingEngineIndex')
    def test_upsert_chunks_success(self, mock_index_class, mock_aiplatform):
        """Test successful chunk upserting"""
        mock_index = Mock()
        mock_index.upsert_datapoints.return_value = None
        mock_index_class.return_value = mock_index
        
        mock_aiplatform.init.return_value = None
        
        # Set environment variables
        os.environ['GOOGLE_CLOUD_PROJECT'] = 'test-project'
        os.environ['VERTEX_INDEX_ID'] = 'test-index'
        
        chunks = [
            {
                'text': '测试文档内容',
                'embedding': [0.1, 0.2, 0.3, 0.4, 0.5],
                'chunk_index': 0,
                'metadata': {
                    'title': '测试文档',
                    'province': 'gd',
                    'asset': 'solar',
                    'checksum': 'abc123'
                }
            }
        ]
        
        upsert_chunks(chunks)
        
        # Verify upsert was called
        mock_index.upsert_datapoints.assert_called_once()
        call_args = mock_index.upsert_datapoints.call_args[1]['datapoints']
        
        assert len(call_args) == 1
        assert call_args[0]['datapoint_id'] == 'abc123-0'
        assert call_args[0]['feature_vector'] == [0.1, 0.2, 0.3, 0.4, 0.5]
        
    def test_upsert_empty_chunks(self):
        """Test upserting empty chunks list"""
        # Should not raise error, just return
        upsert_chunks([])
        
    def test_upsert_chunks_missing_embedding(self):
        """Test upserting chunks with missing embeddings"""
        os.environ['GOOGLE_CLOUD_PROJECT'] = 'test-project'
        os.environ['VERTEX_INDEX_ID'] = 'test-index'
        
        chunks = [
            {
                'text': '测试文档内容',
                # Missing embedding
                'metadata': {'title': '测试文档'}
            }
        ]
        
        with patch('lib.vertex_index.aiplatform'), \
             patch('lib.vertex_index.MatchingEngineIndex') as mock_index_class:
            
            mock_index = Mock()
            mock_index_class.return_value = mock_index
            
            upsert_chunks(chunks)
            
            # Should not call upsert since no valid chunks
            mock_index.upsert_datapoints.assert_not_called()


class TestBatchEmbedTexts:
    """Test batch embedding functionality"""
    
    @patch('lib.vertex_index.aiplatform')
    def test_batch_embed_success(self, mock_aiplatform):
        """Test successful batch embedding"""
        mock_model = Mock()
        
        # Mock embeddings for batch
        mock_embedding1 = Mock()
        mock_embedding1.values = [0.1, 0.2, 0.3]
        mock_embedding2 = Mock()
        mock_embedding2.values = [0.4, 0.5, 0.6]
        
        mock_model.get_embeddings.return_value = [mock_embedding1, mock_embedding2]
        
        mock_aiplatform.init.return_value = None
        mock_aiplatform.TextEmbeddingModel.from_pretrained.return_value = mock_model
        
        os.environ['GOOGLE_CLOUD_PROJECT'] = 'test-project'
        
        texts = ["第一个文档", "第二个文档"]
        results = batch_embed_texts(texts, batch_size=2)
        
        assert len(results) == 2
        assert results[0] == [0.1, 0.2, 0.3]
        assert results[1] == [0.4, 0.5, 0.6]
        
    def test_batch_embed_empty_list(self):
        """Test batch embedding with empty list"""
        result = batch_embed_texts([])
        assert result == []
        
    @patch('lib.vertex_index.aiplatform')
    def test_batch_embed_with_empty_texts(self, mock_aiplatform):
        """Test batch embedding with some empty texts"""
        mock_model = Mock()
        
        mock_embedding1 = Mock()
        mock_embedding1.values = [0.1, 0.2, 0.3]
        mock_embedding2 = Mock()
        mock_embedding2.values = [0.4, 0.5, 0.6]
        
        mock_model.get_embeddings.return_value = [mock_embedding1, mock_embedding2]
        
        mock_aiplatform.init.return_value = None
        mock_aiplatform.TextEmbeddingModel.from_pretrained.return_value = mock_model
        
        os.environ['GOOGLE_CLOUD_PROJECT'] = 'test-project'
        
        texts = ["有效文档", ""]  # One valid, one empty
        results = batch_embed_texts(texts)
        
        assert len(results) == 2
        assert results[0] == [0.1, 0.2, 0.3]  # Valid embedding
        assert results[1] == [0.0, 0.0, 0.0]  # Zero vector for empty text


class TestValidateEmbeddingVector:
    """Test embedding vector validation"""
    
    def test_valid_vector(self):
        """Test validation of valid embedding vector"""
        vector = [0.1, -0.2, 0.3, -0.4, 0.5]
        assert validate_embedding_vector(vector) is True
        
    def test_empty_vector(self):
        """Test validation of empty vector"""
        assert validate_embedding_vector([]) is False
        assert validate_embedding_vector(None) is False
        
    def test_non_list_vector(self):
        """Test validation of non-list input"""
        assert validate_embedding_vector("not a list") is False
        assert validate_embedding_vector(123) is False
        
    def test_vector_with_invalid_values(self):
        """Test validation of vector with invalid values"""
        # Non-numeric values
        assert validate_embedding_vector([0.1, "invalid", 0.3]) is False
        
        # Values outside reasonable range
        assert validate_embedding_vector([0.1, 15.0, 0.3]) is False
        assert validate_embedding_vector([0.1, -15.0, 0.3]) is False


class TestCreateMetadataFilters:
    """Test metadata filter creation"""
    
    def test_create_all_filters(self):
        """Test creating filters with all parameters"""
        filters = create_metadata_filters(
            province='gd',
            asset='solar', 
            doc_class='grid'
        )
        
        expected = {
            'province': 'gd',
            'asset': 'solar',
            'doc_class': 'grid'
        }
        
        assert filters == expected
        
    def test_create_partial_filters(self):
        """Test creating filters with some parameters"""
        filters = create_metadata_filters(province='gd', asset='solar')
        
        expected = {
            'province': 'gd',
            'asset': 'solar'
        }
        
        assert filters == expected
        
    def test_create_empty_filters(self):
        """Test creating filters with no parameters"""
        filters = create_metadata_filters()
        assert filters == {}
        
    def test_create_filters_with_none_values(self):
        """Test creating filters with None values"""
        filters = create_metadata_filters(
            province='gd',
            asset=None,
            doc_class='grid'
        )
        
        expected = {
            'province': 'gd',
            'doc_class': 'grid'
        }
        
        assert filters == expected


class TestGetIndexStatus:
    """Test index status checking"""
    
    @patch('lib.vertex_index.aiplatform')
    @patch('lib.vertex_index.MatchingEngineIndex')
    @patch('lib.vertex_index.MatchingEngineIndexEndpoint')
    def test_get_status_healthy(self, mock_endpoint_class, mock_index_class, mock_aiplatform):
        """Test getting healthy status"""
        # Mock healthy index and endpoint
        mock_index = Mock()
        mock_index.gca_resource.state = 1  # DEPLOYED state
        mock_index_class.return_value = mock_index
        
        mock_endpoint = Mock()
        mock_endpoint.gca_resource.state = 1  # DEPLOYED state
        mock_endpoint_class.return_value = mock_endpoint
        
        mock_aiplatform.init.return_value = None
        
        os.environ['GOOGLE_CLOUD_PROJECT'] = 'test-project'
        
        status = get_index_status('test-index', 'test-endpoint')
        assert status == 'healthy'
        
    @patch('lib.vertex_index.aiplatform')
    @patch('lib.vertex_index.MatchingEngineIndex')
    @patch('lib.vertex_index.MatchingEngineIndexEndpoint')
    def test_get_status_unhealthy(self, mock_endpoint_class, mock_index_class, mock_aiplatform):
        """Test getting unhealthy status"""
        # Mock unhealthy index and endpoint
        mock_index = Mock()
        mock_index.gca_resource.state = 0  # Not deployed
        mock_index_class.return_value = mock_index
        
        mock_endpoint = Mock()
        mock_endpoint.gca_resource.state = 0  # Not deployed
        mock_endpoint_class.return_value = mock_endpoint
        
        mock_aiplatform.init.return_value = None
        
        os.environ['GOOGLE_CLOUD_PROJECT'] = 'test-project'
        
        status = get_index_status('test-index', 'test-endpoint')
        assert 'index_state=0, endpoint_state=0' in status


if __name__ == "__main__":
    pytest.main([__file__])