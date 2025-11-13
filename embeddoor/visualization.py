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
    print("vis start")
    print("data length:", len(data))
    print("data sample:", data[:2])
    print("x_col:", x_col)
    print("y_col:", y_col)
    print("z_col:", z_col)
    print("hue_col:", hue_col)
    print("size_col:", size_col)
    print("plot_type:", plot_type)

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
            for hue_value in df[hue_col].unique():
                mask = df[hue_col] == hue_value
                subset = df[mask].reset_index(drop=True)
                subset_indices = indices[mask].reset_index(drop=True)
                
                # Prepare marker settings
                marker_dict = {'size': 5}
                if size_col:
                    marker_dict['size'] = subset[size_col].tolist()
                
                fig.add_trace(go.Scatter3d(
                    x=subset[x_col].tolist(),
                    y=subset[y_col].tolist(),
                    z=subset[z_col].tolist(),
                    mode='markers',
                    name=str(hue_value),
                    marker=marker_dict,
                    text=subset_indices.tolist(),
                    hovertemplate=(
                        f'<b>Index: %{{text}}</b><br>'
                        f'{x_col}: %{{x}}<br>'
                        f'{y_col}: %{{y}}<br>'
                        f'{z_col}: %{{z}}<br>'
                        '<extra></extra>'
                    )
                ))
        elif has_selection:
            # Split data into selected and unselected
            print("handling selection column in 3D")
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
        print("2d plot")
        # 2D scatter plot
        fig = go.Figure()
        
        # Check if 'selection' column exists
        has_selection = 'selection' in df.columns
        
        if hue_col:
            print("hue")
            for hue_value in df[hue_col].unique():
                mask = df[hue_col] == hue_value
                subset = df[mask].reset_index(drop=True)
                subset_indices = indices[mask].reset_index(drop=True)
                
                marker_dict = {'size': 8}
                if size_col:
                    marker_dict['size'] = subset[size_col].tolist()
                
                fig.add_trace(go.Scatter(
                    x=subset[x_col].tolist(),
                    y=subset[y_col].tolist(),
                    mode='markers',
                    name=str(hue_value),
                    marker=marker_dict,
                    text=subset_indices.tolist(),
                    hovertemplate=(
                        f'<b>Index: %{{text}}</b><br>'
                        f'{x_col}: %{{x}}<br>'
                        f'{y_col}: %{{y}}<br>'
                        '<extra></extra>'
                    )
                ))
        elif has_selection:
            # Split data into selected and unselected
            print("handling selection column")
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
            print("no hue")
            print("data", df.head())
            print("indices", indices.head() if hasattr(indices, 'head') else indices[:5])
            print("x values", df[x_col].head())
            print("y values", df[y_col].head())

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
            

        print("update layout")
        fig.update_layout(
            xaxis_title=x_col,
            yaxis_title=y_col,
            xaxis=dict(autorange=True),
            yaxis=dict(autorange=True),
            height=700,
            hovermode='closest',
            dragmode='lasso'  # Enable lasso selection
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
    print("vis done")
    fig.write_html("debug_plot.html")

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


def create_heatmap_embedding(df: pd.DataFrame, embedding_column: str) -> str:
    """
    Create a heatmap from an embedding column.
    
    Args:
        df: DataFrame containing the data
        embedding_column: Column name containing embedding vectors
    
    Returns:
        JSON string of the Plotly figure
    """
    # Check if selection column exists
    has_selection = 'selection' in df.columns

    print("df.shape", df.shape)
    
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
    print("E shape", embeddings_array.shape)
    
    # Normalize embeddings to 0-255 range and convert to integers
    data_min = embeddings_array.min()
    data_max = embeddings_array.max()
    if data_max > data_min:
        embeddings_array = ((embeddings_array - data_min) / (data_max - data_min) * 255).astype(np.int32)
    else:
        embeddings_array = np.zeros_like(embeddings_array, dtype=np.int32)

    print("E2 shape", embeddings_array.shape)


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

        print("SHAPE", normalized_data.shape)
        
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
        print("A", array2d_to_list(embeddings_array))
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
        print("A-")
    
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
    
    print("xaxis", fig.layout.xaxis)
    print("xaxis.range", fig.layout.xaxis.range)

    fig.write_html("debug_plot2.html")

    return fig.to_json()


def array2d_to_list(arr: Any):
    return [[x.item() if hasattr(x, "item") else x for x in row] for row in arr]

def create_heatmap_columns(df: pd.DataFrame, columns: Optional[List[str]] = None) -> str:
    """
    Create a heatmap from numeric columns.
    
    Args:
        df: DataFrame containing the data
        columns: List of column names to use (optional, defaults to all numeric)
    
    Returns:
        JSON string of the Plotly figure
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
            # Reorder data: unselected first, then selected
            unselected_indices = [i for i, sel in enumerate(selected_mask) if not sel]
            selected_indices = [i for i, sel in enumerate(selected_mask) if sel]
            
            new_order = unselected_indices + selected_indices
            reordered_data = data_array[new_order]
            reordered_labels = [row_labels[i] for i in new_order]
            reordered_selection = [selected_mask[i] for i in new_order]
            
            # Create custom colorscale with offset for selected rows
            normalized_data = reordered_data.copy().astype(np.float64)
            
            # Add offset to selected rows (shift to orange color range)
            # Data is now 0-255, so add offset accordingly
            for i, is_selected in enumerate(reordered_selection):
                if is_selected:
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
                y=reordered_labels,
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
                text=f"Blue: Unselected ({len(unselected_indices)}) | Orange: Selected ({len(selected_indices)})",
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
