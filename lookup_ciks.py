# -*- coding: utf-8 -*-
"""验证 CIK 列表是否都有 13F filing"""
import time, requests, json

SESSION = requests.Session()
SESSION.headers.update({
    "User-Agent": "13F-Tracker research@example.com",
    "Accept-Encoding": "gzip, deflate",
})

# 完整的基金 CIK 列表（公开信息）
FUNDS = [
    # === 已有的 10 个 ===
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

    # === 价值投资大师 ===
    {"cik": "0001336528", "name": "Pershing Square Capital Management", "name_cn": "潘兴广场"},          # Bill Ackman
    {"cik": "0001061768", "name": "Baupost Group LLC",                  "name_cn": "鲍波斯特集团"},      # Seth Klarman
    {"cik": "0001173334", "name": "Pabrai Investment Funds",            "name_cn": "帕布莱投资"},        # Mohnish Pabrai
    {"cik": "0001079114", "name": "Greenlight Capital Inc",             "name_cn": "绿光资本"},          # David Einhorn
    {"cik": "0001548609", "name": "Oaktree Capital Management LP",     "name_cn": "橡树资本"},          # Howard Marks
    {"cik": "0000766704", "name": "Tweedy Browne Company LLC",          "name_cn": "特威迪布朗"},        # Tweedy Browne
    {"cik": "0001056831", "name": "Fairholme Capital Management LLC",   "name_cn": "费尔霍姆"},          # Bruce Berkowitz

    # === 对冲基金巨头 ===
    {"cik": "0001656456", "name": "Appaloosa Management LP",            "name_cn": "阿帕卢萨"},          # David Tepper
    {"cik": "0001040273", "name": "Third Point LLC",                    "name_cn": "第三点"},            # Dan Loeb
    {"cik": "0000921669", "name": "Icahn Carl C",                       "name_cn": "伊坎资本"},          # Carl Icahn
    {"cik": "0001345471", "name": "Trian Fund Management LP",           "name_cn": "特里安基金"},        # Nelson Peltz
    {"cik": "0001048445", "name": "Elliott Investment Management LP",   "name_cn": "艾略特管理"},        # Paul Singer
    {"cik": "0001035674", "name": "Paulson & Co Inc",                   "name_cn": "保尔森"},            # John Paulson
    {"cik": "0001061983", "name": "Omega Advisors Inc",                 "name_cn": "欧米茄"},            # Leon Cooperman
    {"cik": "0001536411", "name": "Duquesne Family Office LLC",         "name_cn": "杜肯家族办公室"},    # Druckenmiller
    {"cik": "0001603466", "name": "Point72 Asset Management LP",        "name_cn": "Point72"},           # Steve Cohen
    {"cik": "0001009207", "name": "D E Shaw & Co Inc",                  "name_cn": "德劭基金"},          # David Shaw
    {"cik": "0001179392", "name": "Two Sigma Investments LP",           "name_cn": "Two Sigma"},         # John Overdeck
    {"cik": "0001273087", "name": "Millennium Management LLC",          "name_cn": "千禧管理"},          # Israel Englander
    {"cik": "0001167557", "name": "AQR Capital Management LLC",         "name_cn": "AQR资本"},           # Cliff Asness
    {"cik": "0001535392", "name": "Coatue Management LLC",              "name_cn": "科图管理"},          # Philippe Laffont
    {"cik": "0001061165", "name": "Lone Pine Capital LLC",              "name_cn": "孤松资本"},          # Stephen Mandel
    {"cik": "0001103804", "name": "Viking Global Investors LP",         "name_cn": "维京全球"},          # Andreas Halvorsen
    {"cik": "0001009477", "name": "Maverick Capital Ltd",               "name_cn": "独行侠资本"},        # Lee Ainslie
    {"cik": "0001345032", "name": "ValueAct Capital Management LP",     "name_cn": "价值行动资本"},      # Jeff Ubben
    {"cik": "0001647251", "name": "TCI Fund Management Ltd",            "name_cn": "TCI基金"},           # Chris Hohn

    # === 知名机构 ===
    {"cik": "0001697748", "name": "ARK Investment Management LLC",      "name_cn": "方舟投资"},          # Cathie Wood
    {"cik": "0000807985", "name": "GAMCO Investors Inc",                "name_cn": "GAMCO"},             # Mario Gabelli
    {"cik": "0000029440", "name": "Dodge & Cox",                        "name_cn": "道奇考克斯"},
    {"cik": "0001000275", "name": "T Rowe Price Associates Inc",        "name_cn": "普信集团"},
    {"cik": "0000315066", "name": "Fidelity Management & Research Co",  "name_cn": "富达投资"},
    {"cik": "0000036405", "name": "Capital Research Global Investors",   "name_cn": "资本集团"},
    {"cik": "0000093751", "name": "State Street Corp",                  "name_cn": "道富集团"},
    {"cik": "0000019617", "name": "JPMorgan Chase & Co",                "name_cn": "摩根大通"},
    {"cik": "0000886982", "name": "Goldman Sachs Group Inc",            "name_cn": "高盛集团"},

    # === 其他知名基金 ===
    {"cik": "0001159159", "name": "Abrams Capital Management LP",       "name_cn": "阿布拉姆斯资本"},   # David Abrams
    {"cik": "0001649339", "name": "General Atlantic LLC",               "name_cn": "泛大西洋投资"},
    {"cik": "0001099281", "name": "Causeway Capital Management LLC",    "name_cn": "考斯韦资本"},        # Sarah Ketterer
    {"cik": "0000905571", "name": "Yacktman Asset Management Co",       "name_cn": "雅克曼资管"},        # Donald Yacktman
    {"cik": "0001279708", "name": "Matthews International Capital Mgmt","name_cn": "马修斯亚洲"},        # Matthews Asia
    {"cik": "0001582283", "name": "Brave Warrior Advisors LLC",         "name_cn": "勇猛武士"},          # Glenn Greenberg
]


def verify_cik(cik):
    """验证 CIK 是否在 SEC EDGAR 有 13F filing"""
    cik_clean = cik.lstrip("0") or "0"
    url = f"https://data.sec.gov/submissions/CIK{cik}.json"
    try:
        time.sleep(0.15)
        resp = SESSION.get(url, timeout=15)
        if resp.status_code == 200:
            data = resp.json()
            name = data.get("name", "")
            forms = data.get("filings", {}).get("recent", {}).get("form", [])
            has_13f = "13F-HR" in forms
            return True, name, has_13f
    except:
        pass
    return False, "", False


# 验证
valid = 0
invalid = 0
no_13f = 0
for fund in FUNDS:
    ok, real_name, has_13f = verify_cik(fund["cik"])
    if ok and has_13f:
        print(f"  ✓ {fund['name_cn']:20s} CIK={fund['cik']}  SEC名: {real_name}")
        valid += 1
    elif ok and not has_13f:
        print(f"  ⚠ {fund['name_cn']:20s} CIK={fund['cik']}  SEC名: {real_name}  (无13F)")
        no_13f += 1
    else:
        print(f"  ✗ {fund['name_cn']:20s} CIK={fund['cik']}  (CIK无效)")
        invalid += 1

print(f"\n共 {len(FUNDS)} 个基金: {valid} 有效+有13F, {no_13f} 有效但无13F, {invalid} CIK无效")
