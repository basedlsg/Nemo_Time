"""
Model Functions for RAG-Anything Integration
Provides LLM, embedding, and vision model functions
"""

import os
import asyncio
from typing import List, Dict, Any, Optional, Callable
import openai
from openai import AsyncOpenAI


def create_llm_model_func(provider: str = "openai") -> Callable:
    """
    Create LLM model function for RAG-Anything
    
    Args:
        provider: LLM provider (openai, anthropic, etc.)
        
    Returns:
        Async LLM function compatible with RAG-Anything
    """
    
    if provider.lower() == "openai":
        return create_openai_llm_func()
    else:
        raise ValueError(f"Unsupported LLM provider: {provider}")


def create_embedding_func(provider: str = "openai") -> Callable:
    """
    Create embedding function for RAG-Anything
    
    Args:
        provider: Embedding provider
        
    Returns:
        Async embedding function compatible with RAG-Anything
    """
    
    if provider.lower() == "openai":
        return create_openai_embedding_func()
    else:
        raise ValueError(f"Unsupported embedding provider: {provider}")


def create_vision_model_func(provider: str = "openai") -> Callable:
    """
    Create vision model function for RAG-Anything
    
    Args:
        provider: Vision model provider
        
    Returns:
        Async vision function compatible with RAG-Anything
    """
    
    if provider.lower() == "openai":
        return create_openai_vision_func()
    else:
        raise ValueError(f"Unsupported vision provider: {provider}")


def create_openai_llm_func() -> Callable:
    """Create OpenAI LLM function optimized for Chinese regulatory documents"""
    
    # Get API key from environment
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable not set")
    
    client = AsyncOpenAI(api_key=api_key)
    
    async def openai_llm_func(
        prompt: str,
        system_prompt: Optional[str] = None,
        history_messages: Optional[List[Dict[str, str]]] = None,
        **kwargs
    ) -> str:
        """
        OpenAI LLM function with Chinese language optimization
        
        Args:
            prompt: User prompt
            system_prompt: System prompt
            history_messages: Conversation history
            **kwargs: Additional parameters
            
        Returns:
            Generated response text
        """
        try:
            # Build messages
            messages = []
            
            # Add system prompt with Chinese optimization
            if system_prompt:
                enhanced_system_prompt = f"""
                {system_prompt}
                
                Additional instructions for Chinese regulatory documents:
                - Respond in Chinese when the input is in Chinese
                - Maintain formal regulatory language style
                - Preserve technical terms and legal references
                - Use proper Chinese punctuation and formatting
                """
                messages.append({"role": "system", "content": enhanced_system_prompt})
            
            # Add history messages
            if history_messages:
                messages.extend(history_messages)
            
            # Add current prompt
            messages.append({"role": "user", "content": prompt})
            
            # Get model parameters
            model = kwargs.get("model", "gpt-4o-mini")
            max_tokens = kwargs.get("max_tokens", 2000)
            temperature = kwargs.get("temperature", 0.1)  # Lower for regulatory consistency
            
            # Make API call
            response = await client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=0.9,
                frequency_penalty=0.0,
                presence_penalty=0.0
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"Error in OpenAI LLM function: {str(e)}")
            return f"Error generating response: {str(e)}"
    
    return openai_llm_func


def create_openai_embedding_func() -> Callable:
    """Create OpenAI embedding function optimized for Chinese text"""
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable not set")
    
    client = AsyncOpenAI(api_key=api_key)
    
    async def openai_embedding_func(texts: List[str]) -> List[List[float]]:
        """
        OpenAI embedding function for Chinese regulatory text
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embedding vectors
        """
        try:
            # Use text-embedding-3-small for better Chinese support
            model = "text-embedding-3-small"
            
            # Process in batches to avoid rate limits
            batch_size = 100
            all_embeddings = []
            
            for i in range(0, len(texts), batch_size):
                batch = texts[i:i + batch_size]
                
                response = await client.embeddings.create(
                    model=model,
                    input=batch,
                    encoding_format="float"
                )
                
                batch_embeddings = [item.embedding for item in response.data]
                all_embeddings.extend(batch_embeddings)
            
            return all_embeddings
            
        except Exception as e:
            print(f"Error in OpenAI embedding function: {str(e)}")
            # Return zero embeddings as fallback
            return [[0.0] * 1536 for _ in texts]
    
    return openai_embedding_func


def create_openai_vision_func() -> Callable:
    """Create OpenAI vision function for processing images in regulatory documents"""
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable not set")
    
    client = AsyncOpenAI(api_key=api_key)
    
    async def openai_vision_func(
        image_data: str,  # Base64 encoded image
        prompt: str = "Describe this image in detail, focusing on any text, tables, or technical diagrams.",
        **kwargs
    ) -> str:
        """
        OpenAI vision function for regulatory document images
        
        Args:
            image_data: Base64 encoded image data
            prompt: Description prompt
            **kwargs: Additional parameters
            
        Returns:
            Image description text
        """
        try:
            # Enhanced prompt for regulatory documents
            enhanced_prompt = f"""
            {prompt}
            
            This image is from a Chinese regulatory document. Please:
            1. Extract any Chinese text visible in the image
            2. Describe any tables, charts, or technical diagrams
            3. Identify regulatory elements like article numbers, sections, or legal references
            4. Maintain the original Chinese text formatting and terminology
            5. Note any technical specifications, measurements, or formulas
            """
            
            messages = [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": enhanced_prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_data}",
                                "detail": "high"
                            }
                        }
                    ]
                }
            ]
            
            response = await client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                max_tokens=1000,
                temperature=0.1
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"Error in OpenAI vision function: {str(e)}")
            return f"Error processing image: {str(e)}"
    
    return openai_vision_func


# Alternative model functions for different providers can be added here

def create_anthropic_llm_func() -> Callable:
    """Create Anthropic Claude LLM function (placeholder for future implementation)"""
    raise NotImplementedError("Anthropic integration not yet implemented")


def create_local_llm_func(model_path: str) -> Callable:
    """Create local LLM function (placeholder for future implementation)"""
    raise NotImplementedError("Local LLM integration not yet implemented")


# Utility functions for model configuration

def get_available_providers() -> Dict[str, List[str]]:
    """Get list of available model providers and their capabilities"""
    return {
        "llm": ["openai"],
        "embedding": ["openai"],
        "vision": ["openai"]
    }


def validate_model_configuration(
    llm_provider: str,
    embedding_provider: str,
    vision_provider: str
) -> Dict[str, Any]:
    """
    Validate model configuration
    
    Args:
        llm_provider: LLM provider name
        embedding_provider: Embedding provider name
        vision_provider: Vision provider name
        
    Returns:
        Validation result dictionary
    """
    available = get_available_providers()
    
    issues = []
    
    if llm_provider not in available["llm"]:
        issues.append(f"Unsupported LLM provider: {llm_provider}")
    
    if embedding_provider not in available["embedding"]:
        issues.append(f"Unsupported embedding provider: {embedding_provider}")
    
    if vision_provider not in available["vision"]:
        issues.append(f"Unsupported vision provider: {vision_provider}")
    
    # Check API keys for OpenAI
    if "openai" in [llm_provider, embedding_provider, vision_provider]:
        if not os.getenv("OPENAI_API_KEY"):
            issues.append("OPENAI_API_KEY environment variable not set")
    
    return {
        "valid": len(issues) == 0,
        "issues": issues,
        "providers": {
            "llm": llm_provider,
            "embedding": embedding_provider,
            "vision": vision_provider
        }
    }