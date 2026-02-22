import logging
import requests
import re
from bs4 import BeautifulSoup
from backend.config import SEC_REQUEST_DELAY
import time

logger = logging.getLogger(__name__)

DATAROMA_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
}

def _parse_dataroma_value(val_str):
    """Convert $12,345,000 to thousands (float) -> 12345.0"""
    if not val_str: return 0.0
    val_str = val_str.replace('$', '').replace(',', '').strip()
    try:
        return float(val_str) / 1000.0
    except ValueError:
        return 0.0

def _parse_dataroma_shares(share_str):
    """Convert 1,234,567 to int"""
    if not share_str: return 0
    share_str = share_str.replace(',', '').strip()
    try:
        return int(share_str)
    except ValueError:
        return 0

def _parse_dataroma_pct(pct_str):
    """Convert 12.34% or 12.34 to float 12.34"""
    if not pct_str: return 0.0
    pct_str = pct_str.replace('%', '').strip()
    try:
        return float(pct_str)
    except ValueError:
        return 0.0

def scrape_dataroma_fund(dataroma_id, target_quarter=None):
    """
    Scrape holdings for a specific manager from Dataroma.
    Returns: (holdings_list, actual_period_str)
    holdings_list item: {
        "issuer": "APPLE INC",
        "ticker": "AAPL",
        "value": 12345.0, # in thousands
        "shares": 1000000,
        "portfolio_pct": 5.5,
        "title_of_class": "COM",
        "put_call": "",
        "share_type": "SH",
        "discretion": "SOLE"
    }
    actual_period_str: e.g. "2023-Q4"
    """
    url = f"https://www.dataroma.com/m/holdings.php?m={dataroma_id}"
    # Dataroma doesn't seem to support an easy quarter param in the same way, but usually shows the latest.
    
    time.sleep(1) # delay to be polite
    try:
        resp = requests.get(url, headers=DATAROMA_HEADERS, timeout=15)
        resp.raise_for_status()
    except Exception as e:
        logger.error(f"Failed to fetch Dataroma info for {dataroma_id}: {e}")
        return [], None

    soup = BeautifulSoup(resp.text, 'html.parser')
    
    # Extract Period
    # Dataroma page usually contains text like "Period:" followed by "Q4 2025"
    page_text = soup.get_text(separator=' ')
    period_match = re.search(r'Period:\s+(Q[1-4])\s+(\d{4})', page_text)
    actual_period = None
    if period_match:
        actual_period = f"{period_match.group(2)}-{period_match.group(1)}"
    else:
        logger.warning(f"Could not find period for {dataroma_id} on Dataroma.")
        # fallback, maybe it's not present
        
    holdings = []
    
    # Find grid
    grid = soup.find('table', id='grid')
    if not grid:
        logger.warning(f"No holdings grid found for {dataroma_id}")
        return holdings, actual_period
        
    tbody = grid.find('tbody')
    if not tbody:
        return holdings, actual_period
        
    rows = tbody.find_all('tr')
    for row in rows:
        tds = row.find_all('td')
        # Expecting at least 7 cols: 
        # 0: icon, 1: sym-desc (e.g. AAPL - Apple Inc.), 2: portfolio_pct, 3: history, 4: shares, 5: price, 6: value
        if len(tds) < 7:
            continue
            
        sym_desc = tds[1].get_text(strip=True) # e.g. "AAPL - Apple Inc." or "NBR- Nabors Industries Ltd."
        
        parts = re.split(r'\s*-\s*', sym_desc, maxsplit=1)
        if len(parts) == 2:
            ticker = parts[0]
            issuer = parts[1]
        else:
            ticker = sym_desc
            issuer = sym_desc
            
        pct_str = tds[2].get_text(strip=True)
        shares_str = tds[4].get_text(strip=True)
        value_str = tds[6].get_text(strip=True)
        
        # Build holding
        holding = {
            "issuer": issuer.strip().upper(),
            "ticker": ticker.strip().upper(),
            "value": _parse_dataroma_value(value_str),
            "shares": _parse_dataroma_shares(shares_str),
            "portfolio_pct": _parse_dataroma_pct(pct_str),
            "title_of_class": "COM", # Default
            "put_call": "",
            "share_type": "SH", # Default
            "discretion": "SOLE" # Default
        }
        holdings.append(holding)
        
    # === 如果指定了具体历史季度且不等于最新季度，则需退而求其次地遍历每只股票的历史页回溯 ===
    if target_quarter and target_quarter != actual_period:
        logger.info(f"Targeting historic qt {target_quarter} for {dataroma_id}. Starting deep scraping...")
        historic_holdings = []
        target_yr, target_q = target_quarter.split("-Q")
        
        for base_hdg in holdings:
            sym = base_hdg["ticker"]
            hist_url = f"https://www.dataroma.com/m/hist/hist.php?f={dataroma_id}&s={sym}"
            try:
                # 礼貌并发
                time.sleep(0.5)
                h_resp = requests.get(hist_url, headers=DATAROMA_HEADERS, timeout=10)
                h_soup = BeautifulSoup(h_resp.text, 'html.parser')
            except Exception:
                continue
                
            h_grid = h_soup.find('table', id='grid')
            if not h_grid or not h_grid.find('tbody'):
                continue
                
            for h_row in h_grid.find('tbody').find_all('tr'):
                h_tds = h_row.find_all('td')
                if len(h_tds) >= 5:
                    period_text = h_tds[0].text.replace('\xa0', ' ').strip() # e.g. "2025   Q3"
                    # 这里需规整化成 YYYY-QX
                    p_parts = period_text.split()
                    if len(p_parts) >= 2:
                        p_yr, p_q = p_parts[0], p_parts[-1]
                        if p_yr == target_yr and p_q == f"Q{target_q}":
                            # 命中目标带返回！
                            h_shares = _parse_dataroma_shares(h_tds[1].text)
                            # value 在这里可能是 "Buy", "Add XX%", 所以此页并没存绝对市值估值，仅有 Pct 
                            # 鉴于 Dataroma 个股历史并未提供精准的过往季度 Value 我们使用简单的占比替代
                            h_pct = _parse_dataroma_pct(h_tds[4].text)
                            
                            historic_holdings.append({
                                "issuer": base_hdg["issuer"],
                                "ticker": sym,
                                "value": 0.0, # 缺失绝对值，前端只展示占比
                                "shares": h_shares,
                                "portfolio_pct": h_pct,
                                "title_of_class": "COM",
                                "put_call": "",
                                "share_type": "SH",
                                "discretion": "SOLE"
                            })
                            break # 找到当前股票在这个季度的行就去下一个股票
                            
        return historic_holdings, target_quarter
        
    return holdings, actual_period
