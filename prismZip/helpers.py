import requests
import logging
import time
import os
import re
import math
from utils import handle_exceptions
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from urllib.parse import urlparse, parse_qs
import spacy
from spacy.language import Language
from spacy.tokens import Doc
# Separate retry strategies for different APIs
scholar_retry_strategy = Retry(
    total=3,
    backoff_factor=30,
    status_forcelist=[429, 500, 502, 503, 504],
)

semantic_retry_strategy = Retry(
    total=2,  # Fewer retries for Semantic Scholar
    backoff_factor=2,  # Much shorter backoff
    status_forcelist=[429, 500, 502, 503, 504],
)

# Create separate sessions for each API
scholar_session = requests.Session()
semantic_session = requests.Session()

# Configure sessions with their respective retry strategies
scholar_adapter = HTTPAdapter(max_retries=scholar_retry_strategy)
semantic_adapter = HTTPAdapter(max_retries=semantic_retry_strategy)

scholar_session.mount("https://", scholar_adapter)
scholar_session.mount("http://", scholar_adapter)
semantic_session.mount("https://", semantic_adapter)
semantic_session.mount("http://", semantic_adapter)

# Use scholar_session as the default session for backward compatibility
session = scholar_session

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

# Initialize spaCy with English model
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    # If model is not installed, download it
    spacy.cli.download("en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")

# Add custom components to spaCy pipeline
@Language.component("research_topic_extractor")
def research_topic_extractor(doc: Doc) -> Doc:
    """Extract research-related topics from text"""
    research_patterns = [
        "research",
        "study",
        "analysis",
        "investigation",
        "methodology",
        "theory",
        "approach",
        "framework"
    ]
    doc._.research_topics = []
    
    for sent in doc.sents:
        # Look for noun phrases that are likely research topics
        for chunk in sent.noun_chunks:
            if (any(token.pos_ in ["NOUN", "PROPN"] for token in chunk) and
                (any(pattern in chunk.text.lower() for pattern in research_patterns) or
                 any(token.dep_ in ["nsubj", "dobj"] for token in chunk))):
                doc._.research_topics.append(chunk.text)
    
    return doc

# Add custom attributes to Doc
if not Doc.has_extension("research_topics"):
    Doc.set_extension("research_topics", default=[])

# Add the custom component to the pipeline
if "research_topic_extractor" not in nlp.pipe_names:
    nlp.add_pipe("research_topic_extractor", after="parser")


def _strip_html(html: str) -> str:
    """
    Remove HTML tags and compress whitespace to yield readable text.
    """
    # Remove script/style content
    html = re.sub(r"<script[\s\S]*?</script>", " ", html, flags=re.I)
    html = re.sub(r"<style[\s\S]*?</style>", " ", html, flags=re.I)
    # Remove tags
    text = re.sub(r"<[^>]+>", " ", html)
    # Unescape basic entities
    text = text.replace("&nbsp;", " ").replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
    # Normalize whitespace
    return re.sub(r"\s+", " ", text).strip()


def _extract_affiliation(html: str) -> str:
    # Try to get the affiliation text inside profile header
    m = re.search(r'class="gsc_prf_il"[^>]*>(.*?)<', html, flags=re.I | re.S)
    if m:
        return _strip_html(m.group(1))
    return "Not available"


def _extract_research_interests(html: str) -> list:
    interests = re.findall(r'class="gsc_prf_ila"[^>]*>(.*?)<', html, flags=re.I | re.S)
    return [ _strip_html(t) for t in interests if _strip_html(t) ]


def extract_citation_metrics_from_table(html: str) -> dict:
    """
    Extract citation metrics directly from the citation table in Google Scholar HTML.
    This is a more reliable method than text extraction.
    """
    metrics = {'citations': 0, 'h_index': 0, 'i10_index': 0}
    
    # Find the citation table
    table_match = re.search(r'<table[^>]*id="gsc_rsb_st"[^>]*>(.*?)</table>', html, re.DOTALL)
    if not table_match:
        # Try alternative method - look for citation metrics in the summary boxes
        citations_match = re.search(r'<div class="gsc_rsb_std">\s*(\d+)\s*</div>', html, re.DOTALL)
        if citations_match:
            metrics['citations'] = int(citations_match.group(1))
            
            # Find all metrics in order (citations, h-index, i10-index)
            all_metrics = re.findall(r'<div class="gsc_rsb_std">\s*(\d+)\s*</div>', html, re.DOTALL)
            if len(all_metrics) >= 3:
                try:
                    metrics['citations'] = int(all_metrics[0])
                    metrics['h_index'] = int(all_metrics[1])
                    metrics['i10_index'] = int(all_metrics[2])
                    return metrics
                except (ValueError, IndexError):
                    pass
                    
        return metrics
        
    table_html = table_match.group(1)
    
    # Extract rows from the table
    rows = re.findall(r'<tr[^>]*>(.*?)</tr>', table_html, re.DOTALL)
    
    # Each metric should be in its own row with two <td> elements
    for row in rows:
        # Skip header row
        if '<th' in row:
            continue
            
        # Extract cells
        cells = re.findall(r'<td[^>]*>(.*?)</td>', row, re.DOTALL)
        if len(cells) < 2:
            continue
            
        metric_name = _strip_html(cells[0]).lower()
        
        # Try to find and extract the numeric value from the second cell
        value_match = re.search(r'(\d+)', _strip_html(cells[1]))
        if not value_match:
            continue
            
        value = int(value_match.group(1))
        
        # Match the metric to our dictionary
        if 'citation' in metric_name:
            metrics['citations'] = value
        elif 'h-index' in metric_name or 'h index' in metric_name:
            metrics['h_index'] = value
        elif 'i10-index' in metric_name or 'i10 index' in metric_name:
            metrics['i10_index'] = value
    
    return metrics


def _extract_citation_metrics_from_text(text: str) -> dict:
    """
    Extract citation metrics using spaCy NLP processing.
    """
    metrics = {'citations': 0, 'h_index': 0, 'i10_index': 0}
    doc = nlp(text)
    
    # Extract numbers that follow citation-related terms
    for sent in doc.sents:
        # Process each token in the sentence
        for token in sent:
            if token.like_num and token.i > 0:  # If it's a number and not the first token
                prev_text = doc[token.i-1:token.i].text.lower()
                
                # Check for citation metrics
                if 'citation' in prev_text or 'cited' in prev_text:
                    try:
                        metrics['citations'] = int(token.text)
                    except ValueError:
                        pass
                        
                elif any(x in prev_text for x in ['h-index', 'h index', 'hindex']):
                    try:
                        metrics['h_index'] = int(token.text)
                    except ValueError:
                        pass
                        
                elif any(x in prev_text for x in ['i10-index', 'i10 index', 'i10index']):
                    try:
                        metrics['i10_index'] = int(token.text)
                    except ValueError:
                        pass
    
    # If spaCy parsing fails, fall back to regex
    if all(v == 0 for v in metrics.values()):
        # citations
        m = re.search(r'(?:Citations?)\D*(\d{1,7})', text, flags=re.I)
        if m:
            try:
                metrics['citations'] = int(m.group(1))
            except ValueError:
                pass
        # h-index
        m = re.search(r'h[- ]?index\D*(\d{1,4})', text, flags=re.I)
        if m:
            try:
                metrics['h_index'] = int(m.group(1))
            except ValueError:
                pass
        # i10-index
        m = re.search(r'i10[- ]?index\D*(\d{1,4})', text, flags=re.I)
        if m:
            try:
                metrics['i10_index'] = int(m.group(1))
            except ValueError:
                pass
    
    return metrics


def _extract_publications_from_html(html: str) -> list:
    """Extract publication titles and years using lightweight regexes.
    This targets common Scholar classes but gracefully degrades when structure changes.
    """
    publications = []
    # Titles are usually in anchors with class gsc_a_at
    title_matches = re.findall(r'class="gsc_a_at"[^>]*>(.*?)<', html, flags=re.I | re.S)
    # Years are in cells with class gsc_a_y (possibly with a span)
    year_matches = re.findall(r'class="gsc_a_y"[^>]*>\s*(?:<span[^>]*>)?\s*(\d{4})\s*(?:</span>)?\s*<', html, flags=re.I | re.S)
    # Pair up to the min length to avoid index errors
    n = min(len(title_matches), len(year_matches))
    for i in range(n):
        title = _strip_html(title_matches[i])
        year = _strip_html(year_matches[i])
        if title and year:
            publications.append({ 'title': title, 'year': year })
    return publications

@handle_exceptions
def extract_scholar_data(teacher_name, scholar_url):
    """
    Extracts data from a Google Scholar profile.

    Args:
        teacher_name (str): The name of the teacher.
        scholar_url (str): The URL of the Google Scholar profile.

    Returns:
        dict: A dictionary containing the extracted data.
    """
    try:
        # Log the start of the extraction
        logging.info(f"Starting Google Scholar extraction for {teacher_name} at {scholar_url}")
        
        # Fetch the Google Scholar profile
        response = scholar_session.get(scholar_url, headers=headers, timeout=30)
        response.raise_for_status()
        html = response.text
        
        # Debug information: Check if we got a valid response
        logging.info(f"Google Scholar response length: {len(html)} characters")
        
        # Look for citation table - this is a strong indicator of data presence
        citation_table = re.search(r'<table[^>]*id="gsc_rsb_st"[^>]*>(.*?)</table>', html, re.DOTALL)
        if not citation_table:
            logging.warning(f"No citation table found in Google Scholar profile for {teacher_name}")
        else:
            logging.info(f"Citation table found for {teacher_name}")
        
        text = _strip_html(html)
        time.sleep(int(os.getenv('REQUEST_DELAY', 5)))  # Reduced delay

        # Extract citation metrics with direct method
        citation_metrics = extract_citation_metrics(text)
        logging.info(f"Extracted citation metrics: {citation_metrics}")
        
        # Try direct table extraction as backup
        table_metrics = extract_citation_metrics_from_table(html)
        logging.info(f"Table-extracted citation metrics: {table_metrics}")
        
        # Combine metrics, preferring non-zero values
        if table_metrics['citations'] > 0 and citation_metrics['citations'] == 0:
            citation_metrics['citations'] = table_metrics['citations']
        if table_metrics['h_index'] > 0 and citation_metrics['h_index'] == 0:
            citation_metrics['h_index'] = table_metrics['h_index']
        if table_metrics['i10_index'] > 0 and citation_metrics['i10_index'] == 0:
            citation_metrics['i10_index'] = table_metrics['i10_index']
        
        publications = extract_publications(html)
        affiliation = _extract_affiliation(html)
        research_interests = _extract_research_interests(html)

        # Calculate total publications from different sources
        pub_count = len(publications)
        
        # If we have no citation metrics but have publications, estimate h-index
        if citation_metrics['citations'] == 0 and citation_metrics['h_index'] == 0 and pub_count > 0:
            # Estimate h-index as sqrt(publications) - a common heuristic
            estimated_h_index = int(math.sqrt(pub_count))
            if estimated_h_index > 0:
                citation_metrics['h_index'] = estimated_h_index
                logging.info(f"Estimated h-index as {estimated_h_index} based on {pub_count} publications")
        
        data = {
            'Google Scholar Data': {
                'Citations': citation_metrics['citations'],
                'h-index': citation_metrics['h_index'],
                'i10-index': citation_metrics['i10_index'],
                'Total Publications': pub_count,
                'Research Interests': research_interests,
                'Current Affiliation': affiliation,
                'Publications': publications,
                '_debug_info': {
                    'extraction_method': 'direct' if citation_metrics['citations'] > 0 else 'estimated',
                    'url': scholar_url
                }
            }
        }
        
        # Log the final data
        logging.info(f"Final Google Scholar data for {teacher_name}: Citations={citation_metrics['citations']}, h-index={citation_metrics['h_index']}")
        return data

    except requests.exceptions.RequestException as e:
        logging.error(f"Network error while fetching {scholar_url}: {str(e)}")
        raise
    except Exception as e:
        logging.error(f"Error parsing Google Scholar profile for {teacher_name} ({scholar_url}): {str(e)}")
        raise

@handle_exceptions
def extract_citation_metrics(text: str, html: str = None):
    """
    Extracts citation metrics (citations, h-index, i10-index) from text and HTML content.
    Tries multiple methods to ensure the most accurate data extraction.

    Args:
        text (str): Visible text content of the Google Scholar profile page.
        html (str): Optional HTML content for additional extraction methods.

    Returns:
        dict: A dictionary containing the citation metrics.
    """
    default_metrics = { 'citations': 0, 'h_index': 0, 'i10_index': 0 }

    try:
        # Method 1: Extract from text using NLP
        text_metrics = _extract_citation_metrics_from_text(text)
        logging.info(f"Text-based metrics: {text_metrics}")
        
        # Method 2: Extract from HTML table if available
        table_metrics = default_metrics
        if html:
            table_metrics = extract_citation_metrics_from_table(html)
            logging.info(f"Table-based metrics: {table_metrics}")
            
        # Method 3: Extract using regex patterns looking for specific citation formats
        pattern_metrics = extract_metrics_using_patterns(text, html)
        logging.info(f"Pattern-based metrics: {pattern_metrics}")
        
        # Combine all metrics, preferring non-zero values
        final_metrics = {
            'citations': text_metrics.get('citations', 0) or table_metrics.get('citations', 0) or pattern_metrics.get('citations', 0) or 0,
            'h_index': text_metrics.get('h_index', 0) or table_metrics.get('h_index', 0) or pattern_metrics.get('h_index', 0) or 0,
            'i10_index': text_metrics.get('i10_index', 0) or table_metrics.get('i10_index', 0) or pattern_metrics.get('i10_index', 0) or 0,
        }
        
        logging.info(f"Final combined metrics: {final_metrics}")
        return final_metrics
    except Exception as e:
        logging.error(f"Error extracting citation metrics: {str(e)}")
        return default_metrics


def extract_metrics_using_patterns(text: str, html: str = None) -> dict:
    """
    Extract citation metrics using multiple regex patterns to handle different Google Scholar page formats.
    """
    metrics = {'citations': 0, 'h_index': 0, 'i10_index': 0}
    
    # Try to extract citation count with various patterns
    citation_patterns = [
        r'Cited by (\d+)',
        r'Citations: (\d+)',
        r'Total citations: (\d+)',
        r'Citations</a>.*?(\d+)',
        r'Citations:?\s*(\d+)',
    ]
    
    for pattern in citation_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            try:
                metrics['citations'] = int(match.group(1))
                break
            except ValueError:
                pass
    
    # Try to extract h-index with various patterns
    h_patterns = [
        r'h-index:?\s*(\d+)',
        r'h-index</a>.*?(\d+)',
        r'h-index:? (\d+)',
        r'h index:?\s*(\d+)',
    ]
    
    for pattern in h_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            try:
                metrics['h_index'] = int(match.group(1))
                break
            except ValueError:
                pass
    
    # Try to extract i10-index with various patterns
    i10_patterns = [
        r'i10-index:?\s*(\d+)',
        r'i10-index</a>.*?(\d+)',
        r'i10-index:? (\d+)',
        r'i10 index:?\s*(\d+)',
    ]
    
    for pattern in i10_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            try:
                metrics['i10_index'] = int(match.group(1))
                break
            except ValueError:
                pass
    
    # If HTML is available, try to extract from specific HTML elements
    if html:
        # Look for citation count in specific divs/spans
        citation_html_patterns = [
            r'<div[^>]*id="gsc_rsb_cit"[^>]*>.*?<a[^>]*>Cited by (\d+)</a>',
            r'<td[^>]*>Citations</td>\s*<td[^>]*>(\d+)</td>',
            r'<div[^>]*class="gsc_rsb_std"[^>]*>(\d+)</div>'
        ]
        
        for pattern in citation_html_patterns:
            match = re.search(pattern, html, re.IGNORECASE | re.DOTALL)
            if match and metrics['citations'] == 0:
                try:
                    metrics['citations'] = int(match.group(1))
                except ValueError:
                    pass
    
    return metrics

@handle_exceptions
def extract_publications(html: str):
    """
    Extracts publications (title and year) using HTML regex heuristics.

    Args:
        html (str): The HTML of the Google Scholar profile.

    Returns:
        list: A list of dictionaries, where each dictionary contains the title and year of a publication.
    """
    try:
        publications = _extract_publications_from_html(html)
        return publications
    except Exception as e:
        logging.error(f"Error extracting publications: {str(e)}")
        raise

def extract_author_id_from_url(semantic_scholar_url: str) -> str:
    """
    Extract author ID from a Semantic Scholar profile URL.
    
    Args:
        semantic_scholar_url (str): The Semantic Scholar profile URL.
        
    Returns:
        str: The author ID.
    """
    try:
        parsed_url = urlparse(semantic_scholar_url)
        path_parts = parsed_url.path.strip('/').split('/')
        if 'author' in path_parts:
            author_index = path_parts.index('author')
            if len(path_parts) > author_index + 1:
                return path_parts[author_index + 1]
        return None
    except Exception as e:
        logging.error(f"Error extracting author ID from URL {semantic_scholar_url}: {str(e)}")
        return None

@handle_exceptions
def extract_semantic_scholar_data(semantic_scholar_url: str):
    """
    Extracts data from a Semantic Scholar profile using their API.
    
    Args:
        semantic_scholar_url (str): The URL of the Semantic Scholar profile.
        
    Returns:
        dict: A dictionary containing the extracted data.
    """
    default_response = {
        'Semantic Scholar Data': {
            'status': 'error',
            'Citations': 0,
            'h-index': 0,
            'Total Publications': 0,
            'Current Affiliation': 'Not available',
            'Publications': []
        }
    }

    try:
        author_id = extract_author_id_from_url(semantic_scholar_url)
        if not author_id:
            default_response['Semantic Scholar Data']['reason'] = "Could not extract author ID from URL"
            return default_response

        # API endpoint for author details - limit papers to reduce response size
        api_url = f"https://api.semanticscholar.org/graph/v1/author/{author_id}?fields=name,affiliations,paperCount,citationCount,hIndex,papers.limit(10).year,papers.limit(10).title"
        
        try:
            response = semantic_session.get(
                api_url, 
                headers={'User-Agent': headers['User-Agent']},
                timeout=10  # Reduced timeout
            )
            response.raise_for_status()
            
            if response.status_code == 429:  # Rate limit hit
                time.sleep(2)  # Wait briefly
                return extract_semantic_scholar_data(semantic_scholar_url)  # Retry once
                
        except requests.exceptions.Timeout:
            default_response['Semantic Scholar Data']['reason'] = "Request timed out"
            return default_response
        except requests.exceptions.RequestException as e:
            default_response['Semantic Scholar Data']['reason'] = f"Network error: {str(e)}"
            return default_response
        
        try:
            data = response.json()
        except ValueError:
            default_response['Semantic Scholar Data']['reason'] = "Invalid JSON response"
            return default_response

        # Validate response structure
        if not isinstance(data, dict):
            default_response['Semantic Scholar Data']['reason'] = "Invalid response format"
            return default_response

        # Validate required fields
        required_fields = ['paperCount', 'citationCount', 'hIndex']
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            default_response['Semantic Scholar Data']['reason'] = f"Missing required fields: {', '.join(missing_fields)}"
            return default_response
        
        # Format publications with validation
        publications = []
        if isinstance(data.get('papers'), list):
            for paper in data['papers']:
                if isinstance(paper, dict):
                    title = paper.get('title')
                    year = paper.get('year')
                    if title and year and isinstance(title, str) and str(year).isdigit():
                        publications.append({
                            'title': title,
                            'year': str(year)
                        })

        # Get current affiliation with validation
        current_affiliation = "Not available"
        affiliations = data.get('affiliations', [])
        if isinstance(affiliations, list) and affiliations and isinstance(affiliations[0], str):
            current_affiliation = affiliations[0]

        return {
            'Semantic Scholar Data': {
                'status': 'success',
                'Citations': data.get('citationCount', 0),
                'h-index': data.get('hIndex', 0),
                'Total Publications': data.get('paperCount', 0),
                'Current Affiliation': current_affiliation,
                'Publications': publications
            }
        }
        
    except Exception as e:
        default_response['Semantic Scholar Data']['reason'] = f"Unexpected error: {str(e)}"
        return default_response
