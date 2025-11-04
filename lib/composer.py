"""
Response composition module
Formats Chinese answers with verbatim quotes and citations
"""

from typing import Dict, Any, List
from lib.sanitize import pick_verbatim_spans


def compose_response(
    candidates: List[Dict[str, Any]],
    question: str,
    lang: str = "zh-CN"
) -> Dict[str, Any]:
    """
    Compose response with Chinese bullets and citations

    Args:
        candidates: List of candidate document chunks from vector search
        question: Original user question
        lang: Response language (zh-CN or en)

    Returns:
        Formatted response with answer and citations
    """
    if not candidates:
        return {
            'answer_zh': '',
            'citations': []
        }

    # Extract keywords from question for span matching
    keywords = _extract_keywords(question)

    # Process candidates to extract quotes and build citations
    quotes = []
    citations_dict: Dict[str, Dict[str, Any]] = {}  # Deduplicate by URL

    for candidate in candidates[:5]:  # Limit to top 5 for response quality
        # Accept both modern schema (metadata/text) and simplified schema (title/content/url)
        metadata = candidate.get('metadata') or {}
        if not metadata:
            metadata = {
                key: candidate.get(key)
                for key in ('title', 'url', 'effective_date', 'province', 'asset')
                if candidate.get(key)
            }
        text = candidate.get('text') or candidate.get('content', '')

        if not text:
            continue

        # Extract verbatim spans from this chunk
        spans = pick_verbatim_spans(text, keywords, max_spans=2)

        # Fallback to use leading passage when no keywords match
        if not spans:
            snippet = text.strip()
            if snippet:
                spans = [snippet[:120]]

        for span in spans:
            if len(span) > 20:  # Only include substantial quotes
                # Format quote with citation
                title = metadata.get('title', '未知文档')
                effective_date = metadata.get('effective_date')

                if effective_date:
                    citation_suffix = f"〔《{title}》，生效：{effective_date}〕"
                else:
                    citation_suffix = f"〔《{title}》〕"

                formatted_quote = f" • {span}{citation_suffix}"
                quotes.append(formatted_quote)

                # Add to citations (deduplicate by URL)
                url = metadata.get('url', '')
                if url and url not in citations_dict:
                    citations_dict[url] = {
                        'title': title,
                        'effective_date': effective_date,
                        'url': url
                    }

    # Build final response
    if quotes:
        # Determine province and asset for title
        first_candidate = candidates[0]
        first_metadata = first_candidate.get('metadata') or {}
        if not first_metadata:
            first_metadata = {
                key: first_candidate.get(key)
                for key in ('province', 'asset')
                if first_candidate.get(key)
            }
        province_code = first_metadata.get('province', '')
        asset = first_metadata.get('asset', '')

        province_names = {
            'gd': '广东',
            'sd': '山东',
            'nm': '内蒙古'
        }

        asset_names = {
            'solar': '光伏',
            'coal': '煤电',
            'wind': '风电'
        }

        province_name = province_names.get(province_code, province_code or '综合')
        asset_name = asset_names.get(asset, asset or '能源')

        # Format response
        title = f"并网要点（{province_name} / {asset_name}）"
        bullets = "\n".join(quotes[:4])  # Limit to 4 bullets max

        answer_zh = f"{title}\n- 相关规定：\n{bullets}"

        # Convert citations dict to list
        citations = list(citations_dict.values())

        return {
            'answer_zh': answer_zh,
            'citations': citations
        }

    return {
        'answer_zh': '',
        'citations': []
    }


def _extract_keywords(question: str) -> List[str]:
    """
    Extract key terms from user question for span matching
    
    Args:
        question: User question text
        
    Returns:
        List of keywords
    """
    # Common regulatory keywords to prioritize
    regulatory_terms = [
        '并网', '验收', '资料', '清单', '要求', '条件', '程序', '流程',
        '申请', '审批', '许可', '证书', '标准', '规范', '技术', '安全',
        '环保', '土地', '规划', '建设', '运营', '维护', '监管', '检查'
    ]
    
    keywords = []
    
    # Add regulatory terms that appear in question
    for term in regulatory_terms:
        if term in question:
            keywords.append(term)
            
    # Add other significant words from question (2+ characters)
    import re
    words = re.findall(r'[\u4e00-\u9fff]{2,}', question)  # Chinese words 2+ chars
    
    for word in words:
        if word not in keywords and len(word) >= 2:
            keywords.append(word)
            
    # Limit to most relevant keywords
    return keywords[:8]


def format_citation(metadata: Dict[str, Any]) -> Dict[str, Any]:
    """
    Format citation from document metadata
    
    Args:
        metadata: Document metadata
        
    Returns:
        Formatted citation dictionary
    """
    citation = {
        'title': metadata.get('title', '未知文档'),
        'url': metadata.get('url', '')
    }
    
    # Add effective date if available
    effective_date = metadata.get('effective_date')
    if effective_date:
        citation['effective_date'] = effective_date
        
    return citation


def validate_response(response: Dict[str, Any]) -> bool:
    """
    Validate response format and content
    
    Args:
        response: Response dictionary to validate
        
    Returns:
        True if response is valid
    """
    # Check required fields
    if 'answer_zh' not in response or 'citations' not in response:
        return False
        
    # Check that answer is in Chinese if not empty
    answer = response.get('answer_zh', '')
    if answer:
        # Simple check for Chinese characters
        chinese_chars = sum(1 for char in answer if '\u4e00' <= char <= '\u9fff')
        if chinese_chars < len(answer) * 0.3:  # At least 30% Chinese
            return False
            
    # Validate citations format
    citations = response.get('citations', [])
    if not isinstance(citations, list):
        return False
        
    for citation in citations:
        if not isinstance(citation, dict):
            return False
        if 'title' not in citation or 'url' not in citation:
            return False
            
    return True
