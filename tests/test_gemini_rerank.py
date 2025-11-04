"""
Unit tests for Gemini reranking module
Tests result reranking and performance monitoring
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add lib directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'lib'))

from gemini_rerank import rerank_results, should_rerank, format_results_for_reranking


class TestGeminiRerank:
    """Test Gemini reranking functionality"""
    
    def test_should_rerank_enabled(self):
        """Test reranking decision when enabled"""
        with patch.dict(os.environ, {'RERANK': 'true'}):
            assert should_rerank() == True
        
        with patch.dict(os.environ, {'RERANK': 'True'}):
            assert should_rerank() == True
        
        with patch.dict(os.environ, {'RERANK': '1'}):
            assert should_rerank() == True
    
    def test_should_rerank_disabled(self):
        """Test reranking decision when disabled"""
        with patch.dict(os.environ, {'RERANK': 'false'}):
            assert should_rerank() == False
        
        with patch.dict(os.environ, {'RERANK': 'False'}):
            assert should_rerank() == False
        
        with patch.dict(os.environ, {'RERANK': '0'}):
            assert should_rerank() == False
        
        # Default should be False when not set
        with patch.dict(os.environ, {}, clear=True):
            assert should_rerank() == False
    
    def test_format_results_for_reranking(self):
        """Test formatting search results for Gemini reranking"""
        results = [
            {
                'content': '光伏发电项目并网验收需要提交相关资料。',
                'metadata': {
                    'title': '光伏并网管理办法',
                    'effective_date': '2023-01-01'
                }
            },
            {
                'content': '分布式光伏系统应符合技术标准。',
                'metadata': {
                    'title': '分布式光伏技术规范',
                    'effective_date': '2022-12-01'
                }
            }
        ]
        
        question = "光伏并网验收需要什么资料？"
        formatted = format_results_for_reranking(results, question)
        
        assert 'question' in formatted
        assert 'documents' in formatted
        assert formatted['question'] == question
        assert len(formatted['documents']) == 2
        
        # Check document formatting
        doc1 = formatted['documents'][0]
        assert 'id' in doc1
        assert 'title' in doc1
        assert 'content' in doc1
        assert doc1['title'] == '光伏并网管理办法'
        assert '验收需要' in doc1['content']
    
    def test_format_results_for_reranking_empty(self):
        """Test formatting empty results"""
        results = []
        question = "测试问题"
        
        formatted = format_results_for_reranking(results, question)
        
        assert formatted['question'] == question
        assert len(formatted['documents']) == 0
    
    @patch('google.generativeai.GenerativeModel')
    def test_rerank_results_success(self, mock_model_class):
        """Test successful result reranking"""
        # Mock Gemini API response
        mock_model = Mock()
        mock_response = Mock()
        mock_response.text = '''
        {
            "reranked_ids": [1, 0],
            "reasoning": "文档1更直接回答了验收资料的问题"
        }
        '''
        mock_model.generate_content.return_value = mock_response
        mock_model_class.return_value = mock_model
        
        results = [
            {
                'content': '光伏系统技术标准规定...',
                'metadata': {'title': '技术标准', 'score': 0.8}
            },
            {
                'content': '光伏并网验收需要提交以下资料：1.核准文件 2.设计图纸',
                'metadata': {'title': '验收办法', 'score': 0.7}
            }
        ]
        
        question = "光伏并网验收需要什么资料？"
        
        with patch.dict(os.environ, {'GEMINI_API_KEY': 'test-key'}):
            reranked = rerank_results(results, question)
        
        # Should reorder results based on Gemini response
        assert len(reranked) == 2
        assert reranked[0]['metadata']['title'] == '验收办法'  # Should be first now
        assert reranked[1]['metadata']['title'] == '技术标准'
    
    @patch('google.generativeai.GenerativeModel')
    def test_rerank_results_api_error(self, mock_model_class):
        """Test reranking handles API errors gracefully"""
        mock_model = Mock()
        mock_model.generate_content.side_effect = Exception("API Error")
        mock_model_class.return_value = mock_model
        
        results = [
            {'content': '内容1', 'metadata': {'title': '文档1'}},
            {'content': '内容2', 'metadata': {'title': '文档2'}}
        ]
        
        question = "测试问题"
        
        with patch.dict(os.environ, {'GEMINI_API_KEY': 'test-key'}):
            reranked = rerank_results(results, question)
        
        # Should return original results on error
        assert len(reranked) == 2
        assert reranked == results
    
    @patch('google.generativeai.GenerativeModel')
    def test_rerank_results_invalid_json(self, mock_model_class):
        """Test reranking handles invalid JSON response"""
        mock_model = Mock()
        mock_response = Mock()
        mock_response.text = "Invalid JSON response"
        mock_model.generate_content.return_value = mock_response
        mock_model_class.return_value = mock_model
        
        results = [
            {'content': '内容1', 'metadata': {'title': '文档1'}},
            {'content': '内容2', 'metadata': {'title': '文档2'}}
        ]
        
        question = "测试问题"
        
        with patch.dict(os.environ, {'GEMINI_API_KEY': 'test-key'}):
            reranked = rerank_results(results, question)
        
        # Should return original results on invalid JSON
        assert reranked == results
    
    @patch('google.generativeai.GenerativeModel')
    def test_rerank_results_invalid_ids(self, mock_model_class):
        """Test reranking handles invalid document IDs"""
        mock_model = Mock()
        mock_response = Mock()
        mock_response.text = '''
        {
            "reranked_ids": [5, 10],
            "reasoning": "Invalid IDs that don't exist"
        }
        '''
        mock_model.generate_content.return_value = mock_response
        mock_model_class.return_value = mock_model
        
        results = [
            {'content': '内容1', 'metadata': {'title': '文档1'}},
            {'content': '内容2', 'metadata': {'title': '文档2'}}
        ]
        
        question = "测试问题"
        
        with patch.dict(os.environ, {'GEMINI_API_KEY': 'test-key'}):
            reranked = rerank_results(results, question)
        
        # Should return original results on invalid IDs
        assert reranked == results
    
    def test_rerank_results_missing_api_key(self):
        """Test reranking fails gracefully without API key"""
        results = [
            {'content': '内容1', 'metadata': {'title': '文档1'}},
            {'content': '内容2', 'metadata': {'title': '文档2'}}
        ]
        
        question = "测试问题"
        
        with patch.dict(os.environ, {}, clear=True):
            reranked = rerank_results(results, question)
        
        # Should return original results without API key
        assert reranked == results
    
    def test_rerank_results_empty_list(self):
        """Test reranking empty results list"""
        results = []
        question = "测试问题"
        
        reranked = rerank_results(results, question)
        
        assert reranked == []
    
    def test_rerank_results_single_result(self):
        """Test reranking with single result"""
        results = [
            {'content': '单个文档内容', 'metadata': {'title': '单个文档'}}
        ]
        
        question = "测试问题"
        
        reranked = rerank_results(results, question)
        
        # Should return same single result
        assert len(reranked) == 1
        assert reranked == results
    
    @patch('google.generativeai.GenerativeModel')
    def test_rerank_results_performance_monitoring(self, mock_model_class):
        """Test that reranking includes performance monitoring"""
        mock_model = Mock()
        mock_response = Mock()
        mock_response.text = '{"reranked_ids": [0, 1]}'
        mock_model.generate_content.return_value = mock_response
        mock_model_class.return_value = mock_model
        
        results = [
            {'content': '内容1', 'metadata': {'title': '文档1'}},
            {'content': '内容2', 'metadata': {'title': '文档2'}}
        ]
        
        question = "测试问题"
        
        with patch.dict(os.environ, {'GEMINI_API_KEY': 'test-key'}):
            with patch('time.time', side_effect=[1000.0, 1000.5]):  # Mock 500ms duration
                reranked = rerank_results(results, question)
        
        # Should complete successfully
        assert len(reranked) == 2
    
    @patch('google.generativeai.GenerativeModel')
    def test_rerank_results_chinese_content(self, mock_model_class):
        """Test reranking with Chinese content"""
        mock_model = Mock()
        mock_response = Mock()
        mock_response.text = '''
        {
            "reranked_ids": [1, 0],
            "reasoning": "第二个文档更相关"
        }
        '''
        mock_model.generate_content.return_value = mock_response
        mock_model_class.return_value = mock_model
        
        results = [
            {
                'content': '根据《电力法》规定，发电设施应当符合国家技术标准。',
                'metadata': {'title': '电力法实施细则'}
            },
            {
                'content': '光伏发电项目并网验收具体要求：（一）技术资料齐全；（二）设备检测合格。',
                'metadata': {'title': '光伏并网验收办法'}
            }
        ]
        
        question = "光伏并网验收需要什么？"
        
        with patch.dict(os.environ, {'GEMINI_API_KEY': 'test-key'}):
            reranked = rerank_results(results, question)
        
        # Should handle Chinese content properly
        assert len(reranked) == 2
        assert reranked[0]['metadata']['title'] == '光伏并网验收办法'


if __name__ == "__main__":
    pytest.main([__file__, "-v"])