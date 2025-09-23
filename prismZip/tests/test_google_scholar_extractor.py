import pytest
import os
import sys
import logging
from unittest.mock import patch, MagicMock

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the modules to test
from google_scholar_extractor import extract_google_scholar_data, extract_metrics_from_table, extract_metrics_from_boxes

# Setup logging
logging.basicConfig(level=logging.INFO)

class TestGoogleScholarExtractor:
    
    @pytest.fixture
    def mock_response(self):
        """Create a mock response with sample Google Scholar HTML"""
        mock_resp = MagicMock()
        # Read sample HTML from file if exists, otherwise use minimal sample
        sample_file = os.path.join(os.path.dirname(__file__), 'sample_google_scholar.html')
        if os.path.exists(sample_file):
            with open(sample_file, 'r', encoding='utf-8') as f:
                mock_resp.text = f.read()
        else:
            mock_resp.text = """
            <!DOCTYPE html>
            <html>
            <head><title>John Doe - Google Scholar</title></head>
            <body>
                <div id="gsc_prf_in">John Doe</div>
                <div class="gsc_prf_il">University of Example</div>
                <div id="gsc_prf_int">
                    <a class="gsc_prf_inta">Computer Science</a>
                    <a class="gsc_prf_inta">Artificial Intelligence</a>
                </div>
                <table id="gsc_rsb_st">
                    <tr><th>All</th><th>Since 2019</th></tr>
                    <tr><td>Citations</td><td>1234</td><td>567</td></tr>
                    <tr><td>h-index</td><td>20</td><td>15</td></tr>
                    <tr><td>i10-index</td><td>30</td><td>25</td></tr>
                </table>
                <div class="gsc_rsb_std">1234</div>
                <div class="gsc_rsb_std">20</div>
                <div class="gsc_rsb_std">30</div>
                <tr class="gsc_a_tr">
                    <td class="gsc_a_t"><a class="gsc_a_at">Sample Paper Title</a></td>
                    <td class="gsc_a_y">2022</td>
                </tr>
            </body>
            </html>
            """
        mock_resp.raise_for_status = MagicMock()
        return mock_resp
    
    @patch('google_scholar_extractor.session.get')
    def test_extract_google_scholar_data(self, mock_get, mock_response):
        """Test the main extraction function"""
        # Setup mock
        mock_get.return_value = mock_response
        
        # Execute function
        result = extract_google_scholar_data('https://scholar.google.com/citations?user=abc123')
        
        # Assertions
        assert 'Google Scholar Data' in result
        data = result['Google Scholar Data']
        assert data['Name'] == 'John Doe'
        assert data['Citations'] == 1234
        assert data['h-index'] == 20
        assert data['i10-index'] == 30
        assert data['Current Affiliation'] == 'University of Example'
        assert len(data['Research Interests']) == 2
        assert 'Computer Science' in data['Research Interests']
        assert len(data['Publications']) > 0
        
    def test_extract_metrics_from_table(self, mock_response):
        """Test extracting metrics from citation table"""
        from bs4 import BeautifulSoup
        
        # Parse HTML
        soup = BeautifulSoup(mock_response.text, 'html.parser')
        
        # Execute function
        metrics = extract_metrics_from_table(soup, mock_response.text)
        
        # Assertions
        assert metrics['citations'] == 1234
        assert metrics['h_index'] == 20
        assert metrics['i10_index'] == 30
        
    def test_extract_metrics_from_boxes(self, mock_response):
        """Test extracting metrics from summary boxes"""
        from bs4 import BeautifulSoup
        
        # Parse HTML
        soup = BeautifulSoup(mock_response.text, 'html.parser')
        
        # Execute function
        metrics = extract_metrics_from_boxes(soup, mock_response.text)
        
        # Assertions
        assert metrics['citations'] == 1234
        assert metrics['h_index'] == 20
        assert metrics['i10_index'] == 30

if __name__ == "__main__":
    # Run tests with pytest if file is executed directly
    pytest.main(['-v', __file__])