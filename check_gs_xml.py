import urllib.request
import json

base_url = "https://www.sec.gov/Archives/edgar/data/886982/000088698226000052"
json_url = f"{base_url}/0000886982-26-000052-index.json"

req = urllib.request.Request(json_url, headers={'User-Agent': '13F-Tracker research@example.com'})
try:
    with urllib.request.urlopen(req) as response:
        index_data = json.loads(response.read().decode('utf-8'))
        items = index_data.get("directory", {}).get("item", [])
        for item in items:
            print(f"Name: {item.get('name')}, Type: {item.get('type')}")
except Exception as e:
    print(f"Error: {e}")
