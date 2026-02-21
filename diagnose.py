import sqlite3
conn = sqlite3.connect('data/holdings.db')
c = conn.cursor()

# 行业分类统计
print('=== 伯克希尔 2025-Q4 行业分布 ===')
c.execute("""
SELECT h.asset_class, COUNT(*) as cnt, SUM(h.value) as total_val
FROM holdings h JOIN filings f ON h.filing_id=f.id
WHERE f.fund_cik='0001067983' AND f.period='2025-Q4'
GROUP BY h.asset_class ORDER BY total_val DESC
""")
for r in c.fetchall(): print(f"  {r[0]}: {r[1]}只, ${r[2]/1e9:.1f}B")

# 行业为"股票"的未分类比例
print('\n=== 全库 asset_class 分布 ===')
c.execute("""
SELECT asset_class, COUNT(*) as cnt
FROM holdings GROUP BY asset_class ORDER BY cnt DESC LIMIT 15
""")
for r in c.fetchall(): print(f"  {r[0]}: {r[1]}")

# 验证苹果
print('\n=== AAPL ticker 匹配 ===')
c.execute("""
SELECT h.issuer, h.ticker, h.asset_class, h.value/1e9
FROM holdings h JOIN filings f ON h.filing_id=f.id
WHERE f.fund_cik='0001067983' AND f.period='2025-Q4' AND upper(h.issuer) LIKE '%APPLE%'
""")
for r in c.fetchall(): print(r)
