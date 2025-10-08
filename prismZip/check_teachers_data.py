"""
Check if teachers data contains Google Scholar URLs
"""
import json

def check_teachers_data():
    try:
        with open('teachers_data.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"Total teachers: {len(data)}")
        
        scholars = [t for t in data if t.get('google_scholar_url')]
        print(f"Teachers with Scholar URLs: {len(scholars)}")
        
        if scholars:
            print("\nSample Scholar URLs:")
            for teacher in scholars[:3]:
                print(f"- {teacher.get('name', 'Unknown')}: {teacher.get('google_scholar_url')}")
        else:
            print("\nNo teachers have Google Scholar URLs!")
            
    except Exception as e:
        print(f"Error loading data: {str(e)}")

if __name__ == "__main__":
    check_teachers_data()