import os
import time
import logging
import json
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
from professor_routes import professor_bp
# Import the database module for MySQL access
import database
# Import citation extraction functionality
from extract_citations import start_background_extraction

# Load configuration from .env as early as possible (search parent dirs)
try:
    from dotenv import load_dotenv, find_dotenv
    load_dotenv(find_dotenv())
except Exception:
    print("python-dotenv not available; relying on environment variables")

# Try to import spaCy and related modules, but make them optional
try:
    import spacy
    from helpers import extract_scholar_data
    from scholar_extractor import extract_semantic_scholar_data, combine_scholar_data
    from google_scholar_extractor import extract_google_scholar_data
    SCHOLAR_ENABLED = True
    
    # Load spaCy model with error handling
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

# Configure logging with more detail
logging.basicConfig(
    filename='error_log.txt',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

app = Flask(__name__)
CORS(app)

# Register professor blueprint
app.register_blueprint(professor_bp)

# Setup database access
print("📊 MySQL database connection ready")
print("🔍 Professor data will be read directly from database on API requests")
print("✅ Database access configured!")

# Google Scholar request delay (in seconds)
REQUEST_DELAY = int(os.getenv('REQUEST_DELAY', 5))

# Load database configuration from environment variables
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_NAME = os.getenv('DB_NAME', 'prism_professors')
DB_USER = os.getenv('DB_USER', 'root')
DB_PASSWORD = os.getenv('DB_PASSWORD', '')
DB_PORT = int(os.getenv('DB_PORT', 3306))

# Register a route to test database connection
@app.route('/api/test-database', methods=['GET'])
def api_test_database():
    """Test database connection"""
    try:
        # Try to connect to the database
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

# Load professors data on startup
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
