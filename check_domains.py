import mysql.connector

conn = mysql.connector.connect(
    host='localhost', database='prism_sample_faculty',
    user='root', password='123456789', port=3306
)
cur = conn.cursor()

# Check remaining semicolons
cur.execute("SELECT COUNT(*) FROM domains WHERE DomainName LIKE '%;%'")
print(f"Domains with semicolons remaining: {cur.fetchone()[0]}")

# Show sample domains
cur.execute("SELECT DomainName FROM domains ORDER BY DomainName LIMIT 20")
print("\nFirst 20 domains:")
for r in cur.fetchall():
    print(f"  {r[0]}")

# Check a professor who had semicolons
cur.execute("""
    SELECT p.PName, GROUP_CONCAT(d.DomainName SEPARATOR ' | ') as domains
    FROM professors p
    JOIN prof_domain pd ON p.PID = pd.ProfID
    JOIN domains d ON pd.DomainId = d.DomainID
    WHERE p.PName LIKE '%Chakraborty%'
    GROUP BY p.PID
""")
print("\nChakraborty domains:")
for r in cur.fetchall():
    print(f"  {r[0]}: {r[1]}")

cur.close()
conn.close()
