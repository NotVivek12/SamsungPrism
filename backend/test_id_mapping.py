"""
Test ID mapping between database and JSON
"""
import requests
import json
import logging
from pprint import pprint

# Set up logging to console
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def test_id_mapping():
    """Test the ID mapping between database and JSON"""
    
    base_url = "http://localhost:5000"
    
    # First, get an ID mapping test endpoint response
    print("Getting ID mapping...")
    response = requests.get(f"{base_url}/api/citations/id-mapping")
    
    if response.status_code == 200:
        mapping = response.json()
        print(f"Got ID mapping with {len(mapping.get('mappings', {}))} entries")
        
        # Get the first 5 mappings
        for db_id, json_id in list(mapping.get('mappings', {}).items())[:5]:
            print(f"DB ID {db_id} -> JSON ID {json_id}")
        
        # Get a professor by ID
        if mapping.get('mappings'):
            db_id = list(mapping.get('mappings', {}))[0]
            print(f"\nGetting professor with ID {db_id}...")
            response = requests.get(f"{base_url}/api/professors/{db_id}")
            
            if response.status_code == 200:
                prof = response.json()
                print(f"Professor name: {prof.get('name', 'Unknown')}")
                print(f"Professor Google Scholar URL: {prof.get('google_scholar_url', 'None')}")
                print(f"Citations count: {prof.get('citations_count', 'N/A')}")
                print(f"h-index: {prof.get('h_index', 'N/A')}")
                print(f"i10-index: {prof.get('i10_index', 'N/A')}")
            else:
                print(f"Error getting professor: {response.status_code}")
                print(response.text)
        
    else:
        print(f"Error getting ID mapping: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    test_id_mapping()