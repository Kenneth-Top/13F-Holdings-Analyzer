import urllib.request
import json

ciks = ['0001364742', '0000886982']
names = ['BlackRock Inc.', 'Goldman Sachs Group Inc']

headers = {'User-Agent': '13F-Tracker research@example.com'}

for cik, name in zip(ciks, names):
    url = f"https://data.sec.gov/submissions/CIK{cik.zfill(10)}.json"
    print(f"Checking {name} ({cik})...")
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode('utf-8'))
            
            filings = data.get("filings", {}).get("recent", {})
            if not filings:
                print("  No recent filings found.")
                continue
                
            forms = filings.get("form", [])
            dates = filings.get("filingDate", [])
            accessions = filings.get("accessionNumber", [])
            report_dates = filings.get("reportDate", [])
            
            found = 0
            for form, fdate, acc, rdate in zip(forms, dates, accessions, report_dates):
                if form in ("13F-HR", "13F-HR/A"):
                    print(f"  [{form}] Report Date: {rdate} | Filing Date: {fdate} | Accession: {acc}")
                    found += 1
                    if found >= 5:
                        break
            if found == 0:
                print("  No 13F-HR filings found in recent history.")
    except Exception as e:
        print(f"  Error fetching data: {e}")
    print("-" * 40)
