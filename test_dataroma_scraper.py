import os
import sys

PROJ_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(PROJ_DIR, "backend"))

from dataroma_scraper import scrape_dataroma_fund

holdings, actual_period = scrape_dataroma_fund("LMM")
print(f"Scraped Period: {actual_period}")
print(f"Total Holdings Scraped: {len(holdings)}")
if holdings:
    print("Sample Holding:")
    print(holdings[0])
