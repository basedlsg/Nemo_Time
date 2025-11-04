"""
Document AI integration module
Handles OCR and text extraction from PDF/DOCX files
"""

import os
import hashlib
import mimetypes
from typing import Dict, Any, Optional
from google.cloud import documentai
from google.cloud import storage
import requests
from lib.sanitize import normalize_text, extract_effective_date, extract_title_from_text, extract_document_type


def process_document(url: str, province: str, asset: str, doc_class: str) -> Optional[Dict[str, Any]]:
    """
    Process a document through the full Document AI pipeline
    
    Args:
        url: Document URL to process
        province: Province code (gd, sd, nm)
        asset: Asset type (solar, coal, wind)
        doc_class: Document class (grid)
        
    Returns:
        Processed document data with text and metadata
    """
    try:
        print(f"Processing document: {url}")
        
        # Download and store document
        raw_content, mime_type = _download_document(url)
        if not raw_content:
            print(f"Failed to download document: {url}")
            return None
            
        # Calculate checksum for deduplication
        checksum = hashlib.sha256(raw_content).hexdigest()
        
        # Store raw document in GCS
        raw_gcs_path = _store_raw_document(raw_content, checksum, mime_type, province)
        if not raw_gcs_path:
            print(f"Failed to store raw document: {url}")
            return None
            
        # Process with Document AI
        extracted_text = _extract_text_with_docai(raw_gcs_path, mime_type)
        if not extracted_text:
            print(f"Failed to extract text from document: {url}")
            return None
            
        # Normalize and clean text
        normalized_text = normalize_text(extracted_text)
        
        # Extract metadata
        title = extract_title_from_text(normalized_text)
        effective_date = extract_effective_date(normalized_text)
        doc_type = extract_document_type(normalized_text)
        
        # Build document data
        doc_data = {
            'title': title or f"{province.upper()} {asset} {doc_class} Document",
            'url': url,
            'effective_date': effective_date,
            'province': province,
            'asset': asset,
            'doc_class': doc_class,
            'doc_type': doc_type,
            'lang': 'zh-CN',
            'text': normalized_text,
            'checksum': checksum,
            'raw_gcs_path': raw_gcs_path,
            'ingested_at': _get_current_timestamp()
        }
        
        # Store clean document data
        clean_gcs_path = _store_clean_document(doc_data, checksum, province)
        doc_data['clean_gcs_path'] = clean_gcs_path
        
        print(f"Successfully processed document: {url} -> {len(normalized_text)} chars")
        return doc_data
        
    except Exception as e:
        print(f"Error processing document {url}: {str(e)}")
        return None


def _download_document(url: str) -> tuple[Optional[bytes], Optional[str]]:
    """
    Download document from URL
    
    Args:
        url: Document URL
        
    Returns:
        Tuple of (content bytes, mime type)
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (compatible; NemoComplianceBot/1.0)',
            'Accept': 'application/pdf,application/msword,application/vnd.openxmlformats-officedocument.wordprocessingml.document,text/html'
        }
        
        response = requests.get(url, headers=headers, timeout=30, stream=True)
        response.raise_for_status()
        
        # Check content length
        content_length = response.headers.get('content-length')
        if content_length and int(content_length) > 50 * 1024 * 1024:  # 50MB limit
            print(f"Document too large: {content_length} bytes")
            return None, None
            
        # Download content
        content = response.content
        
        # Determine MIME type
        mime_type = response.headers.get('content-type', '').split(';')[0]
        if not mime_type:
            mime_type, _ = mimetypes.guess_type(url)
            
        # Validate MIME type
        supported_types = [
            'application/pdf',
            'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'text/html'
        ]
        
        if mime_type not in supported_types:
            print(f"Unsupported MIME type: {mime_type}")
            return None, None
            
        return content, mime_type
        
    except Exception as e:
        print(f"Error downloading document {url}: {str(e)}")
        return None, None


def _store_raw_document(content: bytes, checksum: str, mime_type: str, province: str) -> Optional[str]:
    """
    Store raw document in GCS
    
    Args:
        content: Document content bytes
        checksum: Document checksum
        mime_type: Document MIME type
        province: Province code
        
    Returns:
        GCS path of stored document
    """
    try:
        bucket_name = os.environ.get('BUCKET_RAW')
        if not bucket_name:
            raise ValueError("BUCKET_RAW environment variable not set")
            
        # Determine file extension
        ext_map = {
            'application/pdf': 'pdf',
            'application/msword': 'doc',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 'docx',
            'text/html': 'html'
        }
        
        extension = ext_map.get(mime_type, 'bin')
        
        # Create GCS path
        from datetime import datetime
        date_str = datetime.utcnow().strftime('%Y%m%d')
        gcs_path = f"raw/{province}/{date_str}/{checksum}.{extension}"
        
        # Upload to GCS
        client = storage.Client()
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(gcs_path)
        
        # Check if already exists
        if blob.exists():
            print(f"Document already exists in GCS: {gcs_path}")
            return f"gs://{bucket_name}/{gcs_path}"
            
        # Upload with metadata
        blob.metadata = {
            'mime_type': mime_type,
            'checksum': checksum,
            'uploaded_at': _get_current_timestamp()
        }
        
        blob.upload_from_string(content, content_type=mime_type)
        
        print(f"Stored raw document: gs://{bucket_name}/{gcs_path}")
        return f"gs://{bucket_name}/{gcs_path}"
        
    except Exception as e:
        print(f"Error storing raw document: {str(e)}")
        return None


def _extract_text_with_docai(gcs_path: str, mime_type: str) -> Optional[str]:
    """
    Extract text from document using Document AI
    
    Args:
        gcs_path: GCS path to document
        mime_type: Document MIME type
        
    Returns:
        Extracted text content
    """
    try:
        project_id = os.environ.get('GOOGLE_CLOUD_PROJECT')
        # Prefer a dedicated Document AI location if provided; fallback to REGION
        location = os.environ.get('DOCAI_LOCATION') or os.environ.get('REGION', 'us')
        processor_id = os.environ.get('DOCAI_PROCESSOR_ID')
        
        if not all([project_id, processor_id]):
            # Fallback path: if HTML, read from GCS and strip tags
            if mime_type == 'text/html' and gcs_path.startswith('gs://'):
                try:
                    print("DOCAI not configured; falling back to simple HTML text extraction")
                    path_parts = gcs_path[5:].split('/', 1)
                    bucket_name = path_parts[0]
                    blob_path = path_parts[1]
                    client = storage.Client()
                    bucket = client.bucket(bucket_name)
                    blob = bucket.blob(blob_path)
                    html_content = blob.download_as_text()
                    # Very simple HTML to text
                    import re
                    text = re.sub(r'<[^>]+>', ' ', html_content)
                    text = re.sub(r'\s+', ' ', text).strip()
                    return text
                except Exception as e:
                    print(f"Fallback HTML extraction failed: {str(e)}")
                    return None
            # Otherwise, fail clearly
            raise ValueError("Missing Document AI configuration")
            
        # Initialize Document AI client
        client = documentai.DocumentProcessorServiceClient()
        
        # Prepare processor name
        processor_name = f"projects/{project_id}/locations/{location}/processors/{processor_id}"
        
        # Read document from GCS
        gcs_input_uri = gcs_path
        
        # Configure request
        raw_document = documentai.RawDocument(
            content=None,  # Will be read from GCS
            mime_type=mime_type
        )
        
        gcs_document = documentai.GcsDocument(
            gcs_uri=gcs_input_uri,
            mime_type=mime_type
        )
        
        # Process document
        request = documentai.ProcessRequest(
            name=processor_name,
            gcs_document=gcs_document
        )
        
        result = client.process_document(request=request)
        document = result.document
        
        # Extract text
        text_content = document.text
        
        if not text_content or len(text_content.strip()) < 10:
            print(f"No meaningful text extracted from {gcs_path}")
            return None
            
        print(f"Extracted {len(text_content)} characters from {gcs_path}")
        return text_content
        
    except Exception as e:
        print(f"Error extracting text with Document AI: {str(e)}")
        return None


def _store_clean_document(doc_data: Dict[str, Any], checksum: str, province: str) -> Optional[str]:
    """
    Store clean document data in GCS
    
    Args:
        doc_data: Processed document data
        checksum: Document checksum
        province: Province code
        
    Returns:
        GCS path of stored clean document
    """
    try:
        bucket_name = os.environ.get('BUCKET_CLEAN')
        if not bucket_name:
            raise ValueError("BUCKET_CLEAN environment variable not set")
            
        # Create GCS path
        gcs_path = f"clean/{province}/{checksum}.json"
        
        # Upload to GCS
        client = storage.Client()
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(gcs_path)
        
        # Store as JSON
        import json
        json_content = json.dumps(doc_data, ensure_ascii=False, indent=2)
        
        blob.upload_from_string(json_content, content_type='application/json')
        
        print(f"Stored clean document: gs://{bucket_name}/{gcs_path}")
        return f"gs://{bucket_name}/{gcs_path}"
        
    except Exception as e:
        print(f"Error storing clean document: {str(e)}")
        return None


def _get_current_timestamp() -> str:
    """Get current timestamp in ISO format"""
    from datetime import datetime
    return datetime.utcnow().isoformat() + 'Z'


def validate_document_quality(doc_data: Dict[str, Any]) -> bool:
    """
    Validate the quality of processed document
    
    Args:
        doc_data: Processed document data
        
    Returns:
        True if document meets quality standards
    """
    text = doc_data.get('text', '')
    
    # Check minimum length
    if len(text) < 100:
        print(f"Document too short: {len(text)} characters")
        return False
        
    # Check Chinese content ratio
    from lib.sanitize import validate_chinese_content_quality
    quality_metrics = validate_chinese_content_quality(text)
    
    if not quality_metrics['is_valid']:
        print(f"Document quality check failed: {quality_metrics}")
        return False
        
    # Check for required metadata
    required_fields = ['title', 'url', 'province', 'asset', 'doc_class']
    for field in required_fields:
        if not doc_data.get(field):
            print(f"Missing required field: {field}")
            return False
            
    return True


def get_document_from_gcs(gcs_path: str) -> Optional[Dict[str, Any]]:
    """
    Retrieve processed document from GCS
    
    Args:
        gcs_path: GCS path to clean document
        
    Returns:
        Document data dictionary
    """
    try:
        # Parse GCS path
        if not gcs_path.startswith('gs://'):
            raise ValueError("Invalid GCS path format")
            
        path_parts = gcs_path[5:].split('/', 1)
        bucket_name = path_parts[0]
        blob_path = path_parts[1]
        
        # Download from GCS
        client = storage.Client()
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(blob_path)
        
        if not blob.exists():
            print(f"Document not found in GCS: {gcs_path}")
            return None
            
        content = blob.download_as_text()
        
        # Parse JSON
        import json
        doc_data = json.loads(content)
        
        return doc_data
        
    except Exception as e:
        print(f"Error retrieving document from GCS: {str(e)}")
        return None


def check_document_exists(checksum: str, province: str) -> bool:
    """
    Check if document already exists in clean storage
    
    Args:
        checksum: Document checksum
        province: Province code
        
    Returns:
        True if document exists
    """
    try:
        bucket_name = os.environ.get('BUCKET_CLEAN')
        if not bucket_name:
            return False
            
        gcs_path = f"clean/{province}/{checksum}.json"
        
        client = storage.Client()
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(gcs_path)
        
        return blob.exists()
        
    except Exception as e:
        print(f"Error checking document existence: {str(e)}")
        return False
