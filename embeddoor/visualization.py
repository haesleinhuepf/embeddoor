"""Visualization module for creating plots."""

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
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
    
    return df.to_html(classes='data-table', index=True, border=0)


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
