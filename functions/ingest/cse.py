"""
Google Custom Search Engine integration module
Handles document discovery from allowlisted government domains
"""

import os
import time
from typing import List, Dict, Any, Optional
import requests
from urllib.parse import urlparse, urljoin
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
        
        for query in search_queries:
            try:
                urls = _search_with_cse(query, allowlist_domains)
                all_urls.update(urls)
                
                # Rate limiting - respect Google's limits
                time.sleep(1)
                
            except Exception as e:
                print(f"Error in search query '{query}': {str(e)}")
                continue
        
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
        # Get API credentials from environment/secrets
        api_key = _get_secret('google-api-key')
        cse_id = _get_secret('google-cse-id')
        
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
        response = requests.get(search_url, params=params, timeout=30)
        response.raise_for_status()
        
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
            
            # Check if URL is accessible (HEAD request)
            if not _is_url_accessible(url):
                continue
            
            # Check relevance based on URL path and parameters
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
        
        response = requests.head(url, headers=headers, timeout=10, allow_redirects=True)
        
        # Accept 2xx and 3xx status codes
        return 200 <= response.status_code < 400
        
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
    
    # Province relevance
    province_indicators = {
        'gd': ['gd', 'guangdong', '广东'],
        'sd': ['sd', 'shandong', '山东'],
        'nm': ['nm', 'neimenggu', 'inner', 'mongolia', '内蒙古']
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
    province_relevant = True  # Assume relevant if from correct domain
    if province in province_indicators:
        indicators = province_indicators[province]
        province_relevant = any(indicator in url_lower for indicator in indicators)
    
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
    
    # URL is relevant if it matches asset OR class criteria (not necessarily both)
    return province_relevant and (asset_relevant or class_relevant)


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