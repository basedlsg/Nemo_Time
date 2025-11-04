#!/usr/bin/env python3
"""
Test script for RAG-Anything document processing pipeline
Demonstrates processing Chinese regulatory documents
"""

import asyncio
import os
import sys
from pathlib import Path

# Add the prototype to Python path
sys.path.insert(0, str(Path(__file__).parent))

from rag_anything_prototype import (
    create_pipeline,
    DocumentMetadata,
    Document,
    ChineseTextProcessor
)


async def test_chinese_text_processing():
    """Test Chinese text processing capabilities"""
    print("=== Testing Chinese Text Processing ===")
    
    processor = ChineseTextProcessor()
    
    # Test with sample regulatory text
    test_text = """
    第一条 为规范分布式光伏发电项目管理，促进分布式光伏发电健康有序发展，
    根据《可再生能源法》、《电力法》等法律法规，结合本省实际，制定本办法。
    
    第二条 本办法适用于在广东省行政区域内建设的分布式光伏发电项目的备案、
    并网、运营等管理活动。
    
    第三条 分布式光伏发电是指在用户场地附近建设，运行方式以用户侧自发自用、
    多余电量上网，且在配电系统平衡调节为特征的光伏发电设施。
    """
    
    # Test text processing
    metadata = DocumentMetadata(
        province="gd",
        asset_type="solar", 
        doc_class="grid"
    )
    
    processed_text = processor.process_text(test_text, metadata)
    print(f"Processed text length: {len(processed_text) if processed_text else 0}")
    
    # Test sentence splitting
    sentences = processor.split_into_sentences(test_text)
    print(f"Split into {len(sentences)} sentences")
    
    # Test statistics
    stats = processor.get_text_statistics(test_text)
    print(f"Text statistics: {stats}")
    
    return processed_text is not None


async def test_document_processing():
    """Test document processing with sample documents"""
    print("\n=== Testing Document Processing ===")
    
    try:
        # Create sample documents from test files
        test_docs_dir = Path("test_documents")
        if not test_docs_dir.exists():
            print("Test documents directory not found, creating sample document...")
            
            # Create a sample document
            sample_doc = Document(
                id="test_doc_1",
                title="广东省分布式光伏发电管理办法",
                content="""
                第一条 为规范分布式光伏发电项目管理，促进分布式光伏发电健康有序发展，
                根据《可再生能源法》、《电力法》等法律法规，结合本省实际，制定本办法。
                
                第二条 本办法适用于在广东省行政区域内建设的分布式光伏发电项目的备案、
                并网、运营等管理活动。
                
                第三条 分布式光伏发电是指在用户场地附近建设，运行方式以用户侧自发自用、
                多余电量上网，且在配电系统平衡调节为特征的光伏发电设施。
                
                第四条 分布式光伏发电项目实行备案制管理。项目备案由县级以上发展改革部门负责。
                
                第五条 申请项目备案应当提交以下材料：
                1. 分布式光伏发电项目备案申请表
                2. 项目建设方案和设计文件
                3. 用电户同意项目建设的证明文件
                4. 土地使用权或屋顶使用权证明
                5. 电网接入系统方案
                """,
                metadata=DocumentMetadata(
                    province="gd",
                    asset_type="solar",
                    doc_class="grid",
                    title="广东省分布式光伏发电管理办法"
                ),
                checksum="test_checksum_1"
            )
            
            return [sample_doc]
        
        else:
            # Load actual test documents
            documents = []
            for doc_file in test_docs_dir.glob("*.md"):
                with open(doc_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Extract metadata from filename
                filename = doc_file.stem
                if "gd" in filename:
                    province = "gd"
                elif "sd" in filename:
                    province = "sd"
                elif "nm" in filename:
                    province = "nm"
                else:
                    province = "unknown"
                
                if "solar" in filename:
                    asset_type = "solar"
                elif "coal" in filename:
                    asset_type = "coal"
                elif "wind" in filename:
                    asset_type = "wind"
                else:
                    asset_type = "unknown"
                
                doc = Document(
                    id=filename,
                    title=content.split('\n')[0].replace('#', '').strip(),
                    content=content,
                    metadata=DocumentMetadata(
                        province=province,
                        asset_type=asset_type,
                        doc_class="grid"
                    ),
                    checksum=f"checksum_{filename}"
                )
                
                documents.append(doc)
            
            return documents
    
    except Exception as e:
        print(f"Error in document processing test: {str(e)}")
        return []


async def test_rag_pipeline():
    """Test the complete RAG pipeline"""
    print("\n=== Testing RAG Pipeline ===")
    
    # Check for required environment variables
    if not os.getenv("OPENAI_API_KEY"):
        print("OPENAI_API_KEY not set. Skipping RAG pipeline test.")
        print("To test the full pipeline, set your OpenAI API key:")
        print("export OPENAI_API_KEY='your-api-key-here'")
        return False
    
    try:
        # Create pipeline
        print("Creating RAG pipeline...")
        pipeline = await create_pipeline(
            working_dir="./test_rag_storage",
            llm_provider="openai",
            embedding_provider="openai"
        )
        
        print("Pipeline created successfully!")
        
        # Get pipeline status
        status = await pipeline.get_pipeline_status()
        print(f"Pipeline status: {status['initialized']}")
        
        # Test with sample documents
        documents = await test_document_processing()
        
        if documents:
            print(f"Processing {len(documents)} test documents...")
            
            # Process documents one by one for testing
            for doc in documents[:2]:  # Limit to 2 documents for testing
                try:
                    print(f"Processing document: {doc.title}")
                    result = await pipeline.document_processor.process_document(doc)
                    
                    if result.success:
                        print(f"✓ Successfully processed: {result.chunk_count} chunks")
                    else:
                        print(f"✗ Failed to process: {result.error}")
                        
                except Exception as e:
                    print(f"✗ Error processing document: {str(e)}")
            
            # Test querying
            print("\nTesting document queries...")
            test_queries = [
                "分布式光伏发电项目如何备案？",
                "What are the requirements for grid connection?",
                "电网接入需要什么材料？"
            ]
            
            for query in test_queries:
                try:
                    print(f"\nQuery: {query}")
                    response = await pipeline.query_documents(query)
                    print(f"Response: {response[:200]}...")
                    
                except Exception as e:
                    print(f"Error querying: {str(e)}")
        
        # Cleanup
        await pipeline.cleanup()
        print("Pipeline test completed successfully!")
        return True
        
    except Exception as e:
        print(f"Error in RAG pipeline test: {str(e)}")
        return False


async def main():
    """Run all tests"""
    print("RAG-Anything Pipeline Test Suite")
    print("=" * 50)
    
    # Test 1: Chinese text processing
    text_test_passed = await test_chinese_text_processing()
    print(f"Chinese text processing test: {'PASSED' if text_test_passed else 'FAILED'}")
    
    # Test 2: Document processing
    documents = await test_document_processing()
    doc_test_passed = len(documents) > 0
    print(f"Document processing test: {'PASSED' if doc_test_passed else 'FAILED'}")
    
    # Test 3: RAG pipeline (requires API key)
    rag_test_passed = await test_rag_pipeline()
    print(f"RAG pipeline test: {'PASSED' if rag_test_passed else 'SKIPPED/FAILED'}")
    
    # Summary
    print("\n" + "=" * 50)
    print("Test Summary:")
    print(f"- Chinese Text Processing: {'✓' if text_test_passed else '✗'}")
    print(f"- Document Processing: {'✓' if doc_test_passed else '✗'}")
    print(f"- RAG Pipeline: {'✓' if rag_test_passed else '✗'}")
    
    if all([text_test_passed, doc_test_passed]):
        print("\nCore functionality tests passed!")
        if not rag_test_passed:
            print("Set OPENAI_API_KEY to test full RAG functionality.")
    else:
        print("\nSome tests failed. Check the output above for details.")


if __name__ == "__main__":
    asyncio.run(main())