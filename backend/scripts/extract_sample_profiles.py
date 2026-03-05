"""
Extract profile data for sample teachers
"""
from profile_data_extractor import ProfileDataExtractor
import sqlite3
import json

def extract_sample_profiles():
    """Extract profile data for a few sample teachers"""
    print("🔄 Starting sample profile data extraction...")
    
    conn = sqlite3.connect('teachers.db')
    cursor = conn.cursor()
    
    # Get teachers with profile links (limit to 3 for testing)
    cursor.execute('''
        SELECT id, name, profile_link, google_scholar_url, semantic_scholar_url 
        FROM teachers 
        WHERE (profile_link IS NOT NULL AND profile_link != '') 
           OR (google_scholar_url IS NOT NULL AND google_scholar_url != '')
        LIMIT 3
    ''')
    
    teachers = cursor.fetchall()
    print(f"Found {len(teachers)} teachers to process")
    
    extractor = ProfileDataExtractor()
    
    for teacher_id, name, profile_link, google_scholar_url, semantic_scholar_url in teachers:
        print(f"\n📋 Processing: {name}")
        print(f"Profile Link: {profile_link if profile_link else 'None'}")
        print(f"Google Scholar: {google_scholar_url if google_scholar_url else 'None'}")
        print(f"Semantic Scholar: {semantic_scholar_url if semantic_scholar_url else 'None'}")
        
        try:
            # Extract all profile data
            profile_data = extractor.extract_all_profile_data(
                name, profile_link, google_scholar_url, semantic_scholar_url
            )
            
            if profile_data and len(profile_data) > 1:  # More than just teacher_name
                print(f"✅ Extracted {len(profile_data)-1} profile fields")
                
                # Prepare update query
                update_fields = []
                update_values = []
                
                for key, value in profile_data.items():
                    if key != 'teacher_name' and value is not None:
                        if isinstance(value, (list, dict)):
                            value = json.dumps(value)
                        update_fields.append(f'{key} = ?')
                        update_values.append(value)
                
                if update_fields:
                    update_fields.append('profile_data_updated = CURRENT_TIMESTAMP')
                    update_values.append(teacher_id)
                    
                    update_query = f'''
                        UPDATE teachers 
                        SET {', '.join(update_fields)}
                        WHERE id = ?
                    '''
                    
                    cursor.execute(update_query, update_values)
                    conn.commit()
                    
                    print(f"💾 Updated database with {len(update_fields)-1} fields")
                    
                    # Show what was extracted
                    print("📊 Extracted data:")
                    for key, value in profile_data.items():
                        if key != 'teacher_name' and value is not None:
                            if isinstance(value, str) and len(str(value)) > 100:
                                print(f"  {key}: {str(value)[:100]}...")
                            else:
                                print(f"  {key}: {value}")
            else:
                print("⚠️  No profile data extracted")
                
        except Exception as e:
            print(f"❌ Error processing {name}: {str(e)}")
            continue
    
    # Verify the results
    print(f"\n🔍 Verification - checking updated teachers:")
    cursor.execute('''
        SELECT name, profile_picture_url, scholar_profile_picture, total_citations, 
               h_index, research_interests, affiliation
        FROM teachers 
        WHERE profile_data_updated IS NOT NULL
    ''')
    
    updated_teachers = cursor.fetchall()
    print(f"Found {len(updated_teachers)} teachers with profile data")
    
    for teacher in updated_teachers:
        name, profile_pic, scholar_pic, citations, h_index, interests, affiliation = teacher
        print(f"\n👤 {name}")
        if profile_pic:
            print(f"  📸 Profile Picture: {profile_pic}")
        if scholar_pic:
            print(f"  🎓 Scholar Picture: {scholar_pic}")
        if citations:
            print(f"  📊 Citations: {citations}")
        if h_index:
            print(f"  📈 H-Index: {h_index}")
        if interests:
            print(f"  🔬 Research Interests: {interests}")
        if affiliation:
            print(f"  🏛️  Affiliation: {affiliation}")
    
    conn.close()
    print(f"\n✅ Sample profile extraction completed!")

if __name__ == "__main__":
    extract_sample_profiles()