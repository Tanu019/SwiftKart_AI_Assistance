"""
auth.py
-------
Supabase Authentication integration for SwiftKart AI.
Handles user login, signup, session persistence, and custom enterprise login UI.
"""

import os
import streamlit as st
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")


@st.cache_resource
def get_supabase_client() -> Client | None:
    """Initializes and caches the Supabase client."""
    if not SUPABASE_URL or not SUPABASE_KEY:
        return None
    try:
        return create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as e:
        st.error(f"Error initializing Supabase client: {e}")
        return None


def login_user(email: str, password: str):
    """Authenticate user with email and password via Supabase Auth."""
    supabase = get_supabase_client()
    if not supabase:
        return False, "Supabase connection is not configured in .env."

    try:
        response = supabase.auth.sign_in_with_password({"email": email.strip(), "password": password})
        if response.user:
            return True, response.user
        return False, "Invalid email or password."
    except Exception as e:
        error_msg = str(e)
        if "Invalid login credentials" in error_msg:
            return False, "Invalid email or password."
        elif "Email not confirmed" in error_msg:
            return False, "Please confirm your email address before logging in, or disable email confirmation in Supabase Auth settings."
        return False, f"Authentication error: {error_msg}"


def signup_user(email: str, password: str):
    """Register a new user account via Supabase Auth."""
    supabase = get_supabase_client()
    if not supabase:
        return False, "Supabase connection is not configured in .env."

    try:
        response = supabase.auth.sign_up({"email": email.strip(), "password": password})
        if response.user:
            return True, "Account created successfully! You can now sign in."
        return False, "Sign-up failed. Please try again."
    except Exception as e:
        return False, f"Sign-up error: {str(e)}"


def signout_user():
    """Sign out the current user and clear session state."""
    supabase = get_supabase_client()
    if supabase:
        try:
            supabase.auth.sign_out()
        except Exception:
            pass
    st.session_state.authenticated = False
    st.session_state.user = None
    st.session_state.current_page = "📊 Dashboard"
    st.session_state.messages = []


def render_login_page():
    """Renders a sleek, modern enterprise login & sign-up portal."""
    theme = st.session_state.get("theme", "Dark")
    is_dark = theme == "Dark"

    card_bg = "#121A24" if is_dark else "#FFFFFF"
    card_border = "rgba(211, 209, 206, 0.15)" if is_dark else "#E2E8F0"
    text_color = "#F8FAFC" if is_dark else "#0F172A"
    subtext_color = "#94A3B8" if is_dark else "#64748B"

    col_left, col_center, col_right = st.columns([1, 1.8, 1])

    with col_center:
        st.markdown(
            f"""
            <div style="text-align: center; margin-top: 1.5rem; margin-bottom: 2rem;">
                <div style="display: inline-flex; align-items: center; justify-content: center; width: 56px; height: 56px; border-radius: 16px; background: linear-gradient(135deg, #2563EB, #7C3AED); margin-bottom: 12px; box-shadow: 0 8px 24px rgba(37, 99, 235, 0.35);">
                    <span style="font-size: 28px;">🛒</span>
                </div>
                <h1 style="font-size: 2rem; font-weight: 700; color: {text_color}; margin: 0; padding: 0; letter-spacing: -0.02em;">SwiftKart AI</h1>
                <p style="font-size: 0.95rem; color: {subtext_color}; margin-top: 6px;">Enterprise Intelligence & Analytics Portal</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        tab_login, tab_signup = st.tabs(["🔐 Sign In", "✨ Create Account"])

        with tab_login:
            with st.form("login_form", clear_on_submit=False):
                st.markdown("<p style='font-size: 0.9rem; font-weight: 600; margin-bottom: 4px;'>Email Address</p>", unsafe_allow_html=True)
                email = st.text_input("Email", placeholder="you@company.com", label_visibility="collapsed")
                
                st.markdown("<p style='font-size: 0.9rem; font-weight: 600; margin-top: 10px; margin-bottom: 4px;'>Password</p>", unsafe_allow_html=True)
                password = st.text_input("Password", type="password", placeholder="••••••••", label_visibility="collapsed")
                
                st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
                submitted = st.form_submit_button("Sign In →", use_container_width=True, type="primary")

                if submitted:
                    if not email or not password:
                        st.error("⚠️ Please enter both email and password.")
                    else:
                        with st.spinner("Authenticating with Supabase..."):
                            success, result = login_user(email, password)
                            if success:
                                st.session_state.authenticated = True
                                st.session_state.user = result
                                st.success("✅ Signed in successfully!")
                                st.rerun()
                            else:
                                st.error(f"❌ {result}")

        with tab_signup:
            with st.form("signup_form", clear_on_submit=True):
                st.markdown("<p style='font-size: 0.9rem; font-weight: 600; margin-bottom: 4px;'>Work Email</p>", unsafe_allow_html=True)
                new_email = st.text_input("Work Email", placeholder="you@company.com", label_visibility="collapsed")
                
                st.markdown("<p style='font-size: 0.9rem; font-weight: 600; margin-top: 10px; margin-bottom: 4px;'>Create Password</p>", unsafe_allow_html=True)
                new_password = st.text_input("Create Password", type="password", placeholder="Minimum 6 characters", label_visibility="collapsed")
                
                st.markdown("<p style='font-size: 0.9rem; font-weight: 600; margin-top: 10px; margin-bottom: 4px;'>Confirm Password</p>", unsafe_allow_html=True)
                confirm_password = st.text_input("Confirm Password", type="password", placeholder="Re-enter password", label_visibility="collapsed")
                
                st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
                signup_submitted = st.form_submit_button("Create Account ✨", use_container_width=True)

                if signup_submitted:
                    if not new_email or not new_password or not confirm_password:
                        st.error("⚠️ Please fill in all fields.")
                    elif len(new_password) < 6:
                        st.error("⚠️ Password must be at least 6 characters long.")
                    elif new_password != confirm_password:
                        st.error("⚠️ Passwords do not match.")
                    else:
                        with st.spinner("Creating your Supabase account..."):
                            success, message = signup_user(new_email, new_password)
                            if success:
                                st.success(f"🎉 {message}")
                            else:
                                st.error(f"❌ {message}")

        st.markdown(
            f"""
            <div style="text-align: center; margin-top: 2rem; padding: 12px; border-radius: 8px; border: 1px dashed {card_border}; font-size: 0.8rem; color: {subtext_color};">
                🔒 Secured with <b>Supabase PostgreSQL Auth</b> & End-to-End Encryption
            </div>
            """,
            unsafe_allow_html=True,
        )
