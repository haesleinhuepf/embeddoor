// Embeddoor JavaScript Application - Floating Panels

class FloatingPanel {
    constructor(id, type, title, x, y, width, height) {
        this.id = id;
        this.type = type;
        this.title = title;
        this.x = x;
        this.y = y;
        this.width = width;
        this.height = height;
        this.minimized = false;
        this.element = null;
        this.isDragging = false;
        this.isResizing = false;
        this.dragOffsetX = 0;
        this.dragOffsetY = 0;
        this.config = {}; // View-specific configuration
        this.selectedIndices = []; // For selection-based views
    }

    createElement() {
        const panel = document.createElement('div');
        panel.className = 'floating-panel';
        panel.id = `panel-${this.id}`;
        panel.style.left = `${this.x}px`;
        panel.style.top = `${this.y}px`;
        panel.style.width = `${this.width}px`;
        panel.style.height = `${this.height}px`;

        const header = document.createElement('div');
        header.className = 'panel-header';
        header.innerHTML = `
            <h2>
                <span class="panel-title">${this.title}</span>
            </h2>
            <div class="panel-header-controls">
                <select class="panel-view-selector">
                    <option value="plot" ${this.type === 'plot' ? 'selected' : ''}>Plot</option>
                    <option value="table" ${this.type === 'table' ? 'selected' : ''}>Table</option>
                    <option value="wordcloud" ${this.type === 'wordcloud' ? 'selected' : ''}>Word Cloud</option>
                    <option value="images" ${this.type === 'images' ? 'selected' : ''}>Images</option>
                    <option value="heatmap-embedding" ${this.type === 'heatmap-embedding' ? 'selected' : ''}>Heatmap (Embedding)</option>
                    <option value="heatmap-columns" ${this.type === 'heatmap-columns' ? 'selected' : ''}>Heatmap (Columns)</option>
                    <option value="terminal" ${this.type === 'terminal' ? 'selected' : ''}>IPython Terminal</option>
                </select>
                <button class="panel-btn" data-action="minimize" title="Minimize">−</button>
                <button class="panel-btn" data-action="close" title="Close">×</button>
            </div>
        `;

        const body = document.createElement('div');
        body.className = 'panel-body';
        body.innerHTML = '<p class="placeholder">Loading...</p>';

        const resizeHandle = document.createElement('div');
        resizeHandle.className = 'resize-handle';

        panel.appendChild(header);
        panel.appendChild(body);
        panel.appendChild(resizeHandle);

        this.element = panel;
        this.setupEventListeners();

        return panel;
    }

    setupEventListeners() {
        const header = this.element.querySelector('.panel-header');
        const resizeHandle = this.element.querySelector('.resize-handle');
        const viewSelector = this.element.querySelector('.panel-view-selector');
        const minimizeBtn = this.element.querySelector('[data-action="minimize"]');
        const closeBtn = this.element.querySelector('[data-action="close"]');

        // View type change
        viewSelector.addEventListener('change', (e) => {
            this.type = e.target.value;
            this.updateTitle();
            this.updateContent();
        });

        // Minimize
        minimizeBtn.addEventListener('click', () => this.toggleMinimize());

        // Close
        closeBtn.addEventListener('click', () => window.app.removePanel(this.id));

        // Dragging
        header.addEventListener('mousedown', (e) => {
            if (e.target.closest('.panel-view-selector') || e.target.closest('.panel-btn')) {
                return;
            }
            this.startDragging(e);
        });

        // Resizing
        resizeHandle.addEventListener('mousedown', (e) => {
            e.stopPropagation();
            this.startResizing(e);
        });

        // Bring to front on click
        this.element.addEventListener('mousedown', () => {
            window.app.bringPanelToFront(this.id);
        });
    }

    startDragging(e) {
        this.isDragging = true;
        this.dragOffsetX = e.clientX - this.x;
        this.dragOffsetY = e.clientY - this.y;
        this.element.classList.add('active');

        const onMouseMove = (e) => {
            if (!this.isDragging) return;
            this.x = e.clientX - this.dragOffsetX;
            this.y = e.clientY - this.dragOffsetY;
            this.element.style.left = `${this.x}px`;
            this.element.style.top = `${this.y}px`;
        };

        const onMouseUp = () => {
            this.isDragging = false;
            document.removeEventListener('mousemove', onMouseMove);
            document.removeEventListener('mouseup', onMouseUp);
        };

        document.addEventListener('mousemove', onMouseMove);
        document.addEventListener('mouseup', onMouseUp);
    }

    startResizing(e) {
        this.isResizing = true;
        const startX = e.clientX;
        const startY = e.clientY;
        const startWidth = this.width;
        const startHeight = this.height;

        const onMouseMove = (e) => {
            if (!this.isResizing) return;
            const deltaX = e.clientX - startX;
            const deltaY = e.clientY - startY;
            this.width = Math.max(300, startWidth + deltaX);
            this.height = Math.max(200, startHeight + deltaY);
            this.element.style.width = `${this.width}px`;
            this.element.style.height = `${this.height}px`;
            
            // Resize plot if this is a plot panel
            if (this.type === 'plot') {
                this.resizePlot();
            }
        };

        const onMouseUp = () => {
            this.isResizing = false;
            document.removeEventListener('mousemove', onMouseMove);
            document.removeEventListener('mouseup', onMouseUp);
        };

        document.addEventListener('mousemove', onMouseMove);
        document.addEventListener('mouseup', onMouseUp);
    }

    toggleMinimize() {
        this.minimized = !this.minimized;
        this.element.classList.toggle('minimized', this.minimized);
        const btn = this.element.querySelector('[data-action="minimize"]');
        btn.textContent = this.minimized ? '+' : '−';
    }

    updateTitle() {
        const typeNames = {
            'plot': 'Plot',
            'table': 'Table',
            'wordcloud': 'Word Cloud',
            'images': 'Images',
            'heatmap-embedding': 'Heatmap (Embedding)',
            'heatmap-columns': 'Heatmap (Columns)',
            'terminal': 'IPython Terminal'
        };
        
        this.title = typeNames[this.type] || this.type;
        const titleElement = this.element.querySelector('.panel-title');
        if (titleElement) {
            titleElement.textContent = this.title;
        }
    }

    async updateContent() {
        const body = this.element.querySelector('.panel-body');
        
        // Terminal can work without data loaded
        if (this.type !== 'terminal' && (!window.app.dataInfo || !window.app.dataInfo.loaded)) {
            body.innerHTML = '<p class="placeholder">No data loaded</p>';
            return;
        }

        try {
            switch (this.type) {
                case 'plot':
                    await this.renderPlot(body);
                    break;
                case 'table':
                    await this.renderTable(body);
                    break;
                case 'wordcloud':
                    await this.renderWordCloud(body);
                    break;
                case 'images':
                    await this.renderImages(body);
                    break;
                case 'heatmap-embedding':
                    await this.renderHeatmapEmbedding(body);
                    break;
                case 'heatmap-columns':
                    await this.renderHeatmapColumns(body);
                    break;
                case 'terminal':
                    await this.renderTerminal(body);
                    break;
            }
        } catch (error) {
            console.error('Error updating panel content:', error);
            body.innerHTML = `<p class="placeholder">Error: ${error.message}</p>`;
        }
    }

    async renderPlot(body) {
        // Create plot controls and container
        body.innerHTML = `
            <div style="padding: 8px; background: #f8f9fa; border-bottom: 1px solid #ddd;">
                <div style="display: flex; gap: 8px; flex-wrap: wrap; align-items: center;">
                    <label style="font-size: 12px;">X: <select class="plot-x-column"></select></label>
                    <label style="font-size: 12px;">Y: <select class="plot-y-column"></select></label>
                    <label style="font-size: 12px;">Z: <select class="plot-z-column"><option value="">None</option></select></label>
                    <label style="font-size: 12px;">Hue: <select class="plot-hue-column"><option value="">None</option></select></label>
                    <button class="panel-btn" style="color: #2779cb;" onclick="window.app.getPanel('${this.id}').updatePlot()">Update</button>
                </div>
            </div>
            <div class="plot-container" style="width: 100%; height: calc(100% - 45px);"></div>
        `;

        // Populate selectors
        const xSelect = body.querySelector('.plot-x-column');
        const ySelect = body.querySelector('.plot-y-column');
        const zSelect = body.querySelector('.plot-z-column');
        const hueSelect = body.querySelector('.plot-hue-column');

        const numCols = window.app.dataInfo.numeric_columns || [];
        const allCols = window.app.dataInfo.columns || [];

        numCols.forEach(col => {
            xSelect.add(new Option(col, col));
            ySelect.add(new Option(col, col));
            zSelect.add(new Option(col, col));
        });

        allCols.forEach(col => {
            hueSelect.add(new Option(col, col));
        });

        // Set defaults
        if (numCols.length >= 2) {
            xSelect.value = numCols[0];
            ySelect.value = numCols[1];
            await this.updatePlot();
        }
    }

    async updatePlot() {
        const body = this.element.querySelector('.panel-body');
        const xSelect = body.querySelector('.plot-x-column');
        const ySelect = body.querySelector('.plot-y-column');
        const zSelect = body.querySelector('.plot-z-column');
        const hueSelect = body.querySelector('.plot-hue-column');

        const x = xSelect?.value;
        const y = ySelect?.value;
        const z = zSelect?.value || null;
        const hue = hueSelect?.value || null;

        if (!x) return;

        try {
            const response = await fetch('/api/view/plot', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    x, y: y || null, z, hue,
                    type: z ? '3d' : '2d'
                })
            });

            const result = await response.json();
            if (result.success && result.plot) {
                const plotData = JSON.parse(result.plot);
                const plotContainer = body.querySelector('.plot-container');
                
                Plotly.newPlot(plotContainer, plotData.data, plotData.layout, {
                    responsive: true,
                    displayModeBar: true
                });

                // Setup selection handler
                plotContainer.on('plotly_selected', (eventData) => {
                    if (eventData) {
                        this.selectedIndices = eventData.points.map(p => {
                            const n = parseInt(p.text, 10);
                            return Number.isNaN(n) ? p.text : n;
                        });
                        window.app.setStatus(`Selected ${this.selectedIndices.length} points in ${this.title}`);
                        
                        // Save selection to dataframe
                        this.saveSelection();
                        
                        // Refresh all when selection is made
                        window.app.refreshOtherPanels(-1);
                    }
                });
            }
        } catch (error) {
            console.error('Error updating plot:', error);
        }
    }

    async saveSelection() {
        if (!this.selectedIndices || this.selectedIndices.length === 0) {
            return;
        }

        try {
            const response = await fetch('/api/selection/save', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    column_name: 'selection',
                    indices: this.selectedIndices
                })
            });

            const result = await response.json();
            if (result.success) {
                window.app.setStatus(`Selection saved: ${result.count} points marked`);
                // Reload data info to include new column
                await window.app.loadDataInfo();
                // Refresh all plot panels to show selected points in orange
                window.app.refreshAllPlotPanels();
            } else {
                console.error('Error saving selection:', result.error);
            }
        } catch (error) {
            console.error('Error saving selection:', error);
        }
    }

    resizePlot() {
        const plotContainer = this.element.querySelector('.plot-container');
        if (plotContainer && plotContainer.data) {
            Plotly.Plots.resize(plotContainer);
        }
    }

    async renderTable(body) {
        // Add controls for start, stop, step
        body.innerHTML = `
            <div style="padding: 8px; background: #f8f9fa; border-bottom: 1px solid #ddd;">
                <div style="display: flex; gap: 8px; align-items: center;">
                    <label style="font-size: 12px;">Start: <input type="number" id="table-start" value="0" style="width: 60px;"></label>
                    <label style="font-size: 12px;">Stop: <input type="number" id="table-stop" value="20" style="width: 60px;"></label>
                    <label style="font-size: 12px;">Step: <input type="number" id="table-step" value="1" min="1" style="width: 60px;"></label>
                    <button class="panel-btn" id="table-update-btn" style="color: #2779cb;">Update</button>
                </div>
            </div>
            <div id="table-content"></div>
        `;

        async function fetchTable() {
            const start = document.getElementById('table-start').value;
            const stop = document.getElementById('table-stop').value;
            const step = document.getElementById('table-step').value;
            const url = `/api/view/table?start=${start}&stop=${stop}&step=${step}`;
            try {
                const response = await fetch(url);
                const html = await response.text();
                document.getElementById('table-content').innerHTML = html;
            } catch (error) {
                document.getElementById('table-content').innerHTML = `<p class="placeholder">Error loading table: ${error.message}</p>`;
            }
        }

        document.getElementById('table-update-btn').addEventListener('click', fetchTable);
        // Initial load
        fetchTable();
    }

    async renderWordCloud(body) {
        body.innerHTML = `
            <div style="padding: 8px; background: #f8f9fa; border-bottom: 1px solid #ddd;">
                <div style="display: flex; gap: 8px; align-items: center;">
                    <label style="font-size: 12px;">Text Column: <select class="wc-text-column"></select></label>
                </div>
            </div>
            <div class="wc-container" style="width: 100%; height: calc(100% - 45px); overflow: auto; text-align: center;">
                <p class="placeholder">Select points in a plot panel to generate word cloud</p>
            </div>
        `;

        // Populate text column selector
        const textSelect = body.querySelector('.wc-text-column');
        let initialValue = this.config.wcTextColumn;
        if (window.app.dataInfo) {
            const dtypes = window.app.dataInfo.dtypes || {};
            const textCols = window.app.dataInfo.columns.filter(col => {
                const dt = (dtypes[col] || '').toLowerCase();
                return dt.includes('object') || dt.includes('string') || dt.includes('category');
            });
            textCols.forEach(col => textSelect.add(new Option(col, col)));
            if (textCols.length > 0) {
                // If previous selection exists and is valid, restore it
                if (initialValue && textCols.includes(initialValue)) {
                    textSelect.value = initialValue;
                } else {
                    textSelect.value = textCols[0];
                }
                // Auto-generate on initial render
                this.generateWordCloud();
            }
        }

        // Auto-generate when column selection changes
        textSelect.addEventListener('change', () => {
            this.config.wcTextColumn = textSelect.value;
            this.generateWordCloud();
        });
    }

    async generateWordCloud() {
        const body = this.element.querySelector('.panel-body');
        const textSelect = body.querySelector('.wc-text-column');
        const container = body.querySelector('.wc-container');
        
        const textColumn = textSelect?.value;
        if (!textColumn) return;

        container.innerHTML = '<p class="placeholder">Generating word cloud...</p>';

        try {
            // Get selected indices from any plot panel or use all data
            let indices = this.selectedIndices;
            if (!indices || indices.length === 0) {
                // Try to get selection from first plot panel
                const plotPanel = window.app.panels.find(p => p.type === 'plot');
                if (plotPanel) {
                    indices = plotPanel.selectedIndices;
                }
            }

            const response = await fetch('/api/view/wordcloud', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 
                    indices: indices || [],
                    text_column: textColumn
                })
            });

            if (response.ok) {
                const blob = await response.blob();
                const url = URL.createObjectURL(blob);
                container.innerHTML = `<img src="${url}" alt="Word Cloud" style="max-width: 100%; height: auto;">`;
            } else {
                const error = await response.json();
                container.innerHTML = `<p class="placeholder">Error: ${error.error}</p>`;
            }
        } catch (error) {
            container.innerHTML = `<p class="placeholder">Error: ${error.message}</p>`;
        }
    }

    async renderImages(body) {
        body.innerHTML = `
            <div style="padding: 8px; background: #f8f9fa; border-bottom: 1px solid #ddd;">
                <div style="display: flex; gap: 8px; align-items: center;">
                    <label style="font-size: 12px;">Image Column: <select class="img-column"></select></label>
                </div>
            </div>
            <div class="img-container" style="width: 100%; height: calc(100% - 45px); overflow: auto; padding: 8px;">
                <p class="placeholder">Select an image column to display images</p>
            </div>
        `;

        // Try to populate image column selector
        try {
            const response = await fetch('/api/view/images/columns');
            const result = await response.json();
            if (result.success && result.columns) {
                const imgSelect = body.querySelector('.img-column');
                result.columns.forEach(col => imgSelect.add(new Option(col, col)));
                
                // Auto-load if there's a column available
                if (result.columns.length > 0) {
                    imgSelect.value = result.columns[0];
                    this.loadImages();
                }

                // Auto-load when column selection changes
                imgSelect.addEventListener('change', () => {
                    this.loadImages();
                });
            }
        } catch (error) {
            console.error('Error fetching image columns:', error);
        }
    }

    async loadImages() {
        const body = this.element.querySelector('.panel-body');
        const imgSelect = body.querySelector('.img-column');
        const container = body.querySelector('.img-container');
        
        const imageColumn = imgSelect?.value;
        if (!imageColumn) return;

        container.innerHTML = '<p class="placeholder">Loading images...</p>';

        try {
            // Get selected indices from any plot panel or use all data
            let indices = this.selectedIndices;
            if (!indices || indices.length === 0) {
                // Try to get selection from first plot panel
                const plotPanel = window.app.panels.find(p => p.type === 'plot');
                if (plotPanel) {
                    indices = plotPanel.selectedIndices;
                }
            }

            const response = await fetch('/api/view/images', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 
                    indices: indices || [],
                    image_column: imageColumn,
                    max_images: 50
                })
            });

            const result = await response.json();
            if (result.success && result.images) {
                container.innerHTML = '<div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(150px, 1fr)); gap: 8px;"></div>';
                const grid = container.querySelector('div');
                
                result.images.forEach(img => {
                    const imgDiv = document.createElement('div');
                    imgDiv.style.cssText = 'border: 1px solid #ddd; padding: 4px;';
                    
                    if (img.type === 'base64' && img.data) {
                        imgDiv.innerHTML = `<img src="${img.data}" style="width: 100%; height: auto;" alt="Image ${img.index}">`;
                    } else if (img.type === 'url' && img.url) {
                        imgDiv.innerHTML = `<img src="${img.url}" style="width: 100%; height: auto;" alt="Image ${img.index}">`;
                    } else {
                        imgDiv.innerHTML = `<p style="font-size: 11px; text-align: center;">Image ${img.index}</p>`;
                    }
                    
                    grid.appendChild(imgDiv);
                });
            } else {
                container.innerHTML = `<p class="placeholder">No images found</p>`;
            }
        } catch (error) {
            container.innerHTML = `<p class="placeholder">Error: ${error.message}</p>`;
        }
    }

    async renderHeatmapEmbedding(body) {
        body.innerHTML = `
            <div style="padding: 8px; background: #f8f9fa; border-bottom: 1px solid #ddd;">
                <div style="display: flex; gap: 8px; align-items: center;">
                    <label style="font-size: 12px;">Embedding Column: <select class="heatmap-embedding-column"></select></label>
                    <button class="panel-btn" style="color: #2779cb;" onclick="window.app.getPanel('${this.id}').updateHeatmapEmbedding()">Update</button>
                </div>
            </div>
            <div class="heatmap-container" style="width: 100%; height: calc(100% - 45px);"></div>
        `;

        // Populate embedding column selector
        const embeddingSelect = body.querySelector('.heatmap-embedding-column');
        try {
            const response = await fetch('/api/view/heatmap/embedding/columns');
            if (response.ok) {
                const data = await response.json();
                const embeddingCols = data.columns || [];
                
                if (embeddingCols.length === 0) {
                    body.querySelector('.heatmap-container').innerHTML = '<p class="placeholder">No embedding columns found (columns with "embedding" in name)</p>';
                    return;
                }

                embeddingCols.forEach(col => {
                    embeddingSelect.add(new Option(col, col));
                });

                // Set default and auto-generate
                if (this.config.embeddingColumn && embeddingCols.includes(this.config.embeddingColumn)) {
                    embeddingSelect.value = this.config.embeddingColumn;
                } else {
                    embeddingSelect.value = embeddingCols[0];
                    this.config.embeddingColumn = embeddingCols[0];
                }
                
                await this.updateHeatmapEmbedding();
            }
        } catch (error) {
            body.querySelector('.heatmap-container').innerHTML = `<p class="placeholder">Error loading columns: ${error.message}</p>`;
        }

        embeddingSelect.addEventListener('change', () => {
            this.config.embeddingColumn = embeddingSelect.value;
        });
    }

    async updateHeatmapEmbedding() {
        const body = this.element.querySelector('.panel-body');
        const embeddingSelect = body.querySelector('.heatmap-embedding-column');
        const container = body.querySelector('.heatmap-container');
        
        const embeddingColumn = embeddingSelect?.value;
        if (!embeddingColumn) return;

        container.innerHTML = '<p class="placeholder">Generating heatmap...</p>';

        try {
            const response = await fetch('/api/view/heatmap/embedding', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    embedding_column: embeddingColumn,
                    width: container.clientWidth || 800,
                    height: container.clientHeight || 600
                })
            });

            if (response.ok) {
                // Check if response is an image
                const contentType = response.headers.get('content-type');
                if (contentType && contentType.includes('image')) {
                    const blob = await response.blob();
                    const imageUrl = URL.createObjectURL(blob);
                    container.innerHTML = `<img src="${imageUrl}" style="width: 100%; height: 100%; object-fit: contain;" />`;
                } else {
                    const error = await response.json();
                    container.innerHTML = `<p class="placeholder">Error: ${error.error || 'Unknown error'}</p>`;
                }
            } else {
                const error = await response.json();
                container.innerHTML = `<p class="placeholder">Error: ${error.error}</p>`;
            }
        } catch (error) {
            console.error('Error in updateHeatmapEmbedding:', error);
            container.innerHTML = `<p class="placeholder">Error: ${error.message}</p>`;
        }
    }

    async renderHeatmapColumns(body) {
        body.innerHTML = `
            <div style="padding: 8px; background: #f8f9fa; border-bottom: 1px solid #ddd;">
                <div style="display: flex; gap: 8px; align-items: center;">
                    <button class="panel-btn" style="color: #2779cb;" onclick="window.app.getPanel('${this.id}').updateHeatmapColumns()">Update</button>
                    <span style="font-size: 12px; color: #666;">Shows all numeric columns normalized 0-1</span>
                </div>
            </div>
            <div class="heatmap-container" style="width: 100%; height: calc(100% - 45px);"></div>
        `;

        // Auto-generate on initial render
        await this.updateHeatmapColumns();
    }

    async updateHeatmapColumns() {
        const body = this.element.querySelector('.panel-body');
        const container = body.querySelector('.heatmap-container');
        
        container.innerHTML = '<p class="placeholder">Generating heatmap...</p>';

        try {
            const response = await fetch('/api/view/heatmap/columns', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    width: container.clientWidth || 800,
                    height: container.clientHeight || 600
                })
            });

            if (response.ok) {
                // Check if response is an image
                const contentType = response.headers.get('content-type');
                if (contentType && contentType.includes('image')) {
                    const blob = await response.blob();
                    const imageUrl = URL.createObjectURL(blob);
                    container.innerHTML = `<img src="${imageUrl}" style="width: 100%; height: 100%; object-fit: contain;" />`;
                } else {
                    const error = await response.json();
                    container.innerHTML = `<p class="placeholder">Error: ${error.error || 'Unknown error'}</p>`;
                }
            } else {
                const error = await response.json();
                container.innerHTML = `<p class="placeholder">Error: ${error.error}</p>`;
            }
        } catch (error) {
            container.innerHTML = `<p class="placeholder">Error: ${error.message}</p>`;
        }
    }

    async renderTerminal(body) {
        // Initialize terminal session ID if not exists
        if (!this.terminalSessionId) {
            this.terminalSessionId = `terminal-${this.id}-${Date.now()}`;
            this.terminalHistory = [];
            this.historyIndex = -1;
        }

        body.innerHTML = `
            <div style="display: flex; flex-direction: column; height: 100%; font-family: 'Courier New', monospace; font-size: 13px;">
                <div style="padding: 4px 8px; background: #2c2c2c; color: #fff; border-bottom: 1px solid #444; display: flex; justify-content: space-between; align-items: center;">
                    <span style="font-size: 11px;">IPython Terminal</span>
                    <button class="panel-btn" style="background: #444; color: #fff; padding: 2px 6px; font-size: 11px;" onclick="window.app.getPanel('${this.id}').resetTerminal()">Reset</button>
                </div>
                <div class="terminal-output" style="flex: 1; overflow-y: auto; background: #1e1e1e; color: #d4d4d4; padding: 8px; white-space: pre-wrap; word-wrap: break-word;"></div>
                <div style="padding: 8px; background: #252526; border-top: 1px solid #444; display: flex; align-items: center;">
                    <span style="color: #4ec9b0; margin-right: 4px;">In [<span class="term-prompt-num">1</span>]:</span>
                    <input type="text" class="terminal-input" style="flex: 1; background: #1e1e1e; color: #d4d4d4; border: 1px solid #444; padding: 4px 8px; font-family: 'Courier New', monospace; font-size: 13px;" placeholder="Enter Python code...">
                    <button class="terminal-execute" style="margin-left: 8px; background: #0e639c; color: #fff; border: none; padding: 4px 12px; cursor: pointer; border-radius: 2px;">Run</button>
                </div>
            </div>
        `;

        const outputDiv = body.querySelector('.terminal-output');
        const input = body.querySelector('.terminal-input');
        const executeBtn = body.querySelector('.terminal-execute');
        const promptNum = body.querySelector('.term-prompt-num');

        // Initialize terminal
        await this.initTerminal();

        // Setup event listeners
        executeBtn.addEventListener('click', () => this.executeTerminalCode());
        
        input.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.executeTerminalCode();
            } else if (e.key === 'ArrowUp') {
                e.preventDefault();
                this.navigateHistory(-1);
            } else if (e.key === 'ArrowDown') {
                e.preventDefault();
                this.navigateHistory(1);
            }
        });

        // Focus input
        input.focus();
    }

    async initTerminal() {
        try {
            const response = await fetch('/api/view/terminal/init', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ session_id: this.terminalSessionId })
            });

            const result = await response.json();
            if (result.success && result.output) {
                this.appendTerminalOutput(result.output, 'info');
            } else if (!result.success) {
                this.appendTerminalOutput(`Error: ${result.error}`, 'error');
            }
        } catch (error) {
            this.appendTerminalOutput(`Error initializing terminal: ${error.message}`, 'error');
        }
    }

    async executeTerminalCode() {
        const body = this.element.querySelector('.panel-body');
        const input = body.querySelector('.terminal-input');
        const promptNum = body.querySelector('.term-prompt-num');
        
        const code = input.value.trim();
        if (!code) return;

        // Check if command starts with "bob"
        if (code.toLowerCase().startsWith('bob')) {
            const bobPrompt = code.substring(3).trim();
            
            // Add to history
            this.terminalHistory.push(code);
            this.historyIndex = this.terminalHistory.length;
            
            // Display the bob command
            const currentPrompt = promptNum.textContent;
            this.appendTerminalOutput(`In [${currentPrompt}]: ${code}`, 'input');
            
            // Clear input
            input.value = '';
            
            // Show loading message
            this.appendTerminalOutput('🤖 Bob is thinking...', 'info');
            
            try {
                const response = await fetch('/api/view/terminal/bob', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ 
                        session_id: this.terminalSessionId,
                        prompt: bobPrompt
                    })
                });

                const result = await response.json();
                
                if (result.success && result.code) {
                    this.appendTerminalOutput(`💡 Bob suggests: ${result.code}`, 'info');
                    // Put the suggested code in the input field for review
                    input.value = result.code;
                    input.focus();
                } else {
                    this.appendTerminalOutput(`❌ Bob error: ${result.error || 'Unknown error'}`, 'error');
                }

            } catch (error) {
                this.appendTerminalOutput(`❌ Error contacting Bob: ${error.message}`, 'error');
            }
            
            // Increment prompt number
            promptNum.textContent = parseInt(currentPrompt) + 1;
            
            // Scroll to bottom
            const outputDiv = body.querySelector('.terminal-output');
            outputDiv.scrollTop = outputDiv.scrollHeight;
            
            return;
        }

        // Normal code execution (not a bob command)
        // Add to history
        this.terminalHistory.push(code);
        this.historyIndex = this.terminalHistory.length;

        // Display input
        const currentPrompt = promptNum.textContent;
        this.appendTerminalOutput(`In [${currentPrompt}]: ${code}`, 'input');

        // Clear input
        input.value = '';

        try {
            const response = await fetch('/api/view/terminal/execute', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 
                    session_id: this.terminalSessionId,
                    code: code 
                })
            });

            const result = await response.json();
            
            if (result.output) {
                this.appendTerminalOutput(result.output, 'output');
            }
            
            if (result.error) {
                this.appendTerminalOutput(result.error, 'error');
            }

            // Increment prompt number
            promptNum.textContent = parseInt(currentPrompt) + 1;

        } catch (error) {
            this.appendTerminalOutput(`Error: ${error.message}`, 'error');
        }

        // Scroll to bottom
        const outputDiv = body.querySelector('.terminal-output');
        outputDiv.scrollTop = outputDiv.scrollHeight;
    }

    appendTerminalOutput(text, type = 'output') {
        const body = this.element.querySelector('.panel-body');
        const outputDiv = body.querySelector('.terminal-output');
        
        const line = document.createElement('div');
        line.style.marginBottom = '4px';
        
        if (type === 'input') {
            line.style.color = '#d4d4d4';
        } else if (type === 'output') {
            line.style.color = '#cccccc';
        } else if (type === 'error') {
            line.style.color = '#f48771';
        } else if (type === 'info') {
            line.style.color = '#4fc1ff';
        }
        
        line.textContent = text;
        outputDiv.appendChild(line);
    }

    navigateHistory(direction) {
        if (this.terminalHistory.length === 0) return;
        
        const body = this.element.querySelector('.panel-body');
        const input = body.querySelector('.terminal-input');
        
        this.historyIndex += direction;
        
        if (this.historyIndex < 0) {
            this.historyIndex = 0;
        } else if (this.historyIndex >= this.terminalHistory.length) {
            this.historyIndex = this.terminalHistory.length;
            input.value = '';
            return;
        }
        
        input.value = this.terminalHistory[this.historyIndex];
    }

    async resetTerminal() {
        try {
            const response = await fetch('/api/view/terminal/reset', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ session_id: this.terminalSessionId })
            });

            const result = await response.json();
            
            // Clear output
            const body = this.element.querySelector('.panel-body');
            const outputDiv = body.querySelector('.terminal-output');
            outputDiv.innerHTML = '';
            
            // Reset prompt number
            const promptNum = body.querySelector('.term-prompt-num');
            promptNum.textContent = '1';
            
            // Clear history
            this.terminalHistory = [];
            this.historyIndex = -1;
            
            // Reinitialize
            await this.initTerminal();
            
        } catch (error) {
            this.appendTerminalOutput(`Error resetting terminal: ${error.message}`, 'error');
        }
    }
}

class EmbeddoorApp {
    constructor() {
        this.dataInfo = null;
        this.panels = [];
        this.nextPanelId = 1;
        this.maxZIndex = 1;
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.checkDataStatus();
    }

    setupEventListeners() {
        // File menu
        document.getElementById('open-file').addEventListener('click', () => this.openFile());
        document.getElementById('btn-load').addEventListener('click', () => this.openFile());
        document.getElementById('save-file').addEventListener('click', () => this.saveFileDialog());
        document.getElementById('btn-save').addEventListener('click', () => this.saveFileDialog());
        document.getElementById('export-csv').addEventListener('click', () => this.saveFileDialog('csv'));
        document.getElementById('load-huggingface').addEventListener('click', () => this.showHuggingfaceDialog());
        document.getElementById('huggingface-form').addEventListener('submit', (e) => {
            e.preventDefault();
            this.loadFromHuggingface();
        });
        document.getElementById('huggingface-dialog-cancel').addEventListener('click', () => this.hideModal('huggingface-dialog'));

        // Embedding menu
        document.getElementById('create-embedding').addEventListener('click', () => this.showEmbeddingDialog());
        document.getElementById('embedding-form').addEventListener('submit', (e) => {
            e.preventDefault();
            this.createEmbedding();
        });
        document.getElementById('embedding-dialog-cancel').addEventListener('click', () => this.hideModal('embedding-dialog'));

        // Dimensionality reduction menu
        document.getElementById('apply-pca').addEventListener('click', () => this.showDimRedDialog('pca'));
        document.getElementById('apply-tsne').addEventListener('click', () => this.showDimRedDialog('tsne'));
        document.getElementById('apply-umap').addEventListener('click', () => this.showDimRedDialog('umap'));
        document.getElementById('dimred-form').addEventListener('submit', (e) => {
            e.preventDefault();
            this.applyDimRed();
        });
        document.getElementById('dimred-dialog-cancel').addEventListener('click', () => this.hideModal('dimred-dialog'));

        // View menu
        document.getElementById('add-panel').addEventListener('click', () => this.showAddPanelDialog());
        document.getElementById('btn-add-panel').addEventListener('click', () => this.showAddPanelDialog());

        // Add panel dialog
        document.getElementById('add-panel-form').addEventListener('submit', (e) => {
            e.preventDefault();
            this.addPanelFromDialog();
        });
        document.getElementById('add-panel-dialog-cancel').addEventListener('click', () => this.hideModal('add-panel-dialog'));

        // Toolbar buttons
        document.getElementById('btn-refresh').addEventListener('click', () => this.refreshAll());

        // Close buttons for modals
        document.querySelectorAll('.close').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const modal = e.target.closest('.modal');
                if (modal) this.hideModal(modal.id);
            });
        });
    }

    async checkDataStatus() {
        try {
            const response = await fetch('/api/data/info');
            const info = await response.json();
            
            if (info.loaded) {
                this.dataInfo = info;
                this.updateUI();
                
                // Create default plot panel if none exists
                if (this.panels.length === 0) {
                    this.addPanel('plot', 'Visualization', 20, 20, 600, 500);
                }
            }
        } catch (error) {
            console.error('Error checking data status:', error);
        }
    }

    showModal(modalId) {
        document.getElementById(modalId).style.display = 'block';
    }

    hideModal(modalId) {
        document.getElementById(modalId).style.display = 'none';
    }

    showAddPanelDialog() {
        this.showModal('add-panel-dialog');
    }

    addPanelFromDialog() {
        const typeSelect = document.getElementById('new-panel-type');
        const type = typeSelect.value;
        
        const typeNames = {
            'plot': 'Plot',
            'table': 'Table',
            'wordcloud': 'Word Cloud',
            'images': 'Images',
            'terminal': 'IPython Terminal'
        };

        // Offset new panels slightly
        const offset = (this.panels.length * 30) % 200;
        this.addPanel(type, typeNames[type], 20 + offset, 20 + offset, 600, 500);
        
        this.hideModal('add-panel-dialog');
    }

    addPanel(type, title, x, y, width, height) {
        const panel = new FloatingPanel(this.nextPanelId++, type, title, x, y, width, height);
        const element = panel.createElement();
        
        document.getElementById('panels-container').appendChild(element);
        this.panels.push(panel);
        
        this.bringPanelToFront(panel.id);
        panel.updateContent();
        
        return panel;
    }

    removePanel(id) {
        const index = this.panels.findIndex(p => p.id === id);
        if (index !== -1) {
            const panel = this.panels[index];
            panel.element.remove();
            this.panels.splice(index, 1);
        }
    }

    getPanel(id) {
        return this.panels.find(p => p.id == id);
    }

    bringPanelToFront(id) {
        // Remove active class from all panels
        this.panels.forEach(p => p.element.classList.remove('active'));
        
        // Find and bring to front
        const panel = this.panels.find(p => p.id === id);
        if (panel) {
            panel.element.style.zIndex = ++this.maxZIndex;
            panel.element.classList.add('active');
        }
    }

    async openFile() {
        this.setStatus('Opening file dialog...');
        
        try {
            const dialogResponse = await fetch('/api/dialog/open-file');
            const dialogResult = await dialogResponse.json();
            
            if (!dialogResult.success) {
                if (!dialogResult.cancelled) {
                    alert('Error opening file dialog: ' + (dialogResult.error || 'Unknown error'));
                }
                this.setStatus('Ready');
                return;
            }
            
            const filepath = dialogResult.filepath;
            this.setStatus('Loading file...');
            
            const response = await fetch('/api/data/load', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ filepath })
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.dataInfo = result;
                this.dataInfo.loaded = true;
                this.updateUI();
                this.refreshAll();
                this.setStatus(`Loaded ${result.shape[0]} rows, ${result.shape[1]} columns`);
                    // Open a table panel if no panels are open
                    if (this.panels.length === 0) {
                        this.addPanel('table', 'Table', 40, 40, 700, 400);
                    }
            } else {
                alert('Error loading file: ' + result.error);
                this.setStatus('Error loading file');
            }
        } catch (error) {
            console.error('Error:', error);
            alert('Error loading file: ' + error.message);
            this.setStatus('Error');
        }
    }

    async saveFileDialog(format = 'parquet') {
        this.setStatus('Opening save dialog...');
        
        try {
            const dialogResponse = await fetch('/api/dialog/save-file', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ format })
            });
            const dialogResult = await dialogResponse.json();
            
            if (!dialogResult.success) {
                if (!dialogResult.cancelled) {
                    alert('Error opening save dialog: ' + (dialogResult.error || 'Unknown error'));
                }
                this.setStatus('Ready');
                return;
            }
            
            const filepath = dialogResult.filepath;
            this.setStatus('Saving file...');
            
            const response = await fetch('/api/data/save', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ filepath, format })
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.setStatus('File saved successfully');
            } else {
                alert('Error saving file: ' + result.error);
                this.setStatus('Error saving file');
            }
        } catch (error) {
            console.error('Error:', error);
            alert('Error saving file: ' + error.message);
            this.setStatus('Error');
        }
    }

    showHuggingfaceDialog() {
        this.showModal('huggingface-dialog');
    }

    async loadFromHuggingface() {
        const datasetName = document.getElementById('hf-dataset-name').value.trim();
        const split = document.getElementById('hf-split').value.trim();
        
        if (!datasetName) {
            alert('Please enter a dataset name');
            return;
        }
        
        this.hideModal('huggingface-dialog');
        this.setStatus('Loading dataset from Huggingface...');
        
        try {
            const response = await fetch('/api/data/load-huggingface', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ dataset_name: datasetName, split: split || null })
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.dataInfo = result;
                this.dataInfo.loaded = true;
                this.updateUI();
                this.refreshAll();
                this.setStatus(`Loaded ${result.shape[0]} rows, ${result.shape[1]} columns from Huggingface`);
            } else {
                alert('Error loading dataset from Huggingface: ' + result.error);
                this.setStatus('Error loading dataset');
            }
        } catch (error) {
            console.error('Error:', error);
            alert('Error loading dataset from Huggingface: ' + error.message);
            this.setStatus('Error');
        }
    }

    showEmbeddingDialog() {
        if (!this.dataInfo || !this.dataInfo.loaded) {
            alert('Please load data first');
            return;
        }
        
        const select = document.getElementById('embed-source-column');
        select.innerHTML = '';
        this.dataInfo.columns.forEach(col => {
            const option = document.createElement('option');
            option.value = col;
            option.textContent = col;
            select.appendChild(option);
        });
        
        this.showModal('embedding-dialog');
    }

    async createEmbedding() {
        const sourceColumn = document.getElementById('embed-source-column').value;
        const provider = document.getElementById('embed-provider').value;
        const model = document.getElementById('embed-model').value;
        const targetColumn = document.getElementById('embed-target-column').value;
        
        this.setStatus('Creating embeddings...');
        this.hideModal('embedding-dialog');
        
        try {
            const response = await fetch('/api/embeddings/create', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    source_column: sourceColumn,
                    provider: provider,
                    model: model,
                    target_column: targetColumn
                })
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.setStatus('Embeddings created successfully');
                await this.checkDataStatus();
            } else {
                alert('Error creating embeddings: ' + result.error);
                this.setStatus('Error');
            }
        } catch (error) {
            console.error('Error:', error);
            alert('Error creating embeddings: ' + error.message);
            this.setStatus('Error');
        }
    }

    showDimRedDialog(method) {
        if (!this.dataInfo || !this.dataInfo.loaded) {
            alert('Please load data first');
            return;
        }
        
        const select = document.getElementById('dimred-source-column');
        select.innerHTML = '';
        this.dataInfo.columns.forEach(col => {
            const option = document.createElement('option');
            option.value = col;
            option.textContent = col;
            select.appendChild(option);
        });
        
        document.getElementById('dimred-method').value = method;
        this.showModal('dimred-dialog');
    }

    async applyDimRed() {
        const sourceColumn = document.getElementById('dimred-source-column').value;
        const method = document.getElementById('dimred-method').value;
        const nComponents = parseInt(document.getElementById('dimred-components').value);
        const targetName = document.getElementById('dimred-target-name').value;
        
        this.setStatus('Applying dimensionality reduction...');
        this.hideModal('dimred-dialog');
        
        try {
            const response = await fetch('/api/dimred/apply', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    source_column: sourceColumn,
                    method: method,
                    n_components: nComponents,
                    target_base_name: targetName,
                    params: {}
                })
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.setStatus('Dimensionality reduction applied successfully');
                await this.checkDataStatus();
                this.refreshAll();
            } else {
                alert('Error applying dimensionality reduction: ' + result.error);
                this.setStatus('Error');
            }
        } catch (error) {
            console.error('Error:', error);
            alert('Error applying dimensionality reduction: ' + error.message);
            this.setStatus('Error');
        }
    }

    updateUI() {
        if (!this.dataInfo || !this.dataInfo.loaded) {
            return;
        }

        document.getElementById('data-info').textContent = 
            `${this.dataInfo.shape[0]} rows × ${this.dataInfo.shape[1]} columns`;
    }

    refreshAll() {
        this.panels.forEach(panel => panel.updateContent());
    }

    refreshOtherPanels(excludePanelId) {
        // Refresh all panels except the one specified
        this.panels.forEach(panel => {
            if (panel.id !== excludePanelId) {
                panel.updateContent();
            }
        });
    }

    refreshAllPlotPanels() {
        // Refresh all plot panels to show updated selection
        this.panels.forEach(panel => {
            if (panel.type === 'plot') {
                panel.updatePlot();
            }
        });
    }

    setStatus(text) {
        document.getElementById('status-text').textContent = text;
    }
}

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.app = new EmbeddoorApp();
});
