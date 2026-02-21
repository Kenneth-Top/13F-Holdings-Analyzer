# -*- coding: utf-8 -*-
"""SQLite 数据库操作封装"""

import os
import sqlite3
from contextlib import contextmanager
from backend.config import DB_PATH, DATA_DIR


def init_db():
    """初始化数据库，创建所需表"""
    os.makedirs(DATA_DIR, exist_ok=True)
    with get_conn() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS funds (
                cik         TEXT PRIMARY KEY,
                name        TEXT NOT NULL,
                name_cn     TEXT
            );

            CREATE TABLE IF NOT EXISTS filings (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                fund_cik        TEXT NOT NULL,
                period          TEXT NOT NULL,       -- 如 '2025-Q4'
                period_date     TEXT NOT NULL,       -- 如 '2025-12-31'
                filing_date     TEXT,
                accession       TEXT,
                total_value     REAL DEFAULT 0,      -- 总市值 (千美元)
                FOREIGN KEY (fund_cik) REFERENCES funds(cik),
                UNIQUE(fund_cik, period)
            );

            CREATE TABLE IF NOT EXISTS holdings (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                filing_id       INTEGER NOT NULL,
                issuer          TEXT NOT NULL,        -- 发行人名称
                cusip           TEXT,
                ticker          TEXT,                 -- 股票代号
                title_of_class  TEXT,                 -- 证券类别
                asset_class     TEXT,                 -- 简化资产类别
                value           REAL,                 -- 市值 (千美元)
                shares          INTEGER,              -- 持股数
                share_type      TEXT,                 -- SH 或 PRN
                put_call        TEXT,                 -- PUT/CALL/NULL
                discretion      TEXT,                 -- 投资权限
                portfolio_pct   REAL DEFAULT 0,       -- 占投组比例 %
                prev_pct        REAL DEFAULT 0,       -- 上季占比 %
                pct_change      REAL DEFAULT 0,       -- 占比变化 (百分点)
                shares_change_pct REAL DEFAULT 0,     -- 持仓量变化 %
                FOREIGN KEY (filing_id) REFERENCES filings(id)
            );

            CREATE INDEX IF NOT EXISTS idx_filings_cik_period ON filings(fund_cik, period);
            CREATE INDEX IF NOT EXISTS idx_holdings_filing ON holdings(filing_id);
        """)


@contextmanager
def get_conn():
    """获取数据库连接的上下文管理器"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def upsert_fund(cik, name, name_cn=""):
    """新增或更新基金信息"""
    with get_conn() as conn:
        conn.execute(
            "INSERT OR REPLACE INTO funds (cik, name, name_cn) VALUES (?, ?, ?)",
            (cik, name, name_cn)
        )


def get_filing(fund_cik, period):
    """获取指定基金某季度的 filing 记录"""
    with get_conn() as conn:
        row = conn.execute(
            "SELECT * FROM filings WHERE fund_cik = ? AND period = ?",
            (fund_cik, period)
        ).fetchone()
        return dict(row) if row else None


def upsert_filing(fund_cik, period, period_date, filing_date, accession, total_value):
    """新增或更新 filing 记录，返回 filing id"""
    with get_conn() as conn:
        existing = conn.execute(
            "SELECT id FROM filings WHERE fund_cik = ? AND period = ?",
            (fund_cik, period)
        ).fetchone()
        if existing:
            conn.execute(
                """UPDATE filings SET period_date=?, filing_date=?, accession=?, total_value=?
                   WHERE id=?""",
                (period_date, filing_date, accession, total_value, existing["id"])
            )
            # 清除旧持仓数据
            conn.execute("DELETE FROM holdings WHERE filing_id = ?", (existing["id"],))
            return existing["id"]
        else:
            cursor = conn.execute(
                """INSERT INTO filings (fund_cik, period, period_date, filing_date, accession, total_value)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (fund_cik, period, period_date, filing_date, accession, total_value)
            )
            return cursor.lastrowid


def insert_holdings(filing_id, holdings_list):
    """批量插入持仓数据"""
    with get_conn() as conn:
        conn.executemany(
            """INSERT INTO holdings
               (filing_id, issuer, cusip, ticker, title_of_class, asset_class,
                value, shares, share_type, put_call, discretion,
                portfolio_pct, prev_pct, pct_change, shares_change_pct)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            [(filing_id, h["issuer"], h.get("cusip"), h.get("ticker"),
              h.get("title_of_class"), h.get("asset_class"),
              h.get("value", 0), h.get("shares", 0), h.get("share_type"),
              h.get("put_call"), h.get("discretion"),
              h.get("portfolio_pct", 0), h.get("prev_pct", 0),
              h.get("pct_change", 0), h.get("shares_change_pct", 0))
             for h in holdings_list]
        )


def get_fund_list():
    """获取所有基金列表"""
    with get_conn() as conn:
        rows = conn.execute("SELECT * FROM funds ORDER BY name_cn").fetchall()
        return [dict(r) for r in rows]


def get_periods(fund_cik):
    """获取某基金可用的季度列表"""
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT period, period_date, total_value FROM filings WHERE fund_cik = ? ORDER BY period_date DESC",
            (fund_cik,)
        ).fetchall()
        return [dict(r) for r in rows]


def get_holdings(fund_cik, period, limit=20):
    """获取某基金某季度的持仓列表 (按市值排序)"""
    with get_conn() as conn:
        rows = conn.execute(
            """SELECT h.*, f.total_value as filing_total_value
               FROM holdings h
               JOIN filings f ON h.filing_id = f.id
               WHERE f.fund_cik = ? AND f.period = ?
               ORDER BY h.value DESC
               LIMIT ?""",
            (fund_cik, period, limit)
        ).fetchall()
        return [dict(r) for r in rows]


def get_all_holdings(fund_cik, period):
    """获取某基金某季度的全部持仓 (不限数量)"""
    with get_conn() as conn:
        rows = conn.execute(
            """SELECT h.*
               FROM holdings h
               JOIN filings f ON h.filing_id = f.id
               WHERE f.fund_cik = ? AND f.period = ?
               ORDER BY h.value DESC""",
            (fund_cik, period)
        ).fetchall()
        return [dict(r) for r in rows]

def get_changes(fund_cik, period):
    """获取持仓变化"""
    with get_conn() as conn:
        rows = conn.execute(
            """SELECT h.issuer, h.cusip, h.ticker, h.asset_class,
                      h.value, h.shares, h.portfolio_pct, h.prev_pct,
                      h.pct_change, h.shares_change_pct
               FROM holdings h
               JOIN filings f ON h.filing_id = f.id
               WHERE f.fund_cik = ? AND f.period = ?
               ORDER BY h.value DESC""",
            (fund_cik, period)
        ).fetchall()
        return [dict(r) for r in rows]


def get_history_composition(fund_cik):
    """获取某基金全部季度的资产类别构成 (用于堆叠柱状图)"""
    with get_conn() as conn:
        rows = conn.execute(
            """SELECT f.period, h.asset_class, SUM(h.value) as class_value, f.total_value
               FROM holdings h
               JOIN filings f ON h.filing_id = f.id
               WHERE f.fund_cik = ?
               GROUP BY f.period, h.asset_class
               ORDER BY f.period_date ASC""",
            (fund_cik,)
        ).fetchall()
        return [dict(r) for r in rows]


def get_filing_total(fund_cik, period):
    """获取某基金某季度的总市值"""
    with get_conn() as conn:
        row = conn.execute(
            "SELECT total_value FROM filings WHERE fund_cik = ? AND period = ?",
            (fund_cik, period)
        ).fetchone()
        return row["total_value"] if row else 0

# ============================================================
# 全局分析查询 (跨基金)
# ============================================================

def get_global_latest_period():
    """获取数据库中最新存在记录的季度"""
    with get_conn() as conn:
        res = conn.execute('''
            SELECT period FROM filings 
            ORDER BY period DESC LIMIT 1
        ''').fetchone()
        return res[0] if res else None


def get_global_changes(period):
    """
    计算特定季度下所有机构的汇总变化，返回 DataFrame
    包含：被多少机构加仓/减仓/新建仓/清仓，以及总市值变化估算
    """
    import pandas as pd
    year, q = period.split("-Q")
    year = int(year)
    q = int(q)
    prev_period = f"{year-1}-Q4" if q == 1 else f"{year}-Q{q-1}"
    
    with get_conn() as conn:
        curr_df = pd.read_sql_query('''
            SELECT h.ticker, h.issuer, h.asset_class, f.fund_cik, 
                   h.shares as curr_shares, h.value as curr_val
            FROM holdings h
            JOIN filings f ON h.filing_id = f.id
            WHERE f.period = ? AND h.put_call IS NULL AND h.ticker != ''
        ''', conn, params=(period,))
        
        prev_df = pd.read_sql_query('''
            SELECT h.ticker, f.fund_cik, h.shares as prev_shares, h.value as prev_val
            FROM holdings h
            JOIN filings f ON h.filing_id = f.id
            WHERE f.period = ? AND h.put_call IS NULL AND h.ticker != ''
        ''', conn, params=(prev_period,))
    
    if curr_df.empty:
        return pd.DataFrame()
        
    merged = pd.merge(
        curr_df, prev_df, 
        on=['ticker', 'fund_cik'], 
        how='outer'
    )
    merged.fillna(0, inplace=True)
    
    merged['is_new'] = (merged['prev_shares'] == 0) & (merged['curr_shares'] > 0)
    merged['is_inc'] = (merged['prev_shares'] > 0) & (merged['curr_shares'] > merged['prev_shares'])
    merged['is_dec'] = (merged['curr_shares'] > 0) & (merged['curr_shares'] < merged['prev_shares'])
    merged['is_exit'] = (merged['prev_shares'] > 0) & (merged['curr_shares'] == 0)
    
    agg_df = merged.groupby(['ticker', 'issuer', 'asset_class']).agg(
        total_curr_val=('curr_val', 'sum'),
        funds_holding=('curr_shares', lambda x: (x > 0).sum()),
        inc_count=('is_inc', 'sum'),
        dec_count=('is_dec', 'sum'),
        new_count=('is_new', 'sum'),
        exit_count=('is_exit', 'sum'),
        val_change=('curr_val', lambda x: x.sum() - merged.loc[x.index, 'prev_val'].sum())
    ).reset_index()
    
    # 填充缺失的名字和行业
    agg_df['issuer'] = agg_df.groupby('ticker')['issuer'].transform('first')
    agg_df['asset_class'] = agg_df.groupby('ticker')['asset_class'].transform('first')
    
    return agg_df

# ============================================================
# 个股分析查询
# ============================================================

def get_stock_holders(ticker, period):
    """
    查询特定季度持有某只股票的所有机构及持仓详情
    返回 DataFrame，按持有市值降序
    """
    import pandas as pd
    year, q = period.split("-Q")
    year = int(year)
    q = int(q)
    prev_period = f"{year-1}-Q4" if q == 1 else f"{year}-Q{q-1}"
    
    with get_conn() as conn:
        # 当前季度的持有情况
        curr_df = pd.read_sql_query('''
            SELECT f.fund_cik, fd.name as fund_name, fd.name_cn as fund_name_cn,
                   h.issuer, h.asset_class,
                   h.shares as curr_shares, h.value as curr_val,
                   h.portfolio_pct as curr_pct
            FROM holdings h
            JOIN filings f ON h.filing_id = f.id
            JOIN funds fd ON f.fund_cik = fd.cik
            WHERE f.period = ? AND h.ticker = ? AND h.put_call IS NULL
        ''', conn, params=(period, ticker))
        
        # 上一季度的持有情况
        prev_df = pd.read_sql_query('''
            SELECT f.fund_cik, h.shares as prev_shares, 
                   h.value as prev_val, h.portfolio_pct as prev_pct
            FROM holdings h
            JOIN filings f ON h.filing_id = f.id
            WHERE f.period = ? AND h.ticker = ? AND h.put_call IS NULL
        ''', conn, params=(prev_period, ticker))
        
    if curr_df.empty:
        return pd.DataFrame()
        
    merged = pd.merge(
        curr_df, prev_df,
        on=['fund_cik'],
        how='left'
    )
    merged.fillna({'prev_shares': 0, 'prev_val': 0, 'prev_pct': 0}, inplace=True)
    
    # 计算变化
    merged['pct_change'] = merged['curr_pct'] - merged['prev_pct']
    merged['shares_change'] = merged['curr_shares'] - merged['prev_shares']
    # 避免除以 0
    merged['shares_change_pct'] = merged.apply(
        lambda row: (row['shares_change'] / row['prev_shares'] * 100) if row['prev_shares'] > 0 
        else (100.0 if row['curr_shares'] > 0 else 0.0), 
        axis=1
    )
    
    # 排序
    merged.sort_values('curr_val', ascending=False, inplace=True)
    
    return merged
