import streamlit as st
from database import init_db
from translations import get_text
import auth
import farmer_dashboard
import admin_dashboard

# --- Page Config ---
st.set_page_config(
    page_title="Smart Kisan Platform",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- Custom CSS ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&family=Noto+Sans+Devanagari:wght@400;600;700&display=swap');

:root {
    --bg-primary: #0d1117;
    --bg-secondary: #161b22;
    --bg-card: #1c2128;
    --accent-green: #39d353;
    --accent-light: #58e36a;
    --accent-dark: #2ea043;
    --text-primary: #e6edf3;
    --text-secondary: #8b949e;
    --border: #30363d;
    --warning: #d29922;
    --danger: #f85149;
    --info: #388bfd;
}

* { font-family: 'Poppins', 'Noto Sans Devanagari', sans-serif; }

.stApp {
    background-color: var(--bg-primary) !important;
    color: var(--text-primary) !important;
}

.main .block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
    max-width: 1200px;
}

/* Cards */
.kisan-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.5rem;
    margin-bottom: 1rem;
    transition: border-color 0.2s ease;
}
.kisan-card:hover { border-color: var(--accent-green); }

/* Hero */
.hero-container {
    background: linear-gradient(135deg, #0d1117 0%, #1a2e1a 50%, #0d1117 100%);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 3rem 2rem;
    text-align: center;
    margin-bottom: 2rem;
    position: relative;
    overflow: hidden;
}
.hero-container::before {
    content: '';
    position: absolute;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: radial-gradient(ellipse at center, rgba(57,211,83,0.05) 0%, transparent 60%);
    pointer-events: none;
}
.hero-title {
    font-size: 3rem;
    font-weight: 700;
    color: var(--accent-green);
    margin-bottom: 0.5rem;
    letter-spacing: -1px;
}
.hero-subtitle {
    font-size: 1.2rem;
    color: var(--text-secondary);
    margin-bottom: 0.25rem;
}

/* Buttons */
.stButton > button {
    background: var(--accent-dark) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 0.6rem 1.5rem !important;
    font-weight: 500 !important;
    font-size: 0.95rem !important;
    transition: all 0.2s ease !important;
    width: 100%;
}
.stButton > button:hover {
    background: var(--accent-green) !important;
    transform: translateY(-1px);
    box-shadow: 0 4px 15px rgba(57,211,83,0.3) !important;
}

/* Language toggle buttons */
.lang-btn {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    padding: 0.75rem 2rem;
    border-radius: 12px;
    border: 2px solid var(--border);
    background: var(--bg-card);
    color: var(--text-primary);
    font-size: 1.1rem;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s;
    text-decoration: none;
    margin: 0.5rem;
}
.lang-btn:hover, .lang-btn.active {
    border-color: var(--accent-green);
    background: rgba(57,211,83,0.1);
    color: var(--accent-green);
}

/* Inputs */
.stTextInput > div > div > input,
.stSelectbox > div > div,
.stTextArea > div > div > textarea {
    background-color: var(--bg-secondary) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    color: var(--text-primary) !important;
}
.stTextInput > div > div > input:focus,
.stSelectbox > div > div:focus {
    border-color: var(--accent-green) !important;
    box-shadow: 0 0 0 2px rgba(57,211,83,0.2) !important;
}

/* Metrics */
.metric-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.25rem;
    text-align: center;
}
.metric-value {
    font-size: 2rem;
    font-weight: 700;
    color: var(--accent-green);
}
.metric-label {
    font-size: 0.85rem;
    color: var(--text-secondary);
    margin-top: 0.25rem;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    background: var(--bg-secondary);
    border-radius: 10px;
    padding: 0.25rem;
    gap: 0.25rem;
}
.stTabs [data-baseweb="tab"] {
    background: transparent;
    border-radius: 8px;
    color: var(--text-secondary);
    font-weight: 500;
}
.stTabs [aria-selected="true"] {
    background: var(--accent-dark) !important;
    color: white !important;
}

/* Sidebar */
.css-1d391kg, [data-testid="stSidebar"] {
    background: var(--bg-secondary) !important;
    border-right: 1px solid var(--border) !important;
}

/* Badge */
.badge {
    display: inline-block;
    padding: 0.2rem 0.6rem;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 600;
}
.badge-high { background: rgba(248,81,73,0.2); color: #f85149; border: 1px solid #f85149; }
.badge-medium { background: rgba(210,153,34,0.2); color: #d29922; border: 1px solid #d29922; }
.badge-low { background: rgba(57,211,83,0.2); color: #39d353; border: 1px solid #39d353; }

/* Status badges */
.badge-submitted { background: rgba(56,139,253,0.2); color: #388bfd; border: 1px solid #388bfd; }
.badge-inprogress { background: rgba(210,153,34,0.2); color: #d29922; border: 1px solid #d29922; }
.badge-resolved { background: rgba(57,211,83,0.2); color: #39d353; border: 1px solid #39d353; }

/* Alert boxes */
.alert-success {
    background: rgba(57,211,83,0.1);
    border: 1px solid var(--accent-green);
    border-radius: 8px;
    padding: 1rem;
    color: var(--accent-green);
    margin: 0.5rem 0;
}
.alert-info {
    background: rgba(56,139,253,0.1);
    border: 1px solid #388bfd;
    border-radius: 8px;
    padding: 1rem;
    color: #388bfd;
    margin: 0.5rem 0;
}
.alert-warning {
    background: rgba(210,153,34,0.1);
    border: 1px solid #d29922;
    border-radius: 8px;
    padding: 1rem;
    color: #d29922;
    margin: 0.5rem 0;
}

/* Divider */
.green-divider {
    height: 2px;
    background: linear-gradient(90deg, transparent, var(--accent-green), transparent);
    margin: 1.5rem 0;
    border: none;
}

/* Step indicator */
.step-indicator {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.5rem;
    margin-bottom: 2rem;
}
.step {
    width: 32px; height: 32px;
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 0.85rem; font-weight: 600;
    border: 2px solid var(--border);
    color: var(--text-secondary);
}
.step.active { border-color: var(--accent-green); background: rgba(57,211,83,0.15); color: var(--accent-green); }
.step.done { border-color: var(--accent-dark); background: var(--accent-dark); color: white; }
.step-line { height: 2px; width: 40px; background: var(--border); }
.step-line.done { background: var(--accent-green); }

/* Hide streamlit branding */
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
header { visibility: hidden; }

/* Scrollbar */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: var(--bg-primary); }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: var(--accent-dark); }

/* DataFrames */
.dataframe { background: var(--bg-card) !important; color: var(--text-primary) !important; }

/* Select box options */
.stSelectbox [data-baseweb="select"] > div { background: var(--bg-secondary) !important; }

/* Number input */
.stNumberInput > div > div > input { background: var(--bg-secondary) !important; color: var(--text-primary) !important; border: 1px solid var(--border) !important; border-radius: 8px !important; }

/* Labels */
.stTextInput label, .stSelectbox label, .stTextArea label, .stNumberInput label, .stRadio label {
    color: var(--text-secondary) !important;
    font-size: 0.9rem !important;
}

/* Radio buttons */
.stRadio > div { flex-direction: row; gap: 1rem; }
.stRadio > div > label { background: var(--bg-card); border: 1px solid var(--border); border-radius: 8px; padding: 0.5rem 1rem; cursor: pointer; }

/* Expander */
.streamlit-expanderHeader { background: var(--bg-card) !important; border: 1px solid var(--border) !important; border-radius: 8px !important; color: var(--text-primary) !important; }
.streamlit-expanderContent { background: var(--bg-secondary) !important; border: 1px solid var(--border) !important; border-bottom-left-radius: 8px !important; border-bottom-right-radius: 8px !important; }

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
        <div class="hero-title">🌾 Smart Kisan Platform</div>
        <div class="hero-subtitle">Empowering Farmers with Smart Technology</div>
        <div class="hero-subtitle" style="font-family: 'Noto Sans Devanagari', sans-serif;">किसानों को स्मार्ट तकनीक से सशक्त बनाना</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='text-align:center; font-size:1.2rem; color:#8b949e; margin-bottom:2rem;'>Please select your preferred language / कृपया अपनी भाषा चुनें</div>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("")
        lcol1, lcol2, lcol3 = st.columns(3)
        with lcol1:
            if st.button("🇬🇧 English", use_container_width=True):
                st.session_state.language = 'en'
                st.session_state.page = 'login'
                st.rerun()
            if st.button("🇮🇳 मराठी", use_container_width=True):
                st.session_state.language = 'mr'
                st.session_state.page = 'login'
                st.rerun()
        with lcol2:
            if st.button("🇮🇳 हिंदी", use_container_width=True):
                st.session_state.language = 'hi'
                st.session_state.page = 'login'
                st.rerun()
            if st.button("🇮🇳 ગુજરાતી", use_container_width=True):
                st.session_state.language = 'gu'
                st.session_state.page = 'login'
                st.rerun()
        with lcol3:
            if st.button("🇮🇳 বাংলা", use_container_width=True):
                st.session_state.language = 'bn'
                st.session_state.page = 'login'
                st.rerun()
            if st.button("🇮🇳 தமிழ்", use_container_width=True):
                st.session_state.language = 'ta'
                st.session_state.page = 'login'
                st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("""
        <div class='kisan-card' style='text-align:center;'>
            <div style='color:#8b949e; font-size:0.85rem;'>
                🌱 Irrigation Planning &nbsp;|&nbsp; 🏛️ Government Schemes &nbsp;|&nbsp; 📋 Complaint Management<br>
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
