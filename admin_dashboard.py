import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import folium
from streamlit_folium import st_folium
from translations import get_text, STATES, DEPARTMENTS
from database import (get_stats, get_all_complaints, get_all_farmers, get_all_schemes,
                       update_complaint_status, add_scheme, update_scheme, delete_scheme,
                       log_admin_action, get_admin_logs, get_scheme_adoption_trend,
                       get_complaint_by_states)

# State coordinates for map
STATE_COORDS = {
    "Andhra Pradesh": [15.9129, 79.7400], "Assam": [26.2006, 92.9376],
    "Bihar": [25.0961, 85.3131], "Chhattisgarh": [21.2787, 81.8661],
    "Gujarat": [22.2587, 71.1924], "Haryana": [29.0588, 76.0856],
    "Himachal Pradesh": [31.1048, 77.1734], "Jharkhand": [23.6102, 85.2799],
    "Karnataka": [15.3173, 75.7139], "Kerala": [10.8505, 76.2711],
    "Madhya Pradesh": [22.9734, 78.6569], "Maharashtra": [19.7515, 75.7139],
    "Manipur": [24.6637, 93.9063], "Odisha": [20.9517, 85.0985],
    "Punjab": [31.1471, 75.3412], "Rajasthan": [27.0238, 74.2179],
    "Tamil Nadu": [11.1271, 78.6569], "Telangana": [18.1124, 79.0193],
    "Uttar Pradesh": [26.8467, 80.9462], "Uttarakhand": [30.0668, 79.0193],
    "West Bengal": [22.9868, 87.8550], "Delhi": [28.7041, 77.1025],
    "Goa": [15.2993, 74.1240], "Meghalaya": [25.4670, 91.3662],
}

def show():
    lang = st.session_state.get('language', 'en')
    admin = st.session_state.user_data

    # Sidebar
    with st.sidebar:
        st.markdown("""
        <div style='text-align:center; padding:1rem 0;'>
            <div style='font-size:2.5rem;'>🔧</div>
            <div style='font-size:1rem; font-weight:600; color:#e6edf3;'>Admin Panel</div>
            <div style='font-size:0.8rem; color:#39d353;'>Smart Kisan Platform</div>
        </div>
        <hr style='border:1px solid #30363d;'>
        """, unsafe_allow_html=True)

        lang_options = {'en': '🇬🇧 English', 'hi': '🇮🇳 हिंदी', 'mr': '🇮🇳 मराठी', 'gu': '🇮🇳 ગુજરાતી', 'bn': '🇮🇳 বাংলা', 'ta': '🇮🇳 தமிழ்'}
        new_lang = st.selectbox("Language", list(lang_options.keys()),
                                 format_func=lambda x: lang_options[x],
                                 index=list(lang_options.keys()).index(lang) if lang in lang_options else 0)
        if new_lang != lang:
            st.session_state.language = new_lang
            st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button(f"🚪 {get_text('logout')}", use_container_width=True):
            log_admin_action(admin['username'], "LOGOUT", "Admin logged out")
            for key in ['logged_in', 'user_type', 'user_data']:
                st.session_state[key] = None
            st.session_state.logged_in = False
            st.session_state.page = 'login'
            st.rerun()

    st.markdown(f"""
    <div style='display:flex; align-items:center; gap:1rem; margin-bottom:1.5rem;'>
        <div style='font-size:1.8rem; font-weight:700; color:#39d353;'>🔧 {get_text('admin_dashboard')}</div>
    </div>
    """, unsafe_allow_html=True)

    tabs = st.tabs([
        f"📊 {get_text('overview')}",
        f"📋 {get_text('manage_complaints')}",
        f"🏛️ {get_text('manage_schemes')}",
        f"🗺️ {get_text('map_view')}",
    ])

    with tabs[0]:
        _show_overview(lang)

    with tabs[1]:
        _show_complaints_mgmt(admin, lang)

    with tabs[2]:
        _show_schemes_mgmt(admin, lang)

    with tabs[3]:
        _show_maps(lang)


def _show_overview(lang):
    stats = get_stats()

    st.markdown(f"<div style='font-size:1.2rem; font-weight:600; color:#e6edf3; margin-bottom:1rem;'>📊 Platform Overview</div>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    metric_data = [
        ("👨‍🌾", get_text('total_farmers'), stats['total_farmers'], "#39d353"),
        ("📋", get_text('total_complaints'), stats['total_complaints'], "#388bfd"),
        ("✅", get_text('resolved'), stats['resolved_complaints'], "#2ea043"),
    ]
    for col, (icon, label, value, color) in zip([col1, col2, col3], metric_data):
        with col:
            st.markdown(f"""
            <div class='metric-card'>
                <div style='font-size:1.8rem;'>{icon}</div>
                <div style='font-size:1.8rem; font-weight:700; color:{color};'>{value}</div>
                <div class='metric-label'>{label}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)

    with col1:
        # Complaints by priority
        complaints = get_all_complaints()
        if complaints:
            df = pd.DataFrame(complaints)
            priority_counts = df['priority'].value_counts().reset_index()
            priority_counts.columns = ['priority', 'count']
            fig = px.pie(priority_counts, names='priority', values='count',
                         title="Complaints by Priority",
                         color='priority',
                         color_discrete_map={'High': '#f85149', 'Medium': '#d29922', 'Low': '#39d353'})
            fig.update_layout(plot_bgcolor='#161b22', paper_bgcolor='#1c2128',
                               font_color='#e6edf3', title_font_color='#39d353')
            st.plotly_chart(fig, use_container_width=True)

            # Status breakdown
            status_counts = df['status'].value_counts().reset_index()
            status_counts.columns = ['status', 'count']
            fig2 = px.bar(status_counts, x='status', y='count',
                           title="Complaints by Status",
                           color='count', color_continuous_scale='Greens')
            fig2.update_layout(plot_bgcolor='#161b22', paper_bgcolor='#1c2128',
                                font_color='#e6edf3', title_font_color='#39d353',
                                xaxis=dict(gridcolor='#30363d'), yaxis=dict(gridcolor='#30363d'))
            st.plotly_chart(fig2, use_container_width=True)

    with col2:
        # Scheme adoption
        adoption_data = get_scheme_adoption_trend()
        if adoption_data:
            df_s = pd.DataFrame(adoption_data)
            fig3 = px.bar(df_s, x='adoption_count', y='name', orientation='h',
                           title="Top Schemes by Adoption",
                           color='adoption_count', color_continuous_scale='Greens')
            fig3.update_layout(plot_bgcolor='#161b22', paper_bgcolor='#1c2128',
                                font_color='#e6edf3', title_font_color='#39d353',
                                xaxis=dict(gridcolor='#30363d'), yaxis=dict(gridcolor='#30363d'),
                                height=350)
            st.plotly_chart(fig3, use_container_width=True)

        # Quick stats
        resolve_rate = (stats['resolved_complaints'] / max(stats['total_complaints'], 1)) * 100
        st.markdown(f"""
        <div class='kisan-card'>
            <div style='font-size:0.95rem; font-weight:600; color:#e6edf3; margin-bottom:1rem;'>📈 Quick Stats</div>
            <div style='display:grid; grid-template-columns:1fr 1fr; gap:0.75rem;'>
                <div>
                    <div style='color:#8b949e; font-size:0.8rem;'>Resolution Rate</div>
                    <div style='color:#39d353; font-size:1.2rem; font-weight:700;'>{resolve_rate:.1f}%</div>
                </div>
                <div>
                    <div style='color:#8b949e; font-size:0.8rem;'>High Priority</div>
                    <div style='color:#f85149; font-size:1.2rem; font-weight:700;'>{stats['high_priority']}</div>
                </div>
                <div>
                    <div style='color:#8b949e; font-size:0.8rem;'>Total Schemes</div>
                    <div style='color:#d29922; font-size:1.2rem; font-weight:700;'>{stats['total_schemes']}</div>
                </div>
                <div>
                    <div style='color:#8b949e; font-size:0.8rem;'>Avg Adoptions/Scheme</div>
                    <div style='color:#388bfd; font-size:1.2rem; font-weight:700;'>{stats['total_adoptions']//max(stats['total_schemes'],1):,}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)


def _show_complaints_mgmt(admin, lang):
    st.markdown(f"<div style='font-size:1.2rem; font-weight:600; color:#e6edf3; margin-bottom:1rem;'>📋 Complaint Management</div>", unsafe_allow_html=True)

    complaints = get_all_complaints()
    if not complaints:
        st.info("No complaints yet.")
        return

    # Filters
    col1, col2, col3 = st.columns(3)
    with col1:
        filter_status = st.selectbox("Filter by Status", ["All", "Submitted", "In Progress", "Resolved"])
    with col2:
        filter_priority = st.selectbox("Filter by Priority", ["All", "High", "Medium", "Low"])
    with col3:
        filter_state = st.selectbox("Filter by State", ["All"] + sorted(list(set(c['state'] for c in complaints if c['state']))))

    filtered = complaints
    if filter_status != "All":
        filtered = [c for c in filtered if c['status'] == filter_status]
    if filter_priority != "All":
        filtered = [c for c in filtered if c['priority'] == filter_priority]
    if filter_state != "All":
        filtered = [c for c in filtered if c['state'] == filter_state]

    st.markdown(f"<div style='color:#8b949e; margin-bottom:1rem;'>Showing <b style='color:#39d353;'>{len(filtered)}</b> complaints</div>", unsafe_allow_html=True)

    priority_colors = {'High': '#f85149', 'Medium': '#d29922', 'Low': '#39d353'}
    status_icons = {'Submitted': '📨', 'In Progress': '⚙️', 'Resolved': '✅'}

    for c in filtered:
        pcolor = priority_colors.get(c['priority'], '#39d353')
        sicon = status_icons.get(c['status'], '📨')

        with st.expander(f"{sicon} [{c['priority']}] {c['complaint_id']} — {c['title'][:50]}"):
            col1, col2 = st.columns([2, 1])
            with col1:
                st.markdown(f"**Farmer:** {c['farmer_name']} | **State:** {c['state']} | **District:** {c['district']}")
                st.markdown(f"**Issue:** {c['description']}")
                st.markdown(f"**Filed:** {c['created_at'][:16]} | **Updated:** {c['updated_at'][:16]}")
                st.markdown(f"**Current Department:** {c['department']}")

                if c['image_path'] and os.path.exists(c['image_path'] if isinstance(c['image_path'], str) else ''):
                    try:
                        st.image(c['image_path'], width=300, caption="Attached Image")
                    except:
                        pass

            with col2:
                st.markdown(f"""
                <div style='background:rgba(0,0,0,0.2); border:1px solid {pcolor}; border-radius:8px; padding:1rem; text-align:center; margin-bottom:0.5rem;'>
                    <div style='color:{pcolor}; font-weight:700; font-size:1.1rem;'>{c['priority']}</div>
                    <div style='color:#8b949e; font-size:0.8rem;'>AI Priority</div>
                </div>
                """, unsafe_allow_html=True)

                new_status = st.selectbox("Update Status", ["Submitted", "In Progress", "Resolved"],
                                           index=["Submitted", "In Progress", "Resolved"].index(c['status']),
                                           key=f"status_{c['complaint_id']}")
                new_dept = st.selectbox("Reassign Dept", DEPARTMENTS,
                                         index=DEPARTMENTS.index(c['department']) if c['department'] in DEPARTMENTS else 0,
                                         key=f"dept_{c['complaint_id']}")

                if st.button("💾 Update", key=f"upd_{c['complaint_id']}", use_container_width=True):
                    update_complaint_status(c['complaint_id'], new_status, new_dept)
                    log_admin_action(admin['username'], "UPDATE_COMPLAINT",
                                     f"Complaint {c['complaint_id']} → {new_status} | Dept: {new_dept}")
                    st.success("✅ Updated!")
                    st.rerun()

import os


def _show_schemes_mgmt(admin, lang):
    st.markdown(f"<div style='font-size:1.2rem; font-weight:600; color:#e6edf3; margin-bottom:1rem;'>🏛️ Scheme Management</div>", unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["📋 View & Manage", "➕ Add New Scheme"])

    with tab1:
        schemes = get_all_schemes()
        for s in schemes:
            with st.expander(f"🏛️ {s['name']} — {s['adoption_count']:,} adoptions | ⭐ {s['rating']}"):
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"**Description:** {s['description']}")
                    st.markdown(f"**Benefits:** {s['benefits']}")
                    st.markdown(f"**Department:** {s['department']}")
                    st.markdown(f"**States:** {s['eligible_states']} | **Crops:** {s['eligible_crops']} | **Category:** {s['eligible_categories']}")
                with col2:
                    if st.button("🗑️ Delete", key=f"del_{s['id']}", use_container_width=True):
                        delete_scheme(s['id'])
                        log_admin_action(admin['username'], "DELETE_SCHEME", f"Deleted scheme: {s['name']}")
                        st.success("Deleted!")
                        st.rerun()

                # Edit form
                with st.form(f"edit_scheme_{s['id']}"):
                    st.markdown("**✏️ Edit Scheme**")
                    ec1, ec2 = st.columns(2)
                    with ec1:
                        e_name = st.text_input("Name", value=s['name'])
                        e_desc = st.text_area("Description", value=s['description'], height=80)
                        e_benefits = st.text_area("Benefits", value=s['benefits'], height=80)
                    with ec2:
                        e_states = st.text_input("Eligible States", value=s['eligible_states'])
                        e_crops = st.text_input("Eligible Crops", value=s['eligible_crops'])
                        e_cats = st.text_input("Eligible Categories", value=s['eligible_categories'])
                        e_dept = st.text_input("Department", value=s['department'])

                    if st.form_submit_button("💾 Save Changes", use_container_width=True):
                        update_scheme(s['id'], {
                            'name': e_name, 'description': e_desc, 'benefits': e_benefits,
                            'eligible_states': e_states, 'eligible_crops': e_crops,
                            'eligible_categories': e_cats, 'department': e_dept
                        })
                        log_admin_action(admin['username'], "EDIT_SCHEME", f"Edited scheme: {e_name}")
                        st.success("✅ Scheme updated!")
                        st.rerun()

    with tab2:
        st.markdown("**➕ Add New Government Scheme**")
        with st.form("add_scheme_form"):
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input(f"📌 {get_text('scheme_name')}", placeholder="Scheme name")
                desc = st.text_area(f"📝 {get_text('description')}", placeholder="Brief description", height=100)
                benefits = st.text_area("💰 Benefits", placeholder="List of benefits", height=100)
            with col2:
                states_elig = st.text_input(f"🗺️ {get_text('eligible_states')}", value="All")
                crops_elig = st.text_input(f"🌾 {get_text('eligible_crops')}", value="All")
                cats_elig = st.text_input(f"👥 {get_text('eligible_categories')}", value="All")
                dept = st.selectbox(f"🏢 {get_text('department')}", DEPARTMENTS)

            if st.form_submit_button(f"✅ {get_text('save_scheme')}", use_container_width=True):
                if name and desc and benefits:
                    add_scheme({
                        'name': name, 'description': desc, 'benefits': benefits,
                        'eligible_states': states_elig, 'eligible_crops': crops_elig,
                        'eligible_categories': cats_elig, 'department': dept
                    })
                    log_admin_action(admin['username'], "ADD_SCHEME", f"Added scheme: {name}")
                    st.success(f"✅ Scheme '{name}' added successfully!")
                    st.rerun()
                else:
                    st.warning("Please fill all required fields")


def _show_maps(lang):
    st.markdown(f"<div style='font-size:1.2rem; font-weight:600; color:#e6edf3; margin-bottom:1rem;'>🗺️ Map Dashboard</div>", unsafe_allow_html=True)

    complaints = get_all_complaints()
    farmers = get_all_farmers()

    map_type = st.radio("Select Map View", ["🔴 Complaint Heatmap", "💧 Water Scarcity Zones", "🏛️ Scheme Adoption Heatmap"], horizontal=True)

    # Build base map centered on India
    m = folium.Map(location=[20.5937, 78.9629], zoom_start=5,
                   tiles='CartoDB dark_matter')

    if "Complaint" in map_type and complaints:
        # Count complaints per state
        state_counts = {}
        for c in complaints:
            if c['state']:
                state_counts[c['state']] = state_counts.get(c['state'], 0) + 1

        for state, count in state_counts.items():
            coords = STATE_COORDS.get(state)
            if coords:
                radius = min(count * 8 + 10, 50)
                color = '#f85149' if count > 5 else '#d29922' if count > 2 else '#39d353'
                folium.CircleMarker(
                    location=coords,
                    radius=radius,
                    color=color,
                    fill=True, fill_opacity=0.7,
                    popup=folium.Popup(f"<b>{state}</b><br>Complaints: {count}", max_width=200),
                    tooltip=f"{state}: {count} complaints"
                ).add_to(m)

        st.markdown(f"<div class='alert-info'>Showing complaint distribution across {len(state_counts)} states. Circle size = complaint count.</div>", unsafe_allow_html=True)

    elif "Water Scarcity" in map_type:
        # Mark known water-scarce states
        water_scarce = {
            "Rajasthan": "High Scarcity", "Gujarat": "Medium Scarcity",
            "Maharashtra": "Medium Scarcity", "Andhra Pradesh": "Low Scarcity",
            "Karnataka": "Medium Scarcity", "Telangana": "Low Scarcity",
            "Madhya Pradesh": "Low Scarcity", "Uttar Pradesh": "Low Scarcity",
        }
        scarcity_colors = {"High Scarcity": "#f85149", "Medium Scarcity": "#d29922", "Low Scarcity": "#388bfd"}

        for state, level in water_scarce.items():
            coords = STATE_COORDS.get(state)
            if coords:
                folium.CircleMarker(
                    location=coords,
                    radius=20,
                    color=scarcity_colors[level],
                    fill=True, fill_opacity=0.6,
                    popup=folium.Popup(f"<b>{state}</b><br>{level}", max_width=200),
                    tooltip=f"{state}: {level}"
                ).add_to(m)

        # Legend
        st.markdown("""
        <div style='display:flex; gap:1rem; margin-bottom:1rem;'>
            <span style='color:#f85149;'>🔴 High Scarcity</span>
            <span style='color:#d29922;'>🟡 Medium Scarcity</span>
            <span style='color:#388bfd;'>🔵 Low Scarcity</span>
        </div>
        """, unsafe_allow_html=True)

    elif "Scheme Adoption" in map_type and farmers:
        # Count farmers per state
        state_farmers = {}
        for f in farmers:
            if f['state']:
                state_farmers[f['state']] = state_farmers.get(f['state'], 0) + 1

        for state, count in state_farmers.items():
            coords = STATE_COORDS.get(state)
            if coords:
                folium.CircleMarker(
                    location=coords,
                    radius=min(count * 10 + 8, 40),
                    color='#39d353',
                    fill=True, fill_opacity=0.6,
                    popup=folium.Popup(f"<b>{state}</b><br>Farmers: {count}", max_width=200),
                    tooltip=f"{state}: {count} farmers"
                ).add_to(m)

    st_folium(m, width=None, height=500)


def _show_logs(lang):
    st.markdown(f"<div style='font-size:1.2rem; font-weight:600; color:#e6edf3; margin-bottom:1rem;'>📜 {get_text('activity_log')}</div>", unsafe_allow_html=True)

    logs = get_admin_logs()
    if not logs:
        st.info("No activity logged yet.")
        return

    for log in logs:
        action_icons = {
            "LOGIN": "🔐", "LOGOUT": "🚪", "UPDATE_COMPLAINT": "📋",
            "DELETE_SCHEME": "🗑️", "EDIT_SCHEME": "✏️", "ADD_SCHEME": "➕"
        }
        icon = action_icons.get(log['action'], "📌")
        st.markdown(f"""
        <div style='display:flex; gap:1rem; align-items:center; padding:0.6rem; border-bottom:1px solid #30363d;'>
            <div style='font-size:1.2rem;'>{icon}</div>
            <div style='flex:1;'>
                <span style='color:#39d353; font-weight:600;'>{log['action']}</span>
                <span style='color:#8b949e; font-size:0.85rem;'> — {log['details']}</span>
            </div>
            <div style='color:#8b949e; font-size:0.8rem;'>{log['timestamp'][:16]}</div>
        </div>
        """, unsafe_allow_html=True)
