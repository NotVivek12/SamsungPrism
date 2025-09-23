import requests
import logging
import re
import math
import time
from bs4 import BeautifulSoup
from utils import handle_exceptions
from typing import Dict, List, Any, Tuple

# Configure session with retries
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Set up a session with retry capability
session = requests.Session()
retry_strategy = Retry(
    total=3,
    backoff_factor=1,
    status_forcelist=[429, 500, 502, 503, 504],
)
adapter = HTTPAdapter(max_retries=retry_strategy)
session.mount("https://", adapter)
session.mount("http://", adapter)

# Headers to mimic a browser
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Referer': 'https://scholar.google.com/',
    'Connection': 'keep-alive',
}

def clean_text(text: str) -> str:
    """Clean text by removing extra whitespace and newlines."""
    return re.sub(r'\s+', ' ', text).strip()

@handle_exceptions
def extract_google_scholar_data(url: str) -> Dict[str, Any]:
    """
    Enhanced extraction of Google Scholar profile data with multiple methods and fallbacks.
    
    Args:
        url (str): URL of the Google Scholar profile
        
    Returns:
        dict: Dictionary with extracted data and debug information
    """
    logging.info(f"Extracting data from Google Scholar URL: {url}")
    
    try:
        # Make request with enhanced headers and longer timeout
        response = session.get(url, headers=HEADERS, timeout=30)
        response.raise_for_status()
        
        logging.info(f"Successfully fetched Google Scholar page ({len(response.text)} bytes)")
        
        # Parse with BeautifulSoup for structured extraction
        soup = BeautifulSoup(response.text, 'html.parser')
        html = response.text
        
        # Extract basic profile information
        name = extract_name(soup, html)
        affiliation = extract_affiliation(soup, html)
        interests = extract_research_interests(soup, html)
        
        # Extract citation metrics using multiple methods
        metrics = extract_all_metrics(soup, html)
        
        # Extract publications
        publications = extract_publications(soup, html)
        
        # Create result dictionary
        result = {
            'Google Scholar Data': {
                'Name': name,
                'Citations': metrics['citations'],
                'h-index': metrics['h_index'],
                'i10-index': metrics['i10_index'],
                'Total Publications': len(publications),
                'Research Interests': interests,
                'Current Affiliation': affiliation,
                'Publications': publications[:10],  # Limit to 10 publications
                '_debug_info': {
                    'extraction_method': metrics['method'],
                    'url': url,
                    'html_length': len(html)
                }
            }
        }
        
        logging.info(f"Successfully extracted Google Scholar data: citations={metrics['citations']}, h-index={metrics['h_index']}")
        return result
        
    except requests.exceptions.Timeout:
        logging.error(f"Timeout when fetching Google Scholar profile: {url}")
        raise TimeoutError(f"Request to Google Scholar timed out: {url}")
        
    except requests.exceptions.RequestException as e:
        logging.error(f"Request error when fetching Google Scholar profile: {url}, {str(e)}")
        raise ConnectionError(f"Error connecting to Google Scholar: {str(e)}")
        
    except Exception as e:
        logging.error(f"Error extracting data from Google Scholar: {url}, {str(e)}")
        raise

def extract_name(soup: BeautifulSoup, html: str) -> str:
    """Extract scholar name using multiple methods."""
    # Method 1: Using BeautifulSoup selector
    name_element = soup.select_one('#gsc_prf_in')
    if name_element:
        return clean_text(name_element.text)
    
    # Method 2: Using regex for profile name
    name_match = re.search(r'<div id="gsc_prf_in">(.*?)</div>', html, re.DOTALL)
    if name_match:
        return clean_text(name_match.group(1))
    
    # Method 3: Look for name in title
    title_element = soup.find('title')
    if title_element:
        title_text = title_element.text
        # Google Scholar titles are typically formatted as "Name - Google Scholar"
        if " - Google Scholar" in title_text:
            return clean_text(title_text.split(" - Google Scholar")[0])
    
    return "Unknown"

def extract_affiliation(soup: BeautifulSoup, html: str) -> str:
    """Extract affiliation using multiple methods."""
    # Method 1: Using BeautifulSoup selector
    affiliation_element = soup.select_one('.gsc_prf_il')
    if affiliation_element:
        return clean_text(affiliation_element.text)
    
    # Method 2: Using regex
    affiliation_match = re.search(r'<div class="gsc_prf_il">(.*?)</div>', html, re.DOTALL)
    if affiliation_match:
        return clean_text(affiliation_match.group(1))
    
    return "Not available"

def extract_research_interests(soup: BeautifulSoup, html: str) -> List[str]:
    """Extract research interests using multiple methods."""
    interests = []
    
    # Method 1: Using BeautifulSoup selector
    interest_elements = soup.select('#gsc_prf_int .gsc_prf_inta')
    if interest_elements:
        for element in interest_elements:
            interests.append(clean_text(element.text))
    
    # Method 2: Using regex if Method 1 failed
    if not interests:
        interest_matches = re.findall(r'<a class="gsc_prf_inta"[^>]*>(.*?)</a>', html, re.DOTALL)
        interests = [clean_text(match) for match in interest_matches]
    
    return interests

def extract_all_metrics(soup: BeautifulSoup, html: str) -> Dict[str, Any]:
    """
    Extract citation metrics using multiple methods with fallbacks.
    Returns the most reliable metrics and the method used.
    """
    # Initialize with defaults
    result = {
        'citations': 0, 
        'h_index': 0, 
        'i10_index': 0,
        'method': 'none'
    }
    
    # Method 1: Extract from citation table (most reliable)
    table_metrics = extract_metrics_from_table(soup, html)
    if any(table_metrics.values()):
        result.update(table_metrics)
        result['method'] = 'table'
        logging.info("Successfully extracted metrics from citation table")
        return result
    
    # Method 2: Extract from summary boxes
    box_metrics = extract_metrics_from_boxes(soup, html)
    if any(box_metrics.values()):
        result.update(box_metrics)
        result['method'] = 'boxes'
        logging.info("Successfully extracted metrics from summary boxes")
        return result
    
    # Method 3: Extract from text mentions
    text_metrics = extract_metrics_from_text(soup, html)
    if any(text_metrics.values()):
        result.update(text_metrics)
        result['method'] = 'text'
        logging.info("Successfully extracted metrics from text mentions")
        return result
    
    # Method 4: Last resort - try to estimate from publications count
    pub_count = len(extract_publications(soup, html))
    if pub_count > 0:
        # Estimate h-index based on publication count (common heuristic)
        estimated_h = int(math.sqrt(pub_count))
        result['h_index'] = estimated_h
        result['citations'] = pub_count * 5  # Very rough estimate
        result['method'] = 'estimated'
        logging.info(f"Estimated metrics from publication count: {pub_count}")
    
    return result

def extract_metrics_from_table(soup: BeautifulSoup, html: str) -> Dict[str, int]:
    """Extract citation metrics from the citation table."""
    metrics = {'citations': 0, 'h_index': 0, 'i10_index': 0}
    
    # Try BeautifulSoup first (more reliable)
    table = soup.select_one('#gsc_rsb_st')
    if table:
        rows = table.select('tr')
        for row in rows[1:]:  # Skip header row
            cells = row.select('td')
            if len(cells) < 2:
                continue
                
            metric_name = cells[0].text.strip().lower()
            try:
                value = int(re.search(r'(\d+)', cells[1].text).group(1))
            except (AttributeError, ValueError):
                continue
                
            if 'citation' in metric_name:
                metrics['citations'] = value
            elif 'h-index' in metric_name or 'h index' in metric_name:
                metrics['h_index'] = value
            elif 'i10-index' in metric_name or 'i10 index' in metric_name:
                metrics['i10_index'] = value
    
    # If BeautifulSoup failed, try regex
    if not any(metrics.values()):
        table_match = re.search(r'<table[^>]*id="gsc_rsb_st"[^>]*>(.*?)</table>', html, re.DOTALL)
        if table_match:
            table_html = table_match.group(1)
            rows = re.findall(r'<tr[^>]*>(.*?)</tr>', table_html, re.DOTALL)
            
            for row in rows:
                if '<th' in row:
                    continue
                    
                cells = re.findall(r'<td[^>]*>(.*?)</td>', row, re.DOTALL)
                if len(cells) < 2:
                    continue
                    
                metric_name = clean_text(re.sub(r'<[^>]+>', '', cells[0])).lower()
                
                try:
                    value_match = re.search(r'(\d+)', re.sub(r'<[^>]+>', '', cells[1]))
                    if not value_match:
                        continue
                    value = int(value_match.group(1))
                except (AttributeError, ValueError):
                    continue
                
                if 'citation' in metric_name:
                    metrics['citations'] = value
                elif 'h-index' in metric_name or 'h index' in metric_name:
                    metrics['h_index'] = value
                elif 'i10-index' in metric_name or 'i10 index' in metric_name:
                    metrics['i10_index'] = value
    
    return metrics

def extract_metrics_from_boxes(soup: BeautifulSoup, html: str) -> Dict[str, int]:
    """Extract citation metrics from the summary boxes."""
    metrics = {'citations': 0, 'h_index': 0, 'i10_index': 0}
    
    # Try BeautifulSoup first
    metric_boxes = soup.select('.gsc_rsb_std')
    if len(metric_boxes) >= 3:
        try:
            metrics['citations'] = int(metric_boxes[0].text.strip())
            metrics['h_index'] = int(metric_boxes[1].text.strip())
            metrics['i10_index'] = int(metric_boxes[2].text.strip())
        except (ValueError, IndexError):
            pass
    
    # If BeautifulSoup failed, try regex
    if not any(metrics.values()):
        all_metrics = re.findall(r'<div class="gsc_rsb_std">\s*(\d+)\s*</div>', html, re.DOTALL)
        if len(all_metrics) >= 3:
            try:
                metrics['citations'] = int(all_metrics[0])
                metrics['h_index'] = int(all_metrics[1])
                metrics['i10_index'] = int(all_metrics[2])
            except (ValueError, IndexError):
                pass
    
    return metrics

def extract_metrics_from_text(soup: BeautifulSoup, html: str) -> Dict[str, int]:
    """Extract citation metrics from text mentions."""
    metrics = {'citations': 0, 'h_index': 0, 'i10_index': 0}
    
    # Get the text content
    text = soup.get_text()
    
    # Citation patterns
    citation_patterns = [
        r'Citations\s*[:=]\s*(\d+)',
        r'Cited by\s*(\d+)',
        r'Total citations\s*[:=]\s*(\d+)',
        r'(\d+)\s+citations',
    ]
    
    for pattern in citation_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            try:
                metrics['citations'] = int(match.group(1))
                break
            except ValueError:
                pass
    
    # h-index patterns
    h_patterns = [
        r'h-index\s*[:=]\s*(\d+)',
        r'h index\s*[:=]\s*(\d+)',
        r'h[-\s]?index\D+(\d+)',
    ]
    
    for pattern in h_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            try:
                metrics['h_index'] = int(match.group(1))
                break
            except ValueError:
                pass
    
    # i10-index patterns
    i10_patterns = [
        r'i10-index\s*[:=]\s*(\d+)',
        r'i10 index\s*[:=]\s*(\d+)',
        r'i10[-\s]?index\D+(\d+)',
    ]
    
    for pattern in i10_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            try:
                metrics['i10_index'] = int(match.group(1))
                break
            except ValueError:
                pass
    
    return metrics

def extract_publications(soup: BeautifulSoup, html: str) -> List[Dict[str, str]]:
    """Extract publications with title and year."""
    publications = []
    
    # Method 1: Using BeautifulSoup
    pub_elements = soup.select('tr.gsc_a_tr')
    for element in pub_elements:
        title_elem = element.select_one('.gsc_a_t a')
        year_elem = element.select_one('.gsc_a_y')
        
        if title_elem and year_elem:
            title = title_elem.text.strip()
            year_text = year_elem.text.strip()
            # Extract year using regex if text contains multiple values
            year_match = re.search(r'(\d{4})', year_text)
            year = year_match.group(1) if year_match else year_text
            
            if title and year:
                publications.append({
                    'title': title,
                    'year': year
                })
    
    # Method 2: Using regex if Method 1 failed
    if not publications:
        title_matches = re.findall(r'<a[^>]*class="gsc_a_at"[^>]*>(.*?)</a>', html, re.DOTALL)
        year_matches = re.findall(r'<td[^>]*class="gsc_a_y"[^>]*>.*?(\d{4}).*?</td>', html, re.DOTALL)
        
        for i in range(min(len(title_matches), len(year_matches))):
            title = clean_text(re.sub(r'<[^>]+>', '', title_matches[i]))
            year = year_matches[i]
            if title and year:
                publications.append({
                    'title': title,
                    'year': year
                })
    
    return publications