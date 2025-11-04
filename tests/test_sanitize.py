"""
Unit tests for text sanitization and normalization module
"""

import pytest
from lib.sanitize import (
    normalize_text, normalize_query, extract_effective_date,
    pick_verbatim_spans, extract_title_from_text, clean_table_content,
    extract_document_type, validate_chinese_content_quality,
    normalize_province_code, normalize_asset_type
)


class TestNormalizeText:
    """Test text normalization functionality"""
    
    def test_normalize_basic_chinese_text(self):
        """Test basic Chinese text normalization"""
        input_text = "广东省光伏并网管理办法（试行）"
        result = normalize_text(input_text)
        assert result == "广东省光伏并网管理办法(试行)"
        
    def test_normalize_punctuation(self):
        """Test punctuation normalization"""
        input_text = ""这是一个"测试"文档""
        result = normalize_text(input_text)
        assert result == ""这是一个"测试"文档""
        
    def test_normalize_whitespace(self):
        """Test whitespace normalization"""
        input_text = "广东省    光伏\n\n\n并网管理办法"
        result = normalize_text(input_text)
        assert result == "广东省 光伏\n\n并网管理办法"
        
    def test_remove_control_characters(self):
        """Test removal of control characters"""
        input_text = "广东省\x00光伏\x01并网"
        result = normalize_text(input_text)
        assert result == "广东省光伏并网"
        
    def test_empty_input(self):
        """Test handling of empty input"""
        assert normalize_text("") == ""
        assert normalize_text(None) == ""


class TestNormalizeQuery:
    """Test query normalization functionality"""
    
    def test_remove_honorifics(self):
        """Test removal of common honorifics"""
        input_query = "请问并网需要什么资料？谢谢"
        result = normalize_query(input_query)
        assert "请问" not in result
        assert "谢谢" not in result
        assert "并网" in result
        
    def test_normalize_question_patterns(self):
        """Test normalization of question patterns"""
        input_query = "并网需要什么资料？"
        result = normalize_query(input_query)
        assert "需要哪些" in result
        
    def test_basic_normalization(self):
        """Test that basic text normalization is applied"""
        input_query = "请问（并网）需要什么？"
        result = normalize_query(input_query)
        assert "(并网)" in result


class TestExtractEffectiveDate:
    """Test effective date extraction functionality"""
    
    def test_extract_standard_format(self):
        """Test extraction of standard date format"""
        text = "本办法自2024年6月1日起施行。"
        result = extract_effective_date(text)
        assert result == "2024-06-01"
        
    def test_extract_with_colon_format(self):
        """Test extraction with colon format"""
        text = "生效日期：2024年3月15日"
        result = extract_effective_date(text)
        assert result == "2024-03-15"
        
    def test_extract_dash_format(self):
        """Test extraction of dash format"""
        text = "印发日期：2024-12-25"
        result = extract_effective_date(text)
        assert result == "2024-12-25"
        
    def test_extract_dot_format(self):
        """Test extraction of dot format"""
        text = "发布日期：2024.09.30"
        result = extract_effective_date(text)
        assert result == "2024-09-30"
        
    def test_single_digit_month_day(self):
        """Test handling of single digit months and days"""
        text = "自2024年3月5日起执行"
        result = extract_effective_date(text)
        assert result == "2024-03-05"
        
    def test_invalid_date_ranges(self):
        """Test rejection of invalid date ranges"""
        # Invalid year
        text = "自1999年6月1日起施行"
        result = extract_effective_date(text)
        assert result is None
        
        # Invalid month
        text = "自2024年13月1日起施行"
        result = extract_effective_date(text)
        assert result is None
        
        # Invalid day
        text = "自2024年6月32日起施行"
        result = extract_effective_date(text)
        assert result is None
        
    def test_no_date_found(self):
        """Test when no date is found"""
        text = "这是一个没有日期的文档"
        result = extract_effective_date(text)
        assert result is None
        
    def test_empty_input(self):
        """Test handling of empty input"""
        assert extract_effective_date("") is None
        assert extract_effective_date(None) is None


class TestPickVerbatimSpans:
    """Test verbatim span extraction functionality"""
    
    def test_extract_matching_sentences(self):
        """Test extraction of sentences matching keywords"""
        text = "光伏项目需要提交技术资料。风电项目需要环评报告。煤电项目需要安全评估。"
        keywords = ["光伏", "技术资料"]
        result = pick_verbatim_spans(text, keywords, max_spans=2)
        
        assert len(result) <= 2
        assert any("光伏" in span for span in result)
        assert any("技术资料" in span for span in result)
        
    def test_prioritize_multiple_keywords(self):
        """Test prioritization of spans with multiple keyword matches"""
        text = "光伏并网需要技术资料和安全评估。光伏项目很重要。"
        keywords = ["光伏", "并网", "技术资料"]
        result = pick_verbatim_spans(text, keywords, max_spans=1)
        
        # Should prioritize the sentence with more keyword matches
        assert len(result) == 1
        assert "技术资料" in result[0]
        assert "安全评估" in result[0]
        
    def test_empty_keywords(self):
        """Test handling of empty keywords"""
        text = "这是一个测试文档。"
        result = pick_verbatim_spans(text, [], max_spans=2)
        assert result == []
        
    def test_no_matches(self):
        """Test when no sentences match keywords"""
        text = "这是一个测试文档。"
        keywords = ["光伏", "并网"]
        result = pick_verbatim_spans(text, keywords, max_spans=2)
        assert result == []


class TestExtractTitleFromText:
    """Test title extraction functionality"""
    
    def test_extract_regulation_title(self):
        """Test extraction of regulation title"""
        text = "广东省光伏并网管理办法\n第一条 为规范..."
        result = extract_title_from_text(text)
        assert result == "广东省光伏并网管理办法"
        
    def test_extract_with_brackets(self):
        """Test extraction with brackets removal"""
        text = "《广东省风电并网规定》\n本规定适用于..."
        result = extract_title_from_text(text)
        assert result == "广东省风电并网规定"
        
    def test_extract_with_prefix_removal(self):
        """Test extraction with prefix removal"""
        text = "关于印发《煤电项目管理办法》的通知\n各有关单位..."
        result = extract_title_from_text(text)
        assert result == "煤电项目管理办法"
        
    def test_no_title_found(self):
        """Test when no title is found"""
        text = "这是一个很短的文档"
        result = extract_title_from_text(text)
        assert result is None
        
    def test_empty_input(self):
        """Test handling of empty input"""
        assert extract_title_from_text("") is None
        assert extract_title_from_text(None) is None


class TestValidateChineseContentQuality:
    """Test Chinese content quality validation"""
    
    def test_valid_regulatory_content(self):
        """Test validation of valid regulatory content"""
        text = "广东省光伏并网管理办法规定，申请并网需要提交技术资料和安全评估报告。"
        result = validate_chinese_content_quality(text)
        
        assert result['is_valid'] is True
        assert result['chinese_ratio'] > 0.8
        assert result['has_regulatory_terms'] is True
        assert result['regulatory_term_count'] > 0
        
    def test_insufficient_chinese_content(self):
        """Test rejection of content with insufficient Chinese"""
        text = "This is mostly English content with some 中文 words."
        result = validate_chinese_content_quality(text)
        
        assert result['is_valid'] is False
        assert result['chinese_ratio'] < 0.3
        
    def test_no_regulatory_terms(self):
        """Test rejection of content without regulatory terms"""
        text = "这是一个关于天气的中文文档，没有任何监管相关的内容。"
        result = validate_chinese_content_quality(text)
        
        assert result['is_valid'] is False
        assert result['has_regulatory_terms'] is False
        
    def test_too_short_content(self):
        """Test rejection of content that is too short"""
        text = "短文档"
        result = validate_chinese_content_quality(text)
        
        assert result['is_valid'] is False
        assert result['length'] < 50


class TestNormalizeProvince:
    """Test province code normalization"""
    
    def test_direct_codes(self):
        """Test direct province codes"""
        assert normalize_province_code("gd") == "gd"
        assert normalize_province_code("sd") == "sd"
        assert normalize_province_code("nm") == "nm"
        
    def test_chinese_names(self):
        """Test Chinese province names"""
        assert normalize_province_code("广东") == "gd"
        assert normalize_province_code("广东省") == "gd"
        assert normalize_province_code("山东") == "sd"
        assert normalize_province_code("山东省") == "sd"
        assert normalize_province_code("内蒙古") == "nm"
        assert normalize_province_code("内蒙古自治区") == "nm"
        
    def test_english_names(self):
        """Test English province names"""
        assert normalize_province_code("guangdong") == "gd"
        assert normalize_province_code("shandong") == "sd"
        assert normalize_province_code("inner mongolia") == "nm"
        
    def test_invalid_province(self):
        """Test invalid province input"""
        assert normalize_province_code("北京") is None
        assert normalize_province_code("invalid") is None
        assert normalize_province_code("") is None
        assert normalize_province_code(None) is None


class TestNormalizeAssetType:
    """Test asset type normalization"""
    
    def test_direct_codes(self):
        """Test direct asset codes"""
        assert normalize_asset_type("solar") == "solar"
        assert normalize_asset_type("coal") == "coal"
        assert normalize_asset_type("wind") == "wind"
        
    def test_chinese_names(self):
        """Test Chinese asset names"""
        assert normalize_asset_type("光伏") == "solar"
        assert normalize_asset_type("太阳能") == "solar"
        assert normalize_asset_type("煤电") == "coal"
        assert normalize_asset_type("煤炭") == "coal"
        assert normalize_asset_type("火电") == "coal"
        assert normalize_asset_type("风电") == "wind"
        assert normalize_asset_type("风能") == "wind"
        
    def test_invalid_asset(self):
        """Test invalid asset input"""
        assert normalize_asset_type("水电") is None
        assert normalize_asset_type("nuclear") is None
        assert normalize_asset_type("") is None
        assert normalize_asset_type(None) is None


class TestCleanTableContent:
    """Test table content cleaning"""
    
    def test_preserve_important_tables(self):
        """Test preservation of tables with key regulatory information"""
        text = """
        资料清单：
        1. 技术资料
        2. 安全评估
        ||||||||||||
        其他无关内容
        """
        result = clean_table_content(text)
        assert "资料清单" in result
        assert "技术资料" in result
        assert "||||||||||||" not in result
        
    def test_remove_formatting_noise(self):
        """Test removal of formatting noise"""
        text = """
        重要内容
        --------
        ||||||||
        ========
        更多重要内容
        """
        result = clean_table_content(text)
        assert "重要内容" in result
        assert "更多重要内容" in result
        assert "--------" not in result
        assert "||||||||" not in result


if __name__ == "__main__":
    pytest.main([__file__])