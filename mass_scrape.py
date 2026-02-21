"""批量采集所有无数据或数据过旧的基金"""
import sys, os

# 确保工作目录和路径正确
PROJ_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(PROJ_DIR)
sys.path.insert(0, PROJ_DIR)
# 让 scraper 内部的 'from config import ...' 也能找到 backend/config.py
sys.path.insert(0, os.path.join(PROJ_DIR, "backend"))

import sqlite3
from backend.config import DB_PATH, FUNDS
from backend.scraper import scrape_fund

def get_fund_status():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT f.cik, f.name, f.name_cn, MAX(fi.period) as latest
        FROM funds f
        LEFT JOIN filings fi ON f.cik = fi.fund_cik
        GROUP BY f.cik
    """)
    rows = cursor.fetchall()
    conn.close()
    return {row[0]: row for row in rows}

if __name__ == "__main__":
    status = get_fund_status()
    
    # 选出需要采集的基金
    to_scrape = []
    for fund in FUNDS:
        cik = fund["cik"]
        row = status.get(cik)
        latest = row[3] if row else None
        if latest is None or latest < "2024-Q1":
            to_scrape.append((cik, fund["name"], fund["name_cn"], latest or "无数据"))
    
    print(f"需要采集的基金: {len(to_scrape)} 家")
    for i, (cik, name, name_cn, status_str) in enumerate(to_scrape, 1):
        print(f"\n{'='*55}")
        print(f"[{i}/{len(to_scrape)}] {name_cn} ({cik}) | 当前: {status_str}")
        print(f"{'='*55}")
        try:
            scrape_fund(cik, name, name_cn, max_quarters=8, latest_only=False)
        except Exception as e:
            print(f"  [错误] {e}")
    
    print("\n\n✅ 所有采集任务完成!")
