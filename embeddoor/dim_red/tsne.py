"""t-SNE (t-distributed Stochastic Neighbor Embedding) dimensionality reduction."""

from typing import Dict, Any, List
import numpy as np
from sklearn.manifold import TSNE

from .base import DimRedMethod


class TSNEMethod(DimRedMethod):
    """t-SNE dimensionality reduction implementation."""
    
    def get_info(self) -> Dict[str, Any]:
        """Get information about t-SNE method."""
        return {
            'name': 'tsne',
            'display_name': 't-SNE (t-distributed Stochastic Neighbor Embedding)',
            'description': 'Non-linear dimensionality reduction technique particularly well-suited '
                          'for visualizing high-dimensional data by preserving local structure.',
            'parameters': {
                'n_components': {
                    'type': 'int',
                    'default': 2,
                    'min': 1,
                    'max': 3,
                    'description': 'Number of dimensions for the embedding (typically 2 or 3)'
                },
                'perplexity': {
                    'type': 'float',
                    'default': 30.0,
                    'min': 5.0,
                    'max': 50.0,
                    'description': 'Balance between local and global structure (typical: 5-50)'
                },
                'learning_rate': {
                    'type': 'float',
                    'default': 200.0,
                    'min': 10.0,
                    'max': 1000.0,
                    'description': 'Learning rate for optimization (typical: 10-1000)'
                },
                'max_iter': {
                    'type': 'int',
                    'default': 1000,
                    'min': 250,
                    'max': 5000,
                    'description': 'Maximum number of iterations for optimization'
                }
            }
        }
    
    def apply(
        self,
        embeddings: List[List[float]],
        n_components: int = 2,
        **kwargs
    ) -> np.ndarray:
        """
        Apply t-SNE to embeddings.
        
        Args:
            embeddings: List of embedding vectors
            n_components: Number of dimensions (default: 2, max: 3)
            perplexity: Balance between local and global structure (default: 30.0)
            learning_rate: Learning rate for optimization (default: 200.0)
            max_iter: Maximum number of optimization iterations (default: 1000)
            **kwargs: Additional parameters
        
        Returns:
            numpy array of shape (n_samples, n_components) with reduced dimensions
        """
        # Validate and convert to numpy array
        X = self._validate_embeddings(embeddings)
        
        # Validate n_components (t-SNE typically works best with 2 or 3)
        self._validate_n_components(n_components, X.shape[1], max_allowed=3)
        
        # Extract parameters with defaults
        perplexity = kwargs.get('perplexity', 30.0)
        learning_rate = kwargs.get('learning_rate', 200.0)
        max_iter = kwargs.get('max_iter', 1000)
        
        # Validate perplexity based on sample size
        max_perplexity = (X.shape[0] - 1) / 3.0
        if perplexity >= max_perplexity:
            perplexity = max(5.0, max_perplexity - 1.0)
        
        # Apply t-SNE
        tsne = TSNE(
            n_components=n_components,
            perplexity=perplexity,
            learning_rate=learning_rate,
            max_iter=max_iter,
            random_state=42
        )
        reduced = tsne.fit_transform(X)
        
        return reduced
