"""
Professor management module for handling professor data, database operations, and API endpoints.
This module contains all professor-related functionality extracted from app.py.
"""

import os
import json
import logging
import sqlite3
from flask import request, jsonify
import pandas as pd

# Database configuration
DATABASE = 'professors.db'

def init_professors_db():
    """Initialize the database with professor-related tables"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS professors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            domain TEXT,
            institute TEXT,
            email TEXT,
            bio TEXT,
            education TEXT,
            experience TEXT,
            projects TEXT,  -- JSON string
            research_papers TEXT,  -- JSON string
            google_scholar_url TEXT,
            semantic_scholar_url TEXT,
            citations INTEGER DEFAULT 0,
            h_index INTEGER DEFAULT 0,
            i10_index INTEGER DEFAULT 0,
            total_publications INTEGER DEFAULT 0,
            research_interests TEXT,  -- JSON string
            current_affiliation TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS publications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            professor_id INTEGER,
            title TEXT,
            journal TEXT,
            year INTEGER,
            citations INTEGER DEFAULT 0,
            url TEXT,
            FOREIGN KEY (professor_id) REFERENCES professors (id)
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ Professor database initialized successfully")

def get_professors():
    """Get all professors"""
    try:
        conn = sqlite3.connect(DATABASE)
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
                'id': row[0],
                'name': row[1],
                'domain': row[2],
                'institute': row[3],
                'email': row[4],
                'bio': row[5],
                'education': row[6],
                'experience': row[7],
                'projects': json.loads(row[8]) if row[8] else [],
                'researchPapers': json.loads(row[9]) if row[9] else [],
                'citations': row[10],
                'hIndex': row[11],
                'i10Index': row[12],
                'totalPublications': row[13],
                'researchInterests': json.loads(row[14]) if row[14] else [],
                'currentAffiliation': row[15]
            }
            professors.append(professor)
        
        conn.close()
        return jsonify(professors)
    except Exception as e:
        logging.error(f"Error fetching professors: {str(e)}")
        return jsonify({"error": "Failed to fetch professors"}), 500

def get_professor(professor_id):
    """Get a specific professor by ID"""
    try:
        conn = sqlite3.connect(DATABASE)
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
            'id': row[0],
            'name': row[1],
            'domain': row[2],
            'institute': row[3],
            'email': row[4],
            'bio': row[5],
            'education': row[6],
            'experience': row[7],
            'projects': json.loads(row[8]) if row[8] else [],
            'researchPapers': json.loads(row[9]) if row[9] else [],
            'citations': row[10],
            'hIndex': row[11],
            'i10Index': row[12],
            'totalPublications': row[13],
            'researchInterests': json.loads(row[14]) if row[14] else [],
            'currentAffiliation': row[15]
        }
        
        conn.close()
        return jsonify(professor)
    except Exception as e:
        logging.error(f"Error fetching professor {professor_id}: {str(e)}")
        return jsonify({"error": "Failed to fetch professor"}), 500

def search_professors():
    """Search professors by domain, name, or research interests"""
    query = request.args.get('q', '').lower()
    
    if not query:
        return jsonify([])
    
    try:
        conn = sqlite3.connect(DATABASE)
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
                'id': row[0],
                'name': row[1],
                'domain': row[2],
                'institute': row[3],
                'email': row[4],
                'bio': row[5],
                'education': row[6],
                'experience': row[7],
                'projects': json.loads(row[8]) if row[8] else [],
                'researchPapers': json.loads(row[9]) if row[9] else [],
                'citations': row[10],
                'hIndex': row[11],
                'i10Index': row[12],
                'totalPublications': row[13],
                'researchInterests': json.loads(row[14]) if row[14] else [],
                'currentAffiliation': row[15]
            }
            professors.append(professor)
        
        conn.close()
        return jsonify(professors)
    except Exception as e:
        logging.error(f"Error searching professors: {str(e)}")
        return jsonify({"error": "Failed to search professors"}), 500

def save_professor_to_db(professor_data):
    """Save professor data to database"""
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        
        # Extract data with defaults
        name = professor_data.get('Teacher Name', '')
        domain = professor_data.get('Domain Expertise', '')
        institute = professor_data.get('College', '')
        email = professor_data.get('College Email', '')
        
        # Create bio from available data
        bio = f"Professor at {institute} specializing in {domain}."
        education = professor_data.get('PhD Thesis', '')
        experience = f"Expert in {domain}"
        
        # Handle scholar data
        google_scholar_data = professor_data.get('Google Scholar Data', {})
        semantic_scholar_data = professor_data.get('Semantic Scholar Data', {})
        
        citations = google_scholar_data.get('Citations', 0)
        h_index = google_scholar_data.get('h-index', 0)
        i10_index = google_scholar_data.get('i10-index', 0)
        total_publications = google_scholar_data.get('Total Publications', 0)
        research_interests = json.dumps(google_scholar_data.get('Research Interests', []))
        current_affiliation = google_scholar_data.get('Current Affiliation', institute)
        
        # Extract publications
        publications = google_scholar_data.get('Publications', [])
        research_papers = [pub.get('title', '') for pub in publications if pub.get('title')]
        
        projects = []  # Will be populated later as needed
        
        cursor.execute('''
            INSERT OR REPLACE INTO professors 
            (name, domain, institute, email, bio, education, experience, projects, 
             research_papers, google_scholar_url, semantic_scholar_url, citations, 
             h_index, i10_index, total_publications, research_interests, current_affiliation)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            name, domain, institute, email, bio, education, experience,
            json.dumps(projects), json.dumps(research_papers),
            professor_data.get('Google Scholar URL'),
            professor_data.get('Semantic Scholar Link'),
            citations, h_index, i10_index, total_publications,
            research_interests, current_affiliation
        ))
        
        professor_id = cursor.lastrowid
        
        # Save publications separately
        for pub in publications:
            if pub.get('title'):
                cursor.execute('''
                    INSERT INTO publications (professor_id, title, journal, year, citations, url)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    professor_id,
                    pub.get('title', ''),
                    pub.get('journal', ''),
                    pub.get('year', None),
                    pub.get('citations', 0),
                    pub.get('url', '')
                ))
        
        conn.commit()
        conn.close()
        return professor_id
        
    except Exception as e:
        logging.error(f"Error saving professor to database: {str(e)}")
        return None

def get_professor_publications(professor_id):
    """Get all publications for a specific professor"""
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT title, journal, year, citations, url
            FROM publications 
            WHERE professor_id = ?
            ORDER BY year DESC, citations DESC
        ''', (professor_id,))
        
        publications = []
        for row in cursor.fetchall():
            publication = {
                'title': row[0],
                'journal': row[1],
                'year': row[2],
                'citations': row[3],
                'url': row[4]
            }
            publications.append(publication)
        
        conn.close()
        return publications
    except Exception as e:
        logging.error(f"Error fetching publications for professor {professor_id}: {str(e)}")
        return []

def delete_professor(professor_id):
    """Delete a professor and their publications"""
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        
        # Delete publications first
        cursor.execute('DELETE FROM publications WHERE professor_id = ?', (professor_id,))
        
        # Delete professor
        cursor.execute('DELETE FROM professors WHERE id = ?', (professor_id,))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        logging.error(f"Error deleting professor {professor_id}: {str(e)}")
        return False

def update_professor(professor_id, professor_data):
    """Update professor information"""
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        
        # Build update query dynamically based on provided data
        update_fields = []
        values = []
        
        field_mapping = {
            'name': 'name',
            'domain': 'domain',
            'institute': 'institute',
            'email': 'email',
            'bio': 'bio',
            'education': 'education',
            'experience': 'experience',
            'projects': 'projects',
            'research_papers': 'research_papers',
            'google_scholar_url': 'google_scholar_url',
            'semantic_scholar_url': 'semantic_scholar_url',
            'citations': 'citations',
            'h_index': 'h_index',
            'i10_index': 'i10_index',
            'total_publications': 'total_publications',
            'research_interests': 'research_interests',
            'current_affiliation': 'current_affiliation'
        }
        
        for key, db_field in field_mapping.items():
            if key in professor_data:
                update_fields.append(f"{db_field} = ?")
                value = professor_data[key]
                
                # Handle JSON fields
                if key in ['projects', 'research_papers', 'research_interests'] and isinstance(value, (list, dict)):
                    value = json.dumps(value)
                
                values.append(value)
        
        if update_fields:
            update_fields.append("updated_at = CURRENT_TIMESTAMP")
            values.append(professor_id)
            
            query = f"UPDATE professors SET {', '.join(update_fields)} WHERE id = ?"
            cursor.execute(query, values)
            
            conn.commit()
            conn.close()
            return True
        
        conn.close()
        return False
    except Exception as e:
        logging.error(f"Error updating professor {professor_id}: {str(e)}")
        return False

def get_professors_stats():
    """Get statistics about professors in the database"""
    try:
        conn = sqlite3.connect(DATABASE)
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
        top_cited = [{'name': row[0], 'citations': row[1]} for row in cursor.fetchall()]
        
        # Total publications
        cursor.execute('SELECT COUNT(*) FROM publications')
        total_publications = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'total_professors': total_professors,
            'total_publications': total_publications,
            'domains': domains,
            'top_cited': top_cited
        }
    except Exception as e:
        logging.error(f"Error fetching professor statistics: {str(e)}")
        return None

# Sample professor data for testing
SAMPLE_PROFESSORS = [
    {
        'Teacher Name': 'Dr. Sarah Johnson',
        'Domain Expertise': 'Machine Learning',
        'College': 'Stanford University',
        'College Email': 'sarah.johnson@stanford.edu',
        'PhD Thesis': 'Deep Learning Applications in Computer Vision',
        'Google Scholar URL': 'https://scholar.google.com/citations?user=sample1',
        'Semantic Scholar Link': 'https://www.semanticscholar.org/author/sample1',
        'Google Scholar Data': {
            'Citations': 1250,
            'h-index': 25,
            'i10-index': 35,
            'Total Publications': 45,
            'Research Interests': ['Machine Learning', 'Computer Vision', 'Neural Networks'],
            'Current Affiliation': 'Stanford University',
            'Publications': [
                {
                    'title': 'Advanced Neural Networks for Image Recognition',
                    'journal': 'Nature Machine Intelligence',
                    'year': 2023,
                    'citations': 89,
                    'url': 'https://example.com/paper1'
                },
                {
                    'title': 'Deep Learning in Medical Imaging',
                    'journal': 'Medical Image Analysis',
                    'year': 2022,
                    'citations': 156,
                    'url': 'https://example.com/paper2'
                }
            ]
        }
    },
    {
        'Teacher Name': 'Dr. Michael Chen',
        'Domain Expertise': 'Cybersecurity',
        'College': 'MIT',
        'College Email': 'michael.chen@mit.edu',
        'PhD Thesis': 'Blockchain-based Security Protocols',
        'Google Scholar URL': 'https://scholar.google.com/citations?user=sample2',
        'Semantic Scholar Link': 'https://www.semanticscholar.org/author/sample2',
        'Google Scholar Data': {
            'Citations': 890,
            'h-index': 22,
            'i10-index': 28,
            'Total Publications': 38,
            'Research Interests': ['Cybersecurity', 'Blockchain', 'Cryptography'],
            'Current Affiliation': 'MIT',
            'Publications': [
                {
                    'title': 'Blockchain Security in IoT Networks',
                    'journal': 'IEEE Security & Privacy',
                    'year': 2023,
                    'citations': 67,
                    'url': 'https://example.com/paper3'
                }
            ]
        }
    },
    {
        'Teacher Name': 'Dr. Emily Rodriguez',
        'Domain Expertise': 'Data Science',
        'College': 'UC Berkeley',
        'College Email': 'emily.rodriguez@berkeley.edu',
        'PhD Thesis': 'Statistical Methods for Big Data Analytics',
        'Google Scholar URL': 'https://scholar.google.com/citations?user=sample3',
        'Semantic Scholar Link': 'https://www.semanticscholar.org/author/sample3',
        'Google Scholar Data': {
            'Citations': 756,
            'h-index': 19,
            'i10-index': 24,
            'Total Publications': 32,
            'Research Interests': ['Data Science', 'Statistics', 'Big Data'],
            'Current Affiliation': 'UC Berkeley',
            'Publications': [
                {
                    'title': 'Scalable Data Mining Algorithms',
                    'journal': 'Data Mining and Knowledge Discovery',
                    'year': 2023,
                    'citations': 43,
                    'url': 'https://example.com/paper4'
                }
            ]
        }
    }
]

def populate_sample_data():
    """Populate the database with sample professor data for testing"""
    try:
        for professor_data in SAMPLE_PROFESSORS:
            save_professor_to_db(professor_data)
        print(f"✅ Successfully populated database with {len(SAMPLE_PROFESSORS)} sample professors")
    except Exception as e:
        logging.error(f"Error populating sample data: {str(e)}")
        print(f"❌ Error populating sample data: {str(e)}")