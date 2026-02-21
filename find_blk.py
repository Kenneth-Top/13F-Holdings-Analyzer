import urllib.request
import json

# Let's search for BlackRock CIKs that file 13F
url = "https://efts.sec.gov/LATEST/search-index"
data = {
    "q": "BlackRock",
    "dateRange": "custom",
    "startdt": "2025-01-01",
    "enddt": "2026-03-01",
    "category": "custom",
    "forms": ["13F-HR"]
}
req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), headers={'User-Agent': '13F-Tracker research@example.com', 'Content-Type': 'application/json'})
try:
    with urllib.request.urlopen(req) as response:
        result = json.loads(response.read().decode('utf-8'))
        hits = result.get('hits', {}).get('hits', [])
        for h in hits[:5]:
            source = h.get('_source', {})
            display_names = source.get('display_names', [])
            form = source.get('form')
            file_date = source.get('file_date')
            ciks = source.get('ciks', [])
            print(f"{display_names} | CIKs: {ciks} | Form: {form} | Date: {file_date}")
except Exception as e:
    print(e)
