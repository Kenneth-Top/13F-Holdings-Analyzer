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

# ============================================================
# 路径设置
# ============================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "data", "holdings.db")

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
        "SELECT period, total_value FROM filings WHERE fund_cik = ? ORDER BY period_date DESC",
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
           ORDER BY f.period_date ASC""",
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
    """格式化市值 (千美元 -> 可读格式)"""
    if pd.isna(val) or val == 0:
        return "$0"
    billion = val / 1_000_000
    if billion >= 1:
        return f"${billion:,.2f}B"
    million = val / 1_000
    return f"${million:,.2f}M"


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
    "股票": "#2ecc71",
    "股票-科技": "#3498db",
    "股票-金融": "#f39c12",
    "股票-医疗保健": "#9b59b6",
    "股票-能源": "#e74c3c",
    "股票-必需消费": "#1abc9c",
    "股票-非必需消费": "#e67e22",
    "股票-工业": "#95a5a6",
    "股票-通讯服务": "#8e44ad",
    "股票-原材料": "#d35400",
    "股票-公用事业": "#27ae60",
    "股票-房地产": "#c0392b",
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
    "期权-看涨": "#fdcb6e",
    "期权-看跌": "#e17055",
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

        st.markdown("---")
        top_n = st.slider("📋 显示前 N 个持仓", 5, 50, 20)

        st.markdown("---")
        st.markdown(
            "<div style='color:#9ca3af;font-size:0.75rem;text-align:center'>"
            "数据来源: SEC EDGAR<br>13F 季度报告</div>",
            unsafe_allow_html=True
        )

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

    st.markdown("")

    # ---- 图表区域 ----
    chart_col, pie_col = st.columns([3, 2])

    with chart_col:
        st.markdown("### 📊 持仓组合历史分布")
        comp_df = get_composition_history(selected_cik)
        if not comp_df.empty:
            fig = px.bar(
                comp_df, x="period", y="pct", color="asset_class",
                color_discrete_map=SECTOR_COLORS,
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

        # 使用 st.dataframe 显示（支持排序和搜索）
        st.dataframe(
            result_df,
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
        tab_inc, tab_dec, tab_new, tab_exit = st.tabs([
            "📈 增持", "📉 减持", "🆕 新买入", "🚪 清仓"
        ])

        with tab_inc:
            inc = changes_df[changes_df["shares_change_pct"] > 0].copy()
            inc = inc[inc["prev_pct"] > 0]  # 排除新买入
            inc = inc.sort_values("shares_change_pct", ascending=False).head(15)
            if not inc.empty:
                fig_inc = px.bar(
                    inc, x="issuer", y="shares_change_pct",
                    color="asset_class", color_discrete_map=SECTOR_COLORS,
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
                    color="asset_class", color_discrete_map=SECTOR_COLORS,
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
