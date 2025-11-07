# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2025-11-07

### Added
- Initial release of Embeddoor
- Browser-based dual-panel interface
- CSV and Parquet file support
- 2D and 3D plotting with Plotly
- Interactive lasso selection tool
- Modular embedding framework
  - Dummy provider for testing
  - HuggingFace/Sentence Transformers support
  - OpenAI API integration
  - Google Gemini API integration
- Dimensionality reduction methods
  - PCA (Principal Component Analysis)
  - t-SNE (t-distributed Stochastic Neighbor Embedding)
  - UMAP (Uniform Manifold Approximation and Projection)
- Data visualization controls
  - Hue mapping
  - Size mapping
  - Shape mapping (planned)
- Toolbar with 100x100px buttons
- Menu system for File, Embedding, and Dimensionality Reduction operations
- Command-line interface
- Flask-based REST API
- Comprehensive test suite
- Example scripts and documentation

### Features
- Load and visualize tabular data
- Create embeddings from text columns
- Apply dimensionality reduction to embeddings
- Interactive point selection and annotation
- Save work in Parquet format

[0.1.0]: https://github.com/yourusername/embeddoor/releases/tag/v0.1.0
