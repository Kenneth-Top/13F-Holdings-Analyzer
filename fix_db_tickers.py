import sqlite3
import os
import sys

PROJ_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(PROJ_DIR, "backend"))

from config import DB_PATH, SEC_USER_AGENT
from scraper import normalize_name, _try_match_ticker, _build_cusip_ticker_map
import requests

def main():
    print("1. 调用 scraper 构建映射字典...")
    maps = _build_cusip_ticker_map()
    print(f"✅ 字典构建完成 (包含 {len(maps['exact'])} 家公司)")

    print("\n2. 查询数据库缺少 Ticker 的记录...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT issuer FROM holdings WHERE ticker = '' OR ticker IS NULL")
    missing_records = cursor.fetchall()
    
    print(f"共发现 {len(missing_records)} 种不同 Issuer 缺少 Ticker。")
    
    # 模拟构建一个只带 Issuer 的 dummy holdings 列表交给 scraper 代码去匹配
    virtual_holdings = []
    for (issuer,) in missing_records:
        virtual_holdings.append({
            "issuer": issuer,
            "ticker": ""
        })

    print("3. 执行本地 Ticker 推断匹配...")
    _try_match_ticker(virtual_holdings, maps, update_sector=False)

    matched_holdings = [h for h in virtual_holdings if h["ticker"]]
    print(f"🎉 成功为 {len(matched_holdings)} 种 Issuer 找到了对应的 Ticker！")

    if not matched_holdings:
        print("没有可更新的记录，退出。")
        conn.close()
        return

    print("4. 写入数据库 (纯本地、瞬间完成)...")
    batch_data = []
    for h in matched_holdings:
        # 仅更新 ticker 字段
        batch_data.append((h["ticker"], h["issuer"]))

    cursor.executemany("""
        UPDATE holdings
        SET ticker = ?
        WHERE issuer = ? AND (ticker = '' OR ticker IS NULL)
    """, batch_data)
    
    conn.commit()
    print(f"✅ 数据库已成功更新，受影响总行数: {cursor.rowcount}。")
    conn.close()

if __name__ == "__main__":
    main()
