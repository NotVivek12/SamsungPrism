"""
Professor API routes for Flask application.
This module contains all Flask routes related to professor management using MySQL database.
"""

from flask import Blueprint, request, jsonify
from domain_expertise_analyzer import DomainExpertiseAnalyzer
import logging
import time
import os
import sys
import re
import json
from gemma_service import parse_search_query_with_gemma, analyze_project_description
# Import the database module for MySQL access
import database
# Import citations cache functionality
from extract_citations import get_cached_citations, get_extraction_status, load_teachers_data

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create a Blueprint for professor routes
professor_bp = Blueprint('professors', __name__)

# Cache for mapping between database IDs and JSON IDs
_id_mapping_cache = {}

def extract_user_id_from_url(url):
    """Extract the Google Scholar user ID from a URL"""
    if not url:
        return None
        
    # Pattern to extract user ID from Google Scholar URL
    pattern = r'user=([^&]+)'
    import re
    match = re.search(pattern, url)
    
    if match:
        return match.group(1)
    return None

def get_id_mapping():
    """
    Create a mapping between database professor IDs and JSON teacher IDs using Google Scholar URLs
    This is now a fixed mapping based on URL matching.
    """
    global _id_mapping_cache
    
    # Return from cache if already created
    if _id_mapping_cache:
        return _id_mapping_cache
    
    # Use a fixed mapping based on URL matching
    _id_mapping_cache = {
        "1": "f82927e5",
        "2": "269d1df4",
        "3": "330b2ec8",
        "4": "604acafb",
        "5": "27a5af22",
        "6": "178c7c38",
        "7": "93f1f247",
        "8": "d1eaa67b",
        "9": "356479b6",
        "10": "fbac84dc",
        "11": "cf49f1ec",
        "12": "2ae48827",
        "13": "531abde5",
        "14": "42352203",
        "15": "6e29ae55",
        "16": "61b86351",
        "17": "0742e275",
        "18": "5b69dd05",
        "19": "ee2462c8",
        "20": "40228e0a",
        "21": "bc094bd0",
        "22": "22caa4c9",
        "23": "f9d3a7fa",
        "24": "90e6e90e",
        "28": "add3ab6d",
        "30": "ca6b7fa2",
        "31": "4cf60b85",
        "32": "5b999cef",
        "33": "0afcc15a",
        "34": "22da2bc5",
        "35": "8c57837a",
        "36": "bf8f1654",
        "37": "ae3fd05b",
        "38": "0c4c9965",
        "39": "a570f76f",
        "40": "d8c863bb",
        "41": "77a51e69",
        "42": "2d766a82",
        "43": "ec7dc7c9",
        "44": "df0182b6",
        "45": "3b13e4a3",
        "46": "4a7c35c2",
        "47": "6b9d99ac",
        "48": "37c82811",
        "49": "d5bfcd25",
        "50": "b3020849",
        "51": "75229028",
        "52": "e87038cb",
        "53": "8c81eecf",
        "54": "3dcaef53",
        "55": "e95fca89",
        "57": "1c600a74",
        "58": "340b79c3",
        "59": "3b9ea944",
        "60": "4ee705e0",
        "61": "d339d4ee",
        "62": "adbd1626",
        "63": "96b96249",
        "64": "84f0f655",
        "65": "a07fdc29",
        "66": "bad083bf",
        "67": "16c18f89",
        "68": "3d3b8d08",
        "69": "e948ff38",
        "70": "66fefbab",
        "71": "78e9202e",
        "72": "97d45c98",
        "73": "b577bea5",
        "74": "d8929d2d",
        "75": "6194fc48",
        "76": "0f8a98a6",
        "78": "02edb62d",
        "80": "80481b35",
        "81": "9961ed33",
        "82": "1c2eb5d4",
        "83": "97d44c78",
        "84": "5674261a",
        "86": "5d71abbd",
        "87": "25e3e04c",
        "88": "aad7b42f",
        "89": "27346626",
        "90": "f1d6ae1c",
        "91": "f7a589d1",
        "92": "1d6f1bc0",
        "93": "8bf55465",
        "94": "53b27e05",
        "95": "e1b795bd",
        "96": "bf72053f",
        "97": "c23e3c54",
        "98": "f3ac5745",
        "99": "d5afb097",
        "100": "17d5d44d",
        "101": "3712af3e",
        "103": "3f075262",
        "104": "6910c2ba",
        "105": "2ccae569",
        "106": "f407b230",
        "107": "616399cb",
        "108": "84789531",
        "109": "741aa7b2",
        "110": "f533407a",
        "111": "0a1bcf15",
        "112": "9795085f",
        "113": "fabe1f64",
        "114": "d301dc18",
        "115": "fabe1f64",
        "116": "a6ffb886",
        "117": "0e31ae47",
        "118": "53ab4f12",
        "119": "bdb5f316",
        "120": "36a056c5",
        "121": "b2f670e0",
        "122": "86666828",
        "123": "a0d8813e",
        "125": "662435a0",
        "126": "003393bd",
        "127": "9a08e3ba",
        "129": "98d4edb1",
        "130": "d55d56e8",
        "131": "48ad13a1",
        "133": "057e7a37",
        "134": "bbe272b9",
        "135": "6b4017f9",
        "136": "d2c13a66",
        "137": "230cf72d",
        "138": "f9502370",
        "139": "59c83240",
        "140": "38898a82",
        "141": "9f3fb71a",
        "142": "9a0ca738",
        "144": "87c8f7b5",
        "146": "f15708c2",
        "147": "f15708c2",
        "148": "ae022b98",
        "149": "d2806c1b",
        "150": "60f0b0cd",
        "151": "745daaf1",
        "152": "9c596abf",
        "153": "78a2248d",
        "154": "076fc9dc",
        "155": "b6cc2602",
        "156": "6765af95",
        "157": "c6f1d12e",
        "158": "5a8e37ce",
        "159": "60141a9b",
        "160": "b88372cc",
        "161": "d79c2c15",
        "162": "1da52796",
        "163": "b7bbc1d9",
        "164": "1d5fdaa4",
        "165": "ed5b6326",
        "167": "23d0b70b",
        "168": "65acd85b",
        "170": "64cb63cf",
        "171": "f1daf02c",
        "172": "63c1f775",
        "173": "6632ab2b",
        "174": "19b0353f",
        "176": "eb18ec01",
        "177": "24299115",
        "178": "bea23e67",
        "179": "5b999cef",
        "180": "119bd6d9",
        "181": "fba293ed",
        "182": "360eca1f",
        "183": "841a653c",
        "184": "c345087f",
        "185": "9505eb8b",
        "187": "01531294",
        "188": "134e89fd",
        "189": "c484fb71",
        "190": "473a1a50",
        "191": "e6cabf1b",
        "192": "28191f09",
        "193": "c0387404",
        "194": "763b5af2",
        "195": "c134e72b",
        "196": "492a63f7",
        "198": "f6baff3c",
        "199": "01b334a2",
        "200": "81cd745f",
        "201": "a7cee113",
        "202": "e54d8c12",
        "203": "6f91cf3c",
        "204": "576e3f1d",
        "205": "e852bff1",
        "206": "73d77e53"
    }
    
    logging.info(f"Using fixed ID mapping with {len(_id_mapping_cache)} entries")
    return _id_mapping_cache
    
    try:
        # Get teachers from JSON
        json_teachers = load_teachers_data()
        
        # Get professors from database
        db_professors = database.load_professors_data()
        
        # Create a mapping from Google Scholar URL to JSON ID
        url_to_json_id = {}
        user_id_to_json_id = {}
        
        for teacher in json_teachers:
            json_id = teacher.get('id')
            if not json_id:
                continue
                
            gs_url = teacher.get('google_scholar_url', '')
            if gs_url:
                url_to_json_id[gs_url] = str(json_id)
                
                # Extract user ID from URL
                user_id = extract_user_id_from_url(gs_url)
                if user_id:
                    user_id_to_json_id[user_id] = str(json_id)
        
        # Create mapping from database ID to JSON ID
        id_mapping = {}
        
        # Try matching by Google Scholar URL
        for prof in db_professors:
            db_id = str(prof.get('id', ''))
            gs_url = prof.get('google_scholar_url', '')
            
            if gs_url and gs_url in url_to_json_id:
                json_id = url_to_json_id[gs_url]
                id_mapping[db_id] = json_id
                continue
                
            # Try extracting user ID from URL and matching
            user_id = extract_user_id_from_url(gs_url)
            if user_id and user_id in user_id_to_json_id:
                json_id = user_id_to_json_id[user_id]
                id_mapping[db_id] = json_id
                continue
            
            # As a fallback, try direct ID mapping (if JSON IDs are numeric)
            if str(db_id) in [str(t.get('id', '')) for t in json_teachers]:
                id_mapping[db_id] = db_id
        
        # Cache the mapping
        _id_mapping_cache = id_mapping
        logging.info(f"Created ID mapping with {len(id_mapping)} entries")
        return id_mapping
        
    except Exception as e:
        logging.error(f"Error creating ID mapping: {str(e)}")
        import traceback
        logging.error(traceback.format_exc())
        return {}

# Initialize spaCy and enable scholar extraction
try:
    import spacy
    import requests
    from bs4 import BeautifulSoup
    
    # Load spaCy model
    try:
        nlp = spacy.load("en_core_web_sm")
    except OSError:
        # If model is not installed, download it
        print("Downloading spaCy model...")
        import subprocess
        subprocess.call([sys.executable, "-m", "spacy", "download", "en_core_web_sm"])
        nlp = spacy.load("en_core_web_sm")
    
    SCHOLAR_ENABLED = True
    print("Scholar extraction enabled with spaCy")
    
    def extract_scholar_data_with_spacy(url):
        """
        Extract scholar data from Google Scholar using spaCy for text processing
        
        Args:
            url: URL of the Google Scholar profile
            
        Returns:
            Dictionary containing extracted data
        """
        try:
            # Use a browser-like user agent to avoid being blocked
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            # Fetch the HTML content
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code != 200:
                print(f"Failed to fetch Google Scholar profile: Status code {response.status_code}")
                return None
                
            # Parse HTML with BeautifulSoup for basic structure
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract metrics (citations, h-index, i10-index)
            metrics_data = {}
            metrics_table = soup.select_one('table#gsc_rsb_st')
            if metrics_table:
                rows = metrics_table.select('tr')
                for row in rows[1:]:  # Skip header row
                    cols = row.select('td')
                    if len(cols) >= 2:
                        metric_name = cols[0].get_text(strip=True)
                        metric_value = cols[1].get_text(strip=True)
                        metrics_data[metric_name] = int(metric_value) if metric_value.isdigit() else metric_value
            
            # Extract publications
            publications = []
            pub_items = soup.select('.gsc_a_tr')
            
            # Try to find the actual total publication count from the page
            # Look for pagination or total count indicators
            total_publications = len(pub_items)  # Default to visible count
            
            # Check if there's pagination info or a "Show more" button that might indicate more publications
            show_more_button = soup.select_one('#gsc_bpf_more')
            if show_more_button and not show_more_button.get('disabled'):
                # If there's an active "Show more" button, there are likely more than what's visible
                # We can't get the exact count without making additional requests, 
                # so we'll indicate this is a partial count
                total_publications = f"{len(pub_items)}+"
            
            # Extract only the first 10 for display
            for item in pub_items[:10]:  # Get first 10 publications
                title_elem = item.select_one('.gsc_a_t a')
                authors_elem = item.select_one('.gsc_a_t .gs_gray:nth-of-type(1)')
                venue_elem = item.select_one('.gsc_a_t .gs_gray:nth-of-type(2)')
                year_elem = item.select_one('.gsc_a_y span')
                citations_elem = item.select_one('.gsc_a_c a')
                
                if title_elem:
                    pub = {
                        'title': title_elem.get_text(strip=True),
                        'authors': authors_elem.get_text(strip=True) if authors_elem else "",
                        'venue': venue_elem.get_text(strip=True) if venue_elem else "",
                        'year': year_elem.get_text(strip=True) if year_elem else "",
                        'citations': int(citations_elem.get_text(strip=True)) if citations_elem and citations_elem.get_text(strip=True).isdigit() else 0
                    }
                    publications.append(pub)
            
            # Extract research interests using spaCy
            interests = []
            interests_div = soup.select_one('#gsc_prf_int')
            if interests_div:
                interests_text = interests_div.get_text(strip=True)
                # Use spaCy to process and extract meaningful phrases
                doc = nlp(interests_text)
                for phrase in interests_text.split(','):
                    clean_phrase = phrase.strip()
                    if clean_phrase:
                        interests.append(clean_phrase)
            
            # Extract profile info
            name = ""
            affiliation = ""
            profile_header = soup.select_one('#gsc_prf_in')
            if profile_header:
                name = profile_header.get_text(strip=True)
            
            affiliation_div = soup.select_one('.gsc_prf_il')
            if affiliation_div:
                affiliation = affiliation_div.get_text(strip=True)
            
            # Use spaCy to extract additional entities from affiliation
            affiliation_doc = nlp(affiliation)
            organizations = [ent.text for ent in affiliation_doc.ents if ent.label_ == "ORG"]
            locations = [ent.text for ent in affiliation_doc.ents if ent.label_ == "GPE" or ent.label_ == "LOC"]
            
            # Prepare the final data
            total_citations = metrics_data.get('Citations', 0)
            
            scholar_data = {
                "Google Scholar Data": {
                    "Name": name,
                    "Affiliation": affiliation,
                    "Citations": total_citations,
                    "h-index": metrics_data.get('h-index', 0),
                    "i10-index": metrics_data.get('i10-index', 0),
                    "Research Interests": ", ".join(interests),
                    "Publications": publications,
                    "Total Publications": total_publications,
                    "Organizations": organizations,
                    "Locations": locations
                }
            }
            
            return scholar_data
            
        except Exception as e:
            print(f"Error extracting Google Scholar data: {str(e)}")
            return None
            
except ImportError as e:
    print(f"Scholar extraction modules not available: {e}")
    SCHOLAR_ENABLED = False

# Database cache to avoid querying repeatedly
professors_data_cache = None
data_last_read_time = 0
CACHE_TIMEOUT = 300  # 5 minutes

def load_teachers_data():
    """Load professors data from MySQL database"""
    global professors_data_cache, data_last_read_time
    
    current_time = time.time()
    
    # Return cached data if it exists and is fresh
    if professors_data_cache is not None and current_time - data_last_read_time < CACHE_TIMEOUT:
        return professors_data_cache
    
    try:
        # Load data from database
        logger.info("Loading professors data from database")
        professors = database.load_professors_data()
        
        # Update cache
        professors_data_cache = professors
        data_last_read_time = current_time
        
        logger.info(f"✅ Successfully loaded {len(professors)} professors from database")
        return professors
    except Exception as e:
        logger.error(f"❌ Error loading professors data from database: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return []

@professor_bp.route('/api/professors/domain-experts', methods=['GET'])
def api_get_domain_experts():
    """
    API endpoint to search for professors with expertise in a specific domain
    
    Query Parameters:
        - domain: The domain/field to search for (required)
        - min_level: Minimum expertise level (Expert, Advanced, Intermediate, Basic)
        
    Returns:
        JSON response with list of experts and domain statistics
    """
    domain = request.args.get('domain')
    min_level = request.args.get('min_level', 'Advanced')
    
    if not domain:
        return jsonify({
            'error': 'Domain parameter is required'
        }), 400
    
    try:
        # Get professors with the specified domain directly from database
        experts = database.get_professors_by_domain(domain)
        
        return jsonify({
            'domain': domain,
            'min_level': min_level,
            'total_experts': len(experts),
            'experts': experts[:20]  # Limit to first 20
        })
        
    except Exception as e:
        logging.error(f"Error in domain experts search: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@professor_bp.route('/api/ai/search-teachers', methods=['POST'])
def api_ai_search_teachers():
    """AI-powered teacher search using Gemma"""
    try:
        data = request.get_json()
        query = data.get('query', '').strip()
        
        if not query or len(query) < 2:
            return jsonify({'teachers': [], 'query_analysis': None})
        
        # Use database search for professors
        filtered_teachers = database.search_professors(query)
        
        # Calculate relevance score
        keywords = query.lower().split()
        
        for professor in filtered_teachers:
            text_to_search = f"{professor.get('name', '')} {professor.get('domain_expertise', '')} {professor.get('phd_thesis', '')}".lower()
            
            score = 0
            for keyword in keywords:
                if keyword in text_to_search:
                    score += 1
            
            professor['relevance_score'] = score
        
        # Sort by relevance score
        filtered_teachers.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
        
        return jsonify({
            'professors': filtered_teachers[:50],  # Limit to top 50 results
            'total_results': len(filtered_teachers),
            'query': query
        })
        
    except Exception as e:
        logging.error(f"Error in AI search: {str(e)}")
        return jsonify({'professors': [], 'error': str(e)}), 500

@professor_bp.route('/api/project/analyze', methods=['POST'])
def api_analyze_project():
    """Analyze project description and find matching professors"""
    try:
        data = request.get_json()
        project_description = data.get('description', '').strip()
        
        if not project_description:
            return jsonify({'error': 'Project description is required'}), 400
        
        # Use Gemma to analyze the project
        try:
            analysis = analyze_project_description(project_description)
        except Exception as e:
            # Fallback analysis if Gemma fails
            analysis = {
                'summary': project_description[:200] + '...' if len(project_description) > 200 else project_description,
                'required_expertise': ['AI', 'Machine Learning', 'Data Science'],
                'key_skills': ['Python', 'Research', 'Analysis']
            }
        
        # Find matching professors
        professors = database.load_professors_data()
        matching_professors = []
        
        required_expertise = analysis.get('required_expertise', [])
        
        for professor in professors:
            if not professor.get('domain_expertise'):
                continue
                
            professor_domains = [d.strip().lower() for d in professor['domain_expertise'].split(',')]
            
            # Calculate match percentage
            matches = 0
            matching_domains = []
            
            for expertise in required_expertise:
                expertise_lower = expertise.lower()
                for domain in professor_domains:
                    if expertise_lower in domain or domain in expertise_lower:
                        matches += 1
                        matching_domains.append(expertise)
                        break
            
            if matches > 0:
                match_percentage = int((matches / len(required_expertise)) * 100)
                
                professor_match = professor.copy()
                professor_match['match_percentage'] = match_percentage
                professor_match['matching_domains'] = matching_domains
                
                matching_professors.append(professor_match)
        
        # Sort by match percentage
        matching_professors.sort(key=lambda x: x['match_percentage'], reverse=True)
        
        return jsonify({
            'analysis': analysis,
            'professors': matching_professors[:20],  # Top 20 matches
            'total_matches': len(matching_professors)
        })
        
    except Exception as e:
        logging.error(f"Error in project analysis: {str(e)}")
        return jsonify({'error': str(e)}), 500

@professor_bp.route('/api/professors', methods=['GET'])
def api_get_all_professors():
    """API endpoint to get all professors from MySQL database with optional filtering"""
    try:
        # Get query parameters
        limit = request.args.get('limit', type=int)
        college = request.args.get('college', '').strip()
        include_citations = request.args.get('include_citations', 'true').lower() == 'true'
        
        # Load professor data
        professors = database.load_professors_data()
        
        if not professors:
            return jsonify({'professors': [], 'total_count': 0, 'message': 'No professors found'})
        
        # Load citation data from cache if requested
        citations_cache = get_cached_citations() if include_citations else {}
        
        # Filter by college if specified
        if college:
            professors = [p for p in professors if p.get('college', '').strip().lower() == college.lower()]
            
        # Calculate total before applying limit
        total_count = len(professors)
            
        # Apply limit if specified
        if limit and limit > 0:
            professors = professors[:limit]
        
        # Add row numbers and citation data
        for i, professor in enumerate(professors, 1):
            professor['row_number'] = i
            
            # Add citation data from cache if available
            if include_citations and citations_cache:
                # Get database ID to JSON ID mapping
                id_mapping = get_id_mapping()
                
                # Try to get the corresponding JSON ID
                db_id = str(professor.get('id', ''))
                json_id = id_mapping.get(db_id)
                
                # If we have a matching JSON ID and it's in the citation cache
                if json_id and json_id in citations_cache:
                    citation_data = citations_cache[json_id]
                    professor['citations_count'] = citation_data.get('citations', 0)
                    professor['h_index'] = citation_data.get('h_index', 0)
                    professor['i10_index'] = citation_data.get('i10_index', 0)
                    # Add the JSON ID for reference
                    professor['json_id'] = json_id
        
        return jsonify({
            'professors': professors,
            'total_count': total_count,
            'filtered_count': len(professors),
            'message': f'Successfully loaded {len(professors)} professors' + (f' from college {college}' if college else ''),
            'citations_included': include_citations
        })
        
    except Exception as e:
        logging.error(f"Error fetching professors: {str(e)}")
        return jsonify({'professors': [], 'total_count': 0, 'error': 'Internal error'}), 500

@professor_bp.route('/api/professors/<int:professor_id>', methods=['GET'])
def api_get_professor_details(professor_id):
    """Get detailed information about a specific professor"""
    try:
        # Get professor by ID directly from database
        professor = database.get_professor_by_id(professor_id)
        
        if not professor:
            return jsonify({'error': 'Professor not found'}), 404
            
        # Add citation data from cache if available
        citations_cache = get_cached_citations()
        if citations_cache:
            # Get database ID to JSON ID mapping
            id_mapping = get_id_mapping()
            
            # Try to get the corresponding JSON ID
            db_id = str(professor_id)
            json_id = id_mapping.get(db_id)
            
            # If we have a matching JSON ID and it's in the citation cache
            if json_id and json_id in citations_cache:
                citation_data = citations_cache[json_id]
                professor['citations_count'] = citation_data.get('citations', 0)
                professor['h_index'] = citation_data.get('h_index', 0)
                professor['i10_index'] = citation_data.get('i10_index', 0)
                # Add the JSON ID for reference
                professor['json_id'] = json_id
        
        # Enhance with scholar data if available and enabled
        if SCHOLAR_ENABLED:
            try:
                scholar_data = None
                if professor.get('google_scholar_url'):
                    scholar_data = extract_scholar_data_with_spacy(professor['google_scholar_url'])
                
                if scholar_data:
                    professor['scholar_data'] = scholar_data
                    
                    # Extract metrics from scholar data
                    google_scholar_data = scholar_data.get('Google Scholar Data', {})
                    
                    # Update academic data
                    academic_data = {
                        'has_academic_data': True,
                        'citations': google_scholar_data.get('Citations', 0),
                        'h_index': google_scholar_data.get('h-index', 0),
                        'i10_index': google_scholar_data.get('i10-index', 0),
                        'total_publications': google_scholar_data.get('Total Publications', 0),
                        'recent_publications': google_scholar_data.get('Publications', [])[:10] if isinstance(google_scholar_data.get('Publications'), list) else [],
                        'research_interests': google_scholar_data.get('Research Interests', "").split(", ") if isinstance(google_scholar_data.get('Research Interests'), str) else [],
                        'data_sources': ['Google Scholar']
                    }
                    professor['academic_data'] = academic_data
                    
            except Exception as e:
                logging.error(f"Error extracting scholar data: {str(e)}")
        
        return jsonify(professor)
        
    except Exception as e:
        logging.error(f"Error fetching professor details: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@professor_bp.route('/api/professors/stats', methods=['GET'])
def api_get_professors_stats():
    """Get statistics about the professors database"""
    try:
        stats = database.get_professors_stats()
        return jsonify(stats)
        
    except Exception as e:
        logging.error(f"Error getting stats: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500
        
@professor_bp.route('/api/colleges', methods=['GET'])
def api_get_colleges():
    """Get list of unique colleges with professor counts for filtering"""
    try:
        # Get college list directly from database
        colleges = database.get_all_colleges()
        
        # Sort alphabetically
        colleges.sort(key=lambda x: x['name'])
        
        return jsonify({
            'colleges': colleges,
            'total': len(colleges)
        })
        
    except Exception as e:
        logging.error(f"Error getting college list: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500
        
@professor_bp.route('/api/domains', methods=['GET'])
def api_get_domains():
    """Get list of all domains with professor counts"""
    try:
        # Get domain list directly from database
        domains = database.get_all_domains()
        
        # Sort alphabetically
        domains.sort(key=lambda x: x['name'])
        
        return jsonify({
            'domains': domains,
            'total': len(domains)
        })
        
    except Exception as e:
        logging.error(f"Error getting domain list: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500
        
@professor_bp.route('/api/citations/status', methods=['GET'])
def api_get_citations_status():
    """Get status information about the citations cache"""
    try:
        # Get citation data from cache
        citations_cache = get_cached_citations()
        
        if not citations_cache:
            return jsonify({
                'status': 'empty',
                'count': 0,
                'message': 'Citations cache is empty'
            })
        
        # Count professors with citation data
        professors_with_citations = len([p for p in citations_cache.values() if p.get('citations', 0) > 0])
        
        # Get timestamp of oldest and newest cache entry
        timestamps = [entry.get('timestamp', 0) for entry in citations_cache.values() if 'timestamp' in entry]
        oldest = min(timestamps) if timestamps else 0
        newest = max(timestamps) if timestamps else 0
        
        # Calculate age in hours
        current_time = time.time()
        oldest_age_hours = round((current_time - oldest) / 3600, 2) if oldest else 0
        newest_age_hours = round((current_time - newest) / 3600, 2) if newest else 0
        
        # Get extraction status
        extraction_status = get_extraction_status()
        
        return jsonify({
            'status': 'available',
            'total_professors': len(citations_cache),
            'professors_with_citations': professors_with_citations,
            'oldest_entry_age_hours': oldest_age_hours,
            'newest_entry_age_hours': newest_age_hours,
            'cache_complete': professors_with_citations > 0,
            'extraction_running': extraction_status.get('running', False),
            'extraction_time_seconds': extraction_status.get('running_time_seconds', 0)
        })
        
    except Exception as e:
        logging.error(f"Error getting citations status: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500
        
@professor_bp.route('/api/citations/id-mapping', methods=['GET'])
def api_get_id_mapping():
    """Get the mapping between database and JSON IDs"""
    try:
        # Get the ID mapping
        id_mapping = get_id_mapping()
        
        return jsonify({
            'status': 'success',
            'count': len(id_mapping),
            'mappings': id_mapping
        })
        
    except Exception as e:
        logging.error(f"Error getting ID mapping: {str(e)}")
        import traceback
        logging.error(traceback.format_exc())
        return jsonify({'error': 'Internal server error'}), 500

@professor_bp.route('/api/citations/refresh', methods=['POST'])
def api_refresh_citations():
    """Manually trigger citation extraction"""
    try:
        import sys
        import traceback
        
        # Import directly from file
        from extract_citations import start_background_extraction, extract_and_cache_citations
        
        # Log some information
        logging.info("Starting citation extraction from API endpoint")
        
        try:
            # Try direct extraction for debugging
            if request.args.get('direct', '').lower() == 'true':
                logging.info("Running direct citation extraction (not in background)")
                result = extract_and_cache_citations()
                return jsonify({
                    'status': 'completed',
                    'message': 'Citation extraction completed directly',
                    'count': len(result),
                    'timestamp': time.time()
                })
            else:
                # Start background extraction
                thread = start_background_extraction()
                logging.info(f"Started background extraction thread: {thread}")
                
                return jsonify({
                    'status': 'started',
                    'message': 'Citation extraction started in background',
                    'timestamp': time.time()
                })
        except Exception as e:
            logging.error(f"Error in extraction process: {e}")
            logging.error(traceback.format_exc())
            return jsonify({
                'status': 'error',
                'message': f'Citation extraction error: {str(e)}',
                'traceback': traceback.format_exc(),
                'timestamp': time.time()
            }), 500
        
    except Exception as e:
        logging.error(f"Error refreshing citations: {str(e)}")
        logging.error(traceback.format_exc())
        return jsonify({
            'error': 'Internal server error', 
            'message': str(e),
            'traceback': traceback.format_exc()
        }), 500