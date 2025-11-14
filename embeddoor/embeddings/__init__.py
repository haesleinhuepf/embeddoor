"""Embedding generation module."""

import numpy as np
from typing import List, Dict, Any
from abc import ABC, abstractmethod


class EmbeddingProvider(ABC):
    """Base class for embedding providers."""
    
    def __init__(self, model_name: str, **kwargs):
        self.model_name = model_name
        self.config = kwargs
    
    @abstractmethod
    def embed(self, texts: List[str]) -> np.ndarray:
        """
        Generate embeddings for a list of texts.
        
        Args:
            texts: List of text strings
        
        Returns:
            numpy array of shape (n_texts, embedding_dim)
        """
        pass
    
    @abstractmethod
    def embed_batch(self, texts: List[str], batch_size: int = 32) -> np.ndarray:
        """
        Generate embeddings in batches.
        
        Args:
            texts: List of text strings
            batch_size: Batch size for processing
        
        Returns:
            numpy array of shape (n_texts, embedding_dim)
        """
        pass


class DummyEmbedding(EmbeddingProvider):
    """Dummy embedding provider for testing."""
    
    def __init__(self, model_name: str = "dummy", dimension: int = 128, **kwargs):
        super().__init__(model_name, **kwargs)
        self.dimension = dimension
    
    def embed(self, texts: List[str]) -> np.ndarray:
        """Generate random embeddings."""
        return np.random.randn(len(texts), self.dimension)
    
    def embed_batch(self, texts: List[str], batch_size: int = 32) -> np.ndarray:
        """Generate random embeddings in batches."""
        return self.embed(texts)


# Registry of available providers
_PROVIDERS: Dict[str, type] = {
    'dummy': DummyEmbedding,
}

# Lazy import CLIP provider to avoid import errors if transformers not installed
def _get_clip_provider():
    try:
        from .providers.clip_provider import CLIPImageEmbedder
        return CLIPImageEmbedder
    except ImportError:
        return None

# Register CLIP if available
_clip = _get_clip_provider()
if _clip:
    _PROVIDERS['clip'] = _clip


def register_provider(name: str, provider_class: type):
    """Register a new embedding provider."""
    _PROVIDERS[name] = provider_class


def get_embedding_providers() -> List[Dict[str, Any]]:
    """Get list of available embedding providers."""
    return [
        {
            'name': name,
            'class': provider.__name__,
            'description': provider.__doc__ or ''
        }
        for name, provider in _PROVIDERS.items()
    ]


def create_embeddings(texts: List[str], provider_name: str, model_name: str, **kwargs) -> np.ndarray:
    """
    Create embeddings using a specified provider.
    
    Args:
        texts: List of text strings
        provider_name: Name of the provider
        model_name: Name of the model
        **kwargs: Additional arguments for the provider
    
    Returns:
        numpy array of embeddings
    """
    if provider_name not in _PROVIDERS:
        raise ValueError(f"Unknown provider: {provider_name}")
    
    provider_class = _PROVIDERS[provider_name]
    provider = provider_class(model_name, **kwargs)
    
    return provider.embed_batch(texts)
