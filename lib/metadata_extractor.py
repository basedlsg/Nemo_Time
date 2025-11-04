"""
Document metadata extraction module
Handles extraction and validation of document metadata
"""

import re
import hashlib
from typing import Dict, Any, Optional, List
from urllib.parse import urlparse
from .sanitize import (
    extract_effective_date, extract_title_from_text, extract_document_type,
    normalize_province_code, normalize_asset_type
)


def extract_comprehensive_metadata(
    text: str, 
    url: str, 
    province: str = None, 
    asset: str = None, 
    doc_class: str = None
) -> Dict[str, Any]:
    """
    Extract comprehensive metadata from document text and context
    
    Args:
        text: Document text content
        url: Source URL
        province: Province code hint
        asset: Asset type hint  
        doc_class: Document class hint
        
    Returns:
        Dictionary with extracted metadata
    """
    metadata = {}
    
    # Basic document information
    metadata['title'] = extract_title_from_text(text) or _extract_title_from_url(url)
    metadata['effective_date'] = extract_effective_date(text)
    metadata['doc_type'] = extract_document_type(text)
    metadata['url'] = url
    metadata['checksum'] = _calculate_content_checksum(text)
    
    # Geographic and asset classification
    metadata['province'] = _determine_province(text, url, province)
    metadata['asset'] = _determine_asset_type(text, url, asset)
    metadata['doc_class'] = _determine_document_class(text, url, doc_class)
    
    # Administrative information
    metadata['issuing_authority'] = _extract_issuing_authority(text)
    metadata['document_number'] = _extract_document_number(text)
    metadata['publication_date'] = _extract_publication_date(text)
    
    # Content analysis
    metadata['language'] = _detect_language(text)
    metadata['content_length'] = len(text)
    metadata['regulatory_scope'] = _extract_regulatory_scope(text)
    
    # URL analysis
    url_info = _analyze_source_url(url)
    metadata.update(url_info)
    
    return metadata


def _extract_title_from_url(url: str) -> Optional[str]:
    """
    Extract potential title from URL path
    
    Args:
        url: Document URL
        
    Returns:
        Extracted title or None
    """
    try:
        parsed = urlparse(url)
        path = parsed.path
        
        # Remove file extension and path separators
        filename = path.split('/')[-1]
        if '.' in filename:
            filename = filename.rsplit('.', 1)[0]
            
        # Clean up filename
        title = filename.replace('_', ' ').replace('-', ' ')
        
        # Only return if it looks like a meaningful title
        if len(title) > 5 and not title.isdigit():
            return title
            
    except Exception:
        pass
        
    return None


def _calculate_content_checksum(text: str) -> str:
    """
    Calculate SHA-256 checksum of text content
    
    Args:
        text: Text content
        
    Returns:
        Hexadecimal checksum string
    """
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


def _determine_province(text: str, url: str, hint: str = None) -> Optional[str]:
    """
    Determine province from text, URL, and hint
    
    Args:
        text: Document text
        url: Source URL
        hint: Province hint
        
    Returns:
        Province code (gd, sd, nm) or None
    """
    # Use hint if provided and valid
    if hint:
        normalized_hint = normalize_province_code(hint)
        if normalized_hint:
            return normalized_hint
    
    # Check URL for province indicators
    url_lower = url.lower()
    if 'gd.gov.cn' in url_lower or 'guangdong' in url_lower:
        return 'gd'
    elif 'sd.gov.cn' in url_lower or 'shandong' in url_lower:
        return 'sd'
    elif 'nmg.gov.cn' in url_lower or 'neimenggu' in url_lower:
        return 'nm'
    
    # Check text content for province names
    text_sample = text[:1000].lower()  # Check first 1000 chars
    
    province_patterns = {
        'gd': ['广东', '粤'],
        'sd': ['山东', '鲁'],
        'nm': ['内蒙古', '蒙']
    }
    
    for code, patterns in province_patterns.items():
        if any(pattern in text_sample for pattern in patterns):
            return code
            
    return None


def _determine_asset_type(text: str, url: str, hint: str = None) -> Optional[str]:
    """
    Determine asset type from text, URL, and hint
    
    Args:
        text: Document text
        url: Source URL
        hint: Asset type hint
        
    Returns:
        Asset type (solar, coal, wind) or None
    """
    # Use hint if provided and valid
    if hint:
        normalized_hint = normalize_asset_type(hint)
        if normalized_hint:
            return normalized_hint
    
    # Check URL for asset type indicators
    url_lower = url.lower()
    if any(term in url_lower for term in ['solar', 'photovoltaic', 'pv']):
        return 'solar'
    elif any(term in url_lower for term in ['coal', 'thermal']):
        return 'coal'
    elif any(term in url_lower for term in ['wind', 'windfarm']):
        return 'wind'
    
    # Check text content for asset type keywords
    text_sample = text[:2000].lower()  # Check first 2000 chars
    
    asset_patterns = {
        'solar': ['光伏', '太阳能', '分布式光伏', 'pv'],
        'coal': ['煤电', '火电', '燃煤', '热电'],
        'wind': ['风电', '风力发电', '风能', '海上风电', '陆上风电']
    }
    
    # Count occurrences of each asset type
    asset_scores = {}
    for asset_type, patterns in asset_patterns.items():
        score = sum(text_sample.count(pattern) for pattern in patterns)
        if score > 0:
            asset_scores[asset_type] = score
    
    # Return asset type with highest score
    if asset_scores:
        return max(asset_scores, key=asset_scores.get)
        
    return None


def _determine_document_class(text: str, url: str, hint: str = None) -> Optional[str]:
    """
    Determine document class from text, URL, and hint
    
    Args:
        text: Document text
        url: Source URL
        hint: Document class hint
        
    Returns:
        Document class or None
    """
    # Use hint if provided
    if hint:
        return hint
    
    # For MVP, focus on grid connection documents
    grid_keywords = [
        '并网', '接入', '电网', '上网', '发电', '电力接入',
        'grid', 'connection', 'interconnection'
    ]
    
    text_sample = text[:1000].lower()
    url_lower = url.lower()
    
    # Check for grid connection indicators
    grid_score = 0
    for keyword in grid_keywords:
        grid_score += text_sample.count(keyword)
        grid_score += url_lower.count(keyword)
    
    if grid_score > 0:
        return 'grid'
        
    return None


def _extract_issuing_authority(text: str) -> Optional[str]:
    """
    Extract issuing authority from document text
    
    Args:
        text: Document text
        
    Returns:
        Issuing authority name or None
    """
    # Common patterns for issuing authorities
    patterns = [
        r'([^。]*?发展(?:和)?改革委员会)',
        r'([^。]*?能源局)',
        r'([^。]*?电力公司)',
        r'([^。]*?人民政府)',
        r'([^。]*?工业和信息化厅)',
        r'([^。]*?住房和城乡建设厅)'
    ]
    
    # Search in first 500 characters where authority is typically mentioned
    search_text = text[:500]
    
    for pattern in patterns:
        matches = re.findall(pattern, search_text)
        if matches:
            authority = matches[0].strip()
            if 5 <= len(authority) <= 50:  # Reasonable length
                return authority
                
    return None


def _extract_document_number(text: str) -> Optional[str]:
    """
    Extract document number from text
    
    Args:
        text: Document text
        
    Returns:
        Document number or None
    """
    # Common patterns for Chinese government document numbers
    patterns = [
        r'([^。]*?〔\d{4}〕\d+号)',
        r'([^。]*?\[\d{4}\]\d+号)',
        r'([^。]*?第\d+号)',
        r'([^。]*?\d{4}年第\d+号)'
    ]
    
    # Search in first 300 characters
    search_text = text[:300]
    
    for pattern in patterns:
        matches = re.findall(pattern, search_text)
        if matches:
            doc_number = matches[0].strip()
            if len(doc_number) <= 30:  # Reasonable length
                return doc_number
                
    return None


def _extract_publication_date(text: str) -> Optional[str]:
    """
    Extract publication date (different from effective date)
    
    Args:
        text: Document text
        
    Returns:
        Publication date in YYYY-MM-DD format or None
    """
    # Patterns for publication/issuance dates
    patterns = [
        r'印发日期[：:]\s*(\d{4})年(\d{1,2})月(\d{1,2})日',
        r'发布日期[：:]\s*(\d{4})年(\d{1,2})月(\d{1,2})日',
        r'颁布日期[：:]\s*(\d{4})年(\d{1,2})月(\d{1,2})日',
        r'(\d{4})年(\d{1,2})月(\d{1,2})日印发',
        r'(\d{4})年(\d{1,2})月(\d{1,2})日发布'
    ]
    
    search_text = text[:1000]
    
    for pattern in patterns:
        matches = re.finditer(pattern, search_text)
        for match in matches:
            year, month, day = match.groups()
            
            # Pad and validate
            month = month.zfill(2)
            day = day.zfill(2)
            
            try:
                year_int = int(year)
                month_int = int(month)
                day_int = int(day)
                
                if (2000 <= year_int <= 2030 and 
                    1 <= month_int <= 12 and 
                    1 <= day_int <= 31):
                    return f"{year}-{month}-{day}"
            except ValueError:
                continue
                
    return None


def _detect_language(text: str) -> str:
    """
    Detect document language
    
    Args:
        text: Document text
        
    Returns:
        Language code (zh-CN, en, etc.)
    """
    if not text:
        return 'unknown'
    
    # Count Chinese characters
    chinese_chars = sum(1 for char in text if '\u4e00' <= char <= '\u9fff')
    total_chars = len(re.sub(r'\s', '', text))
    
    if total_chars == 0:
        return 'unknown'
    
    chinese_ratio = chinese_chars / total_chars
    
    if chinese_ratio >= 0.3:
        return 'zh-CN'
    elif chinese_ratio < 0.1:
        return 'en'
    else:
        return 'mixed'


def _extract_regulatory_scope(text: str) -> List[str]:
    """
    Extract regulatory scope keywords from text
    
    Args:
        text: Document text
        
    Returns:
        List of scope keywords
    """
    scope_keywords = [
        '并网', '验收', '申请', '审批', '许可', '备案',
        '建设', '运营', '维护', '安全', '环保', '土地',
        '规划', '设计', '施工', '调试', '运行', '监管'
    ]
    
    found_scopes = []
    text_lower = text.lower()
    
    for keyword in scope_keywords:
        if keyword in text_lower:
            found_scopes.append(keyword)
    
    return found_scopes[:10]  # Limit to top 10


def _analyze_source_url(url: str) -> Dict[str, Any]:
    """
    Analyze source URL for additional metadata
    
    Args:
        url: Source URL
        
    Returns:
        Dictionary with URL analysis results
    """
    try:
        parsed = urlparse(url)
        
        return {
            'source_domain': parsed.netloc,
            'is_government_source': _is_government_domain(parsed.netloc),
            'url_path_depth': len([p for p in parsed.path.split('/') if p]),
            'has_query_params': bool(parsed.query)
        }
        
    except Exception:
        return {
            'source_domain': 'unknown',
            'is_government_source': False,
            'url_path_depth': 0,
            'has_query_params': False
        }


def _is_government_domain(domain: str) -> bool:
    """
    Check if domain is a government domain
    
    Args:
        domain: Domain name
        
    Returns:
        True if government domain
    """
    gov_indicators = [
        '.gov.cn',
        '.gov.',
        'government',
        'ministry',
        'bureau'
    ]
    
    domain_lower = domain.lower()
    return any(indicator in domain_lower for indicator in gov_indicators)


def validate_metadata_completeness(metadata: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate metadata completeness and quality
    
    Args:
        metadata: Metadata dictionary
        
    Returns:
        Validation results
    """
    required_fields = ['title', 'url', 'province', 'asset', 'doc_class']
    optional_fields = ['effective_date', 'issuing_authority', 'document_number']
    
    validation = {
        'is_complete': True,
        'missing_required': [],
        'missing_optional': [],
        'quality_score': 0.0
    }
    
    # Check required fields
    for field in required_fields:
        if not metadata.get(field):
            validation['missing_required'].append(field)
            validation['is_complete'] = False
    
    # Check optional fields
    for field in optional_fields:
        if not metadata.get(field):
            validation['missing_optional'].append(field)
    
    # Calculate quality score
    total_fields = len(required_fields) + len(optional_fields)
    present_fields = sum(1 for field in required_fields + optional_fields 
                        if metadata.get(field))
    
    validation['quality_score'] = present_fields / total_fields
    
    return validation