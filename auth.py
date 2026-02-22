import streamlit as st
import bcrypt
from database import get_farmer_by_phone, create_farmer, get_admin_by_username, log_admin_action
from translations import get_text, STATES
from i18n_utils import t

G  = "#2e7d32"
M  = "#4a7a5a"
B  = "#c8e3cf"
BG = "#f3fbf4"

def hash_password(p): return bcrypt.hashpw(p.encode(), bcrypt.gensalt()).decode()
def verify_password(p, h):
    try: return bcrypt.checkpw(p.encode(), h.encode())
    except: return False

def show_login_page():
    lang = st.session_state.get("language","en")
    col1,col2,col3 = st.columns([1,3,1])
    with col2:
        st.markdown(f"""
        <div style='text-align:center;margin-bottom:2rem;background:#ffffff;border:1px solid {B};
            border-radius:16px;padding:2rem;box-shadow:0 4px 16px rgba(30,90,50,0.09);'>
            <div style='font-size:2.5rem;font-weight:700;color:{G};'>💧 Smart KisanJal</div>
            <div style='color:{M};font-size:1rem;margin-top:0.4rem;'>{t('empowering_farmers',lang)}</div>
        </div>""", unsafe_allow_html=True)
        if st.button(f"🌐 {get_text('change_language')}", use_container_width=False):
            st.session_state.page = "language_select"; st.rerun()

    st.markdown(f"<hr style='border:1px solid {B};margin:1rem 0;'>", unsafe_allow_html=True)

    col1,col2,col3 = st.columns([1,2,1])
    with col2:
        st.markdown(f"<div style='text-align:center;font-size:1.1rem;color:{M};margin-bottom:1rem;'>{get_text('select_user_type')}</div>", unsafe_allow_html=True)
        if "auth_user_type" not in st.session_state: st.session_state.auth_user_type = "Farmer"
        uc1,uc2 = st.columns(2)
        with uc1:
            if st.button(f"👨‍🌾 {get_text('farmer')}", use_container_width=True):
                st.session_state.auth_user_type = "Farmer"; st.session_state.auth_mode = "login"; st.rerun()
        with uc2:
            if st.button(f"🔧 {get_text('admin')}", use_container_width=True):
                st.session_state.auth_user_type = "Admin"; st.session_state.auth_mode = "login"; st.rerun()

        user_type = st.session_state.auth_user_type
        label = ("👨‍🌾 " + get_text('farmer')) if user_type=="Farmer" else ("🔧 " + get_text('admin'))
        st.markdown(f"""<div style='text-align:center;margin:0.5rem 0;'>
            <span style='background:rgba(46,125,50,0.10);border:1px solid {B};border-radius:20px;
            padding:0.25rem 1rem;color:{G};font-size:0.85rem;font-weight:600;'>
            {t('selected_user_type',lang)}: {label}</span></div>""", unsafe_allow_html=True)

        st.markdown(f"<hr style='border:1px solid {B};margin:1rem 0;'>", unsafe_allow_html=True)
        if user_type == "Farmer": _show_farmer_auth(lang)
        else: _show_admin_auth(lang)


def _show_farmer_auth(lang):
    if "auth_mode" not in st.session_state: st.session_state.auth_mode = "login"
    mode = st.session_state.auth_mode

    if mode == "login":
        st.markdown(f"<div style='text-align:center;font-size:1.3rem;font-weight:700;color:{G};margin-bottom:1rem;'>👨‍🌾 {get_text('login')}</div>", unsafe_allow_html=True)
        phone    = st.text_input(f"📱 {get_text('phone')}", placeholder="e.g. 9876543210", key="login_phone")
        password = st.text_input(f"🔒 {get_text('password')}", type="password", key="login_pass")
        if st.button(f"→ {get_text('login_btn')}", use_container_width=True):
            if phone and password:
                farmer = get_farmer_by_phone(phone.strip())
                if farmer and verify_password(password, farmer["password_hash"]):
                    st.session_state.update(logged_in=True,user_type="farmer",user_data=farmer,page="farmer_dashboard"); st.rerun()
                else: st.error(f"❌ {get_text('invalid_credentials')}")
            else: st.warning(f"⚠️ {get_text('fill_all')}")
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button(f"📝 {get_text('no_account')}", use_container_width=True):
            st.session_state.auth_mode = "register"; st.rerun()
    else:
        st.markdown(f"<div style='text-align:center;font-size:1.3rem;font-weight:700;color:{G};margin-bottom:1rem;'>📝 {get_text('register')}</div>", unsafe_allow_html=True)
        name     = st.text_input(f"👤 {get_text('name')}", key="reg_name")
        phone    = st.text_input(f"📱 {get_text('phone')}", placeholder="10-digit", key="reg_phone")
        state    = st.selectbox(f"🗺️ {get_text('state')}", [""]+STATES, key="reg_state")
        district = st.text_input(f"📍 {get_text('district')}", key="reg_district")
        password = st.text_input(f"🔒 {get_text('password')}", type="password", key="reg_pass")
        confirm  = st.text_input(f"🔒 {t('confirm_password',lang)}", type="password", key="reg_confirm")
        if st.button(f"✅ {get_text('register_btn')}", use_container_width=True):
            if all([name,phone,state,district,password,confirm]):
                if len(phone.strip())!=10 or not phone.strip().isdigit(): st.error(f"❌ {t('valid_phone_error',lang)}")
                elif password!=confirm: st.error(f"❌ {t('password_mismatch',lang)}")
                else:
                    try:
                        create_farmer(name.strip(),phone.strip(),state,district.strip(),hash_password(password))
                        st.success(f"✅ {get_text('register_success')}")
                        import time; time.sleep(1)
                        st.session_state.auth_mode="login"; st.rerun()
                    except Exception as e:
                        st.error(f"❌ {get_text('phone_exists')}" if "UNIQUE" in str(e) else f"❌ {e}")
            else: st.warning(f"⚠️ {get_text('fill_all')}")
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button(f"← {get_text('have_account')}", use_container_width=True):
            st.session_state.auth_mode="login"; st.rerun()


def _show_admin_auth(lang):
    st.markdown(f"<div style='text-align:center;font-size:1.3rem;font-weight:700;color:{G};margin-bottom:1rem;'>🔧 {get_text('admin')} {get_text('login')}</div>", unsafe_allow_html=True)
    st.markdown(f"<div style='background:#eefaf1;border:1px solid {B};border-radius:10px;padding:0.95rem;color:{G};margin:0.5rem 0;'>🔐 {t('admin_access_notice',lang)}</div>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    username = st.text_input(f"👤 {get_text('admin_id')}", placeholder="admin", key="admin_user")
    password = st.text_input(f"🔒 {get_text('admin_password')}", type="password", key="admin_pass")
    if st.button(f"🔑 {get_text('login_btn')}", use_container_width=True):
        if username and password:
            admin = get_admin_by_username(username.strip())
            if admin and verify_password(password, admin["password_hash"]):
                st.session_state.update(logged_in=True,user_type="admin",user_data=admin,page="admin_dashboard")
                log_admin_action(username,"LOGIN","Admin logged in"); st.rerun()
            else: st.error(f"❌ {t('invalid_admin_credentials',lang)}")
        else: st.warning(f"⚠️ {get_text('fill_all')}")
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f"<div style='text-align:center;color:{M};font-size:0.85rem;'>{t('default_credentials',lang)}</div>", unsafe_allow_html=True)
