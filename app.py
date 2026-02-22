import streamlit as st
from database import init_db
from translations import get_text
import auth
import farmer_dashboard
import admin_dashboard

# --- Page Config ---
st.set_page_config(
    page_title="Smart KisanJal",
    page_icon="💧",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── Master Light Theme CSS ─────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&family=Noto+Sans+Devanagari:wght@400;600;700&display=swap');

/* ════════════════════════════════════════════════════════
   ROOT VARIABLES
════════════════════════════════════════════════════════ */
:root {
    --bg:       #f3fbf4;
    --bg2:      #e7f6ea;
    --card:     #ffffff;
    --green:    #43a047;
    --dark:     #2e7d32;
    --text:     #163a2f;
    --muted:    #4a7a5a;
    --border:   #c8e3cf;
    --shadow:   0 4px 16px rgba(30,90,50,0.09);
}

/* ════════════════════════════════════════════════════════
   FORCE LIGHT BACKGROUND ON EVERY STREAMLIT WRAPPER
════════════════════════════════════════════════════════ */
html, body,
.stApp,
[data-testid="stApp"],
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
[data-testid="stMainBlockContainer"],
[data-testid="stVerticalBlock"],
[data-testid="stHorizontalBlock"],
[data-testid="stBottom"],
[data-testid="stHeader"],
[data-testid="stDecoration"],
[data-testid="stToolbar"],
section.main,
.main,
.block-container,
div[class^="css"] {
    background-color: var(--bg) !important;
    background: var(--bg) !important;
    color: var(--text) !important;
}

.stApp {
    background:
        radial-gradient(circle at 10% 8%, #eef9f1 0%, transparent 38%),
        radial-gradient(circle at 95% 92%, #e1f4e7 0%, transparent 28%),
        var(--bg) !important;
}

/* ════════════════════════════════════════════════════════
   SIDEBAR
════════════════════════════════════════════════════════ */
[data-testid="stSidebar"],
[data-testid="stSidebar"] > div,
[data-testid="stSidebar"] > div > div {
    background-color: var(--bg2) !important;
    border-right: 1px solid var(--border) !important;
}

/* ════════════════════════════════════════════════════════
   FORCE ALL TEXT TO DARK GREEN (never white-on-white)
════════════════════════════════════════════════════════ */
*, *::before, *::after,
p, span, label, div, h1, h2, h3, h4, h5, h6,
li, a, small, td, th, pre, code,
input, textarea, select, option, button {
    color: var(--text) !important;
    font-family: 'Poppins', 'Noto Sans Devanagari', sans-serif !important;
}

/* ════════════════════════════════════════════════════════
   INPUTS & TEXTAREAS
════════════════════════════════════════════════════════ */
input, textarea,
[data-baseweb="input"] input,
[data-baseweb="textarea"] textarea,
.stTextInput input,
.stTextArea textarea,
.stNumberInput input {
    background-color: #ffffff !important;
    color: var(--text) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
}
input:focus, textarea:focus {
    border-color: var(--green) !important;
    box-shadow: 0 0 0 3px rgba(67,160,71,0.15) !important;
    outline: none !important;
}

/* ════════════════════════════════════════════════════════
   SELECTBOX / DROPDOWNS
════════════════════════════════════════════════════════ */
[data-baseweb="select"] > div,
[data-baseweb="select"] > div > div {
    background-color: #ffffff !important;
    color: var(--text) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
}
[data-baseweb="popover"],
[data-baseweb="popover"] div,
[data-baseweb="menu"],
[role="listbox"],
[role="option"] {
    background-color: #ffffff !important;
    color: var(--text) !important;
}
[role="option"]:hover {
    background-color: var(--bg2) !important;
}

/* ════════════════════════════════════════════════════════
   BUTTONS
════════════════════════════════════════════════════════ */
.stButton > button {
    background: linear-gradient(135deg, #59b66e, #3f9c56) !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 0.6rem 1rem !important;
    font-weight: 600 !important;
    font-size: 0.92rem !important;
    width: 100% !important;
    min-height: 44px !important;
    box-shadow: 0 4px 12px rgba(53,128,67,0.22) !important;
    transition: all 0.2s ease !important;
}
.stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 18px rgba(53,128,67,0.32) !important;
}
.stButton > button p { color: #ffffff !important; margin: 0 !important; }
.stButton { width: 100% !important; }

/* ════════════════════════════════════════════════════════
   TABS
════════════════════════════════════════════════════════ */
.stTabs [data-baseweb="tab-list"] {
    background: #e9f5ec !important;
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
    padding: 0.2rem !important;
    gap: 0.25rem !important;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 9px !important;
    color: var(--muted) !important;
    font-weight: 600 !important;
    background: transparent !important;
}
.stTabs [aria-selected="true"] {
    background: var(--dark) !important;
    color: #ffffff !important;
}
.stTabs [aria-selected="true"] p { color: #ffffff !important; }

/* ════════════════════════════════════════════════════════
   EXPANDERS
════════════════════════════════════════════════════════ */
[data-testid="stExpander"],
.streamlit-expanderHeader {
    background-color: #ffffff !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    color: var(--text) !important;
}
.streamlit-expanderContent {
    background-color: var(--bg2) !important;
    border: 1px solid var(--border) !important;
}

/* ════════════════════════════════════════════════════════
   ALERTS / INFO / SUCCESS / WARNING / ERROR
════════════════════════════════════════════════════════ */
[data-testid="stAlert"],
.stAlert, .stSuccess, .stInfo, .stWarning, .stError,
div[data-baseweb="notification"] {
    background-color: #eefaf1 !important;
    border: 1px solid var(--border) !important;
    color: var(--text) !important;
    border-radius: 10px !important;
}

/* ════════════════════════════════════════════════════════
   RADIO BUTTONS
════════════════════════════════════════════════════════ */
.stRadio > div { flex-direction: row; gap: 1rem; }
.stRadio > div > label {
    background: var(--card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    padding: 0.5rem 1rem !important;
    color: var(--text) !important;
}

/* ════════════════════════════════════════════════════════
   DATAFRAMES
════════════════════════════════════════════════════════ */
.dataframe, [data-testid="stDataFrame"] {
    background: var(--card) !important;
    color: var(--text) !important;
}

/* ════════════════════════════════════════════════════════
   HERO / CARDS / COMPONENTS
════════════════════════════════════════════════════════ */
.hero-container {
    background: linear-gradient(130deg, #f7fff8 0%, #edf9f0 55%, #e4f5e8 100%);
    border: 1px solid var(--border);
    border-radius: 18px;
    padding: 2.6rem 1.8rem;
    text-align: center;
    margin-bottom: 1.35rem;
    box-shadow: var(--shadow);
}
.hero-title {
    font-size: clamp(2rem, 4vw, 2.8rem) !important;
    font-weight: 700 !important;
    color: var(--dark) !important;
    margin-bottom: 0.45rem;
    letter-spacing: -0.4px;
}
.hero-subtitle {
    font-size: 1.05rem;
    color: var(--muted) !important;
    margin-bottom: 0.25rem;
}
.kisan-card {
    background: var(--card);
    border: 1px solid var(--border) !important;
    border-radius: 14px;
    padding: 1.15rem;
    margin-bottom: 0.85rem;
    box-shadow: var(--shadow);
    transition: transform 0.2s ease;
}
.kisan-card:hover { transform: translateY(-1px); }
.metric-card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1rem;
    text-align: center;
    box-shadow: var(--shadow);
}
.metric-value { font-size: 1.8rem; font-weight: 700; color: var(--green) !important; }
.metric-label { font-size: 0.85rem; color: var(--muted) !important; margin-top: 0.25rem; }

.alert-success { background:#eefaf1; border:1px solid #b7e0c1; border-radius:10px; padding:0.95rem; color:#2f7f44 !important; margin:0.5rem 0; }
.alert-info    { background:#edf9ef; border:1px solid #b7e0c1; border-radius:10px; padding:0.95rem; color:#1f5b40 !important; margin:0.5rem 0; }
.alert-warning { background:#effaf2; border:1px solid #b7e0c1; border-radius:10px; padding:0.95rem; color:#1f5b40 !important; margin:0.5rem 0; }
.green-divider { height:2px; background:linear-gradient(90deg,transparent,var(--green),transparent); margin:1.5rem 0; border:none; }

/* ════════════════════════════════════════════════════════
   TOPBAR PILLS
════════════════════════════════════════════════════════ */
#india-flag-topbar {
    position: fixed; top: 0.5rem; left: 1rem; z-index: 99999;
    display: flex; align-items: center; gap: 0.45rem;
    background: rgba(255,255,255,0.96); border: 1px solid var(--border);
    border-radius: 20px; padding: 0.28rem 0.85rem 0.28rem 0.6rem;
    box-shadow: 0 2px 10px rgba(30,90,50,0.12);
    pointer-events: none; user-select: none;
}
#india-flag-topbar .flag-emoji { font-size: 1.25rem; line-height: 1; }
#india-flag-topbar .flag-text  { font-size: 0.75rem; font-weight: 700; color: var(--text) !important; }

#topbar-login-pill {
    position: fixed; top: 1rem; right: 1.2rem; z-index: 99999;
    display: flex; align-items: center; gap: 0.5rem;
    background: linear-gradient(135deg, #43a047, #2e7d32);
    border: none; border-radius: 24px; padding: 0.55rem 1.4rem;
    box-shadow: 0 3px 14px rgba(46,125,50,0.32);
    cursor: pointer; transition: box-shadow 0.2s, transform 0.15s;
}
#topbar-login-pill:hover { box-shadow: 0 5px 18px rgba(46,125,50,0.42); transform: translateY(-1px); }
#topbar-login-pill span  { font-size: 0.92rem; font-weight: 700; color: #ffffff !important; }

/* ════════════════════════════════════════════════════════
   SCROLLBAR / MISC
════════════════════════════════════════════════════════ */
#MainMenu { visibility: hidden; }
footer    { visibility: hidden; }
header    { visibility: hidden; }
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 3px; }

.main .block-container { padding-top: 1.5rem; padding-bottom: 2.25rem; max-width: 1200px; }

/* ════════════════════════════════════════════════════════
   HIDE TOPBAR TRIGGER BUTTONS (TOPBAR_LOGOUT / TOPBAR_LOGIN)
   These are functional Streamlit buttons hidden visually;
   the visible pill above triggers them via JS onclick.
════════════════════════════════════════════════════════ */
/* Hide the button block that contains TOPBAR_LOGOUT or TOPBAR_LOGIN */
.stButton:has(button p):not(:has(button p:empty)) button p {
    /* visible by default */
}

</style>
""", unsafe_allow_html=True)

# Initialize database
init_db()

def show_topbar():
    logged_in = st.session_state.get("logged_in", False)
    page      = st.session_state.get("page", "language_select")
    show_logout_btn = logged_in
    show_login_btn  = not logged_in and page not in ("login", "language_select")

    st.markdown("""
    <div id="india-flag-topbar">
        <span class="flag-emoji">🇮🇳</span>
        <span class="flag-text">India</span>
    </div>""", unsafe_allow_html=True)

    action_key = f"topbar_btn_{page}"

    if show_logout_btn:
        st.markdown("""
        <div id="topbar-login-pill" onclick="
            Array.from(window.parent.document.querySelectorAll('button')).find(
                b => b.innerText.trim() === 'TOPBAR_LOGOUT')?.click();">
            <span>🚪 Logout</span>
        </div>""", unsafe_allow_html=True)
        if st.button("TOPBAR_LOGOUT", key=action_key):
            from database import log_admin_action as _log
            if st.session_state.get("user_type") == "admin":
                try: _log(st.session_state.user_data["username"], "LOGOUT", "Logged out via topbar")
                except: pass
            for k in ["logged_in","user_type","user_data"]:
                st.session_state[k] = None
            st.session_state.logged_in = False
            st.session_state.page = "language_select"
            st.rerun()

    elif show_login_btn:
        st.markdown("""
        <div id="topbar-login-pill" onclick="
            Array.from(window.parent.document.querySelectorAll('button')).find(
                b => b.innerText.trim().startsWith('TOPBAR_LOGIN'))?.click();">
            <span>🔐 Login</span>
        </div>""", unsafe_allow_html=True)
        st.markdown("<div style='position:fixed;top:-9999px;left:-9999px;width:1px;height:1px;overflow:hidden;'>", unsafe_allow_html=True)
        if st.button("TOPBAR_LOGIN", key=action_key):
            st.session_state.page = "login"
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    else:
        st.markdown("""
        <div id="topbar-login-pill" style="cursor:default;">
            <span>💧 Smart KisanJal</span>
        </div>""", unsafe_allow_html=True)

# --- Session State ---
def init_session():
    for k, v in {'language':None,'logged_in':False,'user_type':None,'user_data':None,'page':'language_select'}.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_session()
page = st.session_state.page
show_topbar()

# Inject JS to hide the TOPBAR_LOGOUT/TOPBAR_LOGIN trigger buttons after render
st.markdown("""<script>
(function(){
  function hideBtn(){
    try {
      var btns=window.parent.document.querySelectorAll('button');
      btns.forEach(function(b){
        var t=b.innerText.trim();
        if(t==='TOPBAR_LOGOUT'||t==='TOPBAR_LOGIN'){
          // Hide the button itself
          b.style.cssText='position:fixed!important;top:-9999px!important;left:-9999px!important;width:1px!important;height:1px!important;overflow:hidden!important;opacity:0!important;pointer-events:auto!important;';
          // Walk up and hide the stVerticalBlock container
          var el=b;
          for(var i=0;i<8;i++){
            el=el.parentElement;
            if(!el) break;
            if(el.className&&el.className.indexOf('stVerticalBlock')>-1){
              el.style.cssText='position:fixed!important;top:-9999px!important;left:-9999px!important;height:1px!important;width:1px!important;overflow:hidden!important;';
              break;
            }
          }
        }
      });
    } catch(e){}
  }
  hideBtn();
  setTimeout(hideBtn,100);
  setTimeout(hideBtn,500);
  setTimeout(hideBtn,1500);
  var mo=new MutationObserver(hideBtn);
  mo.observe(window.parent.document.body,{childList:true,subtree:true});
})();
</script>""", unsafe_allow_html=True)

# ── ROUTER ─────────────────────────────────────────────────────────────────────
if page == 'language_select':
    st.markdown("""
    <div class="hero-container">
        <div class="hero-title">💧 Smart KisanJal</div>
        <div class="hero-subtitle">Empowering Farmers with Smart Technology</div>
        <div class="hero-subtitle" style="font-family:'Noto Sans Devanagari',sans-serif;">किसानों को स्मार्ट तकनीक से सशक्त बनाना</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(
        "<div style='text-align:center;font-size:1.08rem;color:#4c6f60;margin-bottom:1.6rem;'>"
        "Please select your preferred language</div>",
        unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        lcol1, lcol2, lcol3 = st.columns(3)
        lang_map = [
            (lcol1, "English", "en"), (lcol2, "हिंदी", "hi"), (lcol3, "বাংলা", "bn"),
            (lcol1, "मराठी", "mr"),   (lcol2, "ગુજરાતી","gu"), (lcol3, "தமிழ்","ta"),
        ]
        for col, label, code in lang_map:
            with col:
                if st.button(label, use_container_width=True, key=f"lang_{code}"):
                    st.session_state.language = code
                    st.session_state.page = 'login'
                    st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("""
        <div class='kisan-card' style='text-align:center;'>
            <div style='color:#4f6f61;font-size:0.9rem;'>
                Irrigation Planning &nbsp;|&nbsp; Government Schemes &nbsp;|&nbsp; Complaint Management<br>
                सिंचाई योजना &nbsp;|&nbsp; सरकारी योजनाएं &nbsp;|&nbsp; शिकायत प्रबंधन
            </div>
        </div>""", unsafe_allow_html=True)

elif page == 'login':
    auth.show_login_page()

elif page == 'farmer_dashboard':
    farmer_dashboard.show()

elif page == 'admin_dashboard':
    admin_dashboard.show()
