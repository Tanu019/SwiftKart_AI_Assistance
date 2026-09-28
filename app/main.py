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
    inject_enterprise_css, render_data_used, render_sidebar_data_section, render_executive_overview, 
    initialize_chat_history, render_chat_history, render_message_bubble, render_follow_ups
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
    
    if st.session_state.current_page == "🤖 Chatbot":
        if st.sidebar.button("🔙 Back to Dashboard", use_container_width=True):
            st.session_state.current_page = "📊 Dashboard"
            st.rerun()    
    # --- GLOBAL FILTERS ---
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🎛️ Global Filters")
    role = st.sidebar.selectbox("Role View:", ["Business Head", "Sales Manager", "Marketing Manager", "Operations Manager"])
    
    cities = ["All"] + sorted(list(raw_data["orders"]["city"].dropna().unique())) if "orders" in raw_data else ["All"]
    selected_city = st.sidebar.selectbox("City", cities)
    
    personas = ["All"] + sorted(list(raw_data["customers"]["persona"].dropna().unique())) if "customers" in raw_data else ["All"]
    selected_persona = st.sidebar.selectbox("Customer Persona", personas)
    
    active_filters = {"city": selected_city, "persona": selected_persona, "role": role}
    
    # Apply Filters
    filtered_data = apply_global_filters(raw_data, active_filters)
    
    # Render Data Source Files and Uploaded Documents Section
    uploaded_dfs = render_sidebar_data_section(raw_data)
    
    # Merge any custom uploaded datasets into engine datalake
    engine_data = filtered_data.copy()
    if uploaded_dfs:
        engine_data.update(uploaded_dfs)
        
    datalake = get_cached_engine(engine_data) 
    
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
            
            with st.spinner("Analyzing business data..."):
                response = ask_assistant(datalake, last_prompt, history, role=role)
                
                import plotly.graph_objects as go
                import types
                
                if isinstance(response, pd.DataFrame): 
                    st.session_state.messages.append({"role": "assistant", "content": response, "type": "table"})
                    st.session_state.follow_ups = datalake.generate_follow_ups(last_prompt, "Table output")
                    st.rerun()
                elif isinstance(response, go.Figure):
                    st.session_state.messages.append({"role": "assistant", "content": response, "type": "chart"})
                    st.session_state.follow_ups = datalake.generate_follow_ups(last_prompt, "Chart output")
                    st.rerun()
                elif isinstance(response, types.GeneratorType):
                    placeholder = st.empty()
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
                    st.session_state.follow_ups = datalake.generate_follow_ups(last_prompt, full_response)
                    st.rerun()
                else:
                    st.session_state.messages.append({"role": "assistant", "content": str(response), "type": "text"})
                    st.session_state.follow_ups = datalake.generate_follow_ups(last_prompt, str(response))
                    st.rerun()

if __name__ == "__main__":
    main()
