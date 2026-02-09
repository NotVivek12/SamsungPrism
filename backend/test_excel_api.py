import requests
import json

def print_json(obj):
    """Print JSON object nicely formatted"""
    print(json.dumps(obj, indent=2))

def test_api_endpoints():
    """Test the Excel-based API endpoints"""
    base_url = "http://localhost:5000"
    
    print("Testing /api/teachers endpoint...")
    try:
        response = requests.get(f"{base_url}/api/teachers?limit=2")
        print(f"Status: {response.status_code}")
        print_json(response.json())
    except Exception as e:
        print(f"Error: {e}")
    
    print("\nTesting /api/colleges endpoint...")
    try:
        response = requests.get(f"{base_url}/api/colleges")
        print(f"Status: {response.status_code}")
        print_json(response.json())
    except Exception as e:
        print(f"Error: {e}")
    
    print("\nTesting /api/teachers/10 endpoint...")
    try:
        response = requests.get(f"{base_url}/api/teachers/10")
        print(f"Status: {response.status_code}")
        print_json(response.json())
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_api_endpoints()