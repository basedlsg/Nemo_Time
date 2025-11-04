"""
Unit tests for composer module
Tests response composition and citation formatting
"""
import pytest
from unittest.mock import Mock, patch
import sys
import os

# Add lib directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'lib'))

from composer import compose_response, extract_verbatim_quotes, format_citations


class TestComposer:
    """Test response composition functionality"""
    
    def test_extract_verbatim_quotes_basic(self):
        """Test basic verbatim quote extraction"""
        text = "光伏发电项目并网验收需要提交以下资料：1. 项目核准文件；2. 设计图纸；3. 验收报告。"
        quotes = extract_verbatim_quotes(text, "验收需要", max_quotes=2)
        
        assert len(quotes) > 0
        assert "验收需要" in quotes[0]
        assert len(quotes[0]) <= 200  # Should be reasonable length
    
    def test_extract_verbatim_quotes_chinese_punctuation(self):
        """Test quote extraction with Chinese punctuation"""
        text = "根据《电力法》规定，并网发电设施应当符合国家技术标准。具体要求包括：（一）技术参数符合要求；（二）安全措施到位。"
        quotes = extract_verbatim_quotes(text, "技术标准")
        
        assert len(quotes) > 0
        assert "技术标准" in quotes[0]
        # Should preserve Chinese punctuation
        assert any(punct in quotes[0] for punct in ['，', '。', '（', '）'])
    
    def test_extract_verbatim_quotes_no_match(self):
        """Test quote extraction when no matches found"""
        text = "这是一段不相关的文本内容。"
        quotes = extract_verbatim_quotes(text, "火星探索")
        
        assert len(quotes) == 0
    
    def test_extract_verbatim_quotes_multiple_matches(self):
        """Test quote extraction with multiple matches"""
        text = "验收标准如下：第一条验收要求明确规定验收流程。第二条验收标准详细说明验收内容。"
        quotes = extract_verbatim_quotes(text, "验收", max_quotes=3)
        
        assert len(quotes) >= 2
        for quote in quotes:
            assert "验收" in quote
    
    def test_format_citations_complete(self):
        """Test citation formatting with complete information"""
        citations = [
            {
                'title': '广东省分布式光伏发电项目管理办法',
                'effective_date': '2023-01-15',
                'url': 'https://gd.gov.cn/doc123'
            },
            {
                'title': '山东省新能源并网技术规定',
                'effective_date': '2022-12-01',
                'url': 'https://sd.gov.cn/doc456'
            }
        ]
        
        formatted = format_citations(citations)
        
        assert len(formatted) == 2
        assert formatted[0]['title'] == '广东省分布式光伏发电项目管理办法'
        assert formatted[0]['effective_date'] == '2023-01-15'
        assert formatted[0]['url'] == 'https://gd.gov.cn/doc123'
    
    def test_format_citations_missing_date(self):
        """Test citation formatting with missing effective date"""
        citations = [
            {
                'title': '内蒙古自治区风电项目建设规范',
                'url': 'https://nmg.gov.cn/doc789'
            }
        ]
        
        formatted = format_citations(citations)
        
        assert len(formatted) == 1
        assert formatted[0]['title'] == '内蒙古自治区风电项目建设规范'
        assert 'effective_date' not in formatted[0] or formatted[0]['effective_date'] is None
        assert formatted[0]['url'] == 'https://nmg.gov.cn/doc789'
    
    def test_format_citations_empty(self):
        """Test citation formatting with empty list"""
        citations = []
        formatted = format_citations(citations)
        
        assert len(formatted) == 0
        assert isinstance(formatted, list)
    
    def test_compose_response_with_results(self):
        """Test response composition with search results"""
        search_results = [
            {
                'content': '光伏发电项目并网验收应当按照国家标准执行。验收内容包括设备检测、安全评估等。',
                'metadata': {
                    'title': '光伏并网技术规范',
                    'effective_date': '2023-06-01',
                    'url': 'https://gd.gov.cn/pv-grid-standard'
                }
            }
        ]
        
        question = "光伏并网验收需要什么？"
        response = compose_response(search_results, question, lang='zh-CN')
        
        assert 'answer_zh' in response
        assert 'citations' in response
        assert len(response['citations']) == 1
        assert '验收' in response['answer_zh']
        assert response['citations'][0]['title'] == '光伏并网技术规范'
    
    def test_compose_response_no_results(self):
        """Test response composition with no search results"""
        search_results = []
        question = "火星上的光伏发电规定？"
        
        response = compose_response(search_results, question, lang='zh-CN')
        
        assert 'refusal' in response
        assert 'tips' in response
        assert '未找到' in response['refusal'] or '没有' in response['refusal']
        assert len(response['tips']) > 0
    
    def test_compose_response_english(self):
        """Test response composition in English"""
        search_results = [
            {
                'content': 'Solar power grid connection acceptance should follow national standards.',
                'metadata': {
                    'title': 'Solar Grid Connection Technical Specifications',
                    'effective_date': '2023-06-01',
                    'url': 'https://gd.gov.cn/pv-grid-standard'
                }
            }
        ]
        
        question = "What are the solar grid connection requirements?"
        response = compose_response(search_results, question, lang='en')
        
        assert 'answer_en' in response or 'answer_zh' in response  # May fallback to Chinese
        assert 'citations' in response
    
    def test_compose_response_no_mock_data(self):
        """Test that response never contains mock data"""
        search_results = []
        question = "完全不存在的规定"
        
        response = compose_response(search_results, question, lang='zh-CN')
        
        # Should refuse rather than make up data
        assert 'refusal' in response
        assert 'answer_zh' not in response or not response['answer_zh']
        
        # Should not contain any mock indicators
        refusal_text = response.get('refusal', '')
        mock_indicators = ['示例', '假设', '模拟', 'example', 'mock', 'sample']
        for indicator in mock_indicators:
            assert indicator.lower() not in refusal_text.lower()
    
    def test_compose_response_preserves_chinese_formatting(self):
        """Test that Chinese text formatting is preserved"""
        search_results = [
            {
                'content': '根据《电力法》第二十五条规定：（一）发电设施应符合技术标准；（二）必须通过验收。',
                'metadata': {
                    'title': '中华人民共和国电力法',
                    'effective_date': '2023-01-01',
                    'url': 'https://gov.cn/power-law'
                }
            }
        ]
        
        question = "电力法对发电设施有什么规定？"
        response = compose_response(search_results, question, lang='zh-CN')
        
        answer = response.get('answer_zh', '')
        # Should preserve Chinese punctuation and formatting
        assert '（' in answer or '）' in answer or '：' in answer
        assert '《' in answer or '》' in answer


if __name__ == "__main__":
    pytest.main([__file__, "-v"])