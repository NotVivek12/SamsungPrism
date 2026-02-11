"""
Script to migrate data from Excel to MySQL database.
This script reads data from an Excel file and inserts it into the MySQL database tables.
"""

import pandas as pd
import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database configuration
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'database': os.getenv('DB_NAME', 'prism_professors'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', ''),
    'port': int(os.getenv('DB_PORT', 3306))
}

def get_connection():
    """Create and return a connection to the MySQL database"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        if connection.is_connected():
            print("Connected to MySQL database")
            return connection
    except Error as e:
        print(f"Error connecting to MySQL database: {e}")
        raise
    return None

def close_connection(connection, cursor=None):
    """Close database connection and cursor"""
    try:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()
            print("MySQL connection closed")
    except Error as e:
        print(f"Error closing MySQL connection: {e}")

def migrate_data(excel_path):
    """Migrate data from Excel to MySQL database"""
    connection = None
    cursor = None
    try:
        # Read Excel file
        print(f"Reading Excel file: {excel_path}")
        df = pd.read_excel(excel_path)
        print(f"Successfully read {len(df)} rows from Excel")
        
        # Connect to MySQL database
        connection = get_connection()
        cursor = connection.cursor()
        
        # Process each row in the Excel file
        for index, row in df.iterrows():
            try:
                # Extract professor data
                name = str(row.get('name', row.get('Name', '')))
                college = str(row.get('college', row.get('College', row.get('institution', ''))))
                email = str(row.get('email', row.get('Email', '')))
                phd_thesis = str(row.get('phd_thesis', row.get('PhD Thesis', '')))
                
                # Clean up data - replace 'nan' with empty string
                if name.lower() == 'nan':
                    name = ''
                if college.lower() == 'nan':
                    college = ''
                if email.lower() == 'nan':
                    email = ''
                if phd_thesis.lower() == 'nan':
                    phd_thesis = ''
                
                # Skip empty rows
                if not name:
                    continue
                
                # Insert into professors table
                cursor.execute(
                    "INSERT INTO professors (PName, CName, CMailId, Phd) VALUES (%s, %s, %s, %s)",
                    (name, college, email, phd_thesis)
                )
                professor_id = cursor.lastrowid
                
                # Extract URLs
                google_scholar = str(row.get('google_scholar_url', row.get('Google Scholar URL', '')))
                semantic_scholar = str(row.get('semantic_scholar_url', row.get('Semantic Scholar URL', '')))
                profile_link = str(row.get('profile_link', row.get('Profile Link', '')))
                
                # Clean URLs
                if google_scholar.lower() == 'nan':
                    google_scholar = ''
                if semantic_scholar.lower() == 'nan':
                    semantic_scholar = ''
                if profile_link.lower() == 'nan':
                    profile_link = ''
                
                # Insert into plink table
                cursor.execute(
                    "INSERT INTO plink (ProfID, GScholar, SScholar, CProfile) VALUES (%s, %s, %s, %s)",
                    (professor_id, google_scholar, semantic_scholar, profile_link)
                )
                
                # Process domain expertise
                domain_expertise = str(row.get('domain_expertise', row.get('Domain Expertise', '')))
                if domain_expertise and domain_expertise.lower() != 'nan':
                    domains = [domain.strip() for domain in domain_expertise.split(',')]
                    
                    for domain in domains:
                        # Check if domain exists
                        cursor.execute("SELECT DomainID FROM domains WHERE DomainName = %s", (domain,))
                        result = cursor.fetchone()
                        
                        if result:
                            domain_id = result[0]
                        else:
                            # Insert new domain
                            cursor.execute("INSERT INTO domains (DomainName) VALUES (%s)", (domain,))
                            domain_id = cursor.lastrowid
                        
                        # Insert into prof_domain mapping table
                        cursor.execute(
                            "INSERT INTO prof_domain (ProfID, DomainId) VALUES (%s, %s)",
                            (professor_id, domain_id)
                        )
            
            except Exception as row_error:
                print(f"Error processing row {index}: {row_error}")
                continue
        
        # Commit changes
        connection.commit()
        print("Data migration completed successfully!")
        
    except Exception as e:
        print(f"Error during data migration: {e}")
        if connection:
            connection.rollback()
    finally:
        close_connection(connection, cursor)

if __name__ == "__main__":
    # Try to find the Excel file in the current or parent directory
    paths_to_try = [
        os.path.join(os.getcwd(), 'prof.xlsx'),
        os.path.join(os.path.dirname(os.getcwd()), 'prof.xlsx')
    ]
    
    excel_path = None
    for path in paths_to_try:
        if os.path.exists(path):
            excel_path = path
            break
    
    if not excel_path:
        print("Excel file 'prof.xlsx' not found!")
        excel_path = input("Please enter the path to your Excel file: ")
    
    migrate_data(excel_path)