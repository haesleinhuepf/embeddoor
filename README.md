# Embeddoor

A browser-based tool for embedding visualization and analysis, similar to Jupyter Lab, Streamlit, or Voila.

## Features

- **Dual-panel interface**: 2D/3D plots on the left, custom visualizations (tables, images, word clouds) on the right
- **Interactive data exploration**: Load CSV files, visualize tabular data, and plot 2-3 numerical columns
- **Advanced plot controls**: Configure hue, size, and shape based on data columns
- **Lasso selection**: Select data points interactively and store selections in the dataframe
- **Modular embedding framework**: Create embeddings using HuggingFace, OpenAI, Gemini, and custom models
- **Dimensionality reduction**: Apply PCA, t-SNE, and UMAP to high-dimensional embeddings
- **Data persistence**: Save and load data in Parquet format

## Installation

### Basic Installation

```bash
pip install embeddoor
```

### With Embedding Support

```bash
pip install embeddoor[embeddings]
```

### Development Installation

```bash
git clone https://github.com/yourusername/embeddoor.git
cd embeddoor
pip install -e .[dev,embeddings]
```

## Quick Start

Launch the application:

```bash
embeddoor
```

This will start the server and open your default browser to `http://localhost:5000`.

## Workflow

1. **Load Data**: Use File → Open to load a CSV file
2. **Visualize**: View tabular data in the right panel, plot numerical columns in the left panel
3. **Customize Plot**: Select hue, size, and shape attributes for data points
4. **Select Points**: Use the lasso tool to select data points (stored as a new column)
5. **Create Embeddings**: Embedding → Create Embedding to generate embeddings from text/image columns
6. **Reduce Dimensions**: Dimensionality Reduction → Apply PCA/t-SNE/UMAP to embeddings
7. **Save**: File → Save to export data as Parquet

## Extending Embeddoor

### Adding Custom Embedding Models

Create a new embedding provider in `embeddoor/embeddings/providers/`:

```python
from embeddoor.embeddings.base import EmbeddingProvider

class CustomEmbedding(EmbeddingProvider):
    def __init__(self, model_name, **kwargs):
        super().__init__(model_name, **kwargs)
        # Initialize your model
    
    def embed(self, texts):
        # Return list of embeddings (numpy arrays)
        pass
```

Register your provider in `embeddoor/embeddings/__init__.py`.

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
