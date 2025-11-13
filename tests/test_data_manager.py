"""Tests for data_manager module."""

import pytest
import pandas as pd
import numpy as np
from pathlib import Path
import tempfile

from embeddoor.data_manager import DataManager


@pytest.fixture
def data_manager():
    """Create a DataManager instance."""
    return DataManager()


@pytest.fixture
def sample_df():
    """Create a sample dataframe."""
    return pd.DataFrame({
        'a': [1, 2, 3, 4, 5],
        'b': [2.0, 4.0, 6.0, 8.0, 10.0],
        'c': ['x', 'y', 'z', 'x', 'y']
    })


def test_load_csv(data_manager, sample_df, tmp_path):
    """Test loading a CSV file."""
    csv_file = tmp_path / "test.csv"
    sample_df.to_csv(csv_file, index=False)
    
    result = data_manager.load_csv(str(csv_file))
    
    assert result['success'] is True
    assert result['shape'] == (5, 3)
    assert len(result['columns']) == 3


def test_save_parquet(data_manager, sample_df, tmp_path):
    """Test saving to Parquet."""
    data_manager.df = sample_df
    parquet_file = tmp_path / "test.parquet"
    
    result = data_manager.save_parquet(str(parquet_file))
    
    assert result['success'] is True
    assert parquet_file.exists()


def test_get_data_info(data_manager, sample_df):
    """Test getting data info."""
    data_manager.df = sample_df
    
    info = data_manager.get_data_info()
    
    assert info['loaded'] is True
    assert info['shape'] == (5, 3)
    assert len(info['numeric_columns']) == 2
    assert len(info['categorical_columns']) == 1


def test_add_selection_column(data_manager, sample_df):
    """Test adding a selection column."""
    data_manager.df = sample_df
    
    result = data_manager.add_selection_column('selected', [0, 2, 4])
    
    assert result['success'] is True
    assert 'selected' in data_manager.df.columns
    assert data_manager.df['selected'].sum() == 3


def test_add_embedding_column(data_manager, sample_df):
    """Test adding an embedding column."""
    data_manager.df = sample_df
    embeddings = np.random.randn(5, 10)
    
    result = data_manager.add_embedding_column('embedding', embeddings)
    
    assert result['success'] is True
    assert 'embedding' in data_manager.df.columns


def test_add_dimred_columns(data_manager, sample_df):
    """Test adding dimensionality-reduced columns."""
    data_manager.df = sample_df
    reduced = np.random.randn(5, 2)
    
    result = data_manager.add_dimred_columns('pca', reduced)
    
    assert result['success'] is True
    assert 'pca_1' in data_manager.df.columns
    assert 'pca_2' in data_manager.df.columns


def test_store_selection(data_manager, sample_df):
    """Test storing a selection."""
    data_manager.df = sample_df
    data_manager.df['selection'] = [True, False, True, False, True]
    
    result = data_manager.store_selection('test_selection')
    
    assert result['success'] is True
    assert result['name'] == 'test_selection'
    assert 'selection_test_selection' in data_manager.df.columns
    assert data_manager.df['selection_test_selection'].sum() == 3


def test_restore_selection(data_manager, sample_df):
    """Test restoring a selection."""
    data_manager.df = sample_df
    data_manager.df['selection'] = [True, False, True, False, True]
    data_manager.store_selection('saved')
    
    # Change the selection
    data_manager.df['selection'] = [False, True, False, True, False]
    
    # Restore the original selection
    result = data_manager.restore_selection('saved')
    
    assert result['success'] is True
    assert result['name'] == 'saved'
    assert data_manager.df['selection'].sum() == 3
    assert data_manager.df.loc[0, 'selection'] is True
    assert data_manager.df.loc[1, 'selection'] is False


def test_get_stored_selections(data_manager, sample_df):
    """Test getting list of stored selections."""
    data_manager.df = sample_df
    data_manager.df['selection'] = [True, False, True, False, True]
    
    # Store multiple selections
    data_manager.store_selection('first')
    data_manager.store_selection('second')
    data_manager.store_selection('third')
    
    result = data_manager.get_stored_selections()
    
    assert result['success'] is True
    assert len(result['selections']) == 3
    assert 'first' in result['selections']
    assert 'second' in result['selections']
    assert 'third' in result['selections']


def test_store_selection_no_selection_column(data_manager, sample_df):
    """Test storing selection when no selection column exists."""
    data_manager.df = sample_df
    
    result = data_manager.store_selection('test')
    
    assert result['success'] is False
    assert 'No selection column found' in result['error']


def test_restore_selection_not_found(data_manager, sample_df):
    """Test restoring a non-existent selection."""
    data_manager.df = sample_df
    
    result = data_manager.restore_selection('nonexistent')
    
    assert result['success'] is False
    assert 'not found' in result['error']
