"""
Nemo Compliance MVP - Query Cloud Function
Handles real-time user queries for Chinese energy regulation documents
"""

import os
import json
import uuid
import time
from typing import Dict, Any, Optional, List
import functions_framework
from flask import Request, make_response

# Import shared libraries (local copies)
from vertex_index import search_documents, embed_query
from composer import compose_response
from lib.sanitize import normalize_query
# CSE removed - using Perplexity-first architecture
from perplexity import answer_with_perplexity
import requests
import re


@functions_framework.http
def query_handler(request: Request) -> Dict[str, Any]:
    """
    Main query handler for regulatory document search
    
    Expected request format:
    {
        "province": "gd|sd|nm",
        "asset": "solar|coal|wind", 
        "doc_class": "grid",
        "question": "Chinese question text",
        "lang": "zh-CN"
    }
    """
    trace_id = f"gaea-{uuid.uuid4().hex[:12]}"
    start_time = time.time()
    
    try:
        # CORS preflight
        if request.method == 'OPTIONS':
            return _cors_response({}, 204)
        # Parse and validate request
        if request.method != 'POST':
            return _cors_response(_error_dict("Method not allowed", trace_id, 405), 405)
            
        request_json = request.get_json(silent=True)
        if not request_json:
            return _cors_response(_error_dict("Invalid JSON request", trace_id, 400), 400)
            
        # Validate required fields
        required_fields = ['province', 'asset', 'doc_class', 'question']
        for field in required_fields:
            if field not in request_json:
                return _cors_response(_error_dict(f"Missing required field: {field}", trace_id, 400), 400)
        
        province = request_json['province']
        asset = request_json['asset'] 
        doc_class = request_json['doc_class']
        question = request_json['question']
        lang = request_json.get('lang', 'zh-CN')
        
        # Validate enum values
        if province not in ['gd', 'sd', 'nm']:
            return _cors_response(_error_dict("Invalid province. Must be: gd, sd, nm", trace_id, 400), 400)
        if asset not in ['solar', 'coal', 'wind']:
            return _cors_response(_error_dict("Invalid asset. Must be: solar, coal, wind", trace_id, 400), 400)
        if doc_class != 'grid':
            return _cors_response(_error_dict("Invalid doc_class. Must be: grid", trace_id, 400), 400)
            
        # Log request
        print(f"[{trace_id}] Query request: province={province}, asset={asset}, question_hash={hash(question)}")
        
        # Process query
        normalized_question = normalize_query(question)

        # 1) PRIMARY PATH: Vertex AI RAG (vector search)
        candidates: List[Dict[str, Any]] = []
        search_ms = 0
        try:
            query_vector = embed_query(normalized_question)
            filters = {
                'province': province,
                'asset': asset,
                'doc_class': doc_class
            }
            search_start = time.time()
            candidates = search_documents(query_vector, filters, top_k=12)
            search_ms = int((time.time() - search_start) * 1000)
            print(f"[{trace_id}] Vector search: {len(candidates)} candidates in {search_ms}ms")
        except Exception as e:
            print(f"[{trace_id}] Vector search unavailable: {str(e)}")
        
        # Optional reranking (disabled by default)
        rerank_enabled = os.environ.get('RERANK', 'false').lower() == 'true'
        rerank_ms = 0
        
        if rerank_enabled and candidates:
            from gemini_rerank import rerank_candidates
            rerank_start = time.time()
            candidates = rerank_candidates(candidates, normalized_question, top_k=5)
            rerank_ms = int((time.time() - rerank_start) * 1000)
            print(f"[{trace_id}] Gemini reranking: {rerank_ms}ms")
            
        # Compose response
        compose_start = time.time()
        if not candidates:
            # FALLBACK: Try Perplexity if no documents in vector database
            print(f"[{trace_id}] No vector search results, falling back to Perplexity")
            p_start = time.time()
            p_ans = answer_with_perplexity(normalized_question, province, asset, lang=lang, doc_class=doc_class)
            if p_ans and p_ans.get('citations'):
                response = {
                    **p_ans,
                    'trace_id': trace_id,
                    'mode': 'perplexity_fallback'  # Indicate this was fallback path
                }
                elapsed_ms = int((time.time() - start_time) * 1000)
                response['elapsed_ms'] = elapsed_ms
                print(f"[{trace_id}] Perplexity fallback returned {len(p_ans['citations'])} citations in {int((time.time()-p_start)*1000)}ms")
            else:
                # Both RAG and Perplexity failed - return honest refusal
                response = _refusal_response(trace_id, int((time.time() - start_time) * 1000), lang)
        else:
            # SUCCESS: Use documents from vector database (TRUE RAG)
            response = compose_response(candidates, normalized_question, lang)
            response['trace_id'] = trace_id
            response['mode'] = 'vertex_rag'  # Primary path - real RAG
            print(f"[{trace_id}] RAG response generated from {len(candidates)} document chunks")
            
        compose_ms = int((time.time() - compose_start) * 1000)
        
        elapsed_ms = int((time.time() - start_time) * 1000)
        response['elapsed_ms'] = elapsed_ms
        
        print(f"[{trace_id}] Response composed in {compose_ms}ms, total: {elapsed_ms}ms")
        
        return _cors_response(response, 200)
        
    except Exception as e:
        print(f"[{trace_id}] Error: {str(e)}")
        return _cors_response(_error_dict(f"Internal server error: {str(e)}", trace_id, 500), 500)


def _error_dict(message: str, trace_id: str, status_code: int) -> Dict[str, Any]:
    """Generate structured error body (without CORS headers)"""
    return {
        'error': True,
        'message': message,
        'trace_id': trace_id,
        'status_code': status_code
    }


def _refusal_response(trace_id: str, elapsed_ms: int, lang: str) -> Dict[str, Any]:
    """Generate refusal response when no documents found"""
    zh = (lang or '').lower().startswith('zh')
    return {
        'mode': 'vertex_rag',
        'elapsed_ms': elapsed_ms,
        'refusal': '未找到相关的一手资料。' if zh else 'No directly relevant primary sources were found.',
        'tips': [
            ('请指定省份与资产类型' if zh else 'Please specify province and asset type'),
            ('尝试更具体的关键词，例如"并网验收资料清单"' if zh else 'Try more specific keywords, e.g., "grid acceptance document checklist"')
        ],
        'trace_id': trace_id
    }


def _fetch_page_title(url: str, timeout: int = 12) -> Optional[str]:
    """Fetch page title for a URL (lightweight, best-effort)."""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (compatible; NemoComplianceBot/1.0)'
        }
        resp = requests.get(url, headers=headers, timeout=timeout, stream=True)
        # Only attempt to read a small portion of the body
        content = resp.content[:200_000] if resp.content else b''
        text = content.decode('utf-8', errors='ignore')
        m = re.search(r'<title[^>]*>(.*?)</title>', text, flags=re.IGNORECASE | re.DOTALL)
        if m:
            # Clean whitespace/newlines
            title = re.sub(r'\s+', ' ', m.group(1)).strip()
            # Remove common suffixes
            for suf in [
                '_政府门户网站', '-政府门户网站', '_首页', '-首页', '_中国政府网', '-中国政府网'
            ]:
                if title.endswith(suf):
                    title = title[: -len(suf)].strip()
            return title[:120]
        return None
    except Exception:
        return None


def _cors_response(data: Dict[str, Any], status: int = 200):
    body = json.dumps(data, ensure_ascii=False)
    resp = make_response(body, status)
    resp.headers['Content-Type'] = 'application/json; charset=utf-8'
    resp.headers['Access-Control-Allow-Origin'] = '*'
    resp.headers['Access-Control-Allow-Methods'] = 'GET,POST,OPTIONS'
    resp.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization,X-Ingest-Token'
    resp.headers['Access-Control-Max-Age'] = '3600'
    return resp
