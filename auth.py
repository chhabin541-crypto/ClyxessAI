import streamlit as st

if "user" not in st.session_state:
    st.session_state.user = None

def _get_supabase():
    try:
        from supabase import create_client
        url = st.secrets.get("SUPABASE_URL")
        key = st.secrets.get("SUPABASE_ANON_KEY") or st.secrets.get("SUPABASE_KEY")
        if not url or not key:
            return None
        return create_client(url, key)
    except Exception:
        return None

def login(email, password):
    sb = _get_supabase()
    if not sb:
        return False, "Supabase keys missing. Secrets check karo."
    try:
        res = sb.auth.sign_in_with_password({"email": email, "password": password})
        st.session_state.user = res.user
        return True, "Login OK"
    except Exception as e:
        return False, str(e)

def signup(email, password):
    sb = _get_supabase()
    if not sb:
        return False, "Supabase keys missing."
    try:
        sb.auth.sign_up({"email": email, "password": password})
        return True, "Signup OK - Email verify karo"
    except Exception as e:
        return False, str(e)

def logout():
    sb = _get_supabase()
    if sb:
        try: sb.auth.sign_out()
        except: pass
    st.session_state.user = None
    st.rerun()

def show_user_sidebar():
    with st.sidebar:
        if st.session_state.get("user") is None:
            st.warning("🔒 Not Logged In")
        else:
            try:
                st.success(f"👤 {st.session_state.user.email}")
            except:
                st.success("👤 Logged In")
            if st.button("🚪 Logout", use_container_width=True):
                logout()

def auth_page():
    st.title("🚀 ClyxessChat AI")
    
    # --- ORIGINAL LOGO WALE BUTTONS ---
    st.markdown("### Continue with")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("🔵 Google Login", use_container_width=True):
            sb = _get_supabase()
            if sb:
                try:
                    res = sb.auth.sign_in_with_oauth({
                        "provider": "google",
                        "options": {"redirect_to": "https://clyxessai-hy6tmtjz9qj5x7d5xebm9n.streamlit.app"}
                    })
                    st.link_button("Open Google", res.url, use_container_width=True)
                except Exception as e:
                    st.error(str(e))
            else:
                st.error("Supabase keys nahi hai")
    with c2:
        if st.button("🔷 Facebook Login", use_container_width=True):
            sb = _get_supabase()
            if sb:
                try:
                    res = sb.auth.sign_in_with_oauth({
                        "provider": "facebook",
                        "options": {"redirect_to": "https://clyxessai-hy6tmtjz9qj5x7d5xebm9n.streamlit.app"}
                    })
                    st.link_button("Open Facebook", res.url, use_container_width=True)
                except Exception as e:
                    st.error(str(e))

    st.divider()
    tab1, tab2 = st.tabs(["Login", "Sign Up"])
    with tab1:
        e = st.text_input("Email", key="l_e")
        p = st.text_input("Password", type="password", key="l_p")
        if st.button("Login", use_container_width=True):
            ok, msg = login(e, p)
            if ok: st.rerun()
            else: st.error(msg)
    with tab2:
        e = st.text_input("Email", key="s_e")
        p = st.text_input("Password", type="password", key="s_p")
        if st.button("Create Account", use_container_width=True):
            ok, msg = signup(e, p)
            if ok: st.success(msg)
            else: st.error(msg)
