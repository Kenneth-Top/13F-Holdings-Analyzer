/**
 * 13F 机构持仓分析系统 - 前端逻辑
 */

// ============================================================
// 全局状态
// ============================================================
const API_BASE = '';  // 同源请求
let currentCik = '';
let currentPeriod = '';
let chartInstance = null;

// ECharts 配色方案 (对应不同资产类别)
const ASSET_COLORS = {
    '股票': '#00b894',
    'ETF': '#0984e3',
    '期权-看涨': '#fdcb6e',
    '期权-看跌': '#e17055',
    '债券': '#6c5ce7',
    '可转债': '#00cec9',
    '权证': '#e84393',
    '其他': '#b2bec3',
};

const COLOR_PALETTE = [
    '#00b894', '#0984e3', '#fdcb6e', '#e17055', '#6c5ce7',
    '#00cec9', '#e84393', '#b2bec3', '#fab1a0', '#55efc4',
    '#74b9ff', '#a29bfe', '#ffeaa7', '#dfe6e9', '#fd79a8',
];

// ============================================================
// 工具函数
// ============================================================
function showLoading() {
    document.getElementById('loadingOverlay').classList.add('active');
}

function hideLoading() {
    document.getElementById('loadingOverlay').classList.remove('active');
}

function formatValue(val) {
    // val 单位是千美元，转为亿美元或百万美元
    if (!val || val === 0) return '$0';
    const billion = val / 1000000; // 十亿
    if (billion >= 1) return `$${billion.toFixed(2)} bn`;
    const million = val / 1000;
    return `$${million.toFixed(2)} M`;
}

function formatPct(val) {
    if (val === null || val === undefined) return '-';
    return `${val >= 0 ? '+' : ''}${val.toFixed(2)}%`;
}

function pctClass(val) {
    if (val > 0) return 'val-positive';
    if (val < 0) return 'val-negative';
    return 'val-neutral';
}

// ============================================================
// API 调用
// ============================================================
async function apiFetch(url) {
    const resp = await fetch(`${API_BASE}${url}`);
    if (!resp.ok) throw new Error(`API error: ${resp.status}`);
    return resp.json();
}

async function loadFunds() {
    const data = await apiFetch('/api/funds');
    return data.funds || [];
}

async function loadPeriods(cik) {
    const data = await apiFetch(`/api/periods/${cik}`);
    return data.periods || [];
}

async function loadHoldings(cik, period, limit = 20) {
    let url = `/api/holdings/${cik}?limit=${limit}`;
    if (period) url += `&period=${period}`;
    const data = await apiFetch(url);
    return data;
}

async function loadChanges(cik, period) {
    let url = `/api/holdings/${cik}/changes`;
    if (period) url += `?period=${period}`;
    const data = await apiFetch(url);
    return data;
}

async function loadHistory(cik) {
    const data = await apiFetch(`/api/holdings/${cik}/history`);
    return data;
}

// ============================================================
// 初始化
// ============================================================
document.addEventListener('DOMContentLoaded', async () => {
    // 绑定事件
    document.getElementById('fundSelector').addEventListener('change', onFundChange);
    document.getElementById('periodSelector').addEventListener('change', onPeriodChange);
    document.getElementById('viewMode').addEventListener('change', onViewModeChange);
    document.getElementById('refreshBtn').addEventListener('click', onRefresh);

    // 初始化图表
    chartInstance = echarts.init(document.getElementById('compositionChart'));
    window.addEventListener('resize', () => chartInstance && chartInstance.resize());

    // 加载基金列表
    try {
        const funds = await loadFunds();
        populateFundSelector(funds);
        if (funds.length > 0) {
            // 默认选第一个
            document.getElementById('fundSelector').value = funds[0].cik;
            await selectFund(funds[0].cik);
        }
    } catch (e) {
        console.error('加载基金列表失败:', e);
        hideLoading();
    }
});

// ============================================================
// 事件处理
// ============================================================
async function onFundChange(e) {
    const cik = e.target.value;
    if (cik) await selectFund(cik);
}

async function onPeriodChange(e) {
    const period = e.target.value;
    if (period && currentCik) {
        currentPeriod = period;
        await loadPeriodData(currentCik, period);
    }
}

function onViewModeChange() {
    // 重新渲染表格
    if (currentCik && currentPeriod) {
        loadPeriodData(currentCik, currentPeriod);
    }
}

async function onRefresh() {
    if (currentCik) {
        await selectFund(currentCik);
    }
}

// ============================================================
// 核心逻辑
// ============================================================
function populateFundSelector(funds) {
    const sel = document.getElementById('fundSelector');
    sel.innerHTML = '';
    funds.forEach(f => {
        const opt = document.createElement('option');
        opt.value = f.cik;
        opt.textContent = `${f.name_cn || f.name}`;
        sel.appendChild(opt);
    });
}

async function selectFund(cik) {
    showLoading();
    currentCik = cik;

    try {
        // 更新基金名称
        const funds = await loadFunds();
        const fund = funds.find(f => f.cik === cik);
        if (fund) {
            document.getElementById('fundNameCn').textContent = fund.name_cn || fund.name;
            document.getElementById('fundNameEn').textContent = `(${fund.name})`;
        }

        // 加载可用季度
        const periods = await loadPeriods(cik);
        populatePeriodSelector(periods);

        if (periods.length > 0) {
            currentPeriod = periods[0].period;
            document.getElementById('periodSelector').value = currentPeriod;
        }

        // 并行加载数据
        const [historyData] = await Promise.all([
            loadHistory(cik),
        ]);

        // 渲染图表
        renderCompositionChart(historyData);

        // 加载当前季度数据
        if (currentPeriod) {
            await loadPeriodData(cik, currentPeriod);
        }
    } catch (e) {
        console.error('加载基金数据失败:', e);
    } finally {
        hideLoading();
    }
}

function populatePeriodSelector(periods) {
    const sel = document.getElementById('periodSelector');
    sel.innerHTML = '';
    periods.forEach(p => {
        const opt = document.createElement('option');
        opt.value = p.period;
        opt.textContent = p.period;
        sel.appendChild(opt);
    });
}

async function loadPeriodData(cik, period) {
    try {
        const [holdingsData, changesData] = await Promise.all([
            loadHoldings(cik, period),
            loadChanges(cik, period),
        ]);

        renderHoldingsTable(holdingsData);
        renderChangesTable(changesData);
        renderFilingTotal(holdingsData.total_value);
    } catch (e) {
        console.error('加载季度数据失败:', e);
    }
}

// ============================================================
// 图表渲染
// ============================================================
function renderCompositionChart(data) {
    if (!data || !data.periods || data.periods.length === 0) {
        chartInstance.setOption({
            title: {
                text: '暂无历史数据', left: 'center', top: 'center',
                textStyle: { color: '#9ca3af', fontSize: 14, fontWeight: 'normal' }
            },
            xAxis: { show: false }, yAxis: { show: false }, series: []
        });
        document.getElementById('chartLegend').innerHTML = '';
        return;
    }

    const series = data.series.map((s, i) => ({
        name: s.name,
        type: 'bar',
        stack: 'total',
        barWidth: '60%',
        emphasis: { focus: 'series' },
        itemStyle: {
            color: ASSET_COLORS[s.name] || COLOR_PALETTE[i % COLOR_PALETTE.length],
            borderRadius: 0,
        },
        data: s.data,
    }));

    const option = {
        tooltip: {
            trigger: 'axis',
            axisPointer: { type: 'shadow' },
            backgroundColor: 'rgba(255,255,255,0.96)',
            borderColor: '#e8ecef',
            borderWidth: 1,
            textStyle: { color: '#1a1a2e', fontSize: 12 },
            formatter: function (params) {
                let html = `<div style="font-weight:600;margin-bottom:6px">${params[0].axisValue}</div>`;
                params.forEach(p => {
                    if (p.value > 0) {
                        html += `<div style="display:flex;align-items:center;gap:6px;margin:2px 0">
                            <span style="width:10px;height:10px;border-radius:2px;background:${p.color};display:inline-block"></span>
                            <span>${p.seriesName}</span>
                            <span style="margin-left:auto;font-weight:600">${p.value.toFixed(1)}%</span>
                        </div>`;
                    }
                });
                return html;
            }
        },
        grid: {
            left: 46, right: 16, top: 16, bottom: 36
        },
        xAxis: {
            type: 'category',
            data: data.periods,
            axisLabel: {
                fontSize: 11,
                color: '#6b7280',
                rotate: data.periods.length > 10 ? 30 : 0,
            },
            axisTick: { show: false },
            axisLine: { lineStyle: { color: '#e8ecef' } },
        },
        yAxis: {
            type: 'value',
            max: 100,
            axisLabel: {
                fontSize: 11,
                color: '#6b7280',
                formatter: '{value}%',
            },
            splitLine: { lineStyle: { color: '#f1f3f5', type: 'dashed' } },
            axisLine: { show: false },
            axisTick: { show: false },
            name: '持仓比例',
            nameTextStyle: { fontSize: 11, color: '#9ca3af', padding: [0, 40, 0, 0] }
        },
        series: series,
        animationDuration: 600,
        animationEasing: 'cubicOut',
    };

    chartInstance.setOption(option, true);

    // 渲染自定义图例
    const legendHtml = data.series.map((s, i) => {
        const color = ASSET_COLORS[s.name] || COLOR_PALETTE[i % COLOR_PALETTE.length];
        return `<div class="legend-item">
            <span class="legend-dot" style="background:${color}"></span>
            <span>${s.name}</span>
        </div>`;
    }).join('');
    document.getElementById('chartLegend').innerHTML = legendHtml;
}

// ============================================================
// 表格渲染
// ============================================================
function renderHoldingsTable(data) {
    const tbody = document.getElementById('holdingsBody');
    const holdings = data.holdings || [];

    if (holdings.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" class="empty-state">该季度暂无持仓数据</td></tr>';
        return;
    }

    const viewMode = document.getElementById('viewMode').value;

    tbody.innerHTML = holdings.map((h, i) => {
        const pctChangeVal = h.pct_change || 0;
        const sharesChangeVal = h.shares_change_pct || 0;
        const portfolioPct = h.portfolio_pct || 0;

        // 占比列
        let pctCell = '';
        if (viewMode === 'change') {
            const pctChangeSub = pctChangeVal !== 0
                ? `<span class="pct-sub ${pctChangeVal > 0 ? 'sub-positive' : 'sub-negative'}">(${formatPct(pctChangeVal)})</span>`
                : '';
            pctCell = `${portfolioPct.toFixed(2)}%${pctChangeSub}`;
        } else {
            pctCell = `${portfolioPct.toFixed(2)}%`;
        }

        // 持仓变化列
        let changeCell = '';
        const hasPrevData = h.prev_pct !== null && h.prev_pct !== undefined;
        if (!hasPrevData && sharesChangeVal === 0) {
            // 无上期数据（最早季度）
            changeCell = `<span class="val-neutral">-</span>`;
        } else if (sharesChangeVal >= 100 && h.prev_pct === 0) {
            changeCell = `<span class="badge-new">New</span>`;
        } else if (sharesChangeVal !== 0) {
            changeCell = `<span class="${pctClass(sharesChangeVal)}">${formatPct(sharesChangeVal)}</span>`;
        } else {
            changeCell = `<span class="val-neutral">0%</span>`;
        }

        const ticker = h.ticker || h.cusip || '-';

        return `<tr>
            <td class="col-rank">${i + 1}</td>
            <td class="col-name">${h.issuer}</td>
            <td class="col-ticker">${ticker}</td>
            <td class="col-class">${h.asset_class || '-'}</td>
            <td class="col-pct">${pctCell}</td>
            <td class="col-change">${changeCell}</td>
        </tr>`;
    }).join('');
}

function renderChangesTable(data) {
    renderSingleChangesTable('increasesBody', data.increases || [], true);
    renderSingleChangesTable('decreasesBody', data.decreases || [], false);
}

function renderSingleChangesTable(tbodyId, items, isIncrease) {
    const tbody = document.getElementById(tbodyId);

    if (items.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" class="empty-state">暂无数据</td></tr>';
        return;
    }

    tbody.innerHTML = items.map((h, i) => {
        const sharesChangeVal = h.shares_change_pct || 0;
        const portfolioPct = h.portfolio_pct || 0;
        const pctChangeVal = h.pct_change || 0;
        const ticker = h.ticker || h.cusip || '-';

        // 占比
        const pctChangeSub = pctChangeVal !== 0
            ? `<span class="pct-sub ${pctChangeVal > 0 ? 'sub-positive' : 'sub-negative'}">(${formatPct(pctChangeVal)})</span>`
            : '';
        const pctCell = `${portfolioPct.toFixed(2)}%${pctChangeSub}`;

        // 变化
        let changeCell = '';
        if (isIncrease && sharesChangeVal >= 100 && h.prev_pct === 0) {
            changeCell = `<span class="badge-new">New</span>`;
        } else if (!isIncrease && sharesChangeVal <= -99) {
            changeCell = `<span class="badge-exit">Exit</span>`;
        } else {
            changeCell = `<span class="${pctClass(sharesChangeVal)}">${formatPct(sharesChangeVal)}</span>`;
        }

        return `<tr>
            <td class="col-rank">${i + 1}</td>
            <td class="col-name">${h.issuer}</td>
            <td class="col-ticker">${ticker}</td>
            <td class="col-class">${h.asset_class || '-'}</td>
            <td class="col-pct">${pctCell}</td>
            <td class="col-change">${changeCell}</td>
        </tr>`;
    }).join('');
}

function renderFilingTotal(totalValue) {
    const el = document.getElementById('filingTotal');
    if (totalValue && totalValue > 0) {
        el.innerHTML = `申报金额：<strong>${formatValue(totalValue)}</strong>`;
    } else {
        el.innerHTML = '';
    }
}
