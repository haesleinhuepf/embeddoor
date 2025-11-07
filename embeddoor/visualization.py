"""Visualization module for creating plots."""

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from typing import Optional, List, Dict, Any


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
        indices = df['index']
        df = df.drop(columns=['index'])
    else:
        indices = df.index
    
    # Determine if we're doing 3D
    is_3d = plot_type == '3d' and z_col is not None
    
    # Create figure based on dimensionality
    if is_3d:
        fig = go.Figure()
        
        # Group by hue if specified
        if hue_col:
            for hue_value in df[hue_col].unique():
                subset = df[df[hue_col] == hue_value]
                subset_indices = indices[df[hue_col] == hue_value]
                
                # Prepare marker settings
                marker_dict = {'size': 5}
                if size_col:
                    marker_dict['size'] = subset[size_col]
                
                fig.add_trace(go.Scatter3d(
                    x=subset[x_col],
                    y=subset[y_col],
                    z=subset[z_col],
                    mode='markers',
                    name=str(hue_value),
                    marker=marker_dict,
                    text=subset_indices,
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
                marker_dict['size'] = df[size_col]
            
            fig.add_trace(go.Scatter3d(
                x=df[x_col],
                y=df[y_col],
                z=df[z_col],
                mode='markers',
                marker=marker_dict,
                text=indices,
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
                subset = df[df[hue_col] == hue_value]
                subset_indices = indices[df[hue_col] == hue_value]
                
                marker_dict = {'size': 8}
                if size_col:
                    marker_dict['size'] = subset[size_col]
                
                fig.add_trace(go.Scatter(
                    x=subset[x_col],
                    y=subset[y_col],
                    mode='markers',
                    name=str(hue_value),
                    marker=marker_dict,
                    text=subset_indices,
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

            marker_dict = {'size': 8}
            if size_col:
                marker_dict['size'] = df[size_col]
            
            fig.add_trace(go.Scatter(
                x=df[x_col],
                y=df[y_col],
                mode='markers',
                marker=marker_dict,
                #text=indices,
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
