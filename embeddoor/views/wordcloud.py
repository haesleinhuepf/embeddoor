"""Word cloud view module for embeddoor.

Handles route endpoints for word cloud visualization.
"""

from flask import jsonify, request, send_file
from io import BytesIO
import pandas as pd
from embeddoor.visualization import create_wordcloud_image


def register_wordcloud_routes(app):
    """Register word cloud-related routes."""
    
    @app.route('/api/view/wordcloud', methods=['POST'])
    def generate_wordcloud():
        """Generate a word cloud PNG from selected indices and a text column.
        
        Request JSON:
            indices: list[int or str] - Dataframe index labels to include (optional)
            text_column: str - Column to use for text (optional, will auto-detect)
            width: int - Image width in pixels (default: 800)
            height: int - Image height in pixels (default: 500)
        
        Returns:
            PNG image or JSON error
        """
        if app.data_manager.df is None:
            return jsonify({'error': 'No data loaded'}), 404
        
        payload = request.get_json(silent=True) or {}
        indices = payload.get('indices') or []
        text_column = payload.get('text_column')
        width = payload.get('width', 800)
        height = payload.get('height', 500)
        
        df = app.data_manager.df
        
        # Choose a default text column if not provided
        if not text_column:
            preferred = [
                'text', 'content', 'description', 'body', 'message', 'title', 'summary'
            ]
            # Pick first existing preferred column
            for col in preferred:
                if col in df.columns and df[col].dtype == object:
                    text_column = col
                    break
            # Fallback to first categorical/object column
            if not text_column:
                cat_cols = list(df.select_dtypes(include=['object', 'string', 'category']).columns)
                text_column = cat_cols[0] if cat_cols else None
        
        if not text_column or text_column not in df.columns:
            return jsonify({'error': 'No suitable text column found'}), 400
        
        # Select subset by index labels
        if indices:
            try:
                # Normalize index types
                sel_index = pd.Index(indices)
                try:
                    sel_index = sel_index.astype(df.index.dtype)
                except Exception:
                    pass
                # Intersect with existing index to avoid KeyError
                valid_labels = df.index.intersection(sel_index)
                subset = df.loc[valid_labels]
            except Exception:
                # Fallback: try positional indexing
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
            png_bytes = create_wordcloud_image(texts, width=width, height=height)
        except Exception as e:
            return jsonify({'error': str(e)}), 500
        
        buf = BytesIO(png_bytes)
        buf.seek(0)
        return send_file(buf, mimetype='image/png', as_attachment=False)
    
    @app.route('/api/view/wordcloud/columns', methods=['GET'])
    def get_wordcloud_columns():
        """Get available text columns for word cloud generation.
        
        Returns:
            JSON with list of suitable text columns
        """
        if app.data_manager.df is None:
            return jsonify({'error': 'No data loaded'}), 404
        
        df = app.data_manager.df
        text_columns = list(df.select_dtypes(include=['object', 'string', 'category']).columns)
        
        return jsonify({
            'success': True,
            'columns': text_columns
        })
