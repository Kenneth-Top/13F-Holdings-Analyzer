# -*- coding: utf-8 -*-
"""13F 持仓分析系统 - 配置文件 (Dataroma 数据源)"""

import os

# ============================================================
# Dataroma 爬虫配置
# ============================================================
DATAROMA_BASE = "https://www.dataroma.com/m"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Referer": "https://www.dataroma.com/m/home.php",
}
REQUEST_DELAY = 1.5  # 秒

# ============================================================
# 路径配置
# ============================================================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
HOLDINGS_DIR = os.path.join(DATA_DIR, "holdings")
FUNDS_CSV = os.path.join(DATA_DIR, "funds.csv")

# ============================================================
# 完整基金列表 (Dataroma Superinvestors, ~75 家)
# fund_id = Dataroma URL 参数 m 的值
# ============================================================
FUNDS = [
    {"fund_id": "AKO",   "name": "AKO Capital",                                    "name_cn": "AKO资本"},
    {"fund_id": "AIM",   "name": "Alex Roepers - Atlantic Investment Management",   "name_cn": "大西洋投资 (Alex Roepers)"},
    {"fund_id": "AP",    "name": "AltaRock Partners",                               "name_cn": "AltaRock Partners"},
    {"fund_id": "psc",   "name": "Bill Ackman - Pershing Square Capital",           "name_cn": "潘兴广场 (Bill Ackman)"},
    {"fund_id": "GFT",   "name": "Bill & Melinda Gates Foundation Trust",           "name_cn": "盖茨基金会"},
    {"fund_id": "LMM",   "name": "Bill Miller - Miller Value Partners",             "name_cn": "米勒价值 (Bill Miller)"},
    {"fund_id": "oaklx", "name": "Bill Nygren - Oakmark Select Fund",               "name_cn": "橡树精选 (Bill Nygren)"},
    {"fund_id": "fairx", "name": "Bruce Berkowitz - Fairholme Capital",             "name_cn": "公平港资本 (Bruce Berkowitz)"},
    {"fund_id": "OCL",   "name": "Bryan Lawrence - Oakcliff Capital",               "name_cn": "橡崖资本 (Bryan Lawrence)"},
    {"fund_id": "ic",    "name": "Carl Icahn - Icahn Capital Management",           "name_cn": "伊坎资本 (Carl Icahn)"},
    {"fund_id": "ARFFX", "name": "Charles Bobrinskoy - Ariel Focus Fund",           "name_cn": "爱丽儿焦点基金 (Charles Bobrinskoy)"},
    {"fund_id": "TGM",   "name": "Chase Coleman - Tiger Global Management",         "name_cn": "老虎全球 (Chase Coleman)"},
    {"fund_id": "tci",   "name": "Chris Hohn - TCI Fund Management",                "name_cn": "TCI基金 (Chris Hohn)"},
    {"fund_id": "SA",    "name": "Christopher Bloomstran - Semper Augustus",         "name_cn": "塞珀奥古斯都 (Christopher Bloomstran)"},
    {"fund_id": "DAV",   "name": "Christopher Davis - Davis Advisors",              "name_cn": "戴维斯顾问 (Christopher Davis)"},
    {"fund_id": "AC",    "name": "Chuck Akre - Akre Capital Management",            "name_cn": "阿克里资本 (Chuck Akre)"},
    {"fund_id": "CAS",   "name": "Clifford Sosin - CAS Investment Partners",        "name_cn": "CAS投资 (Clifford Sosin)"},
    {"fund_id": "tp",    "name": "Daniel Loeb - Third Point",                       "name_cn": "第三点 (Daniel Loeb)"},
    {"fund_id": "abc",   "name": "David Abrams - Abrams Capital Management",        "name_cn": "亚伯拉罕资本 (David Abrams)"},
    {"fund_id": "GLRE",  "name": "David Einhorn - Greenlight Capital",              "name_cn": "绿光资本 (David Einhorn)"},
    {"fund_id": "MAVFX", "name": "David Katz - Matrix Asset Advisors",              "name_cn": "矩阵资产 (David Katz)"},
    {"fund_id": "WP",    "name": "David Rolfe - Wedgewood Partners",                "name_cn": "韦奇伍德 (David Rolfe)"},
    {"fund_id": "AM",    "name": "David Tepper - Appaloosa Management",             "name_cn": "阿帕卢萨 (David Tepper)"},
    {"fund_id": "SP",    "name": "Dennis Hong - ShawSpring Partners",               "name_cn": "肖斯普林 (Dennis Hong)"},
    {"fund_id": "HH",    "name": "Duan Yongping - H&H International Investment",    "name_cn": "步步高投资 (段永平)"},
    {"fund_id": "FE",    "name": "First Eagle Investment Management",               "name_cn": "第一鹰投资"},
    {"fund_id": "FPACX", "name": "Steven Romick - FPA Crescent Fund",               "name_cn": "FPA新月基金 (Steven Romick)"},
    {"fund_id": "FPPTX", "name": "FPA Queens Road Small Cap Value Fund",            "name_cn": "FPA皇后路小盘价值基金"},
    {"fund_id": "ca",    "name": "Francis Chou - Chou Associates",                  "name_cn": "周氏资本 (Francis Chou)"},
    {"fund_id": "GC",    "name": "Francois Rochon - Giverny Capital",               "name_cn": "吉维尼资本 (Francois Rochon)"},
    {"fund_id": "CCM",   "name": "Glenn Greenberg - Brave Warrior Advisors",        "name_cn": "勇武顾问 (Glenn Greenberg)"},
    {"fund_id": "ENG",   "name": "Glenn Welling - Engaged Capital",                 "name_cn": "恩格资本 (Glenn Welling)"},
    {"fund_id": "CM",    "name": "Greg Alexander - Conifer Management",             "name_cn": "松柏资管 (Greg Alexander)"},
    {"fund_id": "aq",    "name": "Guy Spier - Aquamarine Capital",                  "name_cn": "碧水资本 (Guy Spier)"},
    {"fund_id": "SSHFX", "name": "Harry Burn - Sound Shore",                        "name_cn": "滨海基金 (Harry Burn)"},
    {"fund_id": "DCP",   "name": "Henry Ellenbogen - Durable Capital Partners",     "name_cn": "耐久资本 (Henry Ellenbogen)"},
    {"fund_id": "hcmax", "name": "Hillman Value Fund",                              "name_cn": "希尔曼价值基金"},
    {"fund_id": "oc",    "name": "Howard Marks - Oaktree Capital Management",       "name_cn": "橡树资本 (Howard Marks)"},
    {"fund_id": "JIM",   "name": "Jensen Investment Management",                    "name_cn": "詹森投资"},
    {"fund_id": "EC",    "name": "John Armitage - Egerton Capital",                  "name_cn": "埃格顿资本 (John Armitage)"},
    {"fund_id": "CAAPX", "name": "John Rogers - Ariel Appreciation Fund",           "name_cn": "爱丽儿升值基金 (John Rogers)"},
    {"fund_id": "GLC",   "name": "Josh Tarasoff - Greenlea Lane Capital",           "name_cn": "绿地巷资本 (Josh Tarasoff)"},
    {"fund_id": "KB",    "name": "Kahn Brothers Group",                             "name_cn": "卡恩兄弟"},
    {"fund_id": "mc",    "name": "Lee Ainslie - Maverick Capital",                  "name_cn": "独行侠资本 (Lee Ainslie)"},
    {"fund_id": "HC",    "name": "Li Lu - Himalaya Capital Management",             "name_cn": "喜马拉雅资本 (李录)"},
    {"fund_id": "DODGX", "name": "Dodge & Cox",                                      "name_cn": "道奇考克斯"},
    {"fund_id": "MPGFX", "name": "Mairs & Power Growth Fund",                       "name_cn": "Mairs & Power增长基金"},
    {"fund_id": "LLPFX", "name": "Mason Hawkins - Longleaf Partners",               "name_cn": "长叶合伙 (Mason Hawkins)"},
    {"fund_id": "MVALX", "name": "Meridian Contrarian Fund",                        "name_cn": "经络逆向基金"},
    {"fund_id": "SAM",   "name": "Michael Burry - Scion Asset Management",          "name_cn": "大空头资本 (Michael Burry)"},
    {"fund_id": "PI",    "name": "Mohnish Pabrai - Pabrai Investments",             "name_cn": "帕布莱投资 (Mohnish Pabrai)"},
    {"fund_id": "PC",    "name": "Norbert Lou - Punch Card Management",             "name_cn": "打卡资本 (Norbert Lou)"},
    {"fund_id": "DA",    "name": "Pat Dorsey - Dorsey Asset Management",            "name_cn": "多尔西资管 (Pat Dorsey)"},
    {"fund_id": "FFH",   "name": "Prem Watsa - Fairfax Financial Holdings",         "name_cn": "枫信金融 (Prem Watsa)"},
    {"fund_id": "pzfvx", "name": "Richard Pzena - Hancock Classic Value",           "name_cn": "汉考克经典价值 (Richard Pzena)"},
    {"fund_id": "OFALX", "name": "Robert Olstein - Olstein Capital Management",     "name_cn": "奥尔斯坦资管 (Robert Olstein)"},
    {"fund_id": "SEQUX", "name": "Ruane Cunniff - Sequoia Fund",                    "name_cn": "红杉基金 (Ruane Cunniff)"},
    {"fund_id": "PTNT",  "name": "Samantha McLemore - Patient Capital Management",  "name_cn": "耐心资本 (Samantha McLemore)"},
    {"fund_id": "CAU",   "name": "Sarah Ketterer - Causeway Capital Management",    "name_cn": "通道资管 (Sarah Ketterer)"},
    {"fund_id": "bau",   "name": "Seth Klarman - Baupost Group",                    "name_cn": "鲍波斯特 (Seth Klarman)"},
    {"fund_id": "LPC",   "name": "Stephen Mandel - Lone Pine Capital",              "name_cn": "孤松资本 (Stephen Mandel)"},
    {"fund_id": "FS",    "name": "Terry Smith - Fundsmith",                          "name_cn": "Fundsmith (Terry Smith)"},
    {"fund_id": "TA",    "name": "Third Avenue Management",                         "name_cn": "第三大道"},
    {"fund_id": "MKL",   "name": "Thomas Gayner - Markel Group",                    "name_cn": "马克尔集团 (Thomas Gayner)"},
    {"fund_id": "GR",    "name": "Thomas Russo - Gardner Russo & Quinn",            "name_cn": "加德纳-鲁索 (Thomas Russo)"},
    {"fund_id": "MP",    "name": "Tom Bancroft - Makaira Partners",                  "name_cn": "马凯拉 (Tom Bancroft)"},
    {"fund_id": "T",     "name": "Torray Funds",                                    "name_cn": "Torray基金"},
    {"fund_id": "TWEBX", "name": "Tweedy Browne - Value Fund",                      "name_cn": "特维迪布朗价值基金"},
    {"fund_id": "VA",    "name": "ValueAct Capital",                                 "name_cn": "ValueAct资本"},
    {"fund_id": "WIM",   "name": "Wallace Weitz - Weitz Investment Management",     "name_cn": "韦茨投资 (Wallace Weitz)"},
    {"fund_id": "BRK",   "name": "Warren Buffett - Berkshire Hathaway",              "name_cn": "伯克希尔·哈撒韦 (Warren Buffett)"},
    {"fund_id": "cc",    "name": "William Von Mueffling - Cantillon Capital",       "name_cn": "坎蒂隆资本 (William Von Mueffling)"},
]
