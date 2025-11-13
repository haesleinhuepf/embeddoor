# Heatmap Views

## Overview

Two new heatmap visualization views have been added to Embeddoor:

1. **Heatmap (Embedding)** - Visualizes embedding vectors as heatmaps
2. **Heatmap (Columns)** - Visualizes numeric columns as normalized heatmaps

Both views support selection highlighting, showing selected rows in orange and unselected rows in blue.

## Heatmap (Embedding)

### Description
Displays embedding vectors as a heatmap where:
- **X-axis**: Embedding dimensions (0, 1, 2, ...)
- **Y-axis**: DataFrame row indices
- **Color**: Value intensity (white to blue)

### Usage
1. Select "Heatmap (Embedding)" from the view dropdown in any panel
2. Choose an embedding column from the dropdown (shows columns containing "embedding" in their name)
3. Click "Update" to generate the visualization

### Requirements
- At least one column containing "embedding" in its name
- Column values should be:
  - Lists of numbers: `[1.2, 3.4, 5.6, ...]`
  - NumPy arrays
  - String representations of lists that can be parsed

### Features
- Auto-detects embedding columns
- Supports row selection highlighting
- Interactive hover tooltips showing row, dimension, and value
- Responsive height based on number of rows

## Heatmap (Columns)

### Description
Displays all numeric columns as a normalized heatmap where:
- **X-axis**: Column names
- **Y-axis**: DataFrame row indices
- **Color**: Normalized value intensity (white to blue)
- All columns are normalized to 0-1 range independently

### Usage
1. Select "Heatmap (Columns)" from the view dropdown in any panel
2. Click "Update" to generate the visualization
3. The view automatically uses all numeric columns (excluding 'selection' column)

### Features
- Automatic column normalization (min-max scaling to 0-1)
- Supports row selection highlighting
- Interactive hover tooltips showing row, column, and normalized value
- Responsive height based on number of rows

## Selection Highlighting

Both heatmap views support selection highlighting:

- **Blue colorscale** (white → matplotlib blue `#1f77b4`): Unselected rows
- **Orange colorscale** (white → matplotlib orange `#ff7f0e`): Selected rows

Selection is determined by a `selection` column where values of `1`, `True`, `'1'`, `'True'`, or `'true'` indicate selected rows.

## API Endpoints

### Get Embedding Columns
```
GET /api/view/heatmap/embedding/columns
```

Returns list of columns containing "embedding" in their name.

**Response:**
```json
{
  "success": true,
  "columns": ["text_embedding", "image_embedding"]
}
```

### Generate Embedding Heatmap
```
POST /api/view/heatmap/embedding
Content-Type: application/json

{
  "embedding_column": "text_embedding",
  "indices": [0, 1, 2, 3, 4]  // optional
}
```

**Response:**
```json
{
  "success": true,
  "plot": "<plotly json>"
}
```

### Get Numeric Columns
```
GET /api/view/heatmap/columns/available
```

Returns list of numeric columns.

**Response:**
```json
{
  "success": true,
  "columns": ["age", "score", "price"]
}
```

### Generate Columns Heatmap
```
POST /api/view/heatmap/columns
Content-Type: application/json

{
  "indices": [0, 1, 2, 3, 4],  // optional
  "columns": ["age", "score"]   // optional, defaults to all numeric
}
```

**Response:**
```json
{
  "success": true,
  "plot": "<plotly json>"
}
```

## Example Data Format

### Embedding Column
```python
df = pd.DataFrame({
    'text': ['hello', 'world'],
    'text_embedding': [
        [0.1, 0.2, 0.3, 0.4],
        [0.5, 0.6, 0.7, 0.8]
    ]
})
```

### With Selection
```python
df = pd.DataFrame({
    'text_embedding': [[0.1, 0.2], [0.3, 0.4]],
    'feature_1': [10, 20],
    'feature_2': [30, 40],
    'selection': [1, 0]  # first row selected
})
```

## Implementation Files

- **Backend Routes**: `embeddoor/views/heatmap.py`
- **Visualization Functions**: `embeddoor/visualization.py`
  - `create_heatmap_embedding()`
  - `create_heatmap_columns()`
- **Frontend**: `embeddoor/static/js/app.js`
  - `renderHeatmapEmbedding()`
  - `renderHeatmapColumns()`
  - `updateHeatmapEmbedding()`
  - `updateHeatmapColumns()`
