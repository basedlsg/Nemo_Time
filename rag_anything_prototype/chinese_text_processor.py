"""
Chinese Text Processing Module
Specialized processing for Chinese regulatory documents
"""

import re
from typing import List, Dict, Any, Optional

try:
    from .document_models import DocumentMetadata
except ImportError:
    # Handle case when imported directly
    from document_models import DocumentMetadata


class ChineseTextProcessor:
    """
    Specialized processor for Chinese regulatory text
    Handles normalization, segmentation, and quality validation
    """
    
    def __init__(self):
        # Chinese punctuation patterns
        self.sentence_endings = r'[。！？；]'
        self.paragraph_markers = r'[第一二三四五六七八九十百千万\d]+[章条款项]'
        
        # Regulatory document patterns
        self.regulation_patterns = {
            'article': r'第[一二三四五六七八九十百千万\d]+条',
            'chapter': r'第[一二三四五六七八九十百千万\d]+章',
            'section': r'第[一二三四五六七八九十百千万\d]+节',
            'item': r'[（(][一二三四五六七八九十\d]+[）)]',
            'numbered_list': r'^\s*\d+[.、]',
            'bullet_point': r'^\s*[-•·]'
        }
        
        # Technical terms that should be preserved
        self.technical_terms = {
            '电力系统', '配电网', '输电线路', '变电站', '发电机组',
            '光伏发电', '风力发电', '煤电机组', '并网', '电网',
            '功率因数', '短路电流', '电压等级', '频率调节', '继电保护',
            '备案', '许可证', '环评', '安全评价', '技术标准'
        }
    
    def process_text(
        self, 
        text: str, 
        metadata: DocumentMetadata
    ) -> Optional[str]:
        """
        Process Chinese regulatory text with normalization and validation
        
        Args:
            text: Raw text content
            metadata: Document metadata for context
            
        Returns:
            Processed text or None if processing fails
        """
        if not text or not text.strip():
            return None
        
        try:
            # Step 1: Basic normalization
            normalized_text = self._normalize_text(text)
            
            # Step 2: Validate Chinese content
            if not self._validate_chinese_content(normalized_text):
                print("Text validation failed - insufficient Chinese content")
                return None
            
            # Step 3: Structure-aware processing for regulatory documents
            structured_text = self._process_regulatory_structure(normalized_text)
            
            # Step 4: Clean and format
            cleaned_text = self._clean_text(structured_text)
            
            # Step 5: Final validation
            if len(cleaned_text.strip()) < 50:
                print("Processed text too short")
                return None
            
            return cleaned_text
            
        except Exception as e:
            print(f"Error processing Chinese text: {str(e)}")
            return None
    
    def split_into_sentences(self, text: str) -> List[str]:
        """
        Split Chinese text into sentences with regulatory structure awareness
        
        Args:
            text: Text to split
            
        Returns:
            List of sentences
        """
        if not text:
            return []
        
        # First, split on major sentence endings
        sentences = re.split(f'({self.sentence_endings})', text)
        
        # Recombine sentences with their punctuation
        combined_sentences = []
        for i in range(0, len(sentences) - 1, 2):
            sentence = sentences[i]
            if i + 1 < len(sentences):
                punctuation = sentences[i + 1]
                sentence += punctuation
            
            if sentence.strip():
                combined_sentences.append(sentence)
        
        # Further split long sentences at regulatory boundaries
        final_sentences = []
        for sentence in combined_sentences:
            if len(sentence) > 200:  # Long sentence, try to split
                sub_sentences = self._split_long_sentence(sentence)
                final_sentences.extend(sub_sentences)
            else:
                final_sentences.append(sentence)
        
        return [s.strip() for s in final_sentences if s.strip()]
    
    def _normalize_text(self, text: str) -> str:
        """Basic text normalization for Chinese content"""
        
        # Convert full-width characters to half-width where appropriate
        text = text.replace('（', '(').replace('）', ')')
        text = text.replace('【', '[').replace('】', ']')
        
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'\n\s*\n', '\n\n', text)  # Preserve paragraph breaks
        
        # Remove excessive punctuation
        text = re.sub(r'[。]{2,}', '。', text)
        text = re.sub(r'[，]{2,}', '，', text)
        
        # Clean up common OCR errors in Chinese text
        text = text.replace('O', '0')  # Common OCR confusion
        text = text.replace('l', '1')  # Common OCR confusion in numbers
        
        return text.strip()
    
    def _validate_chinese_content(self, text: str) -> bool:
        """Validate that text contains sufficient Chinese content"""
        
        if not text:
            return False
        
        # Count Chinese characters
        chinese_chars = sum(1 for char in text if '\u4e00' <= char <= '\u9fff')
        total_chars = len([c for c in text if c.strip()])
        
        if total_chars == 0:
            return False
        
        chinese_ratio = chinese_chars / total_chars
        
        # Require at least 50% Chinese characters for regulatory documents
        return chinese_ratio >= 0.5
    
    def _process_regulatory_structure(self, text: str) -> str:
        """Process text with awareness of regulatory document structure"""
        
        lines = text.split('\n')
        processed_lines = []
        
        for line in lines:
            line = line.strip()
            if not line:
                processed_lines.append('')
                continue
            
            # Identify and mark regulatory structures
            marked_line = self._mark_regulatory_elements(line)
            processed_lines.append(marked_line)
        
        return '\n'.join(processed_lines)
    
    def _mark_regulatory_elements(self, line: str) -> str:
        """Mark regulatory elements in a line for better chunking"""
        
        # Check for articles, chapters, sections
        for element_type, pattern in self.regulation_patterns.items():
            if re.match(pattern, line):
                # Add structural marker (will be used for chunking boundaries)
                return f"[{element_type.upper()}] {line}"
        
        return line
    
    def _split_long_sentence(self, sentence: str) -> List[str]:
        """Split long sentences at natural regulatory boundaries"""
        
        # Try to split at regulatory markers
        for pattern in self.regulation_patterns.values():
            matches = list(re.finditer(pattern, sentence))
            if len(matches) > 1:
                # Split at regulatory boundaries
                parts = []
                last_end = 0
                
                for match in matches[1:]:  # Skip first match
                    part = sentence[last_end:match.start()].strip()
                    if part:
                        parts.append(part)
                    last_end = match.start()
                
                # Add remaining part
                remaining = sentence[last_end:].strip()
                if remaining:
                    parts.append(remaining)
                
                if len(parts) > 1:
                    return parts
        
        # Fallback: split at commas if sentence is very long
        if len(sentence) > 300:
            parts = sentence.split('，')
            if len(parts) > 2:
                # Recombine into reasonable chunks
                chunks = []
                current_chunk = ""
                
                for part in parts:
                    if len(current_chunk + part) > 150 and current_chunk:
                        chunks.append(current_chunk.strip() + '，')
                        current_chunk = part
                    else:
                        current_chunk += part + '，'
                
                if current_chunk:
                    chunks.append(current_chunk.rstrip('，'))
                
                return [chunk for chunk in chunks if chunk.strip()]
        
        return [sentence]
    
    def _clean_text(self, text: str) -> str:
        """Final text cleaning and formatting"""
        
        # Remove excessive whitespace
        text = re.sub(r' +', ' ', text)
        text = re.sub(r'\n +', '\n', text)
        text = re.sub(r' +\n', '\n', text)
        
        # Remove empty lines between regulatory elements
        text = re.sub(r'\n\[([A-Z_]+)\]\s*\n', r'\n[\1] ', text)
        
        # Ensure proper spacing around punctuation
        text = re.sub(r'([。！？；])([^\s\n])', r'\1 \2', text)
        
        # Remove trailing whitespace from lines
        lines = [line.rstrip() for line in text.split('\n')]
        text = '\n'.join(lines)
        
        return text.strip()
    
    def extract_key_terms(self, text: str) -> List[str]:
        """Extract key regulatory terms from text"""
        
        found_terms = []
        
        # Look for predefined technical terms
        for term in self.technical_terms:
            if term in text:
                found_terms.append(term)
        
        # Extract regulatory references
        for element_type, pattern in self.regulation_patterns.items():
            matches = re.findall(pattern, text)
            found_terms.extend(matches)
        
        # Extract numbers and measurements (common in technical docs)
        number_patterns = [
            r'\d+(?:\.\d+)?[kKmM]?[VvWwAa]',  # Electrical units
            r'\d+(?:\.\d+)?%',  # Percentages
            r'\d+(?:\.\d+)?[年月日]',  # Dates
            r'\d+(?:\.\d+)?[米千万亿]'  # Chinese numbers
        ]
        
        for pattern in number_patterns:
            matches = re.findall(pattern, text)
            found_terms.extend(matches)
        
        return list(set(found_terms))  # Remove duplicates
    
    def get_text_statistics(self, text: str) -> Dict[str, Any]:
        """Get statistics about the processed text"""
        
        if not text:
            return {}
        
        # Basic counts
        char_count = len(text)
        chinese_char_count = sum(1 for char in text if '\u4e00' <= char <= '\u9fff')
        sentence_count = len(re.findall(self.sentence_endings, text))
        
        # Regulatory structure counts
        structure_counts = {}
        for element_type, pattern in self.regulation_patterns.items():
            count = len(re.findall(pattern, text))
            if count > 0:
                structure_counts[element_type] = count
        
        # Key terms
        key_terms = self.extract_key_terms(text)
        
        return {
            'char_count': char_count,
            'chinese_char_count': chinese_char_count,
            'chinese_ratio': chinese_char_count / char_count if char_count > 0 else 0,
            'sentence_count': sentence_count,
            'structure_counts': structure_counts,
            'key_terms_count': len(key_terms),
            'key_terms': key_terms[:10]  # Top 10 terms
        }