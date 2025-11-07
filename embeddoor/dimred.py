"""Dimensionality reduction module."""

import numpy as np
from typing import List, Dict, Any
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE


def get_dimred_methods() -> List[Dict[str, Any]]:
    """Get list of available dimensionality reduction methods."""
    return [
        {
            'name': 'pca',
            'display_name': 'PCA (Principal Component Analysis)',
            'description': 'Linear dimensionality reduction using SVD',
            'parameters': {
                'n_components': {'type': 'int', 'default': 2, 'min': 1, 'max': 10}
            }
        },
        {
            'name': 'tsne',
            'display_name': 't-SNE (t-distributed Stochastic Neighbor Embedding)',
            'description': 'Non-linear dimensionality reduction for visualization',
            'parameters': {
                'n_components': {'type': 'int', 'default': 2, 'min': 1, 'max': 3},
                'perplexity': {'type': 'float', 'default': 30.0, 'min': 5.0, 'max': 50.0},
                'learning_rate': {'type': 'float', 'default': 200.0, 'min': 10.0, 'max': 1000.0},
                'n_iter': {'type': 'int', 'default': 1000, 'min': 250, 'max': 5000}
            }
        },
        {
            'name': 'umap',
            'display_name': 'UMAP (Uniform Manifold Approximation and Projection)',
            'description': 'Non-linear dimensionality reduction preserving global structure',
            'parameters': {
                'n_components': {'type': 'int', 'default': 2, 'min': 1, 'max': 10},
                'n_neighbors': {'type': 'int', 'default': 15, 'min': 2, 'max': 200},
                'min_dist': {'type': 'float', 'default': 0.1, 'min': 0.0, 'max': 0.99},
                'metric': {'type': 'str', 'default': 'euclidean', 'options': ['euclidean', 'cosine', 'manhattan']}
            }
        }
    ]


def apply_dimred(
    embeddings: List[List[float]],
    method: str,
    n_components: int = 2,
    **kwargs
) -> np.ndarray:
    """
    Apply dimensionality reduction to embeddings.
    
    Args:
        embeddings: List of embedding vectors
        method: Name of the method ('pca', 'tsne', 'umap')
        n_components: Number of components to reduce to
        **kwargs: Additional parameters for the method
    
    Returns:
        numpy array of shape (n_samples, n_components)
    """
    # Convert to numpy array
    X = np.array(embeddings)
    
    if method == 'pca':
        reducer = PCA(n_components=n_components)
        reduced = reducer.fit_transform(X)
    
    elif method == 'tsne':
        perplexity = kwargs.get('perplexity', 30.0)
        learning_rate = kwargs.get('learning_rate', 200.0)
        n_iter = kwargs.get('n_iter', 1000)
        
        reducer = TSNE(
            n_components=n_components,
            perplexity=perplexity,
            learning_rate=learning_rate,
            n_iter=n_iter,
            random_state=42
        )
        reduced = reducer.fit_transform(X)
    
    elif method == 'umap':
        try:
            from umap import UMAP
        except ImportError:
            raise ImportError(
                "umap-learn is required for UMAP. "
                "Install with: pip install umap-learn"
            )
        
        n_neighbors = kwargs.get('n_neighbors', 15)
        min_dist = kwargs.get('min_dist', 0.1)
        metric = kwargs.get('metric', 'euclidean')
        
        reducer = UMAP(
            n_components=n_components,
            n_neighbors=n_neighbors,
            min_dist=min_dist,
            metric=metric,
            random_state=42
        )
        reduced = reducer.fit_transform(X)
    
    else:
        raise ValueError(f"Unknown dimensionality reduction method: {method}")
    
    return reduced
