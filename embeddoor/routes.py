"""Route registration for embeddoor."""

from flask import jsonify, request, send_file
import json
from pathlib import Path
import tkinter as tk
from tkinter import filedialog
import pandas as pd

from embeddoor.embeddings import get_embedding_providers, create_embeddings
from embeddoor.dimred import get_dimred_methods, apply_dimred
from embeddoor.views import register_all_views


def register_routes(app):
    """Register all application routes."""
    
    # Register modular view routes
    register_all_views(app)
    
    @app.route('/api/dialog/open-file', methods=['GET'])
    def open_file_dialog():
        """Show native OS file dialog to select a file."""
        try:
            # Create a temporary root window (hidden)
            root = tk.Tk()
            root.withdraw()
            root.wm_attributes('-topmost', 1)
            
            # Show file dialog
            filepath = filedialog.askopenfilename(
                title='Open Data File',
                filetypes=[
                    ('All supported files', '*.csv *.parquet'),
                    ('CSV files', '*.csv'),
                    ('Parquet files', '*.parquet'),
                    ('All files', '*.*')
                ]
            )
            
            # Clean up
            root.destroy()
            
            if filepath:
                return jsonify({'success': True, 'filepath': filepath})
            else:
                return jsonify({'success': False, 'cancelled': True})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/dialog/save-file', methods=['POST'])
    def save_file_dialog():
        """Show native OS file dialog to select save location."""
        try:
            data = request.json
            format_type = data.get('format', 'parquet')
            
            # Create a temporary root window (hidden)
            root = tk.Tk()
            root.withdraw()
            root.wm_attributes('-topmost', 1)
            
            # Show save dialog
            if format_type == 'csv':
                filetypes = [('CSV files', '*.csv'), ('All files', '*.*')]
                default_ext = '.csv'
            else:
                filetypes = [('Parquet files', '*.parquet'), ('All files', '*.*')]
                default_ext = '.parquet'
            
            filepath = filedialog.asksaveasfilename(
                title='Save Data File',
                filetypes=filetypes,
                defaultextension=default_ext
            )
            
            # Clean up
            root.destroy()
            
            if filepath:
                return jsonify({'success': True, 'filepath': filepath})
            else:
                return jsonify({'success': False, 'cancelled': True})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/data/load', methods=['POST'])
    def load_data():
        """Load data from a file."""
        data = request.json
        filepath = data.get('filepath')
        
        if not filepath:
            return jsonify({'success': False, 'error': 'No filepath provided'}), 400
        
        filepath = Path(filepath)
        if not filepath.exists():
            return jsonify({'success': False, 'error': 'File not found'}), 404
        
        # Determine file type and load
        if filepath.suffix.lower() == '.csv':
            result = app.data_manager.load_csv(str(filepath))
        elif filepath.suffix.lower() == '.parquet':
            result = app.data_manager.load_parquet(str(filepath))
        else:
            return jsonify({'success': False, 'error': 'Unsupported file type'}), 400

        print("Data loaded successfully:", result)

        return jsonify(result)
    
    @app.route('/api/data/load-huggingface', methods=['POST'])
    def load_huggingface():
        """Load data from a Huggingface dataset."""
        data = request.json
        dataset_name = data.get('dataset_name')
        split = data.get('split')
        
        if not dataset_name:
            return jsonify({'success': False, 'error': 'No dataset name provided'}), 400
        
        result = app.data_manager.load_huggingface(dataset_name, split)
        
        if result.get('success'):
            print("Huggingface dataset loaded successfully:", result)
        
        return jsonify(result)
    
    @app.route('/api/data/save', methods=['POST'])
    def save_data():
        """Save data to a file."""
        data = request.json
        filepath = data.get('filepath')
        format_type = data.get('format', 'parquet')
        
        if not filepath:
            return jsonify({'success': False, 'error': 'No filepath provided'}), 400
        
        if format_type == 'parquet':
            result = app.data_manager.save_parquet(filepath)
        elif format_type == 'csv':
            result = app.data_manager.save_csv(filepath)
        else:
            return jsonify({'success': False, 'error': 'Unsupported format'}), 400
        
        return jsonify(result)
    
    @app.route('/api/data/info', methods=['GET'])
    def get_data_info():
        """Get information about the current dataset."""
        info = app.data_manager.get_data_info()
        return jsonify(info)
    
    @app.route('/api/data/sample', methods=['GET'])
    def get_data_sample():
        """Get a sample of the current data."""
        n = request.args.get('n', default=100, type=int)
        sample = app.data_manager.get_data_sample(n)
        
        if sample is None:
            return jsonify({'error': 'No data loaded'}), 404
        
        return jsonify(sample)


    @app.route('/api/embeddings/providers', methods=['GET'])
    def list_embedding_providers():
        """List available embedding providers."""
        providers = get_embedding_providers()
        return jsonify({'providers': providers})
    
    @app.route('/api/embeddings/create', methods=['POST'])
    def create_embedding():
        """Create embeddings for a column."""
        config = request.json
        
        source_column = config.get('source_column')
        provider_name = config.get('provider')
        model_name = config.get('model')
        target_column = config.get('target_column')
        
        if not all([source_column, provider_name, model_name, target_column]):
            return jsonify({'success': False, 'error': 'Missing required parameters'}), 400
        
        if app.data_manager.df is None:
            return jsonify({'success': False, 'error': 'No data loaded'}), 404
        
        # Get source data
        texts = app.data_manager.df[source_column].tolist()
        
        # Create embeddings
        try:
            embeddings = create_embeddings(texts, provider_name, model_name)
            result = app.data_manager.add_embedding_column(target_column, embeddings)
            return jsonify(result)
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/dimred/methods', methods=['GET'])
    def list_dimred_methods():
        """List available dimensionality reduction methods."""
        methods = get_dimred_methods()
        return jsonify({'methods': methods})
    
    @app.route('/api/dimred/apply', methods=['POST'])
    def apply_dimred_route():
        """Apply dimensionality reduction to embeddings."""
        config = request.json
        
        source_column = config.get('source_column')
        method = config.get('method')
        n_components = config.get('n_components', 2)
        target_base_name = config.get('target_base_name')
        params = config.get('params', {})
        
        if not all([source_column, method, target_base_name]):
            return jsonify({'success': False, 'error': 'Missing required parameters'}), 400
        
        if app.data_manager.df is None:
            return jsonify({'success': False, 'error': 'No data loaded'}), 404
        
        # Get embeddings
        try:
            embeddings = app.data_manager.df[source_column].tolist()
            embeddings = [emb if isinstance(emb, list) else emb.tolist() for emb in embeddings]
            
            # Apply dimensionality reduction
            reduced = apply_dimred(embeddings, method, n_components, **params)
            result = app.data_manager.add_dimred_columns(target_base_name, reduced)
            return jsonify(result)
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
