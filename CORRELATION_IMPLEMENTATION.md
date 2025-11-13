# Pairwise Correlation Panel - Implementation Summary

## Overview
Added a new "Pairwise Correlation" panel type to embeddoor that visualizes correlation matrices of all numeric columns in the dataset.

## Features
- **Multiple correlation methods**: Users can choose between Pearson, Spearman, and Kendall correlation
- **Automatic column filtering**: Automatically excludes non-numeric columns and the 'selection' column
- **Blue color scheme**: Consistent with heatmap visualizations, uses blue intensity for correlation values
- **Interactive method selection**: Dropdown menu to switch between correlation methods with live updates
- **Annotated matrix**: Correlation values are displayed as text on each cell
- **Ignores selection**: Works with all data regardless of row selection

## Implementation Details

### Backend Components

#### 1. New View Module: `embeddoor/views/correlation.py`
- `register_correlation_routes(app)`: Registers correlation-related Flask routes
- `POST /api/view/correlation/matrix`: Generates correlation matrix PNG
- `GET /api/view/correlation/columns/available`: Returns list of numeric columns

#### 2. Visualization Function: `embeddoor/visualization.py`
- `create_correlation_matrix_image()`: Generates correlation matrix as PNG image
  - Parameters: `df`, `method`, `columns`, `width`, `height`
  - Methods: 'pearson', 'spearman', 'kendall'
  - Returns: Raw PNG bytes
  - Uses matplotlib with 'Blues' colormap
  - Adds text annotations showing correlation values

#### 3. View Registration: `embeddoor/views/__init__.py`
- Added import: `from embeddoor.views.correlation import register_correlation_routes`
- Added registration: `register_correlation_routes(app)` in `register_all_views()`

### Frontend Components

#### 1. Panel Type: `embeddoor/static/js/app.js`
- Added 'correlation' option to panel view selector dropdown
- Added case in `updateContent()` switch statement
- Implemented `renderCorrelation(body)` method:
  - Creates UI with correlation method dropdown (Pearson/Spearman/Kendall)
  - Adds Update button
  - Auto-generates on initial render
- Implemented `updateCorrelation()` method:
  - Fetches correlation matrix from API
  - Displays PNG image in panel
  - Handles errors gracefully

### User Interface

```
┌─────────────────────────────────────┐
│ Method: [Pearson ▼] [Update] Info  │
├─────────────────────────────────────┤
│                                     │
│     Correlation Matrix Image        │
│     (Blue heatmap with values)      │
│                                     │
└─────────────────────────────────────┘
```

## Usage

### From the UI
1. Launch embeddoor: `embeddoor`
2. Load a dataset with numeric columns
3. Create a new panel or change existing panel type to "Pairwise Correlation"
4. Select correlation method from dropdown (Pearson, Spearman, or Kendall)
5. The matrix updates automatically when method is changed

### From Code
```python
from embeddoor.visualization import create_correlation_matrix_image
import pandas as pd

df = pd.DataFrame({
    'x': [1, 2, 3, 4, 5],
    'y': [2, 4, 6, 8, 10],
    'z': [5, 4, 3, 2, 1]
})

# Generate correlation matrix image
png_bytes = create_correlation_matrix_image(
    df, 
    method='pearson',
    width=800, 
    height=600
)

# Save to file
with open('correlation_matrix.png', 'wb') as f:
    f.write(png_bytes)
```

## Testing

Created `tests/test_correlation.py` with comprehensive tests:
- ✓ Pearson correlation
- ✓ Spearman correlation  
- ✓ Kendall correlation
- ✓ Specific column selection
- ✓ Error handling (no numeric columns, single column)

Created `examples/correlation_example.py` demonstrating:
- Creating data with known correlations
- Expected correlation patterns
- Usage instructions

## API Specification

### POST /api/view/correlation/matrix
**Request:**
```json
{
  "method": "pearson",
  "columns": ["col1", "col2"],  // optional
  "width": 800,
  "height": 600
}
```

**Response:** PNG image (image/png)

**Error Responses:**
- 400: Invalid correlation method
- 400: No numeric columns found
- 400: Less than 2 numeric columns
- 404: No data loaded
- 500: Processing error

### GET /api/view/correlation/columns/available
**Response:**
```json
{
  "success": true,
  "columns": ["value1", "value2", "value3"]
}
```

## Correlation Methods

### Pearson (default)
- Measures linear correlation
- Range: -1 (perfect negative) to +1 (perfect positive)
- Best for: Linear relationships, normally distributed data

### Spearman
- Measures monotonic relationships (rank-based)
- Range: -1 to +1
- Best for: Non-linear monotonic relationships, ordinal data

### Kendall
- Measures ordinal association (tau correlation)
- Range: -1 to +1
- Best for: Small datasets, ordinal data, robust to outliers

## Files Modified/Created

### Created:
- `embeddoor/views/correlation.py` - Correlation view routes
- `tests/test_correlation.py` - Test suite
- `examples/correlation_example.py` - Usage example

### Modified:
- `embeddoor/visualization.py` - Added `create_correlation_matrix_image()`
- `embeddoor/views/__init__.py` - Registered correlation routes
- `embeddoor/static/js/app.js` - Added correlation panel UI
- `VIEWS_MODULE_REFERENCE.md` - Added documentation

## Design Decisions

1. **Blue colormap**: Chosen to match existing heatmap views for visual consistency
2. **Ignores selection**: Correlation is a dataset-wide property, selection doesn't affect it
3. **PNG output**: Consistent with heatmap implementation, better performance than JSON
4. **Method dropdown**: User-friendly way to explore different correlation types
5. **Auto-update**: Regenerates on method change for immediate feedback
6. **Text annotations**: Shows exact correlation values for precise interpretation
