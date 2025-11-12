"""Data management for embeddoor."""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Optional, List, Dict, Any


class DataManager:
    """Manages the current dataframe and operations on it."""
    
    def __init__(self):
        self.df: Optional[pd.DataFrame] = None
        self.current_file: Optional[str] = None
        self.history: List[Dict[str, Any]] = []
    
    def load_csv(self, filepath: str) -> Dict[str, Any]:
        """Load a CSV file."""
        try:
            self.df = pd.read_csv(filepath)
            self.current_file = filepath
            return {
                'success': True,
                'shape': self.df.shape,
                'columns': list(self.df.columns),
                'numeric_columns': list(self.df.select_dtypes(include=[np.float64, np.float32, np.int32, np.int64]).columns),
                'dtypes': {col: str(dtype) for col, dtype in self.df.dtypes.items()}
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def load_parquet(self, filepath: str) -> Dict[str, Any]:
        """Load a Parquet file."""
        try:
            print("loading", filepath)
            self.df = pd.read_parquet(filepath)
            print("loaded", self.df.head())
            
            self.current_file = filepath
            return {
                'success': True,
                'shape': self.df.shape,
                'columns': list(self.df.columns),
                'numeric_columns': list(self.df.select_dtypes(include=[np.float64, np.float32, np.int32, np.int64]).columns),
                'dtypes': {col: str(dtype) for col, dtype in self.df.dtypes.items()}
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def load_huggingface(self, dataset_name: str, split: Optional[str] = None) -> Dict[str, Any]:
        """Load a dataset from Huggingface."""
        try:
            from datasets import load_dataset
            
            print(f"Loading dataset from Huggingface: {dataset_name}")
            
            # Load the dataset
            if split:
                dataset = load_dataset(dataset_name, split=split)
            else:
                # Load all splits and use the first one
                dataset = load_dataset(dataset_name)
                # If it's a DatasetDict, get the first split
                if hasattr(dataset, 'keys'):
                    split_name = list(dataset.keys())[0]
                    dataset = dataset[split_name]
                    print(f"Using split: {split_name}")
            
            # Convert to pandas DataFrame
            self.df = dataset.to_pandas()
            print(f"Loaded dataset with shape: {self.df.shape}")
            
            self.current_file = f"huggingface:{dataset_name}"
            
            return {
                'success': True,
                'shape': self.df.shape,
                'columns': list(self.df.columns),
                'numeric_columns': list(self.df.select_dtypes(include=[np.float64, np.float32, np.int32, np.int64]).columns),
                'dtypes': {col: str(dtype) for col, dtype in self.df.dtypes.items()}
            }
        except ImportError:
            return {'success': False, 'error': 'The datasets library is not installed. Please install it with: pip install datasets'}
        except Exception as e:
            return {'success': False, 'error': f'Error loading dataset: {str(e)}'}
    
    def save_parquet(self, filepath: str) -> Dict[str, Any]:
        """Save the current dataframe to Parquet."""
        if self.df is None:
            return {'success': False, 'error': 'No data loaded'}
        
        try:
            self.df.to_parquet(filepath, index=False)
            return {'success': True, 'filepath': filepath}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def save_csv(self, filepath: str) -> Dict[str, Any]:
        """Save the current dataframe to CSV."""
        if self.df is None:
            return {'success': False, 'error': 'No data loaded'}
        
        try:
            self.df.to_csv(filepath, index=False)
            return {'success': True, 'filepath': filepath}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_data_info(self) -> Dict[str, Any]:
        """Get information about the current dataframe."""
        if self.df is None:
            return {'loaded': False}
        
        return {
            'loaded': True,
            'shape': self.df.shape,
            'columns': list(self.df.columns),
            'dtypes': {col: str(dtype) for col, dtype in self.df.dtypes.items()},
            'numeric_columns': list(self.df.select_dtypes(include=[np.number]).columns),
            'categorical_columns': list(self.df.select_dtypes(include=['object', 'category']).columns),
        }
    
    def get_data_sample(self, n: int = 100) -> Optional[Dict]:
        """Get a sample of the data for display."""
        if self.df is None:
            return None
        
        sample_df = self.df.head(n)
        return {
            'data': sample_df.to_dict(orient='records'),
            'columns': list(sample_df.columns)
        }
    
    def get_plot_data(self, x_col: str, y_col: Optional[str] = None, 
                     z_col: Optional[str] = None, hue_col: Optional[str] = None,
                     size_col: Optional[str] = None) -> Optional[Dict]:
        """Get data formatted for plotting."""
        if self.df is None:
            return None
        
        # Start with x column
        columns = [x_col]
        if y_col:
            columns.append(y_col)
        if z_col:
            columns.append(z_col)
        if hue_col and hue_col not in columns:
            columns.append(hue_col)
        if size_col and size_col not in columns:
            columns.append(size_col)
        
        # Include 'selection' column if it exists
        if 'selection' in self.df.columns and 'selection' not in columns:
            columns.append('selection')
        
        # Get data for these columns
        plot_df = self.df[columns].copy()
        
        # Handle missing values
        plot_df = plot_df.dropna()
        
        # Include the index in the data
        plot_df_with_index = plot_df.reset_index()
        
        return {
            'data': plot_df_with_index.to_dict(orient='records'),
            'columns': columns
        }
    
    def add_selection_column(self, column_name: str, selected_indices: List[int]) -> Dict[str, Any]:
        """Add a column marking selected points."""
        if self.df is None:
            return {'success': False, 'error': 'No data loaded'}
        
        try:
            # Create selection column
            self.df[column_name] = False
            self.df.loc[selected_indices, column_name] = True
            
            return {
                'success': True,
                'column': column_name,
                'count': len(selected_indices)
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def add_embedding_column(self, column_name: str, embeddings: np.ndarray) -> Dict[str, Any]:
        """Add a column containing embeddings."""
        if self.df is None:
            return {'success': False, 'error': 'No data loaded'}
        
        try:
            # Store embeddings as a column of arrays
            self.df[column_name] = list(embeddings)
            
            return {
                'success': True,
                'column': column_name,
                'shape': embeddings.shape
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def add_dimred_columns(self, base_name: str, reduced_data: np.ndarray) -> Dict[str, Any]:
        """Add columns for dimensionality-reduced data."""
        if self.df is None:
            return {'success': False, 'error': 'No data loaded'}
        
        try:
            n_components = reduced_data.shape[1]
            column_names = [f"{base_name}_{i+1}" for i in range(n_components)]
            
            for i, col_name in enumerate(column_names):
                self.df[col_name] = reduced_data[:, i]
            
            return {
                'success': True,
                'columns': column_names,
                'n_components': n_components
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
