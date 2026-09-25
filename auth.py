import streamlit as st
from supabase import create_client, Client

def get_supabase() -> Client:
    try:
        url = st.secrets.get("SUPABASE_URL")
        key = st.secrets.get("SUPABASE_KEY") or st.secrets.get("SUPABASE_ANON_KEY") or st.secrets.get("SUPABASE_ANON")
        if not url or not key:
            return None
        return create_client(url, key)
    except Exception:
        return None

if "user" not in st.session_state:
    st.session_state.user = None

def show_user_sidebar():
    user = st.session_state.get("user")
    if user:
        with st.sidebar:
            st.write(f"👤 {user.get('email','User')}")
            if st.button("Logout"):
                st.session_state.user = None
                st.rerun()

def auth_page():
    st.title("🔐 ClyxessAI Login")
    supabase = get_supabase()
    if supabase is None:
        st.error("Supabase keys nahi mile. Secrets me SUPABASE_URL aur SUPABASE_KEY daalo.")
        return

    tab1, tab2 = st.tabs(["Login", "Signup"])
    
    with tab1:
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_pass")
        if st.button("Login", key="login_btn"):
            try:
                res = supabase.auth.sign_in_with_password({"email": email, "password": password})
                if res.user:
                    st.session_state.user = {"email": res.user.email, "id": str(res.user.id)}
                    st.success("Login ho gaya!")
                    st.rerun()
            except Exception as e:
                st.error(f"Login fail: {e}")

    with tab2:
        email2 = st.text_input("Email", key="signup_email")
        password2 = st.text_input("Password", type="password", key="signup_pass")
        if st.button("Create Account", key="signup_btn"):
            try:
                res = supabase.auth.sign_up({"email": email2, "password": password2})
                st.success("Account ban gaya! Ab Login tab me login karo.")
            except Exception as e:
                st.error(f"Signup fail: {e}")
