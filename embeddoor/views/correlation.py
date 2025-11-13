"""Correlation view module for embeddoor.

Handles route endpoints for correlation matrix visualizations.
"""

from flask import jsonify, request, send_file
from io import BytesIO
import pandas as pd
import numpy as np
from embeddoor.visualization import create_correlation_matrix_image


def register_correlation_routes(app):
    """Register correlation-related routes."""
    
    @app.route('/api/view/correlation/matrix', methods=['POST'])
    def generate_correlation_matrix():
        """Generate a correlation matrix PNG from numeric columns.
        
        Request JSON:
            method: str - Correlation method ('pearson', 'spearman', 'kendall') (default: 'pearson')
            columns: list[str] - Specific columns to use (optional, defaults to all numeric)
            width: int - Image width in pixels (default: 800)
            height: int - Image height in pixels (default: 600)
        
        Returns:
            PNG image or JSON error
        """
        if app.data_manager.df is None:
            return jsonify({'error': 'No data loaded'}), 404
        
        payload = request.get_json(silent=True) or {}
        method = payload.get('method', 'pearson')
        columns = payload.get('columns')
        width = payload.get('width', 800)
        height = payload.get('height', 600)
        
        # Validate method
        valid_methods = ['pearson', 'spearman', 'kendall']
        if method not in valid_methods:
            return jsonify({'error': f'Invalid method. Must be one of: {", ".join(valid_methods)}'}), 400
        
        df = app.data_manager.df
        
        try:
            png_bytes = create_correlation_matrix_image(df, method=method, columns=columns, width=width, height=height)
            buf = BytesIO(png_bytes)
            buf.seek(0)
            return send_file(buf, mimetype='image/png', as_attachment=False)
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/view/correlation/columns/available', methods=['GET'])
    def get_numeric_columns_for_correlation():
        """Get available columns for correlation.
        
        Includes numeric columns, boolean columns, and the 'selection' column
        if present. Boolean columns are represented by their original names; the
        conversion to 0/1 is handled during correlation computation.
        
        Returns:
            JSON with list of eligible columns
        """
        if app.data_manager.df is None:
            return jsonify({'error': 'No data loaded'}), 404
        
        df = app.data_manager.df
        numeric_cols = list(df.select_dtypes(include=[np.number]).columns)
        # Also include boolean columns explicitly
        bool_cols = list(df.select_dtypes(include=['bool']).columns)
        # Add 'selection' column if present (even if non-numeric)
        if 'selection' in df.columns and 'selection' not in numeric_cols and 'selection' not in bool_cols:
            bool_cols.append('selection')

        # Merge and keep order as in DataFrame
        eligible = [c for c in df.columns if c in set(numeric_cols) | set(bool_cols)]

        return jsonify({
            'success': True,
            'columns': eligible
        })
