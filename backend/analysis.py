import pandas as pd

def calc_hhi(holdings_df):
    """
    计算持仓集中度 (Herfindahl-Hirschman Index, HHI)
    HHI = sum( (portfolio_pct)^2 )
    
    Args:
        holdings_df: 包含 'portfolio_pct' 列的 DataFrame (百分比, 例如 5.5 = 5.5%)
        
    Returns:
        float: HHI 值 (范围通常在 0 到 10000 之间)
    """
    if holdings_df is None or holdings_df.empty or 'portfolio_pct' not in holdings_df.columns:
        return 0.0
    
    # 将 NaN 或 非数值转为 0
    pcts = pd.to_numeric(holdings_df['portfolio_pct'], errors='coerce').fillna(0)
    
    # 计算平方和
    hhi = (pcts ** 2).sum()
    
    return round(hhi, 2)


def get_fund_style_tags(fund_cik, current_holdings, composition_history):
    """
    计算并生成基金风格标签
    
    Args:
        fund_cik: 基金标识
        current_holdings: 最新一季度的持仓 DataFrame
        composition_history: 从 database.get_composition_history() 获得的 DataFrame
        
    Returns:
        list of str: 风格标签数组，例如 ["重仓出击", "科技主导"]
    """
    tags = []
    
    if current_holdings is None or current_holdings.empty:
        return tags
        
    # 1. 集中度标签
    hhi = calc_hhi(current_holdings)
    stock_count = len(current_holdings)
    
    if hhi > 2000 or (stock_count < 20 and hhi > 1000):
        tags.append("🎯 高度集中 (重仓出击)")
    elif hhi < 150 and stock_count > 200:
        tags.append("🌐 极度分散 (量化风范)")
    elif hhi < 300 and stock_count > 100:
        tags.append("📊 广泛持股 (分散避风)")
        
    # 2. 行业偏好标签
    if composition_history is not None and not composition_history.empty:
        # 提取最新季度的资产分布
        latest_period = composition_history['period'].max()
        latest_comp = composition_history[composition_history['period'] == latest_period].copy()
        
        # 按类型排除 ETF 和 期权，聚焦个股偏好
        # 假设含有 'ETF' 或 '期权' 字样
        stock_comp = latest_comp[~latest_comp['asset_class'].str.contains('ETF|期权|债券', na=False, case=False)]
        
        if not stock_comp.empty and stock_comp['total_value'].iloc[0] > 0:
            stock_comp['pct'] = stock_comp['class_value'] / stock_comp['total_value'] * 100
            
            # 如果某个行业超过了阈值，如 30%
            top_sector = stock_comp.loc[stock_comp['pct'].idxmax()]
            top_sector_name = top_sector['asset_class']
            top_sector_pct = top_sector['pct']
            
            if top_sector_pct > 35:
                # 特定行业的专属称呼
                if '科技' in top_sector_name:
                    tags.append("💻 科技偏好")
                elif '医疗' in top_sector_name:
                    tags.append("🏥 医疗偏好")
                elif '金融' in top_sector_name:
                    tags.append("🏦 金融偏好")
                elif '能源' in top_sector_name:
                    tags.append("🛢️ 能源偏好")
                elif '消费' in top_sector_name:
                    tags.append("🛍️ 消费偏好")
                else:
                    tags.append(f"⭐ {top_sector_name}主力")

    return tags
