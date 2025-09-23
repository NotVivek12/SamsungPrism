"""
Simple Excel processor for extracting teacher details from sirs.xlsx
This script processes the Excel file and extracts all teacher information
"""

import pandas as pd
import json
import sqlite3
import os
from datetime import datetime

# Database setup
DATABASE = 'teachers.db'

def init_db():
    """Initialize the database with teachers table"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS teachers (
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
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ Database initialized successfully")

def clean_value(value):
    """Clean pandas NaN values and convert to string"""
    if pd.isna(value):
        return ""
    return str(value).strip()

def process_excel_file(file_path):
    """Process the Excel file and extract teacher details"""
    try:
        # Read the Excel file
        df = pd.read_excel(file_path)
        print(f"📊 Loaded Excel file with {len(df)} rows")
        
        # Clean the data
        df_clean = df.dropna(subset=['Teacher Name'])
        df_clean = df_clean[df_clean['Teacher Name'] != 'test']
        df_clean = df_clean[df_clean['Teacher Name'].str.strip() != '']
        
        print(f"📝 After cleaning: {len(df_clean)} valid teacher records")
        
        # Initialize database
        init_db()
        
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        
        teachers = []
        saved_count = 0
        
        for index, row in df_clean.iterrows():
            teacher_data = {
                'name': clean_value(row.get('Teacher Name', '')),
                'college': clean_value(row.get('College', '')),
                'email': clean_value(row.get('College Email Id', '')),
                'profile_link': clean_value(row.get('College Profile Link(please mention your profile link)', '')),
                'domain_expertise': clean_value(row.get('Domain Expertise', '')),
                'phd_thesis': clean_value(row.get('Ph D Thesis', '')),
                'google_scholar_url': clean_value(row.get('Google Scholar URL', '')),
                'semantic_scholar_url': clean_value(row.get('Semantic Scholar Link', '')),
                'timestamp': clean_value(row.get('Timestamp', ''))
            }
            
            # Save to database
            try:
                cursor.execute('''
                    INSERT INTO teachers 
                    (name, college, email, profile_link, domain_expertise, phd_thesis, 
                     google_scholar_url, semantic_scholar_url, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    teacher_data['name'],
                    teacher_data['college'],
                    teacher_data['email'],
                    teacher_data['profile_link'],
                    teacher_data['domain_expertise'],
                    teacher_data['phd_thesis'],
                    teacher_data['google_scholar_url'],
                    teacher_data['semantic_scholar_url'],
                    teacher_data['timestamp']
                ))
                saved_count += 1
            except Exception as e:
                print(f"❌ Error saving teacher {teacher_data['name']}: {str(e)}")
            
            teachers.append(teacher_data)
        
        conn.commit()
        conn.close()
        
        print(f"✅ Successfully processed {len(teachers)} teachers")
        print(f"💾 Saved {saved_count} teachers to database")
        
        return teachers
        
    except Exception as e:
        print(f"❌ Error processing Excel file: {str(e)}")
        return []

def save_to_json(teachers, filename='teachers_data.json'):
    """Save teacher data to JSON file"""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(teachers, f, indent=2, ensure_ascii=False)
        print(f"📄 Teacher data saved to {filename}")
    except Exception as e:
        print(f"❌ Error saving to JSON: {str(e)}")

def display_teacher_summary(teachers):
    """Display summary of teacher data"""
    if not teachers:
        print("❌ No teacher data to display")
        return
    
    print("\n" + "="*80)
    print("📊 TEACHER DATA SUMMARY")
    print("="*80)
    
    # Statistics
    total_teachers = len(teachers)
    with_google_scholar = sum(1 for t in teachers if t['google_scholar_url'])
    with_semantic_scholar = sum(1 for t in teachers if t['semantic_scholar_url'])
    with_domain_expertise = sum(1 for t in teachers if t['domain_expertise'])
    with_phd_thesis = sum(1 for t in teachers if t['phd_thesis'])
    
    print(f"📈 Total Teachers: {total_teachers}")
    print(f"🔗 With Google Scholar: {with_google_scholar} ({with_google_scholar/total_teachers*100:.1f}%)")
    print(f"🔗 With Semantic Scholar: {with_semantic_scholar} ({with_semantic_scholar/total_teachers*100:.1f}%)")
    print(f"🎓 With Domain Expertise: {with_domain_expertise} ({with_domain_expertise/total_teachers*100:.1f}%)")
    print(f"📚 With PhD Thesis: {with_phd_thesis} ({with_phd_thesis/total_teachers*100:.1f}%)")
    
    # Top domains
    domains = [t['domain_expertise'] for t in teachers if t['domain_expertise']]
    if domains:
        print(f"\n🏆 TOP DOMAINS:")
        domain_count = {}
        for domain in domains:
            # Split multiple domains and count each
            parts = domain.replace(',', ';').split(';')
            for part in parts:
                part = part.strip()
                if part:
                    domain_count[part] = domain_count.get(part, 0) + 1
        
        sorted_domains = sorted(domain_count.items(), key=lambda x: x[1], reverse=True)[:10]
        for i, (domain, count) in enumerate(sorted_domains, 1):
            print(f"{i:2d}. {domain}: {count} teachers")
    
    # Sample teachers
    print(f"\n👥 SAMPLE TEACHERS:")
    for i, teacher in enumerate(teachers[:10], 1):
        status = "🔗" if teacher['google_scholar_url'] else "📝"
        print(f"{i:2d}. {status} {teacher['name']} - {teacher['college']}")
        if teacher['domain_expertise']:
            print(f"    📖 {teacher['domain_expertise']}")
    
    if len(teachers) > 10:
        print(f"    ... and {len(teachers) - 10} more teachers")

def main():
    """Main function to process the sirs.xlsx file"""
    file_path = r"c:\Users\ssd99\OneDrive\Desktop\new prism\sirs.xlsx"
    
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return
    
    print("🚀 Starting teacher details extraction from sirs.xlsx")
    print("-" * 60)
    
    # Process the Excel file
    teachers = process_excel_file(file_path)
    
    if teachers:
        # Save to JSON
        save_to_json(teachers)
        
        # Display summary
        display_teacher_summary(teachers)
        
        print("\n" + "="*80)
        print("✅ EXTRACTION COMPLETED SUCCESSFULLY!")
        print("="*80)
        print(f"📄 Data saved to: teachers_data.json")
        print(f"💾 Database: {DATABASE}")
        print(f"📊 Total teachers processed: {len(teachers)}")
    else:
        print("❌ No teacher data extracted")

if __name__ == "__main__":
    main()