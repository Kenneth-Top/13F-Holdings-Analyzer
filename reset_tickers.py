import sqlite3
import os
import sys

PROJ_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(PROJ_DIR, "backend"))

from config import DB_PATH

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()
cursor.execute("UPDATE holdings SET ticker = ''")
conn.commit()
print(f"✅ 成功清空了 {cursor.rowcount} 条记录的 ticker 字段，准备重新全量推断。")
conn.close()
