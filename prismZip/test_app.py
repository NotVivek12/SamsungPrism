"""
Simple Flask app tester for teacher extraction
"""

from flask import Flask, jsonify
from flask_cors import CORS
from auto_extract_teachers import auto_extract_teachers, check_database_status
import sqlite3

app = Flask(__name__)
CORS(app)

# Auto-extract teachers on startup
print("🚀 Starting Flask app with automatic teacher extraction...")
try:
    auto_extract_teachers()
    print("✅ Teacher extraction completed!")
except Exception as e:
    print(f"❌ Error during teacher extraction: {str(e)}")

@app.route('/api/teachers', methods=['GET'])
def get_teachers():
    """Get all teachers from database"""
    try:
        conn = sqlite3.connect('teachers.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, name, college, email, domain_expertise, 
                   has_google_scholar, has_semantic_scholar, row_number
            FROM teachers 
            ORDER BY name
        ''')
        
        teachers = []
        for row in cursor.fetchall():
            teachers.append({
                'id': row[0],
                'name': row[1],
                'college': row[2],
                'email': row[3],
                'domain_expertise': row[4],
                'has_google_scholar': bool(row[5]),
                'has_semantic_scholar': bool(row[6]),
                'row_number': row[7]
            })
        
        conn.close()
        
        return jsonify({
            'success': True,
            'teachers': teachers,
            'total_count': len(teachers)
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/teachers/status', methods=['GET'])
def get_status():
    """Get teacher database status"""
    try:
        if not check_database_status():
            return jsonify({
                'database_exists': False,
                'total_teachers': 0
            })
        
        conn = sqlite3.connect('teachers.db')
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM teachers')
        total_count = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM teachers WHERE has_google_scholar = 1')
        google_count = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM teachers WHERE has_semantic_scholar = 1')
        semantic_count = cursor.fetchone()[0]
        
        conn.close()
        
        return jsonify({
            'database_exists': True,
            'total_teachers': total_count,
            'with_google_scholar': google_count,
            'with_semantic_scholar': semantic_count
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("Starting test server on port 5001...")
    app.run(debug=True, host='0.0.0.0', port=5001)