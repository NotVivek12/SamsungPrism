import pandas as pd
import os
import time
import json
import requests

def test_api():
    """Test API endpoints"""
    base_url = "http://localhost:5000"
    
    # Wait a bit for the server to start
    print("Waiting for server to start...")
    time.sleep(2)
    
    endpoints = [
        "/api/teachers?limit=2",
        "/api/colleges",
        "/api/teachers/10"
    ]
    
    for endpoint in endpoints:
        url = f"{base_url}{endpoint}"
        print(f"\nTesting {url}")
        
        try:
            response = requests.get(url)
            print(f"Status code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(json.dumps(data, indent=2))
            else:
                print(f"Error response: {response.text}")
                
        except Exception as e:
            print(f"Error: {e}")
            
if __name__ == "__main__":
    test_api()