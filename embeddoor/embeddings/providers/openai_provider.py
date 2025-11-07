"""OpenAI embedding provider."""

import numpy as np
from typing import List

from embeddoor.embeddings.base import EmbeddingProvider


class OpenAIEmbedding(EmbeddingProvider):
    """Embedding provider using OpenAI API."""
    
    def __init__(self, model_name: str = "text-embedding-3-small", api_key: str = None, **kwargs):
        super().__init__(model_name, **kwargs)
        self.api_key = api_key
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize the OpenAI client."""
        try:
            from openai import OpenAI
            self.client = OpenAI(api_key=self.api_key)
        except ImportError:
            raise ImportError(
                "openai is required for OpenAI embeddings. "
                "Install with: pip install openai"
            )
    
    def embed(self, texts: List[str]) -> np.ndarray:
        """Generate embeddings using OpenAI API."""
        if self.client is None:
            raise RuntimeError("Client not initialized")
        
        # OpenAI has a limit on batch size (typically 2048)
        return self.embed_batch(texts, batch_size=100)
    
    def embed_batch(self, texts: List[str], batch_size: int = 100) -> np.ndarray:
        """Generate embeddings in batches."""
        if self.client is None:
            raise RuntimeError("Client not initialized")
        
        all_embeddings = []
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            
            response = self.client.embeddings.create(
                input=batch,
                model=self.model_name
            )
            
            batch_embeddings = [item.embedding for item in response.data]
            all_embeddings.extend(batch_embeddings)
        
        return np.array(all_embeddings)
