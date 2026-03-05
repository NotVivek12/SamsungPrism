import mysql.connector

conn = mysql.connector.connect(
    host='localhost', database='prism_sample_faculty',
    user='root', password='123456789', port=3306
)
cur = conn.cursor()
cur.execute("SELECT DomainName FROM domains WHERE DomainName LIKE '%;%' OR DomainName LIKE '%/%'")
results = cur.fetchall()
print(f"Domains with semicolons or slashes: {len(results)}")
for r in results[:30]:
    print(f"  {repr(r[0])}")

# Check citations
cur.execute("SELECT COUNT(*) FROM professors WHERE citations_count IS NOT NULL AND citations_count > 0")
print(f"\nProfessors with citations_count: {cur.fetchone()[0]}")
cur.execute("SELECT COUNT(*) FROM professors WHERE h_index IS NOT NULL AND h_index > 0")
print(f"Professors with h_index: {cur.fetchone()[0]}")
cur.execute("SELECT PName, h_index, citations_count FROM professors WHERE h_index IS NULL OR h_index = 0 LIMIT 10")
print("\nProfessors without h_index (sample):")
for r in cur.fetchall():
    print(f"  {r}")

# Check google scholar links
cur.execute("SELECT COUNT(*) FROM plink WHERE GScholar IS NOT NULL AND GScholar != ''")
print(f"\nProfessors with Google Scholar URL: {cur.fetchone()[0]}")
cur.execute("SELECT p.PName, pl.GScholar FROM professors p JOIN plink pl ON p.PID=pl.ProfID WHERE pl.GScholar IS NULL OR pl.GScholar = '' LIMIT 5")
print("Professors without Google Scholar (sample):")
for r in cur.fetchall():
    print(f"  {r[0]}")

cur.close()
conn.close()
