"""
Document chunking module
Creates overlapping text chunks with metadata preservation
"""

import re
from typing import List, Dict, Any


def create_chunks(
    doc_data: Dict[str, Any], 
    chunk_size: int = 800, 
    overlap: int = 100
) -> List[Dict[str, Any]]:
    """
    Create overlapping text chunks from document data
    
    Args:
        doc_data: Document data with text and metadata
        chunk_size: Target chunk size in tokens (approximate)
        overlap: Overlap size in tokens
        
    Returns:
        List of chunks with text and preserved metadata
    """
    text = doc_data.get('text', '')
    if not text:
        return []
        
    # Estimate tokens (rough approximation for Chinese text)
    # Chinese characters are roughly 1.5 tokens each
    char_to_token_ratio = 1.5
    target_chars = int(chunk_size / char_to_token_ratio)
    overlap_chars = int(overlap / char_to_token_ratio)
    
    chunks = []
    
    # Split text into sentences for better chunk boundaries
    sentences = _split_into_sentences(text)
    
    current_chunk = ""
    current_length = 0
    
    for sentence in sentences:
        sentence_length = len(sentence)
        
        # If adding this sentence would exceed chunk size, finalize current chunk
        if current_length + sentence_length > target_chars and current_chunk:
            # Create chunk with metadata
            chunk = _create_chunk_dict(
                text=current_chunk.strip(),
                doc_data=doc_data,
                chunk_index=len(chunks)
            )
            chunks.append(chunk)
            
            # Start new chunk with overlap
            overlap_text = _get_overlap_text(current_chunk, overlap_chars)
            current_chunk = overlap_text + sentence
            current_length = len(current_chunk)
        else:
            # Add sentence to current chunk
            current_chunk += sentence
            current_length += sentence_length
            
    # Add final chunk if there's remaining text
    if current_chunk.strip():
        chunk = _create_chunk_dict(
            text=current_chunk.strip(),
            doc_data=doc_data,
            chunk_index=len(chunks)
        )
        chunks.append(chunk)
        
    return chunks


def _split_into_sentences(text: str) -> List[str]:
    """
    Split Chinese text into sentences using punctuation
    
    Args:
        text: Input text
        
    Returns:
        List of sentences
    """
    # Chinese sentence endings
    sentence_endings = r'[。！？；]'
    
    # Split on sentence endings but keep the punctuation
    sentences = re.split(f'({sentence_endings})', text)
    
    # Recombine sentences with their punctuation
    result = []
    for i in range(0, len(sentences) - 1, 2):
        sentence = sentences[i]
        if i + 1 < len(sentences):
            punctuation = sentences[i + 1]
            sentence += punctuation
            
        if sentence.strip():
            result.append(sentence)
            
    return result


def _get_overlap_text(text: str, overlap_chars: int) -> str:
    """
    Get overlap text from the end of current chunk
    
    Args:
        text: Current chunk text
        overlap_chars: Number of characters for overlap
        
    Returns:
        Overlap text
    """
    if len(text) <= overlap_chars:
        return text
        
    # Try to find a good sentence boundary for overlap
    overlap_text = text[-overlap_chars:]
    
    # Look for sentence boundary in overlap region
    sentence_endings = r'[。！？；]'
    matches = list(re.finditer(sentence_endings, overlap_text))
    
    if matches:
        # Use text after the last sentence ending in overlap
        last_match = matches[-1]
        overlap_text = overlap_text[last_match.end():]
        
    return overlap_text


def _create_chunk_dict(text: str, doc_data: Dict[str, Any], chunk_index: int) -> Dict[str, Any]:
    """
    Create chunk dictionary with text and metadata
    
    Args:
        text: Chunk text content
        doc_data: Original document data
        chunk_index: Index of this chunk in the document
        
    Returns:
        Chunk dictionary with metadata
    """
    # Preserve important metadata from document
    chunk = {
        'text': text,
        'chunk_index': chunk_index,
        'metadata': {
            'title': doc_data.get('title', ''),
            'url': doc_data.get('url', ''),
            'effective_date': doc_data.get('effective_date'),
            'province': doc_data.get('province', ''),
            'asset': doc_data.get('asset', ''),
            'doc_class': doc_data.get('doc_class', ''),
            'checksum': doc_data.get('checksum', ''),
            'lang': doc_data.get('lang', 'zh-CN')
        }
    }
    
    # Remove None values from metadata
    chunk['metadata'] = {k: v for k, v in chunk['metadata'].items() if v is not None}
    
    return chunk


def validate_chunks(chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Validate and filter chunks for quality
    
    Args:
        chunks: List of chunks to validate
        
    Returns:
        Filtered list of valid chunks
    """
    valid_chunks = []
    
    for chunk in chunks:
        text = chunk.get('text', '')
        
        # Skip chunks that are too short or too long
        if len(text) < 50:  # Too short to be meaningful
            continue
            
        if len(text) > 2000:  # Too long, might be malformed
            continue
            
        # Skip chunks with too much repetitive content
        if _is_repetitive_content(text):
            continue
            
        # Skip chunks that are mostly non-Chinese content
        if not _has_sufficient_chinese_content(text):
            continue
            
        valid_chunks.append(chunk)
        
    return valid_chunks


def _is_repetitive_content(text: str) -> bool:
    """
    Check if text contains too much repetitive content
    
    Args:
        text: Text to check
        
    Returns:
        True if content is repetitive
    """
    # Simple check for repeated patterns
    words = text.split()
    if len(words) < 10:
        return False
        
    # Check for repeated sequences
    word_counts = {}
    for word in words:
        word_counts[word] = word_counts.get(word, 0) + 1
        
    # If any word appears more than 30% of the time, consider repetitive
    max_count = max(word_counts.values())
    if max_count > len(words) * 0.3:
        return True
        
    return False


def _has_sufficient_chinese_content(text: str) -> bool:
    """
    Check if text has sufficient Chinese content
    
    Args:
        text: Text to check
        
    Returns:
        True if text has enough Chinese characters
    """
    chinese_chars = 0
    total_chars = 0
    
    for char in text:
        if char.strip():  # Skip whitespace
            total_chars += 1
            # Check if character is in CJK Unicode ranges
            if '\u4e00' <= char <= '\u9fff':  # CJK Unified Ideographs
                chinese_chars += 1
                
    if total_chars == 0:
        return False
        
    # Require at least 50% Chinese characters
    chinese_ratio = chinese_chars / total_chars
    return chinese_ratio >= 0.5