import urllib.request
import json
import re

def normalize_name(name):
    name = name.upper()
    name = re.sub(r'[^\w\s]', '', name)
    name = " " + name + " "
    
    # 扩展常见 13F 英文缩写
    name = name.replace(" FINL ", " FINANCIAL ")
    name = name.replace(" PETE ", " PETROLEUM ")
    name = name.replace(" HLDG ", " HOLDING ")
    name = name.replace(" HLDGS ", " HOLDINGS ")
    name = name.replace(" GRP ", " GROUP ")
    name = name.replace(" NATL ", " NATIONAL ")
    
    # 移除连词、无关后缀以及代表注册地特拉华州的 DE
    for suffix in [" INC ", " CORP ", " CORPORATION ", " CO ", " LTD ", " PLC ", " LLC ", " LP ", " COMPANY ", " DE ", " OF ", " THE "]:
        name = name.replace(suffix, " ")
    name = name.replace(" NEW ", " ")
    return " ".join(name.split())

req = urllib.request.Request("https://www.sec.gov/files/company_tickers.json", headers={'User-Agent': 'Sample Company AdminContact@sample.com'})
try:
    with urllib.request.urlopen(req) as response:
        data = json.loads(response.read().decode())

    exact_map = {}
    norm_map = {}
    for k, v in data.items():
        title = v.get("title", "").upper()
        ticker = v.get("ticker", "")
        if not ticker or not title: continue
        exact_map[title] = ticker
        norm_map[normalize_name(title)] = ticker

    test_issuers = ["BANK AMERICA CORP", "MOODYS CORP", "DANAHER CORPORATION", "CAPITAL ONE FINL CORP", "OCCIDENTAL PETE CORP"]
    for iss in test_issuers:
        norm = normalize_name(iss)
        print(f"Testing {iss} -> norm: '{norm}'")
        if norm in norm_map:
            print(f"  Matched exact norm! Ticker: {norm_map[norm]}")
        else:
            print(f"  Not matched exact norm.")
            words = norm.split()
            matched = False
            for length in range(len(words), 0, -1):
                partial = " ".join(words[:length])
                if partial and partial in norm_map:
                    print(f"  Matched partial: '{partial}' -> Ticker: {norm_map[partial]}")
                    matched = True
                    break
            if not matched:
                print("  Failed to match. Best SEC matches containing word 1:")
                word1 = words[0] if words else ""
                matches = [k for k in norm_map.keys() if word1 in k]
                print(f"    Some SEC norms: {matches[:5]}")

except Exception as e:
    print(f"Error: {e}")
