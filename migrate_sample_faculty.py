"""
Migration script: SAMPLE Faculty Data.xlsx -> prism_sample_faculty MySQL database.
Reads both sheets (IITB, IITK) and maps the sheet name to the college name.
Domains are extracted from "Main Technical Field" and "Technical Areas working on" columns only.
"""

import pandas as pd
import mysql.connector
from mysql.connector import Error
import math

# --- Configuration ---
EXCEL_PATH = r"D:\Professor Profile\SamsungPrism\SAMPLE Faculty Data.xlsx"

DB_CONFIG = {
    'host': 'localhost',
    'database': 'prism_sample_faculty',
    'user': 'root',
    'password': '123456789',
    'port': 3306
}

SHEET_TO_COLLEGE = {
    'IITB': 'IIT Bombay',
    'IITK': 'IIT Kharagpur',
}


def clean(val):
    """Return cleaned string; empty string for NaN / None."""
    if val is None:
        return ''
    s = str(val).strip()
    if s.lower() == 'nan':
        return ''
    s = s.replace('\xa0', ' ')
    return s


def clean_int(val):
    """Return int or None."""
    if val is None:
        return None
    try:
        f = float(val)
        if math.isnan(f):
            return None
        return int(f)
    except (ValueError, TypeError):
        return None


def get_col(row, candidates):
    """Try multiple column-name variants and return the first match."""
    for c in candidates:
        if c in row.index:
            return clean(row[c])
    return ''


def get_or_create_domain(cursor, domain_name):
    """Get domain ID, creating the domain if it doesn't exist."""
    cursor.execute("SELECT DomainID FROM domains WHERE DomainName = %s", (domain_name,))
    result = cursor.fetchone()
    if result:
        return result[0]
    cursor.execute("INSERT INTO domains (DomainName) VALUES (%s)", (domain_name,))
    return cursor.lastrowid


def reset_tables(cursor):
    """Drop and recreate tables for a clean migration."""
    cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
    for tbl in ['prof_domain', 'plink', 'domains', 'professors']:
        cursor.execute(f"DROP TABLE IF EXISTS {tbl}")
    cursor.execute("SET FOREIGN_KEY_CHECKS = 1")

    cursor.execute("""CREATE TABLE professors (
        PID INT AUTO_INCREMENT PRIMARY KEY,
        PName VARCHAR(255) NOT NULL,
        CName VARCHAR(255),
        CMailId VARCHAR(255),
        Phd TEXT,
        citations_count INT DEFAULT NULL,
        h_index INT DEFAULT NULL,
        i10_index INT DEFAULT NULL,
        citations_updated_at DATETIME DEFAULT NULL
    )""")
    cursor.execute("""CREATE TABLE plink (
        ProfID INT,
        GScholar VARCHAR(512),
        SScholar VARCHAR(512),
        CProfile VARCHAR(512),
        PRIMARY KEY (ProfID),
        FOREIGN KEY (ProfID) REFERENCES professors(PID)
    )""")
    cursor.execute("""CREATE TABLE domains (
        DomainID INT AUTO_INCREMENT PRIMARY KEY,
        DomainName VARCHAR(255) NOT NULL
    )""")
    cursor.execute("""CREATE TABLE prof_domain (
        ID INT AUTO_INCREMENT PRIMARY KEY,
        ProfID INT,
        DomainId INT,
        FOREIGN KEY (ProfID) REFERENCES professors(PID),
        FOREIGN KEY (DomainId) REFERENCES domains(DomainID)
    )""")
    print("Tables recreated successfully.")


def migrate():
    conn = None
    cursor = None
    try:
        all_sheets = pd.read_excel(EXCEL_PATH, sheet_name=None)
        print(f"Found sheets: {list(all_sheets.keys())}")

        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # Clean start
        reset_tables(cursor)
        conn.commit()

        total_inserted = 0
        skipped = 0

        for sheet_name, df in all_sheets.items():
            college = SHEET_TO_COLLEGE.get(sheet_name, sheet_name)
            print(f"\n--- Sheet: {sheet_name} -> College: {college}  ({len(df)} rows) ---")

            for idx, row in df.iterrows():
                name = get_col(row, ['Faculty name', 'Faculty Name', 'Name', 'name'])
                if not name:
                    skipped += 1
                    continue

                email = get_col(row, ['email.id', 'EMAIL ID ', 'EMAIL ID', 'Email', 'email'])
                h_index = clean_int(row.get('H index'))

                # Insert professor
                cursor.execute(
                    "INSERT INTO professors (PName, CName, CMailId, Phd, h_index) VALUES (%s, %s, %s, %s, %s)",
                    (name, college, email, '', h_index)
                )
                pid = cursor.lastrowid

                # Insert links
                google_scholar = get_col(row, ['GoogleScholar', 'Google Scholar', 'google_scholar_url'])
                personal_page = get_col(row, ['personal page link', 'Personal Page Link', 'profile_link'])
                cursor.execute(
                    "INSERT INTO plink (ProfID, GScholar, SScholar, CProfile) VALUES (%s, %s, %s, %s)",
                    (pid, google_scholar, '', personal_page)
                )

                # --- Domain extraction (improved splitting) ---
                # 1. Main Technical Field  — the primary, clean domain label
                main_field = get_col(row, [
                    ' Main Technical Field (For setting a filter)',
                    'Main Technical Field (For setting a filter)',
                ])
                # 2. Technical Areas working on — granular topics
                tech_areas = get_col(row, ['Technical Areas working on'])

                seen = set()
                all_domain_parts = []

                def split_domains(text):
                    """Split a domain string by commas and semicolons."""
                    import re
                    # Split by comma or semicolon
                    parts = re.split(r'[,;]', text)
                    return [p.strip() for p in parts if p.strip()]

                # Add main field first
                if main_field:
                    all_domain_parts.extend(split_domains(main_field))

                # Then add technical areas
                if tech_areas:
                    all_domain_parts.extend(split_domains(tech_areas))

                for domain_name in all_domain_parts:
                    # Skip empty, too-long, or duplicate entries
                    if not domain_name or len(domain_name) > 250 or domain_name in seen:
                        continue
                    seen.add(domain_name)
                    domain_id = get_or_create_domain(cursor, domain_name)
                    cursor.execute(
                        "INSERT INTO prof_domain (ProfID, DomainId) VALUES (%s, %s)",
                        (pid, domain_id)
                    )

                total_inserted += 1

        conn.commit()
        print(f"\n{'='*50}")
        print(f"✅ Migration complete!")
        print(f"   Professors inserted : {total_inserted}")
        print(f"   Rows skipped (empty): {skipped}")

        # Verification counts
        for tbl in ['professors', 'plink', 'domains', 'prof_domain']:
            cursor.execute(f"SELECT COUNT(*) FROM {tbl}")
            print(f"   {tbl:20s}: {cursor.fetchone()[0]} rows")

        # Show college breakdown
        cursor.execute("SELECT CName, COUNT(*) FROM professors GROUP BY CName")
        print("\n   College breakdown:")
        for row in cursor.fetchall():
            print(f"     {row[0]}: {row[1]} professors")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        if conn:
            conn.rollback()
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()


if __name__ == '__main__':
    migrate()
