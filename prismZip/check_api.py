import requests
import sys

# URL to test
url = "http://localhost:5000/api/teachers?limit=1"

try:
    # Make the request
    response = requests.get(url)
    
    # Print the response status code
    print(f"Status code: {response.status_code}")
    
    # Print the response body
    if response.status_code == 200:
        print(response.text[:200] + "...")  # Print first 200 characters
        data = response.json()
        teachers = data.get("teachers", [])
        print(f"Got {len(teachers)} teachers")
    else:
        print(f"Error: {response.text}")
        
    sys.exit(0)
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)