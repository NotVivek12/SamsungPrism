import os
import json
import logging
from extract_citations import load_teachers_data, get_cached_citations

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('citation_debug')

def debug_id_mapping():
    """Debug the ID mapping between database and JSON IDs"""
    try:
        # Get JSON teachers
        json_teachers = load_teachers_data()
        
        # Get citation cache
        citation_cache = get_cached_citations()
        
        # Get database professors
        import database
        db_professors = database.load_professors_data()
        
        print(f"JSON teachers: {len(json_teachers)}")
        print(f"Citation cache entries: {len(citation_cache)}")
        print(f"Database professors: {len(db_professors)}")
        
        # Check how many JSON IDs are in the citation cache
        json_ids = [str(t.get('id', '')) for t in json_teachers]
        json_ids_in_cache = [id for id in json_ids if id in citation_cache]
        print(f"JSON IDs in citation cache: {len(json_ids_in_cache)}/{len(json_ids)}")
        
        # Create mapping between database professors and JSON teachers
        matches = []
        
        # Try matching by URL
        for db_prof in db_professors:
            db_id = str(db_prof.get('id', ''))
            db_url = db_prof.get('google_scholar_url', '').strip()
            
            if not db_url:
                continue
                
            # Extract user ID from URL
            import re
            user_id_match = re.search(r'user=([^&]+)', db_url)
            db_user_id = user_id_match.group(1) if user_id_match else None
            
            # Try to find matching JSON teacher
            for json_teacher in json_teachers:
                json_id = str(json_teacher.get('id', ''))
                json_url = json_teacher.get('google_scholar_url', '').strip()
                
                if not json_url:
                    continue
                    
                # Extract user ID from URL
                user_id_match = re.search(r'user=([^&]+)', json_url)
                json_user_id = user_id_match.group(1) if user_id_match else None
                
                # Check if URLs match
                if db_url == json_url or (db_user_id and json_user_id and db_user_id == json_user_id):
                    matches.append({
                        'db_id': db_id,
                        'json_id': json_id,
                        'db_url': db_url,
                        'json_url': json_url,
                        'db_user_id': db_user_id,
                        'json_user_id': json_user_id,
                        'in_cache': json_id in citation_cache
                    })
                    break
        
        print(f"Found {len(matches)} matches between database and JSON")
        
        # Print some sample matches
        print("\nSample matches:")
        for i, match in enumerate(matches[:5]):
            print(f"Match {i+1}:")
            print(f"  DB ID: {match['db_id']}")
            print(f"  JSON ID: {match['json_id']}")
            print(f"  DB URL: {match['db_url']}")
            print(f"  JSON URL: {match['json_url']}")
            print(f"  In cache: {match['in_cache']}")
            if match['in_cache']:
                citation_data = citation_cache[match['json_id']]
                print(f"  Citations: {citation_data.get('citations', 'N/A')}")
                print(f"  h-index: {citation_data.get('h_index', 'N/A')}")
                print(f"  i10-index: {citation_data.get('i10_index', 'N/A')}")
        
        # Create a debug mapping file
        debug_mapping = {}
        for match in matches:
            debug_mapping[match['db_id']] = match['json_id']
            
        with open('debug_id_mapping.json', 'w', encoding='utf-8') as f:
            json.dump(debug_mapping, f, indent=2)
            
        print(f"\nCreated debug mapping with {len(debug_mapping)} entries")
        print("Saved to debug_id_mapping.json")
        
        # Debug professor_routes.py get_id_mapping function
        print("\nTesting professor_routes.get_id_mapping function:")
        try:
            import sys
            sys.path.insert(0, '.')
            from professor_routes import get_id_mapping
            
            mapping = get_id_mapping()
            print(f"get_id_mapping returned {len(mapping)} entries")
            
            # Check if our debug mapping is similar
            common_keys = set(debug_mapping.keys()) & set(mapping.keys())
            common_matches = sum(1 for k in common_keys if debug_mapping[k] == mapping[k])
            
            print(f"Common keys: {len(common_keys)}")
            print(f"Common matches: {common_matches}")
            
            # Print a few entries from both mappings
            print("\nSample comparison:")
            for db_id in list(debug_mapping.keys())[:5]:
                debug_json_id = debug_mapping.get(db_id)
                mapping_json_id = mapping.get(db_id)
                print(f"DB ID {db_id}: Debug: {debug_json_id}, Mapping: {mapping_json_id}, Match: {debug_json_id == mapping_json_id}")
        except Exception as e:
            print(f"Error testing get_id_mapping: {str(e)}")
            import traceback
            print(traceback.format_exc())
        
    except Exception as e:
        logger.error(f"Error in debug_id_mapping: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())

if __name__ == "__main__":
    debug_id_mapping()