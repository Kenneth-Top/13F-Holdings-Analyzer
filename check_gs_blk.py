import sqlite3
from backend.config import DB_PATH

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()
cursor.execute('''
    SELECT fd.name_cn, f.period, f.filing_date, f.accession 
    FROM filings f 
    JOIN funds fd ON f.fund_cik = fd.cik 
    WHERE fd.name_cn LIKE '%高盛%' OR fd.name_cn LIKE '%贝莱德%' 
    ORDER BY fd.name_cn, f.period DESC
''')
for row in cursor.fetchall():
    print(row)
conn.close()
