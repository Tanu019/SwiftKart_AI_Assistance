/**
 * SwiftKart AI — Modern Vanilla JS Application
 * Handles Left Sidebar Navigation, Analytics, Plotly Charts, Conversational AI, and Theme Toggling.
 * Zero Emojis — Clean Vector SVG & Typography.
 */

// Application State
const state = {
  currentTab: 'dashboard',
  theme: localStorage.getItem('swiftkart_theme') || 'dark',
  role: 'Business Head',
  filters: {
    city: 'All',
    persona: 'All',
    time_filter_type: 'Total',
    selected_month: 'All Months',
    selected_quarter: 'All Quarters'
  },
  chatHistory: [],
  isLoadingAnalytics: false,
  isSendingChat: false
};

// -----------------------------------------------------------------------------
// Markdown Configuration & Preprocessing (Paragraphs, Points, Zero Emojis)
// -----------------------------------------------------------------------------
if (typeof marked !== 'undefined') {
  marked.setOptions({
    breaks: true,
    gfm: true
  });
}

function formatAssistantMarkdown(text) {
  if (!text) return '';
  let str = String(text);
  
  // 1. Strip all unicode emojis, icons, and warning pictograms
  str = str.replace(/[\u{1F000}-\u{1FFFF}\u{2600}-\u{26FF}\u{2700}-\u{27BF}\u{FE00}-\u{FE0F}\u{2B50}]/gu, '');
  
  // 2. Ensure section headers have double line breaks before them
  str = str.replace(/([^\n])\s*(###+\s*)/g, '$1\n\n$2');
  
  // 3. Ensure bullet points (•, -, *) have line breaks before them if joined to preceding sentences
  str = str.replace(/([^\n])\s*([•\-\*]\s+)/g, '$1\n\n$2');
  
  // 4. Ensure numbered points (e.g. "SKUs.2. Action:" or "baseline.3. Step:") have line breaks before them
  str = str.replace(/([^\n])\s*(\d+\.\s+\*\*)/g, '$1\n\n$2');
  str = str.replace(/(\.)\s*(\d+\.\s+)/g, '$1\n\n$2');
  
  // 5. Convert bullet character • to markdown standard - for flawless HTML list rendering
  str = str.replace(/^[ \t]*•[ \t]+/gm, '- ');
  
  return str;
}

// SVG Icon Helpers
const ICONS = {
  sun: `<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <circle cx="12" cy="12" r="5"/>
    <line x1="12" y1="1" x2="12" y2="3"/>
    <line x1="12" y1="21" x2="12" y2="23"/>
    <line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/>
    <line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/>
    <line x1="1" y1="12" x2="3" y2="12"/>
    <line x1="21" y1="12" x2="23" y2="12"/>
    <line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/>
    <line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/>
  </svg>`,
  moon: `<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>
  </svg>`,
  user: `<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
    <circle cx="12" cy="7" r="4"/>
  </svg>`,
  bot: `<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <rect x="3" y="11" width="18" height="10" rx="2"/>
    <circle cx="12" cy="5" r="2"/>
    <path d="M12 7v4"/>
    <line x1="8" y1="16" x2="8.01" y2="16"/>
    <line x1="16" y1="16" x2="16.01" y2="16"/>
  </svg>`,
  download: `<svg viewBox="0 0 24 24" width="13" height="13" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
    <polyline points="7 10 12 15 17 10"/>
    <line x1="12" y1="15" x2="12" y2="3"/>
  </svg>`,
  code: `<svg viewBox="0 0 24 24" width="13" height="13" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <polyline points="16 18 22 12 16 6"/>
    <polyline points="8 6 2 12 8 18"/>
  </svg>`
};

// DOM Elements
const elements = {
  // Theme
  html: document.documentElement,
  themeToggleBtn: document.getElementById('theme-toggle-btn'),
  themeSvgSlot: document.getElementById('theme-svg-slot'),
  themeTextLbl: document.getElementById('theme-text-lbl'),

  // Tabs in Left Sidebar
  tabDashboardBtn: document.getElementById('tab-dashboard-btn'),
  tabChatBtn: document.getElementById('tab-chat-btn'),
  viewDashboard: document.getElementById('view-dashboard'),
  viewChat: document.getElementById('view-chat'),

  // Role Perspective in Left Sidebar
  roleSelect: document.getElementById('role-select'),
  briefingRoleLabel: document.getElementById('briefing-role-label'),

  // Pulse Stats in Left Sidebar
  statGrossVol: document.getElementById('stat-gross-vol'),
  statOrdersCount: document.getElementById('stat-orders-count'),
  statCsat: document.getElementById('stat-csat'),

  // Executive Command Header Controls
  quickPresetPills: document.getElementById('quick-preset-pills'),
  btnExportKpis: document.getElementById('btn-export-kpis'),

  // Filter Bar
  filterCity: document.getElementById('filter-city'),
  filterPersona: document.getElementById('filter-persona'),
  filterTimeType: document.getElementById('filter-time-type'),
  monthContainer: document.getElementById('month-select-container'),
  filterMonth: document.getElementById('filter-month'),
  quarterContainer: document.getElementById('quarter-select-container'),
  filterQuarter: document.getElementById('filter-quarter'),
  btnResetFilters: document.getElementById('btn-reset-filters'),
  activeFilterChips: document.getElementById('active-filter-chips'),

  // Executive Briefing
  briefingAttention: document.getElementById('briefing-attention'),
  briefingWatch: document.getElementById('briefing-watch'),
  briefingPositive: document.getElementById('briefing-positive'),
  briefingPriority: document.getElementById('briefing-priority'),
  btnAskBriefing: document.getElementById('btn-ask-briefing'),

  // KPIs
  kpiRevenue: document.getElementById('kpi-revenue'),
  kpiRevenueSub: document.getElementById('kpi-revenue-sub'),
  kpiOrders: document.getElementById('kpi-orders'),
  kpiOrdersSub: document.getElementById('kpi-orders-sub'),
  kpiCustomers: document.getElementById('kpi-customers'),
  kpiCustomersSub: document.getElementById('kpi-customers-sub'),
  kpiAov: document.getElementById('kpi-aov'),
  kpiAovSub: document.getElementById('kpi-aov-sub'),
  kpiRepeat: document.getElementById('kpi-repeat'),
  kpiRepeatSub: document.getElementById('kpi-repeat-sub'),
  kpiChurn: document.getElementById('kpi-churn'),
  kpiChurnSub: document.getElementById('kpi-churn-sub'),

  // Chat
  chatForm: document.getElementById('chat-form'),
  chatTextarea: document.getElementById('chat-textarea'),
  chatMessagesFlow: document.getElementById('chat-messages-flow'),
  chatThinkingIndicator: document.getElementById('chat-thinking-indicator'),
  thinkingStatusText: document.getElementById('thinking-status-text'),
  chatFollowupsBar: document.getElementById('chat-followups-bar'),
  followupsChipsList: document.getElementById('followups-chips-list'),
  starterPromptChips: document.getElementById('starter-prompt-chips'),
  btnClearChat: document.getElementById('btn-clear-chat'),

  // Upload Modal
  modalUpload: document.getElementById('modal-upload'),
  btnOpenUpload: document.getElementById('btn-open-upload'),
  btnCloseUpload: document.getElementById('btn-close-upload'),
  csvDropZone: document.getElementById('csv-drop-zone'),
  csvFileInput: document.getElementById('csv-file-input'),
  uploadStatusMsg: document.getElementById('upload-status-msg')
};

// -----------------------------------------------------------------------------
// Theme Management (Clean SVG Icons, Zero Emojis)
// -----------------------------------------------------------------------------
function applyTheme(theme) {
  state.theme = theme;
  elements.html.setAttribute('data-theme', theme);
  localStorage.setItem('swiftkart_theme', theme);

  if (theme === 'dark') {
    elements.themeSvgSlot.innerHTML = ICONS.sun;
    elements.themeTextLbl.textContent = 'Light Mode';
  } else {
    elements.themeSvgSlot.innerHTML = ICONS.moon;
    elements.themeTextLbl.textContent = 'Dark Mode';
  }

  // Re-render dashboard charts with updated theme palette if data exists
  if (state.lastChartsData) {
    renderDashboardCharts(state.lastChartsData);
  }
}

function toggleTheme() {
  const newTheme = state.theme === 'dark' ? 'light' : 'dark';
  applyTheme(newTheme);
}

// -----------------------------------------------------------------------------
// Tab Switching
// -----------------------------------------------------------------------------
function switchTab(tab) {
  state.currentTab = tab;
  if (tab === 'dashboard') {
    elements.tabDashboardBtn.classList.add('active');
    elements.tabDashboardBtn.setAttribute('aria-selected', 'true');
    elements.tabChatBtn.classList.remove('active');
    elements.tabChatBtn.setAttribute('aria-selected', 'false');

    elements.viewDashboard.style.display = 'flex';
    elements.viewChat.style.display = 'none';

    // Trigger window resize for Plotly responsiveness
    window.dispatchEvent(new Event('resize'));
  } else {
    elements.tabChatBtn.classList.add('active');
    elements.tabChatBtn.setAttribute('aria-selected', 'true');
    elements.tabDashboardBtn.classList.remove('active');
    elements.tabDashboardBtn.setAttribute('aria-selected', 'false');

    elements.viewDashboard.style.display = 'none';
    elements.viewChat.style.display = 'flex';

    elements.chatTextarea.focus();
    scrollChatToBottom();
  }
}

// -----------------------------------------------------------------------------
// Filter Initialization & Synchronization
// -----------------------------------------------------------------------------
async function initFilters() {
  try {
    const res = await fetch('/api/filters');
    if (!res.ok) throw new Error('Failed to load filter options');
    const data = await res.json();

    // Pulse Stats in Sidebar
    if (data.pulse) {
      elements.statGrossVol.textContent = data.pulse.gross_volume || '₹52.4Cr';
      elements.statOrdersCount.textContent = data.pulse.total_orders || '100K';
      elements.statCsat.textContent = data.pulse.csat || '4.6 / 5.0';
    }

    // Cities
    elements.filterCity.innerHTML = '';
    (data.cities || ['All']).forEach(city => {
      const opt = document.createElement('option');
      opt.value = city;
      opt.textContent = city === 'All' ? 'All Cities' : city;
      elements.filterCity.appendChild(opt);
    });

    // Personas
    elements.filterPersona.innerHTML = '';
    (data.personas || ['All']).forEach(persona => {
      const opt = document.createElement('option');
      opt.value = persona;
      opt.textContent = persona === 'All' ? 'All Personas' : persona;
      elements.filterPersona.appendChild(opt);
    });

    // Months
    elements.filterMonth.innerHTML = '';
    (data.months || ['All Months']).forEach(m => {
      const opt = document.createElement('option');
      opt.value = m;
      opt.textContent = m;
      elements.filterMonth.appendChild(opt);
    });

    // Quarters
    elements.filterQuarter.innerHTML = '';
    (data.quarters || ['All Quarters']).forEach(q => {
      const opt = document.createElement('option');
      opt.value = q;
      opt.textContent = q;
      elements.filterQuarter.appendChild(opt);
    });

    updateActiveFilterChips();
  } catch (err) {
    console.error('Filter options error:', err);
  }
}

function updateActiveFilterChips() {
  elements.activeFilterChips.innerHTML = '';

  const addChip = (text) => {
    const span = document.createElement('span');
    span.className = 'filter-chip';
    span.textContent = text;
    elements.activeFilterChips.appendChild(span);
  };

  addChip(`Role: ${state.role}`);
  if (state.filters.city !== 'All') addChip(`City: ${state.filters.city}`);
  if (state.filters.persona !== 'All') addChip(`Persona: ${state.filters.persona}`);
  if (state.filters.time_filter_type === 'Month' && state.filters.selected_month !== 'All Months') {
    addChip(`Month: ${state.filters.selected_month}`);
  } else if (state.filters.time_filter_type === 'Quarter' && state.filters.selected_quarter !== 'All Quarters') {
    addChip(`Quarter: ${state.filters.selected_quarter}`);
  }
}

function resetFilters() {
  state.filters.city = 'All';
  state.filters.persona = 'All';
  state.filters.time_filter_type = 'Total';
  state.filters.selected_month = 'All Months';
  state.filters.selected_quarter = 'All Quarters';

  elements.filterCity.value = 'All';
  elements.filterPersona.value = 'All';
  elements.filterTimeType.value = 'Total';
  elements.filterMonth.value = 'All Months';
  elements.filterQuarter.value = 'All Quarters';

  elements.monthContainer.style.display = 'none';
  elements.quarterContainer.style.display = 'none';

  updateActiveFilterChips();
  fetchAnalytics();
}

// -----------------------------------------------------------------------------
// -----------------------------------------------------------------------------
// In-Memory Client Cache (0ms Instant Filter Switching)
// -----------------------------------------------------------------------------
const analyticsCache = new Map();

function renderAnalyticsData(data) {
  // 1. Update KPIs
  if (data.kpis) {
    state.lastKpiData = data.kpis;
    elements.kpiRevenue.textContent = data.kpis.total_revenue.formatted;
    elements.kpiRevenueSub.textContent = data.kpis.total_revenue.sub;

    elements.kpiOrders.textContent = data.kpis.total_orders.formatted;
    elements.kpiOrdersSub.textContent = data.kpis.total_orders.sub;

    elements.kpiCustomers.textContent = data.kpis.active_customers.formatted;
    elements.kpiCustomersSub.textContent = data.kpis.active_customers.sub;

    elements.kpiAov.textContent = data.kpis.avg_order_value.formatted;
    elements.kpiAovSub.textContent = data.kpis.avg_order_value.sub;

    elements.kpiRepeat.textContent = data.kpis.repeat_purchase_rate.formatted;
    elements.kpiRepeatSub.textContent = data.kpis.repeat_purchase_rate.sub;

    elements.kpiChurn.textContent = data.kpis.churn_risk_avg.formatted;
    elements.kpiChurnSub.textContent = data.kpis.churn_risk_avg.sub;

    // Update progress bar widths dynamically
    const fillRev = document.querySelector('.kpi-card[data-kpi="total_revenue"] .kpi-progress-fill');
    if (fillRev) fillRev.style.width = '88%';

    const fillOrders = document.querySelector('.kpi-card[data-kpi="total_orders"] .kpi-progress-fill');
    if (fillOrders) fillOrders.style.width = '82%';

    const fillCust = document.querySelector('.kpi-card[data-kpi="active_customers"] .kpi-progress-fill');
    if (fillCust) fillCust.style.width = '75%';

    const fillAov = document.querySelector('.kpi-card[data-kpi="avg_order_value"] .kpi-progress-fill');
    if (fillAov) fillAov.style.width = '68%';

    const fillRepeat = document.querySelector('.kpi-card[data-kpi="repeat_purchase_rate"] .kpi-progress-fill');
    if (fillRepeat) {
      const rateVal = parseFloat(data.kpis.repeat_purchase_rate.val || 65);
      fillRepeat.style.width = `${Math.min(100, Math.max(10, rateVal))}%`;
    }

    const fillChurn = document.querySelector('.kpi-card[data-kpi="churn_risk_avg"] .kpi-progress-fill');
    if (fillChurn) {
      const churnVal = parseFloat(data.kpis.churn_risk_avg.val || 55);
      fillChurn.style.width = `${Math.min(100, Math.max(10, churnVal))}%`;
    }
  }

  // 2. Update Briefing
  if (data.briefing) {
    elements.briefingRoleLabel.textContent = `Executive Briefing • ${state.role}`;
    elements.briefingAttention.textContent = data.briefing.needs_attention;
    elements.briefingWatch.textContent = data.briefing.watch;
    elements.briefingPositive.textContent = data.briefing.positive;
    elements.briefingPriority.textContent = data.briefing.priority;
  }

  // 3. Render Dashboard Charts
  if (data.charts) {
    state.lastChartsData = data.charts;
    renderDashboardCharts(data.charts);
  }
}

async function fetchAnalytics() {
  const payload = {
    role: state.role,
    city: state.filters.city,
    persona: state.filters.persona,
    time_filter_type: state.filters.time_filter_type,
    selected_month: state.filters.selected_month,
    selected_quarter: state.filters.selected_quarter
  };

  const cacheKey = JSON.stringify(payload);
  if (analyticsCache.has(cacheKey)) {
    renderAnalyticsData(analyticsCache.get(cacheKey));
    return;
  }

  if (state.isLoadingAnalytics) return;
  state.isLoadingAnalytics = true;

  try {
    const res = await fetch('/api/analytics', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    if (!res.ok) throw new Error('Analytics API error');
    const data = await res.json();
    analyticsCache.set(cacheKey, data);
    renderAnalyticsData(data);
  } catch (err) {
    console.error('Failed to load analytics:', err);
  } finally {
    state.isLoadingAnalytics = false;
  }
}

// -----------------------------------------------------------------------------
// Plotly Chart Renderers for Dashboard
// -----------------------------------------------------------------------------
function getPlotlyLayoutDefaults() {
  const isDark = state.theme === 'dark';
  return {
    paper_bgcolor: 'rgba(0,0,0,0)',
    plot_bgcolor: 'rgba(0,0,0,0)',
    font: {
      family: 'Plus Jakarta Sans, sans-serif',
      color: isDark ? '#94A3B8' : '#475569',
      size: 10
    },
    margin: { t: 15, r: 15, l: 48, b: 32 },
    xaxis: {
      gridcolor: isDark ? 'rgba(255,255,255,0.05)' : 'rgba(0,0,0,0.05)',
      zerolinecolor: isDark ? 'rgba(255,255,255,0.08)' : 'rgba(0,0,0,0.08)',
      tickfont: { size: 9.5, color: isDark ? '#94A3B8' : '#64748B' }
    },
    yaxis: {
      gridcolor: isDark ? 'rgba(255,255,255,0.05)' : 'rgba(0,0,0,0.05)',
      zerolinecolor: isDark ? 'rgba(255,255,255,0.08)' : 'rgba(0,0,0,0.08)',
      tickfont: { size: 9.5, color: isDark ? '#94A3B8' : '#64748B' }
    },
    legend: {
      orientation: 'h',
      y: 1.15,
      x: 0,
      font: { size: 9.5, color: isDark ? '#CBD5E1' : '#334155' }
    }
  };
}

function renderDashboardCharts(charts) {
  const defaults = getPlotlyLayoutDefaults();
  const isDark = state.theme === 'dark';
  const config = { responsive: true, displayModeBar: false };

  // Chart 1: Orders Trend (Monthly / Daily timeline)
  if (charts.orders_trend && charts.orders_trend.records && charts.orders_trend.records.length > 0) {
    const records = charts.orders_trend.records;
    const xDates = records.map(r => r.dt);
    const yRevenue = records.map(r => r.revenue);
    const yOrders = records.map(r => r.orders);

    const trace1 = {
      x: xDates,
      y: yRevenue,
      name: 'Gross Turnover (INR)',
      type: 'scatter',
      mode: 'lines+markers',
      fill: 'tozeroy',
      line: { color: '#6366F1', width: 3, shape: 'spline' },
      marker: { size: 6, color: '#6366F1' },
      fillcolor: isDark ? 'rgba(99, 102, 241, 0.16)' : 'rgba(79, 70, 229, 0.1)',
      hovertemplate: '<b>%{x}</b><br>Gross Revenue: ₹%{y:,.0f}<extra></extra>'
    };

    const trace2 = {
      x: xDates,
      y: yOrders,
      name: 'Order Volume',
      type: 'bar',
      yaxis: 'y2',
      marker: {
        color: isDark ? 'rgba(6, 182, 212, 0.45)' : 'rgba(6, 182, 212, 0.35)',
        line: { color: '#06B6D4', width: 1.5 }
      },
      hovertemplate: '<b>%{x}</b><br>Orders Fulfilled: %{y:,}<extra></extra>'
    };

    const layout = {
      ...defaults,
      xaxis: {
        ...defaults.xaxis,
        type: 'category'
      },
      yaxis: {
        ...defaults.yaxis,
        title: 'Gross Revenue (INR)',
        tickprefix: '₹',
        separatethousands: true
      },
      yaxis2: {
        title: 'Order Volume',
        overlaying: 'y',
        side: 'right',
        gridcolor: 'transparent',
        tickfont: { size: 10, color: isDark ? '#94A3B8' : '#64748B' }
      }
    };

    Plotly.react('chart-orders-trend', [trace1, trace2], layout, config);
  }

  // Chart 2: Revenue by Metro City
  if (charts.revenue_by_city && charts.revenue_by_city.records && charts.revenue_by_city.records.length > 0) {
    const records = charts.revenue_by_city.records;
    const cities = records.map(r => r.city);
    const revenues = records.map(r => r.revenue);
    const customData = records.map(r => [
      r.orders || 0,
      Math.round(r.aov || (r.revenue / Math.max(1, r.orders || 1)))
    ]);

    const palette = ['#6366F1', '#4F46E5', '#8B5CF6', '#7C3AED', '#EC4899', '#DB2777', '#06B6D4', '#0891B2', '#10B981', '#059669'];

    const trace = {
      x: cities,
      y: revenues,
      customdata: customData,
      type: 'bar',
      marker: {
        color: palette.slice(0, cities.length),
        line: { width: 1, color: isDark ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.1)' }
      },
      hovertemplate: '<b>%{x}</b><br>Revenue: ₹%{y:,.0f}<br>Orders: %{customdata[0]:,}<br>AOV: ₹%{customdata[1]:,}<extra></extra>'
    };

    const layout = {
      ...defaults,
      xaxis: {
        ...defaults.xaxis,
        type: 'category',
        tickangle: -20
      },
      yaxis: {
        ...defaults.yaxis,
        title: 'Gross Revenue (INR)',
        tickprefix: '₹',
        separatethousands: true
      }
    };

    Plotly.react('chart-revenue-city', [trace], layout, config);
  }

  // Chart 3: CSAT Score vs Delivery Window
  if (charts.delivery_vs_sat && charts.delivery_vs_sat.records && charts.delivery_vs_sat.records.length > 0) {
    const records = charts.delivery_vs_sat.records;
    const windows = records.map(r => r.delivery_window || (r.delivery_bucket !== undefined ? `${r.delivery_bucket}m` : 'Standard'));
    const satScores = records.map(r => typeof r.avg_sat === 'number' ? Number(r.avg_sat.toFixed(2)) : parseFloat(r.avg_sat || 4));
    const orderCounts = records.map(r => r.orders || 0);

    const traceCsat = {
      x: windows,
      y: satScores,
      customdata: orderCounts,
      name: 'CSAT Rating',
      type: 'scatter',
      mode: 'lines+markers+text',
      text: satScores.map(s => s.toFixed(2)),
      textposition: 'top center',
      textfont: {
        color: isDark ? '#F8FAFC' : '#0F172A',
        size: 11,
        family: 'Plus Jakarta Sans'
      },
      line: { color: '#F59E0B', width: 3, shape: 'spline' },
      marker: { size: 9, color: '#F59E0B', line: { width: 2, color: '#FFFFFF' } },
      hovertemplate: '<b>%{x}</b><br>CSAT Score: <b>%{y:.2f} / 5.0</b><br>Order Volume: %{customdata:,}<extra></extra>'
    };

    const traceBenchmark = {
      x: windows,
      y: windows.map(() => 4.0),
      name: 'SLA Benchmark (4.0)',
      type: 'scatter',
      mode: 'lines',
      line: { dash: 'dash', color: '#10B981', width: 2 },
      hoverinfo: 'name'
    };

    const layout = {
      ...defaults,
      xaxis: {
        ...defaults.xaxis,
        type: 'category',
        title: 'Delivery Window'
      },
      yaxis: {
        ...defaults.yaxis,
        title: 'CSAT (1 - 5 Scale)',
        range: [2.5, 5.0],
        dtick: 0.5
      }
    };

    Plotly.react('chart-delivery-sat', [traceCsat, traceBenchmark], layout, config);
  }

  // Chart 4: Customer Persona Composition
  if (charts.persona_dist && charts.persona_dist.records && charts.persona_dist.records.length > 0) {
    const records = charts.persona_dist.records;
    const labels = records.map(r => r.persona);
    const values = records.map(r => r.count);
    const totalCount = values.reduce((a, b) => a + b, 0);

    const trace = {
      labels: labels,
      values: values,
      type: 'pie',
      hole: 0.62,
      marker: {
        colors: ['#6366F1', '#06B6D4', '#10B981', '#F59E0B', '#8B5CF6', '#EC4899']
      },
      textinfo: 'percent',
      textposition: 'outside',
      automargin: true,
      hovertemplate: '<b>%{label}</b><br>Active Customers: %{value:,}<br>Cohort Share: %{percent}<extra></extra>'
    };

    const layout = {
      ...defaults,
      showlegend: true,
      annotations: [
        {
          font: { size: 14, family: 'Plus Jakarta Sans', color: isDark ? '#F8FAFC' : '#0F172A', weight: 'bold' },
          showarrow: false,
          text: `<b>${totalCount.toLocaleString()}</b><br><span style="font-size:10px; color:#94A3B8; font-weight:normal;">CUSTOMERS</span>`,
          x: 0.5,
          y: 0.5
        }
      ]
    };

    Plotly.react('chart-persona-dist', [trace], layout, config);
  }

  // Chart 5: Predicted Attrition Risk by Segment
  if (charts.churn_by_persona && charts.churn_by_persona.records && charts.churn_by_persona.records.length > 0) {
    const records = charts.churn_by_persona.records;
    const personas = records.map(r => r.persona);
    const churnScores = records.map(r => typeof r.avg_churn === 'number' ? r.avg_churn : parseFloat(r.avg_churn || 0));
    const colors = churnScores.map(c => c >= 50 ? '#EF4444' : c >= 35 ? '#F59E0B' : '#10B981');

    const trace = {
      y: personas,
      x: churnScores,
      type: 'bar',
      orientation: 'h',
      text: churnScores.map(c => `${c}%`),
      textposition: 'auto',
      marker: {
        color: colors,
        line: { width: 1, color: isDark ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.1)' }
      },
      hovertemplate: '<b>%{y}</b><br>Predicted Churn Risk: <b>%{x}%</b><extra></extra>'
    };

    const layout = {
      ...defaults,
      margin: { ...defaults.margin, l: 120 },
      xaxis: {
        ...defaults.xaxis,
        type: 'linear',
        range: [0, 100],
        title: 'Predicted Churn Risk (%)',
        ticksuffix: '%'
      },
      yaxis: {
        ...defaults.yaxis,
        type: 'category',
        automargin: true
      }
    };

    Plotly.react('chart-churn-persona', [trace], layout, config);
  }

  // Chart 6: Top Merchandise Categories by Turnover
  if (charts.cat_revenue && charts.cat_revenue.records && charts.cat_revenue.records.length > 0) {
    const records = charts.cat_revenue.records;
    const categories = records.map(r => r.category || 'General');
    const revenues = records.map(r => r.revenue || 0);
    const catPalette = ['#8B5CF6', '#6366F1', '#06B6D4', '#10B981', '#F59E0B', '#EC4899', '#3B82F6', '#14B8A6'];

    const trace = {
      x: categories,
      y: revenues,
      type: 'bar',
      marker: {
        color: catPalette.slice(0, categories.length),
        line: { width: 1, color: isDark ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.1)' }
      },
      hovertemplate: '<b>%{x}</b><br>Gross Revenue: ₹%{y:,.0f}<extra></extra>'
    };

    const layout = {
      ...defaults,
      xaxis: {
        ...defaults.xaxis,
        type: 'category',
        tickangle: -20
      },
      yaxis: {
        ...defaults.yaxis,
        title: 'Gross Revenue (INR)',
        tickprefix: '₹',
        separatethousands: true
      }
    };

    Plotly.react('chart-category-rev', [trace], layout, config);
  }
}

// -----------------------------------------------------------------------------
// Conversational AI Chat Flow (Zero Emojis, Clean SVG Icons)
// -----------------------------------------------------------------------------
function scrollChatToBottom() {
  setTimeout(() => {
    elements.chatMessagesFlow.scrollTop = elements.chatMessagesFlow.scrollHeight;
  }, 50);
}

function appendUserMessage(text) {
  const msgEl = document.createElement('div');
  msgEl.className = 'chat-message user';
  msgEl.innerHTML = `
    <div class="msg-avatar">${ICONS.user}</div>
    <div class="msg-body">
      <div class="msg-author">
        <span>You</span>
        <span class="msg-time">${new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
      </div>
      <div class="msg-content">
        <p>${escapeHtml(text)}</p>
      </div>
    </div>
  `;
  elements.chatMessagesFlow.appendChild(msgEl);
  scrollChatToBottom();
}

function escapeHtml(str) {
  return str
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

function appendAssistantMessage(data) {
  const msgEl = document.createElement('div');
  msgEl.className = 'chat-message assistant';

  let bodyHtml = '';

  // 1. Text or Markdown Content
  if (data.content) {
    const formatted = formatAssistantMarkdown(data.content);
    const renderedMarkdown = typeof marked !== 'undefined' ? marked.parse(formatted) : `<p>${escapeHtml(formatted)}</p>`;
    bodyHtml += `<div class="msg-content markdown-body">${renderedMarkdown}</div>`;
  }

  // 2. Table Data
  if (data.type === 'table' && data.data && data.data.length > 0) {
    const cols = data.columns || Object.keys(data.data[0]);
    const tableId = `table-${Date.now()}`;

    let tableHeaders = cols.map(c => `<th>${escapeHtml(String(c))}</th>`).join('');
    let tableRows = data.data.slice(0, 15).map(row => {
      const cells = cols.map(c => `<td>${escapeHtml(String(row[c] !== null && row[c] !== undefined ? row[c] : ''))}</td>`).join('');
      return `<tr>${cells}</tr>`;
    }).join('');

    bodyHtml += `
      <div class="chat-table-wrapper">
        <div class="chat-table-actions">
          <span class="chat-table-title">Query Results (${data.total_rows || data.data.length} records)</span>
          <button class="btn-csv-download" data-table-id="${tableId}">
            ${ICONS.download}
            <span>Download CSV</span>
          </button>
        </div>
        <div style="overflow-x: auto; max-height: 350px;">
          <table class="chat-data-table" id="${tableId}">
            <thead><tr>${tableHeaders}</tr></thead>
            <tbody>${tableRows}</tbody>
          </table>
        </div>
      </div>
    `;

    // Store table data for CSV export
    window[`csv_${tableId}`] = data.data;
  }

  // 3. Interactive Plotly Chart
  let chartContainerId = null;
  if (data.type === 'chart' && data.figure) {
    chartContainerId = `chart-ai-${Date.now()}`;
    bodyHtml += `
      <div class="chat-chart-box" id="${chartContainerId}"></div>
    `;
  }

  // 4. DuckDB SQL Accordion (Clean code icon, no emojis)
  if (data.sql) {
    bodyHtml += `
      <details class="sql-query-accordion">
        <summary class="sql-query-toggle">
          ${ICONS.code}
          <span>View Executed SQL Query</span>
        </summary>
        <div class="sql-query-content"><code>${escapeHtml(data.sql)}</code></div>
      </details>
    `;
  }

  msgEl.innerHTML = `
    <div class="msg-avatar">${ICONS.bot}</div>
    <div class="msg-body">
      <div class="msg-author">
        <span>SwiftKart AI Analyst</span>
        <span class="msg-time">${new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
      </div>
      ${bodyHtml}
    </div>
  `;

  elements.chatMessagesFlow.appendChild(msgEl);

  // If there's an interactive chart, render it with Plotly
  if (chartContainerId && data.figure) {
    const layout = {
      ...data.figure.layout,
      paper_bgcolor: 'rgba(0,0,0,0)',
      plot_bgcolor: 'rgba(0,0,0,0)',
      font: { color: state.theme === 'dark' ? '#94A3B8' : '#475569' }
    };
    Plotly.newPlot(chartContainerId, data.figure.data, layout, { responsive: true, displayModeBar: false });
  }

  // Render Follow-up Chips
  if (data.follow_ups && data.follow_ups.length > 0) {
    renderFollowUpChips(data.follow_ups);
  } else {
    elements.chatFollowupsBar.style.display = 'none';
  }

  scrollChatToBottom();
}

function renderFollowUpChips(chips) {
  elements.followupsChipsList.innerHTML = '';
  chips.forEach(text => {
    const btn = document.createElement('button');
    btn.className = 'followup-pill-btn';
    btn.textContent = text;
    btn.addEventListener('click', () => {
      sendChatMessage(text);
    });
    elements.followupsChipsList.appendChild(btn);
  });
  elements.chatFollowupsBar.style.display = 'flex';
}

async function sendChatMessage(query) {
  if (!query || state.isSendingChat) return;

  state.isSendingChat = true;
  elements.chatTextarea.value = '';
  elements.chatFollowupsBar.style.display = 'none';

  // 1. Add user message
  appendUserMessage(query);
  state.chatHistory.push({ role: 'user', content: query, type: 'text' });

  // 2. Show thinking indicator with dynamic progress
  elements.chatThinkingIndicator.style.display = 'flex';
  elements.thinkingStatusText.textContent = 'Querying DuckDB datalake...';
  scrollChatToBottom();

  const payload = {
    message: query,
    history: state.chatHistory.slice(-4),
    role: state.role
  };

  try {
    const res = await fetch('/api/chat/stream', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    if (!res.ok) throw new Error(`HTTP error ${res.status}`);

    const reader = res.body.getReader();
    const decoder = new TextDecoder('utf-8');
    let buffer = '';
    let msgEl = null;
    let contentEl = null;
    let executedSql = null;
    let accumulatedText = '';
    let isStreamActive = false;

    let renderRafId = null;

    while (true) {
      const { value, done } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const events = buffer.split('\n\n');
      buffer = events.pop(); // retain incomplete remainder

      for (const rawEvent of events) {
        if (!rawEvent.startsWith('data: ')) continue;
        const jsonStr = rawEvent.slice(6).trim();
        if (!jsonStr) continue;

        let evt;
        try {
          evt = JSON.parse(jsonStr);
        } catch {
          continue;
        }

        // Error event
        if (evt.type === 'error') {
          elements.chatThinkingIndicator.style.display = 'none';
          appendAssistantMessage({
            type: 'text',
            content: evt.content || 'AI Assistant Engine is currently offline. Please configure your GROQ_API_KEY.',
            follow_ups: evt.follow_ups || [
              'Which city generated the highest gross revenue?',
              'Which customer persona has the highest churn risk?'
            ]
          });
          state.chatHistory.push({ role: 'assistant', content: evt.content, type: 'text' });
          return;
        }

        // Table or Chart output
        if (evt.type === 'table' || evt.type === 'chart' || evt.type === 'done_single') {
          elements.chatThinkingIndicator.style.display = 'none';
          appendAssistantMessage(evt);
          if (evt.content) {
            state.chatHistory.push({ role: 'assistant', content: evt.content, type: 'text' });
          }
          return;
        }

        // Start event with SQL
        if (evt.type === 'start') {
          executedSql = evt.sql;
          elements.thinkingStatusText.textContent = 'Synthesizing executive brief...';
          continue;
        }

        // Streaming text delta with 60fps RAF throttling
        if (evt.type === 'chunk') {
          if (!isStreamActive) {
            isStreamActive = true;
            elements.chatThinkingIndicator.style.display = 'none';

            msgEl = document.createElement('div');
            msgEl.className = 'chat-message assistant';
            msgEl.innerHTML = `
              <div class="msg-avatar">${ICONS.bot}</div>
              <div class="msg-body">
                <div class="msg-author">
                  <span>SwiftKart AI Analyst</span>
                  <span class="msg-time">${new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
                </div>
                <div class="msg-content markdown-body"></div>
              </div>
            `;
            contentEl = msgEl.querySelector('.msg-content');
            elements.chatMessagesFlow.appendChild(msgEl);
          }

          accumulatedText += evt.delta;
          if (contentEl && !renderRafId) {
            renderRafId = requestAnimationFrame(() => {
              renderRafId = null;
              if (contentEl) {
                const formatted = formatAssistantMarkdown(accumulatedText);
                contentEl.innerHTML = typeof marked !== 'undefined' ? marked.parse(formatted) : `<p>${escapeHtml(formatted)}</p>`;
              }
              scrollChatToBottom();
            });
          }
        }

        // Stream complete
        if (evt.type === 'done') {
          if (renderRafId) {
            cancelAnimationFrame(renderRafId);
            renderRafId = null;
          }
          elements.chatThinkingIndicator.style.display = 'none';
          if (contentEl && accumulatedText) {
            const formatted = formatAssistantMarkdown(accumulatedText);
            contentEl.innerHTML = typeof marked !== 'undefined' ? marked.parse(formatted) : `<p>${escapeHtml(formatted)}</p>`;
          }
          if (executedSql && msgEl) {
            const bodyDiv = msgEl.querySelector('.msg-body');
            const sqlDiv = document.createElement('details');
            sqlDiv.className = 'sql-query-accordion';
            sqlDiv.innerHTML = `
              <summary class="sql-query-toggle">
                ${ICONS.code}
                <span>View Executed SQL Query</span>
              </summary>
              <div class="sql-query-content"><code>${escapeHtml(executedSql)}</code></div>
            `;
            bodyDiv.appendChild(sqlDiv);
          }

          if (accumulatedText) {
            state.chatHistory.push({ role: 'assistant', content: formatAssistantMarkdown(accumulatedText), type: 'text' });
          }

          if (evt.follow_ups && evt.follow_ups.length > 0) {
            renderFollowUpChips(evt.follow_ups);
          }
          scrollChatToBottom();
        }
    }

    if (!isStreamActive && !msgEl) {
      elements.chatThinkingIndicator.style.display = 'none';
      appendAssistantMessage({
        type: 'text',
        content: 'AI Assistant received your inquiry. Please verify that `GROQ_API_KEY` is configured in Render Environment Variables.',
        follow_ups: ['Which customer persona has the highest churn risk, and why?']
      });
    }

  } catch (err) {
    console.warn('Streaming error, falling back to standard API:', err);
    try {
      const res = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      elements.chatThinkingIndicator.style.display = 'none';
      if (!res.ok) throw new Error('Chat API returned an error');
      const responseData = await res.json();
      appendAssistantMessage(responseData);
      if (responseData.content) {
        state.chatHistory.push({ role: 'assistant', content: responseData.content, type: 'text' });
      }
    } catch (fallbackErr) {
      elements.chatThinkingIndicator.style.display = 'none';
      appendAssistantMessage({
        type: 'text',
        content: `Failed to get answer: ${fallbackErr.message}. Please verify GROQ_API_KEY.`,
        follow_ups: []
      });
    }
  } finally {
    state.isSendingChat = false;
    elements.chatThinkingIndicator.style.display = 'none';
    elements.chatTextarea.focus();
  }
}

// -----------------------------------------------------------------------------
// CSV Download Functionality for Table Results
// -----------------------------------------------------------------------------
function downloadRecordsAsCsv(records, filename = 'swiftkart_data.csv') {
  if (!records || !records.length) return;
  const keys = Object.keys(records[0]);
  const csvRows = [keys.join(',')];

  records.forEach(row => {
    const values = keys.map(k => {
      const escaped = ('' + (row[k] !== null && row[k] !== undefined ? row[k] : '')).replace(/"/g, '""');
      return `"${escaped}"`;
    });
    csvRows.push(values.join(','));
  });

  const blob = new Blob([csvRows.join('\n')], { type: 'text/csv;charset=utf-8;' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.setAttribute('href', url);
  a.setAttribute('download', filename);
  a.style.display = 'none';
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
}

// -----------------------------------------------------------------------------
// CSV Upload Handler (Zero Emojis)
// -----------------------------------------------------------------------------
async function handleCsvUpload(file) {
  if (!file || !file.name.endsWith('.csv')) {
    elements.uploadStatusMsg.textContent = 'Please upload a valid .csv file';
    elements.uploadStatusMsg.style.color = '#EF4444';
    return;
  }

  elements.uploadStatusMsg.textContent = 'Registering table into DuckDB Datalake...';
  elements.uploadStatusMsg.style.color = '#6366F1';

  const formData = new FormData();
  formData.append('file', file);

  try {
    const res = await fetch('/api/upload', {
      method: 'POST',
      body: formData
    });

    if (!res.ok) throw new Error('Upload failed');
    const data = await res.json();

    elements.uploadStatusMsg.textContent = `Successfully registered table "${data.table_name}" (${data.rows} rows)!`;
    elements.uploadStatusMsg.style.color = '#10B981';

    // Invalidate client analytics cache so fresh data is rendered
    analyticsCache.clear();

    setTimeout(() => {
      elements.modalUpload.style.display = 'none';
      initFilters();
      fetchAnalytics();
    }, 1500);

  } catch (err) {
    elements.uploadStatusMsg.textContent = `Upload failed: ${err.message}`;
    elements.uploadStatusMsg.style.color = '#EF4444';
  }
}

// -----------------------------------------------------------------------------
// Event Listeners Setup
// -----------------------------------------------------------------------------
function setupEventListeners() {
  // Theme Toggle
  elements.themeToggleBtn.addEventListener('click', toggleTheme);

  // Tab Navigation in Left Sidebar
  elements.tabDashboardBtn.addEventListener('click', () => switchTab('dashboard'));
  elements.tabChatBtn.addEventListener('click', () => switchTab('chat'));

  // Role Selector in Left Sidebar
  elements.roleSelect.addEventListener('change', (e) => {
    state.role = e.target.value;
    updateActiveFilterChips();
    fetchAnalytics();
  });

  // Filter Selects
  elements.filterCity.addEventListener('change', (e) => {
    state.filters.city = e.target.value;
    updateActiveFilterChips();
    fetchAnalytics();
  });

  elements.filterPersona.addEventListener('change', (e) => {
    state.filters.persona = e.target.value;
    updateActiveFilterChips();
    fetchAnalytics();
  });

  elements.filterTimeType.addEventListener('change', (e) => {
    const val = e.target.value;
    state.filters.time_filter_type = val;

    if (val === 'Month') {
      elements.monthContainer.style.display = 'flex';
      elements.quarterContainer.style.display = 'none';
    } else if (val === 'Quarter') {
      elements.monthContainer.style.display = 'none';
      elements.quarterContainer.style.display = 'flex';
    } else {
      elements.monthContainer.style.display = 'none';
      elements.quarterContainer.style.display = 'none';
    }

    updateActiveFilterChips();
    fetchAnalytics();
  });

  elements.filterMonth.addEventListener('change', (e) => {
    state.filters.selected_month = e.target.value;
    updateActiveFilterChips();
    fetchAnalytics();
  });

  elements.filterQuarter.addEventListener('change', (e) => {
    state.filters.selected_quarter = e.target.value;
    updateActiveFilterChips();
    fetchAnalytics();
  });

  // Reset Filters Button
  elements.btnResetFilters.addEventListener('click', resetFilters);

  // Quick Preset Time Pills in Command Header
  if (elements.quickPresetPills) {
    elements.quickPresetPills.addEventListener('click', (e) => {
      const pill = e.target.closest('.preset-pill-btn');
      if (!pill) return;

      document.querySelectorAll('.preset-pill-btn').forEach(btn => btn.classList.remove('active'));
      pill.classList.add('active');

      const filterType = pill.getAttribute('data-filter');
      const filterVal = pill.getAttribute('data-val');

      if (filterType === 'total') {
        state.filters.time_filter_type = 'Total';
        elements.filterTimeType.value = 'Total';
        elements.monthContainer.style.display = 'none';
        elements.quarterContainer.style.display = 'none';
      } else if (filterType === 'quarter') {
        state.filters.time_filter_type = 'Quarter';
        state.filters.selected_quarter = filterVal;
        elements.filterTimeType.value = 'Quarter';
        elements.quarterContainer.style.display = 'flex';
        elements.monthContainer.style.display = 'none';
        elements.filterQuarter.value = filterVal;
      } else if (filterType === 'month') {
        state.filters.time_filter_type = 'Month';
        state.filters.selected_month = filterVal;
        elements.filterTimeType.value = 'Month';
        elements.monthContainer.style.display = 'flex';
        elements.quarterContainer.style.display = 'none';
        elements.filterMonth.value = filterVal;
      }

      updateActiveFilterChips();
      fetchAnalytics();
    });
  }

  // Export Executive KPI Summary Button
  if (elements.btnExportKpis) {
    elements.btnExportKpis.addEventListener('click', () => {
      if (!state.lastKpiData) return;
      const rows = Object.entries(state.lastKpiData).map(([key, val]) => ({
        Metric_Key: key,
        Metric_Name: val.label || key,
        Current_Value: val.formatted || val.val,
        Period_Context: val.sub || ''
      }));
      downloadRecordsAsCsv(rows, `swiftkart_executive_kpis_${new Date().toISOString().slice(0, 10)}.csv`);
    });
  }

  // Responsive Plotly Resize Handler
  let resizeDebounceTimer;
  window.addEventListener('resize', () => {
    clearTimeout(resizeDebounceTimer);
    resizeDebounceTimer = setTimeout(() => {
      const chartIds = [
        'chart-orders-trend',
        'chart-revenue-city',
        'chart-delivery-sat',
        'chart-persona-dist',
        'chart-churn-persona',
        'chart-category-rev'
      ];
      chartIds.forEach(id => {
        const container = document.getElementById(id);
        if (container && container.data) {
          Plotly.Plots.resize(container);
        }
      });
    }, 120);
  });

  // Deep Dive from Briefing
  elements.btnAskBriefing.addEventListener('click', () => {
    switchTab('chat');
    sendChatMessage(`Provide a detailed strategic briefing for our ${state.role} based on current performance and high churn cities.`);
  });

  // Ask AI triggers from KPI cards & Charts
  document.addEventListener('click', (e) => {
    const aiBtn = e.target.closest('.kpi-ai-trigger, .chart-ai-btn');
    if (aiBtn) {
      const prompt = aiBtn.getAttribute('data-prompt');
      if (prompt) {
        switchTab('chat');
        sendChatMessage(prompt);
      }
    }

    // CSV Download click
    const csvBtn = e.target.closest('.btn-csv-download');
    if (csvBtn) {
      const tableId = csvBtn.getAttribute('data-table-id');
      const records = window[`csv_${tableId}`];
      if (records) {
        downloadRecordsAsCsv(records, `swiftkart_${tableId}.csv`);
      }
    }
  });

  // Starter Prompt Chips in Chat
  elements.starterPromptChips.addEventListener('click', (e) => {
    const chip = e.target.closest('.chip-prompt-btn');
    if (chip) {
      const query = chip.getAttribute('data-query');
      if (query) {
        sendChatMessage(query);
      }
    }
  });

  // Chat Form Submission
  elements.chatForm.addEventListener('submit', (e) => {
    e.preventDefault();
    const query = elements.chatTextarea.value.trim();
    if (query) {
      sendChatMessage(query);
    }
  });

  // Enter to send, Shift+Enter for newline
  elements.chatTextarea.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      elements.chatForm.dispatchEvent(new Event('submit'));
    }
  });

  // Auto-resize chat textarea
  elements.chatTextarea.addEventListener('input', () => {
    elements.chatTextarea.style.height = 'auto';
    elements.chatTextarea.style.height = `${Math.min(elements.chatTextarea.scrollHeight, 120)}px`;
  });

  // Clear Chat History
  elements.btnClearChat.addEventListener('click', () => {
    state.chatHistory = [];
    elements.chatMessagesFlow.innerHTML = `
      <div class="chat-message assistant">
        <div class="msg-avatar">${ICONS.bot}</div>
        <div class="msg-body">
          <div class="msg-author">
            <span>SwiftKart AI Analyst</span>
            <span class="msg-time">Ready</span>
          </div>
          <div class="msg-content markdown-body">
            <p>Chat cleared. Ready for your next business inquiry.</p>
          </div>
        </div>
      </div>
    `;
    elements.chatFollowupsBar.style.display = 'none';
  });

  // Upload Modal Handlers
  elements.btnOpenUpload.addEventListener('click', () => {
    elements.modalUpload.style.display = 'flex';
    elements.uploadStatusMsg.textContent = '';
  });

  elements.btnCloseUpload.addEventListener('click', () => {
    elements.modalUpload.style.display = 'none';
  });

  elements.csvDropZone.addEventListener('click', () => {
    elements.csvFileInput.click();
  });

  elements.csvFileInput.addEventListener('change', (e) => {
    if (e.target.files.length) {
      handleCsvUpload(e.target.files[0]);
    }
  });

  // Drag and drop for upload
  ['dragenter', 'dragover'].forEach(eventName => {
    elements.csvDropZone.addEventListener(eventName, (e) => {
      e.preventDefault();
      elements.csvDropZone.classList.add('dragover');
    });
  });

  ['dragleave', 'drop'].forEach(eventName => {
    elements.csvDropZone.addEventListener(eventName, (e) => {
      e.preventDefault();
      elements.csvDropZone.classList.remove('dragover');
    });
  });

  elements.csvDropZone.addEventListener('drop', (e) => {
    const dt = e.dataTransfer;
    if (dt && dt.files.length) {
      handleCsvUpload(dt.files[0]);
    }
  });
}

// -----------------------------------------------------------------------------
// App Initialization
// -----------------------------------------------------------------------------
document.addEventListener('DOMContentLoaded', () => {
  applyTheme(state.theme);
  setupEventListeners();
  initFilters();
  fetchAnalytics();
});
