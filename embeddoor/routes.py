"""Route registration for embeddoor."""

from flask import jsonify, request, send_file
import json
from pathlib import Path
import tkinter as tk
from tkinter import filedialog
import pandas as pd

from embeddoor.visualization import create_plot, create_table_html, create_wordcloud_image
from embeddoor.embeddings import get_embedding_providers, create_embeddings
from embeddoor.dimred import get_dimred_methods, apply_dimred


def register_routes(app):
    """Register all application routes."""
    
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

    @app.route('/api/data/sample_html', methods=['GET'])
    def get_data_sample_html():
        """Get a sample of the current data as pre-rendered HTML table."""
        import numpy as np

        n = request.args.get('n', default=100, type=int)

        # Ensure data is loaded
        if app.data_manager.df is None:
            return 'No data loaded', 404

        # Build HTML using helper
        sample_df = app.data_manager.df.head(n).copy()

        # replace lists with strings for better display
        for col in sample_df.select_dtypes(include=['object']).columns:
            sample_df[col] = sample_df[col].apply(lambda x: "[...]" if isinstance(x, list) or isinstance(x, np.ndarray) else x)

        html = create_table_html(sample_df.to_dict(orient='records'), max_rows=n)

        # Return raw HTML (text/html)
        return html
    
    @app.route('/api/plot', methods=['POST'])
    def generate_plot():
        """Generate a plot based on the current data."""
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
        
        return jsonify({'plot': plot_json})
    
    @app.route('/api/selection/save', methods=['POST'])
    def save_selection():
        """Save a lasso selection as a new column."""
        data = request.json
        column_name = data.get('column_name', 'selection')
        selected_indices = data.get('indices', [])
        
        result = app.data_manager.add_selection_column(column_name, selected_indices)
        return jsonify(result)

    @app.route('/api/wordcloud', methods=['POST'])
    def wordcloud_route():
        """Generate a word cloud PNG from selected indices and a text column.

        Request JSON:
            indices: list[int or str] (required) -> dataframe index labels to include
            text_column: str (optional) -> column to use for text; if not provided, a best-effort default is chosen

        Response: image/png
        """
        if app.data_manager.df is None:
            return jsonify({'success': False, 'error': 'No data loaded'}), 404

        payload = request.get_json(silent=True) or {}
        indices = payload.get('indices') or []
        text_column = payload.get('text_column')

        df = app.data_manager.df

        # Choose a default text column if not provided
        if not text_column:
            preferred = [
                'text', 'content', 'description', 'body', 'message', 'title', 'summary'
            ]
            # pick first existing preferred
            for col in preferred:
                if col in df.columns and df[col].dtype == object:
                    text_column = col
                    break
            # else first categorical/object column
            if not text_column:
                cat_cols = list(df.select_dtypes(include=['object', 'string', 'category']).columns)
                text_column = cat_cols[0] if cat_cols else None

        if not text_column or text_column not in df.columns:
            return jsonify({'success': False, 'error': 'No suitable text column found'}), 400

        # Select subset by index labels; indices may be strings that represent ints
        if indices:
            try:
                # Normalize index types to original index type by attempting astype
                sel_index = pd.Index(indices)
                try:
                    sel_index = sel_index.astype(df.index.dtype)
                except Exception:
                    pass
                # Intersect with existing index to avoid KeyError
                valid_labels = df.index.intersection(sel_index)
                subset = df.loc[valid_labels]
            except Exception:
                # Fallback: if labels failed, try positional via list of ints within range
                try:
                    pos = [int(i) for i in indices]
                    subset = df.iloc[[p for p in pos if 0 <= p < len(df)]]
                except Exception:
                    subset = df
        else:
            # No selection -> use entire dataframe
            subset = df

        texts = subset[text_column].astype(str).tolist()

        try:
            png_bytes = create_wordcloud_image(texts, width=800, height=500)
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500

        from io import BytesIO
        buf = BytesIO(png_bytes)
        buf.seek(0)
        return send_file(buf, mimetype='image/png', as_attachment=False)
    
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
