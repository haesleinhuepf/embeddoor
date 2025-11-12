"""PCA (Principal Component Analysis) dimensionality reduction."""

from typing import Dict, Any, List
import numpy as np
from sklearn.decomposition import PCA

from .base import DimRedMethod


class PCAMethod(DimRedMethod):
    """PCA dimensionality reduction implementation."""
    
    def get_info(self) -> Dict[str, Any]:
        """Get information about PCA method."""
        return {
            'name': 'pca',
            'display_name': 'PCA (Principal Component Analysis)',
            'description': 'Linear dimensionality reduction using Singular Value Decomposition (SVD). '
                          'Best for finding the directions of maximum variance in high-dimensional data.',
            'parameters': {
                'n_components': {
                    'type': 'int',
                    'default': 2,
                    'min': 1,
                    'max': 10,
                    'description': 'Number of principal components to compute'
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
        Apply PCA to embeddings.
        
        Args:
            embeddings: List of embedding vectors
            n_components: Number of principal components (default: 2)
            **kwargs: Additional parameters (not used for PCA)
        
        Returns:
            numpy array of shape (n_samples, n_components) with reduced dimensions
        """
        # Validate and convert to numpy array
        X = self._validate_embeddings(embeddings)
        
        # Validate n_components
        self._validate_n_components(n_components, X.shape[1])
        
        # Apply PCA
        pca = PCA(n_components=n_components, random_state=42)
        reduced = pca.fit_transform(X)
        
        return reduced
