"""Main Flask application for embeddoor."""

import os
from flask import Flask, render_template, jsonify, request, session
import secrets

from embeddoor.data_manager import DataManager
from embeddoor.routes import register_routes


def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__)
    
    # Secret key for session management
    app.config['SECRET_KEY'] = secrets.token_hex(16)
    app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB max file size
    
    # Initialize data manager
    app.data_manager = DataManager()
    
    # Register routes
    register_routes(app)
    
    @app.route('/')
    def index():
        """Main application page."""
        return render_template('index.html')
    
    @app.route('/health')
    def health():
        """Health check endpoint."""
        return jsonify({'status': 'ok'})
    
    return app
