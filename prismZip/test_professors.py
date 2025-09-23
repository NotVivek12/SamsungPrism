"""
Test script to verify professor data is ready for the React frontend
"""

import sqlite3
import json

def get_professors_simple():
    """Get professors data without Flask context"""
    try:
        conn = sqlite3.connect('professors.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, name, domain, institute, email, bio, education, experience, 
                   projects, research_papers, citations, h_index, i10_index, 
                   total_publications, research_interests, current_affiliation
            FROM professors
        ''')
        
        professors = []
        for row in cursor.fetchall():
            professor = {
                'id': row[0],
                'name': row[1],
                'domain': row[2],
                'institute': row[3],
                'email': row[4],
                'bio': row[5],
                'education': row[6],
                'experience': row[7],
                'projects': json.loads(row[8]) if row[8] else [],
                'researchPapers': json.loads(row[9]) if row[9] else [],
                'citations': row[10],
                'hIndex': row[11],
                'i10Index': row[12],
                'totalPublications': row[13],
                'researchInterests': json.loads(row[14]) if row[14] else [],
                'currentAffiliation': row[15]
            }
            professors.append(professor)
        
        conn.close()
        return professors
        
    except Exception as e:
        print(f"Error fetching professors: {str(e)}")
        return []

def main():
    print("🔍 Testing Professor Data for React Frontend")
    print("=" * 60)
    
    # Get all professors
    professors = get_professors_simple()
    
    if professors:
        print(f"✅ SUCCESS: Found {len(professors)} professors")
        
        # Show sample data
        print(f"\n📋 Sample Professors (first 5):")
        for i, prof in enumerate(professors[:5], 1):
            print(f"{i}. {prof['name']}")
            print(f"   🏛️  {prof['institute']}")
            print(f"   📖 {prof['domain']}")
            print(f"   📧 {prof['email']}")
            print(f"   📈 Citations: {prof['citations']}, h-index: {prof['hIndex']}")
            print()
        
        # Test search functionality
        print("🔍 Testing Search Functionality:")
        ml_professors = [p for p in professors if 'Machine Learning' in (p['domain'] or '')]
        ai_professors = [p for p in professors if 'AI' in (p['domain'] or '') or 'Artificial Intelligence' in (p['domain'] or '')]
        
        print(f"   📚 Machine Learning experts: {len(ml_professors)}")
        print(f"   🤖 AI experts: {len(ai_professors)}")
        
        # Statistics
        with_emails = len([p for p in professors if p['email']])
        with_domains = len([p for p in professors if p['domain']])
        
        print(f"\n📊 Data Quality:")
        print(f"   👥 Total professors: {len(professors)}")
        print(f"   📧 With emails: {with_emails} ({with_emails/len(professors)*100:.1f}%)")
        print(f"   📖 With domains: {with_domains} ({with_domains/len(professors)*100:.1f}%)")
        
        print(f"\n✅ Professor data is ready for React frontend!")
        print(f"🌐 The React app should now be able to fetch and display professors")
        
    else:
        print("❌ ERROR: No professors found in database")

if __name__ == "__main__":
    main()