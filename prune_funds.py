import sqlite3
import json
from backend.config import DB_PATH

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

cursor.execute("SELECT fund_cik, COUNT(*) FROM filings GROUP BY fund_cik")
filing_counts = {row[0]: row[1] for row in cursor.fetchall()}

cursor.execute("SELECT cik, name_cn FROM funds")
all_funds = cursor.fetchall()

no_data_ciks = [cik for cik, name in all_funds if filing_counts.get(cik, 0) == 0]

print(f"Found {len(no_data_ciks)} funds with 0 filings.")
for cik in no_data_ciks:
    name = next(name for c, name in all_funds if c == cik)
    print(f"  - {name} ({cik})")

# Remove from DB
if no_data_ciks:
    placeholders = ','.join(['?']*len(no_data_ciks))
    cursor.execute(f"DELETE FROM funds WHERE cik IN ({placeholders})", no_data_ciks)
    conn.commit()
    print("Deleted from database.")

conn.close()

# Also write to a file so we know what to remove from config.py
with open("ciks_to_remove.txt", "w", encoding="utf-8") as f:
    for cik in no_data_ciks:
        f.write(f"{cik}\n")
