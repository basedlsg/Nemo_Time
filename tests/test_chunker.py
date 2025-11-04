"""
Unit tests for document chunking module
"""

import pytest
from lib.chunker import (
    create_chunks, validate_chunks, _split_into_sentences,
    _get_overlap_text, _create_chunk_dict, _is_repetitive_content,
    _has_sufficient_chinese_content
)


class TestCreateChunks:
    """Test document chunking functionality"""
    
    def test_basic_chunking(self):
        """Test basic document chunking"""
        doc_data = {
            'text': '广东省光伏并网管理办法第一条为规范光伏发电项目并网管理。第二条本办法适用于广东省内所有光伏项目。第三条申请并网需要提交技术资料和安全评估报告。',
            'title': '广东省光伏并网管理办法',
            'url': 'https://gd.gov.cn/test',
            'province': 'gd',
            'asset': 'solar',
            'doc_class': 'grid',
            'checksum': 'test123'
        }
        
        chunks = create_chunks(doc_data, chunk_size=50, overlap=10)
        
        # Should create multiple chunks for this text
        assert len(chunks) > 1
        
        # Each chunk should have required fields
        for chunk in chunks:
            assert 'text' in chunk
            assert 'chunk_index' in chunk
            assert 'metadata' in chunk
            assert chunk['metadata']['title'] == '广东省光伏并网管理办法'
            assert chunk['metadata']['province'] == 'gd'
            
    def test_short_document(self):
        """Test chunking of short document"""
        doc_data = {
            'text': '短文档测试。',
            'title': '测试文档',
            'province': 'gd',
            'asset': 'solar',
            'doc_class': 'grid'
        }
        
        chunks = create_chunks(doc_data, chunk_size=800, overlap=100)
        
        # Should create exactly one chunk
        assert len(chunks) == 1
        assert chunks[0]['text'] == '短文档测试。'
        
    def test_empty_text(self):
        """Test handling of empty text"""
        doc_data = {
            'text': '',
            'title': '空文档'
        }
        
        chunks = create_chunks(doc_data)
        assert chunks == []
        
    def test_metadata_preservation(self):
        """Test that metadata is preserved in chunks"""
        doc_data = {
            'text': '测试文档内容。这是第二句。',
            'title': '测试标题',
            'url': 'https://test.gov.cn',
            'effective_date': '2024-06-01',
            'province': 'gd',
            'asset': 'solar',
            'doc_class': 'grid',
            'checksum': 'abc123',
            'lang': 'zh-CN'
        }
        
        chunks = create_chunks(doc_data)
        
        for chunk in chunks:
            metadata = chunk['metadata']
            assert metadata['title'] == '测试标题'
            assert metadata['url'] == 'https://test.gov.cn'
            assert metadata['effective_date'] == '2024-06-01'
            assert metadata['province'] == 'gd'
            assert metadata['asset'] == 'solar'
            assert metadata['doc_class'] == 'grid'
            assert metadata['checksum'] == 'abc123'
            assert metadata['lang'] == 'zh-CN'


class TestSplitIntoSentences:
    """Test sentence splitting functionality"""
    
    def test_chinese_sentence_splitting(self):
        """Test splitting Chinese text into sentences"""
        text = "第一条规定内容。第二条管理办法！第三条实施细则？"
        sentences = _split_into_sentences(text)
        
        assert len(sentences) == 3
        assert sentences[0] == "第一条规定内容。"
        assert sentences[1] == "第二条管理办法！"
        assert sentences[2] == "第三条实施细则？"
        
    def test_mixed_punctuation(self):
        """Test splitting with mixed punctuation"""
        text = "规定如下：第一项内容；第二项要求。"
        sentences = _split_into_sentences(text)
        
        # Should split on both semicolon and period
        assert len(sentences) >= 2
        assert any("第一项内容；" in s for s in sentences)
        assert any("第二项要求。" in s for s in sentences)
        
    def test_empty_sentences(self):
        """Test handling of empty sentences"""
        text = "内容。。。更多内容。"
        sentences = _split_into_sentences(text)
        
        # Should filter out empty sentences
        for sentence in sentences:
            assert sentence.strip() != ""


class TestGetOverlapText:
    """Test overlap text extraction"""
    
    def test_basic_overlap(self):
        """Test basic overlap extraction"""
        text = "这是一个很长的文档内容。包含多个句子。需要重叠处理。"
        overlap = _get_overlap_text(text, 10)
        
        assert len(overlap) <= 10
        assert overlap in text
        
    def test_overlap_longer_than_text(self):
        """Test when overlap is longer than text"""
        text = "短文本。"
        overlap = _get_overlap_text(text, 100)
        
        assert overlap == text
        
    def test_sentence_boundary_overlap(self):
        """Test overlap respects sentence boundaries"""
        text = "第一句内容。第二句内容。第三句内容。"
        overlap = _get_overlap_text(text, 8)
        
        # Should try to start after a sentence boundary
        assert not overlap.startswith("容。第")  # Shouldn't break mid-sentence


class TestCreateChunkDict:
    """Test chunk dictionary creation"""
    
    def test_basic_chunk_creation(self):
        """Test basic chunk dictionary creation"""
        doc_data = {
            'title': '测试文档',
            'url': 'https://test.gov.cn',
            'province': 'gd',
            'asset': 'solar',
            'doc_class': 'grid'
        }
        
        chunk = _create_chunk_dict("测试文本内容", doc_data, 0)
        
        assert chunk['text'] == "测试文本内容"
        assert chunk['chunk_index'] == 0
        assert 'metadata' in chunk
        assert chunk['metadata']['title'] == '测试文档'
        
    def test_none_value_filtering(self):
        """Test that None values are filtered from metadata"""
        doc_data = {
            'title': '测试文档',
            'url': None,
            'effective_date': None,
            'province': 'gd'
        }
        
        chunk = _create_chunk_dict("测试文本", doc_data, 0)
        
        # None values should be filtered out
        assert 'url' not in chunk['metadata']
        assert 'effective_date' not in chunk['metadata']
        assert chunk['metadata']['province'] == 'gd'


class TestValidateChunks:
    """Test chunk validation functionality"""
    
    def test_valid_chunks(self):
        """Test validation of valid chunks"""
        chunks = [
            {
                'text': '这是一个有效的中文文档内容，包含足够的信息用于处理和分析。',
                'metadata': {'title': '测试文档'}
            },
            {
                'text': '另一个有效的文档片段，具有合理的长度和中文内容比例。',
                'metadata': {'title': '测试文档2'}
            }
        ]
        
        valid_chunks = validate_chunks(chunks)
        assert len(valid_chunks) == 2
        
    def test_filter_short_chunks(self):
        """Test filtering of chunks that are too short"""
        chunks = [
            {
                'text': '短',  # Too short
                'metadata': {'title': '测试'}
            },
            {
                'text': '这是一个足够长的有效文档内容，应该通过验证。',
                'metadata': {'title': '有效文档'}
            }
        ]
        
        valid_chunks = validate_chunks(chunks)
        assert len(valid_chunks) == 1
        assert '足够长' in valid_chunks[0]['text']
        
    def test_filter_long_chunks(self):
        """Test filtering of chunks that are too long"""
        long_text = '很长的文档内容。' * 100  # Create very long text
        chunks = [
            {
                'text': long_text,
                'metadata': {'title': '过长文档'}
            },
            {
                'text': '正常长度的文档内容，应该通过验证。',
                'metadata': {'title': '正常文档'}
            }
        ]
        
        valid_chunks = validate_chunks(chunks)
        assert len(valid_chunks) == 1
        assert '正常长度' in valid_chunks[0]['text']
        
    def test_filter_insufficient_chinese(self):
        """Test filtering of chunks with insufficient Chinese content"""
        chunks = [
            {
                'text': 'This is mostly English content with very little Chinese 内容.',
                'metadata': {'title': 'English Doc'}
            },
            {
                'text': '这是一个主要包含中文内容的文档，应该通过中文内容验证。',
                'metadata': {'title': '中文文档'}
            }
        ]
        
        valid_chunks = validate_chunks(chunks)
        assert len(valid_chunks) == 1
        assert '中文内容' in valid_chunks[0]['text']


class TestIsRepetitiveContent:
    """Test repetitive content detection"""
    
    def test_normal_content(self):
        """Test normal content is not flagged as repetitive"""
        text = "广东省光伏并网管理办法规定了详细的申请流程和技术要求。"
        assert not _is_repetitive_content(text)
        
    def test_repetitive_content(self):
        """Test repetitive content is detected"""
        text = "测试 测试 测试 测试 测试 测试 测试 测试 测试 测试"
        assert _is_repetitive_content(text)
        
    def test_short_content(self):
        """Test short content is not flagged as repetitive"""
        text = "短文档"
        assert not _is_repetitive_content(text)


class TestHasSufficientChineseContent:
    """Test Chinese content detection"""
    
    def test_sufficient_chinese(self):
        """Test content with sufficient Chinese characters"""
        text = "这是一个包含足够中文字符的文档内容。"
        assert _has_sufficient_chinese_content(text)
        
    def test_insufficient_chinese(self):
        """Test content with insufficient Chinese characters"""
        text = "This is mostly English with some 中文 words."
        assert not _has_sufficient_chinese_content(text)
        
    def test_empty_content(self):
        """Test empty content"""
        text = ""
        assert not _has_sufficient_chinese_content(text)
        
    def test_whitespace_only(self):
        """Test whitespace-only content"""
        text = "   \n\t   "
        assert not _has_sufficient_chinese_content(text)


if __name__ == "__main__":
    pytest.main([__file__])