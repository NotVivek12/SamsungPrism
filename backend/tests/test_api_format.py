import requests
import json

def test_api_response_format():
    """Test the API response format to confirm citation data is included"""
    try:
        # Make request to API
        print("Making API request for professors with citations...")
        response = requests.get("http://localhost:5000/api/professors", params={
            "include_citations": "true",
            "limit": 5
        })
        
        if response.status_code != 200:
            print(f"❌ API request failed with status {response.status_code}")
            print(response.text)
            return
        
        # Parse response and save to file for inspection
        data = response.json()
        
        # Save the response to a file for inspection
        with open("api_response_sample.json", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            
        print(f"✅ API response saved to api_response_sample.json")
        
        # Check if professors have citation data
        professors = data.get("professors", [])
        professors_with_citations = [
            p for p in professors 
            if any(p.get(field) not in (None, 0, "") for field in ["citations_count", "h_index", "i10_index"])
        ]
        
        print(f"Professors with citation data: {len(professors_with_citations)}/{len(professors)}")
        
        if professors_with_citations:
            print("\nSample professor with citations:")
            prof = professors_with_citations[0]
            print(f"Name: {prof.get('name')}")
            print(f"Citations: {prof.get('citations_count')}")
            print(f"h-index: {prof.get('h_index')}")
            print(f"i10-index: {prof.get('i10_index')}")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        print(traceback.format_exc())

if __name__ == "__main__":
    test_api_response_format()