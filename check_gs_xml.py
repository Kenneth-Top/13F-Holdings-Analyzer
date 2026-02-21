"""查看高盛 2025-Q4 的实际 filing 文件结构"""
import urllib.request, json, re

cik = "886982"  # 不带前导零
acc_num = "0000886982-26-000052"
acc_clean = acc_num.replace("-", "")
base_url = f"https://www.sec.gov/Archives/edgar/data/{cik}/{acc_clean}"

headers = {'User-Agent': '13F-Tracker research@example.com', 'Accept-Encoding': 'gzip, deflate'}

# 方法1: 尝试 JSON index
json_url = f"{base_url}/{acc_num}-index.json"
print(f"尝试 JSON: {json_url}")
try:
    req = urllib.request.Request(json_url, headers=headers)
    with urllib.request.urlopen(req, timeout=10) as res:
        data = json.loads(res.read().decode('utf-8'))
        items = data.get("directory", {}).get("item", [])
        print(f"  找到 {len(items)} 个文件:")
        for item in items:
            print(f"    {item.get('name'):50s} | {item.get('type', 'N/A')}")
except Exception as e:
    print(f"  JSON 失败: {e}")

# 方法2: HTML 目录
html_url = f"{base_url}/"
print(f"\n尝试 HTML: {html_url}")
try:
    req = urllib.request.Request(html_url, headers=headers)
    with urllib.request.urlopen(req, timeout=10) as res:
        html = res.read().decode('utf-8')
    # 找所有 href
    all_hrefs = re.findall(r'href="([^"]+)"', html)
    print(f"  找到 {len(all_hrefs)} 个链接:")
    for href in all_hrefs:
        if any(ext in href.lower() for ext in ['.xml', '.htm', '.html', '.txt', '.csv']):
            print(f"    {href}")
except Exception as e:
    print(f"  HTML 失败: {e}")

# 方法3: EDGAR submissions API
print(f"\n尝试 submissions API:")
try:
    api_url = f"https://data.sec.gov/submissions/CIK{cik.zfill(10)}.json"
    req = urllib.request.Request(api_url, headers=headers)
    with urllib.request.urlopen(req, timeout=10) as res:
        data = json.loads(res.read().decode('utf-8'))
    recent = data.get("filings", {}).get("recent", {})
    forms = recent.get("form", [])
    accs = recent.get("accessionNumber", [])
    report_dates = recent.get("reportDate", [])
    primary_docs = recent.get("primaryDocument", [])
    
    for i, form in enumerate(forms):
        if form in ("13F-HR", "13F-HR/A"):
            print(f"  {form} | ReportDate: {report_dates[i]} | Acc: {accs[i]} | PrimaryDoc: {primary_docs[i] if i < len(primary_docs) else 'N/A'}")
            if i >= 5:
                break
except Exception as e:
    print(f"  API 失败: {e}")
