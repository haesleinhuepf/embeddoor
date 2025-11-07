// Embeddoor JavaScript Application

class EmbeddoorApp {
    constructor() {
        this.dataInfo = null;
        this.currentPlot = null;
        this.selectedIndices = [];
        this.isGeneratingWordCloud = false; // guard to prevent recursive redraws
        this.isResizing = false;
        this.leftPanelMin = 200;
        this.rightPanelMin = 260;
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

        // Plot controls
        document.getElementById('update-plot').addEventListener('click', () => this.updatePlot());

        // Toolbar buttons
        document.getElementById('btn-refresh').addEventListener('click', () => this.refreshView());
        
        // View mode
        document.getElementById('view-mode').addEventListener('change', () => this.updateDataView());
        const wcGenerateBtn = document.getElementById('wordcloud-generate');
        if (wcGenerateBtn) {
            wcGenerateBtn.addEventListener('click', () => this.generateWordCloud());
        }
        const wcTextSelect = document.getElementById('wordcloud-text-column');
        if (wcTextSelect) {
            wcTextSelect.addEventListener('change', () => {
                if (document.getElementById('view-mode').value === 'wordcloud' && this.selectedIndices.length > 0) {
                    this.generateWordCloud();
                }
            });
        }

        // Close buttons for modals
        document.querySelectorAll('.close').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const modal = e.target.closest('.modal');
                if (modal) this.hideModal(modal.id);
            });
        });

        // Divider resize events
        this.setupResizeDivider();
    }

    setupResizeDivider() {
        const divider = document.getElementById('panel-divider');
        const leftPanel = document.getElementById('left-panel');
        const rightPanel = document.getElementById('right-panel');
        if (!divider || !leftPanel || !rightPanel) return;

        const container = document.querySelector('.main-content');

        // Helper to clamp desired width to bounds
        const clampWidth = (desired) => {
            const rect = container.getBoundingClientRect();
            const totalWidth = rect.width;
            const maxLeft = totalWidth - this.rightPanelMin - divider.offsetWidth;
            let w = desired;
            if (w < this.leftPanelMin) w = this.leftPanelMin;
            if (w > maxLeft) w = Math.max(this.leftPanelMin, maxLeft);
            return w;
        };

        // Initialize fixed left panel width so it won't auto-resize during plot/table renders
        const saved = localStorage.getItem('leftPanelWidthPx');
        let initialWidth;
        if (saved && !Number.isNaN(parseInt(saved, 10))) {
            initialWidth = clampWidth(parseInt(saved, 10));
        } else {
            const rect = container.getBoundingClientRect();
            const totalWidth = rect.width;
            const half = Math.round(totalWidth * 0.5);
            initialWidth = clampWidth(half);
        }
        leftPanel.style.width = initialWidth + 'px';
        leftPanel.style.flex = '0 0 auto'; // keep fixed unless user drags
        rightPanel.style.flex = '1 1 auto';
        this.resizePlotToPanel();

        // Keep width in bounds on window resize (no auto-resize otherwise)
        window.addEventListener('resize', () => {
            const current = parseInt(leftPanel.getBoundingClientRect().width, 10) || initialWidth;
            const clamped = clampWidth(current);
            if (clamped !== current) {
                leftPanel.style.width = clamped + 'px';
            }
            this.resizePlotToPanel();
        });

        const onMouseMove = (e) => {
            if (!this.isResizing) return;
            const rect = container.getBoundingClientRect();
            let newWidth = e.clientX - rect.left; // distance from left edge
            // Constrain
            const totalWidth = rect.width;
            const maxLeft = totalWidth - this.rightPanelMin - divider.offsetWidth;
            if (newWidth < this.leftPanelMin) newWidth = this.leftPanelMin;
            if (newWidth > maxLeft) newWidth = maxLeft;
            leftPanel.style.width = newWidth + 'px';
            // Allow right panel to flex remaining space
            rightPanel.style.flex = '1 1 auto';
            this.resizePlotToPanel();
        };

        const onMouseUp = () => {
            if (!this.isResizing) return;
            this.isResizing = false;
            divider.classList.remove('active');
            document.body.style.userSelect = '';
            const w = parseInt(leftPanel.getBoundingClientRect().width, 10);
            localStorage.setItem('leftPanelWidthPx', String(w));
            window.removeEventListener('mousemove', onMouseMove);
            window.removeEventListener('mouseup', onMouseUp);
            this.resizePlotToPanel();
        };

        divider.addEventListener('mousedown', (e) => {
            e.preventDefault();
            this.isResizing = true;
            divider.classList.add('active');
            document.body.style.userSelect = 'none';
            window.addEventListener('mousemove', onMouseMove);
            window.addEventListener('mouseup', onMouseUp);
        });

        // Observe size changes of left panel (e.g., CSS tweaks)
        if ('ResizeObserver' in window) {
            this._leftPanelRO = new ResizeObserver(() => this.resizePlotToPanel());
            this._leftPanelRO.observe(leftPanel);
        }
    }

    async checkDataStatus() {
        try {
            const response = await fetch('/api/data/info');
            const info = await response.json();
            
            if (info.loaded) {
                this.dataInfo = info;
                this.updateUI();
                this.updateDataView();
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

    async openFile() {
        this.setStatus('Opening file dialog...');
        
        try {
            // Show native OS file dialog
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
            
            // Load the file
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
                this.updateDataView();
                this.setStatus(`Loaded ${result.shape[0]} rows, ${result.shape[1]} columns`);
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
            // Show native OS save dialog
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
            
            // Save the file
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

    showEmbeddingDialog() {
        if (!this.dataInfo || !this.dataInfo.loaded) {
            alert('Please load data first');
            return;
        }
        
        // Populate column selector
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

    showDimRedDialog(method) {
        if (!this.dataInfo || !this.dataInfo.loaded) {
            alert('Please load data first');
            return;
        }
        
        // Set method
        document.getElementById('dimred-method').value = method;
        
        // Populate column selector (only show columns that could be embeddings)
        const select = document.getElementById('dimred-source-column');
        select.innerHTML = '';
        this.dataInfo.columns.forEach(col => {
            const option = document.createElement('option');
            option.value = col;
            option.textContent = col;
            select.appendChild(option);
        });
        
        this.showModal('dimred-dialog');
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
                this.setStatus(`Embedding created: ${result.column}`);
                await this.checkDataStatus();
            } else {
                alert('Error creating embedding: ' + result.error);
                this.setStatus('Error creating embedding');
            }
        } catch (error) {
            console.error('Error:', error);
            alert('Error creating embedding: ' + error.message);
            this.setStatus('Error');
        }
    }

    async applyDimRed() {
        const sourceColumn = document.getElementById('dimred-source-column').value;
        const method = document.getElementById('dimred-method').value;
        const nComponents = parseInt(document.getElementById('dimred-components').value);
        const targetName = document.getElementById('dimred-target-name').value;

        this.setStatus(`Applying ${method.toUpperCase()}...`);
        this.hideModal('dimred-dialog');

        try {
            const response = await fetch('/api/dimred/apply', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    source_column: sourceColumn,
                    method: method,
                    n_components: nComponents,
                    target_base_name: targetName
                })
            });

            const result = await response.json();

            if (result.success) {
                this.setStatus(`Dimensionality reduction complete: ${result.columns.join(', ')}`);
                await this.checkDataStatus();
                this.updateUI();
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

        // Update data info in status bar
        document.getElementById('data-info').textContent = 
            `${this.dataInfo.shape[0]} rows × ${this.dataInfo.shape[1]} columns`;

        // Populate column selectors
        this.populateColumnSelector('x-column', this.dataInfo.numeric_columns);
        this.populateColumnSelector('y-column', this.dataInfo.numeric_columns);
        this.populateColumnSelector('z-column', this.dataInfo.numeric_columns, true);
        this.populateColumnSelector('hue-column', this.dataInfo.columns, true);
        this.populateColumnSelector('size-column', this.dataInfo.numeric_columns, true);
    }

    populateColumnSelector(selectId, columns, includeNone = false) {
        const select = document.getElementById(selectId);
        select.innerHTML = '';
        
        if (includeNone) {
            const option = document.createElement('option');
            option.value = '';
            option.textContent = 'None';
            select.appendChild(option);
        }
        
        columns.forEach(col => {
            const option = document.createElement('option');
            option.value = col;
            option.textContent = col;
            select.appendChild(option);
        });
    }

    async updatePlot() {
        const x = document.getElementById('x-column').value;
        const y = document.getElementById('y-column').value;
        const z = document.getElementById('z-column').value;
        const hue = document.getElementById('hue-column').value;
        const size = document.getElementById('size-column').value;

        if (!x) {
            alert('Please select at least an X column');
            return;
        }

        this.setStatus('Generating plot...');

        try {
            const response = await fetch('/api/plot', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    x: x,
                    y: y || null,
                    z: z || null,
                    hue: hue || null,
                    size: size || null,
                    type: z ? '3d' : '2d'
                })
            });

            const result = await response.json();

            if (result.plot) {
                const plotData = JSON.parse(result.plot);
                    // Remove Plotly default outer frame/grid lines for a frameless look
                    if (plotData.layout) {
                        // Common properties to neutralize framing
                        plotData.layout.paper_bgcolor = 'white';
                        plotData.layout.plot_bgcolor = 'white';
                        if (plotData.layout.xaxis) {
                            plotData.layout.xaxis.showline = false;
                            plotData.layout.xaxis.showgrid = false;
                            plotData.layout.xaxis.zeroline = false;
                        }
                        if (plotData.layout.yaxis) {
                            plotData.layout.yaxis.showline = false;
                            plotData.layout.yaxis.showgrid = false;
                            plotData.layout.yaxis.zeroline = false;
                        }
                        if (plotData.layout.scene) {
                            // 3D plots
                            const axes = ['xaxis','yaxis','zaxis'];
                            axes.forEach(ax => {
                                if (plotData.layout.scene[ax]) {
                                    plotData.layout.scene[ax].showline = false;
                                    plotData.layout.scene[ax].showgrid = false;
                                    plotData.layout.scene[ax].zeroline = false;
                                }
                            });
                            plotData.layout.scene.bgcolor = 'white';
                        }
                    }
                    Plotly.newPlot('plot-container', plotData.data, plotData.layout, {
                        responsive: true,
                        displayModeBar: true
                    });
                    this.resizePlotToPanel();

                // Setup lasso selection handler
                const plotDiv = document.getElementById('plot-container');
                plotDiv.on('plotly_selected', (eventData) => {
                    if (eventData) {
                        this.handleSelection(eventData);
                    }
                });

                this.setStatus('Plot updated');
            } else {
                alert('Error generating plot');
                this.setStatus('Error');
            }
        } catch (error) {
            console.error('Error:', error);
            alert('Error generating plot: ' + error.message);
            this.setStatus('Error');
        }
    }

        resizePlotToPanel() {
            const plotDiv = document.getElementById('plot-container');
            if (!plotDiv || !plotDiv.data) return; // Plotly attaches .data when initialized
            const panelBody = document.querySelector('#left-panel .panel-body');
            if (!panelBody) return;
            // Use requestAnimationFrame to avoid layout thrash on rapid drags
            if (this._pendingPlotResize) cancelAnimationFrame(this._pendingPlotResize);
            this._pendingPlotResize = requestAnimationFrame(() => {
                const rect = panelBody.getBoundingClientRect();
                const targetWidth = Math.max(100, rect.width);
                const targetHeight = Math.max(100, rect.height);
                Plotly.relayout(plotDiv, { width: targetWidth, height: targetHeight });
            });
        }
    async updateDataView() {
        const viewMode = document.getElementById('view-mode').value;
        const container = document.getElementById('data-container');
        const wcControls = document.getElementById('wordcloud-controls');
        const wcTextSelect = document.getElementById('wordcloud-text-column');

        if (!this.dataInfo || !this.dataInfo.loaded) {
            return;
        }

        this.setStatus('Loading data view...');

        try {
            if (viewMode === 'table') {
                // Fetch pre-rendered HTML table from server
                const response = await fetch('/api/data/sample_html?n=100');
                const html = await response.text();
                container.innerHTML = html;
                wcControls.style.display = 'none';
            } else if (viewMode === 'images') {
                container.innerHTML = '<p class="placeholder">Image view not yet implemented</p>';
                wcControls.style.display = 'none';
            } else if (viewMode === 'wordcloud') {
                // Populate text column selector using dtype info (object, string, category)
                wcTextSelect.innerHTML = '';
                const dtypes = this.dataInfo.dtypes || {};
                const textCols = this.dataInfo.columns.filter(col => {
                    const dt = (dtypes[col] || '').toLowerCase();
                    return dt.includes('object') || dt.includes('string') || dt.includes('category');
                });
                textCols.forEach(col => {
                    const opt = document.createElement('option');
                    opt.value = col; opt.textContent = col; wcTextSelect.appendChild(opt);
                });
                // Prefer selecting a commonly named text column
                const preferred = ['text','content','description','body','message','title','summary'];
                for (const p of preferred) {
                    if (textCols.includes(p)) { wcTextSelect.value = p; break; }
                }
                wcControls.style.display = 'flex';
                container.innerHTML = '<p class="placeholder">Select points with lasso on the left plot to generate a word cloud.</p>';
            }

            this.setStatus('Ready');
        } catch (error) {
            console.error('Error:', error);
            container.innerHTML = '<p class="placeholder">Error loading data</p>';
            this.setStatus('Error');
        }
    }

    handleSelection(eventData) {
        if (!eventData || !eventData.points) {
            return;
        }

        // Get indices of selected points; keep label strings if not numeric
        this.selectedIndices = eventData.points.map(p => {
            const n = parseInt(p.text, 10);
            return Number.isNaN(n) ? p.text : n;
        });
        
        const count = this.selectedIndices.length;
        this.setStatus(`Selected ${count} points`);

        // Persist selection to table under a fixed column name 'selection'
        // Empty list means the column is created (or reset) with all False
        this.saveSelection('selection');

        const viewMode = document.getElementById('view-mode').value;
        if (viewMode === 'wordcloud') {
            this.generateWordCloud();
        }
    }

    async generateWordCloud() {
        const container = document.getElementById('data-container');
        const textCol = document.getElementById('wordcloud-text-column').value || null;
        container.innerHTML = '<p class="placeholder">Generating word cloud...</p>';

        // Also keep the selection stored in the table under 'selection'
        // If there are no selected indices, this will reset the column to all False
        if (this.isGeneratingWordCloud) return; // prevent re-entrancy
        this.isGeneratingWordCloud = true;
        await this.saveSelection('selection');
        try {
            const response = await fetch('/api/wordcloud', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ indices: this.selectedIndices, text_column: textCol })
            });
            if (!response.ok) {
                let errMsg = 'failed to generate word cloud';
                try { const err = await response.json(); errMsg = err.error || errMsg; } catch (_) {}
                container.innerHTML = `<p class="placeholder">Error: ${errMsg}</p>`;
                return;
            }
            const blob = await response.blob();
            const url = URL.createObjectURL(blob);
            container.innerHTML = '';
            const img = document.createElement('img');
            img.src = url; img.className = 'wordcloud-image';
            img.alt = 'Word Cloud';
            container.appendChild(img);
            const countDisplay = this.selectedIndices.length > 0 ? this.selectedIndices.length : 'all';
            this.setStatus(`Word cloud generated for ${countDisplay} points`);
        } catch (e) {
            console.error(e);
            container.innerHTML = '<p class="placeholder">Error generating word cloud</p>';
            this.setStatus('Error');
        } finally {
            this.isGeneratingWordCloud = false;
        }
    }

    async saveSelection(columnName) {
        try {
            const response = await fetch('/api/selection/save', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    column_name: columnName,
                    indices: this.selectedIndices
                })
            });

            const result = await response.json();

            if (result.success) {
                this.setStatus(`Selection saved as '${columnName}'`);
                await this.checkDataStatus();
            } else {
                alert('Error saving selection: ' + result.error);
            }
        } catch (error) {
            console.error('Error:', error);
            alert('Error saving selection: ' + error.message);
        }
    }

    refreshView() {
        this.checkDataStatus();
        this.updateDataView();
        if (this.dataInfo && this.dataInfo.loaded) {
            this.updatePlot();
        }
    }

    setStatus(text) {
        document.getElementById('status-text').textContent = text;
    }
}

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.app = new EmbeddoorApp();
});
