"""Heatmap view module for embeddoor.

Handles route endpoints for heatmap visualizations.
"""

from flask import jsonify, request
import pandas as pd
import numpy as np
from embeddoor.visualization import create_heatmap_embedding, create_heatmap_columns


def register_heatmap_routes(app):
    """Register heatmap-related routes."""
    
    @app.route('/api/view/heatmap/embedding', methods=['POST'])
    def generate_heatmap_embedding():
        """Generate a heatmap from an embedding column.
        
        Request JSON:
            embedding_column: str - Column containing embedding vectors (required)
            indices: list[int] - Row indices to display (optional, defaults to all)
        
        Returns:
            JSON with heatmap data
        """
        if app.data_manager.df is None:
            return jsonify({'error': 'No data loaded'}), 404
        
        payload = request.get_json(silent=True) or {}
        embedding_column = payload.get('embedding_column')
        indices = payload.get('indices')
        
        if not embedding_column:
            return jsonify({'error': 'Embedding column required'}), 400
        
        df = app.data_manager.df
        
        if embedding_column not in df.columns:
            return jsonify({'error': f'Column {embedding_column} not found'}), 400
        
        # Select subset
        if indices:
            try:
                subset = df.iloc[indices]
            except Exception:
                subset = df
        else:
            subset = df
        
        try:
            heatmap_json = create_heatmap_embedding(subset, embedding_column)
            return jsonify({'success': True, 'plot': heatmap_json})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/view/heatmap/columns', methods=['POST'])
    def generate_heatmap_columns():
        """Generate a heatmap from numeric columns.
        
        Request JSON:
            indices: list[int] - Row indices to display (optional, defaults to all)
            columns: list[str] - Specific columns to use (optional, defaults to all numeric)
        
        Returns:
            JSON with heatmap data
        """
        if app.data_manager.df is None:
            return jsonify({'error': 'No data loaded'}), 404
        
        payload = request.get_json(silent=True) or {}
        indices = payload.get('indices')
        columns = payload.get('columns')
        
        df = app.data_manager.df
        
        # Select subset
        if indices:
            try:
                subset = df.iloc[indices]
            except Exception:
                subset = df
        else:
            subset = df
        
        try:
            heatmap_json = create_heatmap_columns(subset, columns)
            return jsonify({'success': True, 'plot': heatmap_json})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/view/heatmap/embedding/columns', methods=['GET'])
    def get_embedding_columns():
        """Get available embedding columns (columns containing 'embedding' in name).
        
        Returns:
            JSON with list of embedding columns
        """
        if app.data_manager.df is None:
            return jsonify({'error': 'No data loaded'}), 404
        
        df = app.data_manager.df
        embedding_cols = [col for col in df.columns if 'embedding' in col.lower()]
        
        return jsonify({
            'success': True,
            'columns': embedding_cols
        })
    
    @app.route('/api/view/heatmap/columns/available', methods=['GET'])
    def get_numeric_columns():
        """Get available numeric columns for heatmap.
        
        Returns:
            JSON with list of numeric columns
        """
        if app.data_manager.df is None:
            return jsonify({'error': 'No data loaded'}), 404
        
        df = app.data_manager.df
        numeric_cols = list(df.select_dtypes(include=[np.number]).columns)
        
        return jsonify({
            'success': True,
            'columns': numeric_cols
        })
