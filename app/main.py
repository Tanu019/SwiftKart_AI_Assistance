import streamlit as st
import os
import sys
import pandas as pd
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set page config
st.set_page_config(page_title="SwiftKart Intelligence", page_icon="✨", layout="wide", initial_sidebar_state="expanded")

from app.data_loader import load_data
from app.analytics import get_kpis, generate_management_briefing, generate_management_report, apply_global_filters, get_dashboard_queries
from app.ui_components import (
    inject_enterprise_css, render_sidebar_data_section, render_executive_overview, 
    initialize_chat_history, render_chat_history, render_message_bubble, render_thinking_bubble, render_follow_ups
)
from app.chat_engine import init_chat_engine, ask_assistant

load_dotenv()

@st.cache_resource
def get_cached_data():
    return load_data()

@st.cache_resource
def get_cached_engine(_dataframes):
    return init_chat_engine(_dataframes)

def main():
    if "theme" not in st.session_state:
        st.session_state.theme = "Dark"
        
    inject_enterprise_css(st.session_state.theme)

    st.session_state.authenticated = True
    
    # --- APP STATE INITIALIZATION ---
    if "current_page" not in st.session_state:
        st.session_state.current_page = "📊 Dashboard"
    if "pending_ai_query" not in st.session_state:
        st.session_state.pending_ai_query = None
    if "time_filter_type" not in st.session_state:
        st.session_state.time_filter_type = "Total"
    if "selected_month" not in st.session_state:
        st.session_state.selected_month = "December 2025"
    if "selected_quarter" not in st.session_state:
        st.session_state.selected_quarter = "Q4 2025"

    with st.spinner("Loading Enterprise Datalake..."):
        raw_data = get_cached_data()
        
    # --- SIDEBAR NAVIGATION (Concept 1: Modern Segmented Dock) ---
    col_brand, col_theme = st.sidebar.columns([3.8, 1.2])
    with col_brand:
        st.markdown("""
            <div class="workspace-dock" style="margin-bottom: 0;">
                <div class="workspace-left">
                    <div class="workspace-avatar">⚡</div>
                    <div>
                        <div class="workspace-name">SwiftKart AI</div>
                        <div class="workspace-env-badge">
                            <span class="pulse-dot"></span>
                            <span>Production • India HQ</span>
                        </div>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)
    with col_theme:
        st.markdown("<div style='height: 4px;'></div>", unsafe_allow_html=True)
        theme_icon = "🌙" if st.session_state.theme == "Light" else "☀️"
        if st.button(theme_icon, help=f"Switch to {'Dark' if st.session_state.theme == 'Light' else 'Light'} mode", key="theme_toggle_btn", use_container_width=True):
            st.session_state.theme = "Dark" if st.session_state.theme == "Light" else "Light"
            st.rerun()
    
    st.sidebar.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
    
    # Segmented Navigation Dock
    nav_col1, nav_col2 = st.sidebar.columns(2)
    with nav_col1:
        is_dash = st.session_state.current_page == "📊 Dashboard"
        if st.button("📊 Dashboard", use_container_width=True, type="primary" if is_dash else "secondary", key="nav_dash_btn"):
            if not is_dash:
                st.session_state.current_page = "📊 Dashboard"
                st.rerun()
    with nav_col2:
        is_chat = st.session_state.current_page == "🤖 Chatbot"
        if st.button("🤖 Chatbot", use_container_width=True, type="primary" if is_chat else "secondary", key="nav_chat_btn"):
            if not is_chat:
                st.session_state.current_page = "🤖 Chatbot"
                st.rerun()    
                
    # Mini-Pulse Live Data Pulse Card
    tot_orders = len(raw_data["orders"]) if "orders" in raw_data else 100000
    tot_rev = raw_data["orders"]["total_amount"].sum() if "orders" in raw_data and "total_amount" in raw_data["orders"].columns else 52400000
    tot_rev_str = f"₹{tot_rev/10000000:.1f}Cr" if tot_rev >= 10000000 else f"₹{tot_rev/100000:.1f}L"
    tot_orders_str = f"{tot_orders/1000:.0f}K" if tot_orders >= 1000 else str(tot_orders)
    
    st.sidebar.markdown(f"""
        <div class="mini-pulse-card">
            <div class="mini-pulse-top">
                <span class="mini-pulse-title">⚡ Live Datalake Pulse</span>
                <span class="mini-pulse-engine">DuckDB Active</span>
            </div>
            <div class="mini-pulse-grid">
                <div class="mini-pulse-item">
                    <div class="mini-pulse-val">{tot_orders_str}</div>
                    <div class="mini-pulse-lbl">Orders</div>
                </div>
                <div class="mini-pulse-item">
                    <div class="mini-pulse-val">{tot_rev_str}</div>
                    <div class="mini-pulse-lbl">Gross Vol</div>
                </div>
                <div class="mini-pulse-item">
                    <div class="mini-pulse-val">4.6★</div>
                    <div class="mini-pulse-lbl">CSAT</div>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # --- GLOBAL FILTERS & ANALYTICS SCOPE ---
    hdr_col, reset_col = st.sidebar.columns([0.68, 0.32])
    with hdr_col:
        st.markdown("<div style='font-size: 0.8rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; color: #A5B4FC; padding-top: 6px;'>🎛️ Analytics Scope</div>", unsafe_allow_html=True)
    with reset_col:
        if st.button("↺ Reset", key="btn_reset_filters", help="Reset all filters to default", use_container_width=True):
            st.session_state.selected_city = "All"
            st.session_state.selected_persona = "All"
            st.session_state.selected_role = "Business Head"
            st.rerun()
            
    roles_list = ["Business Head", "Sales Manager", "Marketing Manager", "Operations Manager"]
    current_role = st.session_state.get("selected_role", "Business Head")
    role_idx = roles_list.index(current_role) if current_role in roles_list else 0
    role = st.sidebar.selectbox("Role Perspective:", roles_list, index=role_idx, key="role_selector")
    if role != current_role:
        st.session_state.selected_role = role
        st.rerun()
    
    cities = ["All"] + sorted(list(raw_data["orders"]["city"].dropna().unique())) if "orders" in raw_data else ["All"]
    current_city = st.session_state.get("selected_city", "All")
    city_idx = cities.index(current_city) if current_city in cities else 0
    selected_city = st.sidebar.selectbox("City Region:", cities, index=city_idx, key="city_selector")
    if selected_city != current_city:
        st.session_state.selected_city = selected_city
        st.rerun()
    
    personas = ["All"] + sorted(list(raw_data["customers"]["persona"].dropna().unique())) if "customers" in raw_data else ["All"]
    current_persona = st.session_state.get("selected_persona", "All")
    persona_idx = personas.index(current_persona) if current_persona in personas else 0
    selected_persona = st.sidebar.selectbox("Customer Persona:", personas, index=persona_idx, key="persona_selector")
    if selected_persona != current_persona:
        st.session_state.selected_persona = selected_persona
        st.rerun()
        
    # Active Filter Chips
    chips_html = f"""
    <div style="display: flex; flex-wrap: wrap; gap: 5px; margin: 6px 0 10px 0;">
        <span class="filter-chip">👔 {role}</span>
        {f'<span class="filter-chip">📍 {selected_city}</span>' if selected_city != "All" else ""}
        {f'<span class="filter-chip">👥 {selected_persona}</span>' if selected_persona != "All" else ""}
    </div>
    """
    st.sidebar.markdown(chips_html, unsafe_allow_html=True)
    
    active_filters = {
        "city": selected_city, 
        "persona": selected_persona, 
        "role": role,
        "time_filter_type": st.session_state.time_filter_type,
        "selected_month": st.session_state.selected_month,
        "selected_quarter": st.session_state.selected_quarter
    }
    
    # Apply Filters
    filtered_data = apply_global_filters(raw_data, active_filters)
    
    # Render Data Source Files and Uploaded Documents Section
    uploaded_dfs = render_sidebar_data_section(raw_data)
    
    datalake = get_cached_engine(raw_data)
    if datalake and uploaded_dfs:
        datalake.register_tables(uploaded_dfs) 
    
    # --- PAGE ROUTING ---
    if st.session_state.current_page == "📊 Dashboard":
        kpis = get_kpis(filtered_data)
        briefing = generate_management_briefing(filtered_data, role)
        charts_data = get_dashboard_queries(filtered_data, "executive")
        render_executive_overview(kpis, briefing, charts_data)
        
    elif st.session_state.current_page == "🤖 Chatbot":
        st.markdown("""
            <div style="margin-bottom: 1.2rem; padding-top: 0.1rem;">
                <h1 class="hero-banner-title">🤖 AI Data Analyst</h1>
                <p class="hero-banner-subtitle">Natural Language SQL Queries, Automated Visualizations & Strategic Insights</p>
            </div>
        """, unsafe_allow_html=True)
        
        initialize_chat_history()
        render_chat_history()
        
        # Check if we came here from an "Explain with AI" button
        if st.session_state.pending_ai_query:
            prompt = st.session_state.pending_ai_query
            st.session_state.pending_ai_query = None # clear it
        else:
            prompt = render_follow_ups()
            if not prompt:
                prompt = st.chat_input("Ask a business question...")
                
        if prompt:
            st.session_state.follow_ups = []
            st.session_state.messages.append({"role": "user", "content": prompt, "type": "text"})
            st.rerun()
            
        if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
            last_prompt = st.session_state.messages[-1]["content"]
            history = st.session_state.messages[:-1]
            role_str = str(role) if role is not None else "Business Head"
            
            if datalake is None:
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": "⚠️ AI Assistant Engine is offline. Please check your GROQ_API_KEY in the .env file.", 
                    "type": "text"
                })
                st.rerun()
            
            # Immediately show animated thinking indicator while analyzing data
            placeholder = st.empty()
            with placeholder.container():
                render_thinking_bubble("Analyzing enterprise data & synthesizing insights...")
            
            response = ask_assistant(datalake, last_prompt, history, role=role_str)
            
            import plotly.graph_objects as go
            import types
            
            if isinstance(response, pd.DataFrame): 
                placeholder.empty()
                st.session_state.messages.append({"role": "assistant", "content": response, "type": "table"})
                st.session_state.follow_ups = datalake.generate_follow_ups(last_prompt, "Table output") if datalake else []
                st.rerun()
            elif isinstance(response, go.Figure):
                placeholder.empty()
                st.session_state.messages.append({"role": "assistant", "content": response, "type": "chart"})
                st.session_state.follow_ups = datalake.generate_follow_ups(last_prompt, "Chart output") if datalake else []
                st.rerun()
            elif isinstance(response, types.GeneratorType):
                full_response = ""
                try:
                    for chunk in response:
                        full_response += chunk
                        with placeholder.container():
                            render_message_bubble("assistant", full_response)
                except Exception as e:
                    full_response = f"⚠️ Analysis failed: {e}"
                    with placeholder.container():
                        render_message_bubble("assistant", full_response)
                st.session_state.messages.append({"role": "assistant", "content": full_response, "type": "text"})
                st.session_state.follow_ups = datalake.generate_follow_ups(last_prompt, full_response) if datalake else []
                st.rerun()
            else:
                placeholder.empty()
                st.session_state.messages.append({"role": "assistant", "content": str(response), "type": "text"})
                st.session_state.follow_ups = datalake.generate_follow_ups(last_prompt, str(response)) if datalake else []
                st.rerun()

if __name__ == "__main__":
    main()
