"""Heatmap view module for embeddoor.

Handles route endpoints for heatmap visualizations.
"""

from flask import jsonify, request, send_file
from io import BytesIO
import pandas as pd
import numpy as np
from embeddoor.visualization import create_heatmap_embedding_image, create_heatmap_columns_image


def register_heatmap_routes(app):
    """Register heatmap-related routes."""
    
    @app.route('/api/view/heatmap/embedding', methods=['POST'])
    def generate_heatmap_embedding():
        """Generate a heatmap PNG from an embedding column.
        
        Request JSON:
            embedding_column: str - Column containing embedding vectors (required)
            width: int - Image width in pixels (default: 800)
            height: int - Image height in pixels (default: 600)
            
        Returns:
            PNG image or JSON error
        """
        if app.data_manager.df is None:
            return jsonify({'error': 'No data loaded'}), 404
        
        payload = request.get_json(silent=True) or {}
        embedding_column = payload.get('embedding_column')
        width = payload.get('width', 800)
        height = payload.get('height', 600)
        
        if not embedding_column:
            return jsonify({'error': 'Embedding column required'}), 400
        
        df = app.data_manager.df
        
        if embedding_column not in df.columns:
            return jsonify({'error': f'Column {embedding_column} not found'}), 400
        
        try:
            png_bytes = create_heatmap_embedding_image(df, embedding_column, width=width, height=height)
            buf = BytesIO(png_bytes)
            buf.seek(0)
            return send_file(buf, mimetype='image/png', as_attachment=False)
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/view/heatmap/columns', methods=['POST'])
    def generate_heatmap_columns():
        """Generate a heatmap PNG from numeric columns.
        
        Request JSON:
            columns: list[str] - Specific columns to use (optional, defaults to all numeric)
            width: int - Image width in pixels (default: 800)
            height: int - Image height in pixels (default: 600)
        
        Returns:
            PNG image or JSON error
        """
        if app.data_manager.df is None:
            return jsonify({'error': 'No data loaded'}), 404
        
        payload = request.get_json(silent=True) or {}
        columns = payload.get('columns')
        width = payload.get('width', 800)
        height = payload.get('height', 600)
        
        df = app.data_manager.df
        
        try:
            png_bytes = create_heatmap_columns_image(df, columns, width=width, height=height)
            buf = BytesIO(png_bytes)
            buf.seek(0)
            return send_file(buf, mimetype='image/png', as_attachment=False)
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
