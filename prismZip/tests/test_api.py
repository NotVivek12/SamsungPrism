import pytest
import json
from flask import Flask
from app import app
import os

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_extract_endpoint_valid_file(client):
   
    import pandas as pd
    data = {
        'Teacher Name': ['Test Teacher'],
        'College': ['X College'],
        'College Email Id': ['test@example.com'],
        'College Profile Link(please mention your profile link)': ['http://example.com/profile'],
        'Domain Expertise': ['AI'],
        'Ph D Thesis': ['Thesis Title'],
        'Google Scholar URL': ['https://scholar.google.com/citations?user=some_user_id'],
        'Semantic Scholar Link': ['http://example.com/semantics']
    }
    df = pd.DataFrame(data)
    df.to_excel('test_teachers.xlsx', index=False)

    with open('test_teachers.xlsx', 'rb') as f:
        response = client.post('/extract', data={'file': (f, 'test_teachers.xlsx')})

    os.remove('test_teachers.xlsx')  

    assert response.status_code == 200
    data = json.loads(response.get_data(as_text=True))
    assert isinstance(data, list)
    assert len(data) == 1
    assert 'Teacher Name' in data[0]
    assert 'Google Scholar Data' in data[0]
    gsd = data[0]['Google Scholar Data']
    assert 'Citations' in gsd
    assert 'h-index' in gsd
    assert 'i10-index' in gsd
    assert 'Publications' in gsd

def test_extract_endpoint_no_file(client):
    response = client.post('/extract', data={})
    assert response.status_code == 400
    data = json.loads(response.get_data(as_text=True))
    assert 'error' in data

def test_extract_endpoint_invalid_file_type(client):
    import io
    fake_file = io.BytesIO(b"not an excel file")
    response = client.post('/extract', data={'file': (fake_file, 'test.txt')})
    assert response.status_code == 400
    data = json.loads(response.get_data(as_text=True))
    assert 'error' in data

def test_extract_endpoint_missing_columns(client):
    import pandas as pd
    data = {'Name': ['Test Teacher'], 'URL': ['https://scholar.google.com/citations?user=some_user_id']}
    df = pd.DataFrame(data)
    df.to_excel('test_teachers.xlsx', index=False)

    with open('test_teachers.xlsx', 'rb') as f:
        response = client.post('/extract', data={'file': (f, 'test_teachers.xlsx')})

    os.remove('test_teachers.xlsx') 

    assert response.status_code == 400
    data = json.loads(response.get_data(as_text=True))
    assert 'error' in data
