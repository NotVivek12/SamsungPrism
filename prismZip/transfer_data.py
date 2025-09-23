"""
Transfer teacher data from teachers.db to professors.db
This script converts teacher records to professor format and populates the main database
"""

import sqlite3
import json
from professors import save_professor_to_db, init_professors_db

def transfer_teachers_to_professors():
    """Transfer teacher data to professors database"""
    try:
        # Initialize professors database
        init_professors_db()
        
        # Connect to teachers database
        teachers_conn = sqlite3.connect('teachers.db')
        teachers_cursor = teachers_conn.cursor()
        
        # Get all teachers
        teachers_cursor.execute('''
            SELECT name, college, email, domain_expertise, phd_thesis, 
                   google_scholar_url, semantic_scholar_url
            FROM teachers
        ''')
        
        teachers = teachers_cursor.fetchall()
        teachers_conn.close()
        
        print(f"Found {len(teachers)} teachers to transfer")
        
        transferred_count = 0
        
        for teacher in teachers:
            name, college, email, domain_expertise, phd_thesis, google_scholar_url, semantic_scholar_url = teacher
            
            # Convert teacher data to professor format
            professor_data = {
                'Teacher Name': name or '',
                'College': college or '',
                'College Email': email or '',
                'Domain Expertise': domain_expertise or '',
                'PhD Thesis': phd_thesis or '',
                'Google Scholar URL': google_scholar_url or '',
                'Semantic Scholar Link': semantic_scholar_url or '',
                'Google Scholar Data': {
                    'Citations': 0,
                    'h-index': 0,
                    'i10-index': 0,
                    'Total Publications': 0,
                    'Research Interests': domain_expertise.split(',') if domain_expertise else [],
                    'Current Affiliation': college or 'Not available',
                    'Publications': []
                },
                'Semantic Scholar Data': {
                    'Citations': 0,
                    'h-index': 0,
                    'Total Publications': 0,
                    'Current Affiliation': college or 'Not available',
                    'Research Topics': [],
                    'Publications': [],
                    'Research Trends': {},
                    'Citation Impact': {}
                }
            }
            
            # Save to professors database
            professor_id = save_professor_to_db(professor_data)
            if professor_id:
                transferred_count += 1
                if transferred_count % 10 == 0:
                    print(f"Transferred {transferred_count} professors...")
        
        print(f"✅ Successfully transferred {transferred_count} teachers to professors database")
        return transferred_count
        
    except Exception as e:
        print(f"❌ Error transferring data: {str(e)}")
        return 0

def verify_professors_data():
    """Verify that professors data was transferred correctly"""
    try:
        conn = sqlite3.connect('professors.db')
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM professors')
        total_professors = cursor.fetchone()[0]
        
        cursor.execute('SELECT name, institute, domain FROM professors LIMIT 5')
        sample_professors = cursor.fetchall()
        
        conn.close()
        
        print(f"\n📊 Verification Results:")
        print(f"Total professors in database: {total_professors}")
        print(f"\nSample professors:")
        for i, (name, institute, domain) in enumerate(sample_professors, 1):
            print(f"  {i}. {name} - {institute}")
            print(f"     Domain: {domain}")
        
        return total_professors
        
    except Exception as e:
        print(f"❌ Error verifying data: {str(e)}")
        return 0

if __name__ == "__main__":
    print("🚀 Starting teacher to professor data transfer...")
    print("-" * 60)
    
    # Transfer the data
    transferred = transfer_teachers_to_professors()
    
    if transferred > 0:
        # Verify the transfer
        total = verify_professors_data()
        
        print(f"\n✅ Transfer completed successfully!")
        print(f"📊 Total professors in database: {total}")
        print(f"🔄 Transferred: {transferred} new professors")
    else:
        print("❌ Transfer failed or no data to transfer")