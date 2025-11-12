"""Dimensionality reduction modules package.

This package provides modular implementations of various dimensionality
reduction techniques.
"""

from .base import DimRedMethod
from .pca import PCAMethod
from .tsne import TSNEMethod
from .umap import UMAPMethod

# Registry of all available methods
_METHODS_REGISTRY = {
    'pca': PCAMethod,
    'tsne': TSNEMethod,
    'umap': UMAPMethod,
}


def get_available_methods():
    """Get list of all available dimensionality reduction methods."""
    return [method_cls().get_info() for method_cls in _METHODS_REGISTRY.values()]


def get_method(method_name: str) -> DimRedMethod:
    """
    Get a dimensionality reduction method by name.
    
    Args:
        method_name: Name of the method (e.g., 'pca', 'tsne', 'umap')
    
    Returns:
        Instance of the requested method
    
    Raises:
        ValueError: If method name is not recognized
    """
    method_cls = _METHODS_REGISTRY.get(method_name.lower())
    if method_cls is None:
        available = ', '.join(_METHODS_REGISTRY.keys())
        raise ValueError(f"Unknown method '{method_name}'. Available: {available}")
    return method_cls()


__all__ = [
    'DimRedMethod',
    'PCAMethod',
    'TSNEMethod',
    'UMAPMethod',
    'get_available_methods',
    'get_method',
]
