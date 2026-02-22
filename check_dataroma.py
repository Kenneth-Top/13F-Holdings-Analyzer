import requests
from bs4 import BeautifulSoup
import os
import sys

# Add backend to path to import config
PROJ_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(PROJ_DIR, "backend"))
from config import FUNDS

def get_dataroma_funds():
    url = "https://www.dataroma.com/m/managers.php"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Dataroma managers page has a table/list of managers.
        # usually under <td class="man_name"> or clicking on <a> with href="/m/holdings.php?m=..."
        links = soup.select("a[href^='/m/holdings.php?m=']")
        
        dataroma_funds = []
        for link in links:
            dataroma_id = link['href'].split('?m=')[-1].split('&')[0]
            name = link.text.strip()
            if name:
                dataroma_funds.append({"id": dataroma_id, "name": name})
                
        return dataroma_funds
    except Exception as e:
        print(f"Error scraping dataroma: {e}")
        return []

def main():
    print("Scraping dataroma.com for complete fund list...")
    d_funds = get_dataroma_funds()
    print(f"Found {len(d_funds)} funds on Dataroma.")
    
    # Existing funds in config.py
    # We should match by some fuzzy name or just find the missing ones
    existing_names = [f["name"].lower() for f in FUNDS]
    
    # Also find missing by checking if we have them
    missing = []
    for df in d_funds:
        d_name_lower = df["name"].lower()
        # exact match or partial match
        matched = False
        for ex in existing_names:
            if d_name_lower in ex or ex in d_name_lower:
                matched = True
                break
        
        # Some exceptions: "Warren Buffett" in dataroma vs. "Berkshire Hathaway" in our list
        if "buffett" in d_name_lower and any("berkshire" in ex for ex in existing_names):
            matched = True
        
        if not matched:
            missing.append(df)
            
    print("\n--- Missing Funds Python Dicts ---")
    for m in missing:
        # print something like: {"cik": "", "dataroma_id": "AKO", "name": "AKO Capital", "name_cn": "AKO Capital"},
        d_id = m['id']
        name = m['name']
        print(f'    {{"cik": "", "dataroma_id": "{d_id}", "name": "{name}", "name_cn": "{name}"}},')
        
if __name__ == "__main__":
    main()
