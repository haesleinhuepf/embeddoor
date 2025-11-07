# Embeddoor Development Guide

## Project Structure

```
embeddoor/
├── embeddoor/                 # Main package
│   ├── __init__.py
│   ├── app.py                # Flask application
│   ├── cli.py                # Command-line interface
│   ├── data_manager.py       # Data handling
│   ├── routes.py             # API routes
│   ├── visualization.py      # Plotting functions
│   ├── dimred.py             # Dimensionality reduction
│   ├── embeddings/           # Embedding framework
│   │   ├── __init__.py
│   │   ├── base.py
│   │   └── providers/        # Embedding providers
│   │       ├── __init__.py
│   │       ├── huggingface.py
│   │       ├── openai_provider.py
│   │       └── gemini.py
│   ├── static/               # Static assets
│   │   ├── css/
│   │   │   └── style.css
│   │   └── js/
│   │       └── app.js
│   └── templates/            # HTML templates
│       └── index.html
├── tests/                    # Test suite
├── examples/                 # Example scripts
├── setup.py                  # Setup script
├── pyproject.toml           # Project configuration
├── requirements.txt         # Dependencies
└── README.md                # Documentation
```

## Setting Up Development Environment

1. Create a virtual environment:
```bash
python -m venv venv
venv\Scripts\activate  # Windows
```

2. Install in development mode:
```bash
pip install -e .[dev,embeddings]
```

3. Run tests:
```bash
pytest
```

## Architecture

### Backend (Flask)
- **app.py**: Main Flask application factory
- **routes.py**: REST API endpoints
- **data_manager.py**: DataFrame operations
- **visualization.py**: Plotly chart generation
- **dimred.py**: PCA, t-SNE, UMAP implementations

### Frontend (Vanilla JS + Plotly)
- **index.html**: Single-page application
- **app.js**: JavaScript application logic
- **style.css**: Responsive CSS styling

### Embedding System
The embedding system is modular and extensible:

1. **Base Class** (`base.py`): Abstract `EmbeddingProvider` class
2. **Providers**: Concrete implementations (HuggingFace, OpenAI, Gemini)
3. **Registry**: Dynamic provider registration

#### Adding a New Provider

Create a new file in `embeddoor/embeddings/providers/`:

```python
from embeddoor.embeddings.base import EmbeddingProvider
import numpy as np

class CustomProvider(EmbeddingProvider):
    def __init__(self, model_name, **kwargs):
        super().__init__(model_name, **kwargs)
        # Initialize your model
    
    def embed(self, texts):
        # Generate embeddings
        return np.array(embeddings)
    
    def embed_batch(self, texts, batch_size=32):
        # Batch processing
        return self.embed(texts)
```

Register in `embeddoor/embeddings/__init__.py`:

```python
from embeddoor.embeddings import register_provider
from embeddoor.embeddings.providers.custom import CustomProvider

register_provider('custom', CustomProvider)
```

## API Endpoints

### Data Management
- `POST /api/data/load`: Load CSV/Parquet file
- `POST /api/data/save`: Save to Parquet/CSV
- `GET /api/data/info`: Get dataset information
- `GET /api/data/sample`: Get data sample

### Visualization
- `POST /api/plot`: Generate plot configuration

### Embeddings
- `GET /api/embeddings/providers`: List providers
- `POST /api/embeddings/create`: Create embeddings

### Dimensionality Reduction
- `GET /api/dimred/methods`: List methods
- `POST /api/dimred/apply`: Apply reduction

### Selection
- `POST /api/selection/save`: Save lasso selection

## Testing

Run the full test suite:
```bash
pytest
```

Run with coverage:
```bash
pytest --cov=embeddoor
```

Run specific tests:
```bash
pytest tests/test_data_manager.py
```

## Building and Distribution

Build the package:
```bash
python -m build
```

Install locally:
```bash
pip install dist/embeddoor-0.1.0-py3-none-any.whl
```

## Future Enhancements

1. **Image Visualization**: Display image grids in right panel
2. **Word Clouds**: Generate word clouds from text columns
3. **More Embedding Providers**: Add support for Cohere, Anthropic, etc.
4. **Advanced Selection**: Multiple selection sets, boolean operations
5. **Data Transformations**: Filtering, aggregation, pivoting
6. **Export Options**: Export to various formats (JSON, Excel, etc.)
7. **Collaboration**: Share sessions, annotations
8. **Plugin System**: Load custom visualization plugins

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details
