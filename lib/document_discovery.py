"""
Document Discovery Module - Real Implementation
Uses Perplexity API to discover relevant government documents, then verifies and downloads them.
No mocks, no CSE - pure Perplexity-based discovery.
"""

import requests
import hashlib
import time
from typing import List, Dict, Optional
from urllib.parse import urlparse
import logging

logger = logging.getLogger(__name__)


class DocumentDiscoveryError(Exception):
    """Exception raised when document discovery fails"""
    pass


def discover_documents_with_perplexity(
    province: str,
    asset: str,
    doc_class: str,
    perplexity_api_key: str,
    max_documents: int = 20
) -> List[Dict[str, str]]:
    """
    Discover government documents using Perplexity API.

    Strategy:
    1. Use Perplexity to find relevant .gov.cn documents
    2. Extract URLs from citations
    3. Verify URLs are valid .gov.cn domains
    4. Return list of verified document URLs with metadata

    Args:
        province: Province code (e.g., 'gd', 'sd', 'nm')
        asset: Asset type (e.g., 'solar', 'coal', 'wind')
        doc_class: Document class (e.g., 'grid', 'land_survey', 'environmental')
        perplexity_api_key: Perplexity API key
        max_documents: Maximum number of documents to discover

    Returns:
        List of document dictionaries with keys:
        - url: Document URL
        - title: Document title
        - province: Province code
        - asset: Asset type
        - doc_class: Document classification
        - source: Source domain
    """

    # Map province codes to Chinese names
    province_names = {
        'gd': '广东省',
        'sd': '山东省',
        'nm': '内蒙古自治区',
        'bj': '北京市',
        'sh': '上海市',
    }

    # Map asset types to Chinese terms
    asset_names = {
        'solar': '光伏发电',
        'coal': '煤电',
        'wind': '风电',
        'hydro': '水电',
    }

    # Map doc classes to Chinese terms
    doc_class_names = {
        'grid': '并网验收',
        'land_survey': '土地勘测',
        'environmental': '环境评估',
    }

    province_cn = province_names.get(province, province)
    asset_cn = asset_names.get(asset, asset)
    doc_class_cn = doc_class_names.get(doc_class, doc_class)

    # Build discovery query
    query = f"""
请找出{province_cn}关于{asset_cn}项目{doc_class_cn}的官方政府文件和政策法规。
要求：
1. 必须是.gov.cn官方网站的文件
2. 包含具体的办理流程、所需材料、审批要求等实用信息
3. 优先选择PDF格式的政策文件、办事指南、技术规范
4. 提供每个文件的完整URL链接

请列出至少10个相关的官方文件，包括：
- 文件标题
- 发布部门
- 文件URL
- 发布时间（如果有）
"""

    # Domain filter for government sites
    domain_filter = [
        f"{province}.gov.cn",
        f"drc.{province}.gov.cn",  # Development and Reform Commission
        f"nr.{province}.gov.cn",   # Natural Resources
        f"sthjt.{province}.gov.cn", # Ecology and Environment
        f"fgw.{province}.gov.cn",  # Development and Reform
        "ndrc.gov.cn",              # National Development and Reform Commission
        "nea.gov.cn",               # National Energy Administration
        "www.gov.cn",               # Central government
    ]

    # Call Perplexity API for discovery
    try:
        url = "https://api.perplexity.ai/chat/completions"
        headers = {
            "Authorization": f"Bearer {perplexity_api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": "sonar-pro",
            "messages": [
                {
                    "role": "system",
                    "content": "你是专业的政府文件检索助手。请准确找出官方.gov.cn网站上的政策文件，并提供完整的URL链接。"
                },
                {
                    "role": "user",
                    "content": query
                }
            ],
            "search_domain_filter": domain_filter,
            "search_recency_filter": "year",
            "return_citations": True,
            "web_search_options": {
                "search_context_size": "high"
            },
            "temperature": 0.1,
            "max_tokens": 4000,
        }

        logger.info(f"Discovering documents for {province_cn} {asset_cn} {doc_class_cn}")

        # Retry logic for API resilience
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = requests.post(url, json=payload, headers=headers, timeout=30)

                # If we get rate limited or server error, retry
                if response.status_code in [429, 500, 502, 503, 504]:
                    if attempt < max_retries - 1:
                        wait_time = 2 ** attempt  # Exponential backoff: 1s, 2s, 4s
                        logger.warning(f"API returned {response.status_code}, retrying in {wait_time}s...")
                        time.sleep(wait_time)
                        continue

                response.raise_for_status()
                break

            except requests.exceptions.RequestException as e:
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt
                    logger.warning(f"Request failed: {str(e)}, retrying in {wait_time}s...")
                    time.sleep(wait_time)
                    continue
                raise

        data = response.json()

        # Extract citations (these are the discovered documents)
        citations = data.get('citations', [])

        if not citations:
            logger.warning(f"No citations found for {province} {asset} {doc_class}")
            return []

        # Process citations into document records
        documents = []
        seen_urls = set()

        for citation in citations[:max_documents]:
            url = citation.get('url', '')

            # Verify it's a .gov.cn domain
            if not url or not _is_valid_gov_cn_url(url):
                continue

            # Avoid duplicates
            if url in seen_urls:
                continue
            seen_urls.add(url)

            # Extract domain for source
            parsed = urlparse(url)
            source = parsed.netloc

            # Create document record
            doc = {
                'url': url,
                'title': citation.get('title', ''),
                'province': province,
                'asset': asset,
                'doc_class': doc_class,
                'source': source,
                'discovered_at': int(time.time()),
            }

            documents.append(doc)
            logger.info(f"Discovered: {doc['title'][:50]}... from {source}")

        logger.info(f"Discovered {len(documents)} documents for {province} {asset} {doc_class}")
        return documents

    except requests.exceptions.RequestException as e:
        logger.error(f"Perplexity API error during discovery: {str(e)}")
        raise DocumentDiscoveryError(f"Failed to discover documents: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error during discovery: {str(e)}")
        raise DocumentDiscoveryError(f"Discovery failed: {str(e)}")


def discover_documents(
    province: str,
    asset: str,
    doc_class: str,
    api_key: Optional[str] = None,
    max_results: int = 20
) -> List[str]:
    """
    Backward-compatible wrapper for document discovery.
    Returns list of URLs for compatibility with existing ingestion pipeline.

    Args:
        province: Province code
        asset: Asset type
        doc_class: Document class
        api_key: Perplexity API key (if None, reads from env)
        max_results: Maximum number of URLs to return

    Returns:
        List of document URLs
    """
    import os

    # Get API key from environment if not provided
    if api_key is None:
        api_key = os.environ.get('PERPLEXITY_API_KEY')

    if not api_key:
        raise DocumentDiscoveryError("PERPLEXITY_API_KEY not set")

    # Discover documents
    documents = discover_documents_with_perplexity(
        province=province,
        asset=asset,
        doc_class=doc_class,
        perplexity_api_key=api_key,
        max_documents=max_results
    )

    # Return just the URLs for backward compatibility
    return [doc['url'] for doc in documents]


def _is_valid_gov_cn_url(url: str) -> bool:
    """
    Verify URL is from a legitimate .gov.cn domain.

    Security check to prevent malicious URLs.
    """
    try:
        parsed = urlparse(url)
        domain = parsed.netloc.lower()

        # Must be .gov.cn domain
        if not domain.endswith('.gov.cn'):
            return False

        # Must use http or https
        if parsed.scheme not in ['http', 'https']:
            return False

        return True

    except Exception:
        return False


def generate_document_id(url: str) -> str:
    """
    Generate a unique document ID from URL.
    Uses SHA256 hash for consistency.
    """
    return hashlib.sha256(url.encode('utf-8')).hexdigest()[:16]


# Example usage and testing
if __name__ == "__main__":
    import sys
    import os

    logging.basicConfig(level=logging.INFO)

    # Test discovery
    try:
        api_key = sys.argv[1] if len(sys.argv) > 1 else None

        documents = discover_documents_with_perplexity(
            province='gd',
            asset='solar',
            doc_class='grid',
            perplexity_api_key=api_key or os.environ.get('PERPLEXITY_API_KEY'),
            max_documents=10
        )

        print(f"\n✅ Discovered {len(documents)} documents:\n")
        for i, doc in enumerate(documents, 1):
            print(f"{i}. {doc['title']}")
            print(f"   URL: {doc['url']}")
            print(f"   Source: {doc['source']}")
            print()

    except Exception as e:
        print(f"❌ Error: {str(e)}", file=sys.stderr)
        sys.exit(1)
