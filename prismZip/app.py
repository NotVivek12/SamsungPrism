import os
import time
import logging
import json
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
from professor_routes import professor_bp
from knowledge_graph_routes import knowledge_graph_bp

import database

from extract_citations import start_background_extraction

try:
    from dotenv import load_dotenv, find_dotenv
    load_dotenv(find_dotenv())
except Exception:
    print("python-dotenv not available; relying on environment variables")
try:
    import spacy
    from helpers import extract_scholar_data
    from scholar_extractor import extract_semantic_scholar_data, combine_scholar_data
    from google_scholar_extractor import extract_google_scholar_data
    SCHOLAR_ENABLED = True
    
    
    try:
        nlp = spacy.load('en_core_web_sm')
    except (OSError, KeyboardInterrupt) as e:
        print(f"Warning: spaCy model loading issue: {e}")
        print("Scholar extraction may be limited")
        nlp = None
        SCHOLAR_ENABLED = False
except ImportError as e:
    print(f"Scholar extraction modules not available: {e}")
    SCHOLAR_ENABLED = False
    nlp = None

from utils import handle_exceptions
from professor_routes import professor_bp

logging.basicConfig(
    filename='error_log.txt',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

app = Flask(__name__)
CORS(app)

app.register_blueprint(professor_bp)
app.register_blueprint(knowledge_graph_bp)

print("📊 MySQL database connection ready")
print("🔍 Professor data will be read directly from database on API requests")
print("🌐 Knowledge graph API endpoints registered")
print("✅ Database access configured!")

REQUEST_DELAY = int(os.getenv('REQUEST_DELAY', 5))

DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_NAME = os.getenv('DB_NAME', 'prism_professors')
DB_USER = os.getenv('DB_USER', 'root')
DB_PASSWORD = os.getenv('DB_PASSWORD', '')
DB_PORT = int(os.getenv('DB_PORT', 3306))

@app.route('/api/test-database', methods=['GET'])
def api_test_database():
    """Test database connection"""
    try:
        connection = database.get_connection()
        if connection and connection.is_connected():
            database.close_connection(connection)
            return jsonify({
                'success': True,
                'message': f'Successfully connected to MySQL database {DB_NAME} on {DB_HOST}'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to connect to MySQL database'
            }), 500
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

print("🚀 Initializing professor data from database...")
try:
    professors = database.load_professors_data()
    print(f"✅ Loaded {len(professors)} professors successfully from database!")
except Exception as e:
    print(f"❌ Error loading professors data: {e}")
    print("Database connection may not be properly configured. Please check your environment variables.")
    professors = []

if __name__ == '__main__':
    try:
        print("Starting background citation extraction...")
        citation_thread = start_background_extraction()
        print("✅ Background citation extraction started!")
        
        print("Starting Flask application...")
        print(f"Server will run on port {int(os.environ.get('PORT', 5000))}")
        app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
    except Exception as e:
        print(f"Error starting the app: {str(e)}")
        import traceback
        traceback.print_exc()
        logging.error(f"Application startup error: {str(e)}")
        logging.error(traceback.format_exc())
        raise
