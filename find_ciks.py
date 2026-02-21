"""查找 Dataroma 中缺失基金的正确 CIK 以及验证贝莱德/高盛"""
import urllib.request, json, gzip, io

headers = {'User-Agent': '13F-Tracker research@example.com', 'Accept-Encoding': 'gzip, deflate'}

def search_cik(company_name):
    """通过 EDGAR 全文搜索查找 CIK"""
    url = f"https://efts.sec.gov/LATEST/search-index?q=%22{company_name.replace(' ', '%20')}%22&dateRange=custom&startdt=2020-01-01&enddt=2026-12-31&forms=13F-HR"
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as res:
            raw = res.read()
            if res.headers.get('Content-Encoding') == 'gzip':
                raw = gzip.decompress(raw)
            data = json.loads(raw.decode('utf-8'))
            hits = data.get("hits", {}).get("hits", [])
            if hits:
                for h in hits[:3]:
                    src = h.get("_source", {})
                    print(f"    CIK: {src.get('entity_id', 'N/A'):15s} | Name: {src.get('display_names', ['N/A'])[0]:50s}")
    except Exception as e:
        print(f"    搜索失败: {e}")

def get_recent_13f(cik_padded):
    """获取某个 CIK 最近的 13F 报告"""
    url = f"https://data.sec.gov/submissions/CIK{cik_padded}.json"
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as res:
            raw = res.read()
            if res.headers.get('Content-Encoding') == 'gzip':
                raw = gzip.decompress(raw)
            data = json.loads(raw.decode('utf-8'))
        company_name = data.get("name", "N/A")
        recent = data.get("filings", {}).get("recent", {})
        forms = recent.get("form", [])
        dates = recent.get("reportDate", [])
        count_13f = sum(1 for f in forms if f in ("13F-HR", "13F-HR/A"))
        latest_date = "无"
        for i, f in enumerate(forms):
            if f in ("13F-HR", "13F-HR/A"):
                latest_date = dates[i]
                break
        print(f"  {company_name}: 共 {count_13f} 个 13F | 最新: {latest_date}")
    except Exception as e:
        print(f"  Error: {e}")

# ==== 1. 检查贝莱德 ====
print("=" * 60)
print("1. 贝莱德 CIK 检查")
print("=" * 60)
print("\nCIK 0001086364 (BlackRock Fund Advisors):")
get_recent_13f("0001086364")

# 搜索其他 BlackRock CIK
print("\n搜索 BlackRock 最近的 13F 提交:")
search_cik("BlackRock")

# 试试 BlackRock Inc 主体
for test_cik in ["0001364742", "0000091142", "0001006249"]:
    print(f"\nCIK {test_cik}:")
    get_recent_13f(test_cik)

# ==== 2. 检查高盛 ====
print("\n\n" + "=" * 60)
print("2. 高盛 CIK 检查")
print("=" * 60)
print("\nCIK 0000886982 (Goldman Sachs Group):")
get_recent_13f("0000886982")

# ==== 3. 查找缺失基金的 CIK ====
print("\n\n" + "=" * 60)
print("3. 查找 Dataroma 中缺失基金的 CIK")
print("=" * 60)

missing = [
    "Bill Nygren Oakmark",
    "Charles Bobrinskoy Ariel Focus",
    "FPA Queens Road",
    "Hillman Value Fund",
    "John Rogers Ariel",
    "Mason Hawkins Longleaf",
    "Meridian Contrarian Fund",
    "Richard Pzena",
    "Steven Romick FPA Crescent",
    "Terry Smith Fundsmith",
]
for name in missing:
    print(f"\n  {name}:")
    search_cik(name)
