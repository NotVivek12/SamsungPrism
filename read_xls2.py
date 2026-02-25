import pandas as pd
import json

try:
    df = pd.read_excel('D:\\Professor Profile\\SamsungPrism\\SAMPLE Faculty Data.xlsx')
    # Convert all columns to string to avoid JSON serialization issues with NaN
    df = df.astype(str)
    result = {
        'columns': df.columns.tolist(),
        'sample_data': df.head(1).to_dict(orient='records')
    }
    with open('xls_output.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2)
    print("Success")
except Exception as e:
    print("Error:", str(e))
