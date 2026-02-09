import requests
import json

try:
    response = requests.get('http://localhost:5000/api/teachers')
    if response.status_code == 200:
        data = response.json()
        teachers = data.get('teachers', [])
        print(f"✅ API Returns: {len(teachers)} teachers")
        if teachers:
            sample = teachers[0]
            print(f"📊 Sample: {sample.get('name')} - {sample.get('college')}")
            print(f"🔗 Has URLs: Google={bool(sample.get('google_scholar_url'))}, Semantic={bool(sample.get('semantic_scholar_url'))}")
            print(f"📚 Has PhD: {bool(sample.get('phd_thesis'))}")
            print(f"🏛️ Has expertise: {bool(sample.get('domain_expertise'))}")
    else:
        print(f"❌ API Error: {response.status_code}")
        print(response.text)
except Exception as e:
    print(f"❌ Connection Error: {e}")