#!/usr/bin/env python3
"""
Test script to verify RAG-Anything framework setup and basic functionality.
This script tests the installation and basic imports without requiring API keys.
"""

import sys
import os

def test_imports():
    """Test basic imports from RAG-Anything framework."""
    print("Testing RAG-Anything imports...")
    
    try:
        # Test basic RAG-Anything imports
        from raganything import RAGAnything, RAGAnythingConfig
        print("✅ Successfully imported RAGAnything and RAGAnythingConfig")
        
        # Test LightRAG imports
        from lightrag import LightRAG
        print("✅ Successfully imported LightRAG")
        
        # Test modal processors
        from raganything.modalprocessors import ImageModalProcessor, TableModalProcessor
        print("✅ Successfully imported modal processors")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_basic_functionality():
    """Test basic functionality without requiring API keys."""
    print("\nTesting basic functionality...")
    
    try:
        from raganything import RAGAnythingConfig
        
        # Test configuration creation
        config = RAGAnythingConfig(
            working_dir="./test_rag_storage",
            parser="mineru",
            parse_method="auto",
            enable_image_processing=True,
            enable_table_processing=True,
            enable_equation_processing=True,
        )
        print("✅ Successfully created RAGAnythingConfig")
        
        # Test configuration attributes
        assert config.working_dir == "./test_rag_storage"
        assert config.parser == "mineru"
        assert config.parse_method == "auto"
        assert config.enable_image_processing == True
        print("✅ Configuration attributes are correct")
        
        return True
        
    except Exception as e:
        print(f"❌ Basic functionality test failed: {e}")
        return False

def test_framework_architecture():
    """Test framework architecture understanding."""
    print("\nAnalyzing RAG-Anything framework architecture...")
    
    try:
        # Check available modules
        import raganything
        
        # List available attributes
        available_attrs = [attr for attr in dir(raganything) if not attr.startswith('_')]
        print(f"✅ Available RAG-Anything modules: {available_attrs}")
        
        # Check if we can access the main components
        from raganything import RAGAnything
        from raganything.modalprocessors import GenericModalProcessor
        
        print("✅ Framework architecture analysis complete")
        return True
        
    except Exception as e:
        print(f"❌ Architecture analysis failed: {e}")
        return False

def analyze_chinese_language_support():
    """Analyze Chinese language processing capabilities."""
    print("\nAnalyzing Chinese language processing capabilities...")
    
    try:
        # Test if Chinese text processing libraries are available
        import pypinyin
        print("✅ pypinyin available for Chinese text processing")
        
        # Test basic Chinese text handling
        test_chinese = "中国能源监管文件"
        pinyin_result = pypinyin.lazy_pinyin(test_chinese)
        print(f"✅ Chinese text processing test: '{test_chinese}' -> {pinyin_result}")
        
        return True
        
    except ImportError as e:
        print(f"⚠️  Chinese processing library not available: {e}")
        return False
    except Exception as e:
        print(f"❌ Chinese language analysis failed: {e}")
        return False

def check_mineru_availability():
    """Check if MinerU is available for document processing."""
    print("\nChecking MinerU availability...")
    
    try:
        # Try to import mineru components
        import subprocess
        result = subprocess.run(['mineru', '--version'], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print(f"✅ MinerU is available: {result.stdout.strip()}")
            return True
        else:
            print(f"⚠️  MinerU command failed: {result.stderr}")
            return False
            
    except FileNotFoundError:
        print("⚠️  MinerU command not found - may need separate installation")
        return False
    except subprocess.TimeoutExpired:
        print("⚠️  MinerU command timed out")
        return False
    except Exception as e:
        print(f"⚠️  MinerU check failed: {e}")
        return False

def main():
    """Main test function."""
    print("=" * 60)
    print("RAG-Anything Framework Setup Test")
    print("=" * 60)
    
    tests = [
        ("Import Tests", test_imports),
        ("Basic Functionality", test_basic_functionality),
        ("Framework Architecture", test_framework_architecture),
        ("Chinese Language Support", analyze_chinese_language_support),
        ("MinerU Availability", check_mineru_availability),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'-' * 40}")
        print(f"Running: {test_name}")
        print(f"{'-' * 40}")
        
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"❌ Test '{test_name}' failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print(f"\n{'=' * 60}")
    print("TEST SUMMARY")
    print(f"{'=' * 60}")
    
    passed = 0
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{test_name:<30} {status}")
        if success:
            passed += 1
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! RAG-Anything setup is successful.")
        return 0
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
        return 1

if __name__ == "__main__":
    sys.exit(main())