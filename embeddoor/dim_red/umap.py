"""UMAP (Uniform Manifold Approximation and Projection) dimensionality reduction."""

from typing import Dict, Any, List
import numpy as np

from .base import DimRedMethod


class UMAPMethod(DimRedMethod):
    """UMAP dimensionality reduction implementation."""
    
    def get_info(self) -> Dict[str, Any]:
        """Get information about UMAP method."""
        return {
            'name': 'umap',
            'display_name': 'UMAP (Uniform Manifold Approximation and Projection)',
            'description': 'Non-linear dimensionality reduction that preserves both local and global '
                          'structure better than t-SNE. Faster than t-SNE and scales better to large datasets.',
            'parameters': {
                'n_components': {
                    'type': 'int',
                    'default': 2,
                    'min': 1,
                    'max': 10,
                    'description': 'Number of dimensions for the embedding'
                },
                'n_neighbors': {
                    'type': 'int',
                    'default': 15,
                    'min': 2,
                    'max': 200,
                    'description': 'Size of local neighborhood (larger = more global structure)'
                },
                'min_dist': {
                    'type': 'float',
                    'default': 0.1,
                    'min': 0.0,
                    'max': 0.99,
                    'description': 'Minimum distance between points in low-dimensional space'
                },
                'metric': {
                    'type': 'str',
                    'default': 'euclidean',
                    'options': ['euclidean', 'cosine', 'manhattan', 'chebyshev', 'minkowski'],
                    'description': 'Distance metric to use in high-dimensional space'
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
        Apply UMAP to embeddings.
        
        Args:
            embeddings: List of embedding vectors
            n_components: Number of dimensions (default: 2)
            n_neighbors: Size of local neighborhood (default: 15)
            min_dist: Minimum distance between points (default: 0.1)
            metric: Distance metric (default: 'euclidean')
            **kwargs: Additional parameters
        
        Returns:
            numpy array of shape (n_samples, n_components) with reduced dimensions
        
        Raises:
            ImportError: If umap-learn is not installed
        """
        # Try to import UMAP
        try:
            from umap import UMAP
        except ImportError:
            raise ImportError(
                "umap-learn is required for UMAP dimensionality reduction. "
                "Install it with: pip install umap-learn"
            )
        
        # Validate and convert to numpy array
        X = self._validate_embeddings(embeddings)
        
        # Validate n_components
        self._validate_n_components(n_components, X.shape[1])
        
        # Extract parameters with defaults
        n_neighbors = kwargs.get('n_neighbors', 15)
        min_dist = kwargs.get('min_dist', 0.1)
        metric = kwargs.get('metric', 'euclidean')
        
        # Validate n_neighbors based on sample size
        if n_neighbors >= X.shape[0]:
            n_neighbors = max(2, X.shape[0] - 1)
        
        # Apply UMAP
        umap_reducer = UMAP(
            n_components=n_components,
            n_neighbors=n_neighbors,
            min_dist=min_dist,
            metric=metric,
            random_state=42
        )
        reduced = umap_reducer.fit_transform(X)
        
        return reduced
