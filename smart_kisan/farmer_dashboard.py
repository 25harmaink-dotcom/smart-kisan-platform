import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import os
from datetime import datetime
from translations import get_text, CROPS, SOIL_TYPES, WATER_SOURCES, FARMER_CATEGORIES, STATES
from database import (update_farmer_profile, get_farmer_by_id, get_matching_schemes,
                       create_complaint, get_complaints_by_farmer, adopt_scheme)
from ai_logic import get_irrigation_plan, get_crop_rotation, detect_priority, route_department

def show():
    lang = st.session_state.get('language', 'en')
    farmer = st.session_state.user_data

    # Refresh farmer data
    farmer = get_farmer_by_id(farmer['id'])
    st.session_state.user_data = farmer

    # Sidebar
    with st.sidebar:
        st.markdown(f"""
        <div style='text-align:center; padding:1rem 0;'>
            <div style='font-size:2.5rem;'>👨‍🌾</div>
            <div style='font-size:1rem; font-weight:600; color:#e6edf3;'>{farmer['name']}</div>
            <div style='font-size:0.8rem; color:#8b949e;'>{farmer.get('state','') or 'State not set'} • {farmer.get('district','') or 'District not set'}</div>
            <div style='font-size:0.75rem; color:#39d353; margin-top:0.25rem;'>📱 {farmer['phone']}</div>
        </div>
        <hr style='border:1px solid #30363d;'>
        """, unsafe_allow_html=True)

        if farmer.get('crop_type'):
            st.markdown(f"""
            <div class='kisan-card' style='padding:0.75rem;'>
                <div style='font-size:0.8rem; color:#8b949e;'>Current Profile</div>
                <div style='font-size:0.85rem; color:#e6edf3; margin-top:0.3rem;'>
                    🌾 {farmer.get('crop_type','')}<br>
                    📐 {farmer.get('area_size','') or '-'} acres<br>
                    🌱 {farmer.get('soil_type','') or '-'}<br>
                    💧 {farmer.get('water_source','') or '-'}
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        lang_options = {'en': '🇬🇧 English', 'hi': '🇮🇳 हिंदी', 'mr': '🇮🇳 मराठी', 'gu': '🇮🇳 ગુજરાતી', 'bn': '🇮🇳 বাংলা', 'ta': '🇮🇳 தமிழ்'}
        new_lang = st.selectbox("Language / भाषा", list(lang_options.keys()),
                                 format_func=lambda x: lang_options[x],
                                 index=list(lang_options.keys()).index(lang) if lang in lang_options else 0)
        if new_lang != lang:
            st.session_state.language = new_lang
            st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button(f"🚪 {get_text('logout')}", use_container_width=True):
            for key in ['logged_in', 'user_type', 'user_data']:
                st.session_state[key] = None
            st.session_state.logged_in = False
            st.session_state.page = 'login'
            st.rerun()

    # Main header
    st.markdown(f"""
    <div style='display:flex; align-items:center; gap:1rem; margin-bottom:1.5rem;'>
        <div style='font-size:1.8rem; font-weight:700; color:#39d353;'>🌾 {get_text('dashboard')}</div>
        <div style='color:#8b949e; font-size:0.9rem;'>{get_text('welcome_farmer')}, {farmer['name']}!</div>
    </div>
    """, unsafe_allow_html=True)

    # Tabs
    tabs = st.tabs([
        f"📚 {get_text('tutorial')}",
        f"👤 {get_text('profile')}",
        f"💧 {get_text('irrigation')}",
        f"🔄 {get_text('rotation')}",
        f"🏛️ {get_text('schemes')}",
        f"📋 {get_text('complaints')}",
    ])

    with tabs[0]:
        _show_tutorial(lang)

    with tabs[1]:
        _show_profile(farmer, lang)

    with tabs[2]:
        _show_irrigation(farmer, lang)

    with tabs[3]:
        _show_rotation(farmer, lang)

    with tabs[4]:
        _show_schemes(farmer, lang)

    with tabs[5]:
        _show_complaints(farmer, lang)


def _show_tutorial(lang):
    st.markdown(f"<div style='font-size:1.4rem; font-weight:600; color:#39d353; margin-bottom:1.5rem;'>📚 {get_text('tutorial_title')}</div>", unsafe_allow_html=True)

    steps = [
        ("👤", get_text('tut_step1'), "Fill your crop, soil, and water details to get personalized recommendations"),
        ("💧", get_text('tut_step2'), "Get smart watering schedules based on your crop and soil type"),
        ("🏛️", get_text('tut_step3'), "Find government schemes you're eligible for based on your state and crop"),
        ("🔄", get_text('tut_step4'), "Get advice on what crop to plant next for better yield"),
        ("📋", get_text('tut_step5'), "Report issues and track their resolution status"),
    ]

    for i, (icon, title, desc) in enumerate(steps):
        st.markdown(f"""
        <div class='kisan-card' style='display:flex; gap:1rem; align-items:flex-start;'>
            <div style='font-size:2rem; min-width:48px; text-align:center;'>{icon}</div>
            <div>
                <div style='font-weight:600; color:#e6edf3; margin-bottom:0.3rem;'>
                    <span style='color:#39d353;'>Step {i+1}:</span> {title}
                </div>
                <div style='color:#8b949e; font-size:0.9rem;'>{desc}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <div class='alert-success'>
        ✅ <b>Quick Start:</b> Begin by going to the <b>Profile & Inputs</b> tab and filling in your crop details. All recommendations will be personalized based on your inputs!
    </div>
    """, unsafe_allow_html=True)

    # Demo stats
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)
    demo_stats = [("🌾", "10+", "Crops Supported"), ("🏛️", "10+", "Govt Schemes"), ("💧", "Smart", "Irrigation AI"), ("🔄", "Instant", "Crop Rotation")]
    for col, (icon, val, label) in zip([col1, col2, col3, col4], demo_stats):
        with col:
            st.markdown(f"""
            <div class='metric-card'>
                <div style='font-size:1.5rem;'>{icon}</div>
                <div class='metric-value'>{val}</div>
                <div class='metric-label'>{label}</div>
            </div>
            """, unsafe_allow_html=True)


def _show_profile(farmer, lang):
    st.markdown(f"<div style='font-size:1.4rem; font-weight:600; color:#39d353; margin-bottom:1.5rem;'>👤 {get_text('profile')}</div>", unsafe_allow_html=True)

    with st.form("profile_form"):
        col1, col2 = st.columns(2)
        with col1:
            state = st.selectbox(f"🗺️ {get_text('state')}", STATES,
                                  index=STATES.index(farmer['state']) if farmer.get('state') in STATES else 0)
            crop = st.selectbox(f"🌾 {get_text('crop_type')}", CROPS,
                                 index=CROPS.index(farmer['crop_type']) if farmer.get('crop_type') in CROPS else 0)
            soil = st.selectbox(f"🌱 {get_text('soil_type')}", SOIL_TYPES,
                                 index=SOIL_TYPES.index(farmer['soil_type']) if farmer.get('soil_type') in SOIL_TYPES else 0)
        with col2:
            district = st.text_input(f"📍 {get_text('district')}", value=farmer.get('district') or '')
            area = st.number_input(f"📐 {get_text('area_size')}", min_value=0.1, max_value=1000.0,
                                    value=float(farmer.get('area_size') or 1.0), step=0.5)
            water = st.selectbox(f"💧 {get_text('water_source')}", WATER_SOURCES,
                                  index=WATER_SOURCES.index(farmer['water_source']) if farmer.get('water_source') in WATER_SOURCES else 0)
            category = st.selectbox(f"👥 {get_text('farmer_category')}", FARMER_CATEGORIES,
                                     index=FARMER_CATEGORIES.index(farmer['farmer_category']) if farmer.get('farmer_category') in FARMER_CATEGORIES else 0)

        submitted = st.form_submit_button(f"💾 {get_text('save_profile')}", use_container_width=True)
        if submitted:
            update_farmer_profile(farmer['id'], {
                'crop_type': crop, 'area_size': area, 'soil_type': soil,
                'water_source': water, 'farmer_category': category,
                'state': state, 'district': district
            })
            st.session_state.user_data = get_farmer_by_id(farmer['id'])
            st.success(f"✅ {get_text('profile_saved')}")
            st.rerun()


def _show_irrigation(farmer, lang):
    st.markdown(f"<div style='font-size:1.4rem; font-weight:600; color:#39d353; margin-bottom:1rem;'>💧 {get_text('irrigation')}</div>", unsafe_allow_html=True)

    if not farmer.get('crop_type'):
        st.markdown("""
        <div class='alert-warning'>
            ⚠️ Please fill your <b>Profile & Inputs</b> first to get personalized irrigation recommendations.
        </div>
        """, unsafe_allow_html=True)
        return

    crop = farmer.get('crop_type', 'Default')
    soil = farmer.get('soil_type', 'Default')
    water = farmer.get('water_source', 'Canal')
    area = float(farmer.get('area_size') or 1.0)

    if st.button(f"🔄 {get_text('get_plan')}", use_container_width=True):
        plan = get_irrigation_plan(crop, soil, water, area)
        st.session_state['irr_plan'] = plan

    if 'irr_plan' in st.session_state:
        plan = st.session_state['irr_plan']

        st.markdown(f"<div style='font-size:1.1rem; font-weight:600; color:#e6edf3; margin:1rem 0;'>📊 {get_text('irrigation_plan')} — {crop}</div>", unsafe_allow_html=True)

        col1, col2, col3, col4 = st.columns(4)
        metrics = [
            ("💧", get_text('water_required'), plan['water_per_acre']),
            ("📅", get_text('frequency'), plan['frequency']),
            ("🌾", get_text('est_yield'), plan['estimated_yield']),
            ("⏰", "Best Time", plan['best_time'].split('(')[0].strip()),
        ]
        for col, (icon, label, value) in zip([col1, col2, col3, col4], metrics):
            with col:
                st.markdown(f"""
                <div class='metric-card'>
                    <div style='font-size:1.5rem;'>{icon}</div>
                    <div style='font-size:1rem; font-weight:600; color:#39d353;'>{value}</div>
                    <div class='metric-label'>{label}</div>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        if plan['efficiency_tip']:
            st.markdown(f"<div class='alert-info'>{plan['efficiency_tip']}</div>", unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**📅 Irrigation Schedule (next 5 intervals)**")
            for s in plan['schedule']:
                st.markdown(f"<div style='padding:0.4rem; border-left:3px solid #39d353; margin:0.3rem 0; color:#e6edf3; font-size:0.9rem;'>{s}</div>", unsafe_allow_html=True)

        with col2:
            st.markdown("**🌱 Crop Growth Stage Guide**")
            for stage in plan['stages']:
                st.markdown(f"<div style='padding:0.4rem; border-left:3px solid #2ea043; margin:0.3rem 0; color:#8b949e; font-size:0.85rem;'>{stage}</div>", unsafe_allow_html=True)

        # Chart
        st.markdown("<br>", unsafe_allow_html=True)
        days = [i * int(plan['frequency'].split()[1]) for i in range(1, 8)]
        water_vals = [int(plan['water_per_acre'].replace(',','').replace(' L/acre','')) * 0.2 for _ in days]
        fig = go.Figure()
        fig.add_trace(go.Bar(x=[f"Day {d}" for d in days], y=water_vals,
                              marker_color='#39d353', name="Water (L)"))
        fig.update_layout(
            title=f"Irrigation Schedule for {crop}",
            plot_bgcolor='#161b22', paper_bgcolor='#1c2128',
            font_color='#e6edf3', title_font_color='#39d353',
            xaxis=dict(gridcolor='#30363d'), yaxis=dict(gridcolor='#30363d', title="Water (L)"),
            height=300
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.markdown(f"<div class='alert-info'>👆 Click <b>Generate Irrigation Plan</b> to get your personalized schedule based on: <b>{farmer.get('crop_type')}</b> on <b>{farmer.get('soil_type')}</b> soil.</div>", unsafe_allow_html=True)


def _show_rotation(farmer, lang):
    st.markdown(f"<div style='font-size:1.4rem; font-weight:600; color:#39d353; margin-bottom:1rem;'>🔄 {get_text('rotation')}</div>", unsafe_allow_html=True)

    if not farmer.get('crop_type'):
        st.markdown("<div class='alert-warning'>⚠️ Please fill your Profile first.</div>", unsafe_allow_html=True)
        return

    crop = farmer.get('crop_type', 'Default')
    soil = farmer.get('soil_type', 'Default')

    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f"Current crop: **{crop}** | Soil: **{soil}**")
    with col2:
        if st.button(f"🔄 {get_text('get_rotation')}", use_container_width=True):
            result = get_crop_rotation(crop, soil)
            st.session_state['rotation_result'] = result

    if 'rotation_result' in st.session_state:
        r = st.session_state['rotation_result']

        st.markdown(f"""
        <div class='kisan-card' style='border-color:#39d353;'>
            <div style='font-size:1.2rem; font-weight:700; color:#39d353; margin-bottom:1rem;'>
                {crop} → 🌱 {r['next_crop']}
            </div>
            <div style='display:grid; grid-template-columns:1fr 1fr; gap:1rem;'>
                <div>
                    <div style='color:#8b949e; font-size:0.85rem;'>{get_text('next_crop')}</div>
                    <div style='color:#e6edf3; font-size:1.1rem; font-weight:600;'>🌿 {r['next_crop']}</div>
                </div>
                <div>
                    <div style='color:#8b949e; font-size:0.85rem;'>{get_text('soil_impact')}</div>
                    <div style='color:#39d353; font-size:0.9rem;'>{r['soil_impact']}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class='kisan-card'>
            <div style='color:#8b949e; font-size:0.85rem;'>{get_text('rotation_reason')}</div>
            <div style='color:#e6edf3; margin-top:0.5rem;'>💡 {r['reason']}</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class='kisan-card'>
            <div style='color:#8b949e; font-size:0.85rem;'>Soil-Specific Tip</div>
            <div style='color:#e6edf3; margin-top:0.5rem;'>🌱 {r['soil_tip']}</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class='alert-info'>🔁 {r['fallow_option']}</div>
        """, unsafe_allow_html=True)




def _show_schemes(farmer, lang):
    st.markdown(f"<div style='font-size:1.4rem; font-weight:600; color:#39d353; margin-bottom:1rem;'>🏛️ {get_text('schemes')}</div>", unsafe_allow_html=True)

    state = farmer.get('state') or 'All'
    crop = farmer.get('crop_type') or 'All'
    category_raw = farmer.get('farmer_category') or 'All'
    # Extract simple category
    category = category_raw.split('(')[0].strip() if '(' in category_raw else category_raw

    schemes = get_matching_schemes(state, crop, category)

    if not schemes:
        st.markdown(f"<div class='alert-warning'>⚠️ {get_text('no_schemes')}</div>", unsafe_allow_html=True)
        return

    st.markdown(f"<div class='alert-success'>✅ Found <b>{len(schemes)}</b> schemes matching your profile ({state} • {crop} • {category})</div>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    for s in schemes:
        stars = "⭐" * int(s['rating'])
        with st.expander(f"🏛️ {s['name']} — {'👥 ' + str(s['adoption_count']) + ' farmers'}", expanded=False):
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"**{get_text('description')}:** {s['description']}")
                st.markdown(f"**{get_text('benefits')}:** {s['benefits']}")
                st.markdown(f"**{get_text('department')}:** {s['department']}")
                st.markdown(f"**Eligible States:** {s['eligible_states']} | **Eligible Crops:** {s['eligible_crops']}")
            with col2:
                st.markdown(f"""
                <div class='metric-card'>
                    <div style='font-size:1.2rem; color:#39d353; font-weight:700;'>{s['rating']}</div>
                    <div style='font-size:0.8rem;'>{stars}</div>
                    <div style='font-size:0.75rem; color:#8b949e; margin-top:0.5rem;'>{s['adoption_count']:,} adoptions</div>
                </div>
                """, unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button(f"✋ {get_text('apply_scheme')}", key=f"adopt_{s['id']}", use_container_width=True):
                adopt_scheme(s['id'], farmer['id'])
                st.success(f"✅ Interest registered for **{s['name']}**! The department will contact you.")


def _show_complaints(farmer, lang):
    st.markdown(f"<div style='font-size:1.4rem; font-weight:600; color:#39d353; margin-bottom:1rem;'>📋 {get_text('complaints')}</div>", unsafe_allow_html=True)

    tab1, tab2 = st.tabs([f"📝 {get_text('submit_complaint')}", f"🔍 {get_text('my_complaints')}"])

    with tab1:
        with st.form("complaint_form"):
            title = st.text_input(f"📌 {get_text('complaint_title')}", placeholder="Brief title of your issue")
            desc = st.text_area(f"📝 {get_text('complaint_desc')}", placeholder="Describe your issue in detail...", height=120)
            image = st.file_uploader(f"📷 {get_text('upload_image')}", type=['jpg', 'jpeg', 'png'])

            submitted = st.form_submit_button(f"📤 {get_text('submit_complaint')}", use_container_width=True)
            if submitted:
                if title and desc:
                    priority = detect_priority(title, desc)
                    department = route_department(title, desc)
                    image_path = None
                    if image:
                        os.makedirs("complaint_images", exist_ok=True)
                        image_path = f"complaint_images/{farmer['id']}_{datetime.now().strftime('%Y%m%d%H%M%S')}.jpg"
                        with open(image_path, 'wb') as f:
                            f.write(image.read())

                    cid = create_complaint(
                        farmer_id=farmer['id'],
                        farmer_name=farmer['name'],
                        state=farmer.get('state', ''),
                        district=farmer.get('district', ''),
                        title=title, description=desc,
                        priority=priority, department=department,
                        image_path=image_path
                    )
                    priority_badge = {'High': '🔴', 'Medium': '🟡', 'Low': '🟢'}
                    st.success(f"✅ {get_text('complaint_submitted')}")
                    st.markdown(f"""
                    <div class='kisan-card' style='border-color:#39d353;'>
                        <div><b>Complaint ID:</b> <span style='color:#39d353; font-family:monospace;'>{cid}</span></div>
                        <div style='margin-top:0.5rem;'><b>Priority:</b> {priority_badge.get(priority,'🟡')} {priority}</div>
                        <div><b>Routed to:</b> {department}</div>
                        <div style='color:#8b949e; font-size:0.85rem; margin-top:0.5rem;'>Track your complaint in "My Complaints" tab</div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.warning(f"⚠️ {get_text('fill_all')}")

    with tab2:
        complaints = get_complaints_by_farmer(farmer['id'])
        if not complaints:
            st.markdown(f"<div class='alert-info'>📭 {get_text('no_complaints')}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div style='color:#8b949e; margin-bottom:1rem;'>Total: <b style='color:#39d353;'>{len(complaints)}</b> complaints</div>", unsafe_allow_html=True)
            for c in complaints:
                priority_colors = {'High': '#f85149', 'Medium': '#d29922', 'Low': '#39d353'}
                status_icons = {'Submitted': '📨', 'In Progress': '⚙️', 'Resolved': '✅'}
                pcolor = priority_colors.get(c['priority'], '#39d353')
                sicon = status_icons.get(c['status'], '📨')

                st.markdown(f"""
                <div class='kisan-card'>
                    <div style='display:flex; justify-content:space-between; align-items:flex-start;'>
                        <div>
                            <div style='font-weight:600; color:#e6edf3;'>{c['title']}</div>
                            <div style='font-family:monospace; font-size:0.8rem; color:#39d353;'>{c['complaint_id']}</div>
                        </div>
                        <div style='text-align:right;'>
                            <span style='background:rgba(0,0,0,0.3); border:1px solid {pcolor}; color:{pcolor}; border-radius:20px; padding:0.2rem 0.6rem; font-size:0.75rem;'>{c['priority']}</span>
                        </div>
                    </div>
                    <div style='color:#8b949e; font-size:0.85rem; margin:0.5rem 0;'>{c['description'][:120]}{'...' if len(c['description'])>120 else ''}</div>
                    <div style='display:flex; justify-content:space-between; font-size:0.8rem; color:#8b949e;'>
                        <div>{sicon} Status: <b style='color:#e6edf3;'>{c['status']}</b></div>
                        <div>🏢 {c['department']}</div>
                        <div>📅 {c['created_at'][:10]}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
