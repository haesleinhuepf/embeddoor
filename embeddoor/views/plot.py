"""Plot view module for embeddoor.

Handles route endpoints for plot visualization.
"""

from flask import jsonify, request
from embeddoor.visualization import create_plot


def register_plot_routes(app):
    """Register plot-related routes."""
    
    @app.route('/api/view/plot', methods=['POST'])
    def generate_plot():
        """Generate a plot based on the current data.
        
        Request JSON:
            x: str - X column name (required)
            y: str - Y column name (optional for 1D)
            z: str - Z column name (for 3D plots)
            hue: str - Column for color mapping
            size: str - Column for size mapping
            type: str - Plot type ('2d' or '3d')
        
        Returns:
            JSON with plot data
        """
        config = request.json
        
        x_col = config.get('x')
        y_col = config.get('y')
        z_col = config.get('z')
        hue_col = config.get('hue')
        size_col = config.get('size')
        plot_type = config.get('type', '2d')
        
        if not x_col:
            return jsonify({'error': 'X column required'}), 400
        
        # Get plot data
        plot_data = app.data_manager.get_plot_data(x_col, y_col, z_col, hue_col, size_col)
        
        if plot_data is None:
            return jsonify({'error': 'No data available'}), 404
        
        # Create plot
        plot_json = create_plot(
            plot_data['data'],
            x_col, y_col, z_col, hue_col, size_col,
            plot_type=plot_type
        )
        
        return jsonify({'success': True, 'plot': plot_json})
    
    @app.route('/api/selection/save', methods=['POST'])
    def save_selection():
        """Save a lasso selection as a new column.
        
        Request JSON:
            column_name: str - Name for the new selection column
            indices: list - List of selected row indices
        
        Returns:
            JSON with success status
        """
        data = request.json
        column_name = data.get('column_name', 'selection')
        selected_indices = data.get('indices', [])
        
        result = app.data_manager.add_selection_column(column_name, selected_indices)
        return jsonify(result)
