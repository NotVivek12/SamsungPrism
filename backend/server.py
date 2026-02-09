"""
Minimal Flask server for professor data
This serves the professor data to the React frontend without complex dependencies
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import sqlite3
import json

app = Flask(__name__)
CORS(app)

def get_db_connection():
    """Get database connection"""
    conn = sqlite3.connect('professors.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/api/professors', methods=['GET'])
def get_professors():
    """Get all professors"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, name, domain, institute, email, bio, education, experience, 
                   projects, research_papers, citations, h_index, i10_index, 
                   total_publications, research_interests, current_affiliation
            FROM professors
        ''')
        
        professors = []
        for row in cursor.fetchall():
            professor = {
                'id': row['id'],
                'name': row['name'],
                'domain': row['domain'],
                'institute': row['institute'],
                'email': row['email'],
                'bio': row['bio'],
                'education': row['education'],
                'experience': row['experience'],
                'projects': json.loads(row['projects']) if row['projects'] else [],
                'researchPapers': json.loads(row['research_papers']) if row['research_papers'] else [],
                'citations': row['citations'],
                'hIndex': row['h_index'],
                'i10Index': row['i10_index'],
                'totalPublications': row['total_publications'],
                'researchInterests': json.loads(row['research_interests']) if row['research_interests'] else [],
                'currentAffiliation': row['current_affiliation']
            }
            professors.append(professor)
        
        conn.close()
        return jsonify(professors)
    except Exception as e:
        print(f"Error fetching professors: {str(e)}")
        return jsonify({"error": "Failed to fetch professors"}), 500

@app.route('/api/professors/<int:professor_id>', methods=['GET'])
def get_professor(professor_id):
    """Get a specific professor by ID"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, name, domain, institute, email, bio, education, experience, 
                   projects, research_papers, citations, h_index, i10_index, 
                   total_publications, research_interests, current_affiliation
            FROM professors WHERE id = ?
        ''', (professor_id,))
        
        row = cursor.fetchone()
        if not row:
            return jsonify({"error": "Professor not found"}), 404
        
        professor = {
            'id': row['id'],
            'name': row['name'],
            'domain': row['domain'],
            'institute': row['institute'],
            'email': row['email'],
            'bio': row['bio'],
            'education': row['education'],
            'experience': row['experience'],
            'projects': json.loads(row['projects']) if row['projects'] else [],
            'researchPapers': json.loads(row['research_papers']) if row['research_papers'] else [],
            'citations': row['citations'],
            'hIndex': row['h_index'],
            'i10Index': row['i10_index'],
            'totalPublications': row['total_publications'],
            'researchInterests': json.loads(row['research_interests']) if row['research_interests'] else [],
            'currentAffiliation': row['current_affiliation']
        }
        
        conn.close()
        return jsonify(professor)
    except Exception as e:
        print(f"Error fetching professor {professor_id}: {str(e)}")
        return jsonify({"error": "Failed to fetch professor"}), 500

@app.route('/api/professors/search', methods=['GET'])
def search_professors():
    """Search professors by domain, name, or research interests"""
    query = request.args.get('q', '').lower()
    
    if not query:
        return jsonify([])
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, name, domain, institute, email, bio, education, experience, 
                   projects, research_papers, citations, h_index, i10_index, 
                   total_publications, research_interests, current_affiliation
            FROM professors 
            WHERE LOWER(name) LIKE ? OR LOWER(domain) LIKE ? OR LOWER(research_interests) LIKE ?
        ''', (f'%{query}%', f'%{query}%', f'%{query}%'))
        
        professors = []
        for row in cursor.fetchall():
            professor = {
                'id': row['id'],
                'name': row['name'],
                'domain': row['domain'],
                'institute': row['institute'],
                'email': row['email'],
                'bio': row['bio'],
                'education': row['education'],
                'experience': row['experience'],
                'projects': json.loads(row['projects']) if row['projects'] else [],
                'researchPapers': json.loads(row['research_papers']) if row['research_papers'] else [],
                'citations': row['citations'],
                'hIndex': row['h_index'],
                'i10Index': row['i10_index'],
                'totalPublications': row['total_publications'],
                'researchInterests': json.loads(row['research_interests']) if row['research_interests'] else [],
                'currentAffiliation': row['current_affiliation']
            }
            professors.append(professor)
        
        conn.close()
        return jsonify(professors)
    except Exception as e:
        print(f"Error searching professors: {str(e)}")
        return jsonify({"error": "Failed to search professors"}), 500

@app.route('/api/professors/stats', methods=['GET'])
def get_stats():
    """Get professor statistics"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Total professors
        cursor.execute('SELECT COUNT(*) FROM professors')
        total_professors = cursor.fetchone()[0]
        
        # Professors by domain
        cursor.execute('''
            SELECT domain, COUNT(*) 
            FROM professors 
            WHERE domain IS NOT NULL AND domain != ''
            GROUP BY domain 
            ORDER BY COUNT(*) DESC
        ''')
        domains = dict(cursor.fetchall())
        
        # Top cited professors
        cursor.execute('''
            SELECT name, citations 
            FROM professors 
            ORDER BY citations DESC 
            LIMIT 10
        ''')
        top_cited = [{'name': row['name'], 'citations': row['citations']} for row in cursor.fetchall()]
        
        conn.close()
        
        return jsonify({
            'total_professors': total_professors,
            'domains': domains,
            'top_cited': top_cited
        })
    except Exception as e:
        print(f"Error fetching stats: {str(e)}")
        return jsonify({"error": "Failed to fetch statistics"}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy", 
        "message": "Professor API is running",
        "total_professors": get_professor_count()
    })

def get_professor_count():
    """Get total professor count"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM professors')
        count = cursor.fetchone()[0]
        conn.close()
        return count
    except:
        return 0

if __name__ == '__main__':
    print("🚀 Starting Professor API Server...")
    print("📊 Serving professor data for React frontend")
    print(f"👥 Total professors in database: {get_professor_count()}")
    print("🔗 Server running on http://localhost:5000")
    print("📡 API endpoints:")
    print("   GET /api/professors - Get all professors")
    print("   GET /api/professors/search?q=<query> - Search professors")
    print("   GET /api/professors/stats - Get statistics")
    print("   GET /health - Health check")
    app.run(debug=True, host='0.0.0.0', port=5000)