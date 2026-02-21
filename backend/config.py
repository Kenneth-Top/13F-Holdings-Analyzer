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
# 命名规范: name_cn = "中文名 (经理人/品牌)" 或 "中文名" (纯机构)
# 注意: 每个 CIK 只能出现一次，避免重复
FUNDS = [
    # === 综合投行与资管巨头 ===
    {"cik": "0001086364", "name": "BlackRock Fund Advisors",             "name_cn": "贝莱德"},
    {"cik": "0000102909", "name": "Vanguard Group Inc",                  "name_cn": "先锋集团"},
    {"cik": "0000093751", "name": "State Street Corp",                   "name_cn": "道富集团"},
    {"cik": "0000019617", "name": "JPMorgan Chase & Co",                 "name_cn": "摩根大通"},
    {"cik": "0000886982", "name": "Goldman Sachs Group Inc",             "name_cn": "高盛集团"},
    {"cik": "0000315066", "name": "FMR LLC",                             "name_cn": "富达投资"},
    {"cik": "0001000275", "name": "T Rowe Price Associates Inc",         "name_cn": "普信集团"},

    # === 价值投资与老牌长线基金 ===
    {"cik": "0001067983", "name": "Berkshire Hathaway Inc",              "name_cn": "伯克希尔·哈撒韦 (Warren Buffett)"},
    {"cik": "0001061768", "name": "Baupost Group LLC",                   "name_cn": "鲍波斯特 (Seth Klarman)"},
    {"cik": "0001173334", "name": "Pabrai Mohnish",                      "name_cn": "帕布莱投资 (Mohnish Pabrai)"},
    {"cik": "0001056831", "name": "Fairholme Capital Management",        "name_cn": "费尔霍姆 (Bruce Berkowitz)"},
    {"cik": "0000807985", "name": "GAMCO Investors, Inc.",               "name_cn": "GAMCO (Mario Gabelli)"},
    {"cik": "0001336528", "name": "Pershing Square Capital",             "name_cn": "潘兴广场 (Bill Ackman)"},
    {"cik": "0001112520", "name": "Akre Capital Management LLC",         "name_cn": "阿克里资本 (Chuck Akre)"},
    {"cik": "0001112443", "name": "Abrams Capital LLC",                  "name_cn": "艾布拉姆斯资本 (David Abrams)"},
    {"cik": "0001293803", "name": "Semper Augustus Investment Partners",  "name_cn": "永恒奥古斯都 (Christopher Bloomstran)"},
    {"cik": "0001128295", "name": "Davis Advisors",                      "name_cn": "戴维斯基金 (Christopher Davis)"},
    {"cik": "0000200217", "name": "Dodge & Cox",                         "name_cn": "道奇考克斯"},
    {"cik": "0000906352", "name": "First Eagle Funds Inc",               "name_cn": "第一鹰投资"},
    {"cik": "0001034524", "name": "Polen Capital Management Inc",        "name_cn": "波伦资本"},
    {"cik": "0001002858", "name": "Third Avenue Management LLC",         "name_cn": "第三大道管理"},
    {"cik": "0001389244", "name": "Markel Group",                        "name_cn": "马克尔集团 (Thomas Gayner)"},
    {"cik": "0000860643", "name": "Gardner Russo & Quinn LLC",           "name_cn": "加德纳-鲁索 (Thomas Russo)"},
    {"cik": "0000728086", "name": "Tweedy Browne Co LLC",                "name_cn": "推迪布朗"},
    {"cik": "0001257927", "name": "Weitz Funds",                         "name_cn": "韦茨投资 (Wallace Weitz)"},
    {"cik": "0000905567", "name": "Yacktman Asset Management LP",        "name_cn": "亚克曼资产"},
    {"cik": "0000865827", "name": "Baupost Fund",                        "name_cn": "鲍波斯特基金 (Seth Klarman)"},
    {"cik": "0001080807", "name": "Sequoia Fund",                        "name_cn": "红杉基金 (Ruane Cunniff)"},
    {"cik": "0001007028", "name": "Torray Corp",                         "name_cn": "托雷基金"},
    {"cik": "0000276931", "name": "Kahn Brothers & Co. Inc.",            "name_cn": "卡恩兄弟"},

    # === 对冲基金与量化巨头 ===
    {"cik": "0001350694", "name": "Bridgewater Associates, LP",          "name_cn": "桥水基金 (Ray Dalio)"},
    {"cik": "0001037389", "name": "Renaissance Technologies LLC",        "name_cn": "文艺复兴 (Jim Simons)"},
    {"cik": "0001423053", "name": "Citadel Advisors LLC",                "name_cn": "城堡投资 (Ken Griffin)"},
    {"cik": "0001273087", "name": "Millennium Management LLC",           "name_cn": "千禧管理 (Englander)"},
    {"cik": "0001603466", "name": "Point72 Asset Management",            "name_cn": "Point72 (Steve Cohen)"},
    {"cik": "0001179392", "name": "Two Sigma Investments, LP",           "name_cn": "Two Sigma"},
    {"cik": "0001009207", "name": "D. E. Shaw & Co., Inc.",              "name_cn": "德劭基金 (David Shaw)"},
    {"cik": "0001167557", "name": "AQR Capital Management",              "name_cn": "AQR资本 (Cliff Asness)"},

    # === 激进投资与宏观基金 ===
    {"cik": "0000921669", "name": "Icahn Carl C",                        "name_cn": "伊坎资本 (Carl Icahn)"},
    {"cik": "0001048445", "name": "Elliott Investment Management",       "name_cn": "艾略特管理 (Paul Singer)"},
    {"cik": "0001345471", "name": "Trian Fund Management",               "name_cn": "特里安基金 (Nelson Peltz)"},
    {"cik": "0001029160", "name": "Soros Fund Management LLC",           "name_cn": "索罗斯基金 (George Soros)"},
    {"cik": "0001536411", "name": "Duquesne Family Office",              "name_cn": "杜肯家族 (Druckenmiller)"},
    {"cik": "0001656456", "name": "Appaloosa LP",                        "name_cn": "阿帕卢萨 (David Tepper)"},
    {"cik": "0001040273", "name": "Third Point LLC",                     "name_cn": "第三点 (Dan Loeb)"},
    {"cik": "0001079114", "name": "Greenlight Capital Inc",              "name_cn": "绿光资本 (David Einhorn)"},
    {"cik": "0001035674", "name": "Paulson & Co. Inc.",                  "name_cn": "保尔森 (John Paulson)"},
    {"cik": "0001351073", "name": "ValueAct Capital Management, LLC",    "name_cn": "价值行动资本 (ValueAct)"},
    {"cik": "0001559771", "name": "Engaged Capital LLC",                 "name_cn": "恩格资本 (Glenn Welling)"},

    # === 科技成长与"小虎队" ===
    {"cik": "0001167483", "name": "Tiger Global Management LLC",         "name_cn": "老虎全球 (Chase Coleman)"},
    {"cik": "0001061165", "name": "Lone Pine Capital LLC",               "name_cn": "孤松资本 (Stephen Mandel)"},
    {"cik": "0001103804", "name": "Viking Global Investors LP",          "name_cn": "维京全球 (Andreas Halvorsen)"},
    {"cik": "0001697748", "name": "ARK Investment Management LLC",       "name_cn": "方舟投资 (Cathie Wood)"},
    {"cik": "0001535392", "name": "Coatue Management LLC",               "name_cn": "科图管理 (Philippe Laffont)"},
    {"cik": "0001515007", "name": "Maverick Capital",                    "name_cn": "特立资本 (Lee Ainslie)"},
    {"cik": "0001553733", "name": "Brave Warrior Advisors, LLC",         "name_cn": "勇武顾问 (Glenn Greenberg)"},
    {"cik": "0001798849", "name": "Durable Capital Partners LP",         "name_cn": "耐久资本 (Henry Ellenbogen)"},

    # === 中概与亚太关注 ===
    {"cik": "0001762304", "name": "HHLR Advisors, Ltd.",                 "name_cn": "高瓴资本 (HHLR)"},
    {"cik": "0001709323", "name": "Himalaya Capital Management",         "name_cn": "喜马拉雅资本 (李录)"},
    {"cik": "0001659771", "name": "Greenwoods Asset Management Ltd",     "name_cn": "景林资产"},
    {"cik": "0001608677", "name": "Aspex Management (HK) Ltd",           "name_cn": "Aspex管理"},
    {"cik": "0001844971", "name": "Tencent Holdings Ltd",                "name_cn": "腾讯控股投资部"},
    {"cik": "0001594968", "name": "Alibaba Group Holding Ltd",           "name_cn": "阿里巴巴投资部"},
    {"cik": "0001859942", "name": "Yiheng Capital Management",           "name_cn": "毅恒资本"},
    {"cik": "0001759760", "name": "H&H International Investment, LLC",   "name_cn": "步步高投资 (段永平)"},

    # === 知名价值/GARP基金 ===
    {"cik": "0001647251", "name": "TCI Fund Management Ltd",             "name_cn": "TCI基金 (Chris Hohn)"},
    {"cik": "0001790927", "name": "AKO Capital Management, LLC",         "name_cn": "AKO资本"},
    {"cik": "0001505773", "name": "Atlantic Investment Management",      "name_cn": "大西洋投资 (Alex Roepers)"},
    {"cik": "0001172921", "name": "AltaRock Fund LP",                    "name_cn": "高岩基金 (AltaRock)"},
    {"cik": "0001166559", "name": "Bill & Melinda Gates Foundation Trust","name_cn": "盖茨基金会信托"},
    {"cik": "0001135778", "name": "Miller Value Partners, LLC",          "name_cn": "米勒价值 (Bill Miller)"},
    {"cik": "0001657335", "name": "Oakcliff Capital Partners, LP",       "name_cn": "橡崖资本 (Bryan Lawrence)"},
    {"cik": "0001422119", "name": "CAS Investment Partners",             "name_cn": "CAS投资 (Clifford Sosin)"},
    {"cik": "0000944725", "name": "Matrix Asset Advisors",               "name_cn": "矩阵资产 (David Katz)"},
    {"cik": "0001766017", "name": "Wedgewood Partners",                  "name_cn": "韦奇伍德 (David Rolfe)"},
    {"cik": "0001660080", "name": "Appaloosa Capital Inc.",              "name_cn": "阿帕卢萨资本 (David Tepper)"},
    {"cik": "0001766908", "name": "ShawSpring Partners LLC",             "name_cn": "肖斯普林 (Dennis Hong)"},
    {"cik": "0002029087", "name": "Chou Associates",                     "name_cn": "邹氏基金 (Francis Chou)"},
    {"cik": "0002034934", "name": "Giverny Capital Advisors LLC",        "name_cn": "吉维尼资本 (Francois Rochon)"},
    {"cik": "0000846222", "name": "Greenhaven Associates Inc",           "name_cn": "绿港资本"},
    {"cik": "0001294389", "name": "Conifer Management",                  "name_cn": "松柏管理 (Greg Alexander)"},
    {"cik": "0001404599", "name": "Aquamarine Capital Management, LLC",  "name_cn": "碧水资本 (Guy Spier)"},
    {"cik": "0000764157", "name": "Sound Shore Fund Inc",                "name_cn": "海峡基金 (Harry Burn)"},
    {"cik": "0001425161", "name": "Oaktree Asset Management, LLC",       "name_cn": "橡树资本 (Howard Marks)"},
    {"cik": "0001594744", "name": "Jensen Investment Management",        "name_cn": "詹森投资"},
    {"cik": "0001083657", "name": "Egerton Capital Ltd",                 "name_cn": "埃格顿资本 (John Armitage)"},
    {"cik": "0001766504", "name": "Greenlea Lane Capital Management",    "name_cn": "绿地巷资本 (Josh Tarasoff)"},
    {"cik": "0000898382", "name": "Leon Cooperman",                      "name_cn": "库珀曼 (Leon Cooperman)"},
    {"cik": "0001484150", "name": "Lindsell Train Ltd",                  "name_cn": "林德赛尔火车"},
    {"cik": "0000061628", "name": "Mairs & Power Growth Fund Inc",       "name_cn": "梅尔斯成长基金"},
    {"cik": "0001649339", "name": "Scion Asset Management, LLC",         "name_cn": "大空头资本 (Michael Burry)"},
    {"cik": "0001419050", "name": "Punch Card Capital LLC",              "name_cn": "打卡资本 (Norbert Lou)"},
    {"cik": "0000029805", "name": "Dorsey Asset Management",             "name_cn": "多尔西资管 (Pat Dorsey)"},
    {"cik": "0000915191", "name": "Fairfax Financial Holdings Inc",      "name_cn": "枫信金融 (Prem Watsa)"},
    {"cik": "0000944690", "name": "Olstein Funds",                       "name_cn": "奥尔斯坦基金 (Robert Olstein)"},
    {"cik": "0001766596", "name": "RV Capital GmbH",                     "name_cn": "RV资本 (Robert Vinall)"},
    {"cik": "0001854794", "name": "Patient Capital Management, LLC",     "name_cn": "耐心资本 (Samantha McLemore)"},
    {"cik": "0001264585", "name": "Causeway Capital Management",         "name_cn": "通道资本 (Sarah Ketterer)"},
    {"cik": "0001540866", "name": "Makaira Partners LLC",                "name_cn": "马凯拉 (Tom Bancroft)"},
    {"cik": "0001454502", "name": "Triple Frond Partners LLC",           "name_cn": "三叶资本"},
    {"cik": "0001697868", "name": "Valley Forge Capital Management",     "name_cn": "福吉谷资本"},
    {"cik": "0001279936", "name": "Cantillon Capital Management LLC",    "name_cn": "坎蒂隆资本 (William Von Mueffling)"},
    {"cik": "0000881188", "name": "Icahn & Co Inc",                      "name_cn": "伊坎公司 (Carl Icahn)"},
    {"cik": "0001459360", "name": "Trian Partners",                      "name_cn": "特里安合伙 (Nelson Peltz)"},
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
