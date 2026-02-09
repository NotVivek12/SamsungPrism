"""
Script to add new database columns for enhanced profile data
"""
import sqlite3
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def add_profile_columns():
    """Add new columns to store enhanced profile data"""
    conn = sqlite3.connect('teachers.db')
    cursor = conn.cursor()
    
    # New columns to add
    new_columns = [
        ('profile_picture_url', 'TEXT'),
        ('scholar_profile_picture', 'TEXT'),
        ('bio', 'TEXT'),
        ('phone', 'TEXT'),
        ('office_location', 'TEXT'),
        ('education', 'TEXT'),
        ('teaching_areas', 'TEXT'),
        ('awards', 'TEXT'),
        ('college_publications', 'TEXT'),
        ('total_citations', 'INTEGER'),
        ('h_index', 'INTEGER'),
        ('i10_index', 'INTEGER'),
        ('research_interests', 'TEXT'),
        ('affiliation', 'TEXT'),
        ('recent_publications', 'TEXT'),
        ('frequent_coauthors', 'TEXT'),
        ('semantic_h_index', 'INTEGER'),
        ('total_papers', 'INTEGER'),
        ('semantic_citations', 'INTEGER'),
        ('semantic_research_areas', 'TEXT'),
        ('notable_papers', 'TEXT'),
        ('profile_data_updated', 'TIMESTAMP')
    ]
    
    added_columns = []
    existing_columns = []
    
    for column_name, column_type in new_columns:
        try:
            cursor.execute(f'ALTER TABLE teachers ADD COLUMN {column_name} {column_type}')
            added_columns.append(column_name)
            logger.info(f"✅ Added column: {column_name}")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                existing_columns.append(column_name)
                logger.info(f"⚠️  Column already exists: {column_name}")
            else:
                logger.error(f"❌ Error adding column {column_name}: {e}")
    
    conn.commit()
    
    # Verify the new schema
    cursor.execute('PRAGMA table_info(teachers)')
    columns = cursor.fetchall()
    
    print(f"\n📊 Database Schema Update Summary:")
    print(f"Added {len(added_columns)} new columns")
    print(f"Found {len(existing_columns)} existing columns")
    print(f"Total columns in teachers table: {len(columns)}")
    
    print(f"\n🆕 Newly added columns:")
    for col in added_columns:
        print(f"  - {col}")
    
    if existing_columns:
        print(f"\n♻️  Already existing columns:")
        for col in existing_columns:
            print(f"  - {col}")
    
    print(f"\n📋 Complete database schema:")
    for col in columns:
        print(f"  {col[1]} ({col[2]})")
    
    conn.close()
    print(f"\n✅ Database schema update completed!")

if __name__ == "__main__":
    add_profile_columns()