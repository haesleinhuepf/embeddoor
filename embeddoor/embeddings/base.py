"""Base classes for embedding providers."""

from abc import ABC, abstractmethod
import numpy as np
from typing import List


class EmbeddingProvider(ABC):
    """Base class for all embedding providers."""
    
    def __init__(self, model_name: str, **kwargs):
        """
        Initialize the embedding provider.
        
        Args:
            model_name: Name of the model to use
            **kwargs: Additional configuration parameters
        """
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
    
    def embed_batch(self, texts: List[str], batch_size: int = 32) -> np.ndarray:
        """
        Generate embeddings in batches.
        
        Args:
            texts: List of text strings
            batch_size: Batch size for processing
        
        Returns:
            numpy array of shape (n_texts, embedding_dim)
        """
        # Default implementation: process all at once
        # Override in subclasses for true batching
        return self.embed(texts)
