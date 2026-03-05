import pandas as pd
import os

def test_excel_reading():
    """Test reading Excel data from prof.xlsx"""
    try:
        # Find Excel file
        excel_path = os.path.join(os.getcwd(), 'prof.xlsx')
        if not os.path.exists(excel_path):
            excel_path = os.path.join(os.path.dirname(os.getcwd()), 'prof.xlsx')
            
        print(f"Looking for Excel file at: {excel_path}")
        
        if not os.path.exists(excel_path):
            print(f"Excel file not found at: {excel_path}")
            return
            
        # Read Excel file
        print("Reading Excel file...")
        df = pd.read_excel(excel_path)
        
        # Print DataFrame info
        print(f"DataFrame shape: {df.shape}")
        print(f"DataFrame columns: {df.columns.tolist()}")
        
        # Print first 5 rows
        print("\nFirst 5 rows:")
        print(df.head())
        
        # Convert to list of dictionaries
        teachers = []
        for i, row in df.iterrows():
            if i >= 5:  # Only process first 5 rows
                break
                
            teacher = {
                'id': i + 1,
                'name': str(row.get('Name', '')),
                'college': str(row.get('College', '')),
                'email': str(row.get('Email', '')),
                'domain_expertise': str(row.get('Domain Expertise', '')),
            }
            teachers.append(teacher)
            
        # Print teachers
        print("\nTeachers:")
        for teacher in teachers:
            print(teacher)
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_excel_reading()