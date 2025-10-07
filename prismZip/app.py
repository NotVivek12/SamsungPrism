import os
import time
import logging
import json
import uuid
import pandas as pd
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
from professor_routes import professor_bp

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

# Setup Excel data access
print("📊 Excel data reading function ready")
print("🔍 Excel data will be read directly on API requests")
print("✅ Direct Excel data access configured!")

# Google Scholar request delay (in seconds)
REQUEST_DELAY = int(os.getenv('REQUEST_DELAY', 5))

# Define the Excel file path - adjust as needed
EXCEL_FILE_PATH = "../prof.xlsx"
TEACHERS_DATA_PATH = "teachers_data.json"

def extract_data_from_excel():
    """Extract teacher data from Excel and create JSON file"""
    try:
        print(f"📊 Reading Excel file: {EXCEL_FILE_PATH}")
        df = pd.read_excel(EXCEL_FILE_PATH)
        print(f"✅ Successfully read {len(df)} rows from Excel")
        
        # Clean up column names
        df.columns = [str(col).strip() for col in df.columns]
        
        # Convert DataFrame to list of dictionaries
        teachers = []
        
        for index, row in df.iterrows():
            # Extract basic info
            teacher = {
                'id': str(uuid.uuid4())[:8],  # Generate unique ID
                'name': str(row.get('name', row.get('Name', ''))),
                'college': str(row.get('college', row.get('College', row.get('institution', '')))),
                'email': str(row.get('email', row.get('Email', ''))),
                'profile_link': str(row.get('profile_link', row.get('Profile Link', ''))),
                'domain_expertise': str(row.get('domain_expertise', row.get('Domain Expertise', ''))),
                'phd_thesis': str(row.get('phd_thesis', row.get('PhD Thesis', ''))),
                'google_scholar_url': str(row.get('google_scholar_url', row.get('Google Scholar URL', ''))),
                'semantic_scholar_url': str(row.get('semantic_scholar_url', row.get('Semantic Scholar URL', ''))),
                'profile_picture_url': str(row.get('profile_picture_url', row.get('Profile Picture URL', ''))),
                'has_google_scholar': bool(row.get('google_scholar_url', row.get('Google Scholar URL', ''))),
                'has_semantic_scholar': bool(row.get('semantic_scholar_url', row.get('Semantic Scholar URL', ''))),
            }
            
            # Clean up data - replace 'nan' with empty string
            for key, value in teacher.items():
                if str(value).lower() == 'nan':
                    teacher[key] = ''
                    
            # Extract domain expertise as a list
            if teacher['domain_expertise'] and teacher['domain_expertise'] != 'nan':
                expertise_list = [area.strip() for area in str(teacher['domain_expertise']).split(',')]
                teacher['expertise_array'] = expertise_list
            else:
                teacher['expertise_array'] = []
                
            teachers.append(teacher)
        
        # Save to JSON file
        data = {'teachers': teachers}
        with open(TEACHERS_DATA_PATH, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            
        print(f"💾 Saved {len(teachers)} teachers to {TEACHERS_DATA_PATH}")
        return teachers
        
    except FileNotFoundError:
        print(f"❌ Excel file not found: {EXCEL_FILE_PATH}")
        return []
    except Exception as e:
        print(f"❌ Error extracting data from Excel: {e}")
        import traceback
        traceback.print_exc()
        return []

def load_teachers_data():
    """Load teacher data from JSON file or create from Excel if not exists"""
    try:
        # Try to read existing JSON file
        with open(TEACHERS_DATA_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
            teachers = data.get('teachers', [])
            print(f"✅ Found {len(teachers)} teachers in data file")
            return teachers
    except FileNotFoundError:
        # If not found, extract from Excel
        print(f"⚠️ {TEACHERS_DATA_PATH} not found, extracting from Excel...")
        return extract_data_from_excel()
    except Exception as e:
        print(f"❌ Error reading teacher data: {e}")
        # Try to extract from Excel as fallback
        return extract_data_from_excel()

# Register a route to extract data on demand
@app.route('/api/extract-data', methods=['POST'])
def api_extract_data():
    """Extract data from Excel file on demand"""
    try:
        # Force extraction from Excel
        teachers = extract_data_from_excel()
        return jsonify({
            'success': True,
            'message': f'Successfully extracted {len(teachers)} teachers from Excel',
            'count': len(teachers)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Load teachers data on startup
print("🚀 Initializing teacher data...")
teachers = load_teachers_data()
print(f"✅ Loaded {len(teachers)} teachers successfully!")

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
