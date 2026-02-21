"""自动清理：从 config.py 删除无 13F 数据的基金，并同步数据库"""
import sys, os, re

PROJ_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(PROJ_DIR)
sys.path.insert(0, PROJ_DIR)

import sqlite3
from backend.config import DB_PATH, FUNDS

# 1. 查询数据库中哪些 CIK 无数据
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()
cursor.execute("""
    SELECT f.cik, f.name_cn, COUNT(fi.id) as cnt
    FROM funds f
    LEFT JOIN filings fi ON f.cik = fi.fund_cik
    GROUP BY f.cik
""")
rows = cursor.fetchall()
no_data_ciks = {row[0] for row in rows if row[2] == 0}
print(f"无数据 CIK 共 {len(no_data_ciks)} 个，准备从 config.py 和数据库中删除：")
for row in rows:
    if row[2] == 0:
        print(f"  {row[1]} ({row[0]})")

# 2. 从 config.py 中删除这些 CIK
config_path = os.path.join(PROJ_DIR, "backend", "config.py")
with open(config_path, "r", encoding="utf-8") as f:
    content = f.read()

# 删除每一行包含该 CIK 的 dict 项
lines = content.split("\n")
new_lines = []
for line in lines:
    skip = False
    for cik in no_data_ciks:
        # 匹配形如 {"cik": "0001234567", ... 的行
        if f'"{cik}"' in line and '"cik"' in line:
            skip = True
            break
    if not skip:
        new_lines.append(line)

with open(config_path, "w", encoding="utf-8") as f:
    f.write("\n".join(new_lines))
print(f"\n已从 config.py 删除 {len(no_data_ciks)} 条记录")

# 3. 从数据库删除这些 CIK
for cik in no_data_ciks:
    cursor.execute("DELETE FROM holdings WHERE filing_id IN (SELECT id FROM filings WHERE fund_cik = ?)", (cik,))
    cursor.execute("DELETE FROM filings WHERE fund_cik = ?", (cik,))
    cursor.execute("DELETE FROM funds WHERE cik = ?", (cik,))
conn.commit()
conn.close()
print(f"已从数据库删除 {len(no_data_ciks)} 家基金")

# 4. 验证剩余
conn2 = sqlite3.connect(DB_PATH)
c2 = conn2.cursor()
c2.execute("SELECT COUNT(*) FROM funds")
total = c2.fetchone()[0]
c2.execute("""
    SELECT f.name_cn, MAX(fi.period)
    FROM funds f LEFT JOIN filings fi ON f.cik=fi.fund_cik
    GROUP BY f.cik ORDER BY MAX(fi.period) DESC NULLS LAST
""")
remaining = c2.fetchall()
conn2.close()
print(f"\n数据库剩余 {total} 家基金（均有数据）：")
for name, period in remaining:
    print(f"  {name:45s} | {period or '无数据'}")
