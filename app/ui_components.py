import streamlit as st
import html as html_lib
import re
from app.analytics import format_currency, format_number
from app.visualizations import (
    plot_revenue_by_city, plot_orders_trend, plot_persona_dist,
    plot_delivery_vs_sat, plot_churn_by_persona, plot_cat_revenue
)

def inject_enterprise_css(theme):
    if theme == "Light":
        bg_color = "#F8FAFC"
        sidebar_bg = "#FFFFFF"
        sidebar_border = "#E2E8F0"
        text_color = "#0F172A"
        subtext_color = "#475569"
        card_bg = "#FFFFFF"
        border_color = "#E2E8F0"
        shadow_card = "0 1px 3px rgba(15, 23, 42, 0.06), 0 6px 16px -2px rgba(15, 23, 42, 0.04)"
        shadow_hover = "0 4px 20px -2px rgba(15, 23, 42, 0.10)"
        user_bubble = "#F1F5F9"
        assistant_bubble = "#FFFFFF"
        kpi_value_color = "#0F172A"
        header_color = "#0F172A"
        chat_input_bg = "#FFFFFF"
        chat_border = "#CBD5E1"
        accent_button = "#F8FAFC"
        accent_button_hover = "#F1F5F9"
        button_text = "#0F172A"
        primary_btn_bg = "#0F172A"
        primary_btn_text = "#FFFFFF"
        alert_text = "#0F172A"
        section_hdr_bg = "#F1F5F9"
        section_hdr_text = "#0F172A"
        badge_num_bg = "#2563EB"
        badge_num_text = "#FFFFFF"
        bullet_dot_color = "#2563EB"
    else: # Dark (Alpine Twilight)
        bg_color = "#090F15"
        sidebar_bg = "#0D141C"
        sidebar_border = "rgba(211, 209, 206, 0.12)"
        text_color = "#F1F5F9"
        subtext_color = "#94A3B8"
        card_bg = "#121A24"
        border_color = "rgba(211, 209, 206, 0.12)"
        shadow_card = "0 4px 24px rgba(0, 0, 0, 0.45)"
        shadow_hover = "0 8px 32px rgba(0, 0, 0, 0.65)"
        user_bubble = "#182330"
        assistant_bubble = "#121A24"
        kpi_value_color = "#F8FAFC"
        header_color = "#F8FAFC"
        chat_input_bg = "#121A24"
        chat_border = "#2A3848"
        accent_button = "#18222E"
        accent_button_hover = "#233140"
        button_text = "#F1F5F9"
        primary_btn_bg = "#E2E8F0"
        primary_btn_text = "#090F15"
        alert_text = "#F1F5F9"
        section_hdr_bg = "#1A2533"
        section_hdr_text = "#F8FAFC"
        badge_num_bg = "#38BDF8"
        badge_num_text = "#090F15"
        bullet_dot_color = "#38BDF8"

    st.markdown(f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700&family=Newsreader:wght@600&display=swap');
        
        /* Global Reset & Body Typography */
        html, body, .stApp {{ 
            font-family: 'Manrope', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important; 
            color: {text_color} !important; 
            background-color: {bg_color} !important; 
        }}
        
        /* Universal Typography Overrides */
        h1, h2, h3, h4, h5, h6 {{
            color: {header_color} !important;
            font-family: 'Manrope', sans-serif !important;
        }}
        
        /* Strict Protection for Streamlit Material Symbols / Icons */
        [data-testid="stIconMaterial"],
        .material-symbols-rounded,
        .material-symbols-outlined,
        .material-icons,
        span[data-testid="stIconMaterial"] {{
            font-family: 'Material Symbols Rounded', 'Material Icons', sans-serif !important;
            font-feature-settings: 'liga' 1 !important;
            -webkit-font-feature-settings: 'liga' 1 !important;
            display: inline-block !important;
        }}
        
        /* Clean Sidebar Layout */
        [data-testid="stSidebarCollapseButton"], 
        [data-testid="collapsedControl"] {{
            display: none !important;
        }}
        
        .block-container {{ 
            padding-top: 1.5rem !important; 
            padding-bottom: 3rem !important;
            max-width: 1200px !important;
        }}
        [data-testid="stHeader"] {{ 
            background-color: transparent !important; 
        }}
        
        /* Sidebar Styling & Strict High Color Contrast */
        [data-testid="stSidebar"] {{ 
            background-color: {sidebar_bg} !important; 
            border-right: 1px solid {sidebar_border} !important; 
        }}
        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] *,
        [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3,
        [data-testid="stSidebar"] label,
        [data-testid="stSidebar"] span,
        [data-testid="stSidebar"] p {{ 
            color: {text_color} !important; 
            font-family: 'Manrope', sans-serif !important;
        }}
        [data-testid="stSidebar"] .stCaption,
        [data-testid="stSidebar"] .stCaption * {{
            color: {subtext_color} !important;
            opacity: 0.95 !important;
            font-size: 0.82rem !important;
        }}
        
        /* Form Inputs & Dropdowns */
        div[data-baseweb="select"] > div {{
            background-color: {card_bg} !important;
            border: 1px solid {border_color} !important;
            color: {text_color} !important;
            border-radius: 10px;
            box-shadow: 0 1px 2px rgba(0,0,0,0.06);
            font-family: 'Manrope', sans-serif !important;
        }}
        div[data-baseweb="select"] * {{
            color: {text_color} !important;
        }}
        div[data-baseweb="popover"] ul,
        div[data-baseweb="popover"] li {{
            background-color: {card_bg} !important;
            color: {text_color} !important;
        }}
        
        /* Dashboard Headers */
        .dashboard-header-title {{
            font-family: 'Newsreader', Georgia, 'Times New Roman', serif !important;
            font-size: 2.35rem !important;
            font-weight: 600 !important;
            color: {header_color} !important;
            letter-spacing: -0.01em;
            margin: 0;
            padding: 0;
        }}
        .dashboard-header-subtitle {{
            font-family: 'Manrope', sans-serif !important;
            font-size: 0.95rem !important;
            color: {subtext_color} !important;
            margin-top: 0.2rem;
            font-weight: 500;
        }}
        
        /* KPI Cards */
        .kpi-card {{ 
            background: {card_bg} !important; 
            padding: 18px 20px; 
            border-radius: 14px; 
            text-align: left; 
            border: 1px solid {border_color} !important;
            box-shadow: {shadow_card};
            transition: transform 0.15s ease, box-shadow 0.15s ease;
        }}
        .kpi-card:hover {{
            box-shadow: {shadow_hover};
            transform: translateY(-2px);
        }}
        .kpi-label {{ 
            font-family: 'Manrope', sans-serif !important;
            font-size: 11px !important; 
            font-weight: 600 !important; 
            color: {subtext_color} !important; 
            text-transform: uppercase; 
            letter-spacing: 0.8px; 
            margin-bottom: 6px;
        }}
        .kpi-value {{ 
            font-family: 'Manrope', sans-serif !important;
            font-size: 26px !important; 
            font-weight: 700 !important; 
            color: {kpi_value_color} !important; 
            letter-spacing: -0.5px; 
            margin: 0;
            line-height: 1.1;
        }}
        
        /* Chart Card Containers */
        .chart-card-container {{
            background: {card_bg} !important;
            border: 1px solid {border_color} !important;
            border-radius: 16px;
            padding: 18px 20px;
            box-shadow: {shadow_card};
            margin-bottom: 1rem;
        }}
        .chart-title-text {{
            font-family: 'Newsreader', Georgia, serif !important;
            font-size: 17px !important;
            font-weight: 600 !important;
            color: {header_color} !important;
        }}
        
        /* Buttons Styling */
        div.stButton > button {{
            background-color: {accent_button} !important;
            color: {button_text} !important;
            border: 1px solid {border_color} !important;
            border-radius: 10px !important;
            padding: 0.35rem 0.85rem !important;
            font-size: 12.5px !important;
            font-weight: 600 !important;
            font-family: 'Manrope', sans-serif !important;
            transition: all 0.15s ease !important;
            box-shadow: 0 1px 2px rgba(0,0,0,0.04) !important;
        }}
        div.stButton > button p, 
        div.stButton > button span {{
            color: {button_text} !important;
        }}
        div.stButton > button:hover {{
            background-color: {accent_button_hover} !important;
            border-color: {subtext_color} !important;
            transform: translateY(-1px) !important;
        }}
        div.stButton > button[kind="primary"],
        div.stButton > button[data-testid="baseButton-primary"] {{
            background-color: {primary_btn_bg} !important;
            color: {primary_btn_text} !important;
            border: 1px solid {primary_btn_bg} !important;
            font-weight: 700 !important;
        }}
        div.stButton > button[kind="primary"] p, 
        div.stButton > button[kind="primary"] span,
        div.stButton > button[data-testid="baseButton-primary"] p,
        div.stButton > button[data-testid="baseButton-primary"] span {{
            color: {primary_btn_text} !important;
        }}
        
        /* Chat UI Styling */
        .enterprise-message-container {{ display: flex; margin-bottom: 18px; width: 100%; }}
        .enterprise-message-container.user {{ justify-content: flex-end; }}
        .enterprise-message-container.assistant {{ justify-content: flex-start; }}
        .enterprise-bubble {{ 
            max-width: 88%; 
            padding: 18px 22px; 
            border-radius: 14px; 
            font-size: 14px; 
            line-height: 1.65; 
            color: {text_color}; 
            box-shadow: {shadow_card}; 
            font-family: 'Manrope', sans-serif !important;
        }}
        .enterprise-message-container.user .enterprise-bubble {{ 
            background-color: {user_bubble}; 
            border: 1px solid {border_color};
            border-bottom-right-radius: 4px; 
        }}
        .enterprise-message-container.assistant .enterprise-bubble {{ 
            background-color: {assistant_bubble}; 
            border-bottom-left-radius: 4px; 
            border: 1px solid {border_color}; 
        }}
        
        /* Structured Section Header Inside Bubble */
        .bubble-section-header {{
            background: {section_hdr_bg};
            padding: 6px 12px;
            border-radius: 8px;
            margin-top: 14px;
            margin-bottom: 8px;
            display: inline-block;
            border: 1px solid {border_color};
        }}
        .bubble-section-header:first-child {{
            margin-top: 0;
        }}
        .bubble-section-header h4 {{
            margin: 0 !important;
            padding: 0 !important;
            font-size: 13.5px !important;
            font-weight: 700 !important;
            color: {section_hdr_text} !important;
            display: flex;
            align-items: center;
            gap: 6px;
        }}
        
        /* Pointers & Bullet List Inside Bubble */
        .bubble-pointer-list {{
            margin: 6px 0 10px 0;
            padding-left: 20px;
            list-style-type: none;
        }}
        .bubble-pointer-list li {{
            position: relative;
            padding-left: 14px;
            margin-bottom: 7px;
            line-height: 1.55;
            color: {text_color};
            font-size: 13.5px;
        }}
        .bubble-pointer-list li::before {{
            content: "•";
            position: absolute;
            left: 0;
            color: {bullet_dot_color};
            font-size: 16px;
            line-height: 1;
            font-weight: bold;
        }}
        .bubble-pointer-list li strong {{
            color: {header_color};
            font-weight: 600;
        }}
        
        /* Action Numbered Items Inside Bubble */
        .bubble-action-item {{
            display: flex;
            align-items: flex-start;
            gap: 10px;
            margin-bottom: 8px;
            font-size: 13.5px;
            line-height: 1.55;
        }}
        .bubble-action-item .action-num {{
            background: {badge_num_bg};
            color: {badge_num_text};
            font-size: 11px;
            font-weight: 700;
            padding: 2px 7px;
            border-radius: 6px;
            margin-top: 2px;
            flex-shrink: 0;
        }}
        .bubble-action-item .action-desc {{
            color: {text_color};
        }}
        .bubble-action-item .action-desc strong {{
            color: {header_color};
            font-weight: 600;
        }}
        
        .bubble-paragraph {{
            margin-bottom: 8px;
            font-size: 13.5px;
            line-height: 1.55;
            color: {text_color};
        }}
        .bubble-paragraph strong {{
            color: {header_color};
            font-weight: 600;
        }}
        
        @keyframes pulse-dot {{
            0% {{ opacity: 0.3; transform: scale(0.92); }}
            50% {{ opacity: 1; transform: scale(1.12); }}
            100% {{ opacity: 0.3; transform: scale(0.92); }}
        }}
        .analyzing-pulse {{
            animation: pulse-dot 1.2s ease-in-out infinite;
            display: inline-block;
            font-size: 16px;
        }}
        
        /* Hide streamlit modebar clutter */
        .modebar {{ display: none !important; }}
    </style>
    """, unsafe_allow_html=True)


def render_kpi_card(title, value):
    """
    Renders minimalist, clean KPI cards with bold number and clear metric title.
    """
    return f"""
    <div class='kpi-card'>
        <div class='kpi-label'>{title}</div>
        <div class='kpi-value'>{value}</div>
    </div>
    """

def render_thinking_bubble(text="Analyzing data & synthesizing management insights..."):
    """
    Renders an animated thinking state inside the chat while the response is being analyzed.
    """
    html_content = f"""
    <div class='enterprise-message-container assistant'>
        <div class='enterprise-bubble' style='display: flex; align-items: center; gap: 10px; font-style: italic; opacity: 0.85;'>
            <span class='analyzing-pulse'>✨</span>
            <span>{text}</span>
        </div>
    </div>
    """
    st.markdown(html_content, unsafe_allow_html=True)

def format_structured_bubble_html(raw_text: str) -> str:
    """
    Transforms AI response text into structured, high-contrast pointer cards with
    clean bullet points, section badge headers, and numbered action items.
    """
    text = str(raw_text).strip()
    # Normalize markdown headers that might be joined without double newlines
    text = re.sub(r'([^\n])(###\s*[\U00010000-\U0010ffff\w])', r'\1\n\n\2', text)
    text = re.sub(r'([^\n])(📌\s*)', r'\1\n\n### 📌 ', text)
    text = re.sub(r'([^\n])(📊\s*)', r'\1\n\n### 📊 ', text)
    text = re.sub(r'([^\n])(🔎\s*)', r'\1\n\n### 🔎 ', text)
    text = re.sub(r'([^\n])(🎯\s*)', r'\1\n\n### 🎯 ', text)
    text = re.sub(r'([^\n])(⚠️\s*)', r'\1\n\n### ⚠️ ', text)
    
    # Normalize bullet points joined without newlines
    text = re.sub(r'([^\n])(\*\s+[A-Z0-9\(\[])', r'\1\n* \2', text)
    text = re.sub(r'([^\n])(•\s+[A-Z0-9\(\[])', r'\1\n• \2', text)
    text = re.sub(r'([^\n])(\d+\.\s+[A-Z0-9\(\[])', r'\1\n\2', text)
    
    lines = text.split('\n')
    out = []
    in_ul = False
    
    for line in lines:
        l = line.strip()
        if not l:
            if in_ul:
                out.append('</ul>')
                in_ul = False
            continue
            
        # Section Header (### Title or Icon Title)
        if l.startswith('###') or any(l.startswith(h) for h in ['📌', '📊', '🔎', '🎯', '⚠️']):
            if in_ul:
                out.append('</ul>')
                in_ul = False
            title = l.lstrip('#').strip()
            out.append(f"<div class='bubble-section-header'><h4>{html_lib.escape(title)}</h4></div>")
            continue
            
        # Bullet list item (* or - or •)
        if l.startswith(('* ', '- ', '• ')):
            if not in_ul:
                out.append("<ul class='bubble-pointer-list'>")
                in_ul = True
            content = l[2:].strip()
            content = re.sub(r'^[\*\-•]\s+', '', content)
            escaped = html_lib.escape(content)
            escaped = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', escaped)
            out.append(f"<li>{escaped}</li>")
            continue
            
        # Numbered Action Item (1. Action)
        num_m = re.match(r'^(\d+)\.\s+(.*)$', l)
        if num_m:
            if in_ul:
                out.append('</ul>')
                in_ul = False
            num, content = num_m.group(1), num_m.group(2)
            escaped = html_lib.escape(content)
            escaped = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', escaped)
            out.append(f"<div class='bubble-action-item'><span class='action-num'>{num}</span><div class='action-desc'>{escaped}</div></div>")
            continue
            
        # Regular Paragraph
        if in_ul:
            out.append('</ul>')
            in_ul = False
        escaped = html_lib.escape(l)
        escaped = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', escaped)
        out.append(f"<p class='bubble-paragraph'>{escaped}</p>")
        
    if in_ul:
        out.append('</ul>')
        
    return "".join(out)

def render_message_bubble(role, content_text):
    if role == "user":
        escaped = html_lib.escape(str(content_text))
        html_bubble = f"<div class='enterprise-message-container user'><div class='enterprise-bubble'>{escaped}</div></div>"
    else:
        structured_content = format_structured_bubble_html(content_text)
        html_bubble = f"<div class='enterprise-message-container assistant'><div class='enterprise-bubble'>{structured_content}</div></div>"
    st.markdown(html_bubble, unsafe_allow_html=True)

def render_kpi_row(kpis):
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.markdown(render_kpi_card("Total Revenue", format_currency(kpis.get('total_revenue', 0))), unsafe_allow_html=True)
    with c2: st.markdown(render_kpi_card("Total Orders", format_number(kpis.get('total_orders', 0))), unsafe_allow_html=True)
    with c3: st.markdown(render_kpi_card("Avg Order Value", format_currency(kpis.get('avg_order_value', 0))), unsafe_allow_html=True)
    with c4: st.markdown(render_kpi_card("Active Customers", format_number(kpis.get('active_customers', 0))), unsafe_allow_html=True)

def render_kpi_row_2(kpis):
    c1, c2, c3 = st.columns(3)
    with c1: st.markdown(render_kpi_card("Repeat Purchase Rate", f"{kpis.get('repeat_purchase_rate', 0):.1f}%"), unsafe_allow_html=True)
    with c2: st.markdown(render_kpi_card("Avg Churn Risk", f"{kpis.get('churn_risk_avg', 0):.1f}%"), unsafe_allow_html=True)
    csat = kpis.get('customer_satisfaction', 0.0)
    with c3: st.markdown(render_kpi_card("Customer Satisfaction", f"{csat:.1f} / 5"), unsafe_allow_html=True)

def handle_explain_with_ai(prompt):
    st.session_state.pending_ai_query = prompt
    st.session_state.current_page = "🤖 Chatbot"
    st.rerun()

def render_chart_section(title, fig, button_text, explain_prompt, key):
    hc, bc = st.columns([0.72, 0.28])
    with hc:
        st.markdown(f"<div class='chart-title-text' style='padding-top: 6px;'>{title}</div>", unsafe_allow_html=True)
    with bc:
        if st.button(button_text, key=key, use_container_width=True): 
            handle_explain_with_ai(explain_prompt)
    if fig: 
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

def render_executive_overview(kpis, briefing, charts_data):
    col_hdr, col_btns = st.columns([0.55, 0.45])
    with col_hdr:
        st.markdown("""
            <div style="margin-bottom: 0.6rem; padding-top: 0.2rem;">
                <h1 class="dashboard-header-title">Executive Analytics</h1>
                <p class="dashboard-header-subtitle">Real-time Quick-Commerce Performance Overview</p>
            </div>
        """, unsafe_allow_html=True)
    with col_btns:
        st.markdown("<div style='height: 4px;'></div>", unsafe_allow_html=True)
        current_tr = st.session_state.get("time_filter_type", "Total")
        b1, b2, b3 = st.columns(3)
        with b1:
            if st.button("Month", use_container_width=True, type="primary" if current_tr == "Month" else "secondary", key="btn_month"):
                st.session_state.time_filter_type = "Month"
                st.rerun()
        with b2:
            if st.button("Quarter", use_container_width=True, type="primary" if current_tr == "Quarter" else "secondary", key="btn_quarter"):
                st.session_state.time_filter_type = "Quarter"
                st.rerun()
        with b3:
            if st.button("Total", use_container_width=True, type="primary" if current_tr == "Total" else "secondary", key="btn_total"):
                st.session_state.time_filter_type = "Total"
                st.rerun()
                
        if current_tr == "Month":
            all_months = [
                "January 2025", "February 2025", "March 2025", "April 2025",
                "May 2025", "June 2025", "July 2025", "August 2025",
                "September 2025", "October 2025", "November 2025", "December 2025", "January 2026"
            ]
            default_m = st.session_state.get("selected_month", "December 2025")
            default_idx = all_months.index(default_m) if default_m in all_months else 11
            chosen_m = st.selectbox("Select Month", all_months, index=default_idx, key="month_selector", label_visibility="collapsed")
            if chosen_m != st.session_state.get("selected_month"):
                st.session_state.selected_month = chosen_m
                st.rerun()
                
        elif current_tr == "Quarter":
            all_quarters = ["Q1 2025", "Q2 2025", "Q3 2025", "Q4 2025", "Q1 2026"]
            default_q = st.session_state.get("selected_quarter", "Q4 2025")
            default_idx = all_quarters.index(default_q) if default_q in all_quarters else 3
            chosen_q = st.selectbox("Select Quarter", all_quarters, index=default_idx, key="quarter_selector", label_visibility="collapsed")
            if chosen_q != st.session_state.get("selected_quarter"):
                st.session_state.selected_quarter = chosen_q
                st.rerun()
    
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
    
    # Charts Grid
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
