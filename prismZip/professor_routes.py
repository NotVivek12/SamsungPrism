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

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create a Blueprint for professor routes
professor_bp = Blueprint('professors', __name__)

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
        
        # Load professor data
        professors = database.load_professors_data()
        
        if not professors:
            return jsonify({'professors': [], 'total_count': 0, 'message': 'No professors found'})
        
        # Filter by college if specified
        if college:
            professors = [p for p in professors if p.get('college', '').strip().lower() == college.lower()]
            
        # Calculate total before applying limit
        total_count = len(professors)
            
        # Apply limit if specified
        if limit and limit > 0:
            professors = professors[:limit]
        
        # Add row numbers
        for i, professor in enumerate(professors, 1):
            professor['row_number'] = i
        
        return jsonify({
            'professors': professors,
            'total_count': total_count,
            'filtered_count': len(professors),
            'message': f'Successfully loaded {len(professors)} professors' + (f' from college {college}' if college else '')
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