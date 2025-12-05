# Embeddoor

A browser-based tool for embedding visualization and analysis.

![](docs/images/embeddoor-teaser.gif)

![](logo.png)

## Features

- **Dual-panel interface**: 2D/3D plots on the left, custom visualizations (tables, images, word clouds) on the right
- **Interactive data exploration**: Load CSV files, visualize tabular data, and plot 2-3 numerical columns
- **Advanced plot controls**: Configure hue, size, and shape based on data columns
- **Lasso selection**: Select data points interactively and store selections in the dataframe
- **Correlation analysis**: Visualize pairwise correlations with Pearson, Spearman, or Kendall methods
- **Heatmap visualizations**: View data as heatmaps from embeddings or numeric columns
- **Modular embedding framework**: Create embeddings using HuggingFace, OpenAI, Gemini, and custom models
- **Dimensionality reduction**: Apply PCA, t-SNE, and UMAP to high-dimensional embeddings
- **Data persistence**: Save and load data in Parquet format

## Installation

```bash
pip install embeddoor
```

### Development Installation

```bash
git clone https://github.com/haesleinhuepf/embeddoor.git
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

## License

MIT License

## Notes

* embeddor is in early development. Be careful when using it, check its visualisations and expect changes with every new version.
* Most of the code in this repository was vibe-coded using Github copilot integration in Visual Studio Code. When modifying code here, consider using a similar tool. 

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
