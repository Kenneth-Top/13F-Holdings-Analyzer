# -*- coding: utf-8 -*-
"""
Flask API 服务
提供 13F 持仓数据的 REST API，同时托管前端静态文件
"""

import os
import sys

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

# 添加 backend 目录到 path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import API_HOST, API_PORT
from database import (
    init_db, get_fund_list, get_periods, get_holdings,
    get_all_holdings, get_history_composition, get_filing_total
)

app = Flask(__name__, static_folder=None)
CORS(app)

FRONTEND_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend")


# ============================================================
# 静态文件服务
# ============================================================
@app.route("/")
def index():
    return send_from_directory(FRONTEND_DIR, "index.html")


@app.route("/css/<path:filename>")
def css(filename):
    return send_from_directory(os.path.join(FRONTEND_DIR, "css"), filename)


@app.route("/js/<path:filename>")
def js(filename):
    return send_from_directory(os.path.join(FRONTEND_DIR, "js"), filename)


# ============================================================
# REST API
# ============================================================
@app.route("/api/funds")
def api_funds():
    """获取所有基金列表"""
    funds = get_fund_list()
    return jsonify({"funds": funds})


@app.route("/api/periods/<cik>")
def api_periods(cik):
    """获取某基金可用的季度列表"""
    periods = get_periods(cik)
    return jsonify({"periods": periods})


@app.route("/api/holdings/<cik>")
def api_holdings(cik):
    """
    获取某基金某季度的持仓数据
    Query params:
      - period: 季度标识如 '2025-Q4' (默认最新)
      - limit: 返回数量 (默认 20)
    """
    period = request.args.get("period")
    limit = request.args.get("limit", 20, type=int)

    # 如果没有指定季度，取最新的
    if not period:
        periods = get_periods(cik)
        if periods:
            period = periods[0]["period"]
        else:
            return jsonify({"holdings": [], "period": None, "total_value": 0})

    holdings = get_holdings(cik, period, limit=limit)
    total_value = get_filing_total(cik, period)

    return jsonify({
        "holdings": holdings,
        "period": period,
        "total_value": total_value,
    })


@app.route("/api/holdings/<cik>/changes")
def api_changes(cik):
    """
    获取某基金某季度的持仓变化 (Top5 加码/减码)
    Query params:
      - period: 季度标识如 '2025-Q4'
    """
    period = request.args.get("period")
    if not period:
        periods = get_periods(cik)
        if periods:
            period = periods[0]["period"]
        else:
            return jsonify({"increases": [], "decreases": [], "period": None})

    all_holdings = get_all_holdings(cik, period)

    # 分类
    increases = []  # 加码·新建
    decreases = []  # 减码·出清

    for h in all_holdings:
        change = h.get("shares_change_pct", 0)
        if change > 0:
            increases.append(h)
        elif change < 0:
            decreases.append(h)

    # 加码排序: 按持仓变化百分比降序
    increases.sort(key=lambda x: x.get("shares_change_pct", 0), reverse=True)
    # 减码排序: 按持仓变化百分比升序 (负值越大减仓越多)
    decreases.sort(key=lambda x: x.get("shares_change_pct", 0))

    return jsonify({
        "increases": increases[:5],
        "decreases": decreases[:5],
        "period": period,
    })


@app.route("/api/holdings/<cik>/history")
def api_history(cik):
    """
    获取某基金全部季度的资产类别构成 (用于堆叠柱状图)
    """
    composition = get_history_composition(cik)

    # 整理成前端友好的格式
    # { periods: ["2023-Q1", ...], series: { "股票": [80, 75, ...], "ETF": [...] } }
    periods = []
    series = {}

    for row in composition:
        period = row["period"]
        asset_class = row["asset_class"] or "其他"
        total = row["total_value"]
        class_value = row["class_value"]

        if period not in periods:
            periods.append(period)

        if asset_class not in series:
            series[asset_class] = {}

        pct = round((class_value / total) * 100, 2) if total > 0 else 0
        series[asset_class][period] = pct

    # 补齐缺失值为 0
    result_series = []
    for cls, values in series.items():
        data = [values.get(p, 0) for p in periods]
        result_series.append({"name": cls, "data": data})

    return jsonify({
        "periods": periods,
        "series": result_series,
    })


if __name__ == "__main__":
    init_db()
    print(f"13F 持仓分析系统启动中...")
    print(f"访问 http://localhost:{API_PORT}")
    app.run(host=API_HOST, port=API_PORT, debug=True)
