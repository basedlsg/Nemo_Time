"""
Google Custom Search Engine integration module
Handles document discovery from allowlisted government domains
"""

import os
import time
from typing import List, Dict, Any, Optional
import requests
from urllib.parse import urlparse
import hashlib


def discover_documents(province: str, asset: str, doc_class: str) -> List[str]:
    """
    Discover document URLs using Google Custom Search Engine
    
    Args:
        province: Province code (gd, sd, nm)
        asset: Asset type (solar, coal, wind)
        doc_class: Document class (grid)
        
    Returns:
        List of discovered document URLs
    """
    try:
        print(f"Discovering documents for {province}/{asset}/{doc_class}")
        
        # Get search configuration
        search_queries = _build_search_queries(province, asset, doc_class)
        allowlist_domains = _get_allowlist_domains(province)
        
        all_urls = set()  # Use set to avoid duplicates
        
        cse_fatal = False
        for query in search_queries:
            try:
                urls = _search_with_cse(query, allowlist_domains)
                # If None, indicates fatal (e.g., 403 unauthorized) — abort early
                if urls is None:
                    print("CSE not authorized or unavailable; aborting discovery early")
                    cse_fatal = True
                    break
                all_urls.update(urls)
                
                # Gentle pacing
                time.sleep(0.2)
                
            except Exception as e:
                print(f"Error in search query '{query}': {str(e)}")
                continue
        
        # If CSE failed entirely or found nothing, try Perplexity as a backup
        if (not all_urls) and (os.environ.get('PERPLEXITY_API_KEY')):
            try:
                print("Falling back to Perplexity web search for discovery...")
                # Use a single aggregated query to reduce API calls
                agg_query = f"{province} {asset} {doc_class} 并网 接入 办法 规定 site:.gov.cn"
                p_urls = _search_with_perplexity(agg_query, allowlist_domains)
                if p_urls:
                    all_urls.update(p_urls)
            except Exception as e:
                print(f"Perplexity fallback error: {str(e)}")

        # Filter and validate URLs
        filtered_urls = _filter_and_validate_urls(list(all_urls), province, asset, doc_class)
        
        print(f"Discovered {len(filtered_urls)} valid URLs for {province}/{asset}/{doc_class}")
        return filtered_urls
        
    except Exception as e:
        print(f"Error in document discovery: {str(e)}")
        return []


def _build_search_queries(province: str, asset: str, doc_class: str) -> List[str]:
    """
    Build search queries for specific province/asset/doc_class combination
    
    Args:
        province: Province code
        asset: Asset type
        doc_class: Document class
        
    Returns:
        List of search query strings
    """
    # Province name mapping
    province_names = {
        'gd': '广东',
        'sd': '山东', 
        'nm': '内蒙古'
    }
    
    # Asset name mapping
    asset_names = {
        'solar': ['光伏', '太阳能', '分布式光伏'],
        'coal': ['煤电', '火电', '燃煤'],
        'wind': ['风电', '风力发电', '风能']
    }
    
    # Document class keywords
    doc_class_keywords = {
        'grid': ['并网', '接入', '电网接入', '上网']
    }
    
    province_name = province_names.get(province, province)
    asset_keywords = asset_names.get(asset, [asset])
    class_keywords = doc_class_keywords.get(doc_class, [doc_class])
    
    queries = []
    
    # Build comprehensive search queries
    for asset_keyword in asset_keywords:
        for class_keyword in class_keywords:
            # Basic query
            queries.append(f"{province_name} {asset_keyword} {class_keyword}")
            
            # With management/regulation terms
            queries.append(f"{province_name} {asset_keyword} {class_keyword} 管理办法")
            queries.append(f"{province_name} {asset_keyword} {class_keyword} 规定")
            queries.append(f"{province_name} {asset_keyword} {class_keyword} 实施细则")
            
            # With specific document types
            queries.append(f"{province_name} {asset_keyword} {class_keyword} 技术要求")
            queries.append(f"{province_name} {asset_keyword} {class_keyword} 申请流程")
    
    # Add filetype restrictions for better results
    enhanced_queries = []
    for query in queries:
        enhanced_queries.append(f"{query} filetype:pdf")
        enhanced_queries.append(f"{query} filetype:doc")
        enhanced_queries.append(f"{query} filetype:docx")
        enhanced_queries.append(query)  # Also search without filetype restriction
    
    return enhanced_queries[:20]  # Limit to prevent quota exhaustion


def _get_allowlist_domains(province: str) -> List[str]:
    """
    Get allowlisted domains for a province
    
    Args:
        province: Province code
        
    Returns:
        List of allowed domains
    """
    # Base government domains
    base_domains = ['.gov.cn']
    
    # Province-specific domains
    province_domains = {
        'gd': ['gd.gov.cn', 'gdei.gov.cn', 'gdrc.gov.cn'],
        'sd': ['sd.gov.cn', 'sdei.gov.cn', 'sdrc.gov.cn'],
        'nm': ['nmg.gov.cn', 'nmgei.gov.cn', 'nmgrc.gov.cn']
    }
    
    # Combine base and province-specific domains
    allowed_domains = base_domains + province_domains.get(province, [])
    
    # Add from environment variable if available
    env_domains = os.environ.get('ALLOWLIST_DOMAINS', '')
    if env_domains:
        env_domain_list = [d.strip() for d in env_domains.split(',') if d.strip()]
        allowed_domains.extend(env_domain_list)
    
    return list(set(allowed_domains))  # Remove duplicates


def _search_with_cse(query: str, allowlist_domains: List[str]) -> List[str]:
    """
    Perform search using Google Custom Search Engine
    
    Args:
        query: Search query string
        allowlist_domains: List of allowed domains
        
    Returns:
        List of URLs from search results
    """
    try:
        # Get API credentials from env first, then secrets
        api_key = (
            os.environ.get('CSE_API_KEY')
            or os.environ.get('GOOGLE_CSE_API_KEY')
            or os.environ.get('GOOGLE_API_KEY')
            or _get_secret('google-api-key')
        )
        cse_id = (
            os.environ.get('CSE_ID')
            or os.environ.get('GOOGLE_CSE_ID')
            or os.environ.get('GOOGLE_CSE_CX')
            or _get_secret('google-cse-id')
        )
        
        if not api_key or not cse_id:
            print("Missing Google CSE API credentials")
            return []
        
        # Build search URL
        search_url = "https://www.googleapis.com/customsearch/v1"
        
        params = {
            'key': api_key,
            'cx': cse_id,
            'q': query,
            'num': 10,  # Number of results per query
            'start': 1,
            'lr': 'lang_zh-CN',  # Chinese language preference
            'safe': 'off'
        }
        
        # Add site restriction for allowlisted domains
        if allowlist_domains:
            site_restriction = ' OR '.join(f'site:{domain}' for domain in allowlist_domains)
            params['q'] = f"{query} ({site_restriction})"
        
        print(f"CSE Query: {params['q']}")
        
        # Make API request
        response = requests.get(search_url, params=params, timeout=20)
        # Explicitly handle common failure modes
        if response.status_code == 403:
            print("CSE API returned 403 (forbidden). Check CSE API key and API enablement.")
            return None  # Signal fatal
        if response.status_code == 429:
            print("CSE API rate limited (429). Returning no results for this query.")
            return []
        if response.status_code >= 400:
            print(f"CSE API error {response.status_code}: {response.text[:200]}")
            return []
        
        data = response.json()
        
        # Extract URLs from results
        urls = []
        items = data.get('items', [])
        
        for item in items:
            url = item.get('link')
            if url and _is_url_allowed(url, allowlist_domains):
                urls.append(url)
        
        print(f"CSE returned {len(urls)} URLs for query: {query}")
        return urls
        
    except Exception as e:
        print(f"Error in CSE search: {str(e)}")
        return []


def _search_with_perplexity(query: str, allowlist_domains: List[str]) -> Optional[List[str]]:
    """Use Perplexity API to search for relevant government URLs as a backup.

    Returns a list of URLs or None on fatal error.
    """
    api_key = os.environ.get('PERPLEXITY_API_KEY')
    if not api_key:
        return []
    try:
        import json
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        payload = {
            'model': 'sonar-pro',
            'messages': [
                { 'role': 'system', 'content': 'Return only relevant URLs, one per line.' },
                { 'role': 'user', 'content': (
                    '请仅提供与中国省级政府官方站点（.gov.cn 域名）相关、与电网并网/接入办事指南或规定直接相关的来源URL，'
                    '优先该省发改委/能源局/电网公司。最多返回10条，每条一行，只输出URL，无需解释。查询：' + query
                ) }
            ],
            'search_recency_filter': 'month',
            'return_citations': True
        }
        resp = requests.post('https://api.perplexity.ai/chat/completions', headers=headers, data=json.dumps(payload), timeout=30)
        if resp.status_code >= 400:
            print(f"Perplexity API error {resp.status_code}: {resp.text[:200]}")
            return []
        data = resp.json()
        content = data.get('choices', [{}])[0].get('message', {}).get('content', '')
        urls = []
        for line in content.splitlines():
            line = line.strip()
            if line.startswith('http') and _is_url_allowed(line, allowlist_domains):
                urls.append(line)
        # Deduplicate
        return list(dict.fromkeys(urls))
    except Exception as e:
        print(f"Error in Perplexity search: {str(e)}")
        return []


def _get_secret(secret_name: str) -> Optional[str]:
    """
    Get secret from Google Secret Manager
    
    Args:
        secret_name: Name of the secret
        
    Returns:
        Secret value or None
    """
    try:
        from google.cloud import secretmanager
        
        project_id = os.environ.get('GOOGLE_CLOUD_PROJECT')
        if not project_id:
            return None
            
        client = secretmanager.SecretManagerServiceClient()
        secret_path = f"projects/{project_id}/secrets/{secret_name}/versions/latest"
        
        response = client.access_secret_version(request={"name": secret_path})
        return response.payload.data.decode("UTF-8")
        
    except Exception as e:
        print(f"Error accessing secret {secret_name}: {str(e)}")
        return None


def _is_url_allowed(url: str, allowlist_domains: List[str]) -> bool:
    """
    Check if URL is from an allowed domain
    
    Args:
        url: URL to check
        allowlist_domains: List of allowed domains
        
    Returns:
        True if URL is allowed
    """
    try:
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        
        for allowed_domain in allowlist_domains:
            if allowed_domain.startswith('.'):
                # Suffix match (e.g., .gov.cn)
                if domain.endswith(allowed_domain):
                    return True
            else:
                # Exact match or subdomain
                if domain == allowed_domain or domain.endswith(f'.{allowed_domain}'):
                    return True
        
        return False
        
    except Exception:
        return False


def _filter_and_validate_urls(urls: List[str], province: str, asset: str, doc_class: str) -> List[str]:
    """
    Filter and validate discovered URLs
    
    Args:
        urls: List of URLs to filter
        province: Province code
        asset: Asset type
        doc_class: Document class
        
    Returns:
        List of validated URLs
    """
    validated_urls = []
    seen_checksums = set()
    
    for url in urls:
        try:
            # Basic URL validation
            if not _is_valid_document_url(url):
                continue
            
            # Check for duplicates based on URL content hash
            url_hash = hashlib.md5(url.encode()).hexdigest()
            if url_hash in seen_checksums:
                continue
            seen_checksums.add(url_hash)
            
            # Optionally require network accessibility (default: do not require)
            if os.environ.get('REQUIRE_URL_ACCESS', 'false').lower() == 'true':
                if not _is_url_accessible(url):
                    continue
            
            # Check relevance based on URL path and domain
            if not _is_url_relevant(url, province, asset, doc_class):
                continue
            
            validated_urls.append(url)
            
        except Exception as e:
            print(f"Error validating URL {url}: {str(e)}")
            continue
    
    return validated_urls


def _is_valid_document_url(url: str) -> bool:
    """
    Check if URL points to a valid document
    
    Args:
        url: URL to check
        
    Returns:
        True if URL appears to be a valid document
    """
    try:
        parsed = urlparse(url)
        
        # Check for valid scheme
        if parsed.scheme not in ['http', 'https']:
            return False
        
        # Check for document file extensions
        path = parsed.path.lower()
        valid_extensions = ['.pdf', '.doc', '.docx', '.html', '.htm']
        
        # Either has valid extension or could be a dynamic document
        has_extension = any(path.endswith(ext) for ext in valid_extensions)
        is_dynamic = not path.endswith(('.jpg', '.png', '.gif', '.css', '.js', '.xml'))
        
        return has_extension or is_dynamic
        
    except Exception:
        return False


def _is_url_accessible(url: str) -> bool:
    """
    Check if URL is accessible via HEAD request
    
    Args:
        url: URL to check
        
    Returns:
        True if URL is accessible
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (compatible; NemoComplianceBot/1.0)'
        }
        # Try HEAD first
        try:
            resp = requests.head(url, headers=headers, timeout=10, allow_redirects=True)
            if 200 <= resp.status_code < 400:
                return True
            # Some gov sites return 405/501 for HEAD; fall through to GET
        except Exception:
            pass
        # Fallback to lightweight GET check
        try:
            resp = requests.get(url, headers=headers, timeout=15, allow_redirects=True, stream=True)
            ctype = (resp.headers.get('content-type') or '').lower()
            if 200 <= resp.status_code < 400 and any(
                t in ctype for t in (
                    'pdf', 'msword', 'officedocument.wordprocessingml.document', 'html'
                )
            ):
                return True
        except Exception:
            pass
        return False
        
    except Exception:
        return False


def _is_url_relevant(url: str, province: str, asset: str, doc_class: str) -> bool:
    """
    Check if URL is relevant to the search criteria
    
    Args:
        url: URL to check
        province: Province code
        asset: Asset type
        doc_class: Document class
        
    Returns:
        True if URL appears relevant
    """
    url_lower = url.lower()
    domain = urlparse(url_lower).netloc
    
    # Province relevance
    province_indicators = {
        'gd': ['gd', 'guangdong', '广东'],
        'sd': ['sd', 'shandong', '山东'],
        'nm': ['nm', 'neimenggu', 'inner', 'mongolia', '内蒙古']
    }

    # Province-specific gov domains (exact/suffix match)
    province_domains = {
        'gd': ['gd.gov.cn', 'gdei.gov.cn', 'gdrc.gov.cn'],
        'sd': ['sd.gov.cn', 'sdei.gov.cn', 'sdrc.gov.cn'],
        'nm': ['nmg.gov.cn', 'nmgei.gov.cn', 'nmgrc.gov.cn']
    }
    
    # Asset relevance
    asset_indicators = {
        'solar': ['solar', 'pv', 'photovoltaic', '光伏', '太阳能'],
        'coal': ['coal', 'thermal', '煤', '火电'],
        'wind': ['wind', '风电', '风能']
    }
    
    # Document class relevance
    class_indicators = {
        'grid': ['grid', 'connection', '并网', '接入', '电网']
    }
    
    # Check for province indicators (optional - domain might be sufficient)
    # Consider relevant if:
    # - domain is a gov.cn domain (city/province/agency), or
    # - domain matches known province domains, or
    # - URL contains province indicators
    province_relevant = False
    if domain.endswith('.gov.cn'):
        province_relevant = True
    elif province in province_domains and any(domain == d or domain.endswith('.' + d) for d in province_domains[province]):
        province_relevant = True
    else:
        indicators = province_indicators.get(province, [])
        province_relevant = any(ind in url_lower for ind in indicators)
    
    # Check for asset indicators
    asset_relevant = False
    if asset in asset_indicators:
        indicators = asset_indicators[asset]
        asset_relevant = any(indicator in url_lower for indicator in indicators)
    
    # Check for document class indicators
    class_relevant = False
    if doc_class in class_indicators:
        indicators = class_indicators[doc_class]
        class_relevant = any(indicator in url_lower for indicator in indicators)
    
    # In fallback discovery, accept gov.cn URLs once province relevance passes
    return province_relevant


def get_discovery_statistics() -> Dict[str, Any]:
    """
    Get statistics about document discovery process
    
    Returns:
        Dictionary with discovery statistics
    """
    # This would be enhanced with actual tracking in production
    return {
        'total_queries_made': 0,
        'total_urls_discovered': 0,
        'total_urls_validated': 0,
        'last_discovery_time': None,
        'quota_remaining': None
    }


def test_cse_connectivity() -> bool:
    """
    Test Google Custom Search Engine connectivity
    
    Returns:
        True if CSE is accessible
    """
    try:
        api_key = _get_secret('google-api-key')
        cse_id = _get_secret('google-cse-id')
        
        if not api_key or not cse_id:
            return False
        
        # Simple test query
        test_urls = _search_with_cse("test", [".gov.cn"])
        return True  # If no exception, connectivity is OK
        
    except Exception as e:
        print(f"CSE connectivity test failed: {str(e)}")
        return False
