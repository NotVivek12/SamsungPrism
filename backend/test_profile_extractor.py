"""
Test script for profile data extractor
"""
from profile_data_extractor import ProfileDataExtractor
import sqlite3

def test_profile_extractor():
    print("Testing profile data extraction...")
    
    # Check for teachers with profile links
    conn = sqlite3.connect('teachers.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, name, profile_link, google_scholar_url 
        FROM teachers 
        WHERE (profile_link IS NOT NULL AND profile_link != '') 
           OR (google_scholar_url IS NOT NULL AND google_scholar_url != '')
        LIMIT 5
    ''')
    
    teachers = cursor.fetchall()
    conn.close()
    
    print(f"Found {len(teachers)} teachers with profile links for testing")
    
    for teacher in teachers:
        print(f"Teacher: {teacher[1]}")
        print(f"Profile Link: {teacher[2] if teacher[2] else 'None'}")
        print(f"Google Scholar: {teacher[3] if teacher[3] else 'None'}")
        print("---")
    
    # Test the extractor with one teacher
    if teachers:
        extractor = ProfileDataExtractor()
        teacher_id, name, profile_link, google_scholar_url = teachers[0]
        
        print(f"\nTesting extraction for: {name}")
        
        # Test college profile extraction
        if profile_link:
            print("Testing college profile extraction...")
            college_data = extractor.extract_college_profile_data(profile_link)
            print(f"College data extracted: {len(college_data)} fields")
            for key, value in college_data.items():
                print(f"  {key}: {str(value)[:100]}...")
        
        # Test Google Scholar extraction
        if google_scholar_url:
            print("\nTesting Google Scholar extraction...")
            scholar_data = extractor.extract_google_scholar_data(google_scholar_url)
            print(f"Scholar data extracted: {len(scholar_data)} fields")
            for key, value in scholar_data.items():
                print(f"  {key}: {str(value)[:100]}...")

if __name__ == "__main__":
    test_profile_extractor()