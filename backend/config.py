# -*- coding: utf-8 -*-
"""13F 系统配置文件"""

import os

# ============================================================
# SEC EDGAR 配置
# ============================================================
# SEC 要求 User-Agent 包含真实邮箱，用于速率限制追踪
SEC_USER_AGENT = "13F-Tracker research@example.com"
SEC_BASE_URL = "https://data.sec.gov"
SEC_ARCHIVES_URL = "https://www.sec.gov/Archives/edgar/data"
# SEC 限制: 10 req/s，每次请求间隔 0.15 秒留出余量
SEC_REQUEST_DELAY = 0.15

# ============================================================
# 预置基金 CIK 列表 (对齐 Dataroma: https://www.dataroma.com/m/managers.php)
# ============================================================
# 命名规范: name_cn = "中文名 (经理人)" 或 "中文名" (纯机构)
# 注意: 每个 CIK 只能出现一次
FUNDS = [
    # ──────────────────────────────────────────────────────────
    # 额外补充 (非 Dataroma，但用户指定)
    # ──────────────────────────────────────────────────────────
    {"cik": "0002012383", "name": "BlackRock Inc",                        "name_cn": "贝莱德 (BlackRock)"},

    # ──────────────────────────────────────────────────────────
    # Dataroma 标准名单 (按字母顺序, 共 76 家已验证 CIK)
    # ──────────────────────────────────────────────────────────
    {"cik": "0001166559", "name": "Bill & Melinda Gates Foundation Trust","name_cn": "盖茨基金会信托"},
    {"cik": "0001336528", "name": "Pershing Square Capital Management",   "name_cn": "潘兴广场 (Bill Ackman)"},
    {"cik": "0001135778", "name": "Miller Value Partners, LLC",           "name_cn": "米勒价值 (Bill Miller)"},
    {"cik": "0001657335", "name": "Oakcliff Capital Partners, LP",        "name_cn": "橡崖资本 (Bryan Lawrence)"},
    {"cik": "0000921669", "name": "Icahn Carl C",                         "name_cn": "伊坎资本 (Carl Icahn)"},
    {"cik": "0001167483", "name": "Tiger Global Management LLC",          "name_cn": "老虎全球 (Chase Coleman)"},
    {"cik": "0001647251", "name": "TCI Fund Management Ltd",              "name_cn": "TCI基金 (Chris Hohn)"},
    {"cik": "0001112520", "name": "Akre Capital Management LLC",          "name_cn": "阿克里资本 (Chuck Akre)"},
    {"cik": "0001040273", "name": "Third Point LLC",                      "name_cn": "第三点 (Dan Loeb)"},
    {"cik": "0001079114", "name": "Greenlight Capital Inc",               "name_cn": "绿光资本 (David Einhorn)"},
    {"cik": "0001656456", "name": "Appaloosa LP",                         "name_cn": "阿帕卢萨 (David Tepper)"},
    {"cik": "0001766908", "name": "ShawSpring Partners LLC",              "name_cn": "肖斯普林 (Dennis Hong)"},
    {"cik": "0000200217", "name": "Dodge & Cox",                          "name_cn": "道奇考克斯"},
    {"cik": "0001759760", "name": "H&H International Investment, LLC",    "name_cn": "步步高投资 (段永平)"},
    {"cik": "0001553733", "name": "Brave Warrior Advisors, LLC",          "name_cn": "勇武顾问 (Glenn Greenberg)"},
    {"cik": "0001559771", "name": "Engaged Capital LLC",                  "name_cn": "恩格资本 (Glenn Welling)"},
    {"cik": "0000846222", "name": "Greenhaven Associates Inc",            "name_cn": "绿港资本"},
    {"cik": "0001404599", "name": "Aquamarine Capital Management, LLC",   "name_cn": "碧水资本 (Guy Spier)"},
    {"cik": "0001798849", "name": "Durable Capital Partners LP",          "name_cn": "耐久资本 (Henry Ellenbogen)"},
    {"cik": "0001083657", "name": "Egerton Capital Ltd",                  "name_cn": "埃格顿资本 (John Armitage)"},
    {"cik": "0001766504", "name": "Greenlea Lane Capital Management",     "name_cn": "绿地巷资本 (Josh Tarasoff)"},
    {"cik": "0000898382", "name": "Leon Cooperman",                       "name_cn": "库珀曼 (Leon Cooperman)"},
    {"cik": "0001709323", "name": "Himalaya Capital Management",          "name_cn": "喜马拉雅资本 (李录)"},
    {"cik": "0001484150", "name": "Lindsell Train Ltd",                   "name_cn": "林德赛尔火车"},
    {"cik": "0001649339", "name": "Scion Asset Management, LLC",          "name_cn": "大空头资本 (Michael Burry)"},
    {"cik": "0001345471", "name": "Trian Fund Management",                "name_cn": "特里安基金 (Nelson Peltz)"},
    {"cik": "0001419050", "name": "Punch Card Capital LLC",               "name_cn": "打卡资本 (Norbert Lou)"},
    {"cik": "0001034524", "name": "Polen Capital Management Inc",         "name_cn": "波伦资本"},
    {"cik": "0000915191", "name": "Fairfax Financial Holdings Inc",       "name_cn": "枫信金融 (Prem Watsa)"},
    {"cik": "0001766596", "name": "RV Capital GmbH",                      "name_cn": "RV资本 (Robert Vinall)"},
    {"cik": "0001854794", "name": "Patient Capital Management, LLC",      "name_cn": "耐心资本 (Samantha McLemore)"},
    {"cik": "0001061768", "name": "Baupost Group LLC",                    "name_cn": "鲍波斯特 (Seth Klarman)"},
    {"cik": "0001061165", "name": "Lone Pine Capital LLC",                "name_cn": "孤松资本 (Stephen Mandel)"},
    {"cik": "0000860643", "name": "Gardner Russo & Quinn LLC",            "name_cn": "加德纳-鲁索 (Thomas Russo)"},
    {"cik": "0001540866", "name": "Makaira Partners LLC",                 "name_cn": "马凯拉 (Tom Bancroft)"},
    {"cik": "0001454502", "name": "Triple Frond Partners LLC",            "name_cn": "三叶资本"},
    {"cik": "0001697868", "name": "Valley Forge Capital Management",      "name_cn": "福吉谷资本"},
    {"cik": "0001103804", "name": "Viking Global Investors LP",           "name_cn": "维京全球 (Andreas Halvorsen)"},
    {"cik": "0001067983", "name": "Berkshire Hathaway Inc",               "name_cn": "伯克希尔·哈撒韦 (Warren Buffett)"},
    {"cik": "0001279936", "name": "Cantillon Capital Management LLC",     "name_cn": "坎蒂隆资本 (William Von Mueffling)"},
    {"cik": "0000905567", "name": "Yacktman Asset Management LP",         "name_cn": "亚克曼资产"},

    # ──────────────────────────────────────────────────────────
    # Dataroma 中的共同基金 — 以实际 13F 申报主体 CIK 代替
    # 这些基金在 Dataroma 上以基金经理名义展示，但 SEC 13F 是由下属机构提交
    # ──────────────────────────────────────────────────────────
    {"cik": "0000039263", "name": "First Pacific Advisors LLC",           "name_cn": "FPA资管 (Steven Romick/FPA Crescent)"},
    # 注: Terry Smith (Fundsmith) 为英国公司，不提交美国 SEC 13F，暂无法采集
    # 注: Hillman Value Fund / FPA Queens Road / Meridian Contrarian 无独立 SEC CIK
]

# ============================================================
# 数据库配置
# ============================================================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
DB_PATH = os.path.join(DATA_DIR, "holdings.db")

# ============================================================
# 爬取参数
# ============================================================
# 首次爬取的历史季度数量
INITIAL_QUARTERS = 8
# 资产类别映射 (简化分类)
ASSET_CLASS_MAP = {
    "COM": "股票",
    "SH": "股票",
    "CALL": "期权-看涨",
    "PUT": "期权-看跌",
    "PRN": "债券",
    "NOTE": "债券",
    "CONV": "可转债",
    "WT": "权证",
}

# ============================================================
# 行业映射 (GICS 一级行业)
# ============================================================
SECTOR_MAP = {
    "Technology": "科技",
    "Health Care": "医疗",
    "Financials": "金融",
    "Consumer Discretionary": "消费-可选",
    "Consumer Staples": "消费-必需",
    "Industrials": "工业",
    "Communication Services": "通信",
    "Energy": "能源",
    "Materials": "材料",
    "Real Estate": "房地产",
    "Utilities": "公用事业",
}
