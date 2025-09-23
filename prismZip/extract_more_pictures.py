"""
Extract profile data for more teachers to get profile pictures
"""
from profile_data_extractor import ProfileDataExtractor
import sqlite3
import json
import time

def extract_more_profile_pictures():
    """Extract profile data for teachers with profile links to get more profile pictures"""
    print("🖼️  Extracting More Profile Pictures...")
    print("=" * 50)
    
    conn = sqlite3.connect('teachers.db')
    cursor = conn.cursor()
    
    # Check current status
    cursor.execute('''
        SELECT 
            COUNT(*) as total,
            COUNT(CASE WHEN profile_link IS NOT NULL AND profile_link != '' THEN 1 END) as with_profile_link,
            COUNT(CASE WHEN google_scholar_url IS NOT NULL AND google_scholar_url != '' THEN 1 END) as with_scholar,
            COUNT(CASE WHEN profile_data_updated IS NOT NULL THEN 1 END) as already_processed,
            COUNT(CASE WHEN profile_picture_url IS NOT NULL OR scholar_profile_picture IS NOT NULL THEN 1 END) as with_pictures
        FROM teachers
    ''')
    
    stats = cursor.fetchone()
    print(f"📊 Current Status:")
    print(f"   Total teachers: {stats[0]}")
    print(f"   With college profile links: {stats[1]}")
    print(f"   With Google Scholar URLs: {stats[2]}")
    print(f"   Already processed: {stats[3]}")
    print(f"   With profile pictures: {stats[4]}")
    
    # Get teachers that need processing (prioritize those with college profile links)
    cursor.execute('''
        SELECT id, name, profile_link, google_scholar_url, semantic_scholar_url 
        FROM teachers 
        WHERE profile_data_updated IS NULL 
          AND (profile_link IS NOT NULL AND profile_link != '')
        ORDER BY CASE WHEN profile_link IS NOT NULL AND profile_link != '' THEN 1 ELSE 2 END
        LIMIT 15
    ''')
    
    college_profile_teachers = cursor.fetchall()
    
    if not college_profile_teachers:
        # If no college profiles, get Google Scholar ones
        cursor.execute('''
            SELECT id, name, profile_link, google_scholar_url, semantic_scholar_url 
            FROM teachers 
            WHERE profile_data_updated IS NULL 
              AND (google_scholar_url IS NOT NULL AND google_scholar_url != '')
            LIMIT 10
        ''')
        college_profile_teachers = cursor.fetchall()
    
    print(f"\n🎯 Found {len(college_profile_teachers)} teachers to process for profile pictures")
    
    if not college_profile_teachers:
        print("⚠️  No more teachers available for profile extraction")
        conn.close()
        return
    
    # Initialize extractor
    extractor = ProfileDataExtractor()
    processed_count = 0
    pictures_found = 0
    
    for teacher_id, name, profile_link, google_scholar_url, semantic_scholar_url in college_profile_teachers:
        print(f"\n📋 Processing: {name}")
        print(f"   College Profile: {'✅' if profile_link else '❌'}")
        print(f"   Google Scholar: {'✅' if google_scholar_url else '❌'}")
        
        try:
            # Extract profile data
            profile_data = extractor.extract_all_profile_data(
                name, profile_link, google_scholar_url, semantic_scholar_url
            )
            
            if profile_data and len(profile_data) > 1:
                # Check if we got profile pictures
                has_profile_pic = profile_data.get('profile_picture_url')
                has_scholar_pic = profile_data.get('scholar_profile_picture')
                
                if has_profile_pic:
                    print(f"   📸 College Profile Picture: ✅")
                    pictures_found += 1
                if has_scholar_pic:
                    print(f"   🎓 Scholar Profile Picture: ✅")
                    pictures_found += 1
                
                # Update database
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
                    processed_count += 1
                    
                    print(f"   💾 Updated database with {len(update_fields)-1} fields")
            else:
                print(f"   ⚠️  No profile data extracted")
            
            # Be respectful with requests
            time.sleep(2)
            
        except Exception as e:
            print(f"   ❌ Error processing {name}: {str(e)}")
            continue
    
    # Final statistics
    cursor.execute('''
        SELECT 
            COUNT(CASE WHEN profile_picture_url IS NOT NULL THEN 1 END) as college_pics,
            COUNT(CASE WHEN scholar_profile_picture IS NOT NULL THEN 1 END) as scholar_pics,
            COUNT(CASE WHEN profile_picture_url IS NOT NULL OR scholar_profile_picture IS NOT NULL THEN 1 END) as total_with_pics,
            COUNT(*) as total_teachers
        FROM teachers
    ''')
    
    final_stats = cursor.fetchone()
    conn.close()
    
    print(f"\n" + "=" * 50)
    print(f"🎯 PROFILE PICTURE EXTRACTION COMPLETED")
    print(f"=" * 50)
    print(f"✅ Teachers processed: {processed_count}")
    print(f"🖼️  New pictures found: {pictures_found}")
    print(f"\n📊 Final Statistics:")
    print(f"   📸 College Profile Pictures: {final_stats[0]}")
    print(f"   🎓 Scholar Profile Pictures: {final_stats[1]}")
    print(f"   🖼️  Total with Pictures: {final_stats[2]} ({final_stats[2]/final_stats[3]*100:.1f}%)")
    print(f"   👥 Total Teachers: {final_stats[3]}")
    
    return final_stats[2]  # Return total with pictures

if __name__ == "__main__":
    total_with_pics = extract_more_profile_pictures()
    print(f"\n🚀 Ready to showcase {total_with_pics} teachers with profile pictures!")