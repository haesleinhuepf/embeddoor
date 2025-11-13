"""Ridgeplot view module for embeddoor.

Handles route endpoints for ridgeplot visualizations of numeric columns.
"""

from flask import jsonify, request, send_file
from io import BytesIO
import numpy as np
from embeddoor.visualization import create_ridgeplot_numeric_columns_image


def register_ridgeplot_routes(app):
    """Register ridgeplot-related routes."""

    @app.route('/api/view/ridgeplot/numeric', methods=['POST'])
    def generate_ridgeplot_numeric():
        """Generate a ridgeplot PNG from numeric columns.
        
        Request JSON:
            columns: list[str] - Specific numeric columns to include (optional)
            width: int - Image width in pixels (default: 800)
            height: int - Image height in pixels (default: 600)
            bins: int - Number of density points (default: 200)
            overlap: float - Vertical overlap between ridges 0..1 (default: 0.75)
        
        Returns:
            PNG image or JSON error
        """
        if app.data_manager.df is None:
            return jsonify({'error': 'No data loaded'}), 404

        payload = request.get_json(silent=True) or {}
        columns = payload.get('columns')
        width = payload.get('width', 800)
        height = payload.get('height', 600)
        bins = payload.get('bins', 200)
        overlap = payload.get('overlap', 0.75)

        df = app.data_manager.df

        try:
            png_bytes = create_ridgeplot_numeric_columns_image(
                df,
                columns=columns,
                width=width,
                height=height,
                bins=bins,
                overlap=overlap
            )
            buf = BytesIO(png_bytes)
            buf.seek(0)
            return send_file(buf, mimetype='image/png', as_attachment=False)
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/view/ridgeplot/columns/available', methods=['GET'])
    def get_numeric_columns_for_ridgeplot():
        """Get available numeric columns for ridgeplot.
        
        Returns:
            JSON with list of numeric columns (selection excluded)
        """
        if app.data_manager.df is None:
            return jsonify({'error': 'No data loaded'}), 404

        df = app.data_manager.df
        numeric_cols = list(df.select_dtypes(include=[np.number]).columns)
        if 'selection' in numeric_cols:
            numeric_cols.remove('selection')

        return jsonify({
            'success': True,
            'columns': numeric_cols
        })
