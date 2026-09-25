import streamlit as st
from supabase import create_client, Client

def get_supabase() -> Client:
    try:
        url = st.secrets.get("SUPABASE_URL")
        key = st.secrets.get("SUPABASE_KEY") or st.secrets.get("SUPABASE_ANON_KEY")
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
    st.markdown("""
    <style>
    .social-btn {width:100%; padding:10px; border-radius:8px; border:1px solid #ccc; background:white; color:black; font-weight:600; margin-bottom:10px; display:flex; align-items:center; justify-content:center; gap:10px;}
    </style>
    """, unsafe_allow_html=True)
    
    st.title("🔐 ClyxessAI Login")
    supabase = get_supabase()
    if supabase is None:
        st.error("Secrets missing")
        return

    # --- SOCIAL LOGIN ---
    st.markdown("### Continue with")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔵 G  Google", use_container_width=True):
            try:
                res = supabase.auth.sign_in_with_oauth({"provider": "google", "options": {"redirect_to": "https://clyxessai.streamlit.app"}})
                st.markdown(f'<meta http-equiv="refresh" content="0; url={res.url}">', unsafe_allow_html=True)
                st.link_button("Click to open Google", res.url)
            except Exception as e:
                st.error(f"Google: {e}")
    with col2:
        if st.button("🔵 f  Facebook", use_container_width=True):
            try:
                res = supabase.auth.sign_in_with_oauth({"provider": "facebook", "options": {"redirect_to": "https://clyxessai.streamlit.app"}})
                st.link_button("Click to open Facebook", res.url)
            except Exception as e:
                st.error(f"Facebook: {e}")
    
    st.divider()

    tab1, tab2 = st.tabs(["Login", "Signup"])
    with tab1:
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_pass")
        if st.button("Login", use_container_width=True):
            try:
                res = supabase.auth.sign_in_with_password({"email": email, "password": password})
                if res.user:
                    st.session_state.user = {"email": res.user.email, "id": str(res.user.id)}
                    st.rerun()
            except Exception as e:
                st.error(f"{e}")

    with tab2:
        email2 = st.text_input("Email", key="signup_email", value="infocarloxin24@gmail.com")
        password2 = st.text_input("Password", type="password", key="signup_pass")
        if st.button("Create Account", use_container_width=True):
            try:
                res = supabase.auth.sign_up({"email": email2, "password": password2})
                st.success("Account ban gaya! Ab Login tab me login karo.")
            except Exception as e:
                st.error(f"{e}")

    # Handle OAuth callback
    if "code" in st.query_params:
        try:
            supabase.auth.exchange_code_for_session(dict(st.query_params))
            session = supabase.auth.get_session()
            if session and session.user:
                st.session_state.user = {"email": session.user.email, "id": str(session.user.id)}
                st.query_params.clear()
                st.rerun()
        except Exception:
            pass
