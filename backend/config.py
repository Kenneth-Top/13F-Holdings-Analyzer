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
# 预置基金 CIK 列表
# ============================================================
FUNDS = [
    # === 综合投行与资管巨头 ===
    {"cik": "0001086364", "name": "BlackRock Inc.",                    "name_cn": "贝莱德"},
    {"cik": "0000102909", "name": "Vanguard Group Inc",               "name_cn": "先锋集团"},
    {"cik": "0000093751", "name": "State Street Corp",                  "name_cn": "道富集团"},
    {"cik": "0000019617", "name": "JPMorgan Chase & Co",                "name_cn": "摩根大通"},
    {"cik": "0000886982", "name": "Goldman Sachs Group Inc",            "name_cn": "高盛集团"},
    {"cik": "0000315066", "name": "FMR LLC",                            "name_cn": "富达投资"},
    {"cik": "0001000275", "name": "T Rowe Price Associates Inc",        "name_cn": "普信集团"},

    # === 价值投资与老牌长线基金 ===
    {"cik": "0001067983", "name": "Berkshire Hathaway Inc",             "name_cn": "伯克希尔·哈撒韦"},
    {"cik": "0001061768", "name": "Baupost Group LLC",                  "name_cn": "鲍波斯特 (Seth Klarman)"},
    {"cik": "0001173334", "name": "Pabrai Mohnish",                     "name_cn": "帕布莱投资 (Mohnish Pabrai)"},
    {"cik": "0001056831", "name": "Fairholme Capital Management",       "name_cn": "费尔霍姆 (Bruce Berkowitz)"},
    {"cik": "0000807985", "name": "GAMCO Investors, Inc.",              "name_cn": "GAMCO (Mario Gabelli)"},
    {"cik": "0001336528", "name": "Pershing Square Capital",            "name_cn": "潘兴广场 (Bill Ackman)"},

    # === 对冲基金与量化巨头 ===
    {"cik": "0001350694", "name": "Bridgewater Associates, LP",         "name_cn": "桥水基金 (Ray Dalio)"},
    {"cik": "0001037389", "name": "Renaissance Technologies LLC",       "name_cn": "文艺复兴 (Jim Simons)"},
    {"cik": "0001423053", "name": "Citadel Advisors LLC",               "name_cn": "城堡投资 (Ken Griffin)"},
    {"cik": "0001273087", "name": "Millennium Management LLC",          "name_cn": "千禧管理 (Englander)"},
    {"cik": "0001603466", "name": "Point72 Asset Management",           "name_cn": "Point72 (Steve Cohen)"},
    {"cik": "0001179392", "name": "Two Sigma Investments, LP",          "name_cn": "Two Sigma"},
    {"cik": "0001009207", "name": "D. E. Shaw & Co., Inc.",             "name_cn": "德劭基金 (David Shaw)"},
    {"cik": "0001167557", "name": "AQR Capital Management",             "name_cn": "AQR资本 (Cliff Asness)"},

    # === 激进投资与宏观基金 ===
    {"cik": "0000921669", "name": "Icahn Carl C",                       "name_cn": "伊坎资本 (Carl Icahn)"},
    {"cik": "0001048445", "name": "Elliott Investment Management",      "name_cn": "艾略特管理 (Paul Singer)"},
    {"cik": "0001345471", "name": "Trian Fund Management",              "name_cn": "特里安基金 (Nelson Peltz)"},
    {"cik": "0001029160", "name": "Soros Fund Management LLC",          "name_cn": "索罗斯基金 (George Soros)"},
    {"cik": "0001536411", "name": "Duquesne Family Office",             "name_cn": "杜肯家族 (Druckenmiller)"},
    {"cik": "0001656456", "name": "Appaloosa LP",                       "name_cn": "阿帕卢萨 (David Tepper)"},
    {"cik": "0001040273", "name": "Third Point LLC",                    "name_cn": "第三点 (Dan Loeb)"},
    {"cik": "0001079114", "name": "Greenlight Capital Inc",             "name_cn": "绿光资本 (David Einhorn)"},
    {"cik": "0001035674", "name": "Paulson & Co. Inc.",                 "name_cn": "保尔森 (John Paulson)"},

    # === 科技成长与"小虎队" ===
    {"cik": "0001167483", "name": "Tiger Global Management LLC",        "name_cn": "老虎全球 (Chase Coleman)"},
    {"cik": "0001061165", "name": "Lone Pine Capital LLC",              "name_cn": "孤松资本 (Stephen Mandel)"},
    {"cik": "0001103804", "name": "Viking Global Investors LP",         "name_cn": "维京全球 (Andreas Halvorsen)"},
    {"cik": "0001697748", "name": "ARK Investment Management LLC",      "name_cn": "方舟投资 (Cathie Wood)"},
    {"cik": "0001535392", "name": "Coatue Management LLC",              "name_cn": "科图管理 (Philippe Laffont)"},

    # === 中概与亚太关注 ===
    {"cik": "0001762304", "name": "HHLR Advisors, Ltd.",                "name_cn": "高瓴资本 (HHLR)"},
    {"cik": "0001709323", "name": "Himalaya Capital Management",        "name_cn": "喜马拉雅资本 (李录)"},
    {"cik": "0001659771", "name": "Greenwoods Asset Management Ltd",    "name_cn": "景林资产 (Greenwoods)"},
    {"cik": "0001608677", "name": "Aspex Management (HK) Ltd",          "name_cn": "Aspex Management"},
    {"cik": "0001844971", "name": "Tencent Holdings Ltd",               "name_cn": "腾讯控股投资部"},
    {"cik": "0001594968", "name": "Alibaba Group Holding Ltd",          "name_cn": "阿里巴巴投资部"},
    {"cik": "0001859942", "name": "Yiheng Capital Management",          "name_cn": "毅恒资本 (Yiheng)"},

    # === Dataroma 机构批量引入 ===
    {"cik": "0001790927", "name": "AKO CAPITAL MANAGEMENT, LLC", "name_cn": "AKO Capital"},
    {"cik": "0001505773", "name": "APPLEBEE'S RESTAURANTS MID-ATLANTIC LLC", "name_cn": "Alex Roepers - Atlantic Investment Management"},
    {"cik": "0001172921", "name": "ALTAROCK FUND LP", "name_cn": "AltaRock Partners"},
    {"cik": "0001166559", "name": "BILL & MELINDA GATES FOUNDATION TRUST", "name_cn": "Bill & Melinda Gates Foundation Trust"},
    {"cik": "0001313682", "name": "PERSHING SQUARE LP", "name_cn": "Bill Ackman - Pershing Square Capital Management"},
    {"cik": "0001135778", "name": "MILLER VALUE PARTNERS, LLC", "name_cn": "Bill Miller - Miller Value Partners"},
    {"cik": "0001657335", "name": "OAKCLIFF CAPITAL PARTNERS, LP", "name_cn": "Bryan Lawrence - Oakcliff Capital"},
    {"cik": "0000881188", "name": "ICAHN & CO INC", "name_cn": "Carl Icahn - Icahn Capital Management"},
    {"cik": "0001167483", "name": "TIGER GLOBAL MANAGEMENT LLC", "name_cn": "Chase Coleman - Tiger Global Management"},
    {"cik": "0001647251", "name": "TCI FUND MANAGEMENT LTD", "name_cn": "Chris Hohn - TCI Fund Management"},
    {"cik": "0001293803", "name": "SEMPER AUGUSTUS INVESTMENT PARTNERS LP", "name_cn": "Christopher Bloomstran - Semper Augustus"},
    {"cik": "0001128295", "name": "DAVIS & ASSOCIATES", "name_cn": "Christopher Davis - Davis Advisors"},
    {"cik": "0001112520", "name": "AKRE CAPITAL MANAGEMENT LLC", "name_cn": "Chuck Akre - Akre Capital Management"},
    {"cik": "0001422119", "name": "CAS CORP", "name_cn": "Clifford Sosin - CAS Investment Partners"},
    {"cik": "0001040273", "name": "THIRD POINT LLC", "name_cn": "Daniel Loeb - Third Point"},
    {"cik": "0001112443", "name": "ABRAMS CAPITAL LLC", "name_cn": "David Abrams - Abrams Capital Management"},
    {"cik": "0001079114", "name": "GREENLIGHT CAPITAL INC", "name_cn": "David Einhorn - Greenlight Capital"},
    {"cik": "0000944725", "name": "MATRIX CAPITAL CORP /CO/", "name_cn": "David Katz - Matrix Asset Advisors"},
    {"cik": "0001766017", "name": "WEDGEWOOD CAPITAL LLC", "name_cn": "David Rolfe - Wedgewood Partners"},
    {"cik": "0001660080", "name": "APPALOOSA CAPITAL INC.", "name_cn": "David Tepper - Appaloosa Management"},
    {"cik": "0001766908", "name": "SHAWSPRING PARTNERS LLC", "name_cn": "Dennis Hong - ShawSpring Partners"},
    {"cik": "0000200217", "name": "DODGE & COX", "name_cn": "Dodge & Cox"},
    {"cik": "0001759760", "name": "H&H INTERNATIONAL INVESTMENT, LLC", "name_cn": "Duan Yongping - H&H International Investment"},
    {"cik": "0000906352", "name": "FIRST EAGLE  FUNDS INC", "name_cn": "First Eagle Investment Management"},
    {"cik": "0002029087", "name": "CHANG TAO-CHOU", "name_cn": "Francis Chou - Chou Associates"},
    {"cik": "0002034934", "name": "GIVERNY CAPITAL ADVISORS LLC", "name_cn": "Francois Rochon - Giverny Capital"},
    {"cik": "0001553733", "name": "BRAVE WARRIOR ADVISORS, LLC", "name_cn": "Glenn Greenberg - Brave Warrior Advisors"},
    {"cik": "0001559771", "name": "ENGAGED CAPITAL LLC", "name_cn": "Glenn Welling - Engaged Capital"},
    {"cik": "0000846222", "name": "GREENHAVEN ASSOCIATES INC", "name_cn": "Greenhaven Associates"},
    {"cik": "0001294389", "name": "COLORADO LESSOR - CONIFER, INC.", "name_cn": "Greg Alexander - Conifer Management"},
    {"cik": "0001404599", "name": "AQUAMARINE CAPITAL MANAGEMENT, LLC", "name_cn": "Guy Spier - Aquamarine Capital"},
    {"cik": "0000764157", "name": "SOUND SHORE FUND INC", "name_cn": "Harry Burn - Sound Shore"},
    {"cik": "0001798849", "name": "DURABLE CAPITAL PARTNERS LP", "name_cn": "Henry Ellenbogen - Durable Capital Partners"},
    {"cik": "0001425161", "name": "OAKTREE ASSET MANAGEMENT, LLC", "name_cn": "Howard Marks - Oaktree Capital Management"},
    {"cik": "0001594744", "name": "CORR-JENSEN INC.", "name_cn": "Jensen Investment Management"},
    {"cik": "0001083657", "name": "EGERTON CAPITAL LTD", "name_cn": "John Armitage - Egerton Capital"},
    {"cik": "0001766504", "name": "GREENLEA LANE CAPITAL MANAGEMENT, LLC", "name_cn": "Josh Tarasoff - Greenlea Lane Capital"},
    {"cik": "0000276931", "name": "KAHN BROTHERS & CO. INC.", "name_cn": "Kahn Brothers Group"},
    {"cik": "0001515007", "name": "HUIZENGA OPPORTUNITY PARTNERS - MAVERICK, LP", "name_cn": "Lee Ainslie - Maverick Capital"},
    {"cik": "0000898382", "name": "COOPERMAN LEON G", "name_cn": "Leon Cooperman"},
    {"cik": "0001709323", "name": "HIMALAYA CAPITAL MANAGEMENT LLC", "name_cn": "Li Lu - Himalaya Capital Management"},
    {"cik": "0001484150", "name": "LINDSELL TRAIN LTD", "name_cn": "Lindsell Train"},
    {"cik": "0000061628", "name": "MAIRS & POWER GROWTH FUND INC", "name_cn": "Mairs & Power Growth Fund"},
    {"cik": "0001649339", "name": "SCION ASSET MANAGEMENT, LLC", "name_cn": "Michael Burry - Scion Asset Management"},
    {"cik": "0001459360", "name": "BA HEDGE FUND DIRECT - TRIAN PARTNERS", "name_cn": "Nelson Peltz - Trian Fund Management"},
    {"cik": "0001419050", "name": "PUNCH CARD CAPITAL LLC", "name_cn": "Norbert Lou - Punch Card Management"},
    {"cik": "0000029805", "name": "DORSEY & COMPANY, INC.", "name_cn": "Pat Dorsey - Dorsey Asset Management"},
    {"cik": "0001034524", "name": "POLEN CAPITAL MANAGEMENT INC", "name_cn": "Polen Capital Management"},
    {"cik": "0000915191", "name": "FAIRFAX FINANCIAL HOLDINGS INC", "name_cn": "Prem Watsa - Fairfax Financial Holdings"},
    {"cik": "0000944690", "name": "OLSTEIN FUNDS", "name_cn": "Robert Olstein - Olstein Capital Management"},
    {"cik": "0001766596", "name": "RV CAPITAL GMBH", "name_cn": "Robert Vinall - RV Capital GmbH"},
    {"cik": "0001080807", "name": "SEQUOIA CORP", "name_cn": "Ruane Cunniff - Sequoia Fund"},
    {"cik": "0001854794", "name": "PATIENT CAPITAL MANAGEMENT, LLC", "name_cn": "Samantha McLemore - Patient Capital Management"},
    {"cik": "0001264585", "name": "CAUSEWAY ASSOCIATES LP", "name_cn": "Sarah Ketterer - Causeway Capital Management"},
    {"cik": "0000865827", "name": "BAUPOST FUND", "name_cn": "Seth Klarman - Baupost Group"},
    {"cik": "0001061165", "name": "LONE PINE CAPITAL LLC", "name_cn": "Stephen Mandel - Lone Pine Capital"},
    {"cik": "0001002858", "name": "THIRD AVENUE MANAGEMENT LLC", "name_cn": "Third Avenue Management"},
    {"cik": "0001389244", "name": "MARKEL CAPITAL LTD", "name_cn": "Thomas Gayner - Markel Group"},
    {"cik": "0000860643", "name": "GARDNER RUSSO & QUINN LLC", "name_cn": "Thomas Russo - Gardner Russo & Quinn"},
    {"cik": "0001540866", "name": "MAKAIRA PARTNERS LLC", "name_cn": "Tom Bancroft - Makaira Partners"},
    {"cik": "0001007028", "name": "TORRAY CORP", "name_cn": "Torray Funds"},
    {"cik": "0001454502", "name": "TRIPLE FROND PARTNERS LLC", "name_cn": "Triple Frond Partners"},
    {"cik": "0000728086", "name": "TWEEDY BROWNE CO LLC", "name_cn": "Tweedy Browne Co. - Tweedy Browne Value Fund"},
    {"cik": "0001697868", "name": "VALLEY FORGE ADVISORS, LLC", "name_cn": "Valley Forge Capital Management"},
    {"cik": "0001351073", "name": "VALUEACT CAPITAL MANAGEMENT, LLC", "name_cn": "ValueAct Capital"},
    {"cik": "0001103804", "name": "VIKING GLOBAL INVESTORS LP", "name_cn": "Viking Global Investors"},
    {"cik": "0001257927", "name": "WEITZ FUNDS", "name_cn": "Wallace Weitz - Weitz Investment Management"},
    {"cik": "0001067983", "name": "BERKSHIRE HATHAWAY INC", "name_cn": "Warren Buffett - Berkshire Hathaway"},
    {"cik": "0001279936", "name": "CANTILLON CAPITAL MANAGEMENT LLC", "name_cn": "William Von Mueffling - Cantillon Capital Management"},
    {"cik": "0000905567", "name": "YACKTMAN ASSET MANAGEMENT LP", "name_cn": "Yacktman Asset Management"},
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
# 调度配置
# ============================================================
# 13F 季度提交截止日期后约 46 天，设置在每季度的最后一个月 + 46 天
# 即每年 2/15, 5/15, 8/14, 11/14 附近运行
SCHEDULE_MONTHS = "2,5,8,11"
SCHEDULE_DAY = "16"
SCHEDULE_HOUR = "9"

# ============================================================
# API 服务配置
# ============================================================
API_HOST = "0.0.0.0"
API_PORT = 5000
