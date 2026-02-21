import sys
import os

base_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.join(base_dir, "backend")
sys.path.insert(0, backend_dir)
sys.path.insert(0, base_dir)

from backend.scraper import scrape_fund

ciks_to_scrape = [
    ('0000886982', 'Goldman Sachs Group Inc', '高盛集团'),
    ('0001086364', 'BlackRock Inc.', '贝莱德'),
]

for cik, name, name_cn in ciks_to_scrape:
    print(f"Scraping CIK: {cik}")
    scrape_fund(cik, name, name_cn, latest_only=True)
print("Scraping completed.")
