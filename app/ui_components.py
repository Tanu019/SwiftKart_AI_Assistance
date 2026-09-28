import streamlit as st
from app.analytics import format_currency, format_number
from app.visualizations import (
    plot_revenue_by_city, plot_orders_trend, plot_persona_dist,
    plot_delivery_vs_sat, plot_churn_by_persona, plot_cat_revenue
)

def inject_enterprise_css(theme):
    if theme == "Light":
        bg_color = "#f0f2f5"
        sidebar_bg = "#ffffff"
        text_color = "#0f172a"
        subtext_color = "#64748b"
        card_bg = "#ffffff"
        border_color = "#e2e8f0"
        shadow_card = "0 1px 3px rgba(15, 23, 42, 0.05), 0 10px 15px -5px rgba(15, 23, 42, 0.03)"
        shadow_hover = "0 4px 20px -2px rgba(15, 23, 42, 0.08)"
        user_bubble = "#e2e8f0"
        assistant_bubble = "#ffffff"
        kpi_value_color = "#0f172a"
        chat_input_bg = "#ffffff"
        chat_border = "#cbd5e1"
        accent_button = "#f1f5f9"
        accent_button_hover = "#e2e8f0"
        button_text = "#1e293b"
        sparkline_color = "#2b5c7a"
    else: # Dark
        bg_color = "#0b0f19"
        sidebar_bg = "#111827"
        text_color = "#f8fafc"
        subtext_color = "#94a3b8"
        card_bg = "#161f30"
        border_color = "#243247"
        shadow_card = "0 4px 20px rgba(0, 0, 0, 0.4)"
        shadow_hover = "0 8px 30px rgba(0, 0, 0, 0.6)"
        user_bubble = "#1e293b"
        assistant_bubble = "#161f30"
        kpi_value_color = "#f8fafc"
        chat_input_bg = "#161f30"
        chat_border = "#334155"
        accent_button = "#1e293b"
        accent_button_hover = "#334155"
        button_text = "#f8fafc"
        sparkline_color = "#38bdf8"

    st.markdown(f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        
        /* Global Reset */
        html, body, [class*="css"] {{ 
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important; 
            color: {text_color} !important; 
        }}
        
        /* App Canvas */
        .stApp {{ 
            background-color: {bg_color}; 
        }}
        .block-container {{ 
            padding-top: 1.5rem !important; 
            padding-bottom: 3rem !important;
            max-width: 1200px !important;
        }}
        [data-testid="stHeader"] {{ 
            background-color: transparent !important; 
        }}
        
        /* Sidebar Clean Styling */
        [data-testid="stSidebar"] {{ 
            background-color: {sidebar_bg} !important; 
            border-right: 1px solid {border_color}; 
        }}
        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p, 
        [data-testid="stSidebar"] label {{ 
            color: {text_color} !important; 
        }}
        
        /* Form Inputs & Dropdowns */
        div[data-baseweb="select"] > div {{
            background-color: {card_bg} !important;
            border: 1px solid {border_color} !important;
            color: {text_color} !important;
            border-radius: 10px;
            box-shadow: 0 1px 2px rgba(0,0,0,0.03);
        }}
        
        /* Dashboard Headers */
        .dashboard-header-title {{
            font-size: 2.2rem;
            font-weight: 700;
            color: {kpi_value_color};
            letter-spacing: -0.02em;
            margin: 0;
            padding: 0;
        }}
        .dashboard-header-subtitle {{
            font-size: 0.95rem;
            color: {subtext_color};
            margin-top: 0.2rem;
            font-weight: 400;
        }}
        
        /* Top Navigation Filter Pills */
        .filter-pill {{
            background: {accent_button};
            color: {button_text};
            padding: 6px 14px;
            border-radius: 20px;
            font-size: 12.5px;
            font-weight: 500;
            border: 1px solid {border_color};
            display: inline-block;
        }}
        
        /* KPI Cards (Clean SaaS Design with Sparkline) */
        .kpi-card {{ 
            background: {card_bg}; 
            padding: 18px 20px 14px 20px; 
            border-radius: 14px; 
            text-align: left; 
            border: 1px solid {border_color};
            box-shadow: {shadow_card};
            transition: all 0.2s ease;
            position: relative;
            overflow: hidden;
        }}
        .kpi-card:hover {{
            box-shadow: {shadow_hover};
            transform: translateY(-2px);
        }}
        .kpi-label {{ 
            font-size: 11.5px; 
            font-weight: 600; 
            color: {subtext_color}; 
            text-transform: uppercase; 
            letter-spacing: 0.6px; 
            margin-bottom: 6px;
        }}
        .kpi-value {{ 
            font-size: 26px; 
            font-weight: 700; 
            color: {kpi_value_color}; 
            letter-spacing: -0.5px; 
            margin: 2px 0 8px 0;
            line-height: 1.1;
        }}
        .kpi-sparkline {{
            margin-top: 6px;
            height: 24px;
            width: 100%;
        }}
        
        /* Chart Card Containers (Matching Image 2) */
        .chart-card-container {{
            background: {card_bg};
            border: 1px solid {border_color};
            border-radius: 16px;
            padding: 18px 20px;
            box-shadow: {shadow_card};
            margin-bottom: 1rem;
        }}
        .chart-title-text {{
            font-size: 15.5px;
            font-weight: 600;
            color: {kpi_value_color};
            letter-spacing: -0.01em;
        }}
        
        /* Clean Pill Action Buttons */
        div.stButton > button {{
            background: {accent_button} !important;
            color: {button_text} !important;
            border: 1px solid {border_color} !important;
            border-radius: 20px !important;
            padding: 0.35rem 0.85rem !important;
            font-size: 12px !important;
            font-weight: 500 !important;
            transition: all 0.2s ease !important;
            box-shadow: 0 1px 2px rgba(0,0,0,0.03) !important;
        }}
        div.stButton > button:hover {{
            background: {accent_button_hover} !important;
            border-color: #94a3b8 !important;
            transform: translateY(-1px) !important;
        }}
        
        /* Chat UI Styling */
        .enterprise-message-container {{ display: flex; margin-bottom: 16px; width: 100%; }}
        .enterprise-message-container.user {{ justify-content: flex-end; }}
        .enterprise-message-container.assistant {{ justify-content: flex-start; }}
        .enterprise-bubble {{ 
            max-width: 82%; 
            padding: 16px 20px; 
            border-radius: 14px; 
            font-size: 14.5px; 
            line-height: 1.6; 
            color: {text_color}; 
            box-shadow: {shadow_card}; 
        }}
        .enterprise-message-container.user .enterprise-bubble {{ 
            background-color: {user_bubble}; 
            border-bottom-right-radius: 4px; 
        }}
        .enterprise-message-container.assistant .enterprise-bubble {{ 
            background-color: {assistant_bubble}; 
            border-bottom-left-radius: 4px; 
            border: 1px solid {border_color}; 
        }}
        .enterprise-bubble h3 {{ 
            margin-top: 0; 
            margin-bottom: 8px; 
            font-size: 16px; 
            color: {kpi_value_color}; 
            font-weight: 600; 
        }}
        
        /* Hide streamlit modebar clutter */
        .modebar {{ display: none !important; }}
    </style>
    """, unsafe_allow_html=True)


def render_kpi_card(title, value, sparkline_type="up"):
    """
    Renders clean KPI cards with embedded smooth SVG sparklines (matching Image 2).
    """
    if sparkline_type == "up":
        path = "M 0 20 Q 20 24, 35 14 T 65 16 T 95 6 T 120 4"
        stroke = "#2b5c7a"
    elif sparkline_type == "down":
        path = "M 0 6 Q 25 8, 45 16 T 80 12 T 100 22 T 120 24"
        stroke = "#0284c7"
    elif sparkline_type == "pulse":
        path = "M 0 16 Q 15 6, 30 20 T 60 10 T 90 18 T 120 8"
        stroke = "#3b82f6"
    else:
        path = "M 0 18 Q 20 8, 45 20 T 80 8 T 120 12"
        stroke = "#64748b"

    return f"""
    <div class='kpi-card'>
        <div class='kpi-label'>{title}</div>
        <div class='kpi-value'>{value}</div>
        <div class='kpi-sparkline'>
            <svg width="100%" height="24" viewBox="0 0 120 26" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="{path}" stroke="{stroke}" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
        </div>
    </div>
    """

def render_kpi_row(kpis):
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.markdown(render_kpi_card("Total Revenue", format_currency(kpis.get('total_revenue', 0)), "up"), unsafe_allow_html=True)
    with c2: st.markdown(render_kpi_card("Total Orders", format_number(kpis.get('total_orders', 0)), "pulse"), unsafe_allow_html=True)
    with c3: st.markdown(render_kpi_card("Avg Order Value", format_currency(kpis.get('avg_order_value', 0)), "down"), unsafe_allow_html=True)
    with c4: st.markdown(render_kpi_card("Active Customers", format_number(kpis.get('active_customers', 0)), "wave"), unsafe_allow_html=True)

def render_kpi_row_2(kpis):
    c1, c2, c3 = st.columns(3)
    with c1: st.markdown(render_kpi_card("Repeat Purchase Rate", f"{kpis.get('repeat_purchase_rate', 0):.1f}%", "up"), unsafe_allow_html=True)
    with c2: st.markdown(render_kpi_card("Avg Churn Risk", f"{kpis.get('churn_risk_avg', 0):.1f}%", "down"), unsafe_allow_html=True)
    csat = kpis.get('customer_satisfaction', 0.0)
    with c3: st.markdown(render_kpi_card("Customer Satisfaction", f"{csat:.1f} / 5", "pulse"), unsafe_allow_html=True)

def handle_explain_with_ai(prompt):
    st.session_state.pending_ai_query = prompt
    st.session_state.current_page = "🤖 Chatbot"
    st.rerun()

def render_chart_section(title, fig, button_text, explain_prompt, key):
    # Enclose chart inside clean white card container
    hc, bc = st.columns([0.72, 0.28])
    with hc:
        st.markdown(f"<div class='chart-title-text' style='padding-top: 6px;'>{title}</div>", unsafe_allow_html=True)
    with bc:
        if st.button(button_text, key=key, use_container_width=True): 
            handle_explain_with_ai(explain_prompt)
    if fig: 
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

def render_executive_overview(kpis, briefing, charts_data):
    # Top Dashboard Header (Clean Corporate Look matching Image 2)
    st.markdown("""
        <div style="display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 1.4rem; padding-top: 0.5rem;">
            <div>
                <h1 class="dashboard-header-title">Executive Analytics</h1>
                <p class="dashboard-header-subtitle">Real-time Quick-Commerce Performance Overview</p>
            </div>
            <div style="display: flex; gap: 8px;">
                <span class="filter-pill">Month</span>
                <span class="filter-pill">Quarter</span>
                <span class="filter-pill" style="background:#2b5c7a; color:#ffffff; border-color:#2b5c7a;">Total</span>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # KPI Rows
    render_kpi_row(kpis)
    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
    render_kpi_row_2(kpis)
    
    # Management Briefing Alerts
    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        st.error(f"🔴 **Needs Attention**: {briefing['needs_attention']}")
        st.success(f"🟢 **Positive**: {briefing['positive']}")
    with c2:
        st.warning(f"🟡 **Watch**: {briefing['watch']}")
        st.info(f"🔵 **Opportunity**: {briefing['priority']}")

    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)
    
    # Charts Grid (Matching Image 2 Layout)
    c1, c2 = st.columns(2)
    with c1:
        render_chart_section("Revenue by City", plot_revenue_by_city(charts_data.get("revenue_by_city")), "✨ Explain with AI", "Why is revenue distributed like this across cities?", "exp_rev_city")
            
    with c2:
        render_chart_section("Orders Over Time", plot_orders_trend(charts_data.get("orders_trend")), "✨ Explain with AI", "What is causing the current trend in orders over time?", "exp_ord_trend")

    c3, c4 = st.columns(2)
    with c3:
        render_chart_section("Customer Personas", plot_persona_dist(charts_data.get("persona_dist")), "✨ Explain with AI", "Which customer persona is the most valuable and why?", "exp_personas")
    with c4:
        render_chart_section("Avg Churn Risk by Persona", plot_churn_by_persona(charts_data.get("churn_by_persona")), "✨ Explain with AI", "Why does this persona have a higher churn risk?", "exp_churn_persona")
        
    c5, c6 = st.columns(2)
    with c5:
        render_chart_section("Delivery Time vs Satisfaction", plot_delivery_vs_sat(charts_data.get("delivery_vs_sat")), "✨ Explain with AI", "Does delivery time impact customer satisfaction in our data?", "exp_delivery_sat")
    with c6:
        render_chart_section("Category Revenue", plot_cat_revenue(charts_data.get("cat_revenue")), "✨ Explain with AI", "Which product category is driving the most revenue?", "exp_cat_rev")


# --- Chat Components ---

def initialize_chat_history():
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": "Hello! I am your AI Management Analyst. What would you like to explore?", "type": "text"}]
    if "follow_ups" not in st.session_state:
        st.session_state.follow_ups = [
            "Which city has the highest revenue?",
            "Which customer segment has the highest churn risk?",
            "Which products have high revenue but low margins?",
            "Does delivery time impact customer satisfaction?"
        ]

def render_message_bubble(role, content_text):
    if role == "user":
        html = f"<div class='enterprise-message-container user'><div class='enterprise-bubble'>{content_text}</div></div>"
    else:
        import html as html_lib
        import re
        safe_content = html_lib.escape(content_text).replace('\n', '<br>')
        safe_content = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', safe_content)
        safe_content = re.sub(r'### (.*?)(<br>|$)', r'<h3>\1</h3>\2', safe_content)
        html = f"<div class='enterprise-message-container assistant'><div class='enterprise-bubble'>{safe_content}</div></div>"
    st.markdown(html, unsafe_allow_html=True)

def render_follow_ups():
    if st.session_state.follow_ups:
        st.markdown("<div style='font-size:14px; font-weight:600; margin-bottom:8px;'>Explore Further</div>", unsafe_allow_html=True)
        cols = st.columns(len(st.session_state.follow_ups))
        for idx, q in enumerate(st.session_state.follow_ups):
            with cols[idx]:
                if st.button(q, key=f"fu_{idx}", use_container_width=True):
                    st.session_state.follow_ups = []
                    return q
    return None

def render_chat_history():
    for message in st.session_state.messages:
        msg_type = message.get("type", "text")
        if msg_type == "text":
            render_message_bubble(message["role"], message["content"])
        elif msg_type == "table":
            render_message_bubble(message["role"], "Here is the data table you requested:")
            st.dataframe(message["content"], use_container_width=True, hide_index=True)
        elif msg_type == "chart":
            render_message_bubble(message["role"], "Here is the visualization:")
            st.plotly_chart(message["content"], use_container_width=True, config={'displayModeBar': False})

def render_sidebar_data_section(dataframes):
    """
    Renders the active source data files used by the platform,
    as well as an uploaded documents section in the left panel.
    """
    st.sidebar.markdown("---")
    
    # 1. Source Data Files Section
    st.sidebar.markdown("### 📁 Data Source Files")
    with st.sidebar.expander("📊 Platform Datasets", expanded=True):
        source_meta = [
            ("customers.csv", "👥", "customers", "1.1 MB"),
            ("orders.csv", "📦", "orders", "14.9 MB"),
            ("order_items.csv", "🛒", "order_items", "18.1 MB"),
            ("products.csv", "🏷️", "products", "160 KB"),
        ]
        for filename, icon, key, size in source_meta:
            if key in dataframes and not dataframes[key].empty:
                count = len(dataframes[key])
                st.markdown(f"""
                <div style="padding: 7px 10px; margin-bottom: 6px; border-radius: 8px; background: rgba(128,128,128,0.06); font-size: 0.85rem; display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <strong>{icon} {filename}</strong><br>
                        <span style="opacity: 0.7; font-size: 0.75rem;">{count:,} rows • {size}</span>
                    </div>
                    <span style="color: #22c55e; font-size: 0.75rem; font-weight: 600;">● Active</span>
                </div>
                """, unsafe_allow_html=True)

    # 2. Document Upload Section
    st.sidebar.markdown("### 📤 Uploaded Documents")
    uploaded_files = st.sidebar.file_uploader(
        "Upload CSV / Excel to analyze",
        type=["csv", "xlsx", "xls", "txt"],
        accept_multiple_files=True,
        key="sidebar_doc_uploader"
    )
    
    uploaded_dfs = {}
    if uploaded_files:
        import re
        import pandas as pd
        for f in uploaded_files:
            try:
                table_name = f.name.rsplit('.', 1)[0].lower()
                table_name = re.sub(r'[^a-z0-9_]', '_', table_name)
                if f.name.endswith('.csv') or f.name.endswith('.txt'):
                    df = pd.read_csv(f)
                else:
                    df = pd.read_excel(f)
                uploaded_dfs[table_name] = df
                st.sidebar.success(f"✅ **{f.name}** ({df.shape[0]:,} rows)")
            except Exception as e:
                st.sidebar.error(f"Error reading {f.name}: {e}")
                
    return uploaded_dfs

def render_data_used(dataframes):
    """Backwards-compatible wrapper."""
    return render_sidebar_data_section(dataframes)


