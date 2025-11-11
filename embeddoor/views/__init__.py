"""Views module for embeddoor.

This module contains modular view handlers for different visualization types.
Each view can be displayed independently in floating panels.
"""

from embeddoor.views.plot import register_plot_routes
from embeddoor.views.table import register_table_routes
from embeddoor.views.wordcloud import register_wordcloud_routes
from embeddoor.views.images import register_images_routes

def register_all_views(app):
    """Register all view routes with the Flask app."""
    register_plot_routes(app)
    register_table_routes(app)
    register_wordcloud_routes(app)
    register_images_routes(app)
