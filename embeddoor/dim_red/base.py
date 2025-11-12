"""Base class for dimensionality reduction methods."""

from abc import ABC, abstractmethod
from typing import Dict, Any, List
import numpy as np


class DimRedMethod(ABC):
    """Abstract base class for dimensionality reduction methods."""
    
    @abstractmethod
    def get_info(self) -> Dict[str, Any]:
        """
        Get information about the dimensionality reduction method.
        
        Returns:
            Dictionary containing:
                - name: str - Internal name of the method
                - display_name: str - Human-readable name
                - description: str - Brief description
                - parameters: dict - Parameter definitions with types and defaults
        """
        pass
    
    @abstractmethod
    def apply(
        self,
        embeddings: List[List[float]],
        n_components: int = 2,
        **kwargs
    ) -> np.ndarray:
        """
        Apply dimensionality reduction to embeddings.
        
        Args:
            embeddings: List of embedding vectors
            n_components: Number of components to reduce to
            **kwargs: Additional method-specific parameters
        
        Returns:
            numpy array of shape (n_samples, n_components)
        """
        pass
    
    def _validate_embeddings(self, embeddings: List[List[float]]) -> np.ndarray:
        """
        Validate and convert embeddings to numpy array.
        
        Args:
            embeddings: List of embedding vectors
        
        Returns:
            numpy array of embeddings
        
        Raises:
            ValueError: If embeddings are invalid
        """
        if not embeddings:
            raise ValueError("Embeddings list is empty")
        
        X = np.array(embeddings)
        
        if X.ndim != 2:
            raise ValueError(f"Expected 2D array, got {X.ndim}D array")
        
        if X.shape[0] < 2:
            raise ValueError(f"Need at least 2 samples, got {X.shape[0]}")
        
        return X
    
    def _validate_n_components(self, n_components: int, n_features: int, max_allowed: int = None):
        """
        Validate the number of components.
        
        Args:
            n_components: Requested number of components
            n_features: Number of features in the data
            max_allowed: Maximum allowed components (method-specific)
        
        Raises:
            ValueError: If n_components is invalid
        """
        if n_components < 1:
            raise ValueError(f"n_components must be >= 1, got {n_components}")
        
        if n_components > n_features:
            raise ValueError(
                f"n_components ({n_components}) cannot be greater than "
                f"number of features ({n_features})"
            )
        
        if max_allowed is not None and n_components > max_allowed:
            raise ValueError(
                f"n_components ({n_components}) cannot be greater than "
                f"{max_allowed} for this method"
            )
