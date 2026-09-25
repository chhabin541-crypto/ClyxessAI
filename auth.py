def auth_page():
    st.title("🚀 ClyxessChat AI")
    st.subheader("🔐 Login / Sign Up")
    
    # ===== GOOGLE LOGIN BUTTON =====
    st.markdown("### Continue with")
    if st.button("🔵 Continue with Google", use_container_width=True):
        try:
            # Supabase se Google OAuth URL lelo
            res = supabase.auth.sign_in_with_oauth({
                "provider": "google",
                "options": {
                    "redirect_to": "https://clyxessai-hy6tmtjz9qj5x7d5xebm9n.streamlit.app"
                }
            })
            # Google pe redirect
            st.markdown(f'<meta http-equiv="refresh" content="0;url={res.url}">', unsafe_allow_html=True)
            st.link_button("Google pe jao", res.url, use_container_width=True)
        except Exception as e:
            st.error(f"Google Login Error: {e}")
    
    st.divider()
    st.caption("Or login with Email")
    
    tab1, tab2 = st.tabs(["Login", "Sign Up"])
    with tab1:
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_pass")
        if st.button("Login", use_container_width=True):
            if not email or not password:
                st.warning("Email/Password bharo")
            else:
                success, msg = login(email, password)
                if success:
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)
    with tab2:
        email = st.text_input("Email", key="signup_email")
        password = st.text_input("Password", type="password", key="signup_pass")
        if st.button("Create Account", use_container_width=True):
            if not email or not password:
                st.warning("Email/Password bharo")
            else:
                success, msg = signup(email, password)
                if success:
                    st.success(msg)
                    st.info("Email check karo verification ke liye")
                else:
                    st.error(msg)
