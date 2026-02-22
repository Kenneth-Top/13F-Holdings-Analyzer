import sqlite3
import os

PROJ_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(PROJ_DIR, "data", "holdings.db")

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

issuers_to_check = [
    "BANK AMERICA CORP",
    "BK OF AMERICA CORP",
    "MOODYS CORP",
    "OCCIDENTAL PETE CORP",
    "VERISIGN INC",
    "CAPITAL ONE FINL CORP"
]

for issuer in issuers_to_check:
    cursor.execute("SELECT ticker FROM holdings WHERE issuer = ?", (issuer,))
    rows = cursor.fetchall()
    unique_tickers = set(r[0] for r in rows)
    print(f"Issuer: {issuer} -> Tickers in DB: {unique_tickers}")

conn.close()
