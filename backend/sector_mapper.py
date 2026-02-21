# -*- coding: utf-8 -*-
"""
行业/板块映射表
将常见 ticker -> GICS 行业子类别
数据来源: 公开 GICS 行业分类 + 常见 ETF 类型

★ 标签统一规范（与 yfinance 输出一致）:
  - 普通股: "科技"、"金融"、"医疗"、"能源"、"消费-可选"、"消费-必需"、
            "工业"、"原材料"、"通讯"、"公用事业"、"房地产"
  - ETF: "ETF-xxx"
  - 期权: "期权-CALL" / "期权-PUT"
  - 特殊: "债券"、"可转债"、"权证"、"股票"（无法分类兜底）
"""

# Ticker -> 行业子类别（中文）
TICKER_SECTOR = {
    # ===== 科技 =====
    "AAPL": "科技", "MSFT": "科技", "NVDA": "科技",
    "META": "科技", "GOOGL": "科技", "GOOG": "科技",
    "AMZN": "科技", "TSM": "科技", "AVGO": "科技",
    "ORCL": "科技", "ADBE": "科技", "CRM": "科技",
    "AMD": "科技", "INTC": "科技", "QCOM": "科技",
    "TXN": "科技", "MU": "科技", "AMAT": "科技",
    "LRCX": "科技", "KLAC": "科技", "MRVL": "科技",
    "NOW": "科技", "WDAY": "科技", "SNOW": "科技",
    "PLTR": "科技", "CRWD": "科技", "PANW": "科技",
    "FTNT": "科技", "NET": "科技", "ZS": "科技",
    "DELL": "科技", "HPQ": "科技", "IBM": "科技",
    "CSCO": "科技", "ANET": "科技",
    # ===== 通讯 =====
    "NFLX": "通讯", "DIS": "通讯",
    "TMUS": "通讯", "VZ": "通讯", "T": "通讯",
    "CMCSA": "通讯", "CHTR": "通讯",
    "WBD": "通讯", "PARA": "通讯",
    "SPOT": "通讯", "SNAP": "通讯",
    "PINS": "通讯", "RBLX": "通讯",
    # ===== 金融 =====
    "BRK-A": "金融", "BRK-B": "金融", "BRK": "金融",
    "JPM": "金融", "BAC": "金融", "WFC": "金融",
    "GS": "金融", "MS": "金融", "C": "金融",
    "AXP": "金融", "V": "金融", "MA": "金融",
    "PYPL": "金融", "SQ": "金融", "FI": "金融",
    "FISV": "金融", "COF": "金融", "AIG": "金融",
    "MET": "金融", "PRU": "金融", "ALL": "金融",
    "PGR": "金融", "BLK": "金融", "SCHW": "金融",
    "ICE": "金融", "CME": "金融", "SPGI": "金融",
    "MCO": "金融", "USB": "金融", "TFC": "金融",
    "PNC": "金融", "JEF": "金融", "HIG": "金融",
    # ===== 医疗 =====
    "JNJ": "医疗", "UNH": "医疗", "LLY": "医疗",
    "ABT": "医疗", "ABBV": "医疗", "MRK": "医疗",
    "PFE": "医疗", "BMY": "医疗", "GILD": "医疗",
    "AMGN": "医疗", "BIIB": "医疗", "REGN": "医疗",
    "VRTX": "医疗", "MRNA": "医疗", "BNTX": "医疗",
    "CVS": "医疗", "CI": "医疗", "HUM": "医疗",
    "ELV": "医疗", "CNC": "医疗", "MOH": "医疗",
    "ISRG": "医疗", "BSX": "医疗", "MDT": "医疗",
    "SYK": "医疗", "EW": "医疗", "BAX": "医疗",
    "TMO": "医疗", "DHR": "医疗", "A": "医疗",
    "DXCM": "医疗", "IDXX": "医疗",
    # ===== 消费-可选 =====
    "TSLA": "消费-可选", "HD": "消费-可选", "MCD": "消费-可选",
    "SBUX": "消费-可选", "NKE": "消费-可选", "LOW": "消费-可选",
    "TJX": "消费-可选", "BKNG": "消费-可选", "ABNB": "消费-可选",
    "MAR": "消费-可选", "HLT": "消费-可选", "GM": "消费-可选",
    "F": "消费-可选", "RIVN": "消费-可选", "LCID": "消费-可选",
    "RH": "消费-可选", "ROST": "消费-可选", "ULTA": "消费-可选",
    "DECK": "消费-可选", "TPR": "消费-可选", "LVMH": "消费-可选",
    "RL": "消费-可选", "PVH": "消费-可选",
    # ===== 消费-必需 =====
    "WMT": "消费-必需", "PG": "消费-必需", "KO": "消费-必需",
    "PEP": "消费-必需", "COST": "消费-必需", "MDLZ": "消费-必需",
    "KHC": "消费-必需", "GIS": "消费-必需", "K": "消费-必需",
    "MO": "消费-必需", "PM": "消费-必需", "BTI": "消费-必需",
    "CL": "消费-必需", "KMB": "消费-必需", "CHD": "消费-必需",
    "EL": "消费-必需", "SJM": "消费-必需", "HSY": "消费-必需",
    "STZ": "消费-必需", "BF-A": "消费-必需", "BF-B": "消费-必需",
    # ===== 工业 =====
    "CAT": "工业", "DE": "工业", "RTX": "工业",
    "BA": "工业", "LMT": "工业", "NOC": "工业",
    "GD": "工业", "L3H": "工业", "HON": "工业",
    "GE": "工业", "MMM": "工业", "EMR": "工业",
    "ETN": "工业", "PH": "工业", "ITW": "工业",
    "UPS": "工业", "FDX": "工业", "DAL": "工业",
    "UAL": "工业", "AAL": "工业", "LUV": "工业",
    "CSX": "工业", "NSC": "工业", "UNP": "工业",
    "ODFL": "工业", "CHRW": "工业", "EXPD": "工业",
    # ===== 能源 =====
    "XOM": "能源", "CVX": "能源", "COP": "能源",
    "EOG": "能源", "SLB": "能源", "OXY": "能源",
    "PSX": "能源", "VLO": "能源", "MPC": "能源",
    "DVN": "能源", "FANG": "能源", "HAL": "能源",
    "BKR": "能源", "HES": "能源", "APA": "能源",
    # ===== 原材料 =====
    "LIN": "原材料", "APD": "原材料", "SHW": "原材料",
    "FCX": "原材料", "NEM": "原材料", "NUE": "原材料",
    "ALB": "原材料", "CE": "原材料", "DOW": "原材料",
    "LYB": "原材料", "CF": "原材料", "MOS": "原材料",
    "WPM": "原材料", "GOLD": "原材料", "AEM": "原材料",
    "RGLD": "原材料",
    # ===== 公用事业 =====
    "NEE": "公用事业", "SO": "公用事业", "DUK": "公用事业",
    "AEP": "公用事业", "D": "公用事业", "EXC": "公用事业",
    "XEL": "公用事业", "PEG": "公用事业", "ED": "公用事业",
    "WEC": "公用事业", "AWK": "公用事业",
    # ===== 房地产 =====
    "PLD": "房地产", "AMT": "房地产", "CCI": "房地产",
    "EQIX": "房地产", "SPG": "房地产", "O": "房地产",
    "WY": "房地产", "VICI": "房地产", "DLR": "房地产",
    "AVB": "房地产", "EQR": "房地产", "PSA": "房地产",
    "ARE": "房地产", "WELL": "房地产",
    # ===== 中概股 =====
    "PDD": "科技", "BABA": "科技", "JD": "科技",
    "BIDU": "科技", "NIO": "消费-可选", "LI": "消费-可选",
    "XPEV": "消费-可选", "TME": "通讯", "BILI": "通讯",
    "IQ": "通讯", "VNET": "科技", "GDS": "科技",
    "CZHGY": "通讯",
    # ===== 主要 ETF =====
    # 宽基市场
    "SPY": "ETF-大型股平衡型", "IVV": "ETF-大型股平衡型", "VOO": "ETF-大型股平衡型",
    "QQQ": "ETF-科技成熟市场", "TQQQ": "ETF-科技成熟市场", "SQQQ": "ETF-科技成熟市场",
    "IWM": "ETF-小型股市场", "VTI": "ETF-综合股市", "ITOT": "ETF-综合股市",
    "VEA": "ETF-成熟市场", "VWO": "ETF-新兴市场", "EEM": "ETF-新兴市场",
    "EFA": "ETF-成熟市场", "IEFA": "ETF-成熟市场",
    "DIA": "ETF-大型股平衡型", "MDY": "ETF-综合股市",
    # 杠杆/反向
    "UPRO": "ETF-大型股平衡型", "SPXU": "ETF-大型股平衡型",
    "SSO": "ETF-大型股平衡型", "SDS": "ETF-大型股平衡型",
    # 固收
    "TLT": "ETF-高收益债", "IEF": "ETF-投资等级公债", "SHY": "ETF-政府公债",
    "AGG": "ETF-投资等级公债", "BND": "ETF-投资等级公债",
    "HYG": "ETF-高收益债", "LQD": "ETF-投资等级公债",
    "GOVT": "ETF-政府公债", "VGIT": "ETF-政府公债",
    # 商品
    "GLD": "ETF-贵金属", "IAU": "ETF-贵金属", "SLV": "ETF-贵金属",
    "GDX": "ETF-贵金属", "GDXJ": "ETF-贵金属",
    "USO": "ETF-能源", "UCO": "ETF-能源",
    "DBC": "ETF-综合原材料",
    # 板块 ETF
    "XLK": "ETF-科技成熟市场", "XLF": "ETF-金融", "XLV": "ETF-医疗保健",
    "XLE": "ETF-能源", "XLI": "ETF-工业", "XLP": "ETF-必需消费",
    "XLY": "ETF-非必需消费", "XLU": "ETF-公用事业", "XLB": "ETF-原材料",
    "XLRE": "ETF-房地产", "XLC": "ETF-通讯服务",
    "VGT": "ETF-科技成熟市场", "SOXX": "ETF-科技成熟市场",
    "VHT": "ETF-医疗保健", "VFH": "ETF-金融",
    # 太平洋市场
    "FXI": "ETF-亚太新兴市场", "MCHI": "ETF-亚太新兴市场",
    "EWJ": "ETF-亚太成熟市场", "EWT": "ETF-亚太成熟市场",
    "EWY": "ETF-亚太新兴市场", "INDA": "ETF-亚太新兴市场",
}

# ETF 名称关键词 -> 类别 (用于未覆盖的 ETF)
ETF_NAME_KEYWORDS = [
    (["S&P 500", "SP500", "SPX"], "ETF-大型股平衡型"),
    (["NASDAQ", "QQQ", "NDX"], "ETF-科技成熟市场"),
    (["TECHNOLOGY", "TECH", "SEMICONDUCTOR", "SEMI"], "ETF-科技成熟市场"),
    (["EMERGING", "CHINA", "ASIA PACIFIC", "APAC"], "ETF-亚太新兴市场"),
    (["DEVELOPED MARKET", "EUROPE", "EAFE"], "ETF-成熟市场"),
    (["TREASURY", "T-BOND", "GOVERNMENT", "GILT"], "ETF-政府公债"),
    (["HIGH YIELD", "JUNK", "CORPORATE BOND"], "ETF-高收益债"),
    (["INVESTMENT GRADE", "CORP BOND"], "ETF-投资等级公债"),
    (["GOLD", "SILVER", "PRECIOUS METAL"], "ETF-贵金属"),
    (["ENERGY", "OIL", "GAS"], "ETF-能源"),
    (["HEALTHCARE", "HEALTH CARE", "BIOTECH"], "ETF-医疗保健"),
    (["FINANCIAL", "BANK", "INSURANCE"], "ETF-金融"),
    (["REAL ESTATE", "REIT"], "ETF-房地产"),
    (["SMALL CAP", "RUSSELL 2000", "MIDCAP"], "ETF-小型股市场"),
    (["TOTAL MARKET", "TOTAL STOCK"], "ETF-综合股市"),
    (["BALANCED", "ALLOCATION", "BLEND"], "ETF-大型股平衡型"),
    (["DIVIDEND", "INCOME", "YIELD"], "ETF-股票"),
    (["COMMODITY", "MATERIAL"], "ETF-综合原材料"),
]

# 公司名关键词 -> 行业 (最后备选)
COMPANY_NAME_KEYWORDS = [
    (["BANK", "BK OF", "FINANCIAL", "CAPITAL MARKETS", "INSURANCE", "FIDELITY",
      "AMERICAN EXPRESS", "VISA INC", "MASTERCARD", "PAYPAL", "SQUARE", "STRIPE",
      "BERKSHIRE", "JPMORGAN", "JP MORGAN", "GOLDMAN", "MORGAN STANLEY",
      "WELLS FARGO", "CITIGROUP", "CITI ", "PROGRESSIVE"],
     "金融"),
    (["TECH", "SOFTWARE", "SEMICONDUCTOR", "CLOUD", "DATA", "CYBER", "NETWORK",
      "DIGITAL", "INTEL", "APPLE", "MICROSOFT", "GOOGLE", "ALPHABET", "META PLATFORM",
      "AMAZON", "ORACLE", "SAP", "SALESFORCE", "NVIDIA", "BROADCOM", "QUALCOMM",
      "ADVANCED MICRO", "APPLIED MAT", "LAM RESEARCH", "MARVELL",
      "PDD HOLDINGS", "ALIBABA", "JD.COM", "BAIDU", "SERVICENOW", "WORKDAY",
      "SNOWFLAKE", "PALANTIR", "CROWDSTRIKE", "PALO ALTO", "FORTINET"],
     "科技"),
    (["PHARMA", "BIOTECH", "HEALTH", "MEDICAL", "HOSPITAL", "CLINIC", "THERAPEUT",
      "PFIZER", "JOHNSON & JOHNSON", "J&J", "MERCK", "ABBVIE", "AMGEN", "GILEAD",
      "LILLY", "ABBOTT", "BRISTOL", "REGENERON", "VERTEX", "MODERNA",
      "UNITEDHEALTH", "CVS ", "HUMANA", "ELEVANCE", "CENTENE", "INTUITIVE SURGICAL",
      "MEDTRONIC", "STRYKER", "BOSTON SCI", "THERMO FISHER", "DANAHER"],
     "医疗"),
    (["OIL", "GAS", "ENERGY", "PETROLEUM", "CHEVRON", "EXXON", "SHELL",
      "BP ", "MARATHON", "HALLIBURTON", "SCHLUMBERGER",
      "CONOCOPHILLIPS", "PHILLIPS 66", "VALERO", "DEVON", "DIAMONDBACK",
      "OCCIDENTAL", "PIONEER NATURAL", "BAKER HUGHES"],
     "能源"),
    (["RETAIL", "WALMART", "TARGET", "COSTCO", "HOME DEPOT", "LOWE",
      "STARBUCKS", "MCDONALD", "NIKE", "TESLA", "GENERAL MOTORS",
      "FORD MOTOR", "BOOKING", "AIRBNB", "MARRIOTT", "HILTON"],
     "消费-可选"),
    (["COCA", "PEPSI", "PROCTER", "UNILEVER", "NESTLE", "ALTRIA", "PHILIP MORRIS",
      "COLGATE", "KIMBERLY", "HERSHEY", "MONDELEZ", "KRAFT HEINZ",
      "GENERAL MILLS", "CHURCH & DWIGHT"],
     "消费-必需"),
    (["AEROSPACE", "DEFENSE", "BOEING", "LOCKHEED", "RAYTHEON", "GENERAL DYNAMICS",
      "NORTHROP", "L3HARRIS", "HONEYWELL", "GENERAL ELECTRIC",
      "TRANSPORTATION", "LOGISTICS", "RAILROAD", "AIRLINE", "FREIGHT",
      "CATERPILLAR", "DEERE", "UNITED PARCEL", "FEDEX"],
     "工业"),
    (["MINING", "GOLD", "SILVER", "COPPER", "STEEL", "ALUMINUM", "CHEMICAL",
      "NEWMONT", "BARRICK", "FREEPORT", "LINDE", "AIR PRODUCTS",
      "SHERWIN", "NUCOR", "DOW INC", "LYONDELLBASELL"],
     "原材料"),
    (["TELECOM", "COMMUNICATION", "VERIZON", "AT&T", "COMCAST", "NETFLIX",
      "DISNEY", "WARNER", "T-MOBILE", "CHARTER COMM", "SPOTIFY"],
     "通讯"),
    (["UTILITY", "ELECTRIC", "POWER", "WATER", "GAS UTILITY",
      "NEXTERA", "DUKE ENERGY", "SOUTHERN CO", "DOMINION", "EXELON"],
     "公用事业"),
    (["REAL ESTATE", "REIT", "PROPERTY", "REALTY",
      "PROLOGIS", "AMERICAN TOWER", "CROWN CASTLE", "EQUINIX",
      "SIMON PROPERTY", "PUBLIC STORAGE"],
     "房地产"),
]


def get_sector(ticker: str, issuer_name: str, title_of_class: str, put_call: str) -> str:
    """
    获取资产行业/类别
    优先级: put_call > ticker映射 > ETF名称关键词 > 公司名关键词 > 默认
    """
    # 期权类型（统一用英文 CALL/PUT）
    if put_call:
        return f"期权-{'CALL' if put_call.upper() == 'CALL' else 'PUT'}"

    title_upper = (title_of_class or "").upper()
    issuer_upper = (issuer_name or "").upper()
    ticker_upper = (ticker or "").upper().strip()

    # 1. ticker 精确映射
    if ticker_upper and ticker_upper in TICKER_SECTOR:
        return TICKER_SECTOR[ticker_upper]

    # 2. 判断是否是 ETF (从 titleOfClass 或名称)
    is_etf = ("ETF" in issuer_upper or "FUND" in issuer_upper or
              "TRUST" in issuer_upper or "INDEX" in issuer_upper)

    if is_etf or "ETF" in title_upper:
        # ETF 名称关键词匹配
        for keywords, category in ETF_NAME_KEYWORDS:
            if any(kw in issuer_upper for kw in keywords):
                return category
        return "ETF-综合股市"

    # 3. 判断债券
    if any(kw in title_upper for kw in ["NOTE", "BOND", "PRN", "DEBENTURE", "FIXED"]):
        return "债券"
    if any(kw in title_upper for kw in ["CONV"]):
        return "可转债"
    if any(kw in title_upper for kw in ["WT", "WARRANT"]):
        return "权证"

    # 4. 公司名关键词匹配
    for keywords, category in COMPANY_NAME_KEYWORDS:
        if any(kw in issuer_upper for kw in keywords):
            return category

    # 5. 默认: 股票
    return "股票"
