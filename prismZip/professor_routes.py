"""
Professor API routes for Flask application.
This module contains all Flask routes related to professor management.
"""

from flask import Blueprint, request, jsonify
from professors import (
    get_professors, get_professor, search_professors, 
    save_professor_to_db, get_professor_publications,
    delete_professor, update_professor, get_professors_stats,
    populate_sample_data
)
from domain_expertise_analyzer import DomainExpertiseAnalyzer
import pandas as pd
import logging
import time
import os
from auto_extract_teachers import force_refresh_teachers, check_database_status
from gemma_service import parse_search_query_with_gemma, analyze_project_description

# Create a Blueprint for professor routes
professor_bp = Blueprint('professors', __name__)

# Try to import spaCy and related modules, but make them optional
try:
    from helpers import extract_scholar_data
    from scholar_extractor import extract_semantic_scholar_data, combine_scholar_data
    from google_scholar_extractor import extract_google_scholar_data
    SCHOLAR_ENABLED = True
except ImportError as e:
    print(f"Scholar extraction modules not available: {e}")
    SCHOLAR_ENABLED = False

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
        
    analyzer = DomainExpertiseAnalyzer()
    
    try:
        experts = analyzer.search_domain_experts(domain, min_level)
        statistics = analyzer.get_domain_statistics(domain)
        
        return jsonify({
            'success': True,
            'domain': domain,
            'experts': experts,
            'statistics': statistics
        })
    except Exception as e:
        return jsonify({
            'error': f'Failed to search domain experts: {str(e)}'
        }), 500

@professor_bp.route('/api/professors', methods=['GET'])
def api_get_professors():
    """API endpoint to get all professors"""
    return get_professors()

@professor_bp.route('/api/ai/parse-search', methods=['POST'])
def api_ai_parse_search():
    """Parse a natural language search query using Gemma (or fallback)."""
    try:
        data = request.get_json(silent=True) or {}
        query = (data.get('query') or '').strip()
        if not query:
            return jsonify({
                'error': 'query is required'
            }), 400

        result = parse_search_query_with_gemma(query)
        return jsonify({
            'success': True,
            'result': result
        })
    except Exception as e:
        logging.error(f"AI parse search failed: {e}")
        return jsonify({'success': False, 'error': 'Internal error'}), 500

@professor_bp.route('/api/project/analyze', methods=['POST'])
def api_analyze_project():
    """
    Analyze a project description and find professors with matching expertise.
    
    This endpoint uses Gemma to analyze the project description, extract required expertise domains,
    and then finds professors whose expertise matches these domains.
    """
    try:
        data = request.get_json(silent=True) or {}
        description = (data.get('description') or '').strip()
        
        if not description:
            return jsonify({
                'error': 'Project description is required'
            }), 400
        
        # Analyze the project using Gemma
        analysis_result = analyze_project_description(description)
        
        if not analysis_result or not analysis_result.get('required_expertise'):
            return jsonify({
                'error': 'Failed to analyze project description',
                'analysis': analysis_result
            }), 500
        
        # Extract required expertise domains
        required_expertise = analysis_result.get('required_expertise', [])
        
        # Find professors with matching expertise
        import sqlite3
        conn = sqlite3.connect('teachers.db')
        cursor = conn.cursor()
        
        # Build a query to find teachers with matching domain expertise
        where_clauses = []
        params = []
        
        for domain in required_expertise:
            where_clauses.append("LOWER(domain_expertise) LIKE ? OR LOWER(research_interests) LIKE ?")
            domain_param = f"%{domain.lower()}%"
            params.extend([domain_param, domain_param])
        
        if not where_clauses:
            return jsonify({
                'analysis': analysis_result,
                'teachers': [],
                'message': 'No expertise domains identified in the project description'
            }), 200
        
        # Query database for matching professors
        sql = f"""
            SELECT id, name, college, email, profile_link, domain_expertise,
                   research_interests, phd_thesis, google_scholar_url, semantic_scholar_url
            FROM teachers
            WHERE {' OR '.join(where_clauses)}
            ORDER BY name
        """
        
        cursor.execute(sql, params)
        rows = cursor.fetchall()
        conn.close()
        
        # Prepare results
        teachers = []
        for t in rows:
            # Calculate matching score based on number of expertise areas matched
            matching_domains = []
            teacher_domains = []
            
            # Extract domains from domain_expertise and research_interests
            if t[5]:  # domain_expertise
                teacher_domains.extend([d.strip().lower() for d in t[5].split(',')])
            
            if t[6]:  # research_interests
                research_interests = t[6]
                # Handle both string and JSON array formats
                if research_interests.startswith('[') and research_interests.endswith(']'):
                    try:
                        import json
                        interests = json.loads(research_interests)
                        teacher_domains.extend([i.lower() for i in interests])
                    except:
                        teacher_domains.extend([d.strip().lower() for d in research_interests.split(',')])
                else:
                    teacher_domains.extend([d.strip().lower() for d in research_interests.split(',')])
            
            # Count matching domains
            for domain in required_expertise:
                if any(domain.lower() in td for td in teacher_domains):
                    matching_domains.append(domain)
            
            # Calculate match percentage
            match_percentage = round((len(matching_domains) / len(required_expertise)) * 100)
            
            teachers.append({
                'id': t[0],
                'name': t[1],
                'college': t[2],
                'email': t[3],
                'profile_link': t[4],
                'domain_expertise': t[5],
                'research_interests': t[6],
                'phd_thesis': t[7],
                'google_scholar_url': t[8],
                'semantic_scholar_url': t[9],
                'matching_domains': matching_domains,
                'match_percentage': match_percentage
            })
        
        # Sort by match percentage (descending)
        teachers.sort(key=lambda x: x['match_percentage'], reverse=True)
        
        return jsonify({
            'analysis': analysis_result,
            'teachers': teachers,
            'total_matches': len(teachers),
            'message': f'Found {len(teachers)} teachers with expertise matching the project requirements'
        }), 200
        
    except Exception as e:
        logging.error(f"Error analyzing project: {e}")
        return jsonify({
            'error': f'Project analysis failed: {str(e)}'
        }), 500


@professor_bp.route('/api/ai/search-teachers', methods=['POST'])
def api_ai_search_teachers():
    """Search teachers using AI-parsed keywords against multiple fields."""
    try:
        import sqlite3
        data = request.get_json(silent=True) or {}
        query = (data.get('query') or '').strip()
        if not query:
            return jsonify({'teachers': [], 'total_count': 0, 'message': 'Empty query'}), 400

        parsed = parse_search_query_with_gemma(query)
        keywords = [k.lower() for k in (parsed.get('keywords') or [])]
        if not keywords:
            keywords = [w for w in query.lower().split() if len(w) > 2]

        conn = sqlite3.connect('teachers.db')
        cursor = conn.cursor()

        # Build dynamic WHERE with LIKEs for each keyword across fields
        fields = [
            'name', 'college', 'email', 'domain_expertise', 'phd_thesis',
            'research_interests', 'affiliation', 'bio'
        ]

        where_clauses = []
        params = []
        for kw in keywords:
            like = f"%{kw}%"
            sub = ' OR '.join([f"LOWER({f}) LIKE ?" for f in fields])
            where_clauses.append(f"({sub})")
            params.extend([like] * len(fields))

        sql = f"""
            SELECT id, name, college, email, profile_link, domain_expertise,
                   phd_thesis, google_scholar_url, semantic_scholar_url,
                   timestamp, has_google_scholar, has_semantic_scholar,
                   row_number, extraction_timestamp, created_at,
                   profile_picture_url, scholar_profile_picture, bio, phone,
                   office_location, education, teaching_areas, awards,
                   college_publications, total_citations, h_index, i10_index,
                   research_interests, affiliation, recent_publications,
                   frequent_coauthors, semantic_h_index, total_papers,
                   semantic_citations, semantic_research_areas, notable_papers,
                   profile_data_updated
            FROM teachers
            { 'WHERE ' + ' AND '.join(where_clauses) if where_clauses else '' }
            ORDER BY name
        """

        cursor.execute(sql, params)
        rows = cursor.fetchall()
        conn.close()

        results = []
        for t in rows:
            results.append({
                'id': t[0], 'name': t[1], 'college': t[2], 'email': t[3],
                'profile_link': t[4], 'domain_expertise': t[5], 'phd_thesis': t[6],
                'google_scholar_url': t[7], 'semantic_scholar_url': t[8], 'timestamp': t[9],
                'has_google_scholar': bool(t[10]), 'has_semantic_scholar': bool(t[11]),
                'row_number': t[12], 'extraction_timestamp': t[13], 'created_at': t[14],
                'profile_picture_url': t[15], 'scholar_profile_picture': t[16], 'bio': t[17],
                'phone': t[18], 'office_location': t[19], 'education': t[20], 'teaching_areas': t[21],
                'awards': t[22], 'college_publications': t[23], 'total_citations': t[24],
                'h_index': t[25], 'i10_index': t[26], 'research_interests': t[27], 'affiliation': t[28],
                'recent_publications': t[29], 'frequent_coauthors': t[30], 'semantic_h_index': t[31],
                'total_papers': t[32], 'semantic_citations': t[33], 'semantic_research_areas': t[34],
                'notable_papers': t[35], 'profile_data_updated': t[36]
            })

        return jsonify({
            'teachers': results,
            'total_count': len(results),
            'keywords': keywords
        }), 200
    except Exception as e:
        logging.error(f"AI search teachers failed: {e}")
        return jsonify({'teachers': [], 'total_count': 0, 'error': 'Internal error'}), 500

@professor_bp.route('/api/teachers', methods=['GET'])
def api_get_all_teachers():
    """API endpoint to get all teachers from the teachers database"""
    try:
        import sqlite3
        
        # Connect to teachers database
        conn = sqlite3.connect('teachers.db')
        cursor = conn.cursor()
        
        # Fetch all teachers with enhanced profile data
        cursor.execute("""
            SELECT id, name, college, email, profile_link, domain_expertise, 
                   phd_thesis, google_scholar_url, semantic_scholar_url, 
                   timestamp, has_google_scholar, has_semantic_scholar, 
                   row_number, extraction_timestamp, created_at,
                   profile_picture_url, scholar_profile_picture, bio, phone, 
                   office_location, education, teaching_areas, awards, 
                   college_publications, total_citations, h_index, i10_index, 
                   research_interests, affiliation, recent_publications, 
                   frequent_coauthors, semantic_h_index, total_papers, 
                   semantic_citations, semantic_research_areas, notable_papers, 
                   profile_data_updated
            FROM teachers
            ORDER BY name
        """)
        
        teachers_data = cursor.fetchall()
        conn.close()
        
        # Convert to list of dictionaries with enhanced profile data
        teachers = []
        for teacher in teachers_data:
            teacher_dict = {
                'id': teacher[0],
                'name': teacher[1],
                'college': teacher[2],
                'email': teacher[3],
                'profile_link': teacher[4],
                'domain_expertise': teacher[5],
                'phd_thesis': teacher[6],
                'google_scholar_url': teacher[7],
                'semantic_scholar_url': teacher[8],
                'timestamp': teacher[9],
                'has_google_scholar': bool(teacher[10]),
                'has_semantic_scholar': bool(teacher[11]),
                'row_number': teacher[12],
                'extraction_timestamp': teacher[13],
                'created_at': teacher[14],
                # Enhanced profile data
                'profile_picture_url': teacher[15],
                'scholar_profile_picture': teacher[16],
                'bio': teacher[17],
                'phone': teacher[18],
                'office_location': teacher[19],
                'education': teacher[20],
                'teaching_areas': teacher[21],
                'awards': teacher[22],
                'college_publications': teacher[23],
                'total_citations': teacher[24],
                'h_index': teacher[25],
                'i10_index': teacher[26],
                'research_interests': teacher[27],
                'affiliation': teacher[28],
                'recent_publications': teacher[29],
                'frequent_coauthors': teacher[30],
                'semantic_h_index': teacher[31],
                'total_papers': teacher[32],
                'semantic_citations': teacher[33],
                'semantic_research_areas': teacher[34],
                'notable_papers': teacher[35],
                'profile_data_updated': teacher[36]
            }
            teachers.append(teacher_dict)
        
        return jsonify({
            'teachers': teachers,
            'total_count': len(teachers),
            'status': 'success',
            'message': f'Successfully retrieved {len(teachers)} teachers'
        }), 200
        
    except Exception as e:
        logging.error(f"Error fetching all teachers: {str(e)}")
        return jsonify({
            'error': f'Failed to fetch teachers: {str(e)}',
            'teachers': [],
            'total_count': 0
        }), 500

@professor_bp.route('/api/teachers/search', methods=['GET'])
def api_search_teachers():
    """API endpoint to search teachers"""
    try:
        import sqlite3
        
        query = request.args.get('q', '').strip()
        if not query:
            return jsonify({
                'teachers': [],
                'total_count': 0,
                'message': 'No search query provided'
            }), 400
        
        # Connect to teachers database
        conn = sqlite3.connect('teachers.db')
        cursor = conn.cursor()
        
        # Search in multiple fields with enhanced profile data
        search_query = f"%{query}%"
        cursor.execute("""
            SELECT id, name, college, email, profile_link, domain_expertise, 
                   phd_thesis, google_scholar_url, semantic_scholar_url, 
                   timestamp, has_google_scholar, has_semantic_scholar, 
                   row_number, extraction_timestamp, created_at,
                   profile_picture_url, scholar_profile_picture, bio, phone, 
                   office_location, education, teaching_areas, awards, 
                   college_publications, total_citations, h_index, i10_index, 
                   research_interests, affiliation, recent_publications, 
                   frequent_coauthors, semantic_h_index, total_papers, 
                   semantic_citations, semantic_research_areas, notable_papers, 
                   profile_data_updated
            FROM teachers
            WHERE name LIKE ? OR college LIKE ? OR email LIKE ? OR 
                  domain_expertise LIKE ? OR phd_thesis LIKE ? OR
                  research_interests LIKE ? OR affiliation LIKE ? OR bio LIKE ?
            ORDER BY name
        """, (search_query, search_query, search_query, search_query, 
              search_query, search_query, search_query, search_query))
        
        teachers_data = cursor.fetchall()
        conn.close()
        
        # Convert to list of dictionaries with enhanced profile data
        teachers = []
        for teacher in teachers_data:
            teacher_dict = {
                'id': teacher[0],
                'name': teacher[1],
                'college': teacher[2],
                'email': teacher[3],
                'profile_link': teacher[4],
                'domain_expertise': teacher[5],
                'phd_thesis': teacher[6],
                'google_scholar_url': teacher[7],
                'semantic_scholar_url': teacher[8],
                'timestamp': teacher[9],
                'has_google_scholar': bool(teacher[10]),
                'has_semantic_scholar': bool(teacher[11]),
                'row_number': teacher[12],
                'extraction_timestamp': teacher[13],
                'created_at': teacher[14],
                # Enhanced profile data
                'profile_picture_url': teacher[15],
                'scholar_profile_picture': teacher[16],
                'bio': teacher[17],
                'phone': teacher[18],
                'office_location': teacher[19],
                'education': teacher[20],
                'teaching_areas': teacher[21],
                'awards': teacher[22],
                'college_publications': teacher[23],
                'total_citations': teacher[24],
                'h_index': teacher[25],
                'i10_index': teacher[26],
                'research_interests': teacher[27],
                'affiliation': teacher[28],
                'recent_publications': teacher[29],
                'frequent_coauthors': teacher[30],
                'semantic_h_index': teacher[31],
                'total_papers': teacher[32],
                'semantic_citations': teacher[33],
                'semantic_research_areas': teacher[34],
                'notable_papers': teacher[35],
                'profile_data_updated': teacher[36]
            }
            teachers.append(teacher_dict)
        
        return jsonify({
            'teachers': teachers,
            'total_count': len(teachers),
            'status': 'success',
            'query': query,
            'message': f'Found {len(teachers)} teachers matching "{query}"'
        }), 200
        
    except Exception as e:
        logging.error(f"Error searching teachers: {str(e)}")
        return jsonify({
            'error': f'Failed to search teachers: {str(e)}',
            'teachers': [],
            'total_count': 0
        }), 500

@professor_bp.route('/api/teachers/extract-profiles', methods=['POST'])
def api_extract_profile_data():
    """API endpoint to extract and update profile data for all teachers"""
    try:
        from profile_data_extractor import ProfileDataExtractor
        
        # Check if there's a limit parameter
        limit = request.json.get('limit', 10) if request.json else 10
        
        # Initialize the extractor
        extractor = ProfileDataExtractor()
        
        # Get teachers that need profile data extraction
        import sqlite3
        conn = sqlite3.connect('teachers.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, name, profile_link, google_scholar_url, semantic_scholar_url 
            FROM teachers 
            WHERE (profile_link IS NOT NULL AND profile_link != '') 
               OR (google_scholar_url IS NOT NULL AND google_scholar_url != '')
               OR (semantic_scholar_url IS NOT NULL AND semantic_scholar_url != '')
            LIMIT ?
        ''', (limit,))
        
        teachers = cursor.fetchall()
        conn.close()
        
        if not teachers:
            return jsonify({
                'message': 'No teachers with profile links found',
                'processed_count': 0
            }), 200
        
        # Process teachers in background (for production, consider using celery)
        processed_count = 0
        errors = []
        
        for teacher_id, name, profile_link, google_scholar_url, semantic_scholar_url in teachers:
            try:
                # Extract all profile data
                profile_data = extractor.extract_all_profile_data(
                    name, profile_link, google_scholar_url, semantic_scholar_url
                )
                
                if profile_data and len(profile_data) > 1:  # More than just teacher_name
                    # Update database
                    conn = sqlite3.connect('teachers.db')
                    cursor = conn.cursor()
                    
                    # Prepare update query
                    update_fields = []
                    update_values = []
                    
                    for key, value in profile_data.items():
                        if key != 'teacher_name' and value is not None:
                            if isinstance(value, (list, dict)):
                                import json
                                value = json.dumps(value)
                            update_fields.append(f'{key} = ?')
                            update_values.append(value)
                    
                    if update_fields:
                        update_fields.append('profile_data_updated = CURRENT_TIMESTAMP')
                        update_values.append(teacher_id)
                        
                        update_query = f'''
                            UPDATE teachers 
                            SET {', '.join(update_fields)}
                            WHERE id = ?
                        '''
                        
                        cursor.execute(update_query, update_values)
                        conn.commit()
                        processed_count += 1
                    
                    conn.close()
                
                # Add small delay to be respectful
                time.sleep(1)
                
            except Exception as e:
                errors.append(f"Error processing {name}: {str(e)}")
                continue
        
        return jsonify({
            'message': f'Profile data extraction completed',
            'processed_count': processed_count,
            'total_found': len(teachers),
            'errors': errors if errors else None
        }), 200
        
    except Exception as e:
        logging.error(f"Error extracting profile data: {str(e)}")
        return jsonify({
            'error': f'Failed to extract profile data: {str(e)}'
        }), 500

@professor_bp.route('/api/teachers/<int:teacher_id>', methods=['GET'])
def api_get_teacher_details(teacher_id):
    """API endpoint to get detailed teacher information including comprehensive scholar data"""
    try:
        import sqlite3
        from google_scholar_extractor import extract_google_scholar_data
        from scholar_extractor import extract_semantic_scholar_data, combine_scholar_data
        
        # Connect to teachers database
        conn = sqlite3.connect('teachers.db')
        cursor = conn.cursor()
        
        # Fetch teacher data
        cursor.execute("""
            SELECT id, name, college, email, profile_link, domain_expertise, 
                   phd_thesis, google_scholar_url, semantic_scholar_url, timestamp
            FROM teachers WHERE id = ?
        """, (teacher_id,))
        
        teacher_row = cursor.fetchone()
        conn.close()
        
        if not teacher_row:
            return jsonify({'error': 'Teacher not found'}), 404
        
        # Structure teacher data
        teacher_data = {
            'id': teacher_row[0],
            'name': teacher_row[1],
            'college': teacher_row[2],
            'email': teacher_row[3],
            'profile_link': teacher_row[4],
            'domain_expertise': teacher_row[5],
            'phd_thesis': teacher_row[6],
            'google_scholar_url': teacher_row[7],
            'semantic_scholar_url': teacher_row[8],
            'timestamp': teacher_row[9],
            'academic_data': {
                'citations': 0,
                'h_index': 0,
                'i10_index': 0,
                'total_publications': 0,
                'recent_publications': [],
                'research_interests': [],
                'current_affiliation': teacher_row[2],
                'data_sources': []
            }
        }
        
        # Extract comprehensive academic data from scholar sources
        google_scholar_data = {}
        semantic_scholar_data = {}
        
        # Fetch Google Scholar data if URL is available
        if teacher_data['google_scholar_url'] and SCHOLAR_ENABLED:
            try:
                gs_result = extract_google_scholar_data(teacher_data['google_scholar_url'])
                if gs_result and 'Google Scholar Data' in gs_result:
                    google_scholar_data = gs_result['Google Scholar Data']
                    teacher_data['academic_data']['data_sources'].append('Google Scholar')
                    
                    # Extract key metrics
                    teacher_data['academic_data']['citations'] = google_scholar_data.get('Citations', 0)
                    teacher_data['academic_data']['h_index'] = google_scholar_data.get('h-index', 0)
                    teacher_data['academic_data']['i10_index'] = google_scholar_data.get('i10-index', 0)
                    teacher_data['academic_data']['total_publications'] = google_scholar_data.get('Total Publications', 0)
                    teacher_data['academic_data']['recent_publications'] = google_scholar_data.get('Publications', [])[:10]
                    teacher_data['academic_data']['research_interests'] = google_scholar_data.get('Research Interests', [])
                    
                    if google_scholar_data.get('Current Affiliation'):
                        teacher_data['academic_data']['current_affiliation'] = google_scholar_data.get('Current Affiliation')
                    
                    logging.info(f"Successfully extracted Google Scholar data for {teacher_data['name']}")
            except Exception as e:
                logging.error(f"Error extracting Google Scholar data for {teacher_data['name']}: {e}")
        
        # Fetch Semantic Scholar data if URL is available
        if teacher_data['semantic_scholar_url'] and SCHOLAR_ENABLED:
            try:
                ss_result = extract_semantic_scholar_data(teacher_data['semantic_scholar_url'])
                if ss_result and 'Semantic Scholar Data' in ss_result:
                    semantic_scholar_data = ss_result['Semantic Scholar Data']
                    teacher_data['academic_data']['data_sources'].append('Semantic Scholar')
                    
                    # If we don't have Google Scholar data, use Semantic Scholar data
                    if not google_scholar_data:
                        teacher_data['academic_data']['citations'] = semantic_scholar_data.get('Citations', 0)
                        teacher_data['academic_data']['h_index'] = semantic_scholar_data.get('h-index', 0)
                        teacher_data['academic_data']['total_publications'] = semantic_scholar_data.get('Total Publications', 0)
                        teacher_data['academic_data']['recent_publications'] = semantic_scholar_data.get('Publications', [])[:10]
                        teacher_data['academic_data']['research_interests'] = semantic_scholar_data.get('Research Topics', [])
                    
                    logging.info(f"Successfully extracted Semantic Scholar data for {teacher_data['name']}")
            except Exception as e:
                logging.error(f"Error extracting Semantic Scholar data for {teacher_data['name']}: {e}")
        
        # Combine data from both sources for better coverage
        if google_scholar_data and semantic_scholar_data and SCHOLAR_ENABLED:
            try:
                combined_data = combine_scholar_data(
                    {'Semantic Scholar Data': semantic_scholar_data}, 
                    {'Google Scholar Data': google_scholar_data}
                )
                
                if 'Semantic Scholar Data' in combined_data:
                    combined = combined_data['Semantic Scholar Data']
                    teacher_data['academic_data']['citations'] = combined.get('Citations', teacher_data['academic_data']['citations'])
                    teacher_data['academic_data']['h_index'] = combined.get('h-index', teacher_data['academic_data']['h_index'])
                    teacher_data['academic_data']['i10_index'] = combined.get('i10-index', teacher_data['academic_data']['i10_index'])
                    teacher_data['academic_data']['total_publications'] = combined.get('Total Publications', teacher_data['academic_data']['total_publications'])
                    teacher_data['academic_data']['recent_publications'] = combined.get('Publications', teacher_data['academic_data']['recent_publications'])[:10]
                    teacher_data['academic_data']['research_interests'] = combined.get('Research Topics', teacher_data['academic_data']['research_interests'])
                    teacher_data['academic_data']['data_sources'] = ['Combined Google Scholar & Semantic Scholar']
            except Exception as e:
                logging.error(f"Error combining scholar data for {teacher_data['name']}: {e}")
        
        # Add additional computed fields
        teacher_data['academic_data']['has_academic_data'] = (
            teacher_data['academic_data']['citations'] > 0 or 
            teacher_data['academic_data']['h_index'] > 0 or 
            len(teacher_data['academic_data']['recent_publications']) > 0
        )
        
        # Parse research domains from domain_expertise
        if teacher_data['domain_expertise']:
            domains = [domain.strip() for domain in teacher_data['domain_expertise'].split(',')]
            teacher_data['research_domains'] = domains
        else:
            teacher_data['research_domains'] = []
        
        return jsonify(teacher_data)
        
    except Exception as e:
        logging.error(f"Error getting teacher details: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@professor_bp.route('/api/teachers', methods=['GET'])
def api_get_teachers():
    """API endpoint to get all teachers from the database"""
    try:
        import sqlite3
        
        # Connect to teachers database
        conn = sqlite3.connect('teachers.db')
        cursor = conn.cursor()
        
        # Get search parameters
        search = request.args.get('search', '').lower()
        domain = request.args.get('domain', '').lower()
        limit = request.args.get('limit', 50, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        # Base query
        query = """
            SELECT id, name, college, email, domain_expertise, 
                   google_scholar_url, semantic_scholar_url
            FROM teachers WHERE 1=1
        """
        params = []
        
        # Add search filters
        if search:
            query += " AND (LOWER(name) LIKE ? OR LOWER(domain_expertise) LIKE ? OR LOWER(college) LIKE ?)"
            search_param = f"%{search}%"
            params.extend([search_param, search_param, search_param])
        
        if domain:
            query += " AND LOWER(domain_expertise) LIKE ?"
            params.append(f"%{domain}%")
        
        # Add ordering and pagination
        query += " ORDER BY name LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        
        cursor.execute(query, params)
        teachers = []
        
        for row in cursor.fetchall():
            teachers.append({
                'id': row[0],
                'name': row[1],
                'college': row[2],
                'email': row[3],
                'domain_expertise': row[4],
                'google_scholar_url': row[5],
                'semantic_scholar_url': row[6],
                'has_google_scholar': bool(row[5]),
                'has_semantic_scholar': bool(row[6])
            })
        
        # Get total count
        count_query = "SELECT COUNT(*) FROM teachers WHERE 1=1"
        count_params = []
        
        if search:
            count_query += " AND (LOWER(name) LIKE ? OR LOWER(domain_expertise) LIKE ? OR LOWER(college) LIKE ?)"
            search_param = f"%{search}%"
            count_params.extend([search_param, search_param, search_param])
        
        if domain:
            count_query += " AND LOWER(domain_expertise) LIKE ?"
            count_params.append(f"%{domain}%")
        
        cursor.execute(count_query, count_params)
        total_count = cursor.fetchone()[0]
        
        conn.close()
        
        return jsonify({
            'teachers': teachers,
            'total': total_count,
            'limit': limit,
            'offset': offset,
            'has_more': (offset + limit) < total_count
        })
        
    except Exception as e:
        logging.error(f"Error getting teachers: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@professor_bp.route('/api/professors/<int:professor_id>', methods=['GET'])
def api_get_professor(professor_id):
    """API endpoint to get a specific professor by ID"""
    return get_professor(professor_id)

@professor_bp.route('/api/professors/search', methods=['GET'])
def api_search_professors():
    """API endpoint to search professors by domain, name, or research interests"""
    return search_professors()

@professor_bp.route('/api/professors/<int:professor_id>/publications', methods=['GET'])
def api_get_professor_publications(professor_id):
    """API endpoint to get publications for a specific professor"""
    try:
        publications = get_professor_publications(professor_id)
        return jsonify(publications)
    except Exception as e:
        logging.error(f"Error fetching publications for professor {professor_id}: {str(e)}")
        return jsonify({"error": "Failed to fetch publications"}), 500

@professor_bp.route('/api/professors/<int:professor_id>', methods=['DELETE'])
def api_delete_professor(professor_id):
    """API endpoint to delete a professor"""
    try:
        if delete_professor(professor_id):
            return jsonify({"message": "Professor deleted successfully"})
        else:
            return jsonify({"error": "Failed to delete professor"}), 500
    except Exception as e:
        logging.error(f"Error deleting professor {professor_id}: {str(e)}")
        return jsonify({"error": "Failed to delete professor"}), 500

@professor_bp.route('/api/professors/<int:professor_id>', methods=['PUT'])
def api_update_professor(professor_id):
    """API endpoint to update professor information"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        if update_professor(professor_id, data):
            return jsonify({"message": "Professor updated successfully"})
        else:
            return jsonify({"error": "Failed to update professor"}), 500
    except Exception as e:
        logging.error(f"Error updating professor {professor_id}: {str(e)}")
        return jsonify({"error": "Failed to update professor"}), 500

@professor_bp.route('/api/professors/stats', methods=['GET'])
def api_get_professors_stats():
    """API endpoint to get professor statistics"""
    try:
        stats = get_professors_stats()
        if stats:
            return jsonify(stats)
        else:
            return jsonify({"error": "Failed to fetch statistics"}), 500
    except Exception as e:
        logging.error(f"Error fetching professor statistics: {str(e)}")
        return jsonify({"error": "Failed to fetch statistics"}), 500

@professor_bp.route('/api/professors/populate-sample', methods=['POST'])
def api_populate_sample_data():
    """API endpoint to populate database with sample professor data"""
    try:
        populate_sample_data()
        return jsonify({"message": "Sample data populated successfully"})
    except Exception as e:
        logging.error(f"Error populating sample data: {str(e)}")
        return jsonify({"error": "Failed to populate sample data"}), 500

@professor_bp.route('/extract', methods=['POST'])
def extract_data():
    """
    API endpoint to extract data from Google Scholar profiles based on an Excel file.
    Accepts optional list of teacher names to process only specific entries.
    Now saves extracted data to database for future use.
    """
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']
    teacher_names = request.form.getlist('teacher_names[]')
    
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if file:
        filename = file.filename
        if not filename.endswith(('.xlsx', '.xls')):
            return jsonify({"error": "Invalid file type. Only .xlsx and .xls files are supported."}), 400

        try:
            df = pd.read_excel(file)
            required_columns = [
                'Teacher Name', 
                'College', 
                'College Email Id', 
                'College Profile Link(please mention your profile link)',
                'Domain Expertise',
                'Ph D Thesis',
                'Google Scholar URL',
                'Semantic Scholar Link'
            ]
            
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                return jsonify({"error": f"Excel file is missing required columns: {', '.join(missing_columns)}"}), 400

            results = []
            saved_professors = []
            
            def _clean(value):
                """Convert pandas/NumPy NaN to None for JSON safety."""
                try:
                    # pandas.isna handles None, NaN, NaT
                    return None if pd.isna(value) else value
                except Exception:
                    return value
                    
            for index, row in df.iterrows():
                teacher_name = row['Teacher Name']
                if teacher_names and teacher_name not in teacher_names:
                    continue
                    
                teacher_data = {
                    'Teacher Name': _clean(teacher_name),
                    'College': _clean(row['College']),
                    'College Email': _clean(row['College Email Id']),
                    'College Profile': _clean(row['College Profile Link(please mention your profile link)']),
                    'Domain Expertise': _clean(row['Domain Expertise']),
                    'PhD Thesis': _clean(row['Ph D Thesis']),
                    'Google Scholar URL': _clean(row['Google Scholar URL']),
                    'Semantic Scholar Link': _clean(row['Semantic Scholar Link'])
                }
                
                scholar_url = row['Google Scholar URL']
                semantic_scholar_url = row['Semantic Scholar Link']

                empty_fields = [field for field, value in teacher_data.items() if pd.isna(value)]
                if empty_fields:
                    logging.warning(f"Row {index + 2} has empty fields: {', '.join(empty_fields)}")

                # Process Google Scholar data if enabled
                if SCHOLAR_ENABLED and not pd.isna(scholar_url):
                    try:
                        # Try new extraction method first
                        try:
                            logging.info(f"Using enhanced extraction method for Google Scholar: {scholar_url}")
                            scholar_data = extract_google_scholar_data(scholar_url)
                            teacher_data.update(scholar_data)
                            logging.info(f"Enhanced Google Scholar extraction successful for {teacher_name}")
                        except Exception as enhanced_error:
                            # Fall back to original method if new method fails
                            logging.warning(f"Enhanced extraction failed for {teacher_name}, trying original method: {str(enhanced_error)}")
                            scholar_data = extract_scholar_data(teacher_data['Teacher Name'], scholar_url)
                            teacher_data.update(scholar_data)
                            logging.info(f"Original Google Scholar extraction succeeded as fallback for {teacher_name}")
                    except Exception as e:
                        logging.error(f"Error processing Google Scholar data for row {index + 2}: {str(e)}")
                        teacher_data['Google Scholar Data'] = {
                            'status': 'error',
                            'reason': str(e),
                            'Citations': 0,
                            'h-index': 0,
                            'i10-index': 0,
                            'Total Publications': 0,
                            'Research Interests': [],
                            'Current Affiliation': 'Not available',
                            'Publications': []
                        }
                else:
                    teacher_data['Google Scholar Data'] = {
                        'status': 'skipped',
                        'reason': 'Missing Google Scholar URL or Scholar extraction disabled',
                        'Citations': 0,
                        'h-index': 0,
                        'i10-index': 0,
                        'Total Publications': 0,
                        'Research Interests': [],
                        'Current Affiliation': 'Not available',
                        'Publications': []
                    }

                # Process Semantic Scholar data if enabled
                if SCHOLAR_ENABLED and not pd.isna(semantic_scholar_url):
                    try:
                        # Import nlp here to avoid circular imports
                        import spacy
                        try:
                            nlp = spacy.load('en_core_web_sm')
                        except OSError:
                            from spacy.cli import download
                            download('en_core_web_sm')
                            nlp = spacy.load('en_core_web_sm')
                        
                        semantic_data = extract_semantic_scholar_data(semantic_scholar_url, nlp)
                        
                        # If Google Scholar data is available, combine citation metrics if needed
                        if 'Google Scholar Data' in teacher_data and not pd.isna(scholar_url):
                            semantic_data = combine_scholar_data(semantic_data, teacher_data)
                            
                        teacher_data.update(semantic_data)
                    except Exception as e:
                        logging.error(f"Error processing Semantic Scholar data for row {index + 2}: {str(e)}")
                        teacher_data['Semantic Scholar Data'] = {
                            'status': 'error',
                            'reason': str(e),
                            'Citations': 0,
                            'h-index': 0,
                            'Total Publications': 0,
                            'Current Affiliation': 'Not available',
                            'Research Topics': [],
                            'Publications': [],
                            'Research Trends': {},
                            'Citation Impact': {}
                        }
                else:
                    teacher_data['Semantic Scholar Data'] = {
                        'status': 'skipped',
                        'reason': 'Missing Semantic Scholar URL or Scholar extraction disabled',
                        'Citations': 0,
                        'h-index': 0,
                        'Total Publications': 0,
                        'Current Affiliation': 'Not available',
                        'Research Topics': [],
                        'Publications': [],
                        'Research Trends': {},
                        'Citation Impact': {}
                    }

                # Save to database
                professor_id = save_professor_to_db(teacher_data)
                if professor_id:
                    saved_professors.append({
                        'id': professor_id,
                        'name': teacher_data.get('Teacher Name'),
                        'status': 'saved'
                    })
                
                results.append(teacher_data)

                # Shorter delay between requests to improve performance
                if SCHOLAR_ENABLED:
                    time.sleep(int(os.getenv('REQUEST_DELAY', 10)))  

            response = {
                'extracted_data': results,
                'saved_professors': saved_professors,
                'total_processed': len(results),
                'total_saved': len(saved_professors)
            }
            
            return jsonify(response), 200

        except Exception as e:
            logging.error(f"Error processing file: {str(e)}")
            return jsonify({'error': f'File processing failed: {str(e)}'}), 500

# Teacher Data Management Endpoints

@professor_bp.route('/api/teachers/refresh', methods=['POST'])
def refresh_teachers():
    """Force refresh all teacher data from Excel file"""
    try:
        logging.info("Manual teacher data refresh requested")
        success = force_refresh_teachers()
        
        if success:
            # Get updated count
            import sqlite3
            conn = sqlite3.connect('teachers.db')
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM teachers')
            count = cursor.fetchone()[0]
            conn.close()
            
            return jsonify({
                'success': True,
                'message': f'Teacher data refreshed successfully! {count} teachers loaded.',
                'total_teachers': count
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': 'Failed to refresh teacher data'
            }), 500
            
    except Exception as e:
        logging.error(f"Error refreshing teacher data: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Teacher data refresh failed: {str(e)}'
        }), 500

@professor_bp.route('/api/teachers/status', methods=['GET'])
def get_teachers_status():
    """Get status of teacher database"""
    try:
        import sqlite3
        
        if not check_database_status():
            return jsonify({
                'database_exists': False,
                'total_teachers': 0,
                'message': 'Teacher database not initialized'
            }), 200
        
        conn = sqlite3.connect('teachers.db')
        cursor = conn.cursor()
        
        # Get basic counts
        cursor.execute('SELECT COUNT(*) FROM teachers')
        total_count = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM teachers WHERE has_google_scholar = 1')
        google_scholar_count = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM teachers WHERE has_semantic_scholar = 1')
        semantic_scholar_count = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM teachers WHERE domain_expertise != ""')
        with_expertise_count = cursor.fetchone()[0]
        
        # Get latest extraction timestamp
        cursor.execute('SELECT MAX(extraction_timestamp) FROM teachers')
        latest_extraction = cursor.fetchone()[0]
        
        conn.close()
        
        return jsonify({
            'database_exists': True,
            'total_teachers': total_count,
            'teachers_with_google_scholar': google_scholar_count,
            'teachers_with_semantic_scholar': semantic_scholar_count,
            'teachers_with_expertise': with_expertise_count,
            'latest_extraction': latest_extraction,
            'extraction_percentages': {
                'google_scholar': round((google_scholar_count / total_count * 100), 1) if total_count > 0 else 0,
                'semantic_scholar': round((semantic_scholar_count / total_count * 100), 1) if total_count > 0 else 0,
                'with_expertise': round((with_expertise_count / total_count * 100), 1) if total_count > 0 else 0
            }
        }), 200
        
    except Exception as e:
        logging.error(f"Error getting teacher status: {str(e)}")
        return jsonify({
            'error': f'Failed to get teacher status: {str(e)}'
        }), 500

@professor_bp.route('/api/teachers/refresh', methods=['POST'])
def api_refresh_teachers():
    """API endpoint to manually refresh teacher data from Excel"""
    try:
        # Force refresh teachers from Excel
        result = force_refresh_teachers()
        
        if result.get('success'):
            return jsonify({
                'status': 'success',
                'message': result.get('message', 'Teachers data refreshed successfully'),
                'teachers_processed': result.get('teachers_processed', 0),
                'timestamp': result.get('timestamp')
            }), 200
        else:
            return jsonify({
                'status': 'error',
                'message': result.get('error', 'Failed to refresh teachers data'),
                'error': result.get('error')
            }), 500
            
    except Exception as e:
        logging.error(f"Error refreshing teachers: {str(e)}")
        return jsonify({
            'error': f'Failed to refresh teachers: {str(e)}'
        }), 500