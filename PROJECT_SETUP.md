# Embeddoor Project - Complete Setup

## What is Embeddoor?

Embeddoor is a browser-based tool for embedding visualization and analysis, designed to run locally like Jupyter Lab, Streamlit, or Voila. It provides:

- **Dual-panel interface**: Interactive 2D/3D plots + customizable data views
- **Embedding creation**: Support for HuggingFace, OpenAI, Gemini models
- **Dimensionality reduction**: PCA, t-SNE, and UMAP
- **Interactive selection**: Lasso tool to select and annotate data points
- **Data persistence**: Save/load in Parquet format

## Project Structure

```
embeddoor/
├── embeddoor/              # Main application package
│   ├── app.py             # Flask application factory
│   ├── cli.py             # Command-line interface
│   ├── data_manager.py    # DataFrame operations
│   ├── routes.py          # REST API endpoints
│   ├── visualization.py   # Plotly plotting
│   ├── dimred.py          # Dimensionality reduction
│   ├── embeddings/        # Modular embedding framework
│   │   ├── base.py        # Abstract base class
│   │   └── providers/     # Concrete implementations
│   ├── static/            # CSS and JavaScript
│   └── templates/         # HTML templates
├── tests/                 # Test suite
├── examples/              # Example scripts
├── setup.py              # Package setup
├── pyproject.toml        # Modern Python packaging
├── requirements.txt      # Dependencies
└── Documentation files
```

## Installation Steps

### 1. Navigate to Project Directory
```powershell
cd c:\structure\code\embeddoor
```

### 2. Create Virtual Environment (Recommended)
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 3. Install the Package

**Option A: Basic Installation (Core features only)**
```powershell
pip install -e .
```

**Option B: With Embedding Support (Recommended)**
```powershell
pip install -e .[embeddings]
```

**Option C: Full Development Setup**
```powershell
pip install -e .[dev,embeddings]
```

## Quick Start

### 1. Create Sample Data
```powershell
cd examples
python create_sample_data.py
cd ..
```

### 2. Launch Embeddoor
```powershell
embeddoor
```

This will:
- Start the Flask server on http://localhost:5000
- Automatically open your browser
- Display the dual-panel interface

### 3. Load Data
- Click **File → Open** or the **Load** button
- Enter path: `c:\structure\code\embeddoor\examples\sample_data.csv`
- Click **Open**

### 4. Visualize
- **Left Panel**: Select X=value1, Y=value2, Hue=category
- Click **Update Plot**
- Use lasso tool to select points

### 5. Create Embeddings (Optional)
- **Embedding → Create Embedding**
- Source: text column
- Provider: dummy (for testing)
- Target: embedding

### 6. Apply Dimensionality Reduction
- **Dimensionality Reduction → Apply PCA**
- Source: embedding column
- Components: 2
- Target: pca

### 7. Save Results
- **File → Save as Parquet**
- Enter path: `output.parquet`

## Key Features

### File Operations
- **Load**: CSV and Parquet files
- **Save**: Parquet (preserves all data types)
- **Export**: CSV format

### Visualization
- **2D Plots**: Scatter plots with customizable markers
- **3D Plots**: Interactive 3D scatter plots
- **Hue Mapping**: Color by categorical or numerical column
- **Size Mapping**: Marker size by numerical column
- **Lasso Selection**: Interactive point selection

### Embedding Providers
- **Dummy**: Random embeddings for testing (no setup)
- **HuggingFace**: Sentence transformers (`pip install sentence-transformers`)
- **OpenAI**: GPT embeddings (`pip install openai`)
- **Gemini**: Google embeddings (`pip install google-generativeai`)

### Dimensionality Reduction
- **PCA**: Linear, fast, preserves variance
- **t-SNE**: Non-linear, good for visualization
- **UMAP**: Non-linear, preserves global structure

## Command-Line Options

```powershell
# Run on different port
embeddoor --port 8080

# Don't auto-open browser
embeddoor --no-browser

# Enable debug mode
embeddoor --debug

# Bind to all interfaces
embeddoor --host 0.0.0.0 --port 5000
```

## Testing

Run the test suite:
```powershell
pytest
```

Run with coverage:
```powershell
pytest --cov=embeddoor --cov-report=html
```

## Extending Embeddoor

### Adding Custom Embedding Providers

1. Create file: `embeddoor/embeddings/providers/my_provider.py`
```python
from embeddoor.embeddings.base import EmbeddingProvider
import numpy as np

class MyProvider(EmbeddingProvider):
    def embed(self, texts):
        # Your embedding logic
        return np.array(embeddings)
```

2. Register in `embeddoor/embeddings/__init__.py`:
```python
from embeddoor.embeddings import register_provider
from embeddoor.embeddings.providers.my_provider import MyProvider

register_provider('my_provider', MyProvider)
```

## Architecture

### Backend (Python/Flask)
- **Flask**: Web framework
- **Pandas**: Data manipulation
- **NumPy**: Numerical operations
- **Scikit-learn**: PCA and t-SNE
- **UMAP**: Advanced dimensionality reduction
- **Plotly**: Interactive plotting

### Frontend (JavaScript)
- **Vanilla JavaScript**: No framework dependencies
- **Plotly.js**: Interactive charts
- **Responsive CSS**: Clean, modern interface

### Data Flow
```
CSV/Parquet → DataManager → API Routes → Frontend
                  ↓
            Embeddings → DimRed → Visualization
```

## Troubleshooting

### Port Already in Use
```powershell
embeddoor --port 8080
```

### Module Import Errors
```powershell
pip install -e .
```

### Missing Embedding Dependencies
```powershell
pip install sentence-transformers  # HuggingFace
pip install openai                 # OpenAI
pip install google-generativeai    # Gemini
```

### UMAP Not Found
```powershell
pip install umap-learn
```

## Performance Tips

1. **Large Datasets**: Use sampling for initial exploration
2. **Embeddings**: Start with smaller models (e.g., MiniLM)
3. **t-SNE**: Reduce perplexity for large datasets
4. **UMAP**: Faster than t-SNE for large datasets

## Next Steps

- Implement image grid visualization
- Add word cloud generation
- Create more embedding providers
- Add data transformation tools
- Implement session persistence
- Add export to various formats

## Documentation

- **README.md**: Overview and features
- **QUICKSTART.md**: Step-by-step tutorial
- **DEVELOPMENT.md**: Architecture and extension guide
- **CHANGELOG.md**: Version history

## License

MIT License - See LICENSE file

## Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Add tests for new features
4. Submit a pull request

---

**Built with ❤️ for data scientists and ML engineers**
