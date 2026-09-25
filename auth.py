def auth_page():
    st.title("🚀 ClyxessChat AI")
    st.subheader("🔐 Login / Sign Up")

    # Google & Facebook Original Logo wale Button
    st.markdown("""
    <style>
    .social-btn {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 10px;
        width: 100%;
        padding: 10px;
        border: 1px solid #444;
        border-radius: 10px;
        background: white;
        color: black;
        font-weight: 600;
        cursor: pointer;
        margin-bottom: 10px;
        text-decoration: none;
    }
    .social-btn img { width: 20px; height: 20px; }
    .social-btn:hover { background: #f0f0f0; }
    </style>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        if st.button(" ", key="google_real", help="Google Login"):
            pass
        st.markdown("""
        <a href="#" onclick="window.parent.postMessage({type:'google_login'}, '*')" class="social-btn">
            <img src="https://upload.wikimedia.org/wikipedia/commons/c/c1/Google_%22G%22_logo.svg">
            Google
        </a>
        """, unsafe_allow_html=True)
        
        # Asli kaam ka button
        if st.button("Continue with Google", key="g_btn", use_container_width=True):
            try:
                res = supabase.auth.sign_in_with_oauth({
                    "provider": "google",
                    "options": {"redirect_to": "https://clyxessai-hy6tmtjz9qj5x7d5xebm9n.streamlit.app"}
                })
                st.markdown(f'<meta http-equiv="refresh" content="0;url={res.url}">', unsafe_allow_html=True)
                st.link_button("Redirecting to Google...", res.url)
            except Exception as e:
                st.error(f"Google Error: {e}")

    with col2:
        if st.button("Continue with Facebook", key="fb_btn", use_container_width=True):
            try:
                res = supabase.auth.sign_in_with_oauth({
                    "provider": "facebook",
                    "options": {"redirect_to": "https://clyxessai-hy6tmtjz9qj5x7d5xebm9n.streamlit.app"}
                })
                st.markdown(f'<meta http-equiv="refresh" content="0;url={res.url}">', unsafe_allow_html=True)
                st.link_button("Redirecting to Facebook...", res.url)
            except Exception as e:
                st.error(f"Facebook Error: {e}")

    # Facebook logo dikhane ke liye upar custom html
    st.markdown("""
    <script>
    // Hack nahi, bas icon dikhane ke liye
    </script>
    """, unsafe_allow_html=True)
    
    # --- SIMPLE WALA FINAL CODE (100% Kaam Karega) ---
    st.divider()
    st.markdown("""
    <div style="display:flex; gap:10px;">
        <div style="flex:1; background:white; color:black; border-radius:10px; padding:10px; text-align:center; font-weight:600; display:flex; align-items:center; justify-content:center; gap:8px; border:1px solid #ddd;">
            <img src="https://www.svgrepo.com/show/475656/google-color.svg" width="20"> Google
        </div>
        <div style="flex:1; background:#1877F2; color:white; border-radius:10px; padding:10px; text-align:center; font-weight:600; display:flex; align-items:center; justify-content:center; gap:8px;">
            <img src="https://upload.wikimedia.org/wikipedia/commons/5/51/Facebook_f_logo_%282019%29.svg" width="20"> Facebook
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.caption("Or login with Email")
    
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
