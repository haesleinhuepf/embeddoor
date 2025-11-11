# Embeddoor Architecture - Floating Panels System

## Directory Structure
```
embeddoor/
├── views/                          # NEW: Modular view handlers
│   ├── __init__.py                # Registers all view routes
│   ├── plot.py                    # Plot visualization endpoints
│   ├── table.py                   # Table visualization endpoints
│   ├── wordcloud.py               # Word cloud endpoints
│   └── images.py                  # Image gallery endpoints
├── templates/
│   ├── index.html                 # NEW: Floating panels layout
│   └── index_old.html             # Backup of old layout
├── static/
│   ├── js/
│   │   ├── app.js                 # NEW: FloatingPanel system
│   │   └── app_old.js             # Backup of old app
│   └── css/
│       └── style.css              # Updated with floating panel styles
├── routes.py                      # Updated to use modular views
├── visualization.py               # Kept for rendering functions
├── data_manager.py                # Unchanged
└── app.py                         # Unchanged
```

## Component Flow

### Frontend Components
```
┌─────────────────────────────────────────────────────────────┐
│                        EmbeddoorApp                          │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ manages multiple FloatingPanel instances             │  │
│  │ • panels: Array<FloatingPanel>                       │  │
│  │ • addPanel(), removePanel(), bringToFront()          │  │
│  └──────────────────────────────────────────────────────┘  │
│                           │                                  │
│          ┌────────────────┴────────────────┬────────────────┤
│          ▼                 ▼               ▼                │
│   FloatingPanel      FloatingPanel    FloatingPanel         │
│   type: plot         type: table      type: wordcloud       │
│   ┌──────────┐      ┌──────────┐     ┌──────────┐          │
│   │ Header   │      │ Header   │     │ Header   │          │
│   │ • Title  │      │ • Title  │     │ • Title  │          │
│   │ • Select │      │ • Select │     │ • Select │          │
│   │ • Min/Cls│      │ • Min/Cls│     │ • Min/Cls│          │
│   ├──────────┤      ├──────────┤     ├──────────┤          │
│   │ Body     │      │ Body     │     │ Body     │          │
│   │ • Plotly │      │ • Table  │     │ • Image  │          │
│   │ • Config │      │ • HTML   │     │ • Canvas │          │
│   └──────────┘      └──────────┘     └──────────┘          │
└─────────────────────────────────────────────────────────────┘
```

### Backend API Structure
```
Flask App
├── routes.py                      # Core routes
│   ├── /api/dialog/*             # File dialogs
│   ├── /api/data/*               # Data operations
│   ├── /api/embeddings/*         # Embedding operations
│   └── /api/dimred/*             # Dimensionality reduction
│
└── views/                         # NEW: View-specific routes
    ├── plot.py
    │   ├── POST /api/view/plot              # Generate plot
    │   └── POST /api/selection/save         # Save selection
    │
    ├── table.py
    │   ├── GET /api/view/table              # Get table HTML
    │   └── GET /api/view/table/info         # Get metadata
    │
    ├── wordcloud.py
    │   ├── POST /api/view/wordcloud         # Generate image
    │   └── GET /api/view/wordcloud/columns  # Get text columns
    │
    └── images.py
        ├── POST /api/view/images            # Get image data
        └── GET /api/view/images/columns     # Get image columns
```

## Data Flow Example: Creating a Plot Panel

```
User Action                Frontend                    Backend
───────────               ────────                    ───────

Click "Add Panel"    →    showAddPanelDialog()
Select "Plot"        →    
Click "Add"          →    addPanelFromDialog()
                     │    
                     └──→ addPanel('plot', ...)
                          │
                          ├─→ new FloatingPanel(...)
                          │   │
                          │   ├─→ createElement()
                          │   │   • Creates DOM structure
                          │   │   • Attaches event listeners
                          │   │   
                          │   └─→ updateContent()
                          │       │
                          │       └─→ renderPlot()
                          │           • Populate column selectors
                          │           • Call updatePlot()
                          │               │
                          │               └─→ fetch('/api/view/plot')  →  views/plot.py
                          │                                                   │
                          │                                                   ├─→ data_manager.get_plot_data()
                          │                                                   │
                          │                                                   ├─→ visualization.create_plot()
                          │                                                   │
                          │                   ← JSON {success, plot}         ←─┘
                          │                   │
                          └───────────────────┘
                                  │
                                  ├─→ Plotly.newPlot()
                                  │   • Render interactive plot
                                  │   
                                  └─→ Setup selection handler
                                      • Listen for plotly_selected events
```

## Panel Interaction Model

### Dragging
```
User mousedown on header  →  panel.startDragging()
                             │
                             ├─→ Set isDragging = true
                             ├─→ Calculate dragOffset
                             └─→ Listen for mousemove
                                 │
User drags mouse         →  │   Update panel.x, panel.y
                             │   Update element.style.left/top
                             │
User releases mouse      →  │   Set isDragging = false
                             └─→ Remove event listeners
```

### Resizing
```
User mousedown on resize  →  panel.startResizing()
handle                       │
                             ├─→ Set isResizing = true
                             ├─→ Store start dimensions
                             └─→ Listen for mousemove
                                 │
User drags mouse         →  │   Calculate delta
                             │   Update panel.width, panel.height
                             │   Update element.style dimensions
                             │   Call resizePlot() if needed
                             │
User releases mouse      →  │   Set isResizing = false
                             └─→ Remove event listeners
```

### View Switching
```
User selects view type   →  panel-view-selector change event
from dropdown                │
                             ├─→ Update panel.type
                             │
                             └─→ panel.updateContent()
                                 │
                                 ├─→ switch (type)
                                 │   ├─→ case 'plot': renderPlot()
                                 │   ├─→ case 'table': renderTable()
                                 │   ├─→ case 'wordcloud': renderWordCloud()
                                 │   └─→ case 'images': renderImages()
                                 │
                                 └─→ Fetch data from appropriate API
```

## Key Design Decisions

1. **Modular Views**: Each visualization type is a separate Python module
   - Easy to add new view types
   - Each module is self-contained
   - Clear API boundaries

2. **FloatingPanel Class**: Encapsulates all panel behavior
   - Handles UI interactions (drag, resize, minimize)
   - Manages view-specific content rendering
   - Independent state management per panel

3. **Flexible Layout**: Absolute positioning instead of flex layout
   - Panels can overlap (z-index management)
   - Free positioning anywhere in workspace
   - Dynamic panel creation/removal

4. **Per-Panel Configuration**: Each panel maintains its own:
   - View type selection
   - Column mappings (for plots)
   - Selection state
   - Position and size

5. **Backward Compatible**: Old files are backed up, core APIs maintained
   - data_manager unchanged
   - visualization helpers unchanged
   - embedding/dimred APIs unchanged
```
