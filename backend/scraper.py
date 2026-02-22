# -*- coding: utf-8 -*-
"""
13F 数据采集器
从 SEC EDGAR 官方 API 抓取机构投资者的 13F-HR 持仓报告
"""

import re
import sys
import time
import json
import logging
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta

import requests

from backend.config import (
    SEC_USER_AGENT, SEC_BASE_URL, SEC_ARCHIVES_URL,
    INITIAL_QUARTERS,
    FUNDS,
    SEC_REQUEST_DELAY,
)
from backend.sector_mapper_yf import get_sector_yf as get_sector, prefetch_sectors, _init_cache
from backend.database import (
    init_db,
    upsert_fund,
    get_filing,
    upsert_filing,
    insert_holdings,
    get_all_holdings,
)

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


def _throttle():
    """请求速率控制"""
    time.sleep(SEC_REQUEST_DELAY)


def _get_json(url):
    """GET 请求并返回 JSON"""
    _throttle()
    logger.debug(f"GET {url}")
    resp = SESSION.get(url, timeout=30)
    resp.raise_for_status()
    return resp.json()


def _get_text(url):
    """GET 请求并返回文本"""
    _throttle()
    logger.debug(f"GET {url}")
    resp = SESSION.get(url, timeout=30)
    resp.raise_for_status()
    return resp.text


def _period_to_quarter(date_str):
    """将日期 '2025-12-31' 转为季度 '2025-Q4'"""
    dt = datetime.strptime(date_str, "%Y-%m-%d")
    quarter = (dt.month - 1) // 3 + 1
    return f"{dt.year}-Q{quarter}"





def normalize_name(name):
    """移除标点符号及常见公司后缀，用于提升名称匹配率"""
    name = name.upper()
    name = re.sub(r'[^\w\s]', '', name)
    name = " " + name + " "
    
    # 常用 13F 报表内部短语展开
    name = name.replace(" FINL ", " FINANCIAL ")
    name = name.replace(" PETE ", " PETROLEUM ")
    name = name.replace(" HLDG ", " HOLDING ")
    name = name.replace(" HLDGS ", " HOLDINGS ")
    name = name.replace(" GRP ", " GROUP ")
    name = name.replace(" NATL ", " NATIONAL ")
    
    for suffix in [" INC ", " CORP ", " CORPORATION ", " CO ", " LTD ", " PLC ", " LLC ", " LP ", " COMPANY ", " DE ", " OF ", " THE "]:
        name = name.replace(suffix, " ")
    # 清理末尾特殊标记
    name = name.replace(" NEW ", " ")
    return " ".join(name.split())


def _build_cusip_ticker_map():
    """
    尝试构建公司名称 -> ticker 的映射体系。
    使用 SEC 提供的 company_tickers.json 作为来源。
    返回包含 exact_map (原生大写) 和 norm_map (归一化名字) 的字典。
    """
    maps = {"exact": {}, "norm": {}}
    try:
        data = _get_json("https://www.sec.gov/files/company_tickers.json")
        for _, item in data.items():
            title = item.get("title", "").upper()
            ticker = item.get("ticker", "")
            if not ticker or not title:
                continue
            if title not in maps["exact"]:
                maps["exact"][title] = ticker
            norm_title = normalize_name(title)
            if norm_title not in maps["norm"]:
                maps["norm"][norm_title] = ticker
    except Exception as e:
        logger.warning(f"无法加载 ticker 映射表: {e}")
    return maps


def get_fund_submissions(cik):
    """
    获取基金的提交历史
    返回: dict 包含 recent filings 和 company info
    """
    # CIK 需要补齐到 10 位
    cik_padded = cik.lstrip("0").zfill(10)
    url = f"{SEC_BASE_URL}/submissions/CIK{cik_padded}.json"
    data = _get_json(url)
    return data


def get_13f_filings(submissions, max_count=None):
    """
    从提交历史中提取 13F-HR 类型的 filing 信息
    返回: list of dict, 每个包含 accession, filing_date, period_of_report
    """
    recent = submissions.get("filings", {}).get("recent", {})
    forms = recent.get("form", [])
    accessions = recent.get("accessionNumber", [])
    dates = recent.get("filingDate", [])
    report_dates = recent.get("reportDate", [])
    primary_docs = recent.get("primaryDocument", [])

    filings_13f = []
    for i, form in enumerate(forms):
        if form in ("13F-HR", "13F-HR/A"):
            filings_13f.append({
                "accession": accessions[i],
                "filing_date": dates[i],
                "period_of_report": report_dates[i],
                "primary_document": primary_docs[i] if i < len(primary_docs) else "",
                "form": form,
            })

    # 按报告期降序排列
    filings_13f.sort(key=lambda x: x["period_of_report"], reverse=True)

    # 同一报告期如有 /A 修正，只取修正版
    seen_periods = {}
    unique_filings = []
    for f in filings_13f:
        period = f["period_of_report"]
        if period not in seen_periods:
            seen_periods[period] = True
            unique_filings.append(f)

    if max_count:
        unique_filings = unique_filings[:max_count]

    return unique_filings


def find_infotable_url(cik, accession):
    """
    在 filing 的文件列表中找到 XML/HTML infotable 文件的 URL
    策略：
    1. 首先使用 SEC 的 JSON index API ({accession}-index.json) 精确查找 INFORMATION TABLE 类型
    2. 如果失败，回退到 HTML 目录页面正则匹配
    支持: .xml / .htm / .html 格式
    """
    cik_clean = cik.lstrip("0")
    acc_clean = accession.replace("-", "")
    base_url = f"{SEC_ARCHIVES_URL}/{cik_clean}/{acc_clean}"

    # === 策略 1: 使用 SEC JSON index API ===
    json_index_url2 = f"{base_url}/{accession}-index.json"
    for json_url in [json_index_url2]:
        try:
            index_data = _get_json(json_url)
            items = index_data.get("directory", {}).get("item", [])
            # 优先找 INFORMATION TABLE 类型 (.xml 或 .htm/.html)
            for item in items:
                item_type = item.get("type", "").upper()
                item_name = item.get("name", "")
                name_lower = item_name.lower()
                is_data_file = name_lower.endswith((".xml", ".htm", ".html"))
                if "INFORMATION TABLE" in item_type and is_data_file:
                    return f"{base_url}/{item_name}"
            # 回退：找含关键词的 xml/htm 文件
            for item in items:
                item_name = item.get("name", "")
                name_lower = item_name.lower()
                is_data_file = name_lower.endswith((".xml", ".htm", ".html"))
                if is_data_file and item.get("type", "") != "COMPLETE SUBMISSION TEXT FILE":
                    if any(kw in name_lower for kw in ["table", "13f", "info", "holding"]):
                        return f"{base_url}/{item_name}"
        except Exception:
            pass

    # === 策略 2: 回退 - 解析 HTML 目录页面 ===
    filing_index_url = f"{base_url}/"
    try:
        html = _get_text(filing_index_url)
        # 先找 INFORMATION TABLE 类型的行（支持 .xml 和 .htm）
        info_table_block = re.search(
            r'INFORMATION TABLE.*?href="([^"]+\.(?:xml|htm|html))"',
            html, re.IGNORECASE | re.DOTALL
        )
        if info_table_block:
            xml_file = info_table_block.group(1)
            if xml_file.startswith("/"):
                return f"https://www.sec.gov{xml_file}"
            if xml_file.startswith("http"):
                return xml_file
            return f"{filing_index_url}{xml_file}"

        # 再按文件名关键字匹配（支持 .xml 和 .htm）
        xml_patterns = [
            r'href="([^"]*infotable[^"]*\.(?:xml|htm|html))"',
            r'href="([^"]*information[^"]*table[^"]*\.(?:xml|htm|html))"',
            r'href="([^"]*13[fF][^"]*\.(?:xml|htm|html))"',
            r'href="([^"]*holding[^"]*\.(?:xml|htm|html))"',
        ]
        for pattern in xml_patterns:
            matches = re.findall(pattern, html, re.IGNORECASE)
            if matches:
                xml_file = matches[0]
                if xml_file.startswith("/"):
                    return f"https://www.sec.gov{xml_file}"
                if xml_file.startswith("http"):
                    return xml_file
                return f"{filing_index_url}{xml_file}"

        # 最后尝试：找所有 .xml/.htm 文件，排除 primary/submission/index 文档
        all_data = re.findall(r'href="([^"]+\.(?:xml|htm|html))"', html, re.IGNORECASE)
        for data_file in all_data:
            name_lower = data_file.lower()
            # 排除所有 SEC 通用页面和非数据文件
            skip_keywords = [
                "primary", "submission",
                "index.htm", "index.html", "/index",
                "search.htm", "search/search", "/search",
                "cgi-bin", "browse-edgar",
            ]
            if any(kw in name_lower for kw in skip_keywords):
                continue
            # 只接受明确来自 EDGAR archives 的数据文件
            if data_file.startswith("/Archives/edgar/data/"):
                return f"https://www.sec.gov{data_file}"
            if data_file.startswith("http") and "Archives/edgar/data/" in data_file:
                return data_file
            # 相对路径（同目录下的文件，最安全）
            if not data_file.startswith("/") and not data_file.startswith("http"):
                return f"{filing_index_url}{data_file}"

    except Exception as e:
        logger.warning(f"无法获取 filing index HTML: {e}")

    return None


def parse_infotable_xml(xml_text):
    """
    解析 13F infotable XML 文件
    返回: list of dict，每个包含一条持仓信息
    """
    holdings = []

    # 移除 XML 声明中可能的编码问题
    xml_text = re.sub(r'<\?xml[^?]*\?>', '', xml_text).strip()

    # 尝试不同的命名空间
    ns_patterns = [
        {"ns": "http://www.sec.gov/document/thirteenf-2024-10-10.xsd"},
        {"ns": "http://www.sec.gov/document/thirteenf-2024-04-18.xsd"},
        {"ns": "http://www.sec.gov/document/thirteenf-2023-12-01.xsd"},
        {"ns": "http://www.sec.gov/document/thirteenf-2023-04-17.xsd"},
        {"ns": "http://www.sec.gov/document/thirteenf-2016-02-23.xsd"},
        {"ns": "http://www.sec.gov/document/thirteenf"},
    ]

    root = None
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError as e:
        logger.error(f"XML 解析失败: {e}")
        return holdings

    # 获取实际使用的命名空间
    ns_match = re.search(r'\{([^}]+)\}', root.tag)
    ns = ns_match.group(1) if ns_match else ""

    if ns:
        ns_prefix = f"{{{ns}}}"
    else:
        ns_prefix = ""

    # 查找所有 infoTable 条目
    entries = root.findall(f".//{ns_prefix}infoTable")
    if not entries:
        # 尝试其他可能的标签名
        entries = root.findall(f".//{ns_prefix}informationTable")
    if not entries:
        # 没有命名空间前缀的情况
        entries = root.findall(".//infoTable")
    if not entries:
        entries = root.findall(".//informationTable")
    if not entries:
        # 直接获取所有子元素
        entries = list(root)

    for entry in entries:
        def _find_text(tag):
            """在条目中查找特定标签的文本"""
            elem = entry.find(f"{ns_prefix}{tag}")
            if elem is None:
                elem = entry.find(tag)
            if elem is None:
                # 尝试不区分大小写搜索
                for child in entry.iter():
                    local_tag = child.tag.split("}")[-1] if "}" in child.tag else child.tag
                    if local_tag.lower() == tag.lower():
                        return (child.text or "").strip()
                return ""
            return (elem.text or "").strip()

        def _find_nested_text(parent_tag, child_tag):
            """在嵌套标签中查找文本"""
            parent = entry.find(f"{ns_prefix}{parent_tag}")
            if parent is None:
                parent = entry.find(parent_tag)
            if parent is not None:
                child = parent.find(f"{ns_prefix}{child_tag}")
                if child is None:
                    child = parent.find(child_tag)
                if child is not None:
                    return (child.text or "").strip()
            return ""

        issuer = _find_text("nameOfIssuer")
        if not issuer:
            continue  # 跳过无效条目

        value_str = _find_text("value")
        shares_str = _find_nested_text("shrsOrPrnAmt", "sshPrnamt")
        share_type = _find_nested_text("shrsOrPrnAmt", "sshPrnamtType")

        try:
            value = float(value_str) if value_str else 0
        except ValueError:
            value = 0

        try:
            shares = int(shares_str) if shares_str else 0
        except ValueError:
            shares = 0

        put_call = _find_text("putCall") or None
        title_of_class = _find_text("titleOfClass")

        holding = {
            "issuer": issuer,
            "cusip": _find_text("cusip"),
            "title_of_class": title_of_class,
            "value": value,
            "shares": shares,
            "share_type": share_type or "SH",
            "put_call": put_call,
            "discretion": _find_text("investmentDiscretion"),
            "ticker": "",
            "asset_class": "",  # 先置空，ticker 匹配后再填
        }
        holdings.append(holding)

    # ---- 按 CUSIP + put_call 合并同一证券的多行（如伯克希尔按账户拆分上报）----
    merged = {}
    for h in holdings:
        key = (h["cusip"] or h["issuer"], h.get("put_call") or "")
        if key in merged:
            merged[key]["value"] += h["value"]
            merged[key]["shares"] += h["shares"]
        else:
            merged[key] = dict(h)
    holdings = list(merged.values())

    return holdings


def _try_match_ticker(holdings, maps, update_sector=True):
    """尝试通过公司确切原名或归一化名匹配 ticker"""
    exact_map = maps.get("exact", {})
    norm_map = maps.get("norm", {})

    for h in holdings:
        issuer_upper = h["issuer"].upper()
        norm_iss = normalize_name(issuer_upper)
        matched_ticker = ""

        # 1. 尝试完全精确匹配 (Exact map)
        if issuer_upper in exact_map:
            matched_ticker = exact_map[issuer_upper]
        # 2. 尝试归一化全匹配 (Norm map)
        elif norm_iss in norm_map:
            matched_ticker = norm_map[norm_iss]
        else:
            # 3. 模糊匹配 - 依次截断末尾单词 (Norm map)
            words = norm_iss.split()
            for length in range(len(words), 0, -1):
                partial = " ".join(words[:length])
                if partial and partial in norm_map:
                    matched_ticker = norm_map[partial]
                    break
        
        # 4. 特例硬编码 Fallbacks (针对 ADR 和特殊缩写)
        if not matched_ticker:
            if "ALIBABA GROUP" in issuer_upper: matched_ticker = "BABA"
            elif "TAIWAN SEMICONDUCTOR" in issuer_upper: matched_ticker = "TSM"
            elif "ASML HOLDING" in issuer_upper: matched_ticker = "ASML"
            elif "BK OF AMERICA" in issuer_upper: matched_ticker = "BAC"
            elif "VERISIGN" in issuer_upper: matched_ticker = "VRSN"
            elif "BERKSHIRE HATHAWAY" in issuer_upper: matched_ticker = "BRK-B"

        if matched_ticker:
            h["ticker"] = matched_ticker

    # 统一在 ticker 匹配后，通过 get_sector 赋行业分类
    if update_sector:
        from backend.sector_mapper import get_sector
        for h in holdings:
            h["asset_class"] = get_sector(
                h.get("ticker", ""),
                h["issuer"],
                h.get("title_of_class", ""),
                h.get("put_call")
            )


def compute_changes(current_holdings, prev_holdings):
    """
    计算持仓变化
    current_holdings: 当前季度全部持仓 list
    prev_holdings: 上一季度全部持仓 list
    """
    # 用 cusip 创建上期持仓字典
    prev_map = {}
    for h in prev_holdings:
        key = h.get("cusip", "") or h.get("issuer", "")
        if key:
            prev_map[key] = h

    total_value = sum(h.get("value", 0) for h in current_holdings)

    for h in current_holdings:
        # 计算组合占比
        if total_value > 0:
            h["portfolio_pct"] = round((h.get("value", 0) / total_value) * 100, 2)
        else:
            h["portfolio_pct"] = 0

        # 查找上期持仓
        key = h.get("cusip", "") or h.get("issuer", "")
        prev = prev_map.get(key)
        if prev:
            h["prev_pct"] = prev.get("portfolio_pct", 0)
            h["pct_change"] = round(h["portfolio_pct"] - h["prev_pct"], 2)
            prev_shares = prev.get("shares", 0)
            if prev_shares > 0:
                h["shares_change_pct"] = round(
                    ((h.get("shares", 0) - prev_shares) / prev_shares) * 100, 2
                )
            else:
                h["shares_change_pct"] = 100.0 if h.get("shares", 0) > 0 else 0
        else:
            # 新建仓位
            h["prev_pct"] = 0
            h["pct_change"] = h["portfolio_pct"]
            h["shares_change_pct"] = 100.0  # 标记为新建

    return current_holdings


def _fallback_dataroma(dataroma_id, fund_cik, name_cn, target_quarters=None):
    """当 SEC 数据缺失时，从 Dataroma 直接抓取持仓的补充逻辑"""
    from backend.dataroma_scraper import scrape_dataroma_fund
    from backend.database import get_filing, upsert_filing, insert_holdings
    from backend.sector_mapper import get_sector
    
    # 默认只抓一期（最新），如果提供了多个则挨个尝试
    if not target_quarters:
        target_quarters = [None]
        
    for idx, tq in enumerate(target_quarters):
        logger.info(f"  [Dataroma] 尝试提取 {name_cn} 的 {tq if tq else '最新'} 季度数据...")
        
        # 提取数据
        holdings, period = scrape_dataroma_fund(dataroma_id, target_quarter=tq)
        if not holdings or not period:
            logger.warning(f"  [Dataroma] 未抓取到 {name_cn} 在 {tq if tq else '最新'} 的数据")
            continue

        # 检查是否已存在
        existing = get_filing(fund_cik, period)
        if existing:
            logger.info(f"    {period} 数据已存在于数据库，跳过")
            continue

        # 通过 get_sector 添加资产类别
        for h in holdings:
            h["asset_class"] = get_sector(
                h.get("ticker", ""),
                h["issuer"],
                h.get("title_of_class", ""),
                h.get("put_call")
            )

        # 获取上期对比变化
        prev_quarter = _get_prev_quarter(period)
        prev_holdings = get_all_holdings(fund_cik, prev_quarter)
        if prev_holdings:
            holdings = compute_changes(holdings, prev_holdings)

        # 计算预估最新总市值
        total_value = sum(h.get("value", 0) for h in holdings)
        
        # 模拟 filing 日期 (估算截止日)
        period_year, period_q = period.split('-')
        q_month_end = {"Q1": "03-31", "Q2": "06-30", "Q3": "09-30", "Q4": "12-31"}
        period_date = f"{period_year}-{q_month_end[period_q]}"
        filing_date = f"{period_year}-{(int(q_month_end[period_q].split('-')[0])+2)%12 or 12:02d}-15"

        filing_id = upsert_filing(
            fund_cik, period, period_date=period_date,
            filing_date=filing_date, accession=f"DATAROMA-{period}",
            total_value=total_value
        )
        insert_holdings(filing_id, holdings)
        logger.info(f"    ✓ {period} 已通过备用通道完成保存 (总市值: ${total_value/1000:.2f}M)")

        if idx > 0:
            import time
            time.sleep(1.5) # 给 Dataroma 稍作喘息


def scrape_fund(cik, name, name_cn, max_quarters=None, latest_only=False, dataroma_id=None):
    """
    抓取单个基金的 13F 数据

    Args:
        cik: 基金 CIK 号 (如 Dataroma 专属基金则为 "D-xxx")
        name: 英文名
        name_cn: 中文名
        max_quarters: 最多抓取多少个季度
        latest_only: 是否只抓取最新一期
        dataroma_id: 备用提取标识
    """
    logger.info(f"========== 开始采集: {name_cn} ({name}) ==========")

    # 保存基金信息
    upsert_fund(cik, name, name_cn)

    # Dataroma fallback check
    is_dataroma_only = not cik or cik.startswith("D-")
    submissions = None
    
    if not is_dataroma_only:
        # 获取提交历史
        try:
            submissions = get_fund_submissions(cik)
        except Exception as e:
            logger.error(f"获取 {name} 的提交历史失败: {e}")
            if not dataroma_id:
                return

    filings = []
    if submissions:
        # 获取 13F filing 列表
        filings = get_13f_filings(
            submissions,
            max_count=1 if latest_only else max_quarters
        )

    if not filings:
        if dataroma_id:
            logger.info(f"  -> SEC 无可用数据，触发 Dataroma 降级抓取...")
            
            tqs = [None]
            if max_quarters is not None and max_quarters > 1 and not latest_only:
                # 简单硬编码补全最近几个季度以满足图表趋势 (由于 dataroma 限制，不能传太多免得风控，补3个季度即可)
                tqs = [None, "2025-Q3", "2025-Q2", "2025-Q1"]
                
            _fallback_dataroma(dataroma_id, cik, name_cn, target_quarters=tqs)
        else:
            logger.warning(f"{name} 未找到 13F-HR 提交记录且无备用通道")
        logger.info(f"========== {name_cn} 采集完成 ==========\n")
        return

    logger.info(f"  找到 {len(filings)} 个 13F 报告")

    # 加载 ticker 映射表
    ticker_map = _build_cusip_ticker_map()

    # 初始化行业缓存（确保表存在）
    _init_cache()

    # 逐个处理 filing（从旧到新，使每个季度能找到上一季度数据计算变化）
    filings_ordered = list(reversed(filings))
    for i, filing in enumerate(filings_ordered):
        period_date = filing["period_of_report"]
        period = _period_to_quarter(period_date)
        accession = filing["accession"]

        logger.info(f"  [{i+1}/{len(filings)}] 处理 {period} (报告日期: {period_date})")

        # 检查是否已存在
        existing = get_filing(cik, period)
        if existing and not latest_only:
            logger.info(f"    {period} 数据已存在，跳过")
            continue

        # 找到 infotable XML 文件
        xml_url = find_infotable_url(cik, accession)
        if not xml_url:
            logger.warning(f"    未找到 {period} 的 infotable XML 文件")
            continue

        logger.info(f"    XML URL: {xml_url}")

        # 下载并解析 XML
        try:
            xml_text = _get_text(xml_url)
            holdings = parse_infotable_xml(xml_text)
        except Exception as e:
            logger.error(f"    解析 XML 失败: {e}")
            continue

        if not holdings:
            logger.warning(f"    {period} 未解析到任何持仓数据")
            continue

        logger.info(f"    解析到 {len(holdings)} 条持仓记录")

        # 尝试匹配 ticker（并更新 asset_class）
        _try_match_ticker(holdings, ticker_map)

        # 批量预热行业缓存（有 ticker 的）
        tickers = [h["ticker"] for h in holdings if h.get("ticker")]
        if tickers:
            prefetch_sectors(tickers)

        # 计算总市值
        total_value = sum(h.get("value", 0) for h in holdings)

        # 获取上一季度数据用于计算变化
        prev_quarter = _get_prev_quarter(period)
        prev_holdings = get_all_holdings(cik, prev_quarter)
        if prev_holdings:
            holdings = compute_changes(holdings, prev_holdings)
        else:
            # 无上期数据，仅计算占比
            for h in holdings:
                if total_value > 0:
                    h["portfolio_pct"] = round((h.get("value", 0) / total_value) * 100, 2)

        # 写入数据库
        filing_id = upsert_filing(
            cik, period, period_date,
            filing["filing_date"], accession, total_value
        )
        insert_holdings(filing_id, holdings)

        logger.info(f"    ✓ {period} 已保存 (总市值: ${total_value/1000:.2f}M)")

    logger.info(f"========== {name_cn} 采集完成 ==========\n")


def _get_prev_quarter(period_str):
    """获取上一个季度的标识 例如 '2025-Q4' -> '2025-Q3'"""
    year, q = period_str.split("-Q")
    year = int(year)
    q = int(q)
    if q == 1:
        return f"{year-1}-Q4"
    else:
        return f"{year}-Q{q-1}"


def scrape_all(latest_only=False):
    """采集所有预置基金的 13F 数据"""
    init_db()
    logger.info(f"开始采集 {len(FUNDS)} 个基金的 13F 数据...")

    for fund in FUNDS:
        cik = fund.get("cik", "")
        dataroma_id = fund.get("dataroma_id", "")
        key = cik if cik else f"D-{dataroma_id}"
        try:
            scrape_fund(
                cik=key,
                name=fund["name"],
                name_cn=fund["name_cn"],
                max_quarters=INITIAL_QUARTERS if not latest_only else 1,
                latest_only=latest_only,
                dataroma_id=dataroma_id
            )
        except Exception as e:
            logger.error(f"采集 {fund['name_cn']} 失败: {e}")
            continue

    logger.info("所有基金采集完成！")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="13F 数据采集器")
    parser.add_argument("--fund", type=str, help="指定基金 CIK 或简称")
    parser.add_argument("--latest", action="store_true", help="只爬取最新一期")
    parser.add_argument("--quarters", type=int, default=INITIAL_QUARTERS,
                        help=f"爬取季度数 (默认 {INITIAL_QUARTERS})")
    args = parser.parse_args()

    init_db()

    if args.fund:
        # 查找匹配的基金
        target = None
        for f in FUNDS:
            if (args.fund.lower() in f["name"].lower() or
                args.fund.lower() in f["name_cn"] or
                args.fund == f["cik"]):
                target = f
                break
        if target:
            cik = target.get("cik", "")
            dataroma_id = target.get("dataroma_id", "")
            key = cik if cik else f"D-{dataroma_id}"
            scrape_fund(
                key, target["name"], target["name_cn"],
                max_quarters=args.quarters, latest_only=args.latest,
                dataroma_id=dataroma_id
            )
        else:
            logger.error(f"未找到匹配的基金: {args.fund}")
            logger.info("可用基金: " + ", ".join(f["name_cn"] for f in FUNDS))
    else:
        scrape_all(latest_only=args.latest)
