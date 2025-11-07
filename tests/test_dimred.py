"""Tests for dimensionality reduction."""

import pytest
import numpy as np

from embeddoor.dimred import get_dimred_methods, apply_dimred


def test_get_dimred_methods():
    """Test getting available methods."""
    methods = get_dimred_methods()
    
    assert len(methods) > 0
    method_names = [m['name'] for m in methods]
    assert 'pca' in method_names
    assert 'tsne' in method_names
    assert 'umap' in method_names


def test_apply_pca():
    """Test PCA dimensionality reduction."""
    embeddings = np.random.randn(100, 50)
    
    reduced = apply_dimred(embeddings.tolist(), 'pca', n_components=2)
    
    assert reduced.shape == (100, 2)


def test_apply_tsne():
    """Test t-SNE dimensionality reduction."""
    embeddings = np.random.randn(50, 20)
    
    reduced = apply_dimred(embeddings.tolist(), 'tsne', n_components=2)
    
    assert reduced.shape == (50, 2)


@pytest.mark.skipif(True, reason="UMAP requires additional dependencies")
def test_apply_umap():
    """Test UMAP dimensionality reduction."""
    embeddings = np.random.randn(100, 30)
    
    reduced = apply_dimred(embeddings.tolist(), 'umap', n_components=2)
    
    assert reduced.shape == (100, 2)
