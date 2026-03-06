# -*- coding: utf-8 -*-
"""
13F 机构持仓分析系统 - Streamlit 版
数据来源: Dataroma (Superinvestors)
"""

import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from backend.data_access import (
    get_fund_list, get_holdings, get_periods, get_changes,
    get_global_latest_period, get_global_changes, get_stock_holders
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
    .main .block-container { padding-top: 1rem; max-width: 1200px; }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 12px; padding: 1.2rem; color: white;
        text-align: center; box-shadow: 0 4px 15px rgba(102,126,234,0.3);
    }
    .metric-card h3 { margin: 0; font-size: 0.85rem; opacity: 0.9; font-weight: 400; }
    .metric-card .value { font-size: 1.6rem; font-weight: 700; margin-top: 0.3rem; }
    .metric-card-green {
        background: linear-gradient(135deg, #00b894 0%, #00cec9 100%);
        box-shadow: 0 4px 15px rgba(0,184,148,0.3);
    }
    .metric-card-orange {
        background: linear-gradient(135deg, #fdcb6e 0%, #e17055 100%);
        box-shadow: 0 4px 15px rgba(253,203,110,0.3);
    }
    .metric-card-blue {
        background: linear-gradient(135deg, #0984e3 0%, #6c5ce7 100%);
        box-shadow: 0 4px 15px rgba(9,132,227,0.3);
    }
    div[data-testid="stMetric"] {
        background: #f8fafc; border-radius: 8px;
        padding: 12px; border: 1px solid #e8ecef;
    }
    .dataframe { font-size: 0.85rem !important; }
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
# 工具函数
# ============================================================
def format_value(val):
    if pd.isna(val) or val == 0:
        return "$0"
    sign = "-" if val < 0 else ""
    abs_val = abs(val)
    if abs_val >= 1_000_000_000:
        return f"{sign}${abs_val/1e9:,.2f}B"
    if abs_val >= 1_000_000:
        return f"{sign}${abs_val/1e6:,.2f}M"
    if abs_val >= 1_000:
        return f"{sign}${abs_val/1e3:,.2f}K"
    return f"{sign}${abs_val:,.0f}"


def format_pct(val):
    if pd.isna(val):
        return "-"
    sign = "+" if val > 0 else ""
    return f"{sign}{val:.2f}%"


# ============================================================
# 主应用
# ============================================================
def main():
    funds_df = get_fund_list()
    if funds_df.empty:
        st.error("⚠️ 暂无数据。请先运行 `python backend/scraper.py` 采集数据。")
        return

    # ---- 侧边栏 ----
    with st.sidebar:
        st.markdown("## 📊 13F 持仓分析")
        st.markdown("---")

        analysis_mode = st.radio(
            "🔎 选择分析模式",
            ["单只基金分析", "🌍 全局宏观动态", "🔍 个股分析", "⭐ 自选基金追踪"],
            index=0
        )
        st.markdown("---")

        if analysis_mode == "单只基金分析":
            fund_options = {row["name_cn"]: row["fund_id"] for _, row in funds_df.iterrows()}
            selected_name = st.selectbox("🏛️ 选择基金", list(fund_options.keys()))
            selected_fid = fund_options[selected_name]

            period_list = get_periods(selected_fid)
            if not period_list:
                st.warning("该基金暂无数据")
                return
            selected_period = st.selectbox("📅 选择季度", period_list)

        elif analysis_mode == "🌍 全局宏观动态":
            selected_period = get_global_latest_period()
            if not selected_period:
                st.warning("暂无数据")
                return
            st.info(f"统计季度: **{selected_period}**")

        elif analysis_mode == "🔍 个股分析":
            selected_period = get_global_latest_period()
            if not selected_period:
                st.warning("暂无数据")
                return
            search_ticker = st.text_input("🔍 输入股票代码 (如 AAPL)", value="AAPL").upper().strip()
            st.info(f"查询季度: **{selected_period}**")

        elif analysis_mode == "⭐ 自选基金追踪":
            selected_period = get_global_latest_period()
            if not selected_period:
                st.warning("暂无数据")
                return
            fund_options = {row["name_cn"]: row["fund_id"] for _, row in funds_df.iterrows()}
            saved_wl = st.query_params.get("wl", "")
            saved_ids = [c.strip() for c in saved_wl.split(",") if c.strip()] if saved_wl else []
            id_to_name = {row["fund_id"]: row["name_cn"] for _, row in funds_df.iterrows()}
            default_names = [id_to_name[c] for c in saved_ids if c in id_to_name]

            st.info("💡 选择会保存到网址中，刷新或分享链接可恢复。")
            selected_fund_names = st.multiselect("⭐ 选择关注基金", list(fund_options.keys()), default=default_names)
            selected_fids = [fund_options[n] for n in selected_fund_names]
            if selected_fids:
                st.query_params["wl"] = ",".join(selected_fids)
            elif "wl" in st.query_params:
                del st.query_params["wl"]

        st.markdown("---")
        if analysis_mode not in ["🔍 个股分析", "⭐ 自选基金追踪"]:
            top_n = st.slider("📋 显示 Top N", 5, 50, 20)
        st.markdown(
            "<div style='color:#9ca3af;font-size:0.75rem;text-align:center'>"
            "数据来源: Dataroma<br>Superinvestor 13F 持仓</div>",
            unsafe_allow_html=True
        )

    # ============================================================
    # 单只基金分析
    # ============================================================
    if analysis_mode == "单只基金分析":
        fund_row = funds_df[funds_df["fund_id"] == selected_fid].iloc[0]
        holdings = get_holdings(selected_fid, selected_period)
        changes = get_changes(selected_fid, selected_period)

        st.markdown(f"# {selected_name}")
        st.markdown(f"*{fund_row['name']}*")
        st.markdown("<br>", unsafe_allow_html=True)

        # 指标卡片
        total_val = fund_row.get("portfolio_value", 0)
        if pd.isna(total_val):
            total_val = holdings["value"].sum() if not holdings.empty else 0
        num_holdings = len(holdings)
        num_periods = len(get_periods(selected_fid))

        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown(f'<div class="metric-card"><h3>📅 当前季度</h3>'
                        f'<div class="value">{selected_period}</div></div>', unsafe_allow_html=True)
        with c2:
            st.markdown(f'<div class="metric-card metric-card-green"><h3>💰 总市值</h3>'
                        f'<div class="value">{format_value(total_val)}</div></div>', unsafe_allow_html=True)
        with c3:
            st.markdown(f'<div class="metric-card metric-card-orange"><h3>📑 持仓数量</h3>'
                        f'<div class="value">{num_holdings:,}</div></div>', unsafe_allow_html=True)
        with c4:
            st.markdown(f'<div class="metric-card metric-card-blue"><h3>📈 历史季度</h3>'
                        f'<div class="value">{num_periods}</div></div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Tab 视图
        tab_top, tab_changes, tab_chart = st.tabs(["📋 Top 持仓", "📈 持仓变化", "📊 图表"])

        with tab_top:
            if not holdings.empty:
                display = holdings.head(top_n).copy()
                display["value"] = display["value"].apply(format_value)
                display["portfolio_pct"] = display["portfolio_pct"].apply(lambda x: f"{x:.2f}%")
                display["shares"] = display["shares"].apply(lambda x: f"{x:,}")
                cols_map = {"ticker": "代码", "issuer": "公司", "portfolio_pct": "占比(%)",
                            "shares": "持股数", "value": "市值", "activity": "近期操作"}
                st.dataframe(display.rename(columns=cols_map)[list(cols_map.values())],
                             use_container_width=True, hide_index=True)

        with tab_changes:
            if not changes.empty and "pct_change" in changes.columns:
                ch = changes[changes["pct_change"].abs() > 0.01].copy()
                ch = ch.sort_values("pct_change", ascending=False)
                ch_display = ch[["ticker", "issuer", "portfolio_pct", "prev_pct", "pct_change", "activity"]].copy()
                ch_display["portfolio_pct"] = ch_display["portfolio_pct"].apply(lambda x: f"{x:.2f}%")
                ch_display["prev_pct"] = ch_display["prev_pct"].apply(lambda x: f"{x:.2f}%")
                ch_display["pct_change"] = ch_display["pct_change"].apply(lambda x: f"{x:+.2f} pp")
                ch_display.columns = ["代码", "公司", "本期(%)", "上期(%)", "变化(pp)", "操作"]
                st.dataframe(ch_display, use_container_width=True, hide_index=True)
            else:
                st.info("暂无变化数据（可能缺少上一季度数据）")

        with tab_chart:
            if not holdings.empty:
                chart_data = holdings.head(15).copy()
                fig = px.bar(
                    chart_data, x="ticker", y="portfolio_pct",
                    title=f"Top 15 持仓占比",
                    labels={"portfolio_pct": "占比(%)", "ticker": "股票代码"},
                    color="portfolio_pct",
                    color_continuous_scale="Blues",
                )
                fig.update_layout(showlegend=False)
                st.plotly_chart(fig, use_container_width=True)

                # 饼图
                fig_pie = px.pie(
                    chart_data, values="portfolio_pct", names="ticker",
                    title="持仓占比分布",
                    color_discrete_sequence=px.colors.qualitative.Set3,
                )
                st.plotly_chart(fig_pie, use_container_width=True)

        # 历史季度趋势
        all_periods = get_periods(selected_fid)
        if len(all_periods) > 1:
            st.subheader("📈 历史持仓数量趋势")
            trend_data = []
            for p in sorted(all_periods):
                h = get_holdings(selected_fid, p)
                trend_data.append({"period": p, "num_holdings": len(h)})
            trend_df = pd.DataFrame(trend_data)
            fig_trend = px.line(trend_df, x="period", y="num_holdings",
                                title="各季度持仓数量", markers=True)
            st.plotly_chart(fig_trend, use_container_width=True)

    # ============================================================
    # 全局宏观动态
    # ============================================================
    elif analysis_mode == "🌍 全局宏观动态":
        st.title("🌍 13F 全局宏观动态")
        st.markdown(f"**统计范围**: {len(funds_df)} 家超级投资人在 {selected_period} 季度的调仓动向。")

        with st.spinner("正在计算全市场数据..."):
            global_df = get_global_changes(selected_period)

        if global_df.empty:
            st.warning(f"无法获取 {selected_period} 的数据。")
            return

        total_stocks = len(global_df)
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f'<div class="metric-card"><h3>🏢 覆盖标的数</h3>'
                        f'<div class="value">{total_stocks}</div></div>', unsafe_allow_html=True)
        with c2:
            avg_holders = global_df["funds_holding"].mean()
            st.markdown(f'<div class="metric-card metric-card-green"><h3>📊 平均持有机构数</h3>'
                        f'<div class="value">{avg_holders:.1f}</div></div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        tab_pop, tab_buy, tab_sell = st.tabs(["🔥 最多机构持有", "📈 最多加仓", "📉 最多减仓"])

        with tab_pop:
            top_pop = global_df.nlargest(top_n, "funds_holding")
            fig = px.bar(top_pop, x="ticker", y="funds_holding",
                         title=f"Top {top_n} 被最多机构持有", hover_data=["issuer"],
                         color="funds_holding", color_continuous_scale="Viridis")
            st.plotly_chart(fig, use_container_width=True)
            display = top_pop[["ticker", "issuer", "funds_holding", "total_curr_val"]].copy()
            display.columns = ["代码", "公司", "持有机构数", "合计市值"]
            display["合计市值"] = display["合计市值"].apply(format_value)
            st.dataframe(display, use_container_width=True, hide_index=True)

        with tab_buy:
            top_buys = global_df.nlargest(top_n, "inc_count")
            fig = px.bar(top_buys, x="ticker", y="inc_count",
                         title=f"Top {top_n} 被最多机构加仓", hover_data=["issuer"],
                         color="inc_count", color_continuous_scale="Greens")
            st.plotly_chart(fig, use_container_width=True)

        with tab_sell:
            top_sells = global_df.nlargest(top_n, "dec_count")
            fig = px.bar(top_sells, x="ticker", y="dec_count",
                         title=f"Top {top_n} 被最多机构减仓", hover_data=["issuer"],
                         color="dec_count", color_continuous_scale="Reds")
            st.plotly_chart(fig, use_container_width=True)

    # ============================================================
    # 个股分析
    # ============================================================
    elif analysis_mode == "🔍 个股分析":
        st.title(f"🔍 个股分析: {search_ticker}")

        if not search_ticker:
            st.warning("请输入股票代码。")
            return

        with st.spinner(f"正在查询 {search_ticker}..."):
            holders_df = get_stock_holders(search_ticker, selected_period)

        if holders_df.empty:
            st.warning(f"{search_ticker} 在 {selected_period} 未被任何机构持有。")
            return

        num_holders = len(holders_df[holders_df["curr_shares"] > 0])
        total_val = holders_df["curr_val"].sum()

        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f'<div class="metric-card"><h3>🏢 持有机构数</h3>'
                        f'<div class="value">{num_holders}</div></div>', unsafe_allow_html=True)
        with c2:
            st.markdown(f'<div class="metric-card metric-card-green"><h3>💰 总持有市值</h3>'
                        f'<div class="value">{format_value(total_val)}</div></div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # 详细表格
        st.subheader("🏦 持仓机构列表")
        display = holders_df[holders_df["curr_shares"] > 0].copy()
        if not display.empty:
            d = display[["fund_name_cn", "curr_val", "curr_shares", "curr_pct",
                          "pct_change", "shares_change_pct"]].copy()
            d.columns = ["机构", "持有市值", "持股数", "占组合(%)", "占比变动(pp)", "股数变化(%)"]
            d["持有市值"] = d["持有市值"].apply(format_value)
            d["占组合(%)"] = d["占组合(%)"].apply(lambda x: f"{x:.2f}%")
            d["占比变动(pp)"] = d["占比变动(pp)"].apply(lambda x: f"{x:+.2f}")
            d["股数变化(%)"] = d["股数变化(%)"].apply(format_pct)
            st.dataframe(d, use_container_width=True, hide_index=True)

            # 柱状图
            fig = px.bar(display.head(10), x="fund_name_cn", y="curr_val",
                         title=f"{search_ticker} 持有市值 Top 10",
                         labels={"curr_val": "市值", "fund_name_cn": "机构"},
                         color_discrete_sequence=["#3498db"])
            fig.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)

    # ============================================================
    # 自选基金追踪
    # ============================================================
    elif analysis_mode == "⭐ 自选基金追踪":
        st.title("⭐ 自选基金追踪")

        if not selected_fids:
            st.info("👈 请在左侧选择您想追踪的机构。")
            return

        st.markdown(f"**分析范围**: {len(selected_fids)} 家机构在 **{selected_period}** 的持仓对比。")

        # 收集数据
        wl_data = []
        fund_summaries = []
        for fid, name in zip(selected_fids, selected_fund_names):
            changes = get_changes(fid, selected_period)
            if changes.empty:
                continue
            changes["fund_name"] = name
            wl_data.append(changes)

            total_val = changes["value"].sum()
            fund_summaries.append({
                "机构": name,
                "持仓总市值": format_value(total_val),
                "持仓数量": len(changes[changes["value"] > 0]),
                "新买入": len(changes[changes["prev_pct"] == 0]) if "prev_pct" in changes.columns else 0,
            })

        if not wl_data:
            st.warning("选中基金暂无数据。")
            return

        # KPI 仪表盘
        st.subheader("📊 基金 KPI")
        st.dataframe(pd.DataFrame(fund_summaries), use_container_width=True, hide_index=True)

        # 共识持仓
        wl_df = pd.concat(wl_data, ignore_index=True)
        st.subheader("🤝 共识持仓")
        min_overlap = st.slider("至少被 N 家机构持有", 1, max(len(selected_fids), 2),
                                 min(2, len(selected_fids)))

        overlap = wl_df[wl_df["value"] > 0].groupby(["ticker", "issuer"]).agg(
            held_by=("fund_name", lambda x: list(set(x))),
            held_count=("fund_name", "nunique"),
            total_value=("value", "sum"),
            avg_pct=("portfolio_pct", "mean"),
        ).reset_index()
        overlap = overlap[overlap["held_count"] >= min_overlap].sort_values(
            ["held_count", "total_value"], ascending=[False, False])

        if not overlap.empty:
            co = overlap.head(20).copy()
            co["持有机构"] = co["held_by"].apply(lambda x: ", ".join(x))
            co["合计市值"] = co["total_value"].apply(format_value)
            co["平均仓位"] = co["avg_pct"].apply(lambda x: f"{x:.2f}%")
            display = co[["ticker", "issuer", "held_count", "合计市值", "平均仓位", "持有机构"]]
            display.columns = ["代码", "公司", "共持数", "合计市值", "平均仓位", "持有机构"]
            st.dataframe(display, use_container_width=True, hide_index=True)
        else:
            st.info(f"没有被 {min_overlap} 家以上机构共同持有的标的。")

    # 页脚
    st.markdown("---")
    st.markdown(
        "<div style='text-align:center;color:#9ca3af;font-size:0.8rem;padding:1rem'>"
        "📊 13F 机构持仓分析系统 | 数据来源: Dataroma | 仅供研究参考</div>",
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
else:
    main()
