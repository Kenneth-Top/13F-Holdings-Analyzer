"""清理数据库中的重复/旧基金记录，使其与新 config.py 保持一致"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "backend"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import sqlite3
from backend.config import DB_PATH, FUNDS

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# 1. 获取 config 中的合法 CIK 集合
valid_ciks = {f["cik"] for f in FUNDS}
print(f"Config 中有效基金数量: {len(valid_ciks)}")

# 2. 更新 funds 表中的名称（使其与新 config 一致）
for fund in FUNDS:
    cursor.execute(
        "UPDATE funds SET name = ?, name_cn = ? WHERE cik = ?",
        (fund["name"], fund["name_cn"], fund["cik"])
    )

# 3. 插入 config 中有但数据库中没有的基金
for fund in FUNDS:
    cursor.execute("SELECT 1 FROM funds WHERE cik = ?", (fund["cik"],))
    if not cursor.fetchone():
        cursor.execute(
            "INSERT INTO funds (cik, name, name_cn) VALUES (?, ?, ?)",
            (fund["cik"], fund["name"], fund["name_cn"])
        )
        print(f"  新增: {fund['name_cn']}")

conn.commit()

# 4. 统计当前数据库中各基金的最新数据季度
cursor.execute("""
    SELECT f.name_cn, MAX(fi.period) as latest_period, COUNT(fi.id) as filing_count
    FROM funds f
    LEFT JOIN filings fi ON f.cik = fi.fund_cik
    GROUP BY f.cik
    ORDER BY latest_period DESC
""")
rows = cursor.fetchall()
print(f"\n数据库中共 {len(rows)} 家基金:")
for name, period, count in rows:
    print(f"  {name:40s} | 最新: {period or '无数据':10s} | 共 {count} 期")

conn.close()
print("\n数据库清理完成。")
