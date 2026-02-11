"""
API Package - Blueprint Registration
"""

from flask import Blueprint

# Import blueprints
from professor_routes import professor_bp
from knowledge_graph_routes import knowledge_graph_bp

__all__ = ['professor_bp', 'knowledge_graph_bp']
