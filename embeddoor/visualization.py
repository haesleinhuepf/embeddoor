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
    
    # Determine eligible columns: numeric, boolean, and 'selection'
    if columns:
        # Keep requested columns that are numeric/boolean or named 'selection'
        numeric_cols = []
        for col in columns:
            if col not in df.columns:
                continue
            if pd.api.types.is_numeric_dtype(df[col]) or pd.api.types.is_bool_dtype(df[col]) or col == 'selection':
                numeric_cols.append(col)
    else:
        numeric_cols = list(df.select_dtypes(include=[np.number]).columns)
        # Also include boolean columns
        bool_cols = list(df.select_dtypes(include=['bool']).columns)
        # Ensure 'selection' is included even if not numeric/bool
        if 'selection' in df.columns and 'selection' not in numeric_cols and 'selection' not in bool_cols:
            bool_cols.append('selection')
        # Merge preserving DataFrame column order
        numeric_cols = [c for c in df.columns if c in set(numeric_cols) | set(bool_cols)]
    
    if not numeric_cols:
        raise ValueError("No numeric columns found")
    
    if len(numeric_cols) < 2:
        raise ValueError("At least 2 numeric columns required for correlation matrix")
    
    # Extract data and coerce types as needed (bool -> int; selection -> 0/1)
    numeric_data = df[numeric_cols].copy()
    for col in numeric_cols:
        if col == 'selection':
            # Map common truthy values to 1, else 0
            s = df[col]
            truthy = s.isin([1, True, '1', 'True', 'true']) if s.dtype != bool else s
            numeric_data[col] = truthy.astype(int)
        elif pd.api.types.is_bool_dtype(numeric_data[col]):
            numeric_data[col] = numeric_data[col].astype(int)
        else:
            # Ensure numeric (coerce errors to NaN which corr will handle)
            numeric_data[col] = pd.to_numeric(numeric_data[col], errors='coerce')
    
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


def create_ridgeplot_numeric_columns_image(
    df: pd.DataFrame,
    columns: Optional[List[str]] = None,
    width: int = 800,
    height: int = 600,
    bins: int = 200,
    overlap: float = 0.75
) -> bytes:
    """
    Create a ridgeplot (joyplot) PNG image for all numeric columns.

    The x-axis is shared across all columns using the global min/max to align
    the distributions. If a boolean 'selection' column exists, densities for
    selected (orange) and unselected (blue) subsets are overlaid per row.

    Args:
        df: DataFrame containing the data
        columns: Optional list of numeric columns to include. Defaults to all numeric (excl. 'selection').
        width: Output image width in pixels
        height: Output image height in pixels
        bins: Number of points along x-axis for density estimation
        overlap: Fraction of vertical overlap between adjacent ridges (0..1)

    Returns:
        Raw PNG bytes
    """
    import matplotlib
    matplotlib.use('Agg')  # Non-interactive backend for server-side render
    import matplotlib.pyplot as plt

    # Determine numeric columns
    if columns:
        numeric_cols = [c for c in columns if c in df.columns and pd.api.types.is_numeric_dtype(df[c])]
    else:
        numeric_cols = list(df.select_dtypes(include=[np.number]).columns)
        if 'selection' in numeric_cols:
            numeric_cols.remove('selection')

    if not numeric_cols:
        raise ValueError("No numeric columns found")

    # Compute global min/max across all selected numeric columns for shared x-axis
    col_mins = []
    col_maxs = []
    for col in numeric_cols:
        series = pd.to_numeric(df[col], errors='coerce').dropna()
        if series.empty:
            continue
        col_mins.append(series.min())
        col_maxs.append(series.max())
    if not col_mins:
        raise ValueError("No valid numeric data to plot")
    global_min = float(np.min(col_mins))
    global_max = float(np.max(col_maxs))
    if not np.isfinite(global_min) or not np.isfinite(global_max) or global_min == global_max:
        # Fallback range
        global_min, global_max = 0.0, 1.0

    # X grid for density estimation
    x = np.linspace(global_min, global_max, bins)

    # Simple Gaussian kernel for smoothing hist densities (no SciPy dependency)
    def smooth_hist(values: np.ndarray) -> np.ndarray:
        values = values.astype(float)
        if values.size < 2:
            return np.zeros_like(x)
        # Use Freedman–Diaconis rule to set bandwidth-ish window in x bins
        iqr = np.subtract(*np.percentile(values, [75, 25])) if values.size > 1 else 0.0
        std = np.std(values) if values.size > 1 else 0.0
        # Heuristic bandwidth
        bw = 1.06 * std * (values.size ** (-1/5)) if std > 0 else (iqr / 1.34 if iqr > 0 else (global_max - global_min) / 30.0)
        bw = max(bw, (global_max - global_min) / 100.0)
        # Build histogram density on the shared grid using linear interpolation of bin counts
        hist_counts, hist_edges = np.histogram(values, bins=max(20, int(np.sqrt(values.size))), range=(global_min, global_max), density=True)
        centers = (hist_edges[:-1] + hist_edges[1:]) / 2.0
        # Interpolate to x grid
        dens = np.interp(x, centers, hist_counts, left=0.0, right=0.0)
        # Convolve with Gaussian kernel in x-space
        sigma_bins = max(1.0, bw * (bins / max(global_max - global_min, 1e-9)))  # convert to grid bins
        win_half = int(3 * sigma_bins)
        t = np.arange(-win_half, win_half + 1)
        kernel = np.exp(-(t**2) / (2 * sigma_bins**2))
        kernel /= kernel.sum() if kernel.sum() > 0 else 1.0
        smoothed = np.convolve(dens, kernel, mode='same')
        return smoothed

    # Figure: leave space on left for y labels
    fig_w, fig_h = width / 100.0, height / 100.0
    fig, ax = plt.subplots(figsize=(fig_w, fig_h), dpi=100)

    # Determine vertical scaling per ridge
    n = len(numeric_cols)
    if n == 0:
        raise ValueError("No numeric columns found")
    # Vertical positions from top to bottom
    y_positions = np.linspace(n - 1, 0, n)
    # Scale factor to control overlap
    vscale = 1.0 - overlap
    vscale = max(0.1, min(1.0, vscale))

    has_selection = 'selection' in df.columns
    any_selected = False
    if has_selection:
        sel_series = df['selection']
        if sel_series.dtype != bool:
            # Accept 1/0 or truthy strings
            sel_mask = sel_series.isin([1, True, '1', 'True', 'true'])
        else:
            sel_mask = sel_series
        any_selected = sel_mask.any()

    # For consistent color scheme with app
    color_unselected = '#1f77b4'  # matplotlib blue
    color_selected = '#ff7f0e'    # matplotlib orange

    # Normalize area heights to fit nicely; compute max density observed to scale
    max_dens = 1e-9
    precomputed = {}
    for col in numeric_cols:
        values_all = pd.to_numeric(df[col], errors='coerce').dropna().values
        if values_all.size == 0:
            dens_all = np.zeros_like(x)
        else:
            dens_all = smooth_hist(values_all)
        max_dens = max(max_dens, float(dens_all.max()))

        if has_selection and any_selected:
            if sel_series.dtype != bool:
                sel_mask = df['selection'].isin([1, True, '1', 'True', 'true'])
            else:
                sel_mask = df['selection']
            values_sel = pd.to_numeric(df.loc[sel_mask, col], errors='coerce').dropna().values
            values_uns = pd.to_numeric(df.loc[~sel_mask, col], errors='coerce').dropna().values
            dens_sel = smooth_hist(values_sel) if values_sel.size > 0 else np.zeros_like(x)
            dens_uns = smooth_hist(values_uns) if values_uns.size > 0 else np.zeros_like(x)
            max_dens = max(max_dens, float(dens_sel.max()), float(dens_uns.max()))
            precomputed[col] = (dens_all, dens_sel, dens_uns)
        else:
            precomputed[col] = (dens_all, None, None)

    # Plot each ridge
    for idx, col in enumerate(numeric_cols):
        y0 = y_positions[idx]
        dens_all, dens_sel, dens_uns = precomputed[col]
        scale = vscale / max_dens if max_dens > 0 else vscale

        # Base (all data) outline in light gray for context
        ax.plot(x, y0 + dens_all * scale, color='#bbbbbb', lw=1.0, alpha=0.7, zorder=1)

        if has_selection and any_selected and dens_sel is not None and dens_uns is not None:
            # Unselected fill
            ax.fill_between(x, y0, y0 + dens_uns * scale, color=color_unselected, alpha=0.55, linewidth=0, zorder=2)
            ax.plot(x, y0 + dens_uns * scale, color=color_unselected, lw=1.0, alpha=0.9, zorder=3)
            # Selected fill on top
            ax.fill_between(x, y0, y0 + dens_sel * scale, color=color_selected, alpha=0.55, linewidth=0, zorder=4)
            ax.plot(x, y0 + dens_sel * scale, color=color_selected, lw=1.0, alpha=0.9, zorder=5)
        else:
            # Single fill for all data
            ax.fill_between(x, y0, y0 + dens_all * scale, color=color_unselected, alpha=0.6, linewidth=0, zorder=2)
            ax.plot(x, y0 + dens_all * scale, color=color_unselected, lw=1.0, alpha=0.9, zorder=3)

    # Labels and aesthetics
    ax.set_yticks(y_positions)
    ax.set_yticklabels(numeric_cols, fontsize=9)
    ax.set_xlim(global_min, global_max)
    ax.set_xlabel('Value')
    ax.set_title('Ridgeplot of Numeric Columns' + (' (Orange: Selected, Blue: Unselected)' if has_selection and any_selected else ''))
    ax.grid(axis='x', alpha=0.2)

    # Tidy layout
    plt.tight_layout()

    # Save to buffer
    buf = BytesIO()
    plt.savefig(buf, format='PNG', dpi=100, bbox_inches='tight')
    plt.close(fig)
    buf.seek(0)
    return buf.read()
