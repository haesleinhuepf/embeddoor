"""Table view module for embeddoor.

Handles route endpoints for table visualization.
"""

from flask import jsonify, request
import numpy as np
from embeddoor.visualization import create_table_html


def register_table_routes(app):
    """Register table-related routes."""
    
    @app.route('/api/view/table', methods=['GET'])
    def get_table_view():
        """Get a table view of the current data.
        
        Query Parameters:
            n: int - Number of rows to display (default: 100)
            start: int - Starting row index (default: 0)
        
        Returns:
            HTML table or JSON error
        """
        n = request.args.get('n', default=100, type=int)
        start = request.args.get('start', default=0, type=int)
        
        # Ensure data is loaded
        if app.data_manager.df is None:
            return jsonify({'error': 'No data loaded'}), 404
        
        # Get data slice
        df = app.data_manager.df
        end = min(start + n, len(df))
        sample_df = df.iloc[start:end].copy()
        
        # Replace lists/arrays with placeholder strings for better display
        for col in sample_df.select_dtypes(include=['object']).columns:
            sample_df[col] = sample_df[col].apply(
                lambda x: "[...]" if isinstance(x, (list, np.ndarray)) else x
            )
        
        # Convert to HTML
        html = create_table_html(sample_df.to_dict(orient='records'), max_rows=n)
        
        return html
    
    @app.route('/api/view/table/info', methods=['GET'])
    def get_table_info():
        """Get metadata about the table.
        
        Returns:
            JSON with table information (total rows, columns, etc.)
        """
        if app.data_manager.df is None:
            return jsonify({'error': 'No data loaded'}), 404
        
        df = app.data_manager.df
        return jsonify({
            'success': True,
            'total_rows': len(df),
            'total_columns': len(df.columns),
            'columns': list(df.columns),
            'dtypes': {col: str(dtype) for col, dtype in df.dtypes.items()}
        })
