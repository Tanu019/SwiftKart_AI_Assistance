import streamlit as st
import html as html_lib
import re
import pandas as pd
from app.analytics import format_currency, format_number
from app.visualizations import (
    plot_revenue_by_city, plot_orders_trend, plot_persona_dist,
    plot_delivery_vs_sat, plot_churn_by_persona, plot_cat_revenue
)

def inject_enterprise_css(theme):
    if theme == "Light":
        bg_color = "#F8FAFC"
        bg_aura = "radial-gradient(ellipse 80% 50% at 50% -10%, rgba(99, 102, 241, 0.10), rgba(248, 250, 252, 0))"
        sidebar_bg = "rgba(255, 255, 255, 0.95)"
        sidebar_border = "rgba(226, 232, 240, 0.9)"
        text_color = "#0F172A"
        subtext_color = "#64748B"
        card_bg = "rgba(255, 255, 255, 0.85)"
        card_border = "rgba(226, 232, 240, 0.9)"
        shadow_card = "0 4px 20px -2px rgba(99, 102, 241, 0.08), 0 2px 6px -1px rgba(15, 23, 42, 0.04)"
        shadow_hover = "0 10px 30px -4px rgba(99, 102, 241, 0.18), 0 4px 12px -2px rgba(15, 23, 42, 0.08)"
        user_bubble = "linear-gradient(135deg, #4F46E5 0%, #6366F1 100%)"
        user_text = "#FFFFFF"
        assistant_bubble = "rgba(255, 255, 255, 0.95)"
        assistant_border = "rgba(99, 102, 241, 0.2)"
        header_color = "#0F172A"
        accent_button = "#F1F5F9"
        accent_button_hover = "#E2E8F0"
        button_text = "#0F172A"
        primary_btn_bg = "linear-gradient(135deg, #4F46E5 0%, #6366F1 100%)"
        primary_btn_text = "#FFFFFF"
        section_hdr_bg = "rgba(99, 102, 241, 0.08)"
        section_hdr_text = "#4338CA"
        badge_num_bg = "#4F46E5"
        badge_num_text = "#FFFFFF"
        bullet_dot_color = "#6366F1"
        glass_border = "rgba(226, 232, 240, 0.8)"
    else: # Dark (Modern Obsidian & Electric Indigo Glassmorphism)
        bg_color = "#080C14"
        bg_aura = "radial-gradient(ellipse 90% 60% at 50% -15%, rgba(99, 102, 241, 0.16) 0%, rgba(139, 92, 246, 0.06) 45%, rgba(8, 12, 20, 0) 80%)"
        sidebar_bg = "rgba(11, 15, 25, 0.96)"
        sidebar_border = "rgba(255, 255, 255, 0.07)"
        text_color = "#F8FAFC"
        subtext_color = "#94A3B8"
        card_bg = "rgba(15, 23, 42, 0.65)"
        card_border = "rgba(255, 255, 255, 0.09)"
        shadow_card = "0 8px 32px 0 rgba(0, 0, 0, 0.45), inset 0 1px 0 rgba(255, 255, 255, 0.06)"
        shadow_hover = "0 14px 40px -4px rgba(99, 102, 241, 0.25), inset 0 1px 0 rgba(255, 255, 255, 0.15)"
        user_bubble = "linear-gradient(135deg, #4338CA 0%, #6366F1 100%)"
        user_text = "#FFFFFF"
        assistant_bubble = "rgba(15, 23, 42, 0.75)"
        assistant_border = "rgba(99, 102, 241, 0.3)"
        header_color = "#F8FAFC"
        accent_button = "rgba(30, 41, 59, 0.7)"
        accent_button_hover = "rgba(51, 65, 85, 0.9)"
        button_text = "#F8FAFC"
        primary_btn_bg = "linear-gradient(135deg, #6366F1 0%, #8B5CF6 100%)"
        primary_btn_text = "#FFFFFF"
        section_hdr_bg = "rgba(99, 102, 241, 0.16)"
        section_hdr_text = "#A5B4FC"
        badge_num_bg = "#6366F1"
        badge_num_text = "#FFFFFF"
        bullet_dot_color = "#818CF8"
        glass_border = "rgba(255, 255, 255, 0.10)"

    st.markdown(f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=Space+Grotesk:wght@600;700&display=swap');
        @import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200');
        @import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200');
        
        /* Global Reset & Body Typography */
        html, body, .stApp {{ 
            font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important; 
            color: {text_color} !important; 
            background-color: {bg_color} !important; 
            background-image: {bg_aura} !important;
            background-attachment: fixed !important;
            letter-spacing: -0.01em;
        }}
        
        /* Universal Typography Overrides */
        h1, h2, h3, h4, h5, h6 {{
            color: {header_color} !important;
            font-family: 'Space Grotesk', 'Plus Jakarta Sans', sans-serif !important;
            letter-spacing: -0.02em;
        }}
        
        /* Clean Container Spacing */
        .block-container {{ 
            padding-top: 1.8rem !important; 
            padding-bottom: 3.5rem !important;
            max-width: 1260px !important;
        }}
        [data-testid="stHeader"] {{ 
            background-color: transparent !important; 
        }}
        
        /* Sidebar Styling with Glassmorphism */
        [data-testid="stSidebar"] {{ 
            background-color: {sidebar_bg} !important; 
            backdrop-filter: blur(20px) !important;
            -webkit-backdrop-filter: blur(20px) !important;
            border-right: 1px solid {sidebar_border} !important; 
        }}
        [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3,
        [data-testid="stSidebar"] label,
        [data-testid="stSidebar"] p,
        [data-testid="stSidebar"] .stMarkdown p {{ 
            color: {text_color} !important; 
            font-family: 'Plus Jakarta Sans', sans-serif !important;
        }}
        [data-testid="stSidebar"] .stCaption,
        [data-testid="stSidebar"] .stCaption * {{
            color: {subtext_color} !important;
            font-size: 0.8rem !important;
        }}
        
        /* Form Inputs & Dropdowns */
        div[data-baseweb="select"] > div {{
            background-color: {card_bg} !important;
            border: 1px solid {card_border} !important;
            color: {text_color} !important;
            border-radius: 12px !important;
            backdrop-filter: blur(12px) !important;
            -webkit-backdrop-filter: blur(12px) !important;
            box-shadow: 0 2px 8px rgba(0,0,0,0.12) !important;
            font-family: 'Plus Jakarta Sans', sans-serif !important;
            transition: all 0.2s ease !important;
        }}
        div[data-baseweb="select"] > div:hover {{
            border-color: rgba(99, 102, 241, 0.4) !important;
            box-shadow: 0 0 12px rgba(99, 102, 241, 0.2) !important;
        }}
        div[data-baseweb="select"] * {{
            color: {text_color} !important;
        }}
        div[data-baseweb="popover"] ul,
        div[data-baseweb="popover"] li {{
            background-color: {card_bg} !important;
            backdrop-filter: blur(20px) !important;
            color: {text_color} !important;
            border-radius: 8px;
        }}
        
        /* Header Title Banner */
        .hero-banner-title {{
            font-family: 'Space Grotesk', sans-serif !important;
            font-size: 2.35rem !important;
            font-weight: 700 !important;
            background: linear-gradient(135deg, #FFFFFF 30%, #A5B4FC 100%) !important;
            -webkit-background-clip: text !important;
            -webkit-text-fill-color: transparent !important;
            margin: 0 !important;
            padding: 0 !important;
            letter-spacing: -0.03em !important;
        }}
        .hero-banner-subtitle {{
            font-family: 'Plus Jakarta Sans', sans-serif !important;
            font-size: 0.95rem !important;
            color: {subtext_color} !important;
            margin-top: 0.3rem !important;
            font-weight: 400 !important;
        }}

        /* Modern Glassmorphic KPI Cards */
        .kpi-glass-card {{
            background: {card_bg} !important;
            backdrop-filter: blur(16px) !important;
            -webkit-backdrop-filter: blur(16px) !important;
            border: 1px solid {card_border} !important;
            border-radius: 16px !important;
            padding: 18px 20px !important;
            box-shadow: {shadow_card} !important;
            position: relative;
            overflow: hidden;
            transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1) !important;
        }}
        .kpi-glass-card:hover {{
            transform: translateY(-4px);
            box-shadow: {shadow_hover} !important;
            border-color: rgba(99, 102, 241, 0.35) !important;
        }}
        .kpi-top-row {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 12px;
        }}
        .kpi-icon-pill {{
            width: 38px;
            height: 38px;
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.15rem;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }}
        .kpi-trend-pill {{
            font-size: 0.72rem;
            font-weight: 700;
            padding: 3px 8px;
            border-radius: 20px;
            display: inline-flex;
            align-items: center;
            gap: 3px;
            letter-spacing: 0.02em;
        }}
        .kpi-trend-up {{
            background: rgba(16, 185, 129, 0.15);
            color: #34D399;
            border: 1px solid rgba(52, 211, 153, 0.25);
        }}
        .kpi-trend-neutral {{
            background: rgba(99, 102, 241, 0.15);
            color: #A5B4FC;
            border: 1px solid rgba(165, 180, 252, 0.25);
        }}
        .kpi-trend-down {{
            background: rgba(244, 63, 94, 0.15);
            color: #FB7185;
            border: 1px solid rgba(251, 113, 133, 0.25);
        }}
        .kpi-label {{
            font-size: 0.76rem !important;
            font-weight: 600 !important;
            color: {subtext_color} !important;
            text-transform: uppercase !important;
            letter-spacing: 0.07em !important;
            margin-bottom: 4px !important;
        }}
        .kpi-value {{
            font-family: 'Space Grotesk', sans-serif !important;
            font-size: 1.75rem !important;
            font-weight: 700 !important;
            color: {text_color} !important;
            letter-spacing: -0.02em !important;
            line-height: 1.15 !important;
            margin: 0 !important;
        }}

        /* Executive Briefing Cards */
        .briefing-card {{
            background: {card_bg};
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            border: 1px solid {card_border};
            border-radius: 14px;
            padding: 14px 18px;
            margin-bottom: 12px;
            box-shadow: {shadow_card};
            transition: all 0.2s ease;
            position: relative;
        }}
        .briefing-card:hover {{
            transform: translateX(3px);
            border-color: rgba(99, 102, 241, 0.3);
        }}
        .briefing-card.attention {{
            border-left: 4px solid #F43F5E;
        }}
        .briefing-card.positive {{
            border-left: 4px solid #10B981;
        }}
        .briefing-card.watch {{
            border-left: 4px solid #F59E0B;
        }}
        .briefing-card.opportunity {{
            border-left: 4px solid #6366F1;
        }}
        .briefing-header {{
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 0.75rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.06em;
            margin-bottom: 5px;
        }}
        .briefing-text {{
            font-size: 0.88rem;
            color: {text_color};
            line-height: 1.5;
            margin: 0;
        }}
        
        /* Modern Chart Containers */
        .chart-card-container {{
            background: {card_bg} !important;
            backdrop-filter: blur(16px) !important;
            -webkit-backdrop-filter: blur(16px) !important;
            border: 1px solid {card_border} !important;
            border-radius: 18px !important;
            padding: 18px 20px !important;
            box-shadow: {shadow_card} !important;
            margin-bottom: 1.2rem !important;
            transition: all 0.25s ease !important;
        }}
        .chart-card-container:hover {{
            border-color: rgba(99, 102, 241, 0.3) !important;
            box-shadow: {shadow_hover} !important;
        }}
        .chart-title-text {{
            font-family: 'Space Grotesk', sans-serif !important;
            font-size: 1.05rem !important;
            font-weight: 600 !important;
            color: {header_color} !important;
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        .chart-title-dot {{
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: #6366F1;
            box-shadow: 0 0 8px #6366F1;
            display: inline-block;
        }}
        
        /* Buttons Styling */
        div.stButton > button {{
            background: {accent_button} !important;
            color: {button_text} !important;
            border: 1px solid {glass_border} !important;
            border-radius: 12px !important;
            padding: 0.45rem 1rem !important;
            font-size: 13px !important;
            font-weight: 600 !important;
            font-family: 'Plus Jakarta Sans', sans-serif !important;
            transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1) !important;
            box-shadow: 0 2px 6px rgba(0,0,0,0.06) !important;
        }}
        div.stButton > button p, 
        div.stButton > button span {{
            color: {button_text} !important;
        }}
        div.stButton > button:hover {{
            background: {accent_button_hover} !important;
            border-color: rgba(99, 102, 241, 0.4) !important;
            box-shadow: 0 4px 16px rgba(99, 102, 241, 0.25) !important;
            transform: translateY(-2px) !important;
        }}
        div.stButton > button[kind="primary"],
        div.stButton > button[data-testid="baseButton-primary"] {{
            background: {primary_btn_bg} !important;
            color: {primary_btn_text} !important;
            border: 1px solid rgba(255, 255, 255, 0.15) !important;
            box-shadow: 0 4px 18px rgba(99, 102, 241, 0.35) !important;
            font-weight: 700 !important;
        }}
        div.stButton > button[kind="primary"] p, 
        div.stButton > button[kind="primary"] span,
        div.stButton > button[data-testid="baseButton-primary"] p,
        div.stButton > button[data-testid="baseButton-primary"] span {{
            color: {primary_btn_text} !important;
        }}
        div.stButton > button[kind="primary"]:hover,
        div.stButton > button[data-testid="baseButton-primary"]:hover {{
            box-shadow: 0 6px 24px rgba(99, 102, 241, 0.5) !important;
            transform: translateY(-2px) !important;
        }}
        
        /* Chat UI Styling */
        .enterprise-message-container {{ 
            display: flex; 
            margin-bottom: 20px; 
            width: 100%; 
        }}
        .enterprise-message-container.user {{ 
            justify-content: flex-end; 
        }}
        .enterprise-message-container.assistant {{ 
            justify-content: flex-start; 
        }}
        .enterprise-bubble {{ 
            max-width: 88%; 
            padding: 18px 24px; 
            border-radius: 18px; 
            font-size: 14.5px; 
            line-height: 1.65; 
            color: {text_color}; 
            box-shadow: {shadow_card}; 
            font-family: 'Plus Jakarta Sans', sans-serif !important;
            position: relative;
        }}
        .enterprise-message-container.user .enterprise-bubble {{ 
            background: {user_bubble}; 
            color: {user_text};
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-bottom-right-radius: 4px; 
            box-shadow: 0 6px 24px rgba(99, 102, 241, 0.3);
        }}
        .enterprise-message-container.assistant .enterprise-bubble {{ 
            background: {assistant_bubble}; 
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            border: 1px solid {assistant_border}; 
            border-bottom-left-radius: 4px; 
        }}
        
        /* Assistant Avatar Chip */
        .assistant-chip {{
            display: inline-flex;
            align-items: center;
            gap: 6px;
            font-size: 0.76rem;
            font-weight: 700;
            color: #A5B4FC;
            background: rgba(99, 102, 241, 0.15);
            border: 1px solid rgba(99, 102, 241, 0.3);
            border-radius: 20px;
            padding: 2px 10px;
            margin-bottom: 10px;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}
        
        /* Structured Section Header Inside Bubble */
        .bubble-section-header {{
            background: {section_hdr_bg};
            padding: 7px 14px;
            border-radius: 10px;
            margin-top: 16px;
            margin-bottom: 10px;
            display: inline-block;
            border: 1px solid rgba(99, 102, 241, 0.25);
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
            margin: 8px 0 12px 0;
            padding-left: 18px;
            list-style-type: none;
        }}
        .bubble-pointer-list li {{
            position: relative;
            padding-left: 16px;
            margin-bottom: 8px;
            line-height: 1.6;
            color: {text_color};
            font-size: 14px;
        }}
        .bubble-pointer-list li::before {{
            content: "◆";
            position: absolute;
            left: 0;
            color: {bullet_dot_color};
            font-size: 10px;
            line-height: 1.8;
        }}
        .bubble-pointer-list li strong {{
            color: {header_color};
            font-weight: 600;
        }}
        
        /* Action Numbered Items Inside Bubble */
        .bubble-action-item {{
            display: flex;
            align-items: flex-start;
            gap: 12px;
            margin-bottom: 10px;
            font-size: 14px;
            line-height: 1.6;
        }}
        .bubble-action-item .action-num {{
            background: {badge_num_bg};
            color: {badge_num_text};
            font-size: 11px;
            font-weight: 800;
            padding: 2px 8px;
            border-radius: 6px;
            margin-top: 2px;
            flex-shrink: 0;
            box-shadow: 0 2px 8px rgba(99, 102, 241, 0.4);
        }}
        .bubble-action-item .action-desc {{
            color: {text_color};
        }}
        .bubble-action-item .action-desc strong {{
            color: {header_color};
            font-weight: 600;
        }}
        
        .bubble-paragraph {{
            margin-bottom: 10px;
            font-size: 14px;
            line-height: 1.6;
            color: {text_color};
        }}
        .bubble-paragraph strong {{
            color: {header_color};
            font-weight: 600;
        }}
        
        /* Animated Thinking Pulsar */
        @keyframes glow-pulse {{
            0% {{ box-shadow: 0 0 4px rgba(99, 102, 241, 0.4); opacity: 0.6; }}
            50% {{ box-shadow: 0 0 16px rgba(139, 92, 246, 0.8); opacity: 1; }}
            100% {{ box-shadow: 0 0 4px rgba(99, 102, 241, 0.4); opacity: 0.6; }}
        }}
        .thinking-chip {{
            display: inline-flex;
            align-items: center;
            gap: 10px;
            background: rgba(99, 102, 241, 0.15);
            border: 1px solid rgba(99, 102, 241, 0.35);
            padding: 10px 18px;
            border-radius: 30px;
            animation: glow-pulse 2s infinite ease-in-out;
            font-size: 13.5px;
            font-weight: 500;
            color: #A5B4FC;
        }}

        /* Workspace Dock (Linear / Raycast Style) */
        .workspace-dock {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            background: {card_bg};
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            border: 1px solid {card_border};
            border-radius: 14px;
            padding: 9px 12px;
            margin-bottom: 12px;
            box-shadow: {shadow_card};
            transition: all 0.2s ease;
        }}
        .workspace-dock:hover {{
            border-color: rgba(99, 102, 241, 0.35);
        }}
        .workspace-left {{
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        .workspace-avatar {{
            background: linear-gradient(135deg, #6366F1 0%, #8B5CF6 100%);
            width: 32px;
            height: 32px;
            border-radius: 9px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 16px;
            box-shadow: 0 0 14px rgba(99, 102, 241, 0.5);
            flex-shrink: 0;
        }}
        .workspace-name {{
            font-family: 'Space Grotesk', sans-serif;
            font-weight: 700;
            font-size: 0.95rem;
            color: {text_color};
            line-height: 1.15;
        }}
        .workspace-env-badge {{
            display: inline-flex;
            align-items: center;
            gap: 5px;
            font-size: 0.68rem;
            color: #34D399;
            font-weight: 600;
            letter-spacing: 0.02em;
        }}
        .pulse-dot {{
            width: 6px;
            height: 6px;
            background: #34D399;
            border-radius: 50%;
            box-shadow: 0 0 8px #34D399;
            display: inline-block;
            animation: live-pulse 2s infinite ease-in-out;
        }}
        @keyframes live-pulse {{
            0% {{ transform: scale(0.9); opacity: 0.7; }}
            50% {{ transform: scale(1.3); opacity: 1; }}
            100% {{ transform: scale(0.9); opacity: 0.7; }}
        }}

        /* Mini-Pulse Live Data Widget */
        .mini-pulse-card {{
            background: {card_bg};
            backdrop-filter: blur(14px);
            -webkit-backdrop-filter: blur(14px);
            border: 1px solid {card_border};
            border-radius: 14px;
            padding: 11px 13px;
            margin-bottom: 14px;
            box-shadow: {shadow_card};
            transition: all 0.2s ease;
        }}
        .mini-pulse-card:hover {{
            border-color: rgba(99, 102, 241, 0.35);
            box-shadow: {shadow_hover};
        }}
        .mini-pulse-top {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 8px;
        }}
        .mini-pulse-title {{
            font-size: 0.72rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.06em;
            color: #A5B4FC;
            display: flex;
            align-items: center;
            gap: 5px;
        }}
        .mini-pulse-engine {{
            font-size: 0.65rem;
            background: rgba(99, 102, 241, 0.15);
            color: #C7D2FE;
            padding: 2px 7px;
            border-radius: 6px;
            font-weight: 600;
            border: 1px solid rgba(99, 102, 241, 0.25);
        }}
        .mini-pulse-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr 1fr;
            gap: 6px;
            text-align: center;
        }}
        .mini-pulse-item {{
            background: rgba(255, 255, 255, 0.03);
            border: 1px solid rgba(255, 255, 255, 0.05);
            border-radius: 8px;
            padding: 5px 3px;
        }}
        .mini-pulse-val {{
            font-family: 'Space Grotesk', sans-serif;
            font-size: 0.95rem;
            font-weight: 700;
            color: {text_color};
            line-height: 1.1;
        }}
        .mini-pulse-lbl {{
            font-size: 0.63rem;
            color: {subtext_color};
            text-transform: uppercase;
            letter-spacing: 0.04em;
            margin-top: 2px;
        }}

        /* Filter Chips */
        .filter-chip {{
            display: inline-flex;
            align-items: center;
            background: rgba(99, 102, 241, 0.12);
            color: #C7D2FE;
            border: 1px solid rgba(99, 102, 241, 0.25);
            padding: 3px 9px;
            border-radius: 14px;
            font-size: 0.74rem;
            font-weight: 600;
            letter-spacing: 0.01em;
        }}

        /* Streamlit Chat Input Modernization */
        div[data-testid="stChatInput"] {{
            border-radius: 16px !important;
            border: 1px solid {glass_border} !important;
            background: {card_bg} !important;
            backdrop-filter: blur(20px) !important;
            -webkit-backdrop-filter: blur(20px) !important;
            box-shadow: 0 8px 30px rgba(0,0,0,0.2) !important;
            transition: all 0.25s ease !important;
        }}
        div[data-testid="stChatInput"]:focus-within {{
            border-color: #6366F1 !important;
            box-shadow: 0 0 20px rgba(99, 102, 241, 0.35) !important;
        }}
        
        /* Modern Scrollbar */
        ::-webkit-scrollbar {{
            width: 7px;
            height: 7px;
        }}
        ::-webkit-scrollbar-track {{
            background: transparent;
        }}
        ::-webkit-scrollbar-thumb {{
            background: rgba(99, 102, 241, 0.25);
            border-radius: 10px;
        }}
        ::-webkit-scrollbar-thumb:hover {{
            background: rgba(99, 102, 241, 0.5);
        }}
        
        /* Streamlit Expander - Modern Glassmorphic Container & Proper Flex Layout */
        div[data-testid="stExpander"] {{
            background: {card_bg} !important;
            backdrop-filter: blur(16px) !important;
            -webkit-backdrop-filter: blur(16px) !important;
            border: 1px solid {card_border} !important;
            border-radius: 14px !important;
            overflow: hidden !important;
            margin: 8px 0 !important;
            box-shadow: {shadow_card} !important;
            transition: all 0.2s ease !important;
        }}
        div[data-testid="stExpander"]:hover {{
            border-color: rgba(99, 102, 241, 0.35) !important;
        }}
        div[data-testid="stExpander"] details {{
            border: none !important;
            background: transparent !important;
        }}
        div[data-testid="stExpander"] details summary {{
            display: flex !important;
            flex-direction: row !important;
            align-items: center !important;
            justify-content: flex-start !important;
            gap: 12px !important;
            padding: 10px 14px !important;
            border: none !important;
            cursor: pointer !important;
            list-style: none !important;
        }}
        div[data-testid="stExpander"] details summary::-webkit-details-marker {{
            display: none !important;
        }}
        div[data-testid="stExpander"] details summary p {{
            margin: 0 !important;
            font-family: 'Plus Jakarta Sans', sans-serif !important;
            font-size: 0.88rem !important;
            font-weight: 600 !important;
            color: {text_color} !important;
            line-height: 1.4 !important;
        }}
        div[data-testid="stExpander"] div[data-testid="stExpanderDetails"] {{
            padding: 12px 14px !important;
            border-top: 1px solid {card_border} !important;
        }}

        /* Strict Protection for Streamlit Material Symbols / Icons */
        [data-testid="stIconMaterial"],
        [data-testid="stExpanderToggleIcon"],
        [data-testid="stSidebarCollapseButton"] span,
        .material-symbols-rounded,
        .material-symbols-outlined,
        .material-icons,
        span[data-testid="stIconMaterial"],
        summary [data-testid="stIconMaterial"],
        summary span[data-testid="stIconMaterial"],
        [data-testid="stSidebar"] [data-testid="stIconMaterial"],
        [data-testid="stSidebar"] span[data-testid="stIconMaterial"] {{
            font-family: 'Material Symbols Rounded', 'Material Symbols Outlined', 'Material Icons', sans-serif !important;
            font-feature-settings: 'liga' 1 !important;
            -webkit-font-feature-settings: 'liga' 1 !important;
            display: inline-flex !important;
            align-items: center !important;
            justify-content: center !important;
            letter-spacing: normal !important;
            text-transform: none !important;
            white-space: nowrap !important;
            word-wrap: normal !important;
            direction: ltr !important;
            -webkit-font-smoothing: antialiased !important;
            font-size: 1.25rem !important;
            min-width: 24px !important;
            width: 24px !important;
            height: 24px !important;
            line-height: 1 !important;
            overflow: visible !important;
            color: #A5B4FC !important;
        }}
        
        /* Hide streamlit modebar clutter */
        .modebar {{ display: none !important; }}
    </style>
    """, unsafe_allow_html=True)


def render_kpi_card(title, value, icon="📊", trend="+0.0%", is_up=True, trend_label="MoM"):
    """
    Renders high-grade frosted glass KPI card with modern icon badge and trend indicator.
    """
    if is_up:
        trend_class = "kpi-trend-up"
        trend_symbol = "↑"
    elif is_up is False:
        trend_class = "kpi-trend-down"
        trend_symbol = "↓"
    else:
        trend_class = "kpi-trend-neutral"
        trend_symbol = "●"
        
    return f"""
    <div class='kpi-glass-card'>
        <div class='kpi-top-row'>
            <div class='kpi-icon-pill' style='background: rgba(99, 102, 241, 0.15); border: 1px solid rgba(99, 102, 241, 0.3);'>
                {icon}
            </div>
            <div class='kpi-trend-pill {trend_class}'>
                <span>{trend_symbol}</span>
                <span>{trend}</span>
                <span style='opacity: 0.75; font-size: 0.65rem; font-weight: normal;'>{trend_label}</span>
            </div>
        </div>
        <div class='kpi-label'>{title}</div>
        <div class='kpi-value'>{value}</div>
    </div>
    """

def render_thinking_bubble(text="Analyzing datalake & synthesizing management insights..."):
    """
    Renders an animated glowing thinking indicator inside the chat.
    """
    html_content = f"""
    <div class='enterprise-message-container assistant'>
        <div class='thinking-chip'>
            <span style='font-size: 1.1rem;'>✨</span>
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
    text = re.sub(r'([^\n])(###\s*[\U00010000-\U0010ffff\w])', r'\1\n\n\2', text)
    text = re.sub(r'([^\n])(📌\s*)', r'\1\n\n### 📌 ', text)
    text = re.sub(r'([^\n])(📊\s*)', r'\1\n\n### 📊 ', text)
    text = re.sub(r'([^\n])(🔎\s*)', r'\1\n\n### 🔎 ', text)
    text = re.sub(r'([^\n])(🎯\s*)', r'\1\n\n### 🎯 ', text)
    text = re.sub(r'([^\n])(⚠️\s*)', r'\1\n\n### ⚠️ ', text)
    
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
            
        if l.startswith('###') or any(l.startswith(h) for h in ['📌', '📊', '🔎', '🎯', '⚠️']):
            if in_ul:
                out.append('</ul>')
                in_ul = False
            title = l.lstrip('#').strip()
            out.append(f"<div class='bubble-section-header'><h4>{html_lib.escape(title)}</h4></div>")
            continue
            
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
        html_bubble = f"""
        <div class='enterprise-message-container assistant'>
            <div class='enterprise-bubble'>
                <div class='assistant-chip'>⚡ SwiftKart AI</div>
                <div>{structured_content}</div>
            </div>
        </div>
        """
    st.markdown(html_bubble, unsafe_allow_html=True)

def render_kpi_row(kpis):
    c1, c2, c3, c4 = st.columns(4)
    with c1: 
        st.markdown(render_kpi_card("Total Revenue", format_currency(kpis.get('total_revenue', 0)), icon="💰", trend="+12.4%", is_up=True), unsafe_allow_html=True)
    with c2: 
        st.markdown(render_kpi_card("Total Orders", format_number(kpis.get('total_orders', 0)), icon="📦", trend="+8.1%", is_up=True), unsafe_allow_html=True)
    with c3: 
        st.markdown(render_kpi_card("Avg Order Value", format_currency(kpis.get('avg_order_value', 0)), icon="🛒", trend="+3.7%", is_up=True), unsafe_allow_html=True)
    with c4: 
        st.markdown(render_kpi_card("Active Customers", format_number(kpis.get('active_customers', 0)), icon="👥", trend="+15.2%", is_up=True), unsafe_allow_html=True)

def render_kpi_row_2(kpis):
    c1, c2, c3 = st.columns(3)
    with c1: 
        st.markdown(render_kpi_card("Repeat Purchase Rate", f"{kpis.get('repeat_purchase_rate', 0):.1f}%", icon="🔁", trend="+2.8%", is_up=True, trend_label="QoQ"), unsafe_allow_html=True)
    with c2: 
        st.markdown(render_kpi_card("Avg Churn Risk", f"{kpis.get('churn_risk_avg', 0):.1f}%", icon="⚠️", trend="-1.4%", is_up=False, trend_label="MoM"), unsafe_allow_html=True)
    csat = kpis.get('customer_satisfaction', 0.0)
    with c3: 
        st.markdown(render_kpi_card("Customer CSAT", f"{csat:.2f} / 5.0", icon="⭐", trend="+0.2", is_up=True, trend_label="Avg"), unsafe_allow_html=True)

def handle_explain_with_ai(prompt):
    st.session_state.pending_ai_query = prompt
    st.session_state.current_page = "🤖 Chatbot"
    st.rerun()

def render_chart_section(title, fig, button_text, explain_prompt, key):
    st.markdown("<div class='chart-card-container'>", unsafe_allow_html=True)
    hc, bc = st.columns([0.70, 0.30])
    with hc:
        st.markdown(f"""
            <div class='chart-title-text' style='padding-top: 4px;'>
                <span class='chart-title-dot'></span>
                <span>{title}</span>
            </div>
        """, unsafe_allow_html=True)
    with bc:
        if st.button(button_text, key=key, use_container_width=True): 
            handle_explain_with_ai(explain_prompt)
    if fig: 
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    st.markdown("</div>", unsafe_allow_html=True)

def render_executive_overview(kpis, briefing, charts_data):
    col_hdr, col_btns = st.columns([0.55, 0.45])
    with col_hdr:
        st.markdown("""
            <div style="margin-bottom: 0.8rem; padding-top: 0.1rem;">
                <h1 class="hero-banner-title">Executive Analytics</h1>
                <p class="hero-banner-subtitle">Real-time Quick-Commerce Performance & AI Intelligence</p>
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
    
    # Modern Executive Intelligence Alert Grid
    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)
    b_col1, b_col2 = st.columns(2)
    with b_col1:
        st.markdown(f"""
        <div class='briefing-card attention'>
            <div class='briefing-header' style='color: #FB7185;'>
                <span>🔴</span>
                <span>Action Required</span>
            </div>
            <div class='briefing-text'>{html_lib.escape(str(briefing.get('needs_attention', '')))}</div>
        </div>
        <div class='briefing-card positive'>
            <div class='briefing-header' style='color: #34D399;'>
                <span>🟢</span>
                <span>Growth Catalyst</span>
            </div>
            <div class='briefing-text'>{html_lib.escape(str(briefing.get('positive', '')))}</div>
        </div>
        """, unsafe_allow_html=True)
        
    with b_col2:
        st.markdown(f"""
        <div class='briefing-card watch'>
            <div class='briefing-header' style='color: #FBBF24;'>
                <span>🟡</span>
                <span>Metric to Monitor</span>
            </div>
            <div class='briefing-text'>{html_lib.escape(str(briefing.get('watch', '')))}</div>
        </div>
        <div class='briefing-card opportunity'>
            <div class='briefing-header' style='color: #A5B4FC;'>
                <span>🟣</span>
                <span>Strategic Opportunity</span>
            </div>
            <div class='briefing-text'>{html_lib.escape(str(briefing.get('priority', '')))}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)
    
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
        render_chart_section("Category Revenue Distribution", plot_cat_revenue(charts_data.get("cat_revenue")), "✨ Explain with AI", "Which product category is driving the most revenue?", "exp_cat_rev")


# --- Chat Components ---

def initialize_chat_history():
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": "Hello! I am your AI Management Analyst. What would you like to explore across your Quick-Commerce datalake?", "type": "text"}]
    if "follow_ups" not in st.session_state:
        st.session_state.follow_ups = [
            "Which city generated the highest gross revenue?",
            "Which customer segment shows the highest churn risk?",
            "Which product categories drive top margins?",
            "How does delivery time impact CSAT rating?"
        ]

def render_follow_ups():
    if st.session_state.follow_ups:
        st.markdown("""
            <div style='font-size:13px; font-weight:700; color:#A5B4FC; margin-bottom:10px; display:flex; align-items:center; gap:6px;'>
                <span>💡</span>
                <span>RECOMMENDED EXPLORATIONS</span>
            </div>
        """, unsafe_allow_html=True)
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
            render_message_bubble(message["role"], "Here is the structured dataset query results:")
            st.dataframe(message["content"], use_container_width=True, hide_index=True)
        elif msg_type == "chart":
            render_message_bubble(message["role"], "Here is the visualized intelligence breakdown:")
            st.plotly_chart(message["content"], use_container_width=True, config={'displayModeBar': False})

def render_sidebar_data_section(dataframes):
    """
    Renders modern frosted glass cards for data source files and uploader.
    """
    st.sidebar.markdown("---")
    
    st.sidebar.markdown("""
        <div style='display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px;'>
            <span style='font-size: 0.82rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; color: #A5B4FC;'>📁 Live Datalake</span>
            <span style='font-size: 0.7rem; background: rgba(16, 185, 129, 0.15); color: #34D399; padding: 2px 8px; border-radius: 12px; border: 1px solid rgba(52, 211, 153, 0.3); font-weight: 700;'>● 4 Tables</span>
        </div>
    """, unsafe_allow_html=True)
    
    with st.sidebar.expander("Connected Tables", expanded=True):
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
                <div style="padding: 8px 12px; margin-bottom: 7px; border-radius: 10px; background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.06); font-size: 0.83rem; display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <strong style="color: #F8FAFC;">{icon} {filename}</strong><br>
                        <span style="color: #94A3B8; font-size: 0.74rem;">{count:,} records • {size}</span>
                    </div>
                    <span style="color: #34D399; font-size: 0.72rem; font-weight: 700;">Synced</span>
                </div>
                """, unsafe_allow_html=True)

    st.sidebar.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
    st.sidebar.markdown("""
        <div style='font-size: 0.82rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; color: #A5B4FC; margin-bottom: 6px;'>
            📤 Add New Datasets
        </div>
    """, unsafe_allow_html=True)
    uploaded_files = st.sidebar.file_uploader(
        "Upload CSV or Excel tables",
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
                st.sidebar.success(f"✅ **{f.name}** ({df.shape[0]:,} rows synced)")
            except Exception as e:
                st.sidebar.error(f"Error reading {f.name}: {e}")
                
    return uploaded_dfs

def render_data_used(dataframes):
    return render_sidebar_data_section(dataframes)
