import urllib.request
import json
import re

def normalize_name(name):
    name = name.upper()
    name = re.sub(r'[^\w\s]', '', name)
    name = " " + name + " "
    name = name.replace(" FINL ", " FINANCIAL ")
    name = name.replace(" PETE ", " PETROLEUM ")
    name = name.replace(" HLDG ", " HOLDING ")
    name = name.replace(" HLDGS ", " HOLDINGS ")
    name = name.replace(" GRP ", " GROUP ")
    name = name.replace(" NATL ", " NATIONAL ")
    for suffix in [" INC ", " CORP ", " CORPORATION ", " CO ", " LTD ", " PLC ", " LLC ", " LP ", " COMPANY ", " DE ", " OF ", " THE "]:
        name = name.replace(suffix, " ")
    name = name.replace(" NEW ", " ")
    return " ".join(name.split())

req = urllib.request.Request("https://www.sec.gov/files/company_tickers.json", headers={'User-Agent': 'Sample Company AdminContact@sample.com'})
try:
    with urllib.request.urlopen(req) as response:
        data = json.loads(response.read().decode())

    print("Entries for BANK AMERICA:")
    for k, v in data.items():
        title = v.get("title", "").upper()
        ticker = v.get("ticker", "")
        norm = normalize_name(title)
        if norm == "BANK AMERICA":
            print(f"  Title: {title} | Ticker: {ticker}")

    print("\nEntries for CAPITAL ONE FINANCIAL:")
    for k, v in data.items():
        title = v.get("title", "").upper()
        ticker = v.get("ticker", "")
        norm = normalize_name(title)
        if norm == "CAPITAL ONE FINANCIAL":
            print(f"  Title: {title} | Ticker: {ticker}")

except Exception as e:
    print(f"Error: {e}")
