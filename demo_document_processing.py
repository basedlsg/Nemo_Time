#!/usr/bin/env python3
"""
Demo script for RAG-Anything document processing
Shows Chinese regulatory document processing capabilities
"""

import sys
from pathlib import Path

# Add prototype to path
sys.path.insert(0, './rag_anything_prototype')

from chinese_text_processor import ChineseTextProcessor
from document_models import DocumentMetadata, Document
from gcs_document_loader import GCSDocumentLoader


def demo_chinese_text_processing():
    """Demonstrate Chinese text processing capabilities"""
    print("=== Chinese Text Processing Demo ===")
    
    processor = ChineseTextProcessor()
    
    # Sample regulatory text from test documents
    sample_text = """
    # 广东省分布式光伏发电管理办法

    ## 第一章 总则

    第一条 为规范分布式光伏发电项目管理，促进分布式光伏发电健康有序发展，根据《可再生能源法》、《电力法》等法律法规，结合本省实际，制定本办法。

    第二条 本办法适用于在广东省行政区域内建设的分布式光伏发电项目的备案、并网、运营等管理活动。

    第三条 分布式光伏发电是指在用户场地附近建设，运行方式以用户侧自发自用、多余电量上网，且在配电系统平衡调节为特征的光伏发电设施。

    ## 第二章 项目备案

    第四条 分布式光伏发电项目实行备案制管理。项目备案由县级以上发展改革部门负责。

    第五条 申请项目备案应当提交以下材料：
    1. 分布式光伏发电项目备案申请表
    2. 项目建设方案和设计文件
    3. 用电户同意项目建设的证明文件
    4. 土地使用权或屋顶使用权证明
    5. 电网接入系统方案
    """
    
    metadata = DocumentMetadata(
        province="gd",
        asset_type="solar",
        doc_class="grid",
        title="广东省分布式光伏发电管理办法"
    )
    
    print("Original text length:", len(sample_text))
    
    # Process the text
    processed_text = processor.process_text(sample_text, metadata)
    print("Processed text length:", len(processed_text) if processed_text else 0)
    
    # Split into sentences
    sentences = processor.split_into_sentences(sample_text)
    print(f"Split into {len(sentences)} sentences")
    
    # Show first few sentences
    print("\nFirst 3 sentences:")
    for i, sentence in enumerate(sentences[:3]):
        print(f"{i+1}. {sentence.strip()}")
    
    # Get statistics
    stats = processor.get_text_statistics(sample_text)
    print(f"\nText Statistics:")
    print(f"- Character count: {stats['char_count']}")
    print(f"- Chinese characters: {stats['chinese_char_count']}")
    print(f"- Chinese ratio: {stats['chinese_ratio']:.2%}")
    print(f"- Sentence count: {stats['sentence_count']}")
    print(f"- Key terms found: {stats['key_terms_count']}")
    
    if stats['key_terms']:
        print("- Sample key terms:", ", ".join(stats['key_terms'][:5]))
    
    # Extract regulatory structure
    print(f"\nRegulatory Structure:")
    for structure_type, count in stats['structure_counts'].items():
        print(f"- {structure_type}: {count}")
    
    return processed_text


def demo_document_creation():
    """Demonstrate document object creation"""
    print("\n=== Document Creation Demo ===")
    
    # Load sample document from test files
    test_doc_path = Path("test_documents/gd_solar_regulation.md")
    
    if test_doc_path.exists():
        with open(test_doc_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print(f"Loaded document from: {test_doc_path}")
        print(f"Content length: {len(content)} characters")
        
        # Create document object
        document = Document(
            id="gd_solar_001",
            title="广东省分布式光伏发电管理办法",
            content=content,
            metadata=DocumentMetadata(
                province="gd",
                asset_type="solar",
                doc_class="grid",
                title="广东省分布式光伏发电管理办法",
                doc_type="regulation"
            ),
            checksum="demo_checksum_001"
        )
        
        print(f"\nCreated document:")
        print(f"- ID: {document.id}")
        print(f"- Title: {document.title}")
        print(f"- Province: {document.metadata.province}")
        print(f"- Asset Type: {document.metadata.asset_type}")
        print(f"- Document Class: {document.metadata.doc_class}")
        
        # Convert to dictionary (for storage/serialization)
        doc_dict = document.to_dict()
        print(f"- Serializable: {len(doc_dict)} fields")
        
        return document
    
    else:
        print(f"Test document not found: {test_doc_path}")
        print("Creating sample document instead...")
        
        sample_content = """
        第一条 为规范分布式光伏发电项目管理，促进分布式光伏发电健康有序发展。
        第二条 本办法适用于在广东省行政区域内建设的分布式光伏发电项目。
        """
        
        document = Document(
            id="sample_001",
            title="Sample Regulation",
            content=sample_content,
            metadata=DocumentMetadata(
                province="gd",
                asset_type="solar",
                doc_class="grid"
            )
        )
        
        return document


def demo_chunking_strategy():
    """Demonstrate document chunking for RAG processing"""
    print("\n=== Document Chunking Demo ===")
    
    # Create a longer sample text
    long_text = """
    第一章 总则
    
    第一条 为规范分布式光伏发电项目管理，促进分布式光伏发电健康有序发展，根据《可再生能源法》、《电力法》等法律法规，结合本省实际，制定本办法。
    
    第二条 本办法适用于在广东省行政区域内建设的分布式光伏发电项目的备案、并网、运营等管理活动。
    
    第三条 分布式光伏发电是指在用户场地附近建设，运行方式以用户侧自发自用、多余电量上网，且在配电系统平衡调节为特征的光伏发电设施。
    
    第二章 项目备案
    
    第四条 分布式光伏发电项目实行备案制管理。项目备案由县级以上发展改革部门负责。
    
    第五条 申请项目备案应当提交以下材料：
    （一）分布式光伏发电项目备案申请表；
    （二）项目建设方案和设计文件；
    （三）用电户同意项目建设的证明文件；
    （四）土地使用权或屋顶使用权证明；
    （五）电网接入系统方案。
    
    第六条 发展改革部门应当在收到完整备案材料后15个工作日内完成备案手续。
    
    第三章 并网管理
    
    第七条 分布式光伏发电项目并网应当符合国家和省有关技术标准，满足电网安全运行要求。
    
    第八条 项目单位应当向电网企业提出并网申请，提交相关材料。
    """
    
    processor = ChineseTextProcessor()
    
    # Split into sentences for chunking
    sentences = processor.split_into_sentences(long_text)
    print(f"Document split into {len(sentences)} sentences")
    
    # Simulate chunking (simplified version)
    chunk_size = 200  # characters
    chunks = []
    current_chunk = ""
    
    for sentence in sentences:
        if len(current_chunk) + len(sentence) > chunk_size and current_chunk:
            chunks.append(current_chunk.strip())
            current_chunk = sentence
        else:
            current_chunk += sentence
    
    if current_chunk.strip():
        chunks.append(current_chunk.strip())
    
    print(f"Created {len(chunks)} chunks")
    
    # Show chunk information
    for i, chunk in enumerate(chunks):
        print(f"\nChunk {i+1} ({len(chunk)} chars):")
        print(f"  {chunk[:100]}...")
        
        # Extract key regulatory elements
        if "第" in chunk and "条" in chunk:
            print(f"  → Contains regulatory articles")
        if "第" in chunk and "章" in chunk:
            print(f"  → Contains chapter heading")
    
    return chunks


def main():
    """Run all demos"""
    print("RAG-Anything Document Processing Demo")
    print("=" * 50)
    
    # Demo 1: Chinese text processing
    processed_text = demo_chinese_text_processing()
    
    # Demo 2: Document creation
    document = demo_document_creation()
    
    # Demo 3: Chunking strategy
    chunks = demo_chunking_strategy()
    
    # Summary
    print("\n" + "=" * 50)
    print("Demo Summary:")
    print(f"✓ Chinese text processing: {len(processed_text) if processed_text else 0} chars processed")
    print(f"✓ Document creation: {document.id if document else 'None'}")
    print(f"✓ Document chunking: {len(chunks) if chunks else 0} chunks created")
    
    print("\nNext steps:")
    print("1. Install RAG-Anything framework: pip install git+https://github.com/HKUDS/RAG-Anything.git")
    print("2. Set OPENAI_API_KEY environment variable")
    print("3. Run: python test_rag_anything_pipeline.py")


if __name__ == "__main__":
    main()