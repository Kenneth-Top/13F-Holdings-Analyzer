# -*- coding: utf-8 -*-
"""
CSV 数据访问层 - 替代 SQLite database.py
提供基于 CSV 文件的持仓数据读取函数
"""

import os
import glob
import pandas as pd
from backend.config import DATA_DIR, HOLDINGS_DIR, FUNDS_CSV


def get_fund_list():
    """获取所有基金列表"""
    if not os.path.exists(FUNDS_CSV):
        return pd.DataFrame()
    df = pd.read_csv(FUNDS_CSV, encoding="utf-8")
    return df.sort_values("name_cn").reset_index(drop=True)


def get_periods(fund_id):
    """获取某基金可用的季度列表（降序）"""
    fund_dir = os.path.join(HOLDINGS_DIR, fund_id)
    if not os.path.isdir(fund_dir):
        return []
    files = glob.glob(os.path.join(fund_dir, "*.csv"))
    periods = []
    for f in files:
        name = os.path.splitext(os.path.basename(f))[0]
        if name.startswith("20") and "-Q" in name:
            periods.append(name)
    return sorted(periods, reverse=True)


def get_holdings(fund_id, period):
    """获取某基金某季度的持仓数据"""
    filepath = os.path.join(HOLDINGS_DIR, fund_id, f"{period}.csv")
    if not os.path.exists(filepath):
        return pd.DataFrame()
    df = pd.read_csv(filepath, encoding="utf-8")
    # 确保数值列为数值类型
    for col in ["portfolio_pct", "shares", "value", "reported_price"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
    return df.sort_values("portfolio_pct", ascending=False).reset_index(drop=True)


def get_all_fund_ids():
    """获取所有有数据的基金 ID"""
    if not os.path.isdir(HOLDINGS_DIR):
        return []
    return [d for d in os.listdir(HOLDINGS_DIR)
            if os.path.isdir(os.path.join(HOLDINGS_DIR, d))]


def get_global_latest_period():
    """获取全局最新的季度"""
    all_periods = set()
    for fid in get_all_fund_ids():
        all_periods.update(get_periods(fid))
    if not all_periods:
        return None
    return max(all_periods)


def get_changes(fund_id, period):
    """
    获取某基金某季度的持仓变化（与上一季度对比）
    返回包含 pct_change, shares_change_pct 的 DataFrame
    """
    current = get_holdings(fund_id, period)
    if current.empty:
        return current

    # 找到上一个季度
    periods = get_periods(fund_id)
    idx = periods.index(period) if period in periods else -1
    if idx < 0 or idx >= len(periods) - 1:
        # 没有上一季度的数据
        current["prev_pct"] = 0.0
        current["pct_change"] = current["portfolio_pct"]
        current["shares_change_pct"] = 0.0
        return current

    prev_period = periods[idx + 1]
    prev = get_holdings(fund_id, prev_period)

    if prev.empty:
        current["prev_pct"] = 0.0
        current["pct_change"] = current["portfolio_pct"]
        current["shares_change_pct"] = 0.0
        return current

    # 合并当前和上一季度
    prev_map = {row["ticker"]: row for _, row in prev.iterrows()}

    prev_pcts = []
    pct_changes = []
    shares_changes = []
    for _, row in current.iterrows():
        ticker = row["ticker"]
        if ticker in prev_map:
            p = prev_map[ticker]
            prev_pct = p["portfolio_pct"]
            prev_shares = p["shares"]
        else:
            prev_pct = 0.0
            prev_shares = 0

        prev_pcts.append(prev_pct)
        pct_changes.append(row["portfolio_pct"] - prev_pct)
        if prev_shares > 0:
            shares_changes.append(
                (row["shares"] - prev_shares) / prev_shares * 100
            )
        else:
            shares_changes.append(0.0)

    current["prev_pct"] = prev_pcts
    current["pct_change"] = pct_changes
    current["shares_change_pct"] = shares_changes
    return current


def get_global_changes(period):
    """
    全局宏观分析：统计所有基金在某季度的持仓变化汇总
    """
    funds_df = get_fund_list()
    if funds_df.empty:
        return pd.DataFrame()

    all_changes = []
    for _, fund in funds_df.iterrows():
        fid = fund["fund_id"]
        changes = get_changes(fid, period)
        if changes.empty:
            continue
        changes["fund_id"] = fid
        changes["fund_name_cn"] = fund["name_cn"]
        all_changes.append(changes)

    if not all_changes:
        return pd.DataFrame()

    df = pd.concat(all_changes, ignore_index=True)

    # 聚合
    agg = df.groupby(["ticker", "issuer"]).agg(
        funds_holding=("fund_id", "nunique"),
        total_curr_val=("value", "sum"),
        val_change=("pct_change", "sum"),
        inc_count=("pct_change", lambda x: (x > 0).sum()),
        dec_count=("pct_change", lambda x: (x < 0).sum()),
        new_count=("prev_pct", lambda x: (x == 0).sum()),
        exit_count=("portfolio_pct", lambda x: (x == 0).sum()),
    ).reset_index()

    return agg.sort_values("funds_holding", ascending=False)


def get_stock_holders(ticker, period):
    """
    查询特定季度持有某只股票的所有基金
    """
    funds_df = get_fund_list()
    if funds_df.empty:
        return pd.DataFrame()

    holders = []
    for _, fund in funds_df.iterrows():
        fid = fund["fund_id"]
        changes = get_changes(fid, period)
        if changes.empty:
            continue

        match = changes[changes["ticker"].str.upper() == ticker.upper()]
        if match.empty:
            continue

        row = match.iloc[0]
        holders.append({
            "fund_id": fid,
            "fund_name": fund["name"],
            "fund_name_cn": fund["name_cn"],
            "curr_val": row["value"],
            "curr_shares": row["shares"],
            "curr_pct": row["portfolio_pct"],
            "prev_pct": row.get("prev_pct", 0),
            "pct_change": row.get("pct_change", 0),
            "shares_change_pct": row.get("shares_change_pct", 0),
        })

    if not holders:
        return pd.DataFrame()
    return pd.DataFrame(holders).sort_values("curr_val", ascending=False)
