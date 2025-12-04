"""HuggingFace embedding provider."""

import numpy as np
from typing import List

from embeddoor.embeddings.base import EmbeddingProvider


class HuggingFaceEmbedding(EmbeddingProvider):
    """Embedding provider using HuggingFace models."""
    
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2", **kwargs):
        if model_name == "default":
            model_name = "sentence-transformers/all-MiniLM-L6-v2"
        super().__init__(model_name, **kwargs)
        self.model = None
        self._initialize_model()
    
    def _initialize_model(self):
        """Initialize the HuggingFace model."""
        try:
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer(self.model_name)
        except ImportError:
            raise ImportError(
                "sentence-transformers is required for HuggingFace embeddings. "
                "Install with: pip install sentence-transformers"
            )
    
    def embed(self, texts: List[str]) -> np.ndarray:
        """Generate embeddings using the HuggingFace model."""
        if self.model is None:
            raise RuntimeError("Model not initialized")
        
        embeddings = self.model.encode(texts, show_progress_bar=True)
        return np.array(embeddings)
    
    def embed_batch(self, texts: List[str], batch_size: int = 32) -> np.ndarray:
        """Generate embeddings in batches."""
        if self.model is None:
            raise RuntimeError("Model not initialized")
        
        embeddings = self.model.encode(
            texts,
            batch_size=batch_size,
            show_progress_bar=True
        )
        return np.array(embeddings)
