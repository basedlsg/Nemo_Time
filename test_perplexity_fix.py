#!/usr/bin/env python3
"""
Test script to validate the Perplexity API fix.
Tests the original failing query that had 89% irrelevant results.
"""

import os
import sys
import json
from urllib.parse import urlparse

# Add functions directory to path
sys.path.insert(0, '/home/user/Nemo_Time/functions/query')
from perplexity import answer_with_perplexity, _build_domain_filter, _is_allowed, ALLOWLIST_DOMAINS_DEFAULT


def test_domain_filter_generation():
    """Test that domain filter is properly generated"""
    print("=" * 80)
    print("TEST 1: Domain Filter Generation")
    print("=" * 80)

    # Test Guangdong solar project
    domain_filter = _build_domain_filter("gd", "grid_connection")
    print(f"\nDomain filter for 'gd' + 'grid_connection':")
    print(f"  Domains: {domain_filter}")
    print(f"  Count: {len(domain_filter)}")
    print(f"  Within API limit (≤20): {'✅' if len(domain_filter) <= 20 else '❌'}")

    # Verify key domains are included
    required = ["gov.cn", "gd.gov.cn", "ndrc.gov.cn", "nea.gov.cn"]
    missing = [d for d in required if d not in domain_filter]
    if missing:
        print(f"  ❌ Missing required domains: {missing}")
        return False
    else:
        print(f"  ✅ All required domains present")

    # Test no leading dots (API compatibility)
    has_dots = [d for d in domain_filter if d.startswith('.')]
    if has_dots:
        print(f"  ❌ Domains with leading dots (API incompatible): {has_dots}")
        return False
    else:
        print(f"  ✅ No leading dots (API compatible)")

    return True


def test_url_validation():
    """Test that .gov.cn URLs are properly validated"""
    print("\n" + "=" * 80)
    print("TEST 2: URL Domain Validation")
    print("=" * 80)

    allowlist = list(ALLOWLIST_DOMAINS_DEFAULT) + ["gd.gov.cn", "drc.gd.gov.cn"]

    test_cases = [
        ("https://drc.gd.gov.cn/files/solar_grid.pdf", True, "Guangdong DRC"),
        ("https://nea.gov.cn/policy/solar_2024.pdf", True, "National Energy Admin"),
        ("https://www.gov.cn/documents/policy.pdf", True, "National gov.cn"),
        ("https://baidu.com/article.html", False, "Commercial site"),
        ("https://csdn.net/blog/solar", False, "Tech blog"),
    ]

    all_passed = True
    for url, expected, label in test_cases:
        result = _is_allowed(url, allowlist)
        status = "✅" if result == expected else "❌"
        print(f"  {status} {label}: {url}")
        print(f"      Expected: {expected}, Got: {result}")
        if result != expected:
            all_passed = False

    return all_passed


def test_api_integration():
    """Test the actual Perplexity API integration with the fix"""
    print("\n" + "=" * 80)
    print("TEST 3: Perplexity API Integration (Original Failing Query)")
    print("=" * 80)

    # Check if API key is available
    api_key = os.environ.get("PERPLEXITY_API_KEY")
    if not api_key:
        print("  ⚠️  PERPLEXITY_API_KEY not set - skipping API test")
        print("  Set environment variable to test: export PERPLEXITY_API_KEY=your_key")
        return None

    # Original failing query from the analysis
    question = "光伏发电项目土地勘测需要什么材料和流程"
    province = "gd"
    asset = "solar"
    doc_class = "grid"

    print(f"\nQuery: {question}")
    print(f"Province: {province}")
    print(f"Asset: {asset}")
    print(f"Doc Class: {doc_class}")
    print("\nCalling Perplexity API...")

    try:
        result = answer_with_perplexity(
            question=question,
            province=province,
            asset=asset,
            doc_class=doc_class
        )

        if not result:
            print("  ❌ API returned None (no results)")
            return False

        print("\n  ✅ API call successful")
        print(f"\nAnswer preview (first 200 chars):")
        print(f"  {result.get('answer_zh', '')[:200]}...")

        citations = result.get('citations', [])
        print(f"\nCitations: {len(citations)} found")

        if not citations:
            print("  ❌ No citations returned")
            return False

        gov_cn_count = 0
        for i, citation in enumerate(citations[:6], 1):
            url = citation.get('url', '')
            domain = urlparse(url).netloc
            is_gov = '.gov.cn' in domain or domain.endswith('gov.cn')
            status = "✅" if is_gov else "❌"
            print(f"  {status} Citation {i}: {domain}")
            print(f"      URL: {url}")
            if is_gov:
                gov_cn_count += 1

        gov_cn_percentage = (gov_cn_count / len(citations[:6])) * 100
        print(f"\nResults:")
        print(f"  .gov.cn domains: {gov_cn_count}/{len(citations[:6])} ({gov_cn_percentage:.1f}%)")
        print(f"  Target: 100% .gov.cn")

        if gov_cn_percentage >= 80:
            print(f"  ✅ SUCCESS: {gov_cn_percentage:.1f}% .gov.cn (target: ≥80%)")
            return True
        else:
            print(f"  ❌ FAILED: {gov_cn_percentage:.1f}% .gov.cn (target: ≥80%)")
            return False

    except Exception as e:
        print(f"  ❌ API call failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    print("\n" + "=" * 80)
    print("PERPLEXITY API FIX VALIDATION")
    print("=" * 80)
    print("\nThis script tests the fix for the Perplexity API domain filtering issue.")
    print("Original problem: site:.gov.cn in query text (ignored by API)")
    print("Fix: Use search_domain_filter parameter (actually works)")
    print("\n")

    results = {}

    # Run tests
    results['domain_filter'] = test_domain_filter_generation()
    results['url_validation'] = test_url_validation()
    results['api_integration'] = test_api_integration()

    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)

    for test_name, result in results.items():
        if result is None:
            status = "⚠️  SKIPPED"
        elif result:
            status = "✅ PASSED"
        else:
            status = "❌ FAILED"
        print(f"  {status} {test_name.replace('_', ' ').title()}")

    # Overall result
    failures = [k for k, v in results.items() if v is False]
    skipped = [k for k, v in results.items() if v is None]

    print("\n" + "=" * 80)
    if failures:
        print(f"❌ {len(failures)} test(s) failed: {', '.join(failures)}")
        sys.exit(1)
    elif all(v is None for v in results.values()):
        print("⚠️  All tests skipped (API key not available)")
        print("\nTo run the full test suite, set PERPLEXITY_API_KEY:")
        print("  export PERPLEXITY_API_KEY=your_key_here")
        print("  python test_perplexity_fix.py")
        sys.exit(0)
    else:
        passed_count = sum(1 for v in results.values() if v is True)
        print(f"✅ All {passed_count} test(s) passed!")
        if skipped:
            print(f"⚠️  {len(skipped)} test(s) skipped: {', '.join(skipped)}")
        sys.exit(0)


if __name__ == "__main__":
    main()
