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
    # --- Dataroma Missing Funds (Fallback Scraper) ---
    {"cik": "", "dataroma_id": "AKO", "name": "AKO Capital", "name_cn": "AKO Capital"},
    {"cik": "", "dataroma_id": "AIM", "name": "Alex Roepers - Atlantic Investment Management", "name_cn": "Alex Roepers - Atlantic Investment Management"},
    {"cik": "", "dataroma_id": "AP", "name": "AltaRock Partners", "name_cn": "AltaRock Partners"},
    {"cik": "", "dataroma_id": "LMM", "name": "Bill Miller - Miller Value Partners", "name_cn": "Bill Miller - Miller Value Partners"},
    {"cik": "", "dataroma_id": "oaklx", "name": "Bill Nygren - Oakmark Select Fund", "name_cn": "Bill Nygren - Oakmark Select Fund"},
    {"cik": "", "dataroma_id": "fairx", "name": "Bruce Berkowitz - Fairholme Capital", "name_cn": "Bruce Berkowitz - Fairholme Capital"},
    {"cik": "", "dataroma_id": "OCL", "name": "Bryan Lawrence - Oakcliff Capital", "name_cn": "Bryan Lawrence - Oakcliff Capital"},
    {"cik": "", "dataroma_id": "ic", "name": "Carl Icahn - Icahn Capital Management", "name_cn": "Carl Icahn - Icahn Capital Management"},
    {"cik": "", "dataroma_id": "ARFFX", "name": "Charles Bobrinskoy - Ariel Focus Fund", "name_cn": "Charles Bobrinskoy - Ariel Focus Fund"},
    {"cik": "", "dataroma_id": "TGM", "name": "Chase Coleman - Tiger Global Management", "name_cn": "Chase Coleman - Tiger Global Management"},
    {"cik": "", "dataroma_id": "tci", "name": "Chris Hohn - TCI Fund Management", "name_cn": "Chris Hohn - TCI Fund Management"},
    {"cik": "", "dataroma_id": "SA", "name": "Christopher Bloomstran - Semper Augustus", "name_cn": "Christopher Bloomstran - Semper Augustus"},
    {"cik": "", "dataroma_id": "DAV", "name": "Christopher Davis - Davis Advisors", "name_cn": "Christopher Davis - Davis Advisors"},
    {"cik": "", "dataroma_id": "AC", "name": "Chuck Akre - Akre Capital Management", "name_cn": "Chuck Akre - Akre Capital Management"},
    {"cik": "", "dataroma_id": "CAS", "name": "Clifford Sosin - CAS Investment Partners", "name_cn": "Clifford Sosin - CAS Investment Partners"},
    {"cik": "", "dataroma_id": "tp", "name": "Daniel Loeb - Third Point", "name_cn": "Daniel Loeb - Third Point"},
    {"cik": "", "dataroma_id": "abc", "name": "David Abrams - Abrams Capital Management", "name_cn": "David Abrams - Abrams Capital Management"},
    {"cik": "", "dataroma_id": "GLRE", "name": "David Einhorn - Greenlight Capital", "name_cn": "David Einhorn - Greenlight Capital"},
    {"cik": "", "dataroma_id": "MAVFX", "name": "David Katz - Matrix Asset Advisors", "name_cn": "David Katz - Matrix Asset Advisors"},
    {"cik": "", "dataroma_id": "WP", "name": "David Rolfe - Wedgewood Partners", "name_cn": "David Rolfe - Wedgewood Partners"},
    {"cik": "", "dataroma_id": "AM", "name": "David Tepper - Appaloosa Management", "name_cn": "David Tepper - Appaloosa Management"},
    {"cik": "", "dataroma_id": "SP", "name": "Dennis Hong - ShawSpring Partners", "name_cn": "Dennis Hong - ShawSpring Partners"},
    {"cik": "", "dataroma_id": "HH", "name": "Duan Yongping - H&H International Investment", "name_cn": "Duan Yongping - H&H International Investment"},
    {"cik": "", "dataroma_id": "FE", "name": "First Eagle Investment Management", "name_cn": "First Eagle Investment Management"},
    {"cik": "", "dataroma_id": "FPPTX", "name": "FPA Queens Road Small Cap Value Fund", "name_cn": "FPA Queens Road Small Cap Value Fund"},
    {"cik": "", "dataroma_id": "ca", "name": "Francis Chou - Chou Associates", "name_cn": "Francis Chou - Chou Associates"},
    {"cik": "", "dataroma_id": "GC", "name": "Francois Rochon - Giverny Capital", "name_cn": "Francois Rochon - Giverny Capital"},
    {"cik": "", "dataroma_id": "CCM", "name": "Glenn Greenberg - Brave Warrior Advisors", "name_cn": "Glenn Greenberg - Brave Warrior Advisors"},
    {"cik": "", "dataroma_id": "ENG", "name": "Glenn Welling - Engaged Capital", "name_cn": "Glenn Welling - Engaged Capital"},
    {"cik": "", "dataroma_id": "CM", "name": "Greg Alexander - Conifer Management", "name_cn": "Greg Alexander - Conifer Management"},
    {"cik": "", "dataroma_id": "aq", "name": "Guy Spier - Aquamarine Capital", "name_cn": "Guy Spier - Aquamarine Capital"},
    {"cik": "", "dataroma_id": "SSHFX", "name": "Harry Burn - Sound Shore", "name_cn": "Harry Burn - Sound Shore"},
    {"cik": "", "dataroma_id": "DCP", "name": "Henry Ellenbogen - Durable Capital Partners", "name_cn": "Henry Ellenbogen - Durable Capital Partners"},
    {"cik": "", "dataroma_id": "hcmax", "name": "Hillman Value Fund", "name_cn": "Hillman Value Fund"},
    {"cik": "", "dataroma_id": "oc", "name": "Howard Marks - Oaktree Capital Management", "name_cn": "Howard Marks - Oaktree Capital Management"},
    {"cik": "", "dataroma_id": "JIM", "name": "Jensen Investment Management", "name_cn": "Jensen Investment Management"},
    {"cik": "", "dataroma_id": "EC", "name": "John Armitage - Egerton Capital", "name_cn": "John Armitage - Egerton Capital"},
    {"cik": "", "dataroma_id": "CAAPX", "name": "John Rogers - Ariel Appreciation Fund", "name_cn": "John Rogers - Ariel Appreciation Fund"},
    {"cik": "", "dataroma_id": "GLC", "name": "Josh Tarasoff - Greenlea Lane Capital", "name_cn": "Josh Tarasoff - Greenlea Lane Capital"},
    {"cik": "", "dataroma_id": "KB", "name": "Kahn Brothers Group", "name_cn": "Kahn Brothers Group"},
    {"cik": "", "dataroma_id": "mc", "name": "Lee Ainslie - Maverick Capital", "name_cn": "Lee Ainslie - Maverick Capital"},
    {"cik": "", "dataroma_id": "MPGFX", "name": "Mairs & Power Growth Fund", "name_cn": "Mairs & Power Growth Fund"},
    {"cik": "", "dataroma_id": "LLPFX", "name": "Mason Hawkins - Longleaf Partners", "name_cn": "Mason Hawkins - Longleaf Partners"},
    {"cik": "", "dataroma_id": "MVALX", "name": "Meridian Contrarian Fund", "name_cn": "Meridian Contrarian Fund"},
    {"cik": "", "dataroma_id": "SAM", "name": "Michael Burry - Scion Asset Management", "name_cn": "Michael Burry - Scion Asset Management"},
    {"cik": "", "dataroma_id": "PI", "name": "Mohnish Pabrai - Pabrai Investments", "name_cn": "Mohnish Pabrai - Pabrai Investments"},
    {"cik": "", "dataroma_id": "PC", "name": "Norbert Lou - Punch Card Management", "name_cn": "Norbert Lou - Punch Card Management"},
    {"cik": "", "dataroma_id": "DA", "name": "Pat Dorsey - Dorsey Asset Management", "name_cn": "Pat Dorsey - Dorsey Asset Management"},
    {"cik": "", "dataroma_id": "FFH", "name": "Prem Watsa - Fairfax Financial Holdings", "name_cn": "Prem Watsa - Fairfax Financial Holdings"},
    {"cik": "", "dataroma_id": "pzfvx", "name": "Richard Pzena - Hancock Classic Value", "name_cn": "Richard Pzena - Hancock Classic Value"},
    {"cik": "", "dataroma_id": "OFALX", "name": "Robert Olstein - Olstein Capital Management", "name_cn": "Robert Olstein - Olstein Capital Management"},
    {"cik": "", "dataroma_id": "SEQUX", "name": "Ruane Cunniff - Sequoia Fund", "name_cn": "Ruane Cunniff - Sequoia Fund"},
    {"cik": "", "dataroma_id": "PTNT", "name": "Samantha McLemore - Patient Capital Management", "name_cn": "Samantha McLemore - Patient Capital Management"},
    {"cik": "", "dataroma_id": "CAU", "name": "Sarah Ketterer - Causeway Capital Management", "name_cn": "Sarah Ketterer - Causeway Capital Management"},
    {"cik": "", "dataroma_id": "BAUPOST", "name": "Seth Klarman - Baupost Group", "name_cn": "Seth Klarman - Baupost Group"},
    {"cik": "", "dataroma_id": "LPC", "name": "Stephen Mandel - Lone Pine Capital", "name_cn": "Stephen Mandel - Lone Pine Capital"},
    {"cik": "", "dataroma_id": "FPACX", "name": "Steven Romick - FPA Crescent Fund", "name_cn": "Steven Romick - FPA Crescent Fund"},
    {"cik": "", "dataroma_id": "FS", "name": "Terry Smith - Fundsmith", "name_cn": "Terry Smith - Fundsmith"},
    {"cik": "", "dataroma_id": "TA", "name": "Third Avenue Management", "name_cn": "Third Avenue Management"},
    {"cik": "", "dataroma_id": "MKL", "name": "Thomas Gayner - Markel Group", "name_cn": "Thomas Gayner - Markel Group"},
    {"cik": "", "dataroma_id": "GR", "name": "Thomas Russo - Gardner Russo & Quinn", "name_cn": "Thomas Russo - Gardner Russo & Quinn"},
    {"cik": "", "dataroma_id": "MP", "name": "Tom Bancroft - Makaira Partners", "name_cn": "Tom Bancroft - Makaira Partners"},
    {"cik": "", "dataroma_id": "T", "name": "Torray Funds", "name_cn": "Torray Funds"},
    {"cik": "", "dataroma_id": "TWEBX", "name": "Tweedy Browne Co. - Tweedy Browne Value Fund", "name_cn": "Tweedy Browne Co. - Tweedy Browne Value Fund"},
    {"cik": "", "dataroma_id": "VA", "name": "ValueAct Capital", "name_cn": "ValueAct Capital"},
    {"cik": "", "dataroma_id": "WIM", "name": "Wallace Weitz - Weitz Investment Management", "name_cn": "Wallace Weitz - Weitz Investment Management"},
    {"cik": "", "dataroma_id": "cc", "name": "William Von Mueffling - Cantillon Capital Management", "name_cn": "William Von Mueffling - Cantillon Capital Management"},

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
