import streamlit as st
import bcrypt
from database import get_farmer_by_phone, create_farmer, get_admin_by_username, log_admin_action
from translations import get_text, STATES
from i18n_utils import t


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode(), hashed.encode())
    except Exception:
        return False


def show_login_page():
    lang = st.session_state.get("language", "en")

    col1, col2, col3 = st.columns([1, 3, 1])
    with col2:
        st.markdown(
            f"""
        <div style='text-align:center; margin-bottom:2rem;'>
            <div style='font-size:2.5rem; font-weight:700; color:#39d353;'>🌾 Smart Kisan</div>
            <div style='color:#8b949e;'>{t('empowering_farmers', lang)}</div>
        </div>
        """,
            unsafe_allow_html=True,
        )

        if st.button(f"🌐 {get_text('change_language')}", use_container_width=False):
            st.session_state.page = "language_select"
            st.rerun()

    st.markdown("<hr style='border:1px solid #30363d; margin:1rem 0;'>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(
            f"<div style='text-align:center; font-size:1.1rem; color:#8b949e; margin-bottom:1rem;'>{get_text('select_user_type')}</div>",
            unsafe_allow_html=True,
        )

        if "auth_user_type" not in st.session_state:
            st.session_state.auth_user_type = "Farmer"

        uc1, uc2 = st.columns(2)
        with uc1:
            if st.button(f"👨‍🌾 {get_text('farmer')}", use_container_width=True):
                st.session_state.auth_user_type = "Farmer"
                st.session_state.auth_mode = "login"
                st.rerun()
        with uc2:
            if st.button(f"🔧 {get_text('admin')}", use_container_width=True):
                st.session_state.auth_user_type = "Admin"
                st.session_state.auth_mode = "login"
                st.rerun()

        user_type = st.session_state.auth_user_type
        st.markdown(
            f"""
        <div style='text-align:center; margin:0.5rem 0;'>
            <span style='background:rgba(57,211,83,0.15); border:1px solid #39d353; border-radius:20px;
            padding:0.25rem 1rem; color:#39d353; font-size:0.85rem;'>
            {t('selected_user_type', lang)}: {"👨‍🌾 " + get_text('farmer') if user_type=="Farmer" else "🔧 " + get_text('admin')}
            </span>
        </div>
        """,
            unsafe_allow_html=True,
        )

        st.markdown("<hr style='border:1px solid #30363d; margin:1rem 0;'>", unsafe_allow_html=True)

        if user_type == "Farmer":
            _show_farmer_auth(lang)
        else:
            _show_admin_auth(lang)


def _show_farmer_auth(lang):
    if "auth_mode" not in st.session_state:
        st.session_state.auth_mode = "login"

    mode = st.session_state.auth_mode

    if mode == "login":
        st.markdown(
            f"<div style='text-align:center; font-size:1.3rem; font-weight:600; color:#e6edf3; margin-bottom:1rem;'>👨‍🌾 {get_text('login')}</div>",
            unsafe_allow_html=True,
        )

        phone = st.text_input(f"📱 {get_text('phone')}", placeholder="e.g. 9876543210", key="login_phone")
        password = st.text_input(f"🔒 {get_text('password')}", type="password", key="login_pass")

        if st.button(f"→ {get_text('login_btn')}", use_container_width=True):
            if phone and password:
                farmer = get_farmer_by_phone(phone.strip())
                if farmer and verify_password(password, farmer["password_hash"]):
                    st.session_state.logged_in = True
                    st.session_state.user_type = "farmer"
                    st.session_state.user_data = farmer
                    st.session_state.page = "farmer_dashboard"
                    st.rerun()
                else:
                    st.error(f"❌ {get_text('invalid_credentials')}")
            else:
                st.warning(f"⚠️ {get_text('fill_all')}")

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button(f"📝 {get_text('no_account')}", use_container_width=True):
            st.session_state.auth_mode = "register"
            st.rerun()

    else:
        st.markdown(
            f"<div style='text-align:center; font-size:1.3rem; font-weight:600; color:#e6edf3; margin-bottom:1rem;'>📝 {get_text('register')}</div>",
            unsafe_allow_html=True,
        )

        name = st.text_input(f"👤 {get_text('name')}", placeholder=get_text("name"), key="reg_name")
        phone = st.text_input(f"📱 {get_text('phone')}", placeholder="10-digit mobile number", key="reg_phone")
        state = st.selectbox(f"🗺️ {get_text('state')}", [""] + STATES, key="reg_state")
        district = st.text_input(f"📍 {get_text('district')}", placeholder=get_text("district"), key="reg_district")
        password = st.text_input(f"🔒 {get_text('password')}", type="password", key="reg_pass")
        confirm = st.text_input(f"🔒 {t('confirm_password', lang)}", type="password", key="reg_confirm")

        if st.button(f"✅ {get_text('register_btn')}", use_container_width=True):
            if all([name, phone, state, district, password, confirm]):
                if len(phone.strip()) != 10 or not phone.strip().isdigit():
                    st.error(f"❌ {t('valid_phone_error', lang)}")
                elif password != confirm:
                    st.error(f"❌ {t('password_mismatch', lang)}")
                else:
                    try:
                        ph = hash_password(password)
                        create_farmer(name.strip(), phone.strip(), state, district.strip(), ph)
                        st.success(f"✅ {get_text('register_success')}")
                        import time

                        time.sleep(1)
                        st.session_state.auth_mode = "login"
                        st.rerun()
                    except Exception as e:
                        if "UNIQUE" in str(e):
                            st.error(f"❌ {get_text('phone_exists')}")
                        else:
                            st.error(f"❌ {t('error_label', lang)}: {e}")
            else:
                st.warning(f"⚠️ {get_text('fill_all')}")

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button(f"← {get_text('have_account')}", use_container_width=True):
            st.session_state.auth_mode = "login"
            st.rerun()


def _show_admin_auth(lang):
    st.markdown(
        f"<div style='text-align:center; font-size:1.3rem; font-weight:600; color:#e6edf3; margin-bottom:1rem;'>🔧 {get_text('admin')} {get_text('login')}</div>",
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
    <div class='alert-info'>
        🔐 {t('admin_access_notice', lang)}
    </div>
    """,
        unsafe_allow_html=True,
    )

    st.markdown("<br>", unsafe_allow_html=True)
    username = st.text_input(f"👤 {get_text('admin_id')}", placeholder="admin", key="admin_user")
    password = st.text_input(f"🔒 {get_text('admin_password')}", type="password", key="admin_pass")

    if st.button(f"🔑 {get_text('login_btn')}", use_container_width=True):
        if username and password:
            admin = get_admin_by_username(username.strip())
            if admin and verify_password(password, admin["password_hash"]):
                st.session_state.logged_in = True
                st.session_state.user_type = "admin"
                st.session_state.user_data = admin
                st.session_state.page = "admin_dashboard"
                log_admin_action(username, "LOGIN", "Admin logged in")
                st.rerun()
            else:
                st.error(f"❌ {t('invalid_admin_credentials', lang)}")
        else:
            st.warning(f"⚠️ {get_text('fill_all')}")

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        f"""
    <div style='text-align:center; color:#8b949e; font-size:0.85rem;'>
        {t('default_credentials', lang)}
    </div>
    """,
        unsafe_allow_html=True,
    )
