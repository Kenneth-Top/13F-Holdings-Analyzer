import sqlite3
import re
import urllib.request
import json
import os
import sys

PROJ_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(PROJ_DIR, "backend"))
from config import DB_PATH

def normalize_name(name):
    name = name.upper()
    name = re.sub(r'[^\w\s]', '', name)
    name = " " + name + " "
    for suffix in [" INC ", " CORP ", " CORPORATION ", " CO ", " LTD ", " PLC ", " LLC ", " LP ", " COMPANY "]:
        name = name.replace(suffix, " ")
    return " ".join(name.split())

print("Loading company_tickers.json...")
req = urllib.request.Request("https://www.sec.gov/files/company_tickers.json", headers={'User-Agent': 'Sample Company Name AdminContact@sample.com'})
try:
    with urllib.request.urlopen(req) as response:
        data = json.loads(response.read().decode())

    exact_map = {}
    norm_map = {}
    for k, v in data.items():
        title = v.get("title", "").upper()
        ticker = v.get("ticker", "")
        exact_map[title] = ticker
        norm_map[normalize_name(title)] = ticker

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT issuer FROM holdings WHERE ticker = '' OR ticker IS NULL")
    missing_issuers = [row[0] for row in cursor.fetchall()]
    # don't close conn yet

    print(f"Database has {len(missing_issuers)} unique issuers with missing ticker.")

    exact_matches = 0
    norm_matches = 0
    partial_matches = 0

    for issuer in missing_issuers:
        issuer_upper = issuer.upper()
        norm_iss = normalize_name(issuer)
        
        if issuer_upper in exact_map:
            exact_matches += 1
            continue
            
        if norm_iss in norm_map:
            norm_matches += 1
            continue

        words = norm_iss.split()
        matched = False
        for length in range(len(words), 0, -1):
            partial = " ".join(words[:length])
            if partial and partial in norm_map:
                partial_matches += 1
                matched = True
                break
        
        if not matched:
            pass # We don't need to append here because we query directly below
                    
    print(f"If we use EXACT matching, we match {exact_matches}")
    print(f"If we use NORMALIZED names, we match {norm_matches} exact and {partial_matches} partial.")
    
    print("\nTop 20 Unmatched Issuers:")
    from collections import Counter
    cursor = conn.cursor()
    cursor.execute("SELECT issuer, COUNT(*) as cnt FROM holdings WHERE ticker = '' OR ticker IS NULL GROUP BY issuer ORDER BY cnt DESC LIMIT 50")
    top_missing = cursor.fetchall()
    conn.close()
    
    for row in top_missing:
        iss = row[0]
        # Only print if actually unmatched by our new logic
        norm_iss = normalize_name(iss)
        matched = norm_iss in norm_map
        if not matched:
            words = norm_iss.split()
            for length in range(len(words), 0, -1):
                partial = " ".join(words[:length])
                if partial and partial in norm_map:
                    matched = True
                    break
        if not matched:
            print(f"  {row[1]:4d} | {iss}")

except Exception as e:
    print(f"Error: {e}")
