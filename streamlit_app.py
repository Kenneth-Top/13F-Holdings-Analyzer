# -*- coding: utf-8 -*-
"""
13F 机构持仓分析系统 - Streamlit 版
可部署到 Streamlit Cloud，任何人通过链接即可访问
"""

import os
import sys
import sqlite3
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from backend.config import DB_PATH
from backend.database import (
    get_all_holdings,
    get_changes,
    get_history_composition,
    get_filing_total,
    get_fund_list,
    get_holdings,
    get_periods,
    get_global_latest_period,
    get_global_changes,
    get_stock_holders
)

# ============================================================
# 页面配置
# ============================================================
st.set_page_config(
    page_title="13F 机构持仓分析",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
# 自定义样式
# ============================================================
st.markdown("""
<style>
    /* 主题色调 */
    .main .block-container {
        padding-top: 1rem;
        max-width: 1200px;
    }
    /* 指标卡片 */
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 12px;
        padding: 1.2rem;
        color: white;
        text-align: center;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    .metric-card h3 {
        margin: 0;
        font-size: 0.85rem;
        opacity: 0.9;
        font-weight: 400;
    }
    .metric-card .value {
        font-size: 1.6rem;
        font-weight: 700;
        margin-top: 0.3rem;
    }
    .metric-card-green {
        background: linear-gradient(135deg, #00b894 0%, #00cec9 100%);
        box-shadow: 0 4px 15px rgba(0, 184, 148, 0.3);
    }
    .metric-card-orange {
        background: linear-gradient(135deg, #fdcb6e 0%, #e17055 100%);
        box-shadow: 0 4px 15px rgba(253, 203, 110, 0.3);
    }
    .metric-card-blue {
        background: linear-gradient(135deg, #0984e3 0%, #6c5ce7 100%);
        box-shadow: 0 4px 15px rgba(9, 132, 227, 0.3);
    }
    /* 变化标记 */
    .change-positive { color: #00b894; font-weight: 600; }
    .change-negative { color: #e17055; font-weight: 600; }
    .badge-new {
        background: #00b894; color: white; padding: 2px 8px;
        border-radius: 4px; font-size: 0.75rem; font-weight: 600;
    }
    .badge-exit {
        background: #e17055; color: white; padding: 2px 8px;
        border-radius: 4px; font-size: 0.75rem; font-weight: 600;
    }
    /* 隐藏 Streamlit 默认样式 */
    div[data-testid="stMetric"] {
        background: #f8fafc;
        border-radius: 8px;
        padding: 12px;
        border: 1px solid #e8ecef;
    }
    /* 表格美化 */
    .dataframe {
        font-size: 0.85rem !important;
    }
    /* 侧边栏 */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%);
    }
    section[data-testid="stSidebar"] .stSelectbox label,
    section[data-testid="stSidebar"] .stRadio label,
    section[data-testid="stSidebar"] h1, section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3, section[data-testid="stSidebar"] p {
        color: white !important;
    }
</style>
""", unsafe_allow_html=True)


# ============================================================
# 数据库读取函数
# ============================================================
@st.cache_data(ttl=600)
def get_fund_list():
    """获取基金列表"""
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM funds ORDER BY name_cn", conn)
    conn.close()
    return df


@st.cache_data(ttl=600)
def get_periods(fund_cik):
    """获取某基金可用的季度"""
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query(
        "SELECT period, total_value FROM filings WHERE fund_cik = ? ORDER BY period DESC",
        conn, params=(fund_cik,)
    )
    conn.close()
    return df


@st.cache_data(ttl=600)
def get_holdings(fund_cik, period, limit=20):
    """获取持仓数据"""
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query(
        """SELECT h.issuer, h.cusip, h.ticker, h.title_of_class, h.asset_class,
                  h.value, h.shares, h.share_type, h.put_call,
                  h.portfolio_pct, h.prev_pct, h.pct_change, h.shares_change_pct,
                  f.total_value as filing_total_value
           FROM holdings h
           JOIN filings f ON h.filing_id = f.id
           WHERE f.fund_cik = ? AND f.period = ?
           ORDER BY h.value DESC
           LIMIT ?""",
        conn, params=(fund_cik, period, limit)
    )
    conn.close()
    return df


@st.cache_data(ttl=600)
def get_all_holdings(fund_cik, period):
    """获取全部持仓"""
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query(
        """SELECT h.issuer, h.cusip, h.ticker, h.asset_class,
                  h.value, h.shares, h.portfolio_pct, h.pct_change, h.shares_change_pct
           FROM holdings h
           JOIN filings f ON h.filing_id = f.id
           WHERE f.fund_cik = ? AND f.period = ?
           ORDER BY h.value DESC""",
        conn, params=(fund_cik, period)
    )
    conn.close()
    return df


@st.cache_data(ttl=600)
def get_composition_history(fund_cik):
    """获取各季度资产分布"""
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query(
        """SELECT f.period, h.asset_class, SUM(h.value) as class_value, f.total_value
           FROM holdings h
           JOIN filings f ON h.filing_id = f.id
           WHERE f.fund_cik = ?
           GROUP BY f.period, h.asset_class
           ORDER BY f.period ASC""",
        conn, params=(fund_cik,)
    )
    conn.close()
    if not df.empty:
        df["pct"] = df["class_value"] / df["total_value"] * 100
    return df


@st.cache_data(ttl=600)
def get_changes(fund_cik, period):
    """获取持仓变化"""
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query(
        """SELECT h.issuer, h.cusip, h.ticker, h.asset_class,
                  h.value, h.shares, h.portfolio_pct, h.prev_pct,
                  h.pct_change, h.shares_change_pct
           FROM holdings h
           JOIN filings f ON h.filing_id = f.id
           WHERE f.fund_cik = ? AND f.period = ?
           ORDER BY h.value DESC""",
        conn, params=(fund_cik, period)
    )
    conn.close()
    return df


# ============================================================
# 工具函数
# ============================================================
def format_value(val):
    """格式化市值（单位: USD）"""
    if pd.isna(val) or val == 0:
        return "$0"
    
    sign = "-" if val < 0 else ""
    abs_val = abs(val)

    billion = abs_val / 1_000_000_000
    if billion >= 1:
        return f"{sign}${billion:,.2f}B"
    million = abs_val / 1_000_000
    if million >= 1:
        return f"{sign}${million:,.2f}M"
    return f"{sign}${abs_val:,.0f}"


def format_pct(val):
    """格式化百分比"""
    if pd.isna(val):
        return "-"
    sign = "+" if val > 0 else ""
    return f"{sign}{val:.2f}%"


# ============================================================
# 颜色映射
# ============================================================
SECTOR_COLORS = {
    # 普通股（与 yfinance + sector_mapper 统一）
    "股票": "#2ecc71",
    "科技": "#3498db",
    "金融": "#f39c12",
    "医疗": "#9b59b6",
    "能源": "#e74c3c",
    "消费-必需": "#1abc9c",
    "消费-可选": "#e67e22",
    "工业": "#95a5a6",
    "通讯": "#8e44ad",
    "原材料": "#d35400",
    "公用事业": "#27ae60",
    "房地产": "#c0392b",
    # ETF
    "ETF-大型股平衡型": "#2980b9",
    "ETF-综合股市": "#16a085",
    "ETF-科技成熟市场": "#2c3e50",
    "ETF-新兴市场": "#f1c40f",
    "ETF-金融": "#d4ac0d",
    "ETF-医疗保健": "#7d3c98",
    "ETF-能源": "#cb4335",
    "ETF-贵金属": "#f4d03f",
    "ETF-政府公债": "#5dade2",
    "ETF-投资等级公债": "#48c9b0",
    "ETF-高收益债": "#eb984e",
    "ETF-亚太新兴市场": "#45b39d",
    # 期权
    "期权-CALL": "#fdcb6e",
    "期权-PUT": "#e17055",
    # 其他
    "债券": "#6c5ce7",
    "可转债": "#00cec9",
    "权证": "#e84393",
}


# ============================================================
# 主应用逻辑
# ============================================================
def main():
    # 检查数据库
    if not os.path.exists(DB_PATH):
        st.error("⚠️ 数据库文件不存在，请先运行 `python backend/scraper.py` 采集数据。")
        return

    funds_df = get_fund_list()
    if funds_df.empty:
        st.warning("数据库中暂无基金数据。")
        return

    # ---- 侧边栏 ----
    with st.sidebar:
        st.markdown("## 📊 13F 持仓分析")
        st.markdown("---")

        analysis_mode = st.radio(
            "🔎 选择分析模式",
            options=["单只基金分析", "🌍 全局宏观动态", "🔍 个股分析 (Cross-Fund)", "⭐ 自选基金追踪 (Watchlist)"],
            index=0
        )
        st.markdown("---")

        if analysis_mode == "单只基金分析":
            # 基金选择
            fund_options = {
                row["name_cn"]: row["cik"]
                for _, row in funds_df.iterrows()
            }
            selected_fund_name = st.selectbox(
                "🏛️ 选择基金",
                options=list(fund_options.keys()),
                index=0,
            )
            selected_cik = fund_options[selected_fund_name]

            # 获取可用季度
            periods_df = get_periods(selected_cik)
            if periods_df.empty:
                st.warning("该基金暂无数据")
                return

            period_list = periods_df["period"].tolist()
            selected_period = st.selectbox(
                "📅 选择季度",
                options=period_list,
                index=0,
            )

        elif analysis_mode == "🌍 全局宏观动态":
            # 全局模式，只选最新季度 (或其他有数据的季度)
            # 这里简化为系统内最新的可用季度
            latest_period = get_global_latest_period()
            selected_period = latest_period
            
            st.info(f"当前全局统计基于最新可用季度: **{latest_period}**")

        elif analysis_mode == "🔍 个股分析 (Cross-Fund)":
            latest_period = get_global_latest_period()
            selected_period = latest_period
            
            search_ticker = st.text_input("🔍 输入股票代码 (例如: AAPL, TSLA)", value="AAPL").upper().strip()
            st.info(f"查询季度: **{latest_period}**")

        elif analysis_mode == "⭐ 自选基金追踪 (Watchlist)":
            latest_period = get_global_latest_period()
            selected_period = latest_period
            
            # URL 持久化: 从 query_params 恢复自选列表
            fund_options = {row["name_cn"]: row["cik"] for _, row in funds_df.iterrows()}
            cik_to_name = {row["cik"]: row["name_cn"] for _, row in funds_df.iterrows()}
            
            # 读取 URL 参数中的已保存自选
            saved_wl = st.query_params.get("wl", "")
            saved_ciks = [c.strip() for c in saved_wl.split(",") if c.strip()] if saved_wl else []
            default_names = [cik_to_name[c] for c in saved_ciks if c in cik_to_name]
            
            st.info("💡 您的选择会自动保存到网址中，刷新或分享链接均可恢复。")
            selected_fund_names = st.multiselect(
                "⭐ 选择关注的基金",
                options=list(fund_options.keys()),
                default=default_names
            )
            selected_ciks = [fund_options[name] for name in selected_fund_names]
            
            # 写回 URL 参数
            if selected_ciks:
                st.query_params["wl"] = ",".join(selected_ciks)
            elif "wl" in st.query_params:
                del st.query_params["wl"]

        st.markdown("---")
        if analysis_mode not in ["🔍 个股分析 (Cross-Fund)", "⭐ 自选基金追踪 (Watchlist)"]:
            top_n = st.slider("📋 显示 Top N", 5, 50, 20)
            st.markdown("---")
        st.markdown(
            "<div style='color:#9ca3af;font-size:0.75rem;text-align:center'>"
            "数据来源: SEC EDGAR<br>13F 季度报告</div>",
            unsafe_allow_html=True
        )

    # ============================================================
    # 模式: 全局宏观动态
    # ============================================================
    if analysis_mode == "🌍 全局宏观动态":
        st.title("🌍 13F 全局宏观动态")
        st.markdown(f"**统计范围**: 数据库中 {len(funds_df)} 家顶级机构在 {selected_period} 会计季度的统一调仓动作。")
        
        with st.spinner("正在计算全市场数据..."):
            global_df = get_global_changes(selected_period)
            
        if global_df.empty:
            st.warning(f"无法获取 {selected_period} 的全局变化数据 (可能仍在采集中)。")
            return
            
        # 核心指标
        total_stocks = len(global_df)
        total_value_change = global_df['val_change'].sum()
        
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(f'<div class="metric-card"><h3>🏢 覆盖总标的数</h3><div class="value">{total_stocks}</div></div>', unsafe_allow_html=True)
        with c2:
            st.markdown(f'<div class="metric-card"><h3>💰 持仓总市值净变动</h3><div class="value">{format_value(total_value_change)}</div></div>', unsafe_allow_html=True)
        with c3:
            top_sector = global_df.groupby('asset_class')['val_change'].sum().idxmax()
            st.markdown(f'<div class="metric-card"><h3>🔥 最受追捧行业</h3><div class="value">{top_sector}</div></div>', unsafe_allow_html=True)
            
        st.markdown("<br>", unsafe_allow_html=True)
        
        # 排行榜 Tabs
        tab_buy, tab_sell, tab_new, tab_exit = st.tabs([
            "🫂 最多机构加仓", "🏃 最多机构减仓", "🌟 最热新面孔(首次建仓)", "🚪 遭遇共识清仓"
        ])
        
        with tab_buy:
            top_buys = global_df.sort_values('inc_count', ascending=False).head(top_n)
            fig_buy = px.bar(
                top_buys, x="ticker", y="inc_count", color="asset_class",
                title=f"Top {top_n} 被最多机构加仓的标的",
                labels={"inc_count": "加仓机构数", "ticker": "股票代码", "asset_class": "行业"},
                color_discrete_map=SECTOR_COLORS
            )
            st.plotly_chart(fig_buy, use_container_width=True)
            
            tb_df = top_buys[['ticker', 'issuer', 'asset_class', 'inc_count', 'funds_holding', 'val_change']].copy()
            tb_df.columns = ["代码", "公司名", "行业", "加仓机构(家)", "目前总持仓机构(家)", "市值净变动(USD)"]
            tb_df["市值净变动(USD)"] = tb_df["市值净变动(USD)"].apply(format_value)
            st.dataframe(tb_df, use_container_width=True)

        with tab_sell:
            top_sells = global_df.sort_values('dec_count', ascending=False).head(top_n)
            fig_sell = px.bar(
                top_sells, x="ticker", y="dec_count", color="asset_class",
                title=f"Top {top_n} 被最多机构减仓的标的",
                labels={"dec_count": "减仓机构数", "ticker": "股票代码", "asset_class": "行业"},
                color_discrete_map=SECTOR_COLORS
            )
            st.plotly_chart(fig_sell, use_container_width=True)
            
            ts_df = top_sells[['ticker', 'issuer', 'asset_class', 'dec_count', 'funds_holding', 'val_change']].copy()
            ts_df.columns = ["代码", "公司名", "行业", "减仓机构(家)", "目前总持仓机构(家)", "市值净变动(USD)"]
            ts_df["市值净变动(USD)"] = ts_df["市值净变动(USD)"].apply(format_value)
            st.dataframe(ts_df, use_container_width=True)

        with tab_new:
            # 排除由于代码变更导致的伪“新建仓” (如需严谨需要更复杂的 CUSIP 追踪，这里基于简单 ticker)
            new_buys = global_df[global_df['funds_holding'] == global_df['new_count']].sort_values('new_count', ascending=False).head(top_n)
            if not new_buys.empty:
                tn_df = new_buys[['ticker', 'issuer', 'asset_class', 'new_count', 'total_curr_val']].copy()
                tn_df.columns = ["代码", "公司名", "行业", "建仓机构数(本季首次)", "建仓总市值估算"]
                tn_df['建仓总市值估算'] = tn_df['建仓总市值估算'].apply(format_value)
                st.dataframe(tn_df, use_container_width=True)
            else:
                st.info("本季度无纯新增的共识标的")

        with tab_exit:
            top_exits = global_df[global_df['funds_holding'] == 0].sort_values('exit_count', ascending=False).head(top_n)
            if not top_exits.empty:
                te_df = top_exits[['ticker', 'issuer', 'asset_class', 'exit_count']].copy()
                te_df.columns = ["代码", "原公司名", "原行业", "清仓机构数(彻底退出)"]
                st.dataframe(te_df, use_container_width=True)
            else:
                st.info("本季度无被集体清仓的标的")

        st.markdown("---")
        st.markdown(
            "<div style='text-align:center;color:#9ca3af;font-size:0.8rem;padding:1rem'>"
            "📊 13F 机构持仓分析系统 | 数据来源: SEC EDGAR | 仅供研究参考，不构成投资建议"
            "</div>",
            unsafe_allow_html=True
        )
        return

    # ============================================================
    # 模式: 个股分析 (Cross-Fund)
    # ============================================================
    if analysis_mode == "🔍 个股分析 (Cross-Fund)":
        st.title(f"🔍 个股被持有分析: {search_ticker}")
        st.markdown(f"**统计范围**: 数据库中 {len(funds_df)} 家顶级机构在 **{selected_period}** 会计季度对 `{search_ticker}` 的持仓情况。")
        
        if not search_ticker:
            st.warning("请输入有效的股票代码。")
            return
            
        with st.spinner(f"正在查询 {search_ticker} 的持仓数据..."):
            holders_df = get_stock_holders(search_ticker, selected_period)
            
        if holders_df.empty:
            st.warning(f"由于 {search_ticker} 在 {selected_period} 未被库中任何机构持有，或代码错误。")
            return
            
        # 核心指标
        total_holding_value = holders_df['curr_val'].sum()
        total_holding_shares = holders_df['curr_shares'].sum()
        num_holders = len(holders_df[holders_df['curr_shares'] > 0])
        
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(f'<div class="metric-card"><h3>🏢 持有机构数 (家)</h3><div class="value">{num_holders}</div></div>', unsafe_allow_html=True)
        with c2:
            st.markdown(f'<div class="metric-card"><h3>💰 名义总持有市值</h3><div class="value">{format_value(total_holding_value)}</div></div>', unsafe_allow_html=True)
        with c3:
            st.markdown(f'<div class="metric-card"><h3>📈 名义总持有股数</h3><div class="value">{total_holding_shares:,.0f}</div></div>', unsafe_allow_html=True)
            
        st.markdown("<br>", unsafe_allow_html=True)
        
        # 机构明细表格
        st.subheader("🏦 详细持仓机构列表")
        display_df = holders_df[holders_df['curr_shares'] > 0].copy()
        
        if not display_df.empty:
            # 格式化
            d_df = display_df[['fund_name_cn', 'fund_name', 'curr_val', 'curr_shares', 'curr_pct', 'pct_change', 'shares_change_pct']].copy()
            d_df.columns = ["机构名(中)", "机构名(英)", "持有市值(USD)", "持有股数", "占其组合(%)", "占比比上期同比(pp)", "股数变化(%)"]
            d_df["持有市值(USD)"] = d_df["持有市值(USD)"].apply(format_value)
            d_df["占其组合(%)"] = d_df["占其组合(%)"].apply(lambda x: f"{x:.2f}%")
            d_df["占比比上期同比(pp)"] = d_df["占比比上期同比(pp)"].apply(lambda x: f"{x:+.2f} pp")
            d_df["股数变化(%)"] = d_df["股数变化(%)"].apply(format_pct)
            
            # 使用 st.dataframe 渲染
            st.dataframe(d_df, use_container_width=True)
            
            # 柱状图：谁持仓最多
            st.subheader("📊 持有市值前十名机构")
            fig_bar = px.bar(
                display_df.head(10), x="fund_name_cn", y="curr_val",
                title=f"{search_ticker} 持有市值 Top10 机构",
                labels={"curr_val": "市值 (USD)", "fund_name_cn": "机构名称"},
                color_discrete_sequence=["#3498db"]
            )
            fig_bar.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig_bar, use_container_width=True)
        else:
            st.info(f"所有上期持有 {search_ticker} 的机构都在本期清仓了。")
            
        # 清仓记录
        exits = holders_df[(holders_df['prev_shares'] > 0) & (holders_df['curr_shares'] == 0)]
        if not exits.empty:
            st.subheader("🚪 本期清仓机构")
            e_df = exits[['fund_name_cn', 'fund_name', 'prev_val']].copy()
            e_df.columns = ["机构名(中)", "机构名(英)", "上期持有市值(USD)"]
            e_df["上期持有市值(USD)"] = e_df["上期持有市值(USD)"].apply(format_value)
            st.dataframe(e_df, use_container_width=True)

        st.markdown("---")
        st.markdown(
            "<div style='text-align:center;color:#9ca3af;font-size:0.8rem;padding:1rem'>"
            "📊 13F 机构持仓分析系统 | 数据来源: SEC EDGAR | 仅供研究参考，不构成投资建议"
            "</div>",
            unsafe_allow_html=True
        )
        return

    # ============================================================
    # 模式: 自选基金追踪 (Watchlist) — 增强版
    # ============================================================
    if analysis_mode == "⭐ 自选基金追踪 (Watchlist)":
        st.title("⭐ 自选基金追踪与对比 (Watchlist)")
        
        if not selected_ciks:
            st.info("👈 请在左侧边栏选择您想要合并比对的机构。")
            return
            
        st.markdown(f"**分析范围**: 选中的 {len(selected_ciks)} 家机构在 **{selected_period}** 季度的重叠持仓与调仓动态汇总。")
        
        # ---- 收集所有选中基金的持仓变化数据 ----
        watchlist_changes_list = []
        fund_summaries = []
        for cik, name in zip(selected_ciks, selected_fund_names):
            df_changes = get_changes(cik, selected_period)
            if not df_changes.empty:
                df_changes['fund_name'] = name
                watchlist_changes_list.append(df_changes)
                total_val = df_changes['value'].sum()
                num_holdings = len(df_changes[df_changes['value'] > 0])
                top10_val = df_changes.nlargest(10, 'value')['value'].sum()
                top10_pct = (top10_val / total_val * 100) if total_val > 0 else 0
                fund_summaries.append({
                    '机构': name,
                    '持仓总市值': format_value(total_val),
                    '持仓数量': num_holdings,
                    'Top10集中度': f"{top10_pct:.1f}%",
                    '新买入': len(df_changes[df_changes['prev_pct'] == 0]),
                    '清仓数': len(df_changes[(df_changes['portfolio_pct'] == 0) & (df_changes['prev_pct'] > 0)]),
                })
                
        if not watchlist_changes_list:
            st.warning(f"由于选中基金在 {selected_period} 季度暂未披露数据，无法分析。")
            return
            
        wl_df = pd.concat(watchlist_changes_list, ignore_index=True)
        
        # ========== 板块 1: KPI 仪表盘 ==========
        st.subheader("📊 自选基金 KPI 仪表盘")
        summary_df = pd.DataFrame(fund_summaries)
        st.dataframe(summary_df, use_container_width=True, hide_index=True)
        
        st.markdown("")
        
        # ========== 板块 2: 共识持仓交叉分析 ==========
        st.subheader("🤝 共识持仓交叉分析")
        
        min_overlap = st.slider("至少被 N 家机构共同持有", 1, max(len(selected_ciks), 2), min(2, len(selected_ciks)))
        
        overlap_df = wl_df[wl_df['value'] > 0].groupby(['ticker', 'issuer', 'asset_class']).agg(
            held_by=('fund_name', lambda x: list(set(x))),
            held_count=('fund_name', 'nunique'),
            total_value=('value', 'sum'),
            avg_pct=('portfolio_pct', 'mean'),
        ).reset_index()
        overlap_df = overlap_df[overlap_df['held_count'] >= min_overlap].sort_values(
            by=['held_count', 'total_value'], ascending=[False, False]
        )
        
        if not overlap_df.empty:
            co_df = overlap_df.head(20).copy()
            co_df['held_by_str'] = co_df['held_by'].apply(lambda x: ', '.join(x))
            display_co = co_df[['ticker', 'issuer', 'asset_class', 'held_count', 'total_value', 'avg_pct', 'held_by_str']].copy()
            display_co.columns = ["代码", "公司名", "行业", "共同持有数", "合计市值(USD)", "平均仓位(%)", "持有机构"]
            display_co["合计市值(USD)"] = display_co["合计市值(USD)"].apply(format_value)
            display_co["平均仓位(%)"] = display_co["平均仓位(%)"].apply(lambda x: f"{x:.2f}%")
            st.dataframe(display_co, use_container_width=True, hide_index=True)
        else:
            st.info(f"当前没有被 {min_overlap} 家以上机构共同持有的标的。")
        
        st.markdown("")
        
        # ========== 板块 3: 重大调仓异动追踪 ==========
        st.subheader("🌋 重大调仓异动追踪")
        
        move_tab1, move_tab2, move_tab3, move_tab4 = st.tabs(["📈 加仓 Top", "📉 减仓 Top", "🆕 新买入", "🚪 清仓"])
        
        with move_tab1:
            increases = wl_df[(wl_df['pct_change'] > 0) & (wl_df['prev_pct'] > 0)].sort_values('pct_change', ascending=False).head(15)
            if not increases.empty:
                inc_df = increases[['fund_name', 'ticker', 'issuer', 'pct_change', 'prev_pct', 'portfolio_pct', 'value']].copy()
                inc_df.columns = ["机构", "代码", "公司", "占比变动(pp)", "上期(%)", "本期(%)", "市值(USD)"]
                inc_df["占比变动(pp)"] = inc_df["占比变动(pp)"].apply(lambda x: f"+{x:.2f} pp")
                inc_df["上期(%)"] = inc_df["上期(%)"].apply(lambda x: f"{x:.2f}%")
                inc_df["本期(%)"] = inc_df["本期(%)"].apply(lambda x: f"{x:.2f}%")
                inc_df["市值(USD)"] = inc_df["市值(USD)"].apply(format_value)
                st.dataframe(inc_df, use_container_width=True, hide_index=True)
            else:
                st.info("本期无显著加仓操作。")
                
        with move_tab2:
            decreases = wl_df[(wl_df['pct_change'] < 0) & (wl_df['portfolio_pct'] > 0)].sort_values('pct_change').head(15)
            if not decreases.empty:
                dec_df = decreases[['fund_name', 'ticker', 'issuer', 'pct_change', 'prev_pct', 'portfolio_pct', 'value']].copy()
                dec_df.columns = ["机构", "代码", "公司", "占比变动(pp)", "上期(%)", "本期(%)", "市值(USD)"]
                dec_df["占比变动(pp)"] = dec_df["占比变动(pp)"].apply(lambda x: f"{x:.2f} pp")
                dec_df["上期(%)"] = dec_df["上期(%)"].apply(lambda x: f"{x:.2f}%")
                dec_df["本期(%)"] = dec_df["本期(%)"].apply(lambda x: f"{x:.2f}%")
                dec_df["市值(USD)"] = dec_df["市值(USD)"].apply(format_value)
                st.dataframe(dec_df, use_container_width=True, hide_index=True)
            else:
                st.info("本期无显著减仓操作。")
        
        with move_tab3:
            new_buys = wl_df[(wl_df['prev_pct'] == 0) & (wl_df['portfolio_pct'] > 0)].sort_values('value', ascending=False).head(15)
            if not new_buys.empty:
                nb_df = new_buys[['fund_name', 'ticker', 'issuer', 'asset_class', 'portfolio_pct', 'value']].copy()
                nb_df.columns = ["机构", "代码", "公司", "行业", "仓位(%)", "市值(USD)"]
                nb_df["仓位(%)"] = nb_df["仓位(%)"].apply(lambda x: f"{x:.2f}%")
                nb_df["市值(USD)"] = nb_df["市值(USD)"].apply(format_value)
                st.dataframe(nb_df, use_container_width=True, hide_index=True)
            else:
                st.info("本期无新买入标的。")
                
        with move_tab4:
            exits = wl_df[(wl_df['portfolio_pct'] == 0) & (wl_df['prev_pct'] > 0)]
            if not exits.empty:
                ex_df = exits[['fund_name', 'ticker', 'issuer', 'asset_class', 'prev_pct']].sort_values('prev_pct', ascending=False).head(15).copy()
                ex_df.columns = ["机构", "代码", "公司", "行业", "上期仓位(%)"]
                ex_df["上期仓位(%)"] = ex_df["上期仓位(%)"].apply(lambda x: f"{x:.2f}%")
                st.dataframe(ex_df, use_container_width=True, hide_index=True)
            else:
                st.info("本期无清仓操作。")
        
        st.markdown("")
        
        # ========== 板块 4: 行业配置对比 ==========
        st.subheader("📈 行业配置对比")
        
        sector_data = []
        for fund_name in selected_fund_names:
            fund_df = wl_df[(wl_df['fund_name'] == fund_name) & (wl_df['value'] > 0)]
            if not fund_df.empty:
                sector_alloc = fund_df.groupby('asset_class')['value'].sum().reset_index()
                sector_alloc['fund'] = fund_name
                sector_alloc['pct'] = sector_alloc['value'] / sector_alloc['value'].sum() * 100
                sector_data.append(sector_alloc)
        
        if sector_data:
            sector_all = pd.concat(sector_data, ignore_index=True)
            fig_sector = px.bar(
                sector_all, x='fund', y='pct', color='asset_class',
                title="各机构行业配置占比对比",
                labels={'pct': '配置占比 (%)', 'fund': '机构', 'asset_class': '行业'},
                barmode='stack',
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            fig_sector.update_layout(xaxis_tickangle=-30, height=450)
            st.plotly_chart(fig_sector, use_container_width=True)
        
        st.markdown("---")
        return

    # ============================================================
    # 模式: 单只基金分析 (原逻辑保留)
    # ============================================================
    
    # ---- 获取基金英文名 ----
    fund_row = funds_df[funds_df["cik"] == selected_cik].iloc[0]
    fund_name_en = fund_row["name"]

    # ---- 标题 ----
    st.markdown(f"# {selected_fund_name}")
    st.markdown(f"*{fund_name_en}*")

    # ---- 指标卡片 ----
    total_value = periods_df[periods_df["period"] == selected_period]["total_value"].values
    total_val = total_value[0] if len(total_value) > 0 else 0

    all_holdings = get_all_holdings(selected_cik, selected_period)
    num_holdings = len(all_holdings)
    num_sectors = all_holdings["asset_class"].nunique() if not all_holdings.empty else 0

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(
            f'<div class="metric-card">'
            f'<h3>📅 当前季度</h3>'
            f'<div class="value">{selected_period}</div></div>',
            unsafe_allow_html=True
        )
    with col2:
        st.markdown(
            f'<div class="metric-card metric-card-green">'
            f'<h3>💰 总市值</h3>'
            f'<div class="value">{format_value(total_val)}</div></div>',
            unsafe_allow_html=True
        )
    with col3:
        st.markdown(
            f'<div class="metric-card metric-card-orange">'
            f'<h3>📑 持仓数量</h3>'
            f'<div class="value">{num_holdings:,}</div></div>',
            unsafe_allow_html=True
        )
    with col4:
        st.markdown(
            f'<div class="metric-card metric-card-blue">'
            f'<h3>🏷️ 行业类别</h3>'
            f'<div class="value">{num_sectors}</div></div>',
            unsafe_allow_html=True
        )

    # ---- 特殊季度备注 ----
    # 伯克希尔哈撒韦 2025-Q2 特殊情况说明
    BERKSHIRE_CIK = "0001067983"
    if selected_cik == BERKSHIRE_CIK and selected_period == "2025-Q2":
        st.warning(
            "⚠️ **数据说明：伯克希尔哈撒韦 2025-Q2 持仓变化数据存在偏差。**\n\n"
            "原因：伯克希尔在 2025-Q1（2025年3月末）向 SEC 提交的 13F 报告仅包含子账户部分，"
            "总申报市值约 **$1.1B**（正常约 $267B），主要持仓未完整披露。\n\n"
            "因此与 2024-Q4 相比，本季度约 **37 只持仓** 被系统误标为 🆕 New（实为长期持有）。"
            "2025-Q3 及之后数据恢复正常。"
        )

    st.markdown("")


    # ---- 图表区域 ----
    chart_col, pie_col = st.columns([3, 2])

    with chart_col:
        st.markdown("### 📊 持仓组合历史分布")
        comp_df = get_composition_history(selected_cik)
        if not comp_df.empty:
            # 确保 period 按时间顺序排列
            sorted_periods = sorted(comp_df["period"].unique())
            fig = px.bar(
                comp_df, x="period", y="pct", color="asset_class",
                color_discrete_map=SECTOR_COLORS,
                category_orders={"period": sorted_periods},
                labels={"pct": "占比 (%)", "period": "季度", "asset_class": "资产类别"},
                height=420,
            )
            fig.update_layout(
                barmode="stack",
                yaxis=dict(range=[0, 100], ticksuffix="%"),
                legend=dict(
                    orientation="h", yanchor="top", y=-0.18,
                    xanchor="center", x=0.5, font=dict(size=10)
                ),
                margin=dict(l=40, r=20, t=20, b=80),
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
            )
            fig.update_xaxes(showgrid=False)
            fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor="#f0f0f0")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("暂无历史数据")

    with pie_col:
        st.markdown(f"### 🥧 {selected_period} 资产分布")
        if not comp_df.empty:
            period_comp = comp_df[comp_df["period"] == selected_period].copy()
            if not period_comp.empty:
                # 合并小类别
                threshold = 2.0
                period_comp["display_class"] = period_comp["asset_class"].where(
                    period_comp["pct"] >= threshold, "其他"
                )
                grouped = period_comp.groupby("display_class")["pct"].sum().reset_index()
                grouped = grouped.sort_values("pct", ascending=False)

                fig_pie = px.pie(
                    grouped, values="pct", names="display_class",
                    color="display_class",
                    color_discrete_map=SECTOR_COLORS,
                    height=380,
                )
                fig_pie.update_traces(
                    textposition="inside", textinfo="label+percent",
                    textfont_size=11,
                    hole=0.35,
                )
                fig_pie.update_layout(
                    showlegend=False,
                    margin=dict(l=10, r=10, t=20, b=20),
                    paper_bgcolor="rgba(0,0,0,0)",
                )
                st.plotly_chart(fig_pie, use_container_width=True)
            else:
                st.info("该季度暂无数据")

    # ---- 持仓表格 ----
    st.markdown("---")
    st.markdown(f"### 📋 Top {top_n} 持仓部位 — {selected_period}")

    holdings_df = get_holdings(selected_cik, selected_period, limit=top_n)
    if not holdings_df.empty:
        display_df = holdings_df.copy()
        display_df.index = range(1, len(display_df) + 1)
        display_df.index.name = "#"

        # 格式化显示列
        display_df["股号"] = display_df.apply(
            lambda r: r["ticker"] if r["ticker"] else r["cusip"], axis=1
        )
        display_df["市值"] = display_df["value"].apply(format_value)
        display_df["投组占比"] = display_df["portfolio_pct"].apply(lambda x: f"{x:.2f}%")
        display_df["占比变化"] = display_df["pct_change"].apply(format_pct)

        def fmt_shares_change(row):
            val = row["shares_change_pct"]
            prev = row["prev_pct"]
            if pd.isna(prev) and val == 0:
                return "-"
            if val >= 100 and prev == 0:
                return "🆕 New"
            if val <= -99:
                return "🚪 Exit"
            if val != 0:
                return format_pct(val)
            return "0%"

        display_df["持仓变化"] = display_df.apply(fmt_shares_change, axis=1)

        # 选择展示列
        show_cols = ["issuer", "股号", "asset_class", "市值", "投组占比", "占比变化", "持仓变化"]
        result_df = display_df[show_cols].rename(columns={
            "issuer": "资产全名",
            "asset_class": "行业类别",
        })

        # 持仓变化列颜色标记
        def _color_change_cell(val):
            v = str(val)
            if "New" in v:
                return "color: #0984e3; font-weight: 700"  # 蓝色-新买入
            if "Exit" in v:
                return "color: #636e72; font-weight: 700"  # 灰色-清仓
            if v.startswith("+"):
                return "color: #00b894; font-weight: 700"  # 绿色-增持
            if v.startswith("-"):
                return "color: #e17055; font-weight: 700"  # 红色-减持
            return ""

        styled = result_df.style.applymap(_color_change_cell, subset=["持仓变化"])
        st.dataframe(
            styled,
            use_container_width=True,
            height=min(len(result_df) * 38 + 40, 700),
        )
    else:
        st.info("该季度暂无持仓数据")

    # ---- 持仓变化区域 ----
    st.markdown("---")
    st.markdown(f"### 📈 季度持仓变化 — {selected_period}")

    changes_df = get_changes(selected_cik, selected_period)
    if not changes_df.empty:
        tab_top_inc, tab_top_dec, tab_inc, tab_dec, tab_new, tab_exit = st.tabs([
            "⬆️ Top 增仓", "⬇️ Top 减仓", "📈 增持(QoQ)", "📉 减持(QoQ)", "🆕 新买入", "🚪 清仓"
        ])

        # ---- Top 增仓（按投组占比变化 pct_change 排序）----
        with tab_top_inc:
            top_inc = changes_df[changes_df["pct_change"] > 0].copy()
            top_inc = top_inc[top_inc["prev_pct"] > 0]  # 排除新买入
            top_inc = top_inc.sort_values("pct_change", ascending=False).head(top_n)
            if not top_inc.empty:
                fig_top_inc = px.bar(
                    top_inc, x="issuer", y="pct_change",
                    color_discrete_sequence=["#00b894"],
                    labels={"pct_change": "占比变化 (百分点)", "issuer": ""},
                    height=380,
                )
                fig_top_inc.update_layout(
                    showlegend=False,
                    margin=dict(l=40, r=20, t=20, b=120),
                    plot_bgcolor="rgba(0,0,0,0)",
                    paper_bgcolor="rgba(0,0,0,0)",
                    yaxis=dict(ticksuffix=" pp"),
                )
                fig_top_inc.update_xaxes(tickangle=45)
                st.plotly_chart(fig_top_inc, use_container_width=True)
                # 辅助表格
                ti_display = top_inc[["issuer", "asset_class", "portfolio_pct", "prev_pct", "pct_change", "value"]].copy()
                ti_display.index = range(1, len(ti_display) + 1)
                ti_display["value"] = ti_display["value"].apply(format_value)
                ti_display["portfolio_pct"] = ti_display["portfolio_pct"].apply(lambda x: f"{x:.2f}%")
                ti_display["prev_pct"] = ti_display["prev_pct"].apply(lambda x: f"{x:.2f}%")
                ti_display["pct_change"] = ti_display["pct_change"].apply(lambda x: f"+{x:.2f} pp")
                ti_display.columns = ["资产名称", "行业", "当期占比", "上期占比", "变化(pp)", "市值"]
                st.dataframe(ti_display, use_container_width=True)
            else:
                st.info("该季度无占比增加记录")

        # ---- Top 减仓（按投组占比变化 pct_change 排序）----
        with tab_top_dec:
            top_dec = changes_df[changes_df["pct_change"] < 0].copy()
            top_dec = top_dec[top_dec["prev_pct"] > 0]  # 排除清仓
            top_dec = top_dec.sort_values("pct_change", ascending=True).head(top_n)
            if not top_dec.empty:
                fig_top_dec = px.bar(
                    top_dec, x="issuer", y="pct_change",
                    color_discrete_sequence=["#e17055"],
                    labels={"pct_change": "占比变化 (百分点)", "issuer": ""},
                    height=380,
                )
                fig_top_dec.update_layout(
                    showlegend=False,
                    margin=dict(l=40, r=20, t=20, b=120),
                    plot_bgcolor="rgba(0,0,0,0)",
                    paper_bgcolor="rgba(0,0,0,0)",
                    yaxis=dict(ticksuffix=" pp"),
                )
                fig_top_dec.update_xaxes(tickangle=45)
                st.plotly_chart(fig_top_dec, use_container_width=True)
                # 辅助表格
                td_display = top_dec[["issuer", "asset_class", "portfolio_pct", "prev_pct", "pct_change", "value"]].copy()
                td_display.index = range(1, len(td_display) + 1)
                td_display["value"] = td_display["value"].apply(format_value)
                td_display["portfolio_pct"] = td_display["portfolio_pct"].apply(lambda x: f"{x:.2f}%")
                td_display["prev_pct"] = td_display["prev_pct"].apply(lambda x: f"{x:.2f}%")
                td_display["pct_change"] = td_display["pct_change"].apply(lambda x: f"{x:.2f} pp")
                td_display.columns = ["资产名称", "行业", "当期占比", "上期占比", "变化(pp)", "市值"]
                st.dataframe(td_display, use_container_width=True)
            else:
                st.info("该季度无占比减少记录")

        with tab_inc:
            inc = changes_df[changes_df["shares_change_pct"] > 0].copy()
            inc = inc[inc["prev_pct"] > 0]  # 排除新买入
            inc = inc.sort_values("shares_change_pct", ascending=False).head(15)
            if not inc.empty:
                fig_inc = px.bar(
                    inc, x="issuer", y="shares_change_pct",
                    color_discrete_sequence=["#00b894"],  # 统一绿色
                    labels={"shares_change_pct": "持仓增幅 (%)", "issuer": ""},
                    height=350,
                )
                fig_inc.update_layout(
                    showlegend=False,
                    margin=dict(l=40, r=20, t=20, b=100),
                    plot_bgcolor="rgba(0,0,0,0)",
                    paper_bgcolor="rgba(0,0,0,0)",
                )
                fig_inc.update_xaxes(tickangle=45)
                st.plotly_chart(fig_inc, use_container_width=True)
            else:
                st.info("该季度无增持记录")

        with tab_dec:
            dec = changes_df[changes_df["shares_change_pct"] < 0].copy()
            dec = dec[dec["shares_change_pct"] > -99]  # 排除清仓
            dec = dec.sort_values("shares_change_pct", ascending=True).head(15)
            if not dec.empty:
                fig_dec = px.bar(
                    dec, x="issuer", y="shares_change_pct",
                    color_discrete_sequence=["#e17055"],  # 统一红色
                    labels={"shares_change_pct": "持仓减幅 (%)", "issuer": ""},
                    height=350,
                )
                fig_dec.update_layout(
                    showlegend=False,
                    margin=dict(l=40, r=20, t=20, b=100),
                    plot_bgcolor="rgba(0,0,0,0)",
                    paper_bgcolor="rgba(0,0,0,0)",
                )
                fig_dec.update_xaxes(tickangle=45)
                st.plotly_chart(fig_dec, use_container_width=True)
            else:
                st.info("该季度无减持记录")

        with tab_new:
            new_pos = changes_df[
                (changes_df["shares_change_pct"] >= 100) &
                (changes_df["prev_pct"] == 0)
            ].copy()
            new_pos = new_pos.sort_values("value", ascending=False).head(15)
            if not new_pos.empty:
                new_display = new_pos[["issuer", "asset_class", "value", "portfolio_pct"]].copy()
                new_display.index = range(1, len(new_display) + 1)
                new_display["value"] = new_display["value"].apply(format_value)
                new_display["portfolio_pct"] = new_display["portfolio_pct"].apply(lambda x: f"{x:.2f}%")
                new_display.columns = ["资产全名", "行业", "市值", "占比"]
                st.dataframe(new_display, use_container_width=True)
            else:
                st.info("该季度无新买入")

        with tab_exit:
            exit_pos = changes_df[changes_df["shares_change_pct"] <= -99].copy()
            exit_pos = exit_pos.sort_values("value", ascending=False).head(15)
            if not exit_pos.empty:
                exit_display = exit_pos[["issuer", "asset_class", "value", "portfolio_pct"]].copy()
                exit_display.index = range(1, len(exit_display) + 1)
                exit_display["value"] = exit_display["value"].apply(format_value)
                exit_display["portfolio_pct"] = exit_display["portfolio_pct"].apply(lambda x: f"{x:.2f}%")
                exit_display.columns = ["资产全名", "行业", "市值", "占比"]
                st.dataframe(exit_display, use_container_width=True)
            else:
                st.info("该季度无清仓")
    else:
        st.info("暂无变化数据")

    # ---- 页脚 ----
    st.markdown("---")
    st.markdown(
        "<div style='text-align:center;color:#9ca3af;font-size:0.8rem;padding:1rem'>"
        "📊 13F 机构持仓分析系统 | 数据来源: SEC EDGAR | 仅供研究参考，不构成投资建议"
        "</div>",
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
