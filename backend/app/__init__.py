"""
PRISM Backend Application Package
Application Factory Pattern for Flask
"""

from flask import Flask
from flask_cors import CORS
import logging
import os


def create_app(config_name='development'):
    """
    Application factory function
    
    Args:
        config_name: Configuration environment (development, production, testing)
    
    Returns:
        Flask application instance
    """
    app = Flask(__name__)
    
    # Enable CORS
    CORS(app)
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Load configuration
    app.config['DB_HOST'] = os.getenv('DB_HOST', 'localhost')
    app.config['DB_NAME'] = os.getenv('DB_NAME', 'prism_professors')
    app.config['DB_USER'] = os.getenv('DB_USER', 'root')
    app.config['DB_PASSWORD'] = os.getenv('DB_PASSWORD', '')
    app.config['DB_PORT'] = int(os.getenv('DB_PORT', 3306))
    
    # Register blueprints
    from app.api import professor_bp, knowledge_graph_bp
    app.register_blueprint(professor_bp)
    app.register_blueprint(knowledge_graph_bp)
    
    return app
