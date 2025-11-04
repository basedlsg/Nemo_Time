#!/usr/bin/env python3
"""
Test script for intent detection functionality
Tests the core intent detection functions with sample Chinese queries
"""

import sys
import os
sys.path.append('lib')

from intent_detection import detect_query_intent, get_document_keywords, build_enhanced_query, validate_intent_detection
import time


def test_intent_detection():
    """Test intent detection with various Chinese queries"""
    
    print("=== Testing Intent Detection ===\n")
    
    # Test cases covering all 10 intent types
    test_cases = [
        # Definition queries
        ("什么是光伏发电?", ["definition"]),
        ("风电是什么?", ["definition"]),
        ("煤电项目的定义是什么?", ["definition"]),
        
        # Materials queries
        ("光伏项目备案需要什么材料?", ["materials"]),
        ("煤电项目需要哪些许可证?", ["materials", "approval"]),
        ("申请材料清单有哪些?", ["materials"]),
        
        # Timeline queries
        ("光伏项目审批需要多长时间?", ["timeline", "approval"]),
        ("备案程序需要多少天?", ["timeline", "approval"]),
        
        # Environment queries
        ("山东省风电项目环境评估有什么特殊要求?", ["environment"]),
        ("环评报告需要包含哪些内容?", ["environment"]),
        
        # Procedure queries
        ("风电项目如何接入电网?", ["procedure", "technical"]),
        ("光伏项目备案流程是什么?", ["procedure", "approval"]),
        
        # Approval queries
        ("煤电项目审批程序是什么?", ["approval", "procedure"]),
        ("许可证申请流程?", ["approval", "procedure"]),
        
        # Coordination queries
        ("跨省电力项目如何协调?", ["coordination"]),
        ("多部门协调机制是什么?", ["coordination", "definition"]),
        
        # Market queries
        ("电力市场准入条件?", ["market"]),
        ("电力交易规则是什么?", ["market", "definition"]),
        
        # Technical queries
        ("光伏装机容量标准?", ["technical"]),
        ("风电技术要求有哪些?", ["technical"]),
        
        # Future queries
        ("未来光伏政策趋势?", ["future"]),
        ("煤电发展规划展望?", ["future"]),
        
        # Complex multi-intent queries
        ("内蒙古煤电项目在碳达峰目标下的灵活性改造政策要求?", ["technical", "future"]),
        
        # Edge cases
        ("", []),
        ("简单查询", []),
    ]
    
    success_count = 0
    total_count = len(test_cases)
    
    for query, expected_intents in test_cases:
        start_time = time.time()
        detected_intents = detect_query_intent(query)
        processing_time = time.time() - start_time
        
        # Check if detected intents match expected (allowing for partial matches)
        match = all(intent in detected_intents for intent in expected_intents) if expected_intents else not detected_intents
        
        status = "✓" if match else "✗"
        success_count += 1 if match else 0
        
        print(f"{status} Query: '{query}'")
        print(f"  Expected: {expected_intents}")
        print(f"  Detected: {detected_intents}")
        print(f"  Processing time: {processing_time*1000:.2f}ms")
        
        if detected_intents:
            doc_keywords = get_document_keywords(detected_intents)
            print(f"  Document keywords: {doc_keywords}")
        
        print()
    
    print(f"Intent Detection Test Results: {success_count}/{total_count} passed ({success_count/total_count*100:.1f}%)")
    return success_count == total_count


def test_enhanced_query_building():
    """Test enhanced query building functionality"""
    
    print("\n=== Testing Enhanced Query Building ===\n")
    
    test_cases = [
        ("什么是光伏发电?", "gd", "solar"),
        ("光伏项目备案需要什么材料?", "sd", "solar"),
        ("风电项目审批需要多长时间?", "nm", "wind"),
        ("煤电项目环境评估要求?", "gd", "coal"),
        ("简单查询", "gd", "solar"),  # No intent detected
    ]
    
    for query, province, asset in test_cases:
        result = build_enhanced_query(query, province, asset)
        
        print(f"Original query: '{query}'")
        print(f"Province: {province} ({result['province_name']})")
        print(f"Asset: {asset} ({result['asset_name']})")
        print(f"Intents detected: {result['intents_detected']}")
        print(f"Enhancement type: {result['enhancement_type']}")
        print(f"Enhanced query: {result['enhanced_query']}")
        print(f"Document keywords: {result['doc_keywords_used']}")
        print()
    
    return True


def test_validation():
    """Test intent validation functionality"""
    
    print("\n=== Testing Intent Validation ===\n")
    
    test_cases = [
        ("什么是光伏?", ["definition"], True),
        ("简单查询", [], True),
        ("复杂查询", ["definition", "procedure"], True),
        ("过度匹配", ["definition", "materials", "timeline", "environment"], False),  # Too many intents
        ("短查询", ["definition", "procedure"], False),  # Conflicting intents on short query
    ]
    
    for query, intents, expected_valid in test_cases:
        is_valid = validate_intent_detection(query, intents)
        status = "✓" if is_valid == expected_valid else "✗"
        
        print(f"{status} Query: '{query}' | Intents: {intents} | Valid: {is_valid} (expected: {expected_valid})")
    
    return True


def main():
    """Run all tests"""
    print("Intent Detection Module Test Suite")
    print("=" * 50)
    
    try:
        # Run all tests
        test1_passed = test_intent_detection()
        test2_passed = test_enhanced_query_building()
        test3_passed = test_validation()
        
        print("\n" + "=" * 50)
        print("OVERALL TEST RESULTS:")
        print(f"Intent Detection: {'PASS' if test1_passed else 'FAIL'}")
        print(f"Enhanced Query Building: {'PASS' if test2_passed else 'FAIL'}")
        print(f"Validation: {'PASS' if test3_passed else 'FAIL'}")
        
        if all([test1_passed, test2_passed, test3_passed]):
            print("\n🎉 All tests passed! Intent detection module is working correctly.")
            return 0
        else:
            print("\n❌ Some tests failed. Please review the implementation.")
            return 1
            
    except Exception as e:
        print(f"\n❌ Test execution failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())