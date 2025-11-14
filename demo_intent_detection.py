#!/usr/bin/env python3
"""
Interactive demo of enhanced query construction with intent detection
Run this to test the new functionality
"""

from lib.intent_detection import build_enhanced_query

def demo():
    print("=" * 70)
    print("Enhanced Query Construction Demo")
    print("=" * 70)
    print()
    
    test_cases = [
        {
            "query": "什么是光伏发电?",
            "province": "gd",
            "asset": "solar",
            "description": "Definition query"
        },
        {
            "query": "光伏项目需要什么材料?",
            "province": "sd",
            "asset": "solar",
            "description": "Materials query"
        },
        {
            "query": "风电项目审批需要多长时间?",
            "province": "gd",
            "asset": "wind",
            "description": "Timeline query"
        },
        {
            "query": "如何申请煤电项目许可证?",
            "province": "nm",
            "asset": "coal",
            "description": "Procedure + Approval query"
        },
        {
            "query": "光伏项目审批需要什么材料和多长时间?",
            "province": "gd",
            "asset": "solar",
            "description": "Multiple intents (materials + timeline + approval)"
        },
        {
            "query": "能源项目管理",
            "province": "gd",
            "asset": "solar",
            "description": "Generic query (fallback)"
        }
    ]
    
    for i, test in enumerate(test_cases, 1):
        print(f"Test {i}: {test['description']}")
        print("-" * 70)
        print(f"Original Query: {test['query']}")
        print(f"Province: {test['province']}, Asset: {test['asset']}")
        
        result = build_enhanced_query(test['query'], test['province'], test['asset'])
        
        print(f"\nEnhanced Query:")
        print(f"  {result['enhanced_query']}")
        print(f"\nMetadata:")
        print(f"  Intents Detected: {result['intents_detected']}")
        print(f"  Enhancement Type: {result['enhancement_type']}")
        print(f"  Province Name: {result['province_name']}")
        print(f"  Asset Name: {result['asset_name']}")
        
        if result['doc_keywords_used']:
            print(f"  Document Keywords: {result['doc_keywords_used']}")
        
        print()
        print("=" * 70)
        print()

if __name__ == "__main__":
    demo()
