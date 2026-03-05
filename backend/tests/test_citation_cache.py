import os
import json
import sys

# Constants
CACHE_FILE = 'teacher_citations_cache.json'

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

def test_id_mapping():
    """Test the ID mapping functionality"""
    try:
        # Import from professor_routes
        sys.path.insert(0, '.')
        from professor_routes import get_id_mapping
        
        print("Getting ID mapping...")
        id_mapping = get_id_mapping()
        
        print(f"Got ID mapping with {len(id_mapping)} entries")
        
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
    check_citation_cache()
    print("\n" + "="*50 + "\n")
    test_id_mapping()