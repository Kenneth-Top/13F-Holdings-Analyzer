# -*- coding: utf-8 -*-
"""
13F 实时监控脚本 (SEC EDGAR Atom Feed)
用于高频监控配置基金是否有新的 13F filing 提交，实现"出了就抓"
"""
import os
import sys
import time
import json
import logging
import xml.etree.ElementTree as ET
from datetime import datetime

import requests

from config import FUNDS, SEC_USER_AGENT, BASE_DIR
from scraper import init_db, scrape_fund

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

SESSION = requests.Session()
SESSION.headers.update({
    "User-Agent": SEC_USER_AGENT,
    "Accept-Encoding": "gzip, deflate",
})

STATE_FILE = os.path.join(BASE_DIR, "data", "monitor_state.json")


def load_state():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    return {}


def save_state(state):
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)


def check_new_filings():
    """检查是否有新的 filings"""
    state = load_state()
    init_db()
    
    new_filings_found = []

    for fund in FUNDS:
        cik = fund["cik"]
        name_cn = fund["name_cn"]
        
        # SEC RSS Feed
        url = f"https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={cik}&type=13F-HR&owner=include&count=5&output=atom"
        try:
            time.sleep(0.15)  # 限速
            resp = SESSION.get(url, timeout=15)
            if resp.status_code != 200:
                logger.warning(f"获取 {name_cn} RSS 失败: HTTP {resp.status_code}")
                continue
                
            root = ET.fromstring(resp.text)
            ns = {'atom': 'http://www.w3.org/2005/Atom'}
            
            # 找最新的一个 entry
            entry = root.find('atom:entry', ns)
            if entry is not None:
                title = entry.find('atom:title', ns).text  # 包含 form type 和 accession number
                updated = entry.find('atom:updated', ns).text
                
                # 提取 Accession Number
                # Title 示例: "13F-HR - Berkshire Hathaway Inc (0001067983) (Filer)"
                # 我们通过 details 找更精确的 acc_num
                id_tag = entry.find('atom:id', ns).text
                # id_tag 示例: "urn:tag:sec.gov,2008:accession-number=0001067983-24-000001"
                acc_num = id_tag.split("accession-number=")[-1] if "accession-number=" in id_tag else ""
                
                if not acc_num:
                    continue
                
                last_seen_acc = state.get(cik, "")
                if acc_num != last_seen_acc:
                    logger.info(f"🚨 发现 {name_cn} 的新提交! Accession={acc_num}, Updated={updated}")
                    new_filings_found.append((fund, acc_num))
                    state[cik] = acc_num
                else:
                    logger.debug(f"{name_cn} 无新提交")
        except Exception as e:
            logger.error(f"处理 {name_cn} RSS 异常: {e}")

    # 如果有新的提交，触发增量抓取
    if new_filings_found:
        logger.info(f"共发现 {len(new_filings_found)} 个新提交，开始增量采集...")
        for fund, acc_num in new_filings_found:
            run_incremental_scrape(fund, acc_num)
        
        # 采集成功后保存状态
        save_state(state)
        logger.info("增量采集完成并保存状态。")
    else:
        logger.info("未发现新的 13F 提交。")


def run_incremental_scrape(fund, acc_num):
    """只抓取这个基金最新的 filing"""
    logger.info(f"========== 增量采集: {fund['name_cn']} ({fund['name']}) ==========")
    try:
        # 借用已经做好的 scrape_fund 单独采集该基金的最新一期
        scrape_fund(
            cik=fund["cik"],
            name=fund["name"],
            name_cn=fund["name_cn"],
            max_quarters=1,
            latest_only=True
        )
    except Exception as e:
        logger.error(f"增量采集 {fund['name_cn']} 失败: {e}")


if __name__ == "__main__":
    logger.info("开始检查 13F 全网动态...")
    check_new_filings()
