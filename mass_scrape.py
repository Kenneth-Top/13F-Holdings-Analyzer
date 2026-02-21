"""触发所有无数据基金的首次采集（跳过已有数据的）"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import sqlite3
from backend.config import DB_PATH, FUNDS
from backend.scraper import scrape_fund

def get_funds_needing_scrape():
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
    return rows

if __name__ == "__main__":
    fund_rows = get_funds_needing_scrape()
    
    # 优先采集无数据或数据很旧的基金
    to_scrape = []
    for cik, name, name_cn, latest in fund_rows:
        if latest is None:
            to_scrape.append((cik, name, name_cn, "无数据"))
        elif latest < "2024-Q1":
            to_scrape.append((cik, name, name_cn, latest))
    
    print(f"需要采集的基金: {len(to_scrape)} 家")
    for cik, name, name_cn, status in to_scrape:
        print(f"\n{'='*55}")
        print(f"采集: {name_cn} ({cik}) | 当前: {status}")
        print(f"{'='*55}")
        try:
            scrape_fund(cik, name, name_cn, max_quarters=8, latest_only=False)
        except Exception as e:
            print(f"  [错误] {e}")
    
    print("\n\n所有采集任务完成!")
