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
    {"cik": "0001067983", "name": "Berkshire Hathaway Inc",           "name_cn": "伯克希尔·哈撒韦"},
    {"cik": "0001350694", "name": "Bridgewater Associates, LP",       "name_cn": "桥水基金"},
    {"cik": "0001709323", "name": "Himalaya Capital Management",      "name_cn": "喜马拉雅资本"},
    {"cik": "0001037389", "name": "Renaissance Technologies LLC",     "name_cn": "文艺复兴科技"},
    {"cik": "0001423053", "name": "Citadel Advisors LLC",             "name_cn": "城堡投资"},
    {"cik": "0001167483", "name": "Tiger Global Management LLC",      "name_cn": "老虎全球"},
    {"cik": "0001029160", "name": "Soros Fund Management LLC",        "name_cn": "索罗斯基金"},
    {"cik": "0001510589", "name": "Hillhouse Capital Management",     "name_cn": "高瓴资本"},
    {"cik": "0001364742", "name": "BlackRock Inc.",                    "name_cn": "贝莱德"},
    {"cik": "0000102909", "name": "Vanguard Group Inc",               "name_cn": "先锋集团"},
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
