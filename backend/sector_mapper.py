# -*- coding: utf-8 -*-
"""
行业/板块映射表
将常见 ticker -> GICS 行业子类别
数据来源: 公开 GICS 行业分类 + 常见 ETF 类型
"""

# Ticker -> 行业子类别（中文）
TICKER_SECTOR = {
    # ===== 科技 =====
    "AAPL": "股票-科技", "MSFT": "股票-科技", "NVDA": "股票-科技",
    "META": "股票-科技", "GOOGL": "股票-科技", "GOOG": "股票-科技",
    "AMZN": "股票-科技", "TSM": "股票-科技", "AVGO": "股票-科技",
    "ORCL": "股票-科技", "ADBE": "股票-科技", "CRM": "股票-科技",
    "AMD": "股票-科技", "INTC": "股票-科技", "QCOM": "股票-科技",
    "TXN": "股票-科技", "MU": "股票-科技", "AMAT": "股票-科技",
    "LRCX": "股票-科技", "KLAC": "股票-科技", "MRVL": "股票-科技",
    "NOW": "股票-科技", "WDAY": "股票-科技", "SNOW": "股票-科技",
    "PLTR": "股票-科技", "CRWD": "股票-科技", "PANW": "股票-科技",
    "FTNT": "股票-科技", "NET": "股票-科技", "ZS": "股票-科技",
    "DELL": "股票-科技", "HPQ": "股票-科技", "IBM": "股票-科技",
    "CSCO": "股票-科技", "ANET": "股票-科技",
    # ===== 通讯服务 =====
    "NFLX": "股票-通讯服务", "DIS": "股票-通讯服务",
    "TMUS": "股票-通讯服务", "VZ": "股票-通讯服务", "T": "股票-通讯服务",
    "CMCSA": "股票-通讯服务", "CHTR": "股票-通讯服务",
    "WBD": "股票-通讯服务", "PARA": "股票-通讯服务",
    "SPOT": "股票-通讯服务", "SNAP": "股票-通讯服务",
    "PINS": "股票-通讯服务", "RBLX": "股票-通讯服务",
    # ===== 金融 =====
    "BRK-A": "股票-金融", "BRK-B": "股票-金融", "BRK": "股票-金融",
    "JPM": "股票-金融", "BAC": "股票-金融", "WFC": "股票-金融",
    "GS": "股票-金融", "MS": "股票-金融", "C": "股票-金融",
    "AXP": "股票-金融", "V": "股票-金融", "MA": "股票-金融",
    "PYPL": "股票-金融", "SQ": "股票-金融", "FI": "股票-金融",
    "FISV": "股票-金融", "COF": "股票-金融", "AIG": "股票-金融",
    "MET": "股票-金融", "PRU": "股票-金融", "ALL": "股票-金融",
    "PGR": "股票-金融", "BLK": "股票-金融", "SCHW": "股票-金融",
    "ICE": "股票-金融", "CME": "股票-金融", "SPGI": "股票-金融",
    "MCO": "股票-金融", "USB": "股票-金融", "TFC": "股票-金融",
    "PNC": "股票-金融", "NFLX": "股票-通讯服务",
    "JEF": "股票-金融", "HIG": "股票-金融",
    # ===== 医疗保健 =====
    "JNJ": "股票-医疗保健", "UNH": "股票-医疗保健", "LLY": "股票-医疗保健",
    "ABT": "股票-医疗保健", "ABBV": "股票-医疗保健", "MRK": "股票-医疗保健",
    "PFE": "股票-医疗保健", "BMY": "股票-医疗保健", "GILD": "股票-医疗保健",
    "AMGN": "股票-医疗保健", "BIIB": "股票-医疗保健", "REGN": "股票-医疗保健",
    "VRTX": "股票-医疗保健", "MRNA": "股票-医疗保健", "BNTX": "股票-医疗保健",
    "CVS": "股票-医疗保健", "CI": "股票-医疗保健", "HUM": "股票-医疗保健",
    "ELV": "股票-医疗保健", "CNC": "股票-医疗保健", "MOH": "股票-医疗保健",
    "ISRG": "股票-医疗保健", "BSX": "股票-医疗保健", "MDT": "股票-医疗保健",
    "SYK": "股票-医疗保健", "EW": "股票-医疗保健", "BAX": "股票-医疗保健",
    "TMO": "股票-医疗保健", "DHR": "股票-医疗保健", "A": "股票-医疗保健",
    "DXCM": "股票-医疗保健", "IDXX": "股票-医疗保健",
    # ===== 非必需消费 =====
    "TSLA": "股票-非必需消费", "HD": "股票-非必需消费", "MCD": "股票-非必需消费",
    "SBUX": "股票-非必需消费", "NKE": "股票-非必需消费", "LOW": "股票-非必需消费",
    "TJX": "股票-非必需消费", "BKNG": "股票-非必需消费", "ABNB": "股票-非必需消费",
    "MAR": "股票-非必需消费", "HLT": "股票-非必需消费", "GM": "股票-非必需消费",
    "F": "股票-非必需消费", "RIVN": "股票-非必需消费", "LCID": "股票-非必需消费",
    "RH": "股票-非必需消费", "ROST": "股票-非必需消费", "ULTA": "股票-非必需消费",
    "DECK": "股票-非必需消费", "TPR": "股票-非必需消费", "LVMH": "股票-非必需消费",
    "RL": "股票-非必需消费", "PVH": "股票-非必需消费",
    # ===== 必需消费 =====
    "WMT": "股票-必需消费", "PG": "股票-必需消费", "KO": "股票-必需消费",
    "PEP": "股票-必需消费", "COST": "股票-必需消费", "MDLZ": "股票-必需消费",
    "KHC": "股票-必需消费", "GIS": "股票-必需消费", "K": "股票-必需消费",
    "MO": "股票-必需消费", "PM": "股票-必需消费", "BTI": "股票-必需消费",
    "CL": "股票-必需消费", "KMB": "股票-必需消费", "CHD": "股票-必需消费",
    "EL": "股票-必需消费", "SJM": "股票-必需消费", "HSY": "股票-必需消费",
    "STZ": "股票-必需消费", "BF-A": "股票-必需消费", "BF-B": "股票-必需消费",
    # ===== 工业 =====
    "CAT": "股票-工业", "DE": "股票-工业", "RTX": "股票-工业",
    "BA": "股票-工业", "LMT": "股票-工业", "NOC": "股票-工业",
    "GD": "股票-工业", "L3H": "股票-工业", "HON": "股票-工业",
    "GE": "股票-工业", "MMM": "股票-工业", "EMR": "股票-工业",
    "ETN": "股票-工业", "PH": "股票-工业", "ITW": "股票-工业",
    "UPS": "股票-工业", "FDX": "股票-工业", "DAL": "股票-工业",
    "UAL": "股票-工业", "AAL": "股票-工业", "LUV": "股票-工业",
    "CSX": "股票-工业", "NSC": "股票-工业", "UNP": "股票-工业",
    "ODFL": "股票-工业", "CHRW": "股票-工业", "EXPD": "股票-工业",
    # ===== 能源 =====
    "XOM": "股票-能源", "CVX": "股票-能源", "COP": "股票-能源",
    "EOG": "股票-能源", "SLB": "股票-能源", "OXY": "股票-能源",
    "PSX": "股票-能源", "VLO": "股票-能源", "MPC": "股票-能源",
    "DVN": "股票-能源", "FANG": "股票-能源", "HAL": "股票-能源",
    "BKR": "股票-能源", "HES": "股票-能源", "APA": "股票-能源",
    # ===== 原材料 =====
    "LIN": "股票-原材料", "APD": "股票-原材料", "SHW": "股票-原材料",
    "FCX": "股票-原材料", "NEM": "股票-原材料", "NUE": "股票-原材料",
    "ALB": "股票-原材料", "CE": "股票-原材料", "DOW": "股票-原材料",
    "LYB": "股票-原材料", "CF": "股票-原材料", "MOS": "股票-原材料",
    "WPM": "股票-原材料", "GOLD": "股票-原材料", "AEM": "股票-原材料",
    "RGLD": "股票-原材料",
    # ===== 公用事业 =====
    "NEE": "股票-公用事业", "SO": "股票-公用事业", "DUK": "股票-公用事业",
    "AEP": "股票-公用事业", "D": "股票-公用事业", "EXC": "股票-公用事业",
    "XEL": "股票-公用事业", "PEG": "股票-公用事业", "ED": "股票-公用事业",
    "WEC": "股票-公用事业", "AWK": "股票-公用事业",
    # ===== 房地产 =====
    "PLD": "股票-房地产", "AMT": "股票-房地产", "CCI": "股票-房地产",
    "EQIX": "股票-房地产", "SPG": "股票-房地产", "O": "股票-房地产",
    "WY": "股票-房地产", "VICI": "股票-房地产", "DLR": "股票-房地产",
    "AVB": "股票-房地产", "EQR": "股票-房地产", "PSA": "股票-房地产",
    "ARE": "股票-房地产", "WELL": "股票-房地产",
    # ===== 中概股 =====
    "PDD": "股票-科技", "BABA": "股票-科技", "JD": "股票-科技",
    "BIDU": "股票-科技", "NIO": "股票-非必需消费", "LI": "股票-非必需消费",
    "XPEV": "股票-非必需消费", "TME": "股票-通讯服务", "BILI": "股票-通讯服务",
    "IQ": "股票-通讯服务", "VNET": "股票-科技", "GDS": "股票-科技",
    "CZHGY": "股票-通讯服务",
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
    (["COMMODITY", "MATERIAL", "COMMODITY"], "ETF-综合原材料"),
]

# 公司名关键词 -> 行业 (最后备选)
# 注意: 13F 报告中公司名常用缩写，需包含常见简称
COMPANY_NAME_KEYWORDS = [
    (["BANK", "BK OF", "FINANCIAL", "CAPITAL MARKETS", "INSURANCE", "FIDELITY",
      "AMERICAN EXPRESS", "VISA INC", "MASTERCARD", "PAYPAL", "SQUARE", "STRIPE",
      "BERKSHIRE", "JPMORGAN", "JP MORGAN", "GOLDMAN", "MORGAN STANLEY",
      "WELLS FARGO", "CITIGROUP", "CITI ", "PROGRESSIVE"],
     "股票-金融"),
    (["TECH", "SOFTWARE", "SEMICONDUCTOR", "CLOUD", "DATA", "CYBER", "NETWORK",
      "DIGITAL", "INTEL", "APPLE", "MICROSOFT", "GOOGLE", "ALPHABET", "META PLATFORM",
      "AMAZON", "ORACLE", "SAP", "SALESFORCE", "NVIDIA", "BROADCOM", "QUALCOMM",
      "ADVANCED MICRO", "APPLIED MAT", "LAM RESEARCH", "MARVELL",
      "PDD HOLDINGS", "ALIBABA", "JD.COM", "BAIDU", "SERVICENOW", "WORKDAY",
      "SNOWFLAKE", "PALANTIR", "CROWDSTRIKE", "PALO ALTO", "FORTINET"],
     "股票-科技"),
    (["PHARMA", "BIOTECH", "HEALTH", "MEDICAL", "HOSPITAL", "CLINIC", "THERAPEUT",
      "PFIZER", "JOHNSON & JOHNSON", "J&J", "MERCK", "ABBVIE", "AMGEN", "GILEAD",
      "LILLY", "ABBOTT", "BRISTOL", "REGENERON", "VERTEX", "MODERNA",
      "UNITEDHEALTH", "CVS ", "HUMANA", "ELEVANCE", "CENTENE", "INTUITIVE SURGICAL",
      "MEDTRONIC", "STRYKER", "BOSTON SCI", "THERMO FISHER", "DANAHER"],
     "股票-医疗保健"),
    (["OIL", "GAS", "ENERGY", "PETROLEUM", "CHEVRON", "EXXON", "SHELL",
      "BP ", "MARATHON", "HALLIBURTON", "SCHLUMBERGER",
      "CONOCOPHILLIPS", "PHILLIPS 66", "VALERO", "DEVON", "DIAMONDBACK",
      "OCCIDENTAL", "PIONEER NATURAL", "BAKER HUGHES"],
     "股票-能源"),
    (["RETAIL", "WALMART", "TARGET", "COSTCO", "HOME DEPOT", "LOWE",
      "STARBUCKS", "MCDONALD", "NIKE", "TESLA", "GENERAL MOTORS",
      "FORD MOTOR", "BOOKING", "AIRBNB", "MARRIOTT", "HILTON"],
     "股票-非必需消费"),
    (["COCA", "PEPSI", "PROCTER", "UNILEVER", "NESTLE", "ALTRIA", "PHILIP MORRIS",
      "COLGATE", "KIMBERLY", "HERSHEY", "MONDELEZ", "KRAFT HEINZ",
      "GENERAL MILLS", "CHURCH & DWIGHT"],
     "股票-必需消费"),
    (["AEROSPACE", "DEFENSE", "BOEING", "LOCKHEED", "RAYTHEON", "GENERAL DYNAMICS",
      "NORTHROP", "L3HARRIS", "HONEYWELL", "GENERAL ELECTRIC",
      "TRANSPORTATION", "LOGISTICS", "RAILROAD", "AIRLINE", "FREIGHT",
      "CATERPILLAR", "DEERE", "UNITED PARCEL", "FEDEX"],
     "股票-工业"),
    (["MINING", "GOLD", "SILVER", "COPPER", "STEEL", "ALUMINUM", "CHEMICAL",
      "NEWMONT", "BARRICK", "FREEPORT", "LINDE", "AIR PRODUCTS",
      "SHERWIN", "NUCOR", "DOW INC", "LYONDELLBASELL"],
     "股票-原材料"),
    (["TELECOM", "COMMUNICATION", "VERIZON", "AT&T", "COMCAST", "NETFLIX",
      "DISNEY", "WARNER", "T-MOBILE", "CHARTER COMM", "SPOTIFY"],
     "股票-通讯服务"),
    (["UTILITY", "ELECTRIC", "POWER", "WATER", "GAS UTILITY",
      "NEXTERA", "DUKE ENERGY", "SOUTHERN CO", "DOMINION", "EXELON"],
     "股票-公用事业"),
    (["REAL ESTATE", "REIT", "PROPERTY", "REALTY",
      "PROLOGIS", "AMERICAN TOWER", "CROWN CASTLE", "EQUINIX",
      "SIMON PROPERTY", "PUBLIC STORAGE"],
     "股票-房地产"),
]


def get_sector(ticker: str, issuer_name: str, title_of_class: str, put_call: str) -> str:
    """
    获取资产行业/类别
    优先级: put_call > ticker映射 > ETF名称关键词 > 公司名关键词 > 默认
    """
    # 期权类型
    if put_call:
        return f"期权-{'看涨' if put_call.upper() == 'CALL' else '看跌'}"

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
