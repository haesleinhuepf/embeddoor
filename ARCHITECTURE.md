# Embeddoor Architecture Diagram

## System Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                         EMBEDDOOR APPLICATION                        │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                            FRONTEND (Browser)                        │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  ┌───────────────────────────────────────────────────────────┐     │
│  │                   Menu Bar (File, Embedding, DimRed)       │     │
│  └───────────────────────────────────────────────────────────┘     │
│                                                                       │
│  ┌───────────────────────────────────────────────────────────┐     │
│  │   Toolbar: [Load] [Save] [Refresh] [Settings] (100x100px) │     │
│  └───────────────────────────────────────────────────────────┘     │
│                                                                       │
│  ┌─────────────────────────┬─────────────────────────────────┐     │
│  │   LEFT PANEL            │   RIGHT PANEL                    │     │
│  │   ┌──────────────────┐  │   ┌──────────────────────────┐  │     │
│  │   │ 2D/3D Plot       │  │   │  Data Table View         │  │     │
│  │   │ (Plotly.js)      │  │   │  or Image Grid           │  │     │
│  │   │                  │  │   │  or Word Cloud           │  │     │
│  │   │ - Scatter plot   │  │   │                          │  │     │
│  │   │ - Hue/Size map   │  │   │  - Scrollable            │  │     │
│  │   │ - Lasso select   │  │   │  - Sortable columns      │  │     │
│  │   │ - Interactive    │  │   │  - 100 rows preview      │  │     │
│  │   └──────────────────┘  │   └──────────────────────────┘  │     │
│  │                         │                                  │     │
│  │   Controls:             │   Controls:                      │     │
│  │   X: [dropdown]         │   View: [Table▾]                │     │
│  │   Y: [dropdown]         │                                  │     │
│  │   Z: [dropdown]         │                                  │     │
│  │   Hue: [dropdown]       │                                  │     │
│  │   Size: [dropdown]      │                                  │     │
│  │   [Update Plot]         │                                  │     │
│  └─────────────────────────┴─────────────────────────────────┘     │
│                                                                       │
│  ┌───────────────────────────────────────────────────────────┐     │
│  │  Status Bar: Ready | 1000 rows × 15 columns                │     │
│  └───────────────────────────────────────────────────────────┘     │
│                                                                       │
│  JavaScript (app.js) - Event Handlers, API Calls, State Mgmt       │
└───────────────────────────────┬───────────────────────────────────┘
                                │ HTTP/JSON
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        BACKEND (Flask Server)                        │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  ┌───────────────────────────────────────────────────────────┐     │
│  │                    REST API (routes.py)                    │     │
│  │                                                             │     │
│  │  /api/data/load          Load CSV/Parquet                  │     │
│  │  /api/data/save          Save to Parquet                   │     │
│  │  /api/data/info          Get dataset info                  │     │
│  │  /api/data/sample        Get data preview                  │     │
│  │  /api/plot               Generate plot JSON                │     │
│  │  /api/selection/save     Save lasso selection              │     │
│  │  /api/embeddings/...     Embedding operations              │     │
│  │  /api/dimred/...         Dimensionality reduction          │     │
│  └───────────────┬───────────────────────┬────────────────────┘     │
│                  │                       │                           │
│                  ▼                       ▼                           │
│  ┌──────────────────────┐  ┌───────────────────────────────┐       │
│  │   data_manager.py    │  │     visualization.py           │       │
│  │                      │  │                                 │       │
│  │  - load_csv()        │  │  - create_plot()               │       │
│  │  - load_parquet()    │  │  - create_table_html()         │       │
│  │  - save_parquet()    │  │  - Plotly figure generation    │       │
│  │  - get_data_info()   │  │                                 │       │
│  │  - add_selection()   │  └─────────────────────────────────┘       │
│  │  - add_embedding()   │                                             │
│  │  - add_dimred()      │                                             │
│  │                      │                                             │
│  │  DataFrame: self.df  │                                             │
│  └──────────┬───────────┘                                             │
│             │                                                          │
│             ▼                                                          │
│  ┌─────────────────────────────────────────────────────────┐         │
│  │                  Pandas DataFrame                        │         │
│  │                                                           │         │
│  │  Columns:                                                 │         │
│  │  - Original data (a, b, c, ...)                          │         │
│  │  - Selections (selection_1, selection_2, ...)            │         │
│  │  - Embeddings (embedding_text, embedding_img, ...)       │         │
│  │  - Dim-reduced (pca_1, pca_2, tsne_1, umap_1, ...)      │         │
│  └─────────────────────────────────────────────────────────┘         │
│                                                                         │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                      EMBEDDING FRAMEWORK                             │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  ┌───────────────────────────────────────────────────────────┐     │
│  │              embeddings/__init__.py (Registry)             │     │
│  │                                                             │     │
│  │  _PROVIDERS = {                                            │     │
│  │    'dummy': DummyEmbedding,                                │     │
│  │    'huggingface': HuggingFaceEmbedding,                    │     │
│  │    'openai': OpenAIEmbedding,                              │     │
│  │    'gemini': GeminiEmbedding,                              │     │
│  │  }                                                          │     │
│  │                                                             │     │
│  │  create_embeddings(texts, provider, model)                 │     │
│  └───────────────────────────────────────────────────────────┘     │
│                                                                       │
│  ┌───────────────────────────────────────────────────────────┐     │
│  │           embeddings/base.py (Abstract Base)               │     │
│  │                                                             │     │
│  │  class EmbeddingProvider(ABC):                             │     │
│  │    @abstractmethod                                          │     │
│  │    def embed(texts) -> np.ndarray                          │     │
│  │    def embed_batch(texts, batch_size)                      │     │
│  └───────────────────────────────────────────────────────────┘     │
│                                                                       │
│  ┌──────────────┬──────────────┬──────────────┬─────────────┐      │
│  │   Dummy      │ HuggingFace  │   OpenAI     │   Gemini    │      │
│  │              │              │              │             │      │
│  │ Random       │ Sentence     │ API client   │ API client  │      │
│  │ embeddings   │ Transformers │ embeddings   │ embeddings  │      │
│  │              │              │              │             │      │
│  │ No deps      │ + torch      │ + openai     │ + genai     │      │
│  └──────────────┴──────────────┴──────────────┴─────────────┘      │
│                                                                       │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│               DIMENSIONALITY REDUCTION (dimred.py)                   │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  apply_dimred(embeddings, method, n_components, **params)           │
│                                                                       │
│  ┌──────────────┬──────────────┬──────────────┐                    │
│  │     PCA      │    t-SNE     │     UMAP     │                    │
│  │              │              │              │                    │
│  │ Linear       │ Non-linear   │ Non-linear   │                    │
│  │ Fast         │ Slow         │ Fast         │                    │
│  │ Global       │ Local        │ Both         │                    │
│  │              │              │              │                    │
│  │ sklearn      │ sklearn      │ umap-learn   │                    │
│  └──────────────┴──────────────┴──────────────┘                    │
│                                                                       │
│  Returns: np.ndarray of shape (n_samples, n_components)             │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                      DATA FLOW DIAGRAM                               │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  1. LOAD DATA                                                        │
│     CSV/Parquet → DataManager.load_csv() → Pandas DataFrame         │
│                                                                       │
│  2. VISUALIZE                                                        │
│     DataFrame → get_plot_data() → create_plot() → Plotly JSON       │
│     → Frontend → Plotly.newPlot() → Interactive Chart                │
│                                                                       │
│  3. LASSO SELECTION                                                  │
│     User drags lasso → Plotly event → JavaScript handler            │
│     → API call → add_selection_column() → New boolean column        │
│                                                                       │
│  4. CREATE EMBEDDINGS                                                │
│     Text column → EmbeddingProvider.embed_batch() → Embeddings      │
│     → add_embedding_column() → New array column                      │
│                                                                       │
│  5. DIMENSIONALITY REDUCTION                                         │
│     Embedding column → apply_dimred() → Reduced vectors             │
│     → add_dimred_columns() → New numeric columns                     │
│                                                                       │
│  6. VISUALIZE REDUCED                                                │
│     Reduced columns → create_plot() → 2D/3D visualization            │
│                                                                       │
│  7. SAVE                                                             │
│     DataFrame → save_parquet() → .parquet file                       │
│                                                                       │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                    TECHNOLOGY STACK                                  │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  Backend:                                                            │
│  ┌─────────────────┬─────────────────┬─────────────────┐           │
│  │ Flask 2.3+      │ Pandas 2.0+     │ NumPy 1.24+     │           │
│  │ Web framework   │ Data handling   │ Numerical       │           │
│  └─────────────────┴─────────────────┴─────────────────┘           │
│  ┌─────────────────┬─────────────────┬─────────────────┐           │
│  │ Plotly 5.14+    │ Scikit-learn    │ PyArrow 12+     │           │
│  │ Visualization   │ ML algorithms   │ Parquet I/O     │           │
│  └─────────────────┴─────────────────┴─────────────────┘           │
│                                                                       │
│  Frontend:                                                           │
│  ┌─────────────────┬─────────────────┬─────────────────┐           │
│  │ Vanilla JS      │ Plotly.js       │ CSS3            │           │
│  │ No frameworks   │ Interactive     │ Responsive      │           │
│  └─────────────────┴─────────────────┴─────────────────┘           │
│                                                                       │
│  Optional:                                                           │
│  ┌─────────────────┬─────────────────┬─────────────────┐           │
│  │ Transformers    │ OpenAI API      │ Gemini API      │           │
│  │ HF embeddings   │ GPT embeddings  │ Google embed    │           │
│  └─────────────────┴─────────────────┴─────────────────┘           │
│  ┌─────────────────┬─────────────────┬─────────────────┐           │
│  │ UMAP-learn      │ Torch           │ Pillow          │           │
│  │ Dim reduction   │ DL backend      │ Image handling  │           │
│  └─────────────────┴─────────────────┴─────────────────┘           │
│                                                                       │
└─────────────────────────────────────────────────────────────────────┘
```

## Component Interactions

### Workflow 1: Loading and Visualizing Data
```
User clicks "Open"
    ↓
Frontend: showFileDialog()
    ↓
User enters path, clicks OK
    ↓
Frontend: POST /api/data/load
    ↓
Backend: DataManager.load_csv()
    ↓
Backend: Returns {success, shape, columns}
    ↓
Frontend: updateUI(), populateSelectors()
    ↓
User selects X, Y columns
    ↓
Frontend: POST /api/plot
    ↓
Backend: create_plot() → Plotly JSON
    ↓
Frontend: Plotly.newPlot()
    ↓
Interactive chart displayed
```

### Workflow 2: Embedding Creation
```
User clicks "Create Embedding"
    ↓
Frontend: showEmbeddingDialog()
    ↓
User configures: source column, provider, model
    ↓
Frontend: POST /api/embeddings/create
    ↓
Backend: create_embeddings() → np.ndarray
    ↓
Backend: DataManager.add_embedding_column()
    ↓
Backend: Returns {success, column, shape}
    ↓
Frontend: Updates data info
```

### Workflow 3: Dimensionality Reduction
```
User clicks "Apply PCA"
    ↓
Frontend: showDimRedDialog()
    ↓
User configures: source, components, params
    ↓
Frontend: POST /api/dimred/apply
    ↓
Backend: apply_dimred() → np.ndarray
    ↓
Backend: DataManager.add_dimred_columns()
    ↓
Backend: Returns {success, columns: [pca_1, pca_2]}
    ↓
Frontend: Updates column selectors
    ↓
User plots reduced dimensions
```

## Modular Design

### Why This Architecture?

1. **Separation of Concerns**
   - Frontend handles UI/UX
   - Backend handles data processing
   - Clear API boundary

2. **Extensibility**
   - Easy to add new embedding providers
   - Simple to add new dim-red methods
   - Modular visualization components

3. **Testability**
   - Each component can be tested independently
   - Mock API calls for frontend tests
   - Unit tests for backend logic

4. **Scalability**
   - Can replace Flask with FastAPI
   - Can add caching layer
   - Can distribute computation

5. **Maintainability**
   - Clear file organization
   - Well-documented interfaces
   - Consistent naming conventions
