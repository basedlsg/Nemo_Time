"""
Test CSE integration with real API credentials
"""

import os
from lib.cse import discover_documents, _search_with_cse, _get_allowlist_domains

# Set environment variables
os.environ['GOOGLE_API_KEY'] = 'AIzaSyAqko3NqGS-GtXhzm8LeiZ3xUEyo_XIqLo'
os.environ['GOOGLE_CSE_ID'] = 'c2902a74ad3664d41'

def test_cse_direct():
    """Test CSE search directly"""
    print("Testing CSE integration...")
    
    # Test parameters
    province = "gd"
    asset = "solar"
    doc_class = "grid"
    
    # Get allowlist domains
    allowlist_domains = _get_allowlist_domains(province)
    print(f"Allowlist domains: {allowlist_domains}")
    
    # Test a simple search
    query = "广东 光伏 并网"
    if allowlist_domains:
        site_restriction = ' OR '.join(f'site:{domain}' for domain in allowlist_domains)
        full_query = f"{query} ({site_restriction})"
    else:
        full_query = query
    
    print(f"Testing query: {full_query}")
    
    # Get raw URLs from CSE
    urls = _search_with_cse(full_query, allowlist_domains)
    print(f"Raw URLs returned: {len(urls)}")
    
    for i, url in enumerate(urls[:5], 1):
        print(f"  {i}. {url}")
    
    # Test full discovery process
    print("\nTesting full discovery process...")
    filtered_urls = discover_documents(province, asset, doc_class)
    print(f"Filtered URLs: {len(filtered_urls)}")
    
    for i, url in enumerate(filtered_urls[:5], 1):
        print(f"  {i}. {url}")

if __name__ == "__main__":
    test_cse_direct()