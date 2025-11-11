"""Images view module for embeddoor.

Handles route endpoints for image gallery visualization.
"""

from flask import jsonify, request
import base64
from pathlib import Path
import pandas as pd


def register_images_routes(app):
    """Register image gallery-related routes."""
    
    @app.route('/api/view/images', methods=['POST'])
    def get_images_view():
        """Get image gallery view of the current data.
        
        Request JSON:
            indices: list[int] - Row indices to display (optional, defaults to all)
            image_column: str - Column containing image paths or base64 data
            max_images: int - Maximum number of images to return (default: 50)
        
        Returns:
            JSON with image data (paths or base64 encoded images)
        """
        if app.data_manager.df is None:
            return jsonify({'error': 'No data loaded'}), 404
        
        payload = request.get_json(silent=True) or {}
        indices = payload.get('indices')
        image_column = payload.get('image_column')
        max_images = payload.get('max_images', 50)
        
        df = app.data_manager.df
        
        # Auto-detect image column if not provided
        if not image_column:
            # Look for common image column names
            candidates = ['image', 'img', 'image_path', 'img_path', 'path', 'url', 'image_url']
            for col in candidates:
                if col in df.columns:
                    image_column = col
                    break
            
            # If still not found, look for columns with common image extensions
            if not image_column:
                for col in df.select_dtypes(include=['object']).columns:
                    sample_val = str(df[col].iloc[0]) if len(df) > 0 else ''
                    if any(ext in sample_val.lower() for ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']):
                        image_column = col
                        break
        
        if not image_column or image_column not in df.columns:
            return jsonify({'error': 'No suitable image column found'}), 400
        
        # Select subset
        if indices:
            try:
                subset = df.iloc[indices]
            except Exception:
                subset = df
        else:
            subset = df
        
        # Limit to max_images
        subset = subset.head(max_images)
        
        # Prepare image data
        images = []
        for idx, row in subset.iterrows():
            image_val = row[image_column]
            if pd.isna(image_val):
                continue
            
            image_data = {
                'index': int(idx) if isinstance(idx, (int, pd.Int64Dtype)) else str(idx),
                'type': 'unknown'
            }
            
            # Determine if it's a path or base64
            image_str = str(image_val)
            if image_str.startswith('data:image'):
                # Already base64 encoded
                image_data['type'] = 'base64'
                image_data['data'] = image_str
            elif image_str.startswith('http://') or image_str.startswith('https://'):
                # URL
                image_data['type'] = 'url'
                image_data['url'] = image_str
            else:
                # Assume file path
                image_data['type'] = 'path'
                image_data['path'] = image_str
                
                # Try to load and encode as base64
                try:
                    img_path = Path(image_str)
                    if img_path.exists() and img_path.is_file():
                        with open(img_path, 'rb') as f:
                            img_bytes = f.read()
                        # Determine mime type from extension
                        ext = img_path.suffix.lower()
                        mime_map = {
                            '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg',
                            '.png': 'image/png', '.gif': 'image/gif',
                            '.bmp': 'image/bmp', '.webp': 'image/webp'
                        }
                        mime_type = mime_map.get(ext, 'image/jpeg')
                        b64_data = base64.b64encode(img_bytes).decode('utf-8')
                        image_data['type'] = 'base64'
                        image_data['data'] = f'data:{mime_type};base64,{b64_data}'
                except Exception as e:
                    # If loading fails, keep as path
                    image_data['error'] = str(e)
            
            images.append(image_data)
        
        return jsonify({
            'success': True,
            'images': images,
            'total': len(images),
            'column': image_column
        })
    
    @app.route('/api/view/images/columns', methods=['GET'])
    def get_image_columns():
        """Get available image columns.
        
        Returns:
            JSON with list of potential image columns
        """
        if app.data_manager.df is None:
            return jsonify({'error': 'No data loaded'}), 404
        
        df = app.data_manager.df
        
        # Look for columns that might contain images
        image_columns = []
        for col in df.select_dtypes(include=['object']).columns:
            # Check first few non-null values
            sample_values = df[col].dropna().head(5).astype(str)
            if any(any(ext in val.lower() for ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', 'data:image'])
                   for val in sample_values):
                image_columns.append(col)
        
        return jsonify({
            'success': True,
            'columns': image_columns
        })
