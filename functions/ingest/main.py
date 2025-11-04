"""
Nemo Compliance MVP - Ingestion Cloud Function
Handles document discovery, processing, and indexing pipeline
"""

import os
import json
import uuid
import time
from typing import Dict, Any, List
import functions_framework
from flask import Request, make_response

# Import shared libraries (local copies)
from cse import discover_documents
from docai import process_document
from lib.sanitize import normalize_text, extract_effective_date
from chunker import create_chunks
from vertex_index import upsert_chunks, embed_text


@functions_framework.http
def ingest_handler(request: Request) -> Dict[str, Any]:
    """
    Main ingestion handler for regulatory document processing
    
    Expected request format:
    {
        "province": "gd|sd|nm" (optional - if not provided, process all),
        "asset": "solar|coal|wind" (optional - if not provided, process all),
        "doc_class": "grid" (optional - defaults to grid)
    }
    """
    job_id = f"ing-{int(time.time())}-{uuid.uuid4().hex[:6]}"
    
    try:
        # CORS preflight
        if request.method == 'OPTIONS':
            return _cors_response({}, 204)
        # Validate authentication token
        auth_token = request.headers.get('X-Ingest-Token')
        expected_token = os.environ.get('INGEST_TOKEN')
        
        if not auth_token or auth_token != expected_token:
            return _cors_response({'error': 'Unauthorized', 'status_code': 403}, 403)
            
        # Parse request
        request_json = request.get_json(silent=True) or {}
        
        # Set defaults and validate
        provinces = [request_json.get('province')] if request_json.get('province') else ['gd', 'sd', 'nm']
        assets = [request_json.get('asset')] if request_json.get('asset') else ['solar', 'coal', 'wind']
        doc_class = request_json.get('doc_class', 'grid')
        
        # Validate enum values
        valid_provinces = ['gd', 'sd', 'nm']
        valid_assets = ['solar', 'coal', 'wind']
        
        for province in provinces:
            if province not in valid_provinces:
                return {'error': f'Invalid province: {province}', 'status_code': 400}
                
        for asset in assets:
            if asset not in valid_assets:
                return {'error': f'Invalid asset: {asset}', 'status_code': 400}
                
        if doc_class != 'grid':
            return {'error': 'Invalid doc_class. Must be: grid', 'status_code': 400}
            
        print(f"[{job_id}] Starting ingestion: provinces={provinces}, assets={assets}, doc_class={doc_class}")
        
        # Start async ingestion job
        # For MVP, run synchronously but return immediately with job status
        total_processed = 0
        total_errors = 0
        
        for province in provinces:
            for asset in assets:
                try:
                    processed, errors = _process_province_asset(job_id, province, asset, doc_class)
                    total_processed += processed
                    total_errors += errors
                except Exception as e:
                    print(f"[{job_id}] Error processing {province}/{asset}: {str(e)}")
                    total_errors += 1
                    
        print(f"[{job_id}] Ingestion complete: processed={total_processed}, errors={total_errors}")
        
        return _cors_response({
            'accepted': True,
            'job_id': job_id,
            'estimated_minutes': 3,
            'processed_documents': total_processed,
            'errors': total_errors
        }, 202)
        
    except Exception as e:
        print(f"[{job_id}] Ingestion error: {str(e)}")
        return _cors_response({
            'error': f'Ingestion failed: {str(e)}',
            'job_id': job_id,
            'status_code': 500
        }, 500)


def _process_province_asset(job_id: str, province: str, asset: str, doc_class: str) -> tuple[int, int]:
    """Process documents for a specific province/asset combination"""
    
    print(f"[{job_id}] Processing {province}/{asset}/{doc_class}")
    
    # Discover documents
    discovered_urls = discover_documents(province, asset, doc_class)
    print(f"[{job_id}] Discovered {len(discovered_urls)} URLs for {province}/{asset}")
    
    processed_count = 0
    error_count = 0
    
    for url in discovered_urls:
        try:
            # Process single document through full pipeline
            success = _process_single_document(job_id, url, province, asset, doc_class)
            if success:
                processed_count += 1
            else:
                error_count += 1
                
        except Exception as e:
            print(f"[{job_id}] Error processing document {url}: {str(e)}")
            error_count += 1
            
    return processed_count, error_count


def _process_single_document(job_id: str, url: str, province: str, asset: str, doc_class: str) -> bool:
    """Process a single document through the full pipeline"""
    
    try:
        # Fetch and store in GCS /raw/
        # TODO: Implement in task 4.2
        
        # Process with Document AI
        doc_data = process_document(url, province, asset, doc_class)
        if not doc_data:
            print(f"[{job_id}] Failed to process document: {url}")
            return False
            
        # Normalize text
        normalized_text = normalize_text(doc_data['text'])
        doc_data['text'] = normalized_text
        
        # Extract effective date
        effective_date = extract_effective_date(normalized_text)
        if effective_date:
            doc_data['effective_date'] = effective_date
            
        # Create chunks
        chunks = create_chunks(doc_data)
        print(f"[{job_id}] Created {len(chunks)} chunks for {url}")
        
        # Embed chunks
        for chunk in chunks:
            chunk['embedding'] = embed_text(chunk['text'])
            
        # Upsert to vector index
        upsert_chunks(chunks)
        
        print(f"[{job_id}] Successfully processed: {url}")
        return True
        
    except Exception as e:
        print(f"[{job_id}] Error in document pipeline for {url}: {str(e)}")
        return False


def _cors_response(data, status=200):
    import json as _json
    resp = make_response(_json.dumps(data, ensure_ascii=False), status)
    resp.headers['Content-Type'] = 'application/json; charset=utf-8'
    resp.headers['Access-Control-Allow-Origin'] = '*'
    resp.headers['Access-Control-Allow-Methods'] = 'GET,POST,OPTIONS'
    resp.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization,X-Ingest-Token'
    resp.headers['Access-Control-Max-Age'] = '3600'
    return resp
