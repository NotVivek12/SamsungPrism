"""
Database connection and data access module.
This module contains functions to connect to the MySQL database and extract professor data.
"""

import logging
import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Database configuration
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'database': os.getenv('DB_NAME', 'prism_professors'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', ''),
    'port': int(os.getenv('DB_PORT', 3306)),
    'allow_local_infile': True
}

def get_connection():
    """Create and return a connection to the MySQL database"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        if connection.is_connected():
            logger.info("Connected to MySQL database")
            return connection
    except Error as e:
        logger.error(f"Error connecting to MySQL database: {e}")
        raise
    return None

def close_connection(connection, cursor=None):
    """Close database connection and cursor"""
    try:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()
            logger.info("MySQL connection closed")
    except Error as e:
        logger.error(f"Error closing MySQL connection: {e}")

def load_professors_data():
    """Load all professors data from the database"""
    connection = None
    cursor = None
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        
        # Query to join tables and get all professor data
        query = """
        SELECT p.PID as id, p.PName as name, p.CName as college, p.CMailId as email,
               p.Phd as phd_thesis, pl.GScholar as google_scholar_url, 
               pl.SScholar as semantic_scholar_url, pl.CProfile as profile_link,
               GROUP_CONCAT(DISTINCT d.DomainName SEPARATOR ' | ') as domain_expertise
        FROM professors p
        LEFT JOIN plink pl ON p.PID = pl.ProfID
        LEFT JOIN prof_domain pd ON p.PID = pd.ProfID
        LEFT JOIN domains d ON pd.DomainId = d.DomainID
        GROUP BY p.PID
        """
        
        cursor.execute(query)
        professors = cursor.fetchall()
        
        # Process the data
        for professor in professors:
            # Add additional fields
            professor['has_google_scholar'] = bool(professor.get('google_scholar_url'))
            professor['has_semantic_scholar'] = bool(professor.get('semantic_scholar_url'))
            
            # Extract domain expertise as a list
            if professor.get('domain_expertise'):
                expertise_list = [area.strip() for area in professor['domain_expertise'].split(' | ')]
                professor['expertise_array'] = expertise_list
            else:
                professor['expertise_array'] = []
        
        logger.info(f"✅ Successfully loaded {len(professors)} professors from database")
        return professors
        
    except Error as e:
        logger.error(f"❌ Error loading professors data from database: {e}")
        return []
    finally:
        close_connection(connection, cursor)

def get_professor_by_id(professor_id):
    """Get professor details by ID"""
    connection = None
    cursor = None
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        
        # Query for professor details
        query = """
        SELECT p.PID as id, p.PName as name, p.CName as college, p.CMailId as email,
               p.Phd as phd_thesis, pl.GScholar as google_scholar_url, 
               pl.SScholar as semantic_scholar_url, pl.CProfile as profile_link,
               GROUP_CONCAT(DISTINCT d.DomainName SEPARATOR ' | ') as domain_expertise
        FROM professors p
        LEFT JOIN plink pl ON p.PID = pl.ProfID
        LEFT JOIN prof_domain pd ON p.PID = pd.ProfID
        LEFT JOIN domains d ON pd.DomainId = d.DomainID
        WHERE p.PID = %s
        GROUP BY p.PID
        """
        
        cursor.execute(query, (professor_id,))
        professor = cursor.fetchone()
        
        if professor:
            # Add additional fields
            professor['has_google_scholar'] = bool(professor.get('google_scholar_url'))
            professor['has_semantic_scholar'] = bool(professor.get('semantic_scholar_url'))
            
            # Extract domain expertise as a list
            if professor.get('domain_expertise'):
                expertise_list = [area.strip() for area in professor['domain_expertise'].split(' | ')]
                professor['expertise_array'] = expertise_list
            else:
                professor['expertise_array'] = []
        
        return professor
        
    except Error as e:
        logger.error(f"❌ Error getting professor by ID: {e}")
        return None
    finally:
        close_connection(connection, cursor)

def get_professors_by_domain(domain):
    """Get professors with expertise in a specific domain"""
    connection = None
    cursor = None
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        
        # Query for professors by domain expertise
        query = """
        SELECT p.PID as id, p.PName as name, p.CName as college, p.CMailId as email,
               p.Phd as phd_thesis, pl.GScholar as google_scholar_url, 
               pl.SScholar as semantic_scholar_url, pl.CProfile as profile_link,
               GROUP_CONCAT(DISTINCT d.DomainName SEPARATOR ' | ') as domain_expertise
        FROM professors p
        LEFT JOIN plink pl ON p.PID = pl.ProfID
        LEFT JOIN prof_domain pd ON p.PID = pd.ProfID
        LEFT JOIN domains d ON pd.DomainId = d.DomainID
        WHERE d.DomainName LIKE %s
        GROUP BY p.PID
        """
        
        cursor.execute(query, (f'%{domain}%',))
        professors = cursor.fetchall()
        
        # Process the data
        for professor in professors:
            # Add additional fields
            professor['has_google_scholar'] = bool(professor.get('google_scholar_url'))
            professor['has_semantic_scholar'] = bool(professor.get('semantic_scholar_url'))
            
            # Extract domain expertise as a list
            if professor.get('domain_expertise'):
                expertise_list = [area.strip() for area in professor['domain_expertise'].split(' | ')]
                professor['expertise_array'] = expertise_list
            else:
                professor['expertise_array'] = []
        
        return professors
        
    except Error as e:
        logger.error(f"❌ Error getting professors by domain: {e}")
        return []
    finally:
        close_connection(connection, cursor)

def get_all_colleges():
    """Get list of all colleges with professor counts"""
    connection = None
    cursor = None
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        
        # Query for colleges and counts
        query = """
        SELECT CName as name, COUNT(PID) as count
        FROM professors
        GROUP BY CName
        ORDER BY CName
        """
        
        cursor.execute(query)
        colleges = cursor.fetchall()
        
        return colleges
        
    except Error as e:
        logger.error(f"❌ Error getting college list: {e}")
        return []
    finally:
        close_connection(connection, cursor)

def get_all_domains():
    """Get list of all domains"""
    connection = None
    cursor = None
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        
        # Query for domains
        query = """
        SELECT DomainID as id, DomainName as name, 
               COUNT(DISTINCT ProfID) as professor_count
        FROM domains d
        LEFT JOIN prof_domain pd ON d.DomainID = pd.DomainId
        GROUP BY DomainID, DomainName
        ORDER BY DomainName
        """
        
        cursor.execute(query)
        domains = cursor.fetchall()
        
        return domains
        
    except Error as e:
        logger.error(f"❌ Error getting domain list: {e}")
        return []
    finally:
        close_connection(connection, cursor)

def search_professors(query):
    """Search professors by keyword in name, college, or domain"""
    connection = None
    cursor = None
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        
        # Query to search professors
        search_query = """
        SELECT p.PID as id, p.PName as name, p.CName as college, p.CMailId as email,
               p.Phd as phd_thesis, pl.GScholar as google_scholar_url, 
               pl.SScholar as semantic_scholar_url, pl.CProfile as profile_link,
               GROUP_CONCAT(DISTINCT d.DomainName SEPARATOR ' | ') as domain_expertise
        FROM professors p
        LEFT JOIN plink pl ON p.PID = pl.ProfID
        LEFT JOIN prof_domain pd ON p.PID = pd.ProfID
        LEFT JOIN domains d ON pd.DomainId = d.DomainID
        WHERE p.PName LIKE %s OR p.CName LIKE %s OR d.DomainName LIKE %s
        GROUP BY p.PID
        """
        
        search_param = f'%{query}%'
        cursor.execute(search_query, (search_param, search_param, search_param))
        professors = cursor.fetchall()
        
        # Process the data
        for professor in professors:
            # Add additional fields
            professor['has_google_scholar'] = bool(professor.get('google_scholar_url'))
            professor['has_semantic_scholar'] = bool(professor.get('semantic_scholar_url'))
            
            # Extract domain expertise as a list
            if professor.get('domain_expertise'):
                expertise_list = [area.strip() for area in professor['domain_expertise'].split(' | ')]
                professor['expertise_array'] = expertise_list
            else:
                professor['expertise_array'] = []
        
        return professors
        
    except Error as e:
        logger.error(f"❌ Error searching professors: {e}")
        return []
    finally:
        close_connection(connection, cursor)

def get_professors_stats():
    """Get statistics about professors in the database"""
    connection = None
    cursor = None
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        
        stats = {}
        
        # Get total professors count
        cursor.execute("SELECT COUNT(*) as total FROM professors")
        result = cursor.fetchone()
        stats['total_professors'] = result['total']
        
        # Get count of professors with Google Scholar
        cursor.execute("SELECT COUNT(*) as count FROM plink WHERE GScholar IS NOT NULL AND GScholar != ''")
        result = cursor.fetchone()
        stats['with_google_scholar'] = result['count']
        
        # Get count of professors with Semantic Scholar
        cursor.execute("SELECT COUNT(*) as count FROM plink WHERE SScholar IS NOT NULL AND SScholar != ''")
        result = cursor.fetchone()
        stats['with_semantic_scholar'] = result['count']
        
        # Get count of unique colleges
        cursor.execute("SELECT COUNT(DISTINCT CName) as count FROM professors")
        result = cursor.fetchone()
        stats['colleges'] = result['count']
        
        # Get count of unique domains
        cursor.execute("SELECT COUNT(*) as count FROM domains")
        result = cursor.fetchone()
        stats['domains'] = result['count']
        
        return stats
        
    except Error as e:
        logger.error(f"❌ Error getting professor stats: {e}")
        return {}
    finally:
        close_connection(connection, cursor)