#!/usr/bin/env python3
"""
Test script to verify teachers API endpoints are working correctly
"""

import requests
import json

def test_teachers_api():
    """Test all teacher API endpoints"""
    base_url = "http://localhost:5000"
    
    print("🧪 Testing Teachers API Endpoints\n")
    
    # Test 1: Get all teachers
    print("1. Testing GET /api/teachers (All Teachers)")
    try:
        response = requests.get(f"{base_url}/api/teachers")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Success: Found {data.get('total_count', 0)} teachers")
            if data.get('teachers'):
                print(f"   📋 Sample teacher: {data['teachers'][0]['name']} - {data['teachers'][0]['college']}")
            else:
                print("   ⚠️ No teachers found in response")
        else:
            print(f"   ❌ Failed: Status {response.status_code}")
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   ❌ Connection Error: {e}")
    
    print()
    
    # Test 2: Search teachers
    print("2. Testing GET /api/teachers/search?q=computer")
    try:
        response = requests.get(f"{base_url}/api/teachers/search?q=computer")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Success: Found {data.get('total_count', 0)} teachers matching 'computer'")
        else:
            print(f"   ❌ Failed: Status {response.status_code}")
    except Exception as e:
        print(f"   ❌ Connection Error: {e}")
    
    print()
    
    # Test 3: Get teacher status
    print("3. Testing GET /api/teachers/status")
    try:
        response = requests.get(f"{base_url}/api/teachers/status")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Success: Database has {data.get('total_teachers', 0)} teachers")
            print(f"   📊 Google Scholar: {data.get('teachers_with_google_scholar', 0)} ({data.get('extraction_percentages', {}).get('google_scholar', 0)}%)")
            print(f"   📊 Semantic Scholar: {data.get('teachers_with_semantic_scholar', 0)} ({data.get('extraction_percentages', {}).get('semantic_scholar', 0)}%)")
        else:
            print(f"   ❌ Failed: Status {response.status_code}")
    except Exception as e:
        print(f"   ❌ Connection Error: {e}")
    
    print()
    
    # Test 4: Get specific teacher details
    print("4. Testing GET /api/teachers/1 (Teacher Details)")
    try:
        response = requests.get(f"{base_url}/api/teachers/1")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Success: Got details for {data.get('name', 'Unknown')}")
            if data.get('academic_data'):
                print(f"   📚 Academic data available: {len(data['academic_data'])} fields")
        else:
            print(f"   ❌ Failed: Status {response.status_code}")
    except Exception as e:
        print(f"   ❌ Connection Error: {e}")
    
    print("\n🎯 API Testing Complete!")

if __name__ == "__main__":
    test_teachers_api()