import os

# Run Flask app in development mode and redirect output
os.system("python app.py > server_log.txt 2>&1 &")
print("Flask server started in background. Check server_log.txt for output.")

# Give the server time to start
import time
time.sleep(5)

# Now try to access the API
import requests

print("\nTesting API endpoints...")

try:
    # Test teachers endpoint
    response = requests.get("http://localhost:5000/api/teachers?limit=2")
    print(f"/api/teachers status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        teachers = data.get('teachers', [])
        print(f"Got {len(teachers)} teachers")
        
        if teachers:
            print(f"First teacher: {teachers[0]['name']}, {teachers[0]['college']}")
    
    # Test colleges endpoint
    response = requests.get("http://localhost:5000/api/colleges")
    print(f"/api/colleges status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        colleges = data.get('colleges', [])
        print(f"Got {len(colleges)} colleges")
        
        if colleges:
            print(f"First college: {colleges[0]['name']}, Count: {colleges[0]['count']}")
    
    # Test individual teacher endpoint
    response = requests.get("http://localhost:5000/api/teachers/10")
    print(f"/api/teachers/10 status: {response.status_code}")
    
    if response.status_code == 200:
        teacher = response.json()
        print(f"Teacher 10: {teacher.get('name')}, {teacher.get('college')}")
        
except Exception as e:
    print(f"Error testing API: {e}")

print("\nFinished testing API endpoints.")