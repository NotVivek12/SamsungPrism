import os
import json
import sys
import logging
import re

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
CACHE_FILE = 'teacher_citations_cache.json'
JSON_FILE = 'teachers_data.json'

def load_json_teachers():
    """Load teachers from JSON file"""
    try:
        with open(JSON_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        # Check if the data has a "teachers" key (the expected format)
        if isinstance(data, dict) and "teachers" in data:
            teachers = data["teachers"]
            logger.info(f"Successfully loaded {len(teachers)} teachers from {JSON_FILE}")
            return teachers
        else:
            # If it's already an array
            if isinstance(data, list):
                logger.info(f"Successfully loaded {len(data)} teachers from {JSON_FILE}")
                return data
            else:
                logger.error(f"Invalid format in {JSON_FILE}")
                return []
    except Exception as e:
        logger.error(f"Error loading teachers from JSON: {str(e)}")
        return []

def extract_user_id_from_url(url):
    """Extract the Google Scholar user ID from a URL"""
    if not url:
        return None
        
    # Pattern to extract user ID from Google Scholar URL
    pattern = r'user=([^&]+)'
    match = re.search(pattern, url)
    
    if match:
        return match.group(1)
    return None

def update_id_mapping():
    """Create a more accurate mapping between database professor IDs and JSON teacher IDs"""
    try:
        # Import necessary modules
        sys.path.insert(0, '.')
        import database
        from extract_citations import load_teachers_data
        
        # Get teachers from JSON
        json_teachers = load_teachers_data()
        
        # Get professors from database
        db_professors = database.load_professors_data()
        
        # Create a mapping from Google Scholar URL to JSON ID
        url_to_json_id = {}
        user_id_to_json_id = {}
        
        for teacher in json_teachers:
            json_id = teacher.get('id')
            if not json_id:
                continue
                
            gs_url = teacher.get('google_scholar_url', '')
            if gs_url:
                url_to_json_id[gs_url] = str(json_id)
                
                # Extract user ID from URL
                user_id = extract_user_id_from_url(gs_url)
                if user_id:
                    user_id_to_json_id[user_id] = str(json_id)
        
        # Create mapping from database ID to JSON ID
        id_mapping = {}
        
        # Try matching by Google Scholar URL
        for prof in db_professors:
            db_id = str(prof.get('id', ''))
            gs_url = prof.get('google_scholar_url', '')
            
            if gs_url and gs_url in url_to_json_id:
                json_id = url_to_json_id[gs_url]
                id_mapping[db_id] = json_id
                continue
                
            # Try extracting user ID from URL and matching
            user_id = extract_user_id_from_url(gs_url)
            if user_id and user_id in user_id_to_json_id:
                json_id = user_id_to_json_id[user_id]
                id_mapping[db_id] = json_id
                continue
            
            # As a fallback, try direct ID mapping (if JSON IDs are numeric)
            if str(db_id) in [str(t.get('id', '')) for t in json_teachers]:
                id_mapping[db_id] = db_id
        
        logger.info(f"Created ID mapping with {len(id_mapping)} entries")
        
        # Save the mapping to a file for debugging
        with open('id_mapping.json', 'w', encoding='utf-8') as f:
            json.dump(id_mapping, f, indent=2)
            
        return id_mapping
        
    except Exception as e:
        logger.error(f"Error creating ID mapping: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return {}

def check_citation_cache():
    """Check if the citation cache file exists and its contents"""
    print(f"Checking for citation cache file: {CACHE_FILE}")
    
    if os.path.exists(CACHE_FILE):
        print(f"✅ Cache file exists!")
        try:
            with open(CACHE_FILE, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
                
            print(f"Cache entries: {len(cache_data)}")
            print("\nSample entries:")
            for key, value in list(cache_data.items())[:5]:
                print(f"Key: {key}, Data: {value}")
                
            # Check if any entries have citation data
            entries_with_citations = [k for k, v in cache_data.items() 
                                      if v.get('citations', 0) > 0]
            print(f"\nEntries with citation data: {len(entries_with_citations)}")
            
            return cache_data
        except Exception as e:
            print(f"❌ Error reading cache file: {str(e)}")
            return None
    else:
        print(f"❌ Cache file does not exist!")
        # Print current directory
        print(f"Current directory: {os.getcwd()}")
        print(f"Files in current directory: {os.listdir('.')}")
        return None

def test_updated_id_mapping():
    """Test the updated ID mapping functionality"""
    try:
        print("Updating ID mapping...")
        id_mapping = update_id_mapping()
        
        print(f"Got updated ID mapping with {len(id_mapping)} entries")
        
        # Print sample entries
        for i, (db_id, json_id) in enumerate(list(id_mapping.items())[:5]):
            print(f"DB ID {db_id} -> JSON ID {json_id}")
            
        # Try to get a professor with a specific ID
        from database import get_professor_by_id
        
        # Test with a specific ID
        test_id = 1
        print(f"\nGetting professor with ID {test_id}...")
        professor = get_professor_by_id(test_id)
        
        if professor:
            print(f"Professor name: {professor.get('name', 'Unknown')}")
            print(f"Professor Google Scholar URL: {professor.get('google_scholar_url', 'N/A')}")
            
            # Try to get citation data
            json_id = id_mapping.get(str(test_id))
            
            # Get the citation cache
            cache_data = check_citation_cache()
            
            if cache_data and json_id and json_id in cache_data:
                print(f"Citations count: {cache_data[json_id].get('citations', 'N/A')}")
                print(f"h-index: {cache_data[json_id].get('h_index', 'N/A')}")
                print(f"i10-index: {cache_data[json_id].get('i10_index', 'N/A')}")
            else:
                print("Citations count: N/A")
                print("h-index: N/A")
                print("i10-index: N/A")
                
                if not json_id:
                    print(f"❌ No JSON ID mapping for DB ID {test_id}")
                elif not cache_data:
                    print("❌ No cache data available")
                else:
                    print(f"❌ JSON ID {json_id} not in cache")
        else:
            print(f"❌ Professor with ID {test_id} not found")
        
    except Exception as e:
        print(f"❌ Error testing ID mapping: {str(e)}")
        import traceback
        print(traceback.format_exc())

if __name__ == "__main__":
    cache_data = check_citation_cache()
    print("\n" + "="*50 + "\n")
    test_updated_id_mapping()
    
    # Print JSON file check
    print("\n" + "="*50 + "\n")
    print(f"Checking for JSON file: {JSON_FILE}")
    if os.path.exists(JSON_FILE):
        print(f"✅ JSON file exists!")
        json_teachers = load_json_teachers()
        print(f"JSON teachers: {len(json_teachers)}")
        
        # Print a sample of teacher IDs
        print("\nSample teacher IDs from JSON:")
        for i, teacher in enumerate(json_teachers[:5]):
            print(f"Teacher {i+1}: ID={teacher.get('id')}, Name={teacher.get('name')}")
    else:
        print(f"❌ JSON file does not exist!")