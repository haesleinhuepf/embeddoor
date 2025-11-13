"""Visualization module for creating plots."""

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from typing import Optional, List, Dict, Any, Iterable
from io import BytesIO

try:
    from wordcloud import WordCloud, STOPWORDS
except ImportError:  # Graceful fallback if dependency missing
    WordCloud = None
    STOPWORDS = set()


def create_plot(
    data: List[Dict],
    x_col: str,
    y_col: Optional[str] = None,
    z_col: Optional[str] = None,
    hue_col: Optional[str] = None,
    size_col: Optional[str] = None,
    plot_type: str = '2d'
) -> str:
    """
    Create a Plotly plot from data.
    
    Args:
        data: List of data dictionaries
        x_col: Column name for x-axis
        y_col: Column name for y-axis (optional for 1D)
        z_col: Column name for z-axis (for 3D plots)
        hue_col: Column name for color mapping
        size_col: Column name for size mapping
        plot_type: '2d' or '3d'
    
    Returns:
        JSON string of the Plotly figure
    """
    df = pd.DataFrame(data)
    
    # Extract index column if present
    if 'index' in df.columns:
        indices = df['index'].astype(str)  # Convert to string for display
        df = df.drop(columns=['index'])
    else:
        indices = pd.Series(df.index.astype(str))  # Convert to string for display
    
    # Ensure numeric columns are actually numeric
    numeric_cols = [x_col]
    if y_col:
        numeric_cols.append(y_col)
    if z_col:
        numeric_cols.append(z_col)
    if size_col:
        numeric_cols.append(size_col)
    
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Drop rows with NaN in required columns after conversion
    required_cols = [x_col]
    if y_col:
        required_cols.append(y_col)
    if z_col:
        required_cols.append(z_col)
    
    # Keep track of valid indices
    valid_mask = df[required_cols].notna().all(axis=1)
    df = df[valid_mask]
    indices = indices[valid_mask].reset_index(drop=True)
    
    # Determine if we're doing 3D
    is_3d = plot_type == '3d' and z_col is not None
    
    # Create figure based on dimensionality
    if is_3d:
        fig = go.Figure()
        
        # Check if 'selection' column exists
        has_selection = 'selection' in df.columns
        
        # Group by hue if specified
        if hue_col:
            # If selection exists, draw selected points first with orange rings
            if has_selection:
                selected_mask = df['selection'] == True
                if selected_mask.any():
                    selected = df[selected_mask].reset_index(drop=True)
                    selected_indices = indices[selected_mask].reset_index(drop=True)
                    
                    # Draw orange rings (larger size, no fill)
                    ring_size = 8 if not size_col else [s * 1.5 for s in selected[size_col].tolist()]
                    
                    fig.add_trace(go.Scatter3d(
                        x=selected[x_col].tolist(),
                        y=selected[y_col].tolist(),
                        z=selected[z_col].tolist(),
                        mode='markers',
                        marker=dict(
                            size=ring_size,
                            color='rgba(0,0,0,0)',  # Transparent fill
                            line=dict(color='#ff7f0e', width=2)  # Orange ring
                        ),
                        text=selected_indices.tolist(),
                        showlegend=False,
                        hoverinfo='skip'  # Don't show hover for rings
                    ))
            
            # Use continuous colorscale for hue (draw on top)
            marker_dict = {
                'size': 5,
                'color': df[hue_col].tolist(),
                'colorscale': 'Viridis',
                'showscale': True,
                'colorbar': dict(title=hue_col)
            }
            if size_col:
                marker_dict['size'] = df[size_col].tolist()
            
            fig.add_trace(go.Scatter3d(
                x=df[x_col].tolist(),
                y=df[y_col].tolist(),
                z=df[z_col].tolist(),
                mode='markers',
                marker=marker_dict,
                text=indices.tolist(),
                hovertemplate=(
                    f'<b>Index: %{{text}}</b><br>'
                    f'{x_col}: %{{x}}<br>'
                    f'{y_col}: %{{y}}<br>'
                    f'{z_col}: %{{z}}<br>'
                    f'{hue_col}: %{{marker.color}}<br>'
                    '<extra></extra>'
                ),
                showlegend=False
            ))
        elif has_selection:
            # Split data into selected and unselected
            selected_mask = df['selection'] == True
            unselected_mask = ~selected_mask
            
            # Plot unselected points first
            if unselected_mask.any():
                unselected = df[unselected_mask].reset_index(drop=True)
                unselected_indices = indices[unselected_mask].reset_index(drop=True)
                
                marker_dict = {'size': 5, 'color': 'blue'}
                if size_col:
                    marker_dict['size'] = unselected[size_col].tolist()
                
                fig.add_trace(go.Scatter3d(
                    x=unselected[x_col].tolist(),
                    y=unselected[y_col].tolist(),
                    z=unselected[z_col].tolist(),
                    mode='markers',
                    name='Unselected',
                    marker=marker_dict,
                    text=unselected_indices.tolist(),
                    showlegend=False,
                    hovertemplate=(
                        f'<b>Index: %{{text}}</b><br>'
                        f'{x_col}: %{{x}}<br>'
                        f'{y_col}: %{{y}}<br>'
                        f'{z_col}: %{{z}}<br>'
                        '<extra></extra>'
                    )
                ))
            
            # Plot selected points on top in orange
            if selected_mask.any():
                selected = df[selected_mask].reset_index(drop=True)
                selected_indices = indices[selected_mask].reset_index(drop=True)
                
                marker_dict = {'size': 5, 'color': 'orange'}
                if size_col:
                    marker_dict['size'] = selected[size_col].tolist()
                
                fig.add_trace(go.Scatter3d(
                    x=selected[x_col].tolist(),
                    y=selected[y_col].tolist(),
                    z=selected[z_col].tolist(),
                    mode='markers',
                    name='Selected',
                    marker=marker_dict,
                    text=selected_indices.tolist(),
                    showlegend=False,
                    hovertemplate=(
                        f'<b>Index: %{{text}}</b><br>'
                        f'{x_col}: %{{x}}<br>'
                        f'{y_col}: %{{y}}<br>'
                        f'{z_col}: %{{z}}<br>'
                        '<extra></extra>'
                    )
                ))
        else:
            marker_dict = {'size': 5}
            if size_col:
                marker_dict['size'] = df[size_col].tolist()
            
            fig.add_trace(go.Scatter3d(
                x=df[x_col].tolist(),
                y=df[y_col].tolist(),
                z=df[z_col].tolist(),
                mode='markers',
                marker=marker_dict,
                text=indices.tolist(),
                hovertemplate=(
                    f'<b>Index: %{{text}}</b><br>'
                    f'{x_col}: %{{x}}<br>'
                    f'{y_col}: %{{y}}<br>'
                    f'{z_col}: %{{z}}<br>'
                    '<extra></extra>'
                )
            ))
        
        fig.update_layout(
            scene=dict(
                xaxis_title=x_col,
                yaxis_title=y_col,
                zaxis_title=z_col,
                xaxis=dict(autorange=True),
                yaxis=dict(autorange=True),
                zaxis=dict(autorange=True),
            ),
            height=700,
            hovermode='closest'
        )
    
    elif y_col:
        # 2D scatter plot
        fig = go.Figure()
        
        # Check if 'selection' column exists
        has_selection = 'selection' in df.columns
        
        if hue_col:
            # If selection exists, draw selected points first with orange rings
            if has_selection:
                selected_mask = df['selection'] == True
                if selected_mask.any():
                    selected = df[selected_mask].reset_index(drop=True)
                    selected_indices = indices[selected_mask].reset_index(drop=True)
                    
                    # Draw orange rings (larger size, no fill)
                    ring_size = 12 if not size_col else [s * 1.5 for s in selected[size_col].tolist()]
                    
                    fig.add_trace(go.Scatter(
                        x=selected[x_col].tolist(),
                        y=selected[y_col].tolist(),
                        mode='markers',
                        marker=dict(
                            size=ring_size,
                            color='rgba(0,0,0,0)',  # Transparent fill
                            line=dict(color='#ff7f0e', width=2)  # Orange ring
                        ),
                        text=selected_indices.tolist(),
                        showlegend=False,
                        hoverinfo='skip'  # Don't show hover for rings
                    ))
            
            # Use continuous colorscale for hue (draw on top)
            marker_dict = {
                'size': 8,
                'color': df[hue_col].tolist(),
                'colorscale': 'Viridis',
                'showscale': True,
                'colorbar': dict(title=hue_col)
            }
            if size_col:
                marker_dict['size'] = df[size_col].tolist()
            
            fig.add_trace(go.Scatter(
                x=df[x_col].tolist(),
                y=df[y_col].tolist(),
                mode='markers',
                marker=marker_dict,
                text=indices.tolist(),
                hovertemplate=(
                    f'<b>Index: %{{text}}</b><br>'
                    f'{x_col}: %{{x}}<br>'
                    f'{y_col}: %{{y}}<br>'
                    f'{hue_col}: %{{marker.color}}<br>'
                    '<extra></extra>'
                ),
                showlegend=False
            ))
        elif has_selection:
            # Split data into selected and unselected
            selected_mask = df['selection'] == True
            unselected_mask = ~selected_mask
            
            # Plot unselected points first (so they appear behind)
            if unselected_mask.any():
                unselected = df[unselected_mask].reset_index(drop=True)
                unselected_indices = indices[unselected_mask].reset_index(drop=True)
                
                marker_dict = {'size': 8, 'color': '#1f77b4'}
                if size_col:
                    marker_dict['size'] = unselected[size_col].tolist()
                
                fig.add_trace(go.Scatter(
                    x=unselected[x_col].tolist(),
                    y=unselected[y_col].tolist(),
                    mode='markers',
                    name='Unselected',
                    marker=marker_dict,
                    text=unselected_indices.tolist(),
                    showlegend=False,
                    hovertemplate=(
                        f'<b>Index: %{{text}}</b><br>'
                        f'{x_col}: %{{x}}<br>'
                        f'{y_col}: %{{y}}<br>'
                        '<extra></extra>'
                    )
                ))
            
            # Plot selected points on top in orange
            if selected_mask.any():
                selected = df[selected_mask].reset_index(drop=True)
                selected_indices = indices[selected_mask].reset_index(drop=True)
                
                marker_dict = {'size': 8, 'color': '#ff7f0e'}
                if size_col:
                    marker_dict['size'] = selected[size_col].tolist()
                
                fig.add_trace(go.Scatter(
                    x=selected[x_col].tolist(),
                    y=selected[y_col].tolist(),
                    mode='markers',
                    name='Selected',
                    marker=marker_dict,
                    text=selected_indices.tolist(),
                    showlegend=False,
                    hovertemplate=(
                        f'<b>Index: %{{text}}</b><br>'
                        f'{x_col}: %{{x}}<br>'
                        f'{y_col}: %{{y}}<br>'
                        '<extra></extra>'
                    )
                ))
        else:
            marker_dict = {'size': 8}
            if size_col:
                marker_dict['size'] = df[size_col].tolist()
            
            fig.add_trace(go.Scatter(
                x=df[x_col].tolist(),
                y=df[y_col].tolist(),
                mode='markers',
                marker=marker_dict,
                text=indices.tolist(),
                hovertemplate=(
                    f'<b>Index: %{{text}}</b><br>'
                    f'{x_col}: %{{x}}<br>'
                    f'{y_col}: %{{y}}<br>'
                    '<extra></extra>'
                )
            ))
            

        fig.update_layout(
            xaxis_title=x_col,
            yaxis_title=y_col,
            xaxis=dict(
                autorange=True,
                showline=True,
                linewidth=1,
                linecolor='black'
            ),
            yaxis=dict(
                autorange=True,
                showline=True,
                linewidth=1,
                linecolor='black',
            ),
            margin=dict(l=0, r=0, t=20, b=0),
            height=700,
            hovermode='closest',
            dragmode='lasso',  # Enable lasso selection
            paper_bgcolor='white',
            plot_bgcolor='white'
        )
    
    else:
        # 1D plot (histogram or strip plot)
        fig = go.Figure()
        fig.add_trace(go.Histogram(x=df[x_col]))
        fig.update_layout(
            xaxis_title=x_col,
            yaxis_title='Count',
            height=700
        )
    
    # Add lasso selection configuration for 2D plots
    if not is_3d and y_col:
        fig.update_layout(
            dragmode='lasso',
            selectdirection='any'
        )
    return fig.to_json()


def create_table_html(data: List[Dict], max_rows: int = 1000) -> str:
    """
    Create an HTML table from data.
    
    Args:
        data: List of data dictionaries
        max_rows: Maximum number of rows to display
    
    Returns:
        HTML string
    """

    df = pd.DataFrame(data)
    if len(df) > max_rows:
        df = df.head(max_rows)

    def convert_image_cell(col, cell):
        if isinstance(col, str) and 'image' in col.lower():
            if isinstance(cell, dict) and 'bytes' in cell:
                import base64
                img_bytes = cell['bytes']
                if isinstance(img_bytes, str):
                    # If already base64 string
                    b64 = img_bytes
                else:
                    b64 = base64.b64encode(img_bytes).decode('utf-8')
                return f'<img src="data:image/png;base64,{b64}" style="max-width:300px;max-height:200px;" />'
        return cell

    # If 'selection' column exists, style selected rows
    if 'selection' in df.columns:
        def row_style(row):
            sel = row.get('selection', 0)
            if sel == 1 or sel is True:
                return 'background-color: #ffdcbd; color: black;'
            return ''
        styles = [row_style(row) for row in df.to_dict(orient='records')]
        html = '<table class="data-table" border="0">'
        html += '<thead><tr>' + ''.join(f'<th>{col}</th>' for col in df.columns) + '</tr></thead>'
        html += '<tbody>'
        for i, row in enumerate(df.to_dict(orient='records')):
            style = styles[i]
            html += f'<tr style="{style}">' + ''.join(
                f'<td>{convert_image_cell(col, row[col])}</td>' for col in df.columns
            ) + '</tr>'
        html += '</tbody></table>'
        return html
    else:
        # Apply image conversion to all cells
        html = '<table class="data-table" border="0">'
        html += '<thead><tr>' + ''.join(f'<th>{col}</th>' for col in df.columns) + '</tr></thead>'
        html += '<tbody>'
        for row in df.to_dict(orient='records'):
            html += '<tr>' + ''.join(
                f'<td>{convert_image_cell(col, row[col])}</td>' for col in df.columns
            ) + '</tr>'
        html += '</tbody></table>'
        return html


def create_wordcloud_image(
    texts: Iterable[str],
    width: int = 600,
    height: int = 400,
    background_color: str = 'white',
    stopwords: Optional[Iterable[str]] = None,
    colormap: str = 'viridis'
) -> bytes:
    """Generate a word cloud PNG image from an iterable of text strings.

    Args:
        texts: Iterable of text entries to concatenate.
        width: Output image width in pixels.
        height: Output image height in pixels.
        background_color: Background color of the word cloud.
        stopwords: Optional iterable of stop words to exclude.
        colormap: Matplotlib colormap name for word coloring.

    Returns:
        Raw PNG bytes.
    """
    if WordCloud is None:
        raise RuntimeError("wordcloud package not installed. Please install 'wordcloud'.")

    # Concatenate all texts; filter non-string safely
    joined_text = " ".join([t for t in texts if isinstance(t, str)])
    if not joined_text.strip():
        joined_text = "(no text)"

    wc_stopwords = set(STOPWORDS)
    if stopwords:
        wc_stopwords.update([s.lower() for s in stopwords])

    wc = WordCloud(
        width=width,
        height=height,
        background_color=background_color,
        stopwords=wc_stopwords,
        colormap=colormap,
    )
    wc.generate(joined_text)

    image = wc.to_image()
    buf = BytesIO()
    image.save(buf, format='PNG')
    buf.seek(0)
    return buf.read()


def create_heatmap_embedding_image(
    df: pd.DataFrame, 
    embedding_column: str,
    width: int = 800,
    height: int = 600
) -> bytes:
    """
    Create a heatmap PNG image from an embedding column.
    
    Args:
        df: DataFrame containing the data
        embedding_column: Column name containing embedding vectors
        width: Output image width in pixels
        height: Output image height in pixels
    
    Returns:
        Raw PNG bytes
    """
    import matplotlib
    matplotlib.use('Agg')  # Use non-interactive backend
    import matplotlib.pyplot as plt
    
    # Check if selection column exists
    has_selection = 'selection' in df.columns
    
    # Extract embeddings
    embeddings = []
    row_labels = []
    selected_mask = []
    
    for idx, row in df.iterrows():
        try:
            # Get embedding value
            emb = row[embedding_column]
            
            # Convert to list if needed
            if isinstance(emb, str):
                # Try to parse as list/array
                import ast
                try:
                    emb = ast.literal_eval(emb)
                except:
                    continue
            elif isinstance(emb, np.ndarray):
                emb = emb.tolist()
            elif not isinstance(emb, list):
                continue
            
            embeddings.append(emb)
            row_labels.append(str(idx))
            
            # Check selection status
            if has_selection:
                is_selected = row.get('selection', 0) in [1, True, '1', 'True', 'true']
                selected_mask.append(is_selected)
            else:
                selected_mask.append(False)
        except Exception as e:
            print(f"Error processing row {idx}: {e}")
            continue
    
    if not embeddings:
        raise ValueError("No valid embeddings found")
    
    # Convert to numpy array
    embeddings_array = np.array(embeddings)
    
    # Normalize embeddings to 0-1 range
    data_min = embeddings_array.min()
    data_max = embeddings_array.max()
    if data_max > data_min:
        embeddings_array = (embeddings_array - data_min) / (data_max - data_min)
    else:
        embeddings_array = np.zeros_like(embeddings_array, dtype=np.float32)
    
    # Create figure
    fig, ax = plt.subplots(figsize=(width/100, height/100), dpi=100)
    
    if has_selection and any(selected_mask):
        # Split into selected and unselected
        selected_indices = [i for i, sel in enumerate(selected_mask) if sel]
        unselected_indices = [i for i, sel in enumerate(selected_mask) if not sel]
        
        # Create custom colormap combining blue and orange
        from matplotlib.colors import ListedColormap
        import matplotlib.cm as cm
        
        # Get blue and orange colormaps
        blues = cm.get_cmap('Blues', 128)
        oranges = cm.get_cmap('Oranges', 128)
        
        # Combine them
        colors = np.vstack((blues(np.linspace(0, 1, 128)), oranges(np.linspace(0, 1, 128))))
        combined_cmap = ListedColormap(colors)
        
        # Offset selected rows to map to orange range
        normalized_data = embeddings_array.copy()
        for i in selected_indices:
            normalized_data[i] = normalized_data[i] * 0.5 + 0.5  # Map to [0.5, 1.0]
        for i in unselected_indices:
            normalized_data[i] = normalized_data[i] * 0.5  # Map to [0, 0.5]
        
        im = ax.imshow(normalized_data, aspect='auto', cmap=combined_cmap, interpolation='nearest', vmin=0, vmax=1)
        ax.set_title(f'Embedding Heatmap: {embedding_column}\nOrange: Selected ({len(selected_indices)}) | Blue: Unselected ({len(unselected_indices)})')
    else:
        # Use single colormap
        im = ax.imshow(embeddings_array, aspect='auto', cmap='Blues', interpolation='nearest', vmin=0, vmax=1)
        ax.set_title(f'Embedding Heatmap: {embedding_column}')
    
    ax.set_xlabel('Embedding Dimension')
    ax.set_ylabel('Row Index')
    
    # Set y-axis labels (show subset if too many)
    if len(row_labels) <= 50:
        ax.set_yticks(range(len(row_labels)))
        ax.set_yticklabels(row_labels, fontsize=8)
    else:
        # Show only some labels
        step = len(row_labels) // 20
        indices = list(range(0, len(row_labels), step))
        ax.set_yticks(indices)
        ax.set_yticklabels([row_labels[i] for i in indices], fontsize=8)
    
    plt.tight_layout()
    
    # Save to buffer
    buf = BytesIO()
    plt.savefig(buf, format='PNG', dpi=100, bbox_inches='tight')
    plt.close(fig)
    buf.seek(0)
    return buf.read()


def create_heatmap_embedding(df: pd.DataFrame, embedding_column: str) -> str:
    """
    Create a heatmap from an embedding column.
    
    Args:
        df: DataFrame containing the data
        embedding_column: Column name containing embedding vectors
    
    Returns:
        JSON string of the Plotly figure
    
    DEPRECATED: Use create_heatmap_embedding_image for better performance
    """
    # Check if selection column exists
    has_selection = 'selection' in df.columns

    # Extract embeddings
    embeddings = []
    row_labels = []
    selected_mask = []
    
    for idx, row in df.iterrows():
        try:
            # Get embedding value
            emb = row[embedding_column]
            
            # Convert to list if needed
            if isinstance(emb, str):
                # Try to parse as list/array
                import ast
                try:
                    emb = ast.literal_eval(emb)
                except:
                    continue
            elif isinstance(emb, np.ndarray):
                emb = emb.tolist()
            elif not isinstance(emb, list):
                continue
            
            embeddings.append(emb)
            row_labels.append(str(idx))
            
            # Check selection status
            if has_selection:
                is_selected = row.get('selection', 0) in [1, True, '1', 'True', 'true']
                selected_mask.append(is_selected)
            else:
                selected_mask.append(False)
        except Exception as e:
            print(f"Error processing row {idx}: {e}")
            continue
    
    if not embeddings:
        raise ValueError("No valid embeddings found")
    

    # Convert to numpy array
    embeddings_array = np.array(embeddings)
    
    # Normalize embeddings to 0-255 range and convert to integers
    data_min = embeddings_array.min()
    data_max = embeddings_array.max()
    if data_max > data_min:
        embeddings_array = ((embeddings_array - data_min) / (data_max - data_min) * 255).astype(np.int32)
    else:
        embeddings_array = np.zeros_like(embeddings_array, dtype=np.int32)

    # Create figure with single heatmap
    fig = go.Figure()
    
    # For rows with selection, we'll apply color masking by creating custom colorscale
    if has_selection and any(selected_mask):
        # Use a single heatmap with custom colorscale
        # Selected rows: 0-255 (orange range)
        # Unselected rows: 256-511 (blue range)
        
        unselected_indices = [i for i, sel in enumerate(selected_mask) if not sel]
        selected_indices = [i for i, sel in enumerate(selected_mask) if sel]
        
        # Create modified data with offset for unselected rows
        normalized_data = embeddings_array.copy().astype(np.float64)
        
        # Add offset to unselected rows to map to blue part of colorscale (256-511)
        offset = 256
        normalized_data[selected_mask] = normalized_data[selected_mask] + offset
        
        # Create a custom colorscale with orange for selected (0-255) and blue for unselected (256-511)
        max_val = offset + 255  # 511
        
        # Colorscale: orange range [0, 0.5], blue range [0.5, 1.0]
        colorscale = [
            [0.0, 'rgb(255, 255, 255)'],   # white (min blue) at value 256
            [255/max_val, 'rgb(31, 119, 180)'],             # matplotlib blue (max blue) at value 511
            [256/max_val, 'rgb(255, 255, 255)'],           # white (min orange) at value 0
            [1.0, 'rgb(255, 127, 14)']    # matplotlib orange (max orange) at value 255
            
        ]
        
        fig.add_trace(go.Heatmap(
            z=normalized_data.tolist(),
            y=row_labels,
            x=list(range(normalized_data.shape[1])),
            colorscale=colorscale,
            showscale=False,  # Hide scale since values are modified
            hovertemplate='Row: %{y}<br>Dimension: %{x}<br>Value: %{z:.0f}<extra></extra>',
            zauto=False,
            zmin=0,
            zmax=max_val
        ))
        
        # Add annotation to indicate color coding
        fig.add_annotation(
            text=f"Orange: Selected ({len(selected_indices)}) | Blue: Unselected ({len(unselected_indices)})",
            xref="paper", yref="paper",
            x=0.5, y=1.05,
            showarrow=False,
            font=dict(size=12)
        )
    else:
        # No selection, use simple blue colorscale
        colorscale_blue = [
            [0.0, 'rgb(255, 255, 255)'],  # white
            [1.0, 'rgb(31, 119, 180)']     # matplotlib blue
        ]
        fig.add_trace(go.Heatmap(
            z=array2d_to_list(embeddings_array),
            y=row_labels,
            x=list(range(embeddings_array.shape[1])),
            colorscale=colorscale_blue,
            showscale=False,
            hovertemplate='Row: %{y}<br>Dimension: %{x}<br>Value: %{z:.0f}<extra></extra>',
            zmin=0,
            zmax=255
        ))
    
    fig.update_layout(
        title=f'Embedding Heatmap: {embedding_column}',
        xaxis_title='Embedding Dimension',
        yaxis_title='Row Index',
        hovermode='closest',
        xaxis=dict(autorange=True),
        yaxis=dict(autorange='reversed'),
        margin=dict(l=80, r=40, t=40, b=60),
        autosize=True
    )

    return fig.to_json()


def array2d_to_list(arr: Any):
    return [[x.item() if hasattr(x, "item") else x for x in row] for row in arr]

def create_heatmap_columns_image(
    df: pd.DataFrame, 
    columns: Optional[List[str]] = None,
    width: int = 800,
    height: int = 600
) -> bytes:
    """
    Create a heatmap PNG image from numeric columns.
    
    Args:
        df: DataFrame containing the data
        columns: List of column names to use (optional, defaults to all numeric)
        width: Output image width in pixels
        height: Output image height in pixels
    
    Returns:
        Raw PNG bytes
    """
    import matplotlib
    matplotlib.use('Agg')  # Use non-interactive backend
    import matplotlib.pyplot as plt
    
    # Check if selection column exists
    has_selection = 'selection' in df.columns
    
    # Get numeric columns
    if columns:
        numeric_cols = [col for col in columns if col in df.columns and pd.api.types.is_numeric_dtype(df[col])]
    else:
        numeric_cols = list(df.select_dtypes(include=[np.number]).columns)
        # Remove selection column if present
        if 'selection' in numeric_cols:
            numeric_cols.remove('selection')
    
    if not numeric_cols:
        raise ValueError("No numeric columns found")
    
    # Extract numeric data
    numeric_data = df[numeric_cols].copy()
    
    # Normalize each column to 0-1
    for col in numeric_cols:
        col_min = numeric_data[col].min()
        col_max = numeric_data[col].max()
        if col_max > col_min:
            numeric_data[col] = (numeric_data[col] - col_min) / (col_max - col_min)
        else:
            numeric_data[col] = 0
    
    # Convert to numpy array
    data_array = numeric_data.values
    row_labels = [str(idx) for idx in df.index]
    
    # Create figure
    fig, ax = plt.subplots(figsize=(width/100, height/100), dpi=100)
    
    # Check for selection
    if has_selection:
        selected_mask = df['selection'].isin([1, True, '1', 'True', 'true']).values
        
        if any(selected_mask):
            # Split into selected and unselected (for counting only)
            selected_indices = [i for i, sel in enumerate(selected_mask) if sel]
            unselected_indices = [i for i, sel in enumerate(selected_mask) if not sel]
            
            # Create custom colormap combining blue and orange
            from matplotlib.colors import ListedColormap
            import matplotlib.cm as cm
            
            # Get blue and orange colormaps
            blues = cm.get_cmap('Blues', 128)
            oranges = cm.get_cmap('Oranges', 128)
            
            # Combine them
            colors = np.vstack((blues(np.linspace(0, 1, 128)), oranges(np.linspace(0, 1, 128))))
            combined_cmap = ListedColormap(colors)
            
            # Offset selected rows to map to orange range (keep original row order)
            normalized_data = data_array.copy()
            for i in selected_indices:
                normalized_data[i] = normalized_data[i] * 0.5 + 0.5  # Map to [0.5, 1.0]
            for i in unselected_indices:
                normalized_data[i] = normalized_data[i] * 0.5  # Map to [0, 0.5]
            
            im = ax.imshow(normalized_data, aspect='auto', cmap=combined_cmap, interpolation='nearest', vmin=0, vmax=1)
            ax.set_title(f'Normalized Column Heatmap\nOrange: Selected ({len(selected_indices)}) | Blue: Unselected ({len(unselected_indices)})')
            
            # Use original labels (not reordered)
            if len(row_labels) <= 50:
                ax.set_yticks(range(len(row_labels)))
                ax.set_yticklabels(row_labels, fontsize=8)
            else:
                step = len(row_labels) // 20
                indices = list(range(0, len(row_labels), step))
                ax.set_yticks(indices)
                ax.set_yticklabels([row_labels[i] for i in indices], fontsize=8)
        else:
            # No selected rows, use blue for all
            im = ax.imshow(data_array, aspect='auto', cmap='Blues', interpolation='nearest', vmin=0, vmax=1)
            ax.set_title('Normalized Column Heatmap')
            
            if len(row_labels) <= 50:
                ax.set_yticks(range(len(row_labels)))
                ax.set_yticklabels(row_labels, fontsize=8)
            else:
                step = len(row_labels) // 20
                indices = list(range(0, len(row_labels), step))
                ax.set_yticks(indices)
                ax.set_yticklabels([row_labels[i] for i in indices], fontsize=8)
    else:
        # No selection column, use blue for all
        im = ax.imshow(data_array, aspect='auto', cmap='Blues', interpolation='nearest', vmin=0, vmax=1)
        ax.set_title('Normalized Column Heatmap')
        
        if len(row_labels) <= 50:
            ax.set_yticks(range(len(row_labels)))
            ax.set_yticklabels(row_labels, fontsize=8)
        else:
            step = len(row_labels) // 20
            indices = list(range(0, len(row_labels), step))
            ax.set_yticks(indices)
            ax.set_yticklabels([row_labels[i] for i in indices], fontsize=8)
    
    ax.set_xlabel('Column')
    ax.set_ylabel('Row Index')
    
    # Set x-axis labels
    ax.set_xticks(range(len(numeric_cols)))
    ax.set_xticklabels(numeric_cols, rotation=45, ha='right', fontsize=8)
    
    plt.tight_layout()
    
    # Save to buffer
    buf = BytesIO()
    plt.savefig(buf, format='PNG', dpi=100, bbox_inches='tight')
    plt.close(fig)
    buf.seek(0)
    return buf.read()


def create_heatmap_columns(df: pd.DataFrame, columns: Optional[List[str]] = None) -> str:
    """
    Create a heatmap from numeric columns.
    
    Args:
        df: DataFrame containing the data
        columns: List of column names to use (optional, defaults to all numeric)
    
    Returns:
        JSON string of the Plotly figure
    
    DEPRECATED: Use create_heatmap_columns_image for better performance
    """
    # Check if selection column exists
    has_selection = 'selection' in df.columns
    
    # Get numeric columns
    if columns:
        numeric_cols = [col for col in columns if col in df.columns and pd.api.types.is_numeric_dtype(df[col])]
    else:
        numeric_cols = list(df.select_dtypes(include=[np.number]).columns)
        # Remove selection column if present
        if 'selection' in numeric_cols:
            numeric_cols.remove('selection')
    
    if not numeric_cols:
        raise ValueError("No numeric columns found")
    
    # Extract numeric data
    numeric_data = df[numeric_cols].copy()
    
    # Normalize each column to 0-255 and convert to integers
    for col in numeric_cols:
        col_min = numeric_data[col].min()
        col_max = numeric_data[col].max()
        if col_max > col_min:
            numeric_data[col] = ((numeric_data[col] - col_min) / (col_max - col_min) * 255).astype(np.int32)
        else:
            numeric_data[col] = 0
    
    # Convert to numpy array
    data_array = numeric_data.values.astype(np.int32)
    row_labels = [str(idx) for idx in df.index]
    
    # Create figure
    fig = go.Figure()
    
    # Check for selection
    if has_selection:
        selected_mask = df['selection'].isin([1, True, '1', 'True', 'true']).values
        
        if any(selected_mask):
            # Split into selected and unselected (for counting only, keep original order)
            unselected_indices = [i for i, sel in enumerate(selected_mask) if not sel]
            selected_indices = [i for i, sel in enumerate(selected_mask) if sel]
            
            # Create custom colorscale with offset for selected rows
            normalized_data = data_array.copy().astype(np.float64)
            
            # Add offset to selected rows (shift to orange color range)
            # Data is now 0-255, so add offset accordingly
            for i in selected_indices:
                normalized_data[i] = normalized_data[i] + 256  # offset beyond 0-255 range
            
            # Colorscale: blue range [0, 0.5], orange range [0.5, 1.0]
            colorscale = [
                [0.0, 'rgb(255, 255, 255)'],      # white (min blue)
                [0.45, 'rgb(31, 119, 180)'],      # matplotlib blue (max blue)
                [0.55, 'rgb(255, 255, 255)'],     # white (min orange)
                [1.0, 'rgb(255, 127, 14)']        # matplotlib orange (max orange)
            ]
            
            fig.add_trace(go.Heatmap(
                z=normalized_data,
                y=row_labels,
                x=numeric_cols,
                colorscale=colorscale,
                showscale=False,  # Hide scale since values are modified
                hovertemplate='Row: %{y}<br>Column: %{x}<br>Value: %{z:.0f}<extra></extra>',
                zauto=False,
                zmin=0,
                zmax=511  # 0-255 for unselected + 256-511 for selected
            ))
            
            # Add annotation to indicate color coding
            fig.add_annotation(
                text=f"Orange: Selected ({len(selected_indices)}) | Blue: Unselected ({len(unselected_indices)})",
                xref="paper", yref="paper",
                x=0.5, y=1.05,
                showarrow=False,
                font=dict(size=12)
            )
        else:
            # No selected rows, use blue for all
            colorscale_blue = [
                [0.0, 'rgb(255, 255, 255)'],  # white
                [1.0, 'rgb(31, 119, 180)']     # matplotlib blue
            ]
            
            fig.add_trace(go.Heatmap(
                z=data_array,
                y=row_labels,
                x=numeric_cols,
                colorscale=colorscale_blue,
                showscale=False,
                hovertemplate='Row: %{y}<br>Column: %{x}<br>Value: %{z:.0f}<extra></extra>',
                zmin=0,
                zmax=255
            ))
    else:
        # No selection column, use blue for all
        colorscale_blue = [
            [0.0, 'rgb(255, 255, 255)'],  # white
            [1.0, 'rgb(31, 119, 180)']     # matplotlib blue
        ]
        
        fig.add_trace(go.Heatmap(
            z=data_array,
            y=row_labels,
            x=numeric_cols,
            colorscale=colorscale_blue,
            showscale=False,
            hovertemplate='Row: %{y}<br>Column: %{x}<br>Value: %{z:.0f}<extra></extra>',
            zmin=0,
            zmax=255
        ))
    
    fig.update_layout(
        title='Normalized Column Heatmap',
        xaxis_title='Column',
        yaxis_title='Row Index',
        hovermode='closest',
        yaxis=dict(autorange='reversed'),
        autosize=True
    )
    
    # Use remove_uids=False and ensure no binary encoding
    return fig.to_json(remove_uids=False, pretty=False, engine='json')


def create_correlation_matrix_image(
    df: pd.DataFrame, 
    method: str = 'pearson',
    columns: Optional[List[str]] = None,
    width: int = 800,
    height: int = 600
) -> bytes:
    """
    Create a correlation matrix PNG image from numeric columns.
    
    Args:
        df: DataFrame containing the data
        method: Correlation method ('pearson', 'spearman', 'kendall')
        columns: List of column names to use (optional, defaults to all numeric)
        width: Output image width in pixels
        height: Output image height in pixels
    
    Returns:
        Raw PNG bytes
    """
    import matplotlib
    matplotlib.use('Agg')  # Use non-interactive backend
    import matplotlib.pyplot as plt
    
    # Get numeric columns
    if columns:
        numeric_cols = [col for col in columns if col in df.columns and pd.api.types.is_numeric_dtype(df[col])]
    else:
        numeric_cols = list(df.select_dtypes(include=[np.number]).columns)
        # Remove selection column if present
        if 'selection' in numeric_cols:
            numeric_cols.remove('selection')
    
    if not numeric_cols:
        raise ValueError("No numeric columns found")
    
    if len(numeric_cols) < 2:
        raise ValueError("At least 2 numeric columns required for correlation matrix")
    
    # Extract numeric data
    numeric_data = df[numeric_cols].copy()
    
    # Calculate correlation matrix (ignoring selection - work with all data)
    corr_matrix = numeric_data.corr(method=method)
    
    # Create figure
    fig, ax = plt.subplots(figsize=(width/100, height/100), dpi=100)
    
    # Create heatmap using blue colormap
    im = ax.imshow(corr_matrix.values, aspect='auto', cmap='Blues', interpolation='nearest', vmin=-1, vmax=1)
    
    # Add colorbar
    cbar = plt.colorbar(im, ax=ax)
    cbar.set_label(f'{method.capitalize()} Correlation', rotation=270, labelpad=20)
    
    # Set title
    ax.set_title(f'Pairwise Correlation Matrix ({method.capitalize()})')
    
    # Set x and y axis labels
    ax.set_xticks(range(len(numeric_cols)))
    ax.set_yticks(range(len(numeric_cols)))
    ax.set_xticklabels(numeric_cols, rotation=45, ha='right', fontsize=8)
    ax.set_yticklabels(numeric_cols, fontsize=8)
    
    # Add correlation values as text annotations
    for i in range(len(numeric_cols)):
        for j in range(len(numeric_cols)):
            text_color = 'white' if corr_matrix.values[i, j] > 0.5 else 'black'
            text = ax.text(j, i, f'{corr_matrix.values[i, j]:.2f}',
                         ha="center", va="center", color=text_color, fontsize=7)
    
    plt.tight_layout()
    
    # Save to buffer
    buf = BytesIO()
    plt.savefig(buf, format='PNG', dpi=100, bbox_inches='tight')
    plt.close(fig)
    buf.seek(0)
    return buf.read()
