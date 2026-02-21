
import streamlit as st
from database import init_db
from translations import get_text
import auth
import farmer_dashboard
import admin_dashboard

# --- Page Config ---
st.set_page_config(
    page_title="Smart Kisan Platform",
    page_icon="SK",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- Custom CSS ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&family=Noto+Sans+Devanagari:wght@400;600;700&display=swap');
:root {
    --bg-primary: #f3fbf4;
    --bg-secondary: #e7f6ea;
    --bg-card: #ffffff;
    --accent-green: #43a047;
    --accent-dark: #2e7d32;
    --text-primary: #163a2f;
    --text-secondary: #2a5a46;
    --border: #c8e3cf;
    --warning: #3f8f56;
    --danger: #2e7d32;
    --info: #3b8d52;
    --shadow-soft: 0 10px 24px rgba(30, 90, 50, 0.08);
}

* { font-family: 'Poppins', 'Noto Sans Devanagari', sans-serif; }

.stApp {
    background:
        radial-gradient(circle at 10% 8%, #eef9f1 0%, transparent 38%),
        radial-gradient(circle at 95% 92%, #e1f4e7 0%, transparent 28%),
        var(--bg-primary) !important;
    color: var(--text-primary) !important;
}

.main .block-container {
    padding-top: 1.5rem;
    padding-bottom: 2.25rem;
    max-width: 1200px;
}

.kisan-card {
    background: var(--bg-card);
    border: 1px solid var(--border) !important;
    border-radius: 14px;
    padding: 1.15rem;
    margin-bottom: 0.85rem;
    box-shadow: var(--shadow-soft);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.kisan-card:hover { transform: translateY(-1px); }

.hero-container {
    background: linear-gradient(130deg, #f7fff8 0%, #edf9f0 55%, #e4f5e8 100%);
    border: 1px solid var(--border);
    border-radius: 18px;
    padding: 2.6rem 1.8rem;
    text-align: center;
    margin-bottom: 1.35rem;
    position: relative;
    overflow: hidden;
    box-shadow: var(--shadow-soft);
}
.hero-container::before {
    content: '';
    position: absolute;
    inset: -40%;
    background: radial-gradient(ellipse at center, rgba(67,160,71,0.08) 0%, transparent 62%);
    pointer-events: none;
}
.hero-title {
    font-size: clamp(2rem, 4vw, 2.8rem);
    font-weight: 700;
    color: var(--accent-green);
    margin-bottom: 0.45rem;
    letter-spacing: -0.4px;
}
.hero-subtitle {
    font-size: 1.05rem;
    color: var(--text-secondary);
    margin-bottom: 0.25rem;
}

.stButton > button {
    background: linear-gradient(135deg, #59b66e, #3f9c56) !important;
    color: #143629 !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 0.6rem 1rem !important;
    font-weight: 600 !important;
    font-size: 0.92rem !important;
    width: 100% !important;
    min-height: 44px !important;
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
    text-align: center !important;
    box-shadow: 0 8px 16px rgba(53, 128, 67, 0.24);
    transition: all 0.2s ease !important;
}
.stButton > button:hover {
    transform: translateY(-1px);
    box-shadow: 0 10px 18px rgba(53, 128, 67, 0.3);
}
.stButton {
    width: 100% !important;
}
.stButton > button p {
    margin: 0 !important;
    line-height: 1.2 !important;
}

.stTextInput > div > div > input,
.stSelectbox > div > div,
.stTextArea > div > div > textarea {
    background-color: #f6fcf7 !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    color: var(--text-primary) !important;
}
.stTextInput > div > div > input:focus,
.stSelectbox > div > div:focus {
    border-color: var(--accent-green) !important;
    box-shadow: 0 0 0 3px rgba(67,160,71,0.16) !important;
}

.metric-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1rem;
    text-align: center;
    box-shadow: var(--shadow-soft);
}
.metric-value {
    font-size: 1.8rem;
    font-weight: 700;
    color: var(--accent-green);
}
.metric-label {
    font-size: 0.85rem;
    color: var(--text-secondary);
    margin-top: 0.25rem;
}

.stTabs [data-baseweb="tab-list"] {
    background: #e9f5ec;
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 0.2rem;
    gap: 0.25rem;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 9px;
    color: var(--text-secondary);
    font-weight: 600;
}
.stTabs [aria-selected="true"] {
    background: var(--accent-dark) !important;
    color: #e9f7ed !important;
}

.css-1d391kg, [data-testid="stSidebar"] {
    background: var(--bg-secondary) !important;
    border-right: 1px solid var(--border) !important;
}

.alert-success {
    background: #eefaf1;
    border: 1px solid #b7e0c1;
    border-radius: 10px;
    padding: 0.95rem;
    color: #2f7f44;
    margin: 0.5rem 0;
}
.alert-info {
    background: #edf9ef;
    border: 1px solid #b7e0c1;
    border-radius: 10px;
    padding: 0.95rem;
    color: #1f5b40;
    margin: 0.5rem 0;
}
.alert-warning {
    background: #effaf2;
    border: 1px solid #b7e0c1;
    border-radius: 10px;
    padding: 0.95rem;
    color: #1f5b40;
    margin: 0.5rem 0;
}

.green-divider {
    height: 2px;
    background: linear-gradient(90deg, transparent, var(--accent-green), transparent);
    margin: 1.5rem 0;
    border: none;
}

#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
header { visibility: hidden; }

::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: var(--bg-primary); }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: var(--accent-dark); }

.dataframe { background: var(--bg-card) !important; color: var(--text-primary) !important; }
.stSelectbox [data-baseweb="select"] > div { background: var(--bg-secondary) !important; }
.stNumberInput > div > div > input { background: var(--bg-secondary) !important; color: var(--text-primary) !important; border: 1px solid var(--border) !important; border-radius: 8px !important; }
.stTextInput label, .stSelectbox label, .stTextArea label, .stNumberInput label, .stRadio label {
    color: var(--text-secondary) !important;
    font-size: 0.9rem !important;
}
.stRadio > div { flex-direction: row; gap: 1rem; }
.stRadio > div > label { background: var(--bg-card); border: 1px solid var(--border); border-radius: 8px; padding: 0.5rem 1rem; cursor: pointer; }
.streamlit-expanderHeader { background: var(--bg-card) !important; border: 1px solid var(--border) !important; border-radius: 8px !important; color: var(--text-primary) !important; }
.streamlit-expanderContent { background: var(--bg-secondary) !important; border: 1px solid var(--border) !important; border-bottom-left-radius: 8px !important; border-bottom-right-radius: 8px !important; }

/* Enforce project-wide text colors: black + green shades only */
html, body, .stApp,
h1, h2, h3, h4, h5, h6,
p, span, label, li, a, small,
div, th, td, input, textarea, select, option {
    color: var(--text-primary) !important;
}
.hero-title, .metric-value, .stTabs [aria-selected="true"], .streamlit-expanderHeader {
    color: var(--accent-dark) !important;
}
*[style*="color:"] {
    color: var(--text-secondary) !important;
}
</style>
""", unsafe_allow_html=True)

# Initialize database
init_db()

# --- Session State ---
def init_session():
    defaults = {
        'language': None,
        'logged_in': False,
        'user_type': None,
        'user_data': None,
        'page': 'language_select'
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_session()

# --- Router ---
page = st.session_state.page

if page == 'language_select':
    # LANGUAGE SELECTION PAGE
    st.markdown("""
    <div class="hero-container">
        <div class="hero-title">Smart Kisan Platform</div>
        <div class="hero-subtitle">Empowering Farmers with Smart Technology</div>
        <div class="hero-subtitle" style="font-family: 'Noto Sans Devanagari', sans-serif;">किसानों को स्मार्ट तकनीक से सशक्त बनाना</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(
        "<div style='text-align:center; font-size:1.08rem; color:#4c6f60; margin-bottom:1.6rem;'>"
        "Please select your preferred language"
        "</div>",
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("")
        lcol1, lcol2, lcol3 = st.columns(3)
        with lcol1:
            if st.button("English", use_container_width=True):
                st.session_state.language = 'en'
                st.session_state.page = 'login'
                st.rerun()
            if st.button("मराठी", use_container_width=True):
                st.session_state.language = 'mr'
                st.session_state.page = 'login'
                st.rerun()
        with lcol2:
            if st.button("हिंदी", use_container_width=True):
                st.session_state.language = 'hi'
                st.session_state.page = 'login'
                st.rerun()
            if st.button("ગુજરાતી", use_container_width=True):
                st.session_state.language = 'gu'
                st.session_state.page = 'login'
                st.rerun()
        with lcol3:
            if st.button("বাংলা", use_container_width=True):
                st.session_state.language = 'bn'
                st.session_state.page = 'login'
                st.rerun()
            if st.button("தமிழ்", use_container_width=True):
                st.session_state.language = 'ta'
                st.session_state.page = 'login'
                st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("""
        <div class='kisan-card' style='text-align:center;'>
            <div style='color:#4f6f61; font-size:0.9rem;'>
                Irrigation Planning &nbsp;|&nbsp; Government Schemes &nbsp;|&nbsp; Complaint Management<br>
                सिंचाई योजना &nbsp;|&nbsp; सरकारी योजनाएं &nbsp;|&nbsp; शिकायत प्रबंधन
            </div>
        </div>
        """, unsafe_allow_html=True)

elif page == 'login':
    auth.show_login_page()

elif page == 'farmer_dashboard':
    farmer_dashboard.show()

elif page == 'admin_dashboard':
    admin_dashboard.show()
