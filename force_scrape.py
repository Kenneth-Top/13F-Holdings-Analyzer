"""强制补采高盛和贝莱德最新数据"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# 须从 backend 目录运行
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "backend"))

from backend.scraper import scrape_fund

targets = [
    {"cik": "0000886982", "name": "Goldman Sachs Group Inc", "name_cn": "高盛集团"},
    {"cik": "0001086364", "name": "BlackRock Fund Advisors", "name_cn": "贝莱德"},
]

for t in targets:
    print(f"\n{'='*50}")
    print(f"Scraping: {t['name_cn']} ({t['cik']})")
    print(f"{'='*50}")
    scrape_fund(t["cik"], t["name"], t["name_cn"], max_quarters=8, latest_only=False)

print("\nDone!")
