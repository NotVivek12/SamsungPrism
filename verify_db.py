import mysql.connector

conn = mysql.connector.connect(
    host='localhost', database='prism_sample_faculty',
    user='root', password='123456789', port=3306
)
cur = conn.cursor()

print("=== Sample Professors ===")
cur.execute("SELECT PID, PName, CName, CMailId, h_index FROM professors LIMIT 5")
for r in cur.fetchall():
    print(r)

print("\n=== Sample Links ===")
cur.execute("""
    SELECT p.PName, pl.GScholar, pl.CProfile
    FROM professors p JOIN plink pl ON p.PID = pl.ProfID
    WHERE pl.GScholar != ''
    LIMIT 3
""")
for r in cur.fetchall():
    print(r)

print("\n=== Top 10 Domains by Professor Count ===")
cur.execute("""
    SELECT d.DomainName, COUNT(pd.ProfID) as cnt
    FROM domains d JOIN prof_domain pd ON d.DomainID = pd.DomainId
    GROUP BY d.DomainID ORDER BY cnt DESC LIMIT 10
""")
for r in cur.fetchall():
    print(f"  {r[0]:40s} {r[1]} professors")

print("\n=== College Breakdown ===")
cur.execute("SELECT CName, COUNT(*) FROM professors GROUP BY CName")
for r in cur.fetchall():
    print(f"  {r[0]:20s} {r[1]} professors")

cur.close()
conn.close()
