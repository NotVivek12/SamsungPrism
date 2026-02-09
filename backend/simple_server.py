"""
Simple Flask server to serve professor data
This starts the Flask API server for the React frontend
"""

from flask import Flask, jsonify
from flask_cors import CORS
from professors import get_professors, get_professor, search_professors, get_professors_stats

app = Flask(__name__)
CORS(app)

@app.route('/api/professors', methods=['GET'])
def api_get_professors():
    """Get all professors"""
    return get_professors()

@app.route('/api/professors/<int:professor_id>', methods=['GET'])
def api_get_professor(professor_id):
    """Get specific professor"""
    return get_professor(professor_id)

@app.route('/api/professors/search', methods=['GET'])
def api_search_professors():
    """Search professors"""
    return search_professors()

@app.route('/api/professors/stats', methods=['GET'])
def api_get_stats():
    """Get professor statistics"""
    return jsonify(get_professors_stats())

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "message": "Professor API is running"})

if __name__ == '__main__':
    print("🚀 Starting Professor API Server...")
    print("📊 Serving professor data for React frontend")
    print("🔗 Server will run on http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)