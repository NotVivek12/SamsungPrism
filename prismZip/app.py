import os
import time
import logging
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS

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
from professors import init_professors_db
from professor_routes import professor_bp
from auto_extract_teachers import auto_extract_teachers

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

# Google Scholar request delay (in seconds)
REQUEST_DELAY = int(os.getenv('REQUEST_DELAY', 5))

# Initialize databases and auto-extract teachers
init_professors_db()

# Automatically extract all teachers from Excel on startup
print("🚀 Initializing teacher database...")
try:
    auto_extract_teachers()
    print("✅ Teacher extraction completed successfully!")
except Exception as e:
    print(f"❌ Error during teacher extraction: {str(e)}")
    logging.error(f"Teacher extraction error: {str(e)}")

if __name__ == '__main__':
    try:
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
