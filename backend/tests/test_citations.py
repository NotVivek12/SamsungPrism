"""
Test citation extraction and API endpoints
"""
import requests
import time
import json

def test_citations_api():
    """Test the citations API endpoints"""
    
    base_url = "http://localhost:5000"
    
    print("Testing citation extraction APIs...\n")
    
    # Test the status endpoint
    print("1. Testing GET /api/citations/status")
    try:
        response = requests.get(f"{base_url}/api/citations/status")
        print(f"Status code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Citation cache status: {data}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Error: {str(e)}")
    
    print("\n2. Testing POST /api/citations/refresh")
    try:
        response = requests.post(f"{base_url}/api/citations/refresh")
        print(f"Status code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Refresh response: {data}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Error: {str(e)}")
    
    print("\n3. Testing GET /api/professors with citations")
    try:
        response = requests.get(f"{base_url}/api/professors?limit=5&include_citations=true")
        print(f"Status code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Found {len(data['professors'])} professors")
            print("Sample professor data:")
            for prof in data['professors'][:2]:  # Display first 2 professors
                print(f"  - {prof.get('name', 'Unknown')}")
                print(f"    Citations: {prof.get('citations_count', 'N/A')}")
                print(f"    h-index: {prof.get('h_index', 'N/A')}")
                print(f"    i10-index: {prof.get('i10_index', 'N/A')}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Error: {str(e)}")
    
    print("\n4. Checking citation extraction progress (will check status 5 times)...")
    for i in range(5):
        try:
            response = requests.get(f"{base_url}/api/citations/status")
            if response.status_code == 200:
                data = response.json()
                running = data.get('extraction_running', False)
                total = data.get('total_professors', 0)
                with_citations = data.get('professors_with_citations', 0)
                print(f"  Check {i+1}: Running={running}, Professors with citations: {with_citations}/{total}")
            else:
                print(f"  Check {i+1}: Error - {response.text}")
        except Exception as e:
            print(f"  Check {i+1}: Error - {str(e)}")
        
        # Wait 5 seconds between checks
        if i < 4:  # Don't wait after the last check
            print("  Waiting 5 seconds...")
            time.sleep(5)

if __name__ == "__main__":
    test_citations_api()