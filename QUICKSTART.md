# Quick Start Guide

## Installation

### Option 1: Basic Installation (Core Features)
```bash
cd embeddoor
pip install -e .
```

### Option 2: With Embedding Support
```bash
pip install -e .[embeddings]
```

### Option 3: Development Installation
```bash
pip install -e .[dev,embeddings]
```

## Running Embeddoor

Start the application:
```bash
embeddoor
```

This will:
1. Start a Flask server on http://localhost:5000
2. Automatically open your browser

To run without auto-opening browser:
```bash
embeddoor --no-browser
```

To run on a different port:
```bash
embeddoor --port 8080
```

## Creating Sample Data

Run the example script to create sample data:
```bash
cd examples
python create_sample_data.py
```

This creates `sample_data.csv` in the examples directory.

## Basic Workflow

### 1. Load Data
- Click **File → Open CSV/Parquet** or use the **Load** toolbar button
- Enter the full path to your CSV file (e.g., `C:\data\myfile.csv`)
- Click **Open**

### 2. Visualize Data
**Left Panel (Plot):**
- Select columns for X, Y (and optionally Z for 3D)
- Choose Hue, Size, or Shape for additional dimensions
- Click **Update Plot**

**Right Panel (Data View):**
- View tabular data
- Switch between Table, Images, or Word Cloud views

### 3. Interactive Selection
- Use the **lasso tool** in the plot to select data points
- Drag around points you want to select
- When prompted, enter a column name to save the selection
- Selected points are stored as a boolean column in your dataframe

### 4. Create Embeddings
- Click **Embedding → Create Embedding**
- Select a source column (text or data to embed)
- Choose a provider (Dummy for testing, or install embedding packages)
- Enter a target column name
- Click **Create**

**Available Providers:**
- **Dummy**: Random embeddings for testing (no setup required)
- **HuggingFace**: Requires `pip install sentence-transformers`
- **OpenAI**: Requires `pip install openai` and API key
- **Gemini**: Requires `pip install google-generativeai` and API key

### 5. Dimensionality Reduction
- Click **Dimensionality Reduction → Apply PCA/t-SNE/UMAP**
- Select the embedding column as source
- Choose number of components (2 for 2D visualization, 3 for 3D)
- Enter a base name for the new columns
- Click **Apply**

The reduced dimensions will be added as new columns (e.g., `pca_1`, `pca_2`)

### 6. Save Your Work
- Click **File → Save as Parquet** or use the **Save** toolbar button
- Enter the output path
- Click **Save**

Parquet format preserves all data types including embedding arrays.

## Example Session

```python
# 1. Create sample data
cd examples
python create_sample_data.py

# 2. Start embeddoor
cd ..
embeddoor

# 3. In the browser:
#    - Load: examples\sample_data.csv
#    - Plot: X=value1, Y=value2, Hue=category
#    - Select points with lasso tool
#    - Create dummy embeddings on 'text' column
#    - Apply PCA to reduce embeddings to 2D
#    - Plot: X=pca_1, Y=pca_2, Hue=category
#    - Save as output.parquet
```

## Keyboard Shortcuts

- **Ctrl+O**: Open file dialog
- **Ctrl+S**: Save file dialog
- **Ctrl+R**: Refresh view

## Troubleshooting

### "Module not found" errors
Make sure you've installed the package:
```bash
pip install -e .
```

### Embedding creation fails
Install the required embedding packages:
```bash
pip install sentence-transformers  # For HuggingFace
pip install openai                 # For OpenAI
pip install google-generativeai    # For Gemini
```

### UMAP not working
Install UMAP:
```bash
pip install umap-learn
```

### Port already in use
Run on a different port:
```bash
embeddoor --port 8080
```

### Browser doesn't open
Navigate manually to http://localhost:5000 or use:
```bash
embeddoor --no-browser
```

## Tips

1. **Start Simple**: Use the dummy embedding provider first to test the workflow
2. **Save Often**: Parquet files are efficient and preserve all data
3. **Column Names**: Use descriptive names for embedding and dimred columns
4. **Performance**: For large datasets (>10k rows), consider sampling first
5. **3D Plots**: Use Z-axis for true 3D visualization of PCA/t-SNE/UMAP results

## Next Steps

- Read DEVELOPMENT.md for architecture details
- Check examples/ for more complex workflows
- Extend with custom embedding providers
- Contribute on GitHub!

## Support

- GitHub Issues: [Report bugs or request features]
- Documentation: See README.md and DEVELOPMENT.md
