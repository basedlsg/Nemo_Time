"""
Gemini reranking module
Optional reranking of search results using Gemini 1.5 Pro
"""

import os
import json
from typing import List, Dict, Any, Optional
import google.generativeai as genai
from google.cloud import secretmanager


def rerank_candidates(
    candidates: List[Dict[str, Any]], 
    question: str, 
    top_k: int = 5
) -> List[Dict[str, Any]]:
    """
    Rerank candidate chunks using Gemini 1.5 Pro
    
    Args:
        candidates: List of candidate chunks from vector search
        question: Original user question
        top_k: Number of top results to return
        
    Returns:
        Reranked list of candidates
    """
    try:
        # Check if reranking is enabled
        if not _is_reranking_enabled():
            print("Gemini reranking is disabled")
            return candidates[:top_k]
            
        if len(candidates) <= top_k:
            print(f"Only {len(candidates)} candidates, no reranking needed")
            return candidates
            
        print(f"Reranking {len(candidates)} candidates with Gemini")
        
        # Initialize Gemini
        api_key = _get_gemini_api_key()
        if not api_key:
            print("Gemini API key not available, skipping reranking")
            return candidates[:top_k]
            
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-pro')
        
        # Prepare reranking prompt
        prompt = _build_reranking_prompt(question, candidates)
        
        # Generate reranking scores
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.1,  # Low temperature for consistent scoring
                max_output_tokens=1000,
                candidate_count=1
            )
        )
        
        # Parse reranking results
        reranked_candidates = _parse_reranking_response(response.text, candidates)
        
        # Return top-k results
        result = reranked_candidates[:top_k]
        print(f"Gemini reranking returned {len(result)} candidates")
        
        return result
        
    except Exception as e:
        print(f"Error in Gemini reranking: {str(e)}")
        # Fallback to original order
        return candidates[:top_k]


def _is_reranking_enabled() -> bool:
    """
    Check if Gemini reranking is enabled
    
    Returns:
        True if reranking is enabled
    """
    return os.environ.get('RERANK', 'false').lower() == 'true'


def _get_gemini_api_key() -> Optional[str]:
    """
    Get Gemini API key from Secret Manager
    
    Returns:
        API key or None if not available
    """
    try:
        project_id = os.environ.get('GOOGLE_CLOUD_PROJECT')
        if not project_id:
            return None
            
        client = secretmanager.SecretManagerServiceClient()
        secret_path = f"projects/{project_id}/secrets/gemini-api-key/versions/latest"
        
        response = client.access_secret_version(request={"name": secret_path})
        return response.payload.data.decode("UTF-8")
        
    except Exception as e:
        print(f"Error accessing Gemini API key: {str(e)}")
        return None


def _build_reranking_prompt(question: str, candidates: List[Dict[str, Any]]) -> str:
    """
    Build prompt for Gemini reranking
    
    Args:
        question: User question
        candidates: List of candidate chunks
        
    Returns:
        Reranking prompt string
    """
    prompt = f"""你是一个中国能源法规专家。请根据用户问题对以下文档片段进行相关性排序。

用户问题：{question}

请对以下文档片段按相关性从高到低排序（1=最相关，数字越大相关性越低）：

"""
    
    for i, candidate in enumerate(candidates):
        text = candidate.get('text', '')[:300]  # Limit text length
        metadata = candidate.get('metadata', {})
        title = metadata.get('title', '未知文档')
        
        prompt += f"""
片段 {i+1}:
标题: {title}
内容: {text}...

"""
    
    prompt += f"""
请返回JSON格式的排序结果，包含每个片段的序号和相关性分数（1-10，10最相关）：

{{
  "rankings": [
    {{"index": 1, "score": 9, "reason": "直接回答了用户关于并网的问题"}},
    {{"index": 2, "score": 7, "reason": "包含相关的技术要求信息"}},
    ...
  ]
}}

只返回JSON，不要其他解释。"""
    
    return prompt


def _parse_reranking_response(response_text: str, candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Parse Gemini reranking response and reorder candidates
    
    Args:
        response_text: Gemini response text
        candidates: Original candidates list
        
    Returns:
        Reordered candidates list
    """
    try:
        # Extract JSON from response
        json_start = response_text.find('{')
        json_end = response_text.rfind('}') + 1
        
        if json_start == -1 or json_end == 0:
            print("No JSON found in Gemini response")
            return candidates
            
        json_text = response_text[json_start:json_end]
        ranking_data = json.loads(json_text)
        
        rankings = ranking_data.get('rankings', [])
        if not rankings:
            print("No rankings found in Gemini response")
            return candidates
            
        # Sort by score (descending)
        rankings.sort(key=lambda x: x.get('score', 0), reverse=True)
        
        # Reorder candidates based on rankings
        reordered = []
        used_indices = set()
        
        for ranking in rankings:
            index = ranking.get('index', 0) - 1  # Convert to 0-based
            if 0 <= index < len(candidates) and index not in used_indices:
                reordered.append(candidates[index])
                used_indices.add(index)
        
        # Add any remaining candidates that weren't ranked
        for i, candidate in enumerate(candidates):
            if i not in used_indices:
                reordered.append(candidate)
                
        print(f"Gemini reranked {len(used_indices)} out of {len(candidates)} candidates")
        return reordered
        
    except Exception as e:
        print(f"Error parsing Gemini reranking response: {str(e)}")
        return candidates


def test_gemini_connectivity() -> bool:
    """
    Test Gemini API connectivity
    
    Returns:
        True if Gemini is accessible
    """
    try:
        api_key = _get_gemini_api_key()
        if not api_key:
            return False
            
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-pro')
        
        # Simple test query
        response = model.generate_content(
            "测试连接。请回复'连接成功'。",
            generation_config=genai.types.GenerationConfig(
                temperature=0.1,
                max_output_tokens=10
            )
        )
        
        return "连接成功" in response.text or "成功" in response.text
        
    except Exception as e:
        print(f"Gemini connectivity test failed: {str(e)}")
        return False


def get_reranking_stats() -> Dict[str, Any]:
    """
    Get reranking statistics
    
    Returns:
        Dictionary with reranking stats
    """
    return {
        'enabled': _is_reranking_enabled(),
        'api_key_available': _get_gemini_api_key() is not None,
        'model': 'gemini-1.5-pro',
        'total_rerank_calls': 0,  # Would be tracked in production
        'average_latency_ms': 0   # Would be tracked in production
    }