# Views Module - API Reference

## Overview
The `embeddoor/views/` module contains modular view handlers for different visualization types. Each view is a separate Python file that registers its own Flask routes.

## Module Structure

```
embeddoor/views/
├── __init__.py          # Module initialization and route registration
├── plot.py              # Plot visualization endpoints
├── table.py             # Table visualization endpoints
├── wordcloud.py         # Word cloud generation endpoints
└── images.py            # Image gallery endpoints
```

## API Endpoints

### Plot View (`plot.py`)

#### `POST /api/view/plot`
Generate a plot visualization.

**Request Body:**
```json
{
  "x": "column_name",          // Required: X-axis column
  "y": "column_name",          // Optional: Y-axis column
  "z": "column_name",          // Optional: Z-axis column (for 3D)
  "hue": "column_name",        // Optional: Color mapping column
  "size": "column_name",       // Optional: Size mapping column
  "type": "2d|3d"              // Plot type (default: "2d")
}
```

**Response:**
```json
{
  "success": true,
  "plot": "...plotly JSON string..."
}
```

#### `POST /api/selection/save`
Save lasso selection as a new column.

**Request Body:**
```json
{
  "column_name": "selection",  // Name for selection column
  "indices": [0, 1, 2, 3]      // List of selected row indices
}
```

**Response:**
```json
{
  "success": true,
  "message": "Selection saved"
}
```

---

### Table View (`table.py`)

#### `GET /api/view/table?n=100&start=0`
Get table view as HTML.

**Query Parameters:**
- `n` (int, default: 100): Number of rows to display
- `start` (int, default: 0): Starting row index

**Response:** HTML string (text/html)

#### `GET /api/view/table/info`
Get table metadata.

**Response:**
```json
{
  "success": true,
  "total_rows": 1000,
  "total_columns": 10,
  "columns": ["col1", "col2", ...],
  "dtypes": {
    "col1": "int64",
    "col2": "object",
    ...
  }
}
```

---

### Word Cloud View (`wordcloud.py`)

#### `POST /api/view/wordcloud`
Generate word cloud image.

**Request Body:**
```json
{
  "indices": [0, 1, 2],        // Optional: Row indices to include
  "text_column": "text",       // Optional: Text column (auto-detects if not provided)
  "width": 800,                // Optional: Image width (default: 800)
  "height": 500                // Optional: Image height (default: 500)
}
```

**Response:** PNG image (image/png)

#### `GET /api/view/wordcloud/columns`
Get available text columns.

**Response:**
```json
{
  "success": true,
  "columns": ["text", "description", "title"]
}
```

---

### Images View (`images.py`)

#### `POST /api/view/images`
Get image gallery data.

**Request Body:**
```json
{
  "indices": [0, 1, 2],        // Optional: Row indices to display
  "image_column": "image",     // Optional: Image column (auto-detects if not provided)
  "max_images": 50             // Optional: Max images to return (default: 50)
}
```

**Response:**
```json
{
  "success": true,
  "images": [
    {
      "index": 0,
      "type": "base64|url|path",
      "data": "data:image/png;base64,...",  // For base64 type
      "url": "https://...",                  // For url type
      "path": "/path/to/image.jpg",          // For path type
      "error": "..."                         // If loading failed
    },
    ...
  ],
  "total": 10,
  "column": "image"
}
```

#### `GET /api/view/images/columns`
Get available image columns.

**Response:**
```json
{
  "success": true,
  "columns": ["image", "img_path", "photo"]
}
```

---

## Adding a New View

To add a new view type (e.g., "chart"):

### 1. Create the view file

**`embeddoor/views/chart.py`:**
```python
"""Chart view module for embeddoor."""

from flask import jsonify, request

def register_chart_routes(app):
    """Register chart-related routes."""
    
    @app.route('/api/view/chart', methods=['POST'])
    def generate_chart():
        """Generate a chart visualization."""
        config = request.json
        
        # Your chart generation logic here
        
        return jsonify({
            'success': True,
            'chart': chart_data
        })
```

### 2. Update `__init__.py`

**`embeddoor/views/__init__.py`:**
```python
from embeddoor.views.chart import register_chart_routes  # Add import

def register_all_views(app):
    """Register all view routes with the Flask app."""
    # ... existing registrations ...
    register_chart_routes(app)  # Add this line
```

### 3. Update frontend

**In `FloatingPanel` class (`app.js`):**
```javascript
// Add to createElement() dropdown options
<option value="chart">Chart</option>

// Add to updateContent() switch statement
case 'chart':
    await this.renderChart(body);
    break;

// Add rendering method
async renderChart(body) {
    body.innerHTML = `
        <div class="chart-controls">
            <!-- Your controls here -->
        </div>
        <div class="chart-container">
            <!-- Chart content here -->
        </div>
    `;
    
    // Fetch and display chart
    const response = await fetch('/api/view/chart', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ /* config */ })
    });
    
    const result = await response.json();
    // Render chart
}
```

### 4. Update CSS (if needed)

**`style.css`:**
```css
.chart-container {
    width: 100%;
    height: 100%;
}
```

---

## View Module Best Practices

### 1. Error Handling
Always return proper error responses:
```python
if not valid_input:
    return jsonify({'error': 'Descriptive error message'}), 400
```

### 2. Data Validation
Validate inputs before processing:
```python
if app.data_manager.df is None:
    return jsonify({'error': 'No data loaded'}), 404
```

### 3. Documentation
Document all endpoints with:
- Purpose description
- Request format
- Response format
- Error conditions

### 4. Type Hints
Use Python type hints:
```python
def register_routes(app: Flask) -> None:
    """Register routes."""
    pass
```

### 5. Resource Cleanup
Clean up resources properly:
```python
try:
    # Process data
    result = process()
except Exception as e:
    return jsonify({'error': str(e)}), 500
finally:
    # Clean up resources
    pass
```

---

## Testing Views

### Unit Testing
Test each view independently:

```python
import pytest
from embeddoor.app import create_app

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_plot_endpoint(client):
    response = client.post('/api/view/plot', json={
        'x': 'col1',
        'y': 'col2'
    })
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] == True
    assert 'plot' in data
```

### Integration Testing
Test view interaction with data manager:

```python
def test_plot_with_data(client, sample_data):
    # Load sample data
    client.post('/api/data/load', json={'filepath': sample_data})
    
    # Generate plot
    response = client.post('/api/view/plot', json={
        'x': 'x_col',
        'y': 'y_col'
    })
    
    assert response.status_code == 200
```

---

## Common Patterns

### Auto-Detection
Many views auto-detect suitable columns:

```python
# Auto-detect text columns
text_cols = list(df.select_dtypes(include=['object', 'string', 'category']).columns)

# Auto-detect numeric columns
numeric_cols = list(df.select_dtypes(include=['int64', 'float64']).columns)

# Auto-detect image columns (check file extensions)
for col in df.columns:
    sample = str(df[col].iloc[0])
    if any(ext in sample.lower() for ext in ['.jpg', '.png']):
        image_columns.append(col)
```

### Index Handling
Handle both positional and label-based indices:

```python
if indices:
    try:
        # Try label-based indexing
        sel_index = pd.Index(indices)
        sel_index = sel_index.astype(df.index.dtype)
        subset = df.loc[sel_index]
    except Exception:
        # Fallback to positional
        subset = df.iloc[indices]
else:
    subset = df
```

### Configuration Storage
Store view-specific config in panel instances:

```javascript
// In FloatingPanel class
this.config = {
    plot: { x: 'col1', y: 'col2', hue: null },
    table: { start: 0, n: 100 },
    wordcloud: { text_column: 'text' }
};
```

---

## Performance Considerations

1. **Limit Data Transfer**: Don't send entire datasets to frontend
2. **Pagination**: Implement for large datasets (table view)
3. **Caching**: Cache expensive computations
4. **Async Operations**: Use async for I/O operations
5. **Lazy Loading**: Load images/data on demand

---

## Security Considerations

1. **Input Validation**: Always validate user inputs
2. **Path Traversal**: Validate file paths
3. **SQL Injection**: Use parameterized queries (if applicable)
4. **File Access**: Restrict to allowed directories
5. **Resource Limits**: Limit memory/time for operations
