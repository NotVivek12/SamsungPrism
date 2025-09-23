import pytest
from helpers import extract_scholar_data
import requests
from unittest.mock import patch, Mock

def test_extract_scholar_data_valid_url():
    valid_url = "https://scholar.google.com/citations?user=8xJ-K2oAAAAJ"
    teacher_name = "Test Professor"
    fake_html = """
        <div id="gsc_prf_i">
            <div class="gsc_prf_il">Some University</div>
            <a class="gsc_prf_ila">AI</a>
            <a class="gsc_prf_ila">NLP</a>
        </div>
        <table id="gsc_rsb_st">
            <tr><td>Citations</td><td>123</td></tr>
            <tr><td>h-index</td><td>10</td></tr>
            <tr><td>i10-index</td><td>5</td></tr>
        </table>
        <table id="gsc_a_t">
            <tr>
                <td class="gsc_a_t"><a class="gsc_a_at">Paper A</a></td>
                <td class="gsc_a_y">2020</td>
            </tr>
            <tr>
                <td class="gsc_a_t"><a class="gsc_a_at">Paper B</a></td>
                <td class="gsc_a_y">2021</td>
            </tr>
        </table>
    """
    fake_response = Mock(status_code=200, text=fake_html)
    fake_response.raise_for_status = Mock()
    with patch('helpers.session.get', return_value=fake_response):
        data = extract_scholar_data(teacher_name, valid_url)
    assert isinstance(data, dict)
    assert 'Google Scholar Data' in data
    gsd = data['Google Scholar Data']
    assert gsd['Citations'] == 123
    assert gsd['h-index'] == 10
    assert gsd['i10-index'] == 5
    assert isinstance(gsd.get('Publications', []), list)

def test_extract_scholar_data_invalid_url():
    invalid_url = "https://scholar.google.com/citations?user=invalid_user_id"
    teacher_name = "Test Professor"
    fake_response = Mock(status_code=404, text="Not Found")
    def raise_http_error():
        from requests import HTTPError
        raise HTTPError("404")
    fake_response.raise_for_status = raise_http_error
    with patch('helpers.session.get', return_value=fake_response):
        with pytest.raises(Exception):
            extract_scholar_data(teacher_name, invalid_url)

def test_extract_scholar_data_network_error():
    # Patch the session used in helpers
    with patch('helpers.session.get') as mock_get:
        mock_get.side_effect = requests.exceptions.ConnectionError
        with pytest.raises(requests.exceptions.ConnectionError):
            extract_scholar_data("Test Teacher", "http://example.com")

def test_extract_scholar_data_empty_profile():
    empty_profile_url = "https://scholar.google.com/citations?user=j9E0tVMAAAAJ&hl=en&oi=sra"
    teacher_name = "Empty Profile Teacher"
    # Empty profile returns zeros and empty lists
    fake_html = """
        <div id="gsc_prf_i"></div>
        <table id="gsc_rsb_st"></table>
        <table id="gsc_a_t"></table>
    """
    fake_response = Mock(status_code=200, text=fake_html)
    fake_response.raise_for_status = Mock()
    with patch('helpers.session.get', return_value=fake_response):
        data = extract_scholar_data(teacher_name, empty_profile_url)
    assert isinstance(data, dict)
    assert 'Google Scholar Data' in data
    gsd = data['Google Scholar Data']
    assert isinstance(gsd.get('Citations', 0), int)
    assert isinstance(gsd.get('h-index', 0), int)
    assert isinstance(gsd.get('i10-index', 0), int)
    assert isinstance(gsd.get('Publications', []), list)
