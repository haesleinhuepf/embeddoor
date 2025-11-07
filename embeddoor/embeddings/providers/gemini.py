"""Google Gemini embedding provider."""

import numpy as np
from typing import List

from embeddoor.embeddings.base import EmbeddingProvider


class GeminiEmbedding(EmbeddingProvider):
    """Embedding provider using Google Gemini API."""
    
    def __init__(self, model_name: str = "models/embedding-001", api_key: str = None, **kwargs):
        super().__init__(model_name, **kwargs)
        self.api_key = api_key
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize the Gemini client."""
        try:
            import google.generativeai as genai
            if self.api_key:
                genai.configure(api_key=self.api_key)
            self.genai = genai
        except ImportError:
            raise ImportError(
                "google-generativeai is required for Gemini embeddings. "
                "Install with: pip install google-generativeai"
            )
    
    def embed(self, texts: List[str]) -> np.ndarray:
        """Generate embeddings using Gemini API."""
        return self.embed_batch(texts)
    
    def embed_batch(self, texts: List[str], batch_size: int = 100) -> np.ndarray:
        """Generate embeddings in batches."""
        all_embeddings = []
        
        for text in texts:
            result = self.genai.embed_content(
                model=self.model_name,
                content=text,
                task_type="retrieval_document"
            )
            all_embeddings.append(result['embedding'])
        
        return np.array(all_embeddings)
