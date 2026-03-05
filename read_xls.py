import pandas as pd
import json
import sys

try:
    df = pd.read_excel('D:\\Professor Profile\\SamsungPrism\\SAMPLE Faculty Data.xlsx')
    columns = df.columns.tolist()
    sample_data = df.head(3).to_dict(orient='records')
    result = {
        'columns': columns,
        'sample_data': sample_data
    }
    print(json.dumps(result, indent=2))
except Exception as e:
    print(json.dumps({'error': str(e)}))
