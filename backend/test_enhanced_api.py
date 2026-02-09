"""
Test enhanced API endpoints with profile data
"""
import sqlite3
import json

def test_enhanced_api_data():
    """Test that the database has the enhanced profile data available"""
    print("🔍 Testing enhanced API data availability...")
    
    conn = sqlite3.connect('teachers.db')
    cursor = conn.cursor()
    
    # Check teachers with profile data
    cursor.execute('''
        SELECT id, name, profile_picture_url, scholar_profile_picture, 
               total_citations, h_index, research_interests, affiliation,
               bio, recent_publications
        FROM teachers 
        WHERE profile_data_updated IS NOT NULL
    ''')
    
    teachers_with_profiles = cursor.fetchall()
    print(f"Found {len(teachers_with_profiles)} teachers with extracted profile data")
    
    # Show sample data for API testing
    for teacher in teachers_with_profiles:
        teacher_id, name, profile_pic, scholar_pic, citations, h_index, interests, affiliation, bio, publications = teacher
        
        print(f"\n👤 {name} (ID: {teacher_id})")
        
        # Profile pictures
        if profile_pic:
            print(f"  📸 Profile Picture: {profile_pic}")
        if scholar_pic:
            print(f"  🎓 Scholar Picture: {scholar_pic}")
        
        # Metrics
        if citations:
            print(f"  📊 Citations: {citations}")
        if h_index:
            print(f"  📈 H-Index: {h_index}")
        
        # Details
        if interests:
            print(f"  🔬 Research Interests: {interests}")
        if affiliation:
            print(f"  🏛️  Affiliation: {affiliation}")
        if bio:
            print(f"  📝 Bio: {bio[:100]}...")
        
        # Publications sample
        if publications:
            try:
                pubs = json.loads(publications)
                if isinstance(pubs, list) and len(pubs) > 0:
                    print(f"  📚 Recent Publications: {len(pubs)} papers")
                    print(f"    - {pubs[0].get('title', 'No title')[:60]}...")
            except:
                print(f"  📚 Publications: Available")
    
    # Test API query structure
    print(f"\n🔧 Testing API query structure...")
    cursor.execute('''
        SELECT id, name, college, email, profile_link, domain_expertise, 
               phd_thesis, google_scholar_url, semantic_scholar_url, 
               timestamp, has_google_scholar, has_semantic_scholar, 
               row_number, extraction_timestamp, created_at,
               profile_picture_url, scholar_profile_picture, bio, phone, 
               office_location, education, teaching_areas, awards, 
               college_publications, total_citations, h_index, i10_index, 
               research_interests, affiliation, recent_publications, 
               frequent_coauthors, semantic_h_index, total_papers, 
               semantic_citations, semantic_research_areas, notable_papers, 
               profile_data_updated
        FROM teachers 
        WHERE profile_data_updated IS NOT NULL
        LIMIT 1
    ''')
    
    sample_teacher = cursor.fetchone()
    if sample_teacher:
        print("✅ API query structure is valid")
        print(f"Sample teacher record has {len(sample_teacher)} fields")
        
        # Create sample API response
        teacher_dict = {
            'id': sample_teacher[0],
            'name': sample_teacher[1],
            'college': sample_teacher[2],
            'email': sample_teacher[3],
            'profile_link': sample_teacher[4],
            'domain_expertise': sample_teacher[5],
            'phd_thesis': sample_teacher[6],
            'google_scholar_url': sample_teacher[7],
            'semantic_scholar_url': sample_teacher[8],
            'timestamp': sample_teacher[9],
            'has_google_scholar': bool(sample_teacher[10]),
            'has_semantic_scholar': bool(sample_teacher[11]),
            'row_number': sample_teacher[12],
            'extraction_timestamp': sample_teacher[13],
            'created_at': sample_teacher[14],
            # Enhanced profile data
            'profile_picture_url': sample_teacher[15],
            'scholar_profile_picture': sample_teacher[16],
            'bio': sample_teacher[17],
            'phone': sample_teacher[18],
            'office_location': sample_teacher[19],
            'education': sample_teacher[20],
            'teaching_areas': sample_teacher[21],
            'awards': sample_teacher[22],
            'college_publications': sample_teacher[23],
            'total_citations': sample_teacher[24],
            'h_index': sample_teacher[25],
            'i10_index': sample_teacher[26],
            'research_interests': sample_teacher[27],
            'affiliation': sample_teacher[28],
            'recent_publications': sample_teacher[29],
            'frequent_coauthors': sample_teacher[30],
            'semantic_h_index': sample_teacher[31],
            'total_papers': sample_teacher[32],
            'semantic_citations': sample_teacher[33],
            'semantic_research_areas': sample_teacher[34],
            'notable_papers': sample_teacher[35],
            'profile_data_updated': sample_teacher[36]
        }
        
        print(f"✅ Sample API response structure created successfully")
        print(f"Enhanced fields with data:")
        enhanced_fields = [
            'profile_picture_url', 'scholar_profile_picture', 'bio', 
            'total_citations', 'h_index', 'research_interests', 'affiliation'
        ]
        
        for field in enhanced_fields:
            value = teacher_dict.get(field)
            if value:
                print(f"  - {field}: ✅")
            else:
                print(f"  - {field}: ❌")
    
    conn.close()
    print(f"\n✅ Enhanced API data test completed!")

if __name__ == "__main__":
    test_enhanced_api_data()