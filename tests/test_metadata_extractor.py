"""
Unit tests for metadata extraction module
"""

import pytest
from lib.metadata_extractor import (
    extract_comprehensive_metadata, _extract_title_from_url, _calculate_content_checksum,
    _determine_province, _determine_asset_type, _determine_document_class,
    _extract_issuing_authority, _extract_document_number, _extract_publication_date,
    _detect_language, _extract_regulatory_scope, _analyze_source_url,
    _is_government_domain, validate_metadata_completeness
)


class TestExtractComprehensiveMetadata:
    """Test comprehensive metadata extraction"""
    
    def test_extract_full_metadata(self):
        """Test extraction of comprehensive metadata"""
        text = """
        广东省光伏并网管理办法
        广东省发展和改革委员会
        粤发改〔2024〕15号
        发布日期：2024年3月15日
        生效日期：2024年6月1日
        
        第一条 为规范光伏发电项目并网管理，根据国家相关法律法规...
        """
        
        url = "https://gd.gov.cn/documents/solar-grid-connection-2024.pdf"
        
        metadata = extract_comprehensive_metadata(text, url, 'gd', 'solar', 'grid')
        
        assert metadata['title'] == '广东省光伏并网管理办法'
        assert metadata['province'] == 'gd'
        assert metadata['asset'] == 'solar'
        assert metadata['doc_class'] == 'grid'
        assert metadata['effective_date'] == '2024-06-01'
        assert metadata['publication_date'] == '2024-03-15'
        assert metadata['issuing_authority'] == '广东省发展和改革委员会'
        assert metadata['document_number'] == '粤发改〔2024〕15号'
        assert metadata['language'] == 'zh-CN'
        assert metadata['is_government_source'] is True
        
    def test_extract_minimal_metadata(self):
        """Test extraction with minimal information"""
        text = "简短的文档内容"
        url = "https://example.com/doc.pdf"
        
        metadata = extract_comprehensive_metadata(text, url)
        
        assert 'checksum' in metadata
        assert metadata['url'] == url
        assert metadata['content_length'] == len(text)
        assert metadata['language'] == 'zh-CN'


class TestExtractTitleFromUrl:
    """Test title extraction from URL"""
    
    def test_extract_meaningful_title(self):
        """Test extraction of meaningful title from URL"""
        url = "https://gd.gov.cn/documents/solar-grid-connection-management.pdf"
        result = _extract_title_from_url(url)
        assert result == "solar grid connection management"
        
    def test_extract_chinese_filename(self):
        """Test extraction from Chinese filename"""
        url = "https://gd.gov.cn/光伏并网管理办法.pdf"
        result = _extract_title_from_url(url)
        assert result == "光伏并网管理办法"
        
    def test_no_meaningful_title(self):
        """Test when URL has no meaningful title"""
        url = "https://gd.gov.cn/123456.pdf"
        result = _extract_title_from_url(url)
        assert result is None
        
    def test_invalid_url(self):
        """Test handling of invalid URL"""
        result = _extract_title_from_url("not-a-url")
        assert result is None


class TestCalculateContentChecksum:
    """Test content checksum calculation"""
    
    def test_consistent_checksum(self):
        """Test that same content produces same checksum"""
        text = "测试文档内容"
        checksum1 = _calculate_content_checksum(text)
        checksum2 = _calculate_content_checksum(text)
        assert checksum1 == checksum2
        
    def test_different_content_different_checksum(self):
        """Test that different content produces different checksums"""
        text1 = "文档内容1"
        text2 = "文档内容2"
        checksum1 = _calculate_content_checksum(text1)
        checksum2 = _calculate_content_checksum(text2)
        assert checksum1 != checksum2
        
    def test_checksum_format(self):
        """Test checksum format"""
        text = "测试内容"
        checksum = _calculate_content_checksum(text)
        assert len(checksum) == 64  # SHA-256 produces 64-char hex string
        assert all(c in '0123456789abcdef' for c in checksum)


class TestDetermineProvince:
    """Test province determination"""
    
    def test_determine_from_hint(self):
        """Test province determination from hint"""
        result = _determine_province("", "", "广东")
        assert result == "gd"
        
    def test_determine_from_url(self):
        """Test province determination from URL"""
        result = _determine_province("", "https://gd.gov.cn/doc.pdf")
        assert result == "gd"
        
        result = _determine_province("", "https://sd.gov.cn/doc.pdf")
        assert result == "sd"
        
    def test_determine_from_text(self):
        """Test province determination from text content"""
        text = "广东省光伏并网管理办法..."
        result = _determine_province(text, "")
        assert result == "gd"
        
        text = "山东省风电项目管理规定..."
        result = _determine_province(text, "")
        assert result == "sd"
        
    def test_no_province_found(self):
        """Test when no province can be determined"""
        result = _determine_province("普通文档内容", "https://example.com/doc.pdf")
        assert result is None


class TestDetermineAssetType:
    """Test asset type determination"""
    
    def test_determine_from_hint(self):
        """Test asset type determination from hint"""
        result = _determine_asset_type("", "", "光伏")
        assert result == "solar"
        
    def test_determine_from_url(self):
        """Test asset type determination from URL"""
        result = _determine_asset_type("", "https://example.com/solar-project.pdf")
        assert result == "solar"
        
        result = _determine_asset_type("", "https://example.com/wind-farm.pdf")
        assert result == "wind"
        
    def test_determine_from_text(self):
        """Test asset type determination from text content"""
        text = "光伏发电项目并网管理办法..."
        result = _determine_asset_type(text, "")
        assert result == "solar"
        
        text = "风力发电项目建设规范..."
        result = _determine_asset_type(text, "")
        assert result == "wind"
        
        text = "煤电项目环保要求..."
        result = _determine_asset_type(text, "")
        assert result == "coal"
        
    def test_multiple_asset_types(self):
        """Test when text contains multiple asset types"""
        text = "光伏光伏光伏项目管理，风电项目也需要..."  # More solar mentions
        result = _determine_asset_type(text, "")
        assert result == "solar"  # Should pick the most frequent


class TestDetermineDocumentClass:
    """Test document class determination"""
    
    def test_determine_from_hint(self):
        """Test document class determination from hint"""
        result = _determine_document_class("", "", "grid")
        assert result == "grid"
        
    def test_determine_grid_from_text(self):
        """Test grid class determination from text"""
        text = "并网管理办法，电网接入要求..."
        result = _determine_document_class(text, "")
        assert result == "grid"
        
    def test_determine_grid_from_url(self):
        """Test grid class determination from URL"""
        result = _determine_document_class("", "https://example.com/grid-connection.pdf")
        assert result == "grid"
        
    def test_no_class_found(self):
        """Test when no document class can be determined"""
        result = _determine_document_class("普通文档内容", "https://example.com/doc.pdf")
        assert result is None


class TestExtractIssuingAuthority:
    """Test issuing authority extraction"""
    
    def test_extract_development_commission(self):
        """Test extraction of development and reform commission"""
        text = "广东省发展和改革委员会关于印发..."
        result = _extract_issuing_authority(text)
        assert result == "广东省发展和改革委员会"
        
    def test_extract_energy_bureau(self):
        """Test extraction of energy bureau"""
        text = "国家能源局关于规范..."
        result = _extract_issuing_authority(text)
        assert result == "国家能源局"
        
    def test_extract_government(self):
        """Test extraction of government authority"""
        text = "广东省人民政府办公厅关于..."
        result = _extract_issuing_authority(text)
        assert result == "广东省人民政府"
        
    def test_no_authority_found(self):
        """Test when no authority is found"""
        text = "普通文档内容，没有发布机构信息"
        result = _extract_issuing_authority(text)
        assert result is None


class TestExtractDocumentNumber:
    """Test document number extraction"""
    
    def test_extract_standard_format(self):
        """Test extraction of standard document number format"""
        text = "粤发改〔2024〕15号关于印发..."
        result = _extract_document_number(text)
        assert result == "粤发改〔2024〕15号"
        
    def test_extract_bracket_format(self):
        """Test extraction of bracket format"""
        text = "国能发[2024]25号文件..."
        result = _extract_document_number(text)
        assert result == "国能发[2024]25号"
        
    def test_extract_simple_number(self):
        """Test extraction of simple number format"""
        text = "第123号令..."
        result = _extract_document_number(text)
        assert result == "第123号"
        
    def test_no_number_found(self):
        """Test when no document number is found"""
        text = "普通文档内容，没有文件编号"
        result = _extract_document_number(text)
        assert result is None


class TestExtractPublicationDate:
    """Test publication date extraction"""
    
    def test_extract_issuance_date(self):
        """Test extraction of issuance date"""
        text = "印发日期：2024年3月15日"
        result = _extract_publication_date(text)
        assert result == "2024-03-15"
        
    def test_extract_publication_date(self):
        """Test extraction of publication date"""
        text = "发布日期：2024年6月1日"
        result = _extract_publication_date(text)
        assert result == "2024-06-01"
        
    def test_extract_date_in_sentence(self):
        """Test extraction of date within sentence"""
        text = "本办法于2024年5月20日印发"
        result = _extract_publication_date(text)
        assert result == "2024-05-20"
        
    def test_no_date_found(self):
        """Test when no publication date is found"""
        text = "文档内容没有发布日期信息"
        result = _extract_publication_date(text)
        assert result is None


class TestDetectLanguage:
    """Test language detection"""
    
    def test_detect_chinese(self):
        """Test detection of Chinese language"""
        text = "这是一个中文文档，包含大量的中文字符。"
        result = _detect_language(text)
        assert result == "zh-CN"
        
    def test_detect_english(self):
        """Test detection of English language"""
        text = "This is an English document with mostly English content."
        result = _detect_language(text)
        assert result == "en"
        
    def test_detect_mixed(self):
        """Test detection of mixed language"""
        text = "This document contains both English and 中文 content equally."
        result = _detect_language(text)
        assert result == "mixed"
        
    def test_detect_empty(self):
        """Test detection with empty text"""
        result = _detect_language("")
        assert result == "unknown"


class TestExtractRegulatoryScope:
    """Test regulatory scope extraction"""
    
    def test_extract_grid_scope(self):
        """Test extraction of grid-related scope"""
        text = "本办法规定了并网、验收、申请等相关要求..."
        result = _extract_regulatory_scope(text)
        
        assert "并网" in result
        assert "验收" in result
        assert "申请" in result
        
    def test_extract_construction_scope(self):
        """Test extraction of construction-related scope"""
        text = "项目建设、运营、维护的安全要求..."
        result = _extract_regulatory_scope(text)
        
        assert "建设" in result
        assert "运营" in result
        assert "维护" in result
        assert "安全" in result
        
    def test_limit_scope_results(self):
        """Test that scope results are limited"""
        text = "并网验收申请审批许可备案建设运营维护安全环保土地规划设计施工调试运行监管" * 5
        result = _extract_regulatory_scope(text)
        
        assert len(result) <= 10  # Should be limited to 10


class TestAnalyzeSourceUrl:
    """Test source URL analysis"""
    
    def test_analyze_government_url(self):
        """Test analysis of government URL"""
        url = "https://gd.gov.cn/documents/policy.pdf?version=1"
        result = _analyze_source_url(url)
        
        assert result['source_domain'] == 'gd.gov.cn'
        assert result['is_government_source'] is True
        assert result['url_path_depth'] == 2
        assert result['has_query_params'] is True
        
    def test_analyze_non_government_url(self):
        """Test analysis of non-government URL"""
        url = "https://example.com/doc.pdf"
        result = _analyze_source_url(url)
        
        assert result['source_domain'] == 'example.com'
        assert result['is_government_source'] is False
        assert result['url_path_depth'] == 1
        assert result['has_query_params'] is False
        
    def test_analyze_invalid_url(self):
        """Test analysis of invalid URL"""
        result = _analyze_source_url("not-a-url")
        
        assert result['source_domain'] == 'unknown'
        assert result['is_government_source'] is False


class TestIsGovernmentDomain:
    """Test government domain detection"""
    
    def test_chinese_government_domain(self):
        """Test Chinese government domain detection"""
        assert _is_government_domain("gd.gov.cn") is True
        assert _is_government_domain("www.gov.cn") is True
        
    def test_international_government_domain(self):
        """Test international government domain detection"""
        assert _is_government_domain("example.gov") is True
        assert _is_government_domain("ministry.gov.uk") is True
        
    def test_non_government_domain(self):
        """Test non-government domain detection"""
        assert _is_government_domain("example.com") is False
        assert _is_government_domain("company.org") is False


class TestValidateMetadataCompleteness:
    """Test metadata completeness validation"""
    
    def test_complete_metadata(self):
        """Test validation of complete metadata"""
        metadata = {
            'title': '广东省光伏并网管理办法',
            'url': 'https://gd.gov.cn/doc.pdf',
            'province': 'gd',
            'asset': 'solar',
            'doc_class': 'grid',
            'effective_date': '2024-06-01',
            'issuing_authority': '广东省发改委',
            'document_number': '粤发改〔2024〕15号'
        }
        
        result = validate_metadata_completeness(metadata)
        
        assert result['is_complete'] is True
        assert len(result['missing_required']) == 0
        assert len(result['missing_optional']) == 0
        assert result['quality_score'] == 1.0
        
    def test_incomplete_metadata(self):
        """Test validation of incomplete metadata"""
        metadata = {
            'title': '测试文档',
            'url': 'https://example.com/doc.pdf',
            # Missing province, asset, doc_class
            'effective_date': '2024-06-01'
        }
        
        result = validate_metadata_completeness(metadata)
        
        assert result['is_complete'] is False
        assert 'province' in result['missing_required']
        assert 'asset' in result['missing_required']
        assert 'doc_class' in result['missing_required']
        assert result['quality_score'] < 1.0


if __name__ == "__main__":
    pytest.main([__file__])