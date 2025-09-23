#!/usr/bin/env python3
"""
Fix the teachers database schema by adding missing columns
"""

import sqlite3
from datetime import datetime

def fix_database_schema():
    """Add missing columns to the teachers database"""
    try:
        conn = sqlite3.connect('teachers.db')
        cursor = conn.cursor()
        
        # Check current schema
        cursor.execute('PRAGMA table_info(teachers)')
        existing_columns = [col[1] for col in cursor.fetchall()]
        print(f"Existing columns: {existing_columns}")
        
        # Add missing columns
        missing_columns = [
            ('has_google_scholar', 'BOOLEAN DEFAULT 0'),
            ('has_semantic_scholar', 'BOOLEAN DEFAULT 0'), 
            ('row_number', 'INTEGER'),
            ('extraction_timestamp', 'TEXT')
        ]
        
        for col_name, col_def in missing_columns:
            if col_name not in existing_columns:
                try:
                    cursor.execute(f'ALTER TABLE teachers ADD COLUMN {col_name} {col_def}')
                    print(f"✅ Added column: {col_name}")
                except Exception as e:
                    print(f"❌ Failed to add {col_name}: {e}")
            else:
                print(f"⏭️ Column {col_name} already exists")
        
        # Update existing records with default values
        current_time = datetime.now().isoformat()
        
        # Set row numbers based on existing order
        cursor.execute('SELECT id FROM teachers ORDER BY id')
        teacher_ids = [row[0] for row in cursor.fetchall()]
        
        for i, teacher_id in enumerate(teacher_ids, 1):
            cursor.execute('''
                UPDATE teachers 
                SET row_number = ?, extraction_timestamp = ?
                WHERE id = ? AND (row_number IS NULL OR extraction_timestamp IS NULL)
            ''', (i, current_time, teacher_id))
        
        # Update scholar flags based on URLs
        cursor.execute('''
            UPDATE teachers 
            SET has_google_scholar = 1 
            WHERE google_scholar_url IS NOT NULL AND google_scholar_url != ""
        ''')
        
        cursor.execute('''
            UPDATE teachers 
            SET has_semantic_scholar = 1 
            WHERE semantic_scholar_url IS NOT NULL AND semantic_scholar_url != ""
        ''')
        
        conn.commit()
        
        # Verify the fix
        cursor.execute('PRAGMA table_info(teachers)')
        final_columns = [col[1] for col in cursor.fetchall()]
        print(f"\nFinal columns: {final_columns}")
        
        cursor.execute('SELECT COUNT(*) FROM teachers')
        count = cursor.fetchone()[0]
        print(f"✅ Database schema fixed! {count} teachers ready.")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error fixing database: {e}")
        return False

if __name__ == "__main__":
    fix_database_schema()