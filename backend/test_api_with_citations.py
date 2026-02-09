import requests
import json
import sys

def test_api_with_citations():
    """Test API to get professors with citation data"""
    try:
        # Make request to API
        print("Making API request for professors with citations...")
        response = requests.get("http://localhost:5000/api/professors", params={
            "include_citations": "true",
            "limit": 10
        })
        
        # Check response
        if response.status_code != 200:
            print(f"❌ API request failed with status {response.status_code}")
            print(response.text)
            return
        
        # Parse response
        data = response.json()
        
        # Print summary
        total = data.get("total_count", 0)
        filtered = data.get("filtered_count", 0)
        professors = data.get("professors", [])
        
        print(f"✅ API request successful!")
        print(f"Total professors: {total}")
        print(f"Filtered professors: {filtered}")
        print(f"Professors returned: {len(professors)}")
        
        # Check if any professors have citation data
        professors_with_citations = [
            p for p in professors 
            if any(p.get(field) not in (None, 0, "") 
                  for field in ["citations_count", "h_index", "i10_index"])
        ]
        
        print(f"\nProfessors with citation data: {len(professors_with_citations)}/{len(professors)}")
        
        # Print professor details
        print("\nProfessor details:")
        for i, prof in enumerate(professors[:5], 1):
            print(f"Professor {i}: {prof.get('name')}")
            print(f"  ID: {prof.get('id')}")
            print(f"  Google Scholar URL: {prof.get('google_scholar_url')}")
            print(f"  JSON ID: {prof.get('json_id', 'N/A')}")
            print(f"  Citations: {prof.get('citations_count', 'N/A')}")
            print(f"  h-index: {prof.get('h_index', 'N/A')}")
            print(f"  i10-index: {prof.get('i10_index', 'N/A')}")
            print()
        
        # Test specific professor endpoint
        if professors:
            test_id = professors[0].get('id')
            print(f"\nTesting specific professor endpoint for ID {test_id}")
            
            response = requests.get(f"http://localhost:5000/api/professors/{test_id}")
            
            if response.status_code != 200:
                print(f"❌ Professor details request failed with status {response.status_code}")
                print(response.text)
                return
            
            prof = response.json()
            print(f"✅ Professor details request successful!")
            print(f"Professor: {prof.get('name')}")
            print(f"  ID: {prof.get('id')}")
            print(f"  Google Scholar URL: {prof.get('google_scholar_url')}")
            print(f"  JSON ID: {prof.get('json_id', 'N/A')}")
            print(f"  Citations: {prof.get('citations_count', 'N/A')}")
            print(f"  h-index: {prof.get('h_index', 'N/A')}")
            print(f"  i10-index: {prof.get('i10_index', 'N/A')}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection error: Could not connect to API. Make sure the server is running.")
    except Exception as e:
        print(f"❌ Error testing API: {str(e)}")
        import traceback
        print(traceback.format_exc())

if __name__ == "__main__":
    test_api_with_citations()