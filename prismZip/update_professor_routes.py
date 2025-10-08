import os
import json
import sys

# Constants
DEBUG_MAPPING_FILE = 'debug_id_mapping.json'

# Get the absolute path to the directory containing this script
script_dir = os.path.dirname(os.path.abspath(__file__))
# Get the absolute path to the debug_id_mapping.json file
debug_mapping_file = os.path.join(script_dir, DEBUG_MAPPING_FILE)

# Check if the debug mapping file exists and use it to update the professor_routes.py file
if os.path.exists(debug_mapping_file):
    print(f"Loading debug mapping from {debug_mapping_file}")
    with open(debug_mapping_file, 'r', encoding='utf-8') as f:
        debug_mapping = json.load(f)
    print(f"Loaded mapping with {len(debug_mapping)} entries")
    
    # Create a formatted string representation of the mapping
    formatted_mapping = "{\n"
    for db_id, json_id in debug_mapping.items():
        formatted_mapping += f"        \"{db_id}\": \"{json_id}\",\n"
    formatted_mapping = formatted_mapping.rstrip(",\n") + "\n    }"
    
    # Read the professor_routes.py file
    professor_routes_file = os.path.join(script_dir, 'professor_routes.py')
    with open(professor_routes_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find the get_id_mapping function and modify it to use the debug mapping
    import re
    pattern = r'def get_id_mapping\(\):\s+""".*?"""\s+global _id_mapping_cache.*?return _id_mapping_cache'
    replacement = f'''def get_id_mapping():
    """
    Create a mapping between database professor IDs and JSON teacher IDs using Google Scholar URLs
    This is now a fixed mapping based on URL matching.
    """
    global _id_mapping_cache
    
    # Return from cache if already created
    if _id_mapping_cache:
        return _id_mapping_cache
    
    # Use a fixed mapping based on URL matching
    _id_mapping_cache = {formatted_mapping}
    
    logging.info(f"Using fixed ID mapping with {{len(_id_mapping_cache)}} entries")
    return _id_mapping_cache'''
    
    # Replace the function in the content
    new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    
    # Write the updated content back to the file
    with open(professor_routes_file, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"Updated {professor_routes_file} with fixed ID mapping")
    print(f"Fixed mapping has {len(debug_mapping)} entries")
else:
    print(f"❌ Debug mapping file {debug_mapping_file} not found")
    print("Please run debug_id_mapping.py first to generate the mapping")