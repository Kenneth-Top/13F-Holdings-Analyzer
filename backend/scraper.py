# -*- coding: utf-8 -*-
"""
13F 持仓数据采集器 - 基于 Dataroma
从 Dataroma 抓取超级投资人的持仓数据（当前季度 + 历史季度）
"""

import os
import re
import sys
import csv
import time
import logging
import argparse
import requests
from bs4 import BeautifulSoup

from backend.config import (
    FUNDS, DATAROMA_BASE, HEADERS, REQUEST_DELAY,
    DATA_DIR, HOLDINGS_DIR, FUNDS_CSV
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

SESSION = requests.Session()
SESSION.headers.update(HEADERS)


# ============================================================
# 工具函数
# ============================================================
def _throttle():
    time.sleep(REQUEST_DELAY)


def _parse_value(s):
    """'$1,234,567' -> 1234567.0"""
    if not s:
        return 0.0
    s = s.replace('$', '').replace(',', '').strip()
    try:
        return float(s)
    except ValueError:
        return 0.0


def _parse_shares(s):
    """'1,234,567' -> 1234567"""
    if not s:
        return 0
    s = s.replace(',', '').strip()
    try:
        return int(s)
    except ValueError:
        return 0


def _parse_pct(s):
    """'12.34%' -> 12.34"""
    if not s:
        return 0.0
    s = s.replace('%', '').strip()
    try:
        return float(s)
    except ValueError:
        return 0.0


def _normalize_period(text):
    """'Q4 2025' or '2025   Q4' -> '2025-Q4'"""
    text = text.replace('\xa0', ' ').strip()
    # Pattern: Q4 2025
    m = re.search(r'(Q[1-4])\s+(\d{4})', text)
    if m:
        return f"{m.group(2)}-{m.group(1)}"
    # Pattern: 2025 Q4
    m = re.search(r'(\d{4})\s+(Q[1-4])', text)
    if m:
        return f"{m.group(1)}-{m.group(2)}"
    return None


def _ensure_dirs():
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(HOLDINGS_DIR, exist_ok=True)


def _save_holdings_csv(fund_id, period, holdings):
    """保存持仓数据到 CSV"""
    fund_dir = os.path.join(HOLDINGS_DIR, fund_id)
    os.makedirs(fund_dir, exist_ok=True)
    filepath = os.path.join(fund_dir, f"{period}.csv")

    fieldnames = ["ticker", "issuer", "portfolio_pct", "shares", "value",
                   "reported_price", "activity"]
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for h in holdings:
            writer.writerow({
                "ticker": h.get("ticker", ""),
                "issuer": h.get("issuer", ""),
                "portfolio_pct": h.get("portfolio_pct", 0),
                "shares": h.get("shares", 0),
                "value": h.get("value", 0),
                "reported_price": h.get("reported_price", 0),
                "activity": h.get("activity", ""),
            })
    return filepath


def _save_funds_csv(fund_results):
    """保存基金汇总信息"""
    filepath = FUNDS_CSV
    fieldnames = ["fund_id", "name", "name_cn", "portfolio_value",
                   "num_holdings", "latest_period"]
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in fund_results:
            writer.writerow(r)


# ============================================================
# Dataroma 爬虫核心
# ============================================================
def scrape_current_holdings(fund_id):
    """
    抓取某基金的当前季度持仓
    Returns: (holdings_list, period_str, portfolio_value_str)
    """
    url = f"{DATAROMA_BASE}/holdings.php?m={fund_id}"
    _throttle()

    try:
        resp = SESSION.get(url, timeout=20)
        resp.raise_for_status()
    except Exception as e:
        logger.error(f"[{fund_id}] 请求失败: {e}")
        return [], None, 0

    soup = BeautifulSoup(resp.text, "html.parser")

    # 提取季度信息
    page_text = soup.get_text(separator=" ")
    period = None
    period_match = re.search(r'Period:\s*(Q[1-4])\s+(\d{4})', page_text)
    if period_match:
        period = f"{period_match.group(2)}-{period_match.group(1)}"

    # 提取总市值
    portfolio_value = 0
    val_match = re.search(r'Portfolio\s+value[:\s]*\$?([\d,\.]+)\s*(B|M|K)?', page_text, re.IGNORECASE)
    if val_match:
        num = float(val_match.group(1).replace(',', ''))
        suffix = (val_match.group(2) or '').upper()
        if suffix == 'B':
            portfolio_value = num * 1_000_000_000
        elif suffix == 'M':
            portfolio_value = num * 1_000_000
        elif suffix == 'K':
            portfolio_value = num * 1_000
        else:
            portfolio_value = num

    # 解析持仓表格
    holdings = []
    grid = soup.find("table", id="grid")
    if not grid:
        logger.warning(f"[{fund_id}] 未找到持仓表格")
        return holdings, period, portfolio_value

    tbody = grid.find("tbody")
    if not tbody:
        return holdings, period, portfolio_value

    for row in tbody.find_all("tr"):
        tds = row.find_all("td")
        if len(tds) < 7:
            continue

        # 列: 0=icon, 1=stock(ticker-name), 2=%portfolio, 3=recent activity,
        #      4=shares, 5=reported price, 6=value
        sym_desc = tds[1].get_text(strip=True)
        parts = re.split(r'\s*-\s*', sym_desc, maxsplit=1)
        ticker = parts[0].strip().upper() if parts else ""
        issuer = parts[1].strip() if len(parts) > 1 else sym_desc

        pct = _parse_pct(tds[2].get_text(strip=True))
        activity = tds[3].get_text(strip=True) if len(tds) > 3 else ""
        shares = _parse_shares(tds[4].get_text(strip=True))
        reported_price = _parse_value(tds[5].get_text(strip=True)) if len(tds) > 5 else 0
        value = _parse_value(tds[6].get_text(strip=True))

        holdings.append({
            "ticker": ticker,
            "issuer": issuer,
            "portfolio_pct": round(pct, 2),
            "shares": shares,
            "value": round(value, 2),
            "reported_price": round(reported_price, 2),
            "activity": activity,
        })

    return holdings, period, portfolio_value


def scrape_stock_history(fund_id, ticker):
    """
    抓取某基金某只股票的历史持仓
    Returns: list of {period, shares, portfolio_pct, activity}
    """
    url = f"{DATAROMA_BASE}/hist/hist.php?f={fund_id}&s={ticker}"
    _throttle()

    try:
        resp = SESSION.get(url, timeout=15)
        resp.raise_for_status()
    except Exception as e:
        logger.debug(f"[{fund_id}/{ticker}] 历史请求失败: {e}")
        return []

    soup = BeautifulSoup(resp.text, "html.parser")
    grid = soup.find("table", id="grid")
    if not grid:
        return []

    tbody = grid.find("tbody")
    if not tbody:
        return []

    history = []
    for row in tbody.find_all("tr"):
        tds = row.find_all("td")
        if len(tds) < 5:
            continue

        period_text = tds[0].get_text(strip=True)
        period = _normalize_period(period_text)
        if not period:
            continue

        shares = _parse_shares(tds[1].get_text(strip=True))
        activity = tds[2].get_text(strip=True) if len(tds) > 2 else ""
        pct = _parse_pct(tds[4].get_text(strip=True)) if len(tds) > 4 else 0

        history.append({
            "period": period,
            "shares": shares,
            "portfolio_pct": round(pct, 2),
            "activity": activity,
        })

    return history


# ============================================================
# 编排逻辑
# ============================================================
def scrape_fund(fund_id, name, name_cn, with_history=True, max_hist_quarters=4):
    """
    采集单个基金的持仓数据（当前 + 可选历史）
    """
    logger.info(f"{'='*60}")
    logger.info(f"采集: {name_cn} ({fund_id})")
    logger.info(f"{'='*60}")

    # Step 1: 当前持仓
    holdings, period, portfolio_value = scrape_current_holdings(fund_id)
    if not holdings or not period:
        logger.warning(f"[{fund_id}] 无法获取当前持仓数据")
        return None

    logger.info(f"[{fund_id}] 当前季度: {period}, 持仓数: {len(holdings)}, "
                f"总市值: ${portfolio_value:,.0f}")
    _save_holdings_csv(fund_id, period, holdings)

    # Step 2: 历史持仓 (通过每只股票的历史页面)
    if with_history and holdings:
        logger.info(f"[{fund_id}] 正在采集历史数据...")
        # 收集所有历史记录，按季度分组
        history_by_period = {}

        for i, h in enumerate(holdings):
            ticker = h["ticker"]
            if not ticker:
                continue

            stock_hist = scrape_stock_history(fund_id, ticker)
            for sh in stock_hist:
                p = sh["period"]
                if p == period:  # 跳过当前季度（已有）
                    continue
                if p not in history_by_period:
                    history_by_period[p] = []
                history_by_period[p].append({
                    "ticker": ticker,
                    "issuer": h["issuer"],
                    "portfolio_pct": sh["portfolio_pct"],
                    "shares": sh["shares"],
                    "value": 0,  # 历史市值无法从此页获取
                    "reported_price": 0,
                    "activity": sh["activity"],
                })

            if (i + 1) % 10 == 0:
                logger.info(f"[{fund_id}] 历史进度: {i+1}/{len(holdings)} 只股票")

        # 保存历史季度（只保留最近 N 个季度）
        sorted_periods = sorted(history_by_period.keys(), reverse=True)
        for p in sorted_periods[:max_hist_quarters]:
            hist_holdings = history_by_period[p]
            # 按 portfolio_pct 降序排列
            hist_holdings.sort(key=lambda x: x["portfolio_pct"], reverse=True)
            _save_holdings_csv(fund_id, p, hist_holdings)
            logger.info(f"[{fund_id}] 历史季度 {p}: {len(hist_holdings)} 只股票")

    return {
        "fund_id": fund_id,
        "name": name,
        "name_cn": name_cn,
        "portfolio_value": portfolio_value,
        "num_holdings": len(holdings),
        "latest_period": period,
    }


def scrape_all(with_history=True, max_hist_quarters=4, target_fund=None):
    """采集所有基金"""
    _ensure_dirs()

    if target_fund:
        funds_to_scrape = [f for f in FUNDS if f["fund_id"] == target_fund]
        if not funds_to_scrape:
            logger.error(f"未找到基金: {target_fund}")
            logger.info("可用基金: " + ", ".join(f["fund_id"] for f in FUNDS))
            return
    else:
        funds_to_scrape = FUNDS

    results = []
    failed = []

    # 如果是全量采集，先读取已有的 funds.csv 保留之前的结果
    existing_results = {}
    if os.path.exists(FUNDS_CSV) and not target_fund:
        try:
            import pandas as pd
            df = pd.read_csv(FUNDS_CSV)
            for _, row in df.iterrows():
                existing_results[row["fund_id"]] = row.to_dict()
        except Exception:
            pass

    for i, fund in enumerate(funds_to_scrape):
        fid = fund["fund_id"]
        logger.info(f"\n[{i+1}/{len(funds_to_scrape)}] 开始采集 {fund['name_cn']}...")

        try:
            result = scrape_fund(
                fid, fund["name"], fund["name_cn"],
                with_history=with_history,
                max_hist_quarters=max_hist_quarters
            )
            if result:
                results.append(result)
                existing_results[fid] = result
            else:
                failed.append(fid)
                # 保留旧数据
                if fid in existing_results:
                    results.append(existing_results[fid])
        except Exception as e:
            logger.error(f"[{fid}] 采集异常: {e}")
            failed.append(fid)
            if fid in existing_results:
                results.append(existing_results[fid])

    # 合并所有结果写入 funds.csv
    all_results = []
    for fid, data in existing_results.items():
        all_results.append(data)
    # 添加本次新采集但之前不存在的
    existing_ids = set(existing_results.keys())
    for r in results:
        if r["fund_id"] not in existing_ids:
            all_results.append(r)

    # 按 name_cn 排序
    all_results.sort(key=lambda x: x.get("name_cn", ""))
    _save_funds_csv(all_results)

    # 汇总
    logger.info(f"\n{'='*60}")
    logger.info(f"采集完成！成功: {len(results)}, 失败: {len(failed)}")
    if failed:
        logger.info(f"失败基金: {', '.join(failed)}")
    logger.info(f"{'='*60}")


# ============================================================
# CLI 入口
# ============================================================
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="13F 持仓数据采集器 (Dataroma)")
    parser.add_argument("--fund", type=str, help="指定基金 ID (如 BRK, psc, SAM)")
    parser.add_argument("--no-history", action="store_true", help="不采集历史数据")
    parser.add_argument("--quarters", type=int, default=4, help="历史季度数 (默认 4)")
    args = parser.parse_args()

    scrape_all(
        with_history=not args.no_history,
        max_hist_quarters=args.quarters,
        target_fund=args.fund
    )
