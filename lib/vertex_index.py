"""
Vertex AI Vector Search integration module
Handles embedding generation and vector search operations
"""

import os
from typing import List, Dict, Any, Optional
from google.cloud import aiplatform
from google.cloud.aiplatform import MatchingEngineIndex, MatchingEngineIndexEndpoint


def embed_text(text: str) -> List[float]:
    """
    Generate embeddings using Vertex AI text-embedding-004 model
    
    Args:
        text: Input text to embed
        
    Returns:
        List of embedding values
    """
    if not text or not text.strip():
        raise ValueError("Text cannot be empty")
        
    try:
        # Initialize Vertex AI
        project_id = os.environ.get('GOOGLE_CLOUD_PROJECT')
        region = os.environ.get('REGION', 'us-central1')
        
        if not project_id:
            raise ValueError("GOOGLE_CLOUD_PROJECT environment variable not set")
            
        aiplatform.init(project=project_id, location=region)
        
        # Use text-embedding-004 model
        model = aiplatform.TextEmbeddingModel.from_pretrained("text-embedding-004")
        
        # Truncate text if too long (model limit is ~8192 tokens)
        max_chars = 6000  # Conservative limit for Chinese text
        if len(text) > max_chars:
            text = text[:max_chars]
            print(f"Warning: Text truncated to {max_chars} characters for embedding")
        
        # Generate embedding
        embeddings = model.get_embeddings([text])
        
        if embeddings and len(embeddings) > 0:
            return embeddings[0].values
        else:
            raise ValueError("No embeddings returned from model")
            
    except Exception as e:
        print(f"Error generating embedding for text (length: {len(text)}): {str(e)}")
        raise


def embed_query(query: str) -> List[float]:
    """
    Generate embedding for user query (alias for embed_text for clarity)
    
    Args:
        query: User query text
        
    Returns:
        List of embedding values
    """
    return embed_text(query)


def search_documents(
    query_vector: List[float], 
    filters: Dict[str, str], 
    top_k: int = 12
) -> List[Dict[str, Any]]:
    """
    Search vector index with metadata filters
    
    Args:
        query_vector: Query embedding vector
        filters: Metadata filters (province, asset, doc_class)
        top_k: Number of results to return
        
    Returns:
        List of matching document chunks with metadata
    """
    if not query_vector:
        raise ValueError("Query vector cannot be empty")
        
    if top_k <= 0 or top_k > 100:
        raise ValueError("top_k must be between 1 and 100")
        
    try:
        project_id = os.environ.get('GOOGLE_CLOUD_PROJECT')
        region = os.environ.get('REGION', 'us-central1')
        endpoint_id = os.environ.get('VERTEX_ENDPOINT_ID')
        deployed_index_id = os.environ.get('VERTEX_DEPLOYED_INDEX_ID', 'nemo_deployed_index')

        if not all([project_id, endpoint_id]):
            missing = [var for var, val in [
                ('GOOGLE_CLOUD_PROJECT', project_id),
                ('VERTEX_ENDPOINT_ID', endpoint_id)
            ] if not val]
            raise ValueError(f"Missing required environment variables: {', '.join(missing)}")

        aiplatform.init(project=project_id, location=region)

        # Get index endpoint by full resource name
        endpoint_name = f"projects/{project_id}/locations/{region}/indexEndpoints/{endpoint_id}"
        endpoint = MatchingEngineIndexEndpoint(endpoint_name)

        # Build filter expression
        filter_expressions = []
        for key, value in filters.items():
            if value and isinstance(value, str):  # Only add non-empty string filters
                # Escape quotes in filter values
                escaped_value = value.replace('"', '\\"')
                filter_expressions.append(f'{key} = "{escaped_value}"')
                
        filter_str = " AND ".join(filter_expressions) if filter_expressions else None
        
        print(f"Vector search: top_k={top_k}, filters={filter_str}")
        
        # Perform vector search with timeout
        response = endpoint.find_neighbors(
            deployed_index_id=deployed_index_id,
            queries=[query_vector],
            num_neighbors=top_k,
            filter=filter_str
        )
        
        # Process results
        results = []
        if response and len(response) > 0:
            neighbors = response[0]
            
            for neighbor in neighbors:
                # Extract metadata and score
                result = {
                    'id': neighbor.id,
                    'distance': neighbor.distance,
                    'score': 1.0 - neighbor.distance,  # Convert distance to similarity score
                    'metadata': {},
                    'text': ''  # Will be populated from stored metadata
                }
                
                # Add metadata if available
                if hasattr(neighbor, 'restricts'):
                    for restrict in neighbor.restricts:
                        if restrict.allow_list:
                            result['metadata'][restrict.namespace] = restrict.allow_list[0]
                            
                # Add text content if available in metadata
                if 'text' in result['metadata']:
                    result['text'] = result['metadata']['text']
                        
                results.append(result)
                
        print(f"Vector search returned {len(results)} results")
        return results
        
    except Exception as e:
        print(f"Error searching vector index with filters {filters}: {str(e)}")
        raise


def upsert_chunks(chunks: List[Dict[str, Any]]) -> None:
    """
    Upsert document chunks to vector index
    
    Args:
        chunks: List of document chunks with embeddings and metadata
    """
    if not chunks:
        print("No chunks to upsert")
        return
        
    try:
        project_id = os.environ.get('GOOGLE_CLOUD_PROJECT')
        region = os.environ.get('REGION', 'us-central1')
        index_id = os.environ.get('VERTEX_INDEX_ID')
        
        if not all([project_id, index_id]):
            missing = [var for var, val in [
                ('GOOGLE_CLOUD_PROJECT', project_id),
                ('VERTEX_INDEX_ID', index_id)
            ] if not val]
            raise ValueError(f"Missing required environment variables: {', '.join(missing)}")
            
        aiplatform.init(project=project_id, location=region)

        # Get index by full resource name
        index_name = f"projects/{project_id}/locations/{region}/indexes/{index_id}"
        index = MatchingEngineIndex(index_name)
        
        # Prepare datapoints for upsert
        datapoints = []
        
        for i, chunk in enumerate(chunks):
            # Validate chunk structure
            if 'embedding' not in chunk or not chunk['embedding']:
                print(f"Warning: Chunk {i} missing embedding, skipping")
                continue
                
            # Generate unique ID for chunk
            checksum = chunk.get('metadata', {}).get('checksum', 'unknown')
            chunk_id = f"{checksum}-{chunk.get('chunk_index', i)}"
            
            # Prepare metadata restricts
            restricts = []
            metadata = chunk.get('metadata', {})
            
            # Add text content to metadata for retrieval
            if 'text' in chunk and chunk['text']:
                metadata['text'] = chunk['text']
            
            for key, value in metadata.items():
                if value is not None and str(value).strip():  # Only add non-empty metadata
                    # Limit metadata value length to prevent issues
                    str_value = str(value)
                    if len(str_value) > 1000:  # Limit metadata size
                        str_value = str_value[:1000] + "..."
                        
                    restricts.append({
                        'namespace': key,
                        'allow_list': [str_value]
                    })
            
            datapoint = {
                'datapoint_id': chunk_id,
                'feature_vector': chunk['embedding'],
                'restricts': restricts
            }
            
            datapoints.append(datapoint)
            
        # Batch upsert with error handling
        if datapoints:
            # Process in batches to avoid timeout
            batch_size = 100
            for i in range(0, len(datapoints), batch_size):
                batch = datapoints[i:i + batch_size]
                try:
                    index.upsert_datapoints(datapoints=batch)
                    print(f"Upserted batch {i//batch_size + 1}: {len(batch)} chunks")
                except Exception as batch_error:
                    print(f"Error upserting batch {i//batch_size + 1}: {str(batch_error)}")
                    # Continue with next batch
                    
            print(f"Successfully processed {len(datapoints)} chunks for upserting")
        else:
            print("No valid chunks to upsert (all chunks missing embeddings)")
        
    except Exception as e:
        print(f"Error in upsert_chunks: {str(e)}")
        raise


def get_index_status(index_id: str, endpoint_id: str) -> str:
    """
    Check the status of Vertex AI Vector Search index and endpoint
    
    Args:
        index_id: Vector search index ID
        endpoint_id: Vector search endpoint ID
        
    Returns:
        Status string
    """
    try:
        project_id = os.environ.get('GOOGLE_CLOUD_PROJECT')
        region = os.environ.get('REGION', 'us-central1')
        
        aiplatform.init(project=project_id, location=region)
        
        # Check index
        index = MatchingEngineIndex(index_id)
        index_state = index.gca_resource.state
        
        # Check endpoint
        endpoint = MatchingEngineIndexEndpoint(endpoint_id)
        endpoint_state = endpoint.gca_resource.state
        
        if index_state == 1 and endpoint_state == 1:  # DEPLOYED state
            return 'healthy'
        else:
            return f'index_state={index_state}, endpoint_state={endpoint_state}'
            
    except Exception as e:
        return f'error: {str(e)}'

def batch_embed_texts(texts: List[str], batch_size: int = 5) -> List[List[float]]:
    """
    Generate embeddings for multiple texts in batches
    
    Args:
        texts: List of texts to embed
        batch_size: Number of texts to process in each batch
        
    Returns:
        List of embedding vectors
    """
    if not texts:
        return []
        
    try:
        project_id = os.environ.get('GOOGLE_CLOUD_PROJECT')
        region = os.environ.get('REGION', 'us-central1')
        
        if not project_id:
            raise ValueError("GOOGLE_CLOUD_PROJECT environment variable not set")
            
        aiplatform.init(project=project_id, location=region)
        model = aiplatform.TextEmbeddingModel.from_pretrained("text-embedding-004")
        
        all_embeddings = []
        
        # Process in batches
        for i in range(0, len(texts), batch_size):
            batch_texts = texts[i:i + batch_size]
            
            # Filter and truncate texts
            processed_texts = []
            for text in batch_texts:
                if text and text.strip():
                    # Truncate if too long
                    if len(text) > 6000:
                        text = text[:6000]
                    processed_texts.append(text)
                else:
                    processed_texts.append("empty")  # Placeholder for empty text
                    
            # Generate embeddings for batch
            embeddings = model.get_embeddings(processed_texts)
            
            for j, embedding in enumerate(embeddings):
                if batch_texts[j] and batch_texts[j].strip():
                    all_embeddings.append(embedding.values)
                else:
                    # Return zero vector for empty text
                    all_embeddings.append([0.0] * len(embedding.values))
                    
            print(f"Generated embeddings for batch {i//batch_size + 1}/{(len(texts) + batch_size - 1)//batch_size}")
            
        return all_embeddings
        
    except Exception as e:
        print(f"Error in batch embedding: {str(e)}")
        raise


def validate_embedding_vector(vector: List[float]) -> bool:
    """
    Validate that an embedding vector is properly formatted
    
    Args:
        vector: Embedding vector to validate
        
    Returns:
        True if vector is valid
    """
    if not vector or not isinstance(vector, list):
        return False
        
    if len(vector) == 0:
        return False
        
    # Check that all elements are numbers
    for val in vector:
        if not isinstance(val, (int, float)):
            return False
        if not (-10.0 <= val <= 10.0):  # Reasonable range for embeddings
            return False
            
    return True


def create_metadata_filters(province: str = None, asset: str = None, doc_class: str = None) -> Dict[str, str]:
    """
    Create metadata filters dictionary for vector search
    
    Args:
        province: Province code (gd, sd, nm)
        asset: Asset type (solar, coal, wind)
        doc_class: Document class (grid)
        
    Returns:
        Dictionary of filters
    """
    filters = {}
    
    if province:
        filters['province'] = province
    if asset:
        filters['asset'] = asset
    if doc_class:
        filters['doc_class'] = doc_class
        
    return filters
