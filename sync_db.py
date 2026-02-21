"""
sync_db.py — 同步数据库 funds 表与 config.py 的 FUNDS 列表
- 更新名称 (name/name_cn)
- 插入缺失基金
- 删除不再需要的旧基金 (以及对应的 holdings/filings 数据)
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import sqlite3
from backend.config import DB_PATH, FUNDS

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# 1. 获取 config 中的合法 CIK 集合
valid_ciks = {f["cik"] for f in FUNDS}
print(f"Config 中有效基金数量: {len(valid_ciks)}")

# 2. 查找数据库中所有 CIK
cursor.execute("SELECT cik, name_cn FROM funds")
db_funds = {row[0]: row[1] for row in cursor.fetchall()}
print(f"数据库中现有基金数量: {len(db_funds)}")

# 3. 删除不在 config 中的旧基金
to_delete = [cik for cik in db_funds if cik not in valid_ciks]
for cik in to_delete:
    print(f"  [删除] {db_funds[cik]} ({cik})")
    # 先删 holdings，再删 filings，最后删 funds
    cursor.execute("DELETE FROM holdings WHERE filing_id IN (SELECT id FROM filings WHERE fund_cik = ?)", (cik,))
    cursor.execute("DELETE FROM filings WHERE fund_cik = ?", (cik,))
    cursor.execute("DELETE FROM funds WHERE cik = ?", (cik,))
if to_delete:
    print(f"共删除 {len(to_delete)} 家旧基金记录")
else:
    print("  无需删除")

conn.commit()

# 4. 更新现有基金名称
for fund in FUNDS:
    cursor.execute(
        "UPDATE funds SET name = ?, name_cn = ? WHERE cik = ?",
        (fund["name"], fund["name_cn"], fund["cik"])
    )

# 5. 插入 config 中有但数据库中没有的基金
for fund in FUNDS:
    cursor.execute("SELECT 1 FROM funds WHERE cik = ?", (fund["cik"],))
    if not cursor.fetchone():
        cursor.execute(
            "INSERT INTO funds (cik, name, name_cn) VALUES (?, ?, ?)",
            (fund["cik"], fund["name"], fund["name_cn"])
        )
        print(f"  [新增] {fund['name_cn']}")

conn.commit()

# 6. 统计结果
cursor.execute("""
    SELECT f.name_cn, MAX(fi.period) as latest_period, COUNT(fi.id) as filing_count
    FROM funds f
    LEFT JOIN filings fi ON f.cik = fi.fund_cik
    GROUP BY f.cik
    ORDER BY CASE WHEN latest_period IS NULL THEN 0 ELSE 1 END DESC, latest_period DESC
""")
rows = cursor.fetchall()
print(f"\n数据库中共 {len(rows)} 家基金:")
for name, period, count in rows:
    print(f"  {name:45s} | 最新: {period or '无数据':10s} | 共 {count} 期")

conn.close()
print("\n数据库清理完成。")
