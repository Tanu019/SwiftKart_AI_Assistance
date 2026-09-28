import streamlit as st
import os
import sys
import pandas as pd
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set page config
st.set_page_config(page_title="SwiftKart Intelligence", page_icon="✨", layout="wide", initial_sidebar_state="collapsed")

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
        st.session_state.theme = "Light"
        
    inject_enterprise_css(st.session_state.theme)
    
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
        
    # --- SIDEBAR NAVIGATION ---
    col_brand, col_theme = st.sidebar.columns([4, 1])
    with col_brand:
        st.markdown("<h2 style='margin:0; padding:0; font-size:1.35rem; font-weight:600;'>SwiftKart</h2>", unsafe_allow_html=True)
    with col_theme:
        theme_icon = "🌙" if st.session_state.theme == "Light" else "☀️"
        if st.button(theme_icon, help=f"Switch to {'Dark' if st.session_state.theme == 'Light' else 'Light'} mode", key="theme_toggle_btn"):
            st.session_state.theme = "Dark" if st.session_state.theme == "Light" else "Light"
            st.rerun()
    st.sidebar.caption("AI-Powered Management Intelligence")
    
    # Navigation Buttons
    nav_col1, nav_col2 = st.sidebar.columns(2)
    with nav_col1:
        if st.button("📊 Dashboard", use_container_width=True, type="primary" if st.session_state.current_page == "📊 Dashboard" else "secondary"):
            if st.session_state.current_page != "📊 Dashboard":
                st.session_state.current_page = "📊 Dashboard"
                st.rerun()
    with nav_col2:
        if st.button("🤖 Chatbot", use_container_width=True, type="primary" if st.session_state.current_page == "🤖 Chatbot" else "secondary"):
            if st.session_state.current_page != "🤖 Chatbot":
                st.session_state.current_page = "🤖 Chatbot"
                st.rerun()    
    # --- GLOBAL FILTERS ---
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🎛️ Global Filters")
    role = st.sidebar.selectbox("Role View:", ["Business Head", "Sales Manager", "Marketing Manager", "Operations Manager"])
    
    cities = ["All"] + sorted(list(raw_data["orders"]["city"].dropna().unique())) if "orders" in raw_data else ["All"]
    selected_city = st.sidebar.selectbox("City", cities)
    
    personas = ["All"] + sorted(list(raw_data["customers"]["persona"].dropna().unique())) if "customers" in raw_data else ["All"]
    selected_persona = st.sidebar.selectbox("Customer Persona", personas)
    
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
        st.title("🤖 Chatbot")
        st.caption("Ask your business data. Get insights. Make faster decisions.")
        
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
