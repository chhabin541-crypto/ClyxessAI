import streamlit as st
from supabase import create_client

SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_ANON_KEY"]
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

if "user" not in st.session_state:
    st.session_state.user = None

def login(email, password):
    try:
        res = supabase.auth.sign_in_with_password({"email": email, "password": password})
        st.session_state.user = res.user
        return True, "Login successful!"
    except Exception as e:
        return False, str(e)

def signup(email, password):
    try:
        res = supabase.auth.sign_up({"email": email, "password": password})
        return True, "Signup successful! Email verify karo."
    except Exception as e:
        return False, str(e)

def logout():
    supabase.auth.sign_out()
    st.session_state.user = None
    st.rerun()

def show_user_sidebar():
    with st.sidebar:
        if st.session_state.user is None:
            st.warning("🔒 Not Logged In")
        else:
            user = st.session_state.user
            email = user.email
            avatar_url = None
            full_name = email.split('@')[0]
            if hasattr(user, 'user_metadata') and user.user_metadata:
                avatar_url = user.user_metadata.get('avatar_url') or user.user_metadata.get('picture')
                full_name = user.user_metadata.get('full_name', full_name)
            col1, col2 = st.columns([1, 3])
            with col1:
                if avatar_url: st.image(avatar_url, width=45)
                else: st.markdown("### 👤")
            with col2:
                st.markdown(f"**{full_name}**")
                st.caption(email)

            # Chat count
            try:
                result = supabase.table("users").select("chat_count, is_admin").eq("email", email).execute()
                if result.data:
                    data = result.data[0]
                    count = data.get("chat_count", 0)
                    is_admin = data.get("is_admin", False)
                    if is_admin: st.success("👑 Admin — Unlimited")
                    else: st.info(f"💬 Free Chats: {max(0, 3-count)}/3")
            except: pass

            if st.button("🚪 Logout", use_container_width=True):
                logout()

def auth_page():
    st.title("🚀 ClyxessChat AI")
    st.subheader("🔐 Login / Sign Up")
    tab1, tab2 = st.tabs(["Login", "Sign Up"])
    with tab1:
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_pass")
        if st.button("Login", use_container_width=True):
            success, msg = login(email, password)
            if success: st.success(msg); st.rerun()
            else: st.error(msg)
    with tab2:
        email = st.text_input("Email", key="signup_email")
        password = st.text_input("Password", type="password", key="signup_pass")
        if st.button("Create Account", use_container_width=True):
            success, msg = signup(email, password)
            if success: st.success(msg)
            else: st.error(msg)
