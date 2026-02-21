# -*- coding: utf-8 -*-
"""
基于 yfinance 的行业分类模块
使用 Yahoo Finance GICS 标准分类，带本地 SQLite 缓存
回退策略：yfinance -> 关键词匹配 -> "股票"
"""

import logging
import sqlite3
import time
import os

logger = logging.getLogger(__name__)

# 缓存数据库路径（与 holdings.db 同目录）
_CACHE_DB = os.path.join(os.path.dirname(__file__), "..", "data", "sector_cache.db")

# yfinance GICS sector -> 中文大类
SECTOR_ZH = {
    "Technology": "科技",
    "Financial Services": "金融",
    "Consumer Cyclical": "消费-可选",
    "Consumer Defensive": "消费-必需",
    "Healthcare": "医疗",
    "Energy": "能源",
    "Communication Services": "通讯",
    "Industrials": "工业",
    "Basic Materials": "原材料",
    "Real Estate": "房地产",
    "Utilities": "公用事业",
    # 兼容旧版 yfinance 分组名
    "Financial": "金融",
    "Consumer Staples": "消费-必需",
    "Consumer Discretionary": "消费-可选",
    "Information Technology": "科技",
    "Materials": "原材料",
    "Telecommunications": "通讯",
}

# 期权 / 特殊类型 -> 直接分类
PUT_CALL_MAP = {
    "Put": "期权-PUT",
    "Call": "期权-CALL",
}

# 知名 ETF ticker 直接映射（补充 yfinance 的缺口）
ETF_MAP = {
    "SPY": "ETF-大型股平衡型", "IVV": "ETF-大型股平衡型", "VOO": "ETF-大型股平衡型",
    "QQQ": "ETF-科技", "VTI": "ETF-综合市场", "GLD": "ETF-黄金",
    "EEM": "ETF-新兴市场", "VEA": "ETF-发达市场", "AGG": "债券",
    "TLT": "债券", "IEF": "债券", "SHY": "债券",
    "VNQ": "ETF-房地产", "XLF": "ETF-金融", "XLK": "ETF-科技",
    "IAU": "ETF-黄金", "IEMG": "ETF-新兴市场",
}


def _init_cache():
    """初始化缓存数据库"""
    os.makedirs(os.path.dirname(_CACHE_DB), exist_ok=True)
    conn = sqlite3.connect(_CACHE_DB)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS sector_cache (
            ticker TEXT PRIMARY KEY,
            sector_en TEXT,
            sector_zh TEXT,
            updated_ts INTEGER
        )
    """)
    conn.commit()
    conn.close()


def _get_cached(ticker: str):
    """从缓存读取（返回中文分类或 None）"""
    try:
        conn = sqlite3.connect(_CACHE_DB)
        row = conn.execute(
            "SELECT sector_zh FROM sector_cache WHERE ticker = ?", (ticker,)
        ).fetchone()
        conn.close()
        return row[0] if row else None
    except Exception:
        return None


def _set_cache(ticker: str, sector_en: str, sector_zh: str):
    """写入缓存"""
    try:
        conn = sqlite3.connect(_CACHE_DB)
        conn.execute(
            "INSERT OR REPLACE INTO sector_cache VALUES (?, ?, ?, ?)",
            (ticker, sector_en, sector_zh, int(time.time()))
        )
        conn.commit()
        conn.close()
    except Exception:
        pass


def _fetch_from_yfinance(ticker: str) -> str:
    """从 yfinance 获取行业分类，返回中文或 None"""
    try:
        import yfinance as yf
        info = yf.Ticker(ticker).info
        sector_en = info.get("sector", "") or info.get("quoteType", "")
        if sector_en == "ETF":
            return "ETF"
        zh = SECTOR_ZH.get(sector_en)
        return zh  # 可能为 None
    except Exception as e:
        logger.debug(f"yfinance 获取 {ticker} 失败: {e}")
        return None


def get_sector_yf(ticker: str, issuer_name: str, title_of_class: str, put_call: str) -> str:
    """
    主入口：获取标准化行业分类
    优先级：期权 → ETF直接映射 → yfinance缓存 → yfinance联网 → 关键词回退
    """
    # 1. 期权
    if put_call and put_call in PUT_CALL_MAP:
        return PUT_CALL_MAP[put_call]

    ticker_upper = (ticker or "").upper().strip()

    # 2. ETF 直接命中
    if ticker_upper in ETF_MAP:
        return ETF_MAP[ticker_upper]

    # 3. 有 ticker → 查缓存 → 查 yfinance
    if ticker_upper:
        cached = _get_cached(ticker_upper)
        if cached is not None:
            return cached if cached else "股票"  # 空字符串表示 yf 无结果

        # 联网查询
        sector_zh = _fetch_from_yfinance(ticker_upper)
        # 缓存结果（空串表示无法识别）
        _set_cache(ticker_upper, "", sector_zh or "")
        if sector_zh:
            return sector_zh

    # 4. 关键词回退（来自原 sector_mapper）
    from sector_mapper import get_sector as _fallback
    return _fallback(ticker, issuer_name, title_of_class, put_call)


def prefetch_sectors(tickers: list):
    """
    批量预热缓存。采集前调用，避免逐条调用 yfinance 时的长延迟。
    """
    _init_cache()
    unique = [t.upper() for t in set(tickers) if t]
    if not unique:
        return

    try:
        import yfinance as yf
    except ImportError:
        logger.warning("yfinance 未安装，行业分类将使用关键词回退")
        return

    # 过滤已缓存
    to_fetch = [t for t in unique if t not in ETF_MAP and _get_cached(t) is None]
    if not to_fetch:
        logger.info(f"  行业缓存命中 {len(unique)} 个 ticker，无需刷新")
        return

    logger.info(f"  批量获取 {len(to_fetch)} 个 ticker 的行业分类...")
    try:
        # yfinance 支持批量 download，但 info 需逐一获取。分批处理
        batch_size = 20
        for i in range(0, len(to_fetch), batch_size):
            batch = to_fetch[i:i+batch_size]
            for ticker in batch:
                sector_zh = _fetch_from_yfinance(ticker)
                _set_cache(ticker, "", sector_zh or "")
            time.sleep(0.5)  # 小延迟避免被限流
    except Exception as e:
        logger.warning(f"  批量预热行业缓存失败: {e}")

    logger.info(f"  行业缓存预热完成")
