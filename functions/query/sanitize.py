"""
Text sanitization and normalization module
Handles Chinese text processing and metadata extraction
"""

import re
from typing import Optional, List, Dict, Any
import unicodedata


def normalize_text(text: str) -> str:
    """
    Normalize Chinese text and standardize punctuation
    
    Args:
        text: Raw text from document processing
        
    Returns:
        Cleaned and normalized UTF-8 text
    """
    if not text:
        return ""
        
    # Remove control characters
    text = ''.join(char for char in text if unicodedata.category(char)[0] != 'C')
    
    # Normalize Unicode to NFC form
    text = unicodedata.normalize('NFC', text)
    
    # Convert full-width characters to half-width where appropriate
    text = text.replace('（', '(').replace('）', ')')
    text = text.replace('【', '[').replace('】', ']')
    text = text.replace('《', '《').replace('》', '》')  # Keep Chinese book quotes
    
    # Standardize Chinese punctuation
    text = text.replace('"', '"').replace('"', '"')  # Smart quotes to Chinese quotes
    text = text.replace("'", "'").replace("'", "'")  # Smart apostrophes
    text = text.replace('—', '——')  # Em dash to Chinese em dash
    
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text)  # Multiple spaces to single
    text = re.sub(r'\n\s*\n', '\n\n', text)  # Multiple newlines to double
    
    # Remove excessive punctuation
    text = re.sub(r'[。]{2,}', '。', text)  # Multiple periods
    text = re.sub(r'[，]{2,}', '，', text)  # Multiple commas
    
    return text.strip()


def normalize_query(query: str) -> str:
    """
    Normalize user query text for better matching
    
    Args:
        query: User input query
        
    Returns:
        Normalized query text
    """
    if not query:
        return ""
        
    # Basic normalization
    query = normalize_text(query)
    
    # Remove common honorifics and stopwords that don't affect meaning
    stopwords = ['请问', '您好', '麻烦', '谢谢']
    for stopword in stopwords:
        query = query.replace(stopword, '')
        
    # Normalize question patterns
    query = re.sub(r'需要什么', '需要哪些', query)
    query = re.sub(r'要什么', '要哪些', query)
    
    return query.strip()


def extract_effective_date(text: str) -> Optional[str]:
    """
    Extract effective date from document text using regex patterns
    
    Args:
        text: Document text to search
        
    Returns:
        Effective date in YYYY-MM-DD format or None if not found
    """
    if not text:
        return None
        
    # Common Chinese date patterns for regulatory documents (ordered by priority)
    patterns = [
        # 生效：2024年6月1日 / 生效日期：2024年6月1日
        r'生效(?:日期)?[：:]\s*(\d{4})年(\d{1,2})月(\d{1,2})日',
        # 实施日期：2024年6月1日 / 施行日期：2024年6月1日
        r'(?:实施|施行)日期[：:]\s*(\d{4})年(\d{1,2})月(\d{1,2})日',
        # 印发日期：2024-06-01
        r'印发日期[：:]\s*(\d{4})-(\d{1,2})-(\d{1,2})',
        # 发布日期：2024.06.01
        r'发布日期[：:]\s*(\d{4})\.(\d{1,2})\.(\d{1,2})',
        # 颁布日期：2024/06/01
        r'颁布日期[：:]\s*(\d{4})/(\d{1,2})/(\d{1,2})',
        # 自2024年6月1日起施行
        r'自(\d{4})年(\d{1,2})月(\d{1,2})日起(?:施行|执行|生效)',
        # 本办法自2024年6月1日起执行
        r'本[办法规定通知意见]{1,3}自(\d{4})年(\d{1,2})月(\d{1,2})日起(?:施行|执行|生效)',
        # 于2024年6月1日生效
        r'于(\d{4})年(\d{1,2})月(\d{1,2})日(?:生效|施行)',
        # 2024年6月1日起执行
        r'(\d{4})年(\d{1,2})月(\d{1,2})日起(?:执行|施行|生效)',
    ]
    
    # Search in first 2000 characters where dates are typically found
    search_text = text[:2000]
    
    for pattern in patterns:
        matches = re.finditer(pattern, search_text)
        for match in matches:
            year, month, day = match.groups()
            
            # Pad month and day with zeros
            month = month.zfill(2)
            day = day.zfill(2)
            
            # Validate date ranges
            try:
                year_int = int(year)
                month_int = int(month)
                day_int = int(day)
                
                # Reasonable date range for regulatory documents
                if (2000 <= year_int <= 2030 and 
                    1 <= month_int <= 12 and 
                    1 <= day_int <= 31):
                    
                    # Additional validation for day ranges by month
                    if month_int in [4, 6, 9, 11] and day_int > 30:
                        continue
                    if month_int == 2 and day_int > 29:
                        continue
                        
                    return f"{year}-{month}-{day}"
            except ValueError:
                continue
                
    return None


def pick_verbatim_spans(text: str, keywords: List[str], max_spans: int = 2) -> List[str]:
    """
    Extract verbatim text spans that match query keywords
    
    Args:
        text: Source document text
        keywords: List of keywords to match
        max_spans: Maximum number of spans to return
        
    Returns:
        List of verbatim text spans
    """
    if not text or not keywords:
        return []
        
    spans = []
    
    # Split text into sentences (Chinese sentence endings)
    sentences = re.split(r'[。！？；]', text)
    
    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue
            
        # Check if sentence contains any keywords
        sentence_lower = sentence.lower()
        keyword_matches = 0
        
        for keyword in keywords:
            if keyword.lower() in sentence_lower:
                keyword_matches += 1
                
        # If sentence has keyword matches, consider it
        if keyword_matches > 0:
            # Prefer sentences with more keyword matches
            spans.append((sentence, keyword_matches))
            
    # Sort by keyword match count (descending) and take top spans
    spans.sort(key=lambda x: x[1], reverse=True)
    
    # Return just the text, limited to max_spans
    return [span[0] for span in spans[:max_spans]]


def extract_title_from_text(text: str) -> Optional[str]:
    """
    Extract document title from text content
    
    Args:
        text: Document text
        
    Returns:
        Extracted title or None
    """
    if not text:
        return None
        
    # Look for common title patterns in Chinese regulatory documents
    lines = text.split('\n')[:10]  # Check first 10 lines
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Skip very short lines
        if len(line) < 5:
            continue
            
        # Look for regulatory document patterns
        if any(keyword in line for keyword in ['办法', '规定', '通知', '意见', '管理', '实施']):
            # Remove common prefixes
            line = re.sub(r'^关于', '', line)
            line = re.sub(r'^印发', '', line)
            
            # Clean up title
            line = line.replace('《', '').replace('》', '')
            line = line.strip('：: ')
            
            if 5 <= len(line) <= 100:  # Reasonable title length
                return line
                
    return None

def clean_table_content(text: str) -> str:
    """
    Clean and preserve important table content while removing noise
    
    Args:
        text: Raw text that may contain table data
        
    Returns:
        Cleaned text with preserved table information
    """
    if not text:
        return ""
        
    # Preserve tables that contain key regulatory information
    key_phrases = [
        '资料清单', '材料清单', '文件清单', '证件清单',
        '受理时限', '审批时限', '办理时限', '处理时限',
        '收费标准', '费用标准', '价格标准',
        '技术要求', '技术标准', '技术规范',
        '申请条件', '准入条件', '资质要求'
    ]
    
    lines = text.split('\n')
    cleaned_lines = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Keep lines with key regulatory phrases
        if any(phrase in line for phrase in key_phrases):
            cleaned_lines.append(line)
            continue
            
        # Remove lines that are mostly formatting characters
        if len(re.sub(r'[|\-_=+\s]', '', line)) < 3:
            continue
            
        # Remove lines with excessive repetitive characters
        if len(set(line)) < 3:
            continue
            
        cleaned_lines.append(line)
        
    return '\n'.join(cleaned_lines)


def extract_document_type(text: str) -> Optional[str]:
    """
    Extract document type from text content
    
    Args:
        text: Document text
        
    Returns:
        Document type or None if not identified
    """
    if not text:
        return None
        
    # Common regulatory document types
    doc_types = {
        '办法': 'regulation',
        '规定': 'provision', 
        '通知': 'notice',
        '意见': 'opinion',
        '指导意见': 'guidance',
        '实施细则': 'implementation_rules',
        '管理规定': 'management_provision',
        '技术规范': 'technical_standard',
        '标准': 'standard',
        '指南': 'guideline'
    }
    
    # Search in first 500 characters for document type
    search_text = text[:500]
    
    for doc_type, category in doc_types.items():
        if doc_type in search_text:
            return category
            
    return None


def validate_chinese_content_quality(text: str) -> Dict[str, Any]:
    """
    Validate the quality of Chinese text content
    
    Args:
        text: Text to validate
        
    Returns:
        Dictionary with quality metrics
    """
    if not text:
        return {
            'is_valid': False,
            'chinese_ratio': 0.0,
            'length': 0,
            'has_regulatory_terms': False
        }
        
    # Count Chinese characters
    chinese_chars = sum(1 for char in text if '\u4e00' <= char <= '\u9fff')
    total_chars = len(re.sub(r'\s', '', text))  # Exclude whitespace
    
    chinese_ratio = chinese_chars / total_chars if total_chars > 0 else 0.0
    
    # Check for regulatory terminology
    regulatory_terms = [
        '并网', '验收', '申请', '审批', '许可', '证书', '资质',
        '管理', '规定', '办法', '标准', '规范', '要求', '条件',
        '程序', '流程', '时限', '费用', '收费', '材料', '资料'
    ]
    
    has_regulatory_terms = any(term in text for term in regulatory_terms)
    
    # Determine if content is valid
    is_valid = (
        chinese_ratio >= 0.3 and  # At least 30% Chinese characters
        len(text) >= 50 and       # Minimum length
        has_regulatory_terms      # Contains regulatory terminology
    )
    
    return {
        'is_valid': is_valid,
        'chinese_ratio': chinese_ratio,
        'length': len(text),
        'has_regulatory_terms': has_regulatory_terms,
        'regulatory_term_count': sum(1 for term in regulatory_terms if term in text)
    }


def normalize_province_code(province_input: str) -> Optional[str]:
    """
    Normalize province input to standard codes
    
    Args:
        province_input: Province name or code
        
    Returns:
        Standardized province code (gd, sd, nm) or None
    """
    if not province_input:
        return None
        
    province_input = province_input.lower().strip()
    
    # Direct code mapping
    if province_input in ['gd', 'sd', 'nm']:
        return province_input
        
    # Name to code mapping
    name_mapping = {
        '广东': 'gd',
        '广东省': 'gd',
        'guangdong': 'gd',
        '山东': 'sd',
        '山东省': 'sd', 
        'shandong': 'sd',
        '内蒙古': 'nm',
        '内蒙古自治区': 'nm',
        'inner mongolia': 'nm',
        'neimenggu': 'nm'
    }
    
    return name_mapping.get(province_input)


def normalize_asset_type(asset_input: str) -> Optional[str]:
    """
    Normalize asset type input to standard codes
    
    Args:
        asset_input: Asset type name or code
        
    Returns:
        Standardized asset code (solar, coal, wind) or None
    """
    if not asset_input:
        return None
        
    asset_input = asset_input.lower().strip()
    
    # Direct code mapping
    if asset_input in ['solar', 'coal', 'wind']:
        return asset_input
        
    # Name to code mapping
    name_mapping = {
        '光伏': 'solar',
        '太阳能': 'solar',
        '煤电': 'coal',
        '煤炭': 'coal',
        '火电': 'coal',
        '风电': 'wind',
        '风能': 'wind',
        '风力': 'wind'
    }
    
    return name_mapping.get(asset_input)