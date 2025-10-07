"""
Professor API routes for Flask application.
This module contains all Flask routes related to professor management using Excel data.
"""

from flask import Blueprint, request, jsonify
from domain_expertise_analyzer import DomainExpertiseAnalyzer
import logging
import time
import os
import sys
import pandas as pd
import re
import json
from gemma_service import parse_search_query_with_gemma, analyze_project_description

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

# Excel data cache to avoid reading the file repeatedly
excel_data_cache = None
excel_last_read_time = 0
CACHE_TIMEOUT = 300  # 5 minutes

def find_excel_file():
    """Find the Excel file in the current or parent directories"""
    # Look in the current directory
    paths_to_try = [
        os.path.join(os.getcwd(), 'prof.xlsx'),
        os.path.join(os.getcwd(), 'sirs.xlsx'),
        os.path.join(os.path.dirname(os.getcwd()), 'prof.xlsx'),
        os.path.join(os.path.dirname(os.getcwd()), 'sirs.xlsx')
    ]
    
    for path in paths_to_try:
        if os.path.exists(path):
            return path
            
    # If not found, return the default path
    return os.path.join(os.getcwd(), 'prof.xlsx')

def load_teachers_data():
    """Load teachers data from Excel file"""
    global excel_data_cache, excel_last_read_time
    
    current_time = time.time()
    
    # Return cached data if it exists and is fresh
    if excel_data_cache is not None and current_time - excel_last_read_time < CACHE_TIMEOUT:
        # Add a sample Google Scholar URL for testing if not already added
        if excel_data_cache and len(excel_data_cache) > 1 and not excel_data_cache[1].get('google_scholar_url'):
            excel_data_cache[1]['google_scholar_url'] = 'https://scholar.google.com/citations?user=m8dFEawAAAAJ'
            excel_data_cache[1]['has_google_scholar'] = True
        return excel_data_cache
    
    try:
        # Find Excel file
        excel_path = find_excel_file()
        logger.info(f"Loading Excel data from: {excel_path}")
            
        # Read the Excel file
        df = pd.read_excel(excel_path)
        
        # Convert DataFrame to list of dictionaries
        teachers = []
        for i, row in df.iterrows():
            try:
                # Skip empty rows
                if (('Teacher Name' in df.columns and pd.isna(row['Teacher Name'])) and 
                    ('College' in df.columns and pd.isna(row['College']))):
                    continue
                
                # Create teacher dictionary with flexible column mappings
                teacher = {'id': i + 1}  # 1-based index for IDs
                
                # Map columns with different possible names
                name_cols = ['Teacher Name', 'Name', 'Professor Name', 'Faculty Name']
                college_cols = ['College', 'Institution', 'University']
                email_cols = ['College Email Id', 'Email', 'Email Id']
                domain_cols = ['Domain Expertise', 'Expertise', 'Research Areas', 'Specialization']
                thesis_cols = ['Ph D Thesis', 'PhD Thesis', 'Thesis']
                g_scholar_cols = ['Google Scholar URL', 'Google Scholar', 'Scholar URL']
                s_scholar_cols = ['Semantic Scholar Link', 'Semantic Scholar URL']
                
                # Try different column names
                for col_list, key in [
                    (name_cols, 'name'),
                    (college_cols, 'college'),
                    (email_cols, 'email'),
                    (domain_cols, 'domain_expertise'),
                    (thesis_cols, 'phd_thesis'),
                    (g_scholar_cols, 'google_scholar_url'),
                    (s_scholar_cols, 'semantic_scholar_url')
                ]:
                    for col in col_list:
                        if col in df.columns and not pd.isna(row[col]):
                            teacher[key] = str(row[col])
                            break
                    if key not in teacher:
                        teacher[key] = ''
                
                teachers.append(teacher)
            except Exception as row_error:
                logger.error(f"Error processing row {i}: {row_error}")
                continue
        
        # Update cache
        excel_data_cache = teachers
        excel_last_read_time = current_time
        
        logger.info(f"✅ Successfully loaded {len(teachers)} teachers from Excel")
        return teachers
    except Exception as e:
        logger.error(f"❌ Error loading teachers data from Excel: {e}")
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
        teachers = load_teachers_data()
        
        # Filter teachers by domain expertise
        experts = []
        for teacher in teachers:
            if teacher.get('domain_expertise'):
                domains = [d.strip().lower() for d in teacher['domain_expertise'].split(',')]
                if domain.lower() in domains:
                    experts.append(teacher)
        
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
        
        teachers = load_teachers_data()
        
        # Simple keyword search as fallback
        keywords = query.lower().split()
        filtered_teachers = []
        
        for teacher in teachers:
            text_to_search = f"{teacher.get('name', '')} {teacher.get('domain_expertise', '')} {teacher.get('bio', '')} {teacher.get('phd_thesis', '')}".lower()
            
            score = 0
            for keyword in keywords:
                if keyword in text_to_search:
                    score += 1
            
            if score > 0:
                teacher_copy = teacher.copy()
                teacher_copy['relevance_score'] = score
                filtered_teachers.append(teacher_copy)
        
        # Sort by relevance score
        filtered_teachers.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
        
        return jsonify({
            'teachers': filtered_teachers[:50],  # Limit to top 50 results
            'total_results': len(filtered_teachers),
            'query': query
        })
        
    except Exception as e:
        logging.error(f"Error in AI search: {str(e)}")
        return jsonify({'teachers': [], 'error': str(e)}), 500

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
        teachers = load_teachers_data()
        matching_teachers = []
        
        required_expertise = analysis.get('required_expertise', [])
        
        for teacher in teachers:
            if not teacher.get('domain_expertise'):
                continue
                
            teacher_domains = [d.strip().lower() for d in teacher['domain_expertise'].split(',')]
            
            # Calculate match percentage
            matches = 0
            matching_domains = []
            
            for expertise in required_expertise:
                expertise_lower = expertise.lower()
                for domain in teacher_domains:
                    if expertise_lower in domain or domain in expertise_lower:
                        matches += 1
                        matching_domains.append(expertise)
                        break
            
            if matches > 0:
                match_percentage = int((matches / len(required_expertise)) * 100)
                
                teacher_match = teacher.copy()
                teacher_match['match_percentage'] = match_percentage
                teacher_match['matching_domains'] = matching_domains
                
                matching_teachers.append(teacher_match)
        
        # Sort by match percentage
        matching_teachers.sort(key=lambda x: x['match_percentage'], reverse=True)
        
        return jsonify({
            'analysis': analysis,
            'teachers': matching_teachers[:20],  # Top 20 matches
            'total_matches': len(matching_teachers)
        })
        
    except Exception as e:
        logging.error(f"Error in project analysis: {str(e)}")
        return jsonify({'error': str(e)}), 500

@professor_bp.route('/api/teachers', methods=['GET'])
def api_get_all_teachers():
    """API endpoint to get all teachers from Excel data with optional filtering"""
    try:
        # Get query parameters
        limit = request.args.get('limit', type=int)
        college = request.args.get('college', '').strip()
        
        # Load teacher data
        teachers = load_teachers_data()
        
        if not teachers:
            return jsonify({'teachers': [], 'total_count': 0, 'message': 'No teachers found'})
        
        # Filter by college if specified
        if college:
            teachers = [t for t in teachers if t.get('college', '').strip().lower() == college.lower()]
            
        # Calculate total before applying limit
        total_count = len(teachers)
            
        # Apply limit if specified
        if limit and limit > 0:
            teachers = teachers[:limit]
        
        # Add row numbers and ensure required fields
        for i, teacher in enumerate(teachers, 1):
            teacher['row_number'] = i
            
            # Ensure required fields exist
            teacher.setdefault('id', i)
            teacher.setdefault('has_google_scholar', bool(teacher.get('google_scholar_url')))
            teacher.setdefault('has_semantic_scholar', bool(teacher.get('semantic_scholar_url')))
        
        return jsonify({
            'teachers': teachers,
            'total_count': total_count,
            'filtered_count': len(teachers),
            'message': f'Successfully loaded {len(teachers)} teachers' + (f' from college {college}' if college else '')
        })
        
    except Exception as e:
        logging.error(f"Error fetching teachers: {str(e)}")
        return jsonify({'teachers': [], 'total_count': 0, 'error': 'Internal error'}), 500

@professor_bp.route('/api/teachers/<int:teacher_id>', methods=['GET'])
def api_get_teacher_details(teacher_id):
    """Get detailed information about a specific teacher"""
    try:
        teachers = load_teachers_data()
        
        # Find teacher by ID or index
        teacher = None
        for t in teachers:
            if t.get('id') == teacher_id or teachers.index(t) + 1 == teacher_id:
                teacher = t
                break
        
        if not teacher:
            return jsonify({'error': 'Teacher not found'}), 404
        
        # Enhance with scholar data if available and enabled
        if SCHOLAR_ENABLED:
            try:
                scholar_data = None
                if teacher.get('google_scholar_url'):
                    scholar_data = extract_scholar_data_with_spacy(teacher['google_scholar_url'])
                
                if scholar_data:
                    teacher['scholar_data'] = scholar_data
                    
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
                    teacher['academic_data'] = academic_data
                    
            except Exception as e:
                logging.error(f"Error extracting scholar data: {str(e)}")
        
        return jsonify(teacher)
        
    except Exception as e:
        logging.error(f"Error fetching teacher details: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@professor_bp.route('/api/teachers/stats', methods=['GET'])
def api_get_teachers_stats():
    """Get statistics about the teachers database"""
    try:
        teachers = load_teachers_data()
        
        stats = {
            'total_teachers': len(teachers),
            'with_google_scholar': sum(1 for t in teachers if t.get('google_scholar_url')),
            'with_semantic_scholar': sum(1 for t in teachers if t.get('semantic_scholar_url')),
            'with_profile_picture': sum(1 for t in teachers if t.get('profile_picture_url') or t.get('scholar_profile_picture')),
            'colleges': len(set(t.get('college') for t in teachers if t.get('college'))),
            'domains': len(set(domain.strip() for t in teachers if t.get('domain_expertise') for domain in t['domain_expertise'].split(','))),
        }
        
        return jsonify(stats)
        
    except Exception as e:
        logging.error(f"Error getting stats: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500
        
def normalize_college_name(name):
    """Normalize college name to avoid duplicates"""
    if not name:
        return ""
    
    # Convert to lowercase for comparison
    name = name.lower().strip()
    
    # Remove trailing punctuation
    if name and name[-1] in '`.,;:':
        name = name[:-1]
    
    # Common abbreviations and variations
    if name in ['vit', 'vit vellore', 'vit-vellore', 'vit,vellore']:
        return "Vellore Institute of Technology"
    
    if name in ['vit chennai', 'vit university chennai']:
        return "Vellore Institute of Technology, Chennai"
        
    if name in ['srmist', 'srm university']:
        return "SRM Institute of Science and Technology"
        
    if name in ['rvce', 'rv college of engineerin', 'rv college of engineering']:
        return "RV College of Engineering"
        
    if name in ['psg tech', 'psg college of technology, coimbatore']:
        return "PSG College of Technology"
    
    # Return the original name if no normalization needed
    return name

@professor_bp.route('/api/colleges', methods=['GET'])
def api_get_colleges():
    """Get list of unique colleges with teacher counts for filtering"""
    try:
        teachers = load_teachers_data()
        
        # Count teachers per college
        college_counts = {}
        for teacher in teachers:
            college = teacher.get('college', '').strip()
            if college:
                # Normalize college name
                normalized = normalize_college_name(college)
                college_counts[normalized] = college_counts.get(normalized, 0) + 1
        
        # Format as list of objects
        colleges = [
            {'name': college, 'count': count}
            for college, count in college_counts.items()
        ]
        
        # Sort alphabetically
        colleges.sort(key=lambda x: x['name'])
        
        return jsonify({
            'colleges': colleges,
            'total': len(colleges)
        })
        
    except Exception as e:
        logging.error(f"Error getting college list: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500