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
    {"cik": "0001364742", "name": "BlackRock Inc.",                    "name_cn": "贝莱德"},
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
    {"cik": "0001510589", "name": "Hillhouse Investment Management",    "name_cn": "高瓴资本 (HHLR)"},
    {"cik": "0001709323", "name": "Himalaya Capital Management",        "name_cn": "喜马拉雅资本 (李录)"},
    {"cik": "0001659771", "name": "Greenwoods Asset Management Ltd",    "name_cn": "景林资产 (Greenwoods)"},
    {"cik": "0001608677", "name": "Aspex Management (HK) Ltd",          "name_cn": "Aspex Management"},
    {"cik": "0001844971", "name": "Tencent Holdings Ltd",               "name_cn": "腾讯控股投资部"},
    {"cik": "0001594968", "name": "Alibaba Group Holding Ltd",          "name_cn": "阿里巴巴投资部"},
    {"cik": "0001859942", "name": "Yiheng Capital Management",          "name_cn": "毅恒资本 (Yiheng)"},
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
