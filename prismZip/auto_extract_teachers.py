"""
Enhanced automatic teacher extraction that runs when backend starts
This module automatically fetches all 208 rows from sirs.xlsx and stores them in the database
"""

import pandas as pd
import sqlite3
import os
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DATABASE = 'teachers.db'
EXCEL_FILE_PATH = r"c:\Users\ssd99\OneDrive\Desktop\new prism\sirs.xlsx"

def init_teachers_db():
    """Initialize the teachers database with enhanced schema"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Drop existing table to ensure clean start
    cursor.execute('DROP TABLE IF EXISTS teachers')
    
    cursor.execute('''
        CREATE TABLE teachers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            college TEXT,
            email TEXT,
            profile_link TEXT,
            domain_expertise TEXT,
            phd_thesis TEXT,
            google_scholar_url TEXT,
            semantic_scholar_url TEXT,
            timestamp TEXT,
            has_google_scholar BOOLEAN DEFAULT 0,
            has_semantic_scholar BOOLEAN DEFAULT 0,
            row_number INTEGER,
            extraction_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()
    logger.info("✅ Teachers database initialized successfully")

def clean_value(value):
    """Clean pandas NaN values and convert to string"""
    if pd.isna(value) or value is None:
        return ""
    return str(value).strip()

def validate_url(url):
    """Check if URL is valid and not empty"""
    if not url or url.strip() == "":
        return False
    url = url.strip().lower()
    return url.startswith('http') and len(url) > 10

def extract_all_teachers():
    """Extract all teacher details from Excel file and store in database"""
    try:
        if not os.path.exists(EXCEL_FILE_PATH):
            logger.error(f"❌ Excel file not found: {EXCEL_FILE_PATH}")
            return False
        
        # Read Excel file
        logger.info(f"📊 Reading Excel file: {EXCEL_FILE_PATH}")
        df = pd.read_excel(EXCEL_FILE_PATH)
        logger.info(f"📈 Total rows in Excel: {len(df)}")
        
        # Initialize database
        init_teachers_db()
        
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        
        teachers_processed = 0
        teachers_saved = 0
        
        for index, row in df.iterrows():
            teachers_processed += 1
            
            # Extract and clean data
            name = clean_value(row.get('Teacher Name', ''))
            
            # Skip empty names or test entries
            if not name or name.lower() in ['test', 'nan', '']:
                continue
            
            # Extract all fields
            teacher_data = {
                'name': name,
                'college': clean_value(row.get('College', '')),
                'email': clean_value(row.get('College Email Id', '')),
                'profile_link': clean_value(row.get('College Profile Link(please mention your profile link)', '')),
                'domain_expertise': clean_value(row.get('Domain Expertise', '')),
                'phd_thesis': clean_value(row.get('Ph D Thesis', '')),
                'google_scholar_url': clean_value(row.get('Google Scholar URL', '')),
                'semantic_scholar_url': clean_value(row.get('Semantic Scholar Link', '')),
                'timestamp': clean_value(row.get('Timestamp', '')),
                'row_number': index + 1
            }
            
            # Validate URLs and set boolean flags
            has_google_scholar = validate_url(teacher_data['google_scholar_url'])
            has_semantic_scholar = validate_url(teacher_data['semantic_scholar_url'])
            
            try:
                # Insert into database
                cursor.execute('''
                    INSERT INTO teachers 
                    (name, college, email, profile_link, domain_expertise, phd_thesis, 
                     google_scholar_url, semantic_scholar_url, timestamp, 
                     has_google_scholar, has_semantic_scholar, row_number, extraction_timestamp)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    teacher_data['name'],
                    teacher_data['college'],
                    teacher_data['email'],
                    teacher_data['profile_link'],
                    teacher_data['domain_expertise'],
                    teacher_data['phd_thesis'],
                    teacher_data['google_scholar_url'],
                    teacher_data['semantic_scholar_url'],
                    teacher_data['timestamp'],
                    has_google_scholar,
                    has_semantic_scholar,
                    teacher_data['row_number'],
                    datetime.now().isoformat()
                ))
                teachers_saved += 1
                
            except Exception as e:
                logger.error(f"❌ Error saving teacher {teacher_data['name']}: {str(e)}")
        
        conn.commit()
        conn.close()
        
        # Log summary
        logger.info(f"✅ Teacher extraction completed successfully!")
        logger.info(f"📊 Total rows processed: {teachers_processed}")
        logger.info(f"💾 Teachers saved to database: {teachers_saved}")
        
        # Get statistics
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM teachers')
        total_count = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM teachers WHERE has_google_scholar = 1')
        google_scholar_count = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM teachers WHERE has_semantic_scholar = 1')
        semantic_scholar_count = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM teachers WHERE domain_expertise != ""')
        with_expertise_count = cursor.fetchone()[0]
        
        conn.close()
        
        logger.info(f"📈 Database Statistics:")
        logger.info(f"  - Total teachers: {total_count}")
        logger.info(f"  - With Google Scholar: {google_scholar_count}")
        logger.info(f"  - With Semantic Scholar: {semantic_scholar_count}")
        logger.info(f"  - With Domain Expertise: {with_expertise_count}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error during teacher extraction: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return False

def check_database_status():
    """Check if teachers are already loaded in database"""
    try:
        if not os.path.exists(DATABASE):
            return False
        
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        
        # Check if teachers table exists and has data
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='teachers'")
        if not cursor.fetchone():
            conn.close()
            return False
        
        cursor.execute('SELECT COUNT(*) FROM teachers')
        count = cursor.fetchone()[0]
        conn.close()
        
        return count > 0
        
    except Exception:
        return False

def auto_extract_teachers():
    """Main function to automatically extract teachers on backend startup"""
    logger.info("🚀 Starting automatic teacher extraction process...")
    
    # Check if data already exists
    if check_database_status():
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM teachers')
        existing_count = cursor.fetchone()[0]
        conn.close()
        
        logger.info(f"📊 Teachers already loaded in database: {existing_count} records")
        logger.info("✅ Skipping extraction (data already present)")
        return True
    
    # Extract fresh data
    logger.info("📥 No existing teacher data found, extracting from Excel...")
    success = extract_all_teachers()
    
    if success:
        logger.info("✅ Automatic teacher extraction completed successfully!")
    else:
        logger.error("❌ Automatic teacher extraction failed!")
    
    return success

def force_refresh_teachers():
    """Force refresh all teacher data (for manual refresh)"""
    logger.info("🔄 Force refreshing all teacher data...")
    return extract_all_teachers()

if __name__ == "__main__":
    auto_extract_teachers()