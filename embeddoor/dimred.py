"""Dimensionality reduction module.

This module provides a unified interface to various dimensionality reduction
techniques, using the modular implementations in the dim_red package.
"""

import numpy as np
from typing import List, Dict, Any

from embeddoor.dim_red import get_available_methods, get_method


def get_dimred_methods() -> List[Dict[str, Any]]:
    """
    Get list of available dimensionality reduction methods.
    
    Returns:
        List of dictionaries containing method information
    """
    return get_available_methods()


def apply_dimred(
    embeddings: List[List[float]],
    method: str,
    n_components: int = 2,
    **kwargs
) -> np.ndarray:
    """
    Apply dimensionality reduction to embeddings.
    
    This function serves as the main entry point for applying any dimensionality
    reduction technique. It uses the modular implementations from the dim_red package.
    
    Args:
        embeddings: List of embedding vectors
        method: Name of the method (e.g., 'pca', 'tsne', 'umap')
        n_components: Number of components to reduce to
        **kwargs: Additional method-specific parameters
    
    Returns:
        numpy array of shape (n_samples, n_components) with reduced dimensions
    
    Raises:
        ValueError: If method name is not recognized
        ImportError: If required dependencies are not installed (e.g., umap-learn)
    """
    # Get the appropriate method instance
    method_instance = get_method(method)
    
    # Apply the dimensionality reduction
    reduced = method_instance.apply(embeddings, n_components, **kwargs)
    
    return reduced
