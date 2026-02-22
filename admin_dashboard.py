import os

import folium
import pandas as pd
import plotly.express as px
import streamlit as st
from streamlit_folium import st_folium

from database import (
    add_scheme,
    delete_scheme,
    get_admin_logs,
    get_all_complaints,
    get_all_farmers,
    get_all_schemes,
    get_scheme_adoption_trend,
    get_stats,
    log_admin_action,
    update_complaint_status,
    update_scheme,
)
from i18n_utils import language_options, localize_department, localize_priority, localize_scheme_text, localize_status, t
from translations import DEPARTMENTS, get_text

STATE_COORDS = {
    "Andhra Pradesh": [15.9129, 79.7400],
    "Assam": [26.2006, 92.9376],
    "Bihar": [25.0961, 85.3131],
    "Chhattisgarh": [21.2787, 81.8661],
    "Gujarat": [22.2587, 71.1924],
    "Haryana": [29.0588, 76.0856],
    "Himachal Pradesh": [31.1048, 77.1734],
    "Jharkhand": [23.6102, 85.2799],
    "Karnataka": [15.3173, 75.7139],
    "Kerala": [10.8505, 76.2711],
    "Madhya Pradesh": [22.9734, 78.6569],
    "Maharashtra": [19.7515, 75.7139],
    "Manipur": [24.6637, 93.9063],
    "Odisha": [20.9517, 85.0985],
    "Punjab": [31.1471, 75.3412],
    "Rajasthan": [27.0238, 74.2179],
    "Tamil Nadu": [11.1271, 78.6569],
    "Telangana": [18.1124, 79.0193],
    "Uttar Pradesh": [26.8467, 80.9462],
    "Uttarakhand": [30.0668, 79.0193],
    "West Bengal": [22.9868, 87.8550],
    "Delhi": [28.7041, 77.1025],
    "Goa": [15.2993, 74.1240],
    "Meghalaya": [25.4670, 91.3662],
}


def show():
    lang = st.session_state.get("language", "en")
    admin = st.session_state.user_data

    with st.sidebar:
        st.markdown(
            f"""
        <div style='text-align:center; padding:1rem 0;'>
            <div style='font-size:2.5rem;'>🔧</div>
            <div style='font-size:1rem; font-weight:600; color:#e6edf3;'>{t('admin_panel', lang)}</div>
            <div style='font-size:0.8rem; color:#39d353;'>Smart Kisan Platform</div>
        </div>
        <hr style='border:1px solid #30363d;'>
        """,
            unsafe_allow_html=True,
        )
        options = language_options()
        keys = list(options.keys())
        new_lang = st.selectbox(t("language", lang), keys, format_func=lambda x: options[x], index=keys.index(lang) if lang in keys else 0)
        if new_lang != lang:
            st.session_state.language = new_lang
            st.rerun()

        if st.button(f"🚪 {get_text('logout')}", use_container_width=True):
            log_admin_action(admin["username"], "LOGOUT", "Admin logged out")
            for key in ["logged_in", "user_type", "user_data"]:
                st.session_state[key] = None
            st.session_state.logged_in = False
            st.session_state.page = "login"
            st.rerun()

    st.markdown(
        f"<div style='font-size:1.8rem; font-weight:700; color:#39d353; margin-bottom:1.5rem;'>🔧 {get_text('admin_dashboard')}</div>",
        unsafe_allow_html=True,
    )

    tabs = st.tabs([f"📊 {get_text('overview')}", f"📋 {get_text('manage_complaints')}", f"🏛️ {get_text('manage_schemes')}", f"🗺️ {get_text('map_view')}"])
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
    st.markdown(f"<div style='font-size:1.2rem; font-weight:600; color:#e6edf3; margin-bottom:1rem;'>📊 {t('platform_overview', lang)}</div>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    for col, (icon, label, value, color) in zip(
        [col1, col2, col3],
        [("👨‍🌾", get_text("total_farmers"), stats["total_farmers"], "#39d353"), ("📋", get_text("total_complaints"), stats["total_complaints"], "#388bfd"), ("✅", get_text("resolved"), stats["resolved_complaints"], "#2ea043")],
    ):
        with col:
            st.markdown(f"<div class='metric-card'><div style='font-size:1.8rem;'>{icon}</div><div style='font-size:1.8rem; font-weight:700; color:{color};'>{value}</div><div class='metric-label'>{label}</div></div>", unsafe_allow_html=True)

    complaints = get_all_complaints()
    if complaints:
        df = pd.DataFrame(complaints)
        col1, col2 = st.columns(2)
        with col1:
            priority_counts = df["priority"].value_counts().reset_index()
            priority_counts.columns = ["priority", "count"]
            fig = px.pie(priority_counts, names="priority", values="count", title=t("filter_by_priority", lang), color="priority", color_discrete_map={"High": "#f85149", "Medium": "#d29922", "Low": "#39d353"})
            fig.update_layout(plot_bgcolor="#161b22", paper_bgcolor="#1c2128", font_color="#e6edf3", title_font_color="#39d353")
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            status_counts = df["status"].value_counts().reset_index()
            status_counts.columns = ["status", "count"]
            fig2 = px.bar(status_counts, x="status", y="count", title=t("filter_by_status", lang), color="count", color_continuous_scale="Greens")
            fig2.update_layout(plot_bgcolor="#161b22", paper_bgcolor="#1c2128", font_color="#e6edf3", title_font_color="#39d353")
            st.plotly_chart(fig2, use_container_width=True)


def _show_complaints_mgmt(admin, lang):
    st.markdown(f"<div style='font-size:1.2rem; font-weight:600; color:#e6edf3; margin-bottom:1rem;'>📋 {t('complaint_management', lang)}</div>", unsafe_allow_html=True)
    complaints = get_all_complaints()
    if not complaints:
        st.info(t("no_complaints_yet", lang))
        return

    status_values = [t("all", lang), t("submitted", lang), t("in_progress", lang), t("resolved_status", lang)]
    priority_values = [t("all", lang), t("high", lang), t("medium", lang), t("low", lang)]

    col1, col2, col3 = st.columns(3)
    with col1:
        filter_status = st.selectbox(t("filter_by_status", lang), status_values)
    with col2:
        filter_priority = st.selectbox(t("filter_by_priority", lang), priority_values)
    with col3:
        states = sorted(list(set(c["state"] for c in complaints if c["state"])))
        filter_state = st.selectbox(t("filter_by_state", lang), [t("all", lang)] + states)

    status_reverse = {t("submitted", lang): "Submitted", t("in_progress", lang): "In Progress", t("resolved_status", lang): "Resolved", t("all", lang): "All"}
    priority_reverse = {t("high", lang): "High", t("medium", lang): "Medium", t("low", lang): "Low", t("all", lang): "All"}

    filtered = complaints
    if status_reverse[filter_status] != "All":
        filtered = [c for c in filtered if c["status"] == status_reverse[filter_status]]
    if priority_reverse[filter_priority] != "All":
        filtered = [c for c in filtered if c["priority"] == priority_reverse[filter_priority]]
    if filter_state != t("all", lang):
        filtered = [c for c in filtered if c["state"] == filter_state]

    st.markdown(f"<div style='color:#8b949e; margin-bottom:1rem;'>{t('showing_count_complaints', lang)} <b style='color:#39d353;'>{len(filtered)}</b> {t('complaints_label', lang)}</div>", unsafe_allow_html=True)

    priority_colors = {"High": "#f85149", "Medium": "#d29922", "Low": "#39d353"}
    status_icons = {"Submitted": "📨", "In Progress": "⚙️", "Resolved": "✅"}
    for c in filtered:
        pcolor = priority_colors.get(c["priority"], "#39d353")
        sicon = status_icons.get(c["status"], "📨")
        with st.expander(f"{sicon} [{localize_priority(c['priority'], lang)}] {c['complaint_id']} — {c['title'][:50]}"):
            col1, col2 = st.columns([2, 1])
            with col1:
                st.markdown(f"**{get_text('farmer')}:** {c['farmer_name']} | **{get_text('state')}:** {c['state']} | **{get_text('district')}:** {c['district']}")
                st.markdown(f"**{get_text('complaint_desc')}:** {c['description']}")
                st.markdown(f"**{t('filed', lang)}:** {c['created_at'][:16]} | **{t('updated', lang)}:** {c['updated_at'][:16]}")
                st.markdown(f"**{t('current_department', lang)}:** {c['department']}")
                if c.get("image_path") and isinstance(c["image_path"], str) and os.path.exists(c["image_path"]):
                    st.image(c["image_path"], width=300, caption=t("attached_image", lang))

            with col2:
                st.markdown(f"<div style='background:rgba(0,0,0,0.2); border:1px solid {pcolor}; border-radius:8px; padding:1rem; text-align:center; margin-bottom:0.5rem;'><div style='color:{pcolor}; font-weight:700; font-size:1.1rem;'>{localize_priority(c['priority'], lang)}</div><div style='color:#8b949e; font-size:0.8rem;'>{t('ai_priority', lang)}</div></div>", unsafe_allow_html=True)

                status_options = ["Submitted", "In Progress", "Resolved"]
                new_status = st.selectbox(get_text("update_status"), [localize_status(x, lang) for x in status_options], index=status_options.index(c["status"]), key=f"status_{c['complaint_id']}")
                reverse_status = {localize_status(x, lang): x for x in status_options}
                new_status_db = reverse_status[new_status]
                new_dept = st.selectbox(t("reassign_dept", lang), DEPARTMENTS, index=DEPARTMENTS.index(c["department"]) if c["department"] in DEPARTMENTS else 0, key=f"dept_{c['complaint_id']}")

                if st.button(f"💾 {get_text('update_status')}", key=f"upd_{c['complaint_id']}", use_container_width=True):
                    update_complaint_status(c["complaint_id"], new_status_db, new_dept)
                    log_admin_action(admin["username"], "UPDATE_COMPLAINT", f"Complaint {c['complaint_id']} -> {new_status_db} | Dept: {new_dept}")
                    st.success(f"✅ {t('updated_success', lang)}")
                    st.rerun()


def _show_schemes_mgmt(admin, lang):
    st.markdown(f"<div style='font-size:1.2rem; font-weight:600; color:#e6edf3; margin-bottom:1rem;'>🏛️ {t('scheme_management', lang)}</div>", unsafe_allow_html=True)
    tab1, tab2 = st.tabs([f"📋 {t('view_manage', lang)}", f"➕ {t('add_new_scheme_tab', lang)}"])

    with tab1:
        for s in get_all_schemes():
            display_name = localize_scheme_text(s["name"], lang)
            display_desc = localize_scheme_text(s["description"], lang)
            display_benefits = localize_scheme_text(s["benefits"], lang)
            display_dept = localize_department(s["department"], lang)

            with st.expander(f"🏛️ {display_name} — {s['adoption_count']:,} {t('adoptions', lang)} | ★ {s['rating']}"):
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"**{get_text('description')}:** {display_desc}")
                    st.markdown(f"**{get_text('benefits')}:** {display_benefits}")
                    st.markdown(f"**{get_text('department')}:** {display_dept}")
                    st.markdown(f"**{t('eligible_states_label', lang)}:** {s['eligible_states']} | **{t('eligible_crops_label', lang)}:** {s['eligible_crops']} | **{get_text('farmer_category')}:** {s['eligible_categories']}")

                with col2:
                    if st.button(f"🗑️ {get_text('delete_scheme')}", key=f"del_{s['id']}", use_container_width=True):
                        delete_scheme(s["id"])
                        log_admin_action(admin["username"], "DELETE_SCHEME", f"Deleted scheme: {s['name']}")
                        st.success(t("deleted", lang))
                        st.rerun()

                with st.form(f"edit_scheme_{s['id']}"):
                    st.markdown(f"**✏️ {t('edit_scheme_label', lang)}**")
                    ec1, ec2 = st.columns(2)
                    with ec1:
                        e_name = st.text_input(t("name_label", lang), value=s["name"])
                        e_desc = st.text_area(get_text("description"), value=s["description"], height=80)
                        e_benefits = st.text_area(t("benefits_label", lang), value=s["benefits"], height=80)
                    with ec2:
                        e_states = st.text_input(t("eligible_states_label", lang), value=s["eligible_states"])
                        e_crops = st.text_input(t("eligible_crops_label", lang), value=s["eligible_crops"])
                        e_cats = st.text_input(get_text("eligible_categories"), value=s["eligible_categories"])
                        e_dept = st.text_input(get_text("department"), value=s["department"])

                    if st.form_submit_button(f"💾 {t('save_changes', lang)}", use_container_width=True):
                        update_scheme(
                            s["id"],
                            {
                                "name": e_name,
                                "description": e_desc,
                                "benefits": e_benefits,
                                "eligible_states": e_states,
                                "eligible_crops": e_crops,
                                "eligible_categories": e_cats,
                                "department": e_dept,
                            },
                        )
                        log_admin_action(admin["username"], "EDIT_SCHEME", f"Edited scheme: {e_name}")
                        st.success(f"✅ {t('scheme_updated', lang)}")
                        st.rerun()

    with tab2:
        st.markdown(f"**➕ {t('add_new_govt_scheme', lang)}**")
        with st.form("add_scheme_form"):
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input(f"📌 {get_text('scheme_name')}", placeholder=t("scheme_name_placeholder", lang))
                desc = st.text_area(f"📝 {get_text('description')}", placeholder=t("brief_description", lang), height=100)
                benefits = st.text_area(f"💰 {get_text('benefits')}", placeholder=t("list_benefits", lang), height=100)
            with col2:
                states_elig = st.text_input(f"🗺️ {get_text('eligible_states')}", value="All")
                crops_elig = st.text_input(f"🌾 {get_text('eligible_crops')}", value="All")
                cats_elig = st.text_input(f"👥 {get_text('eligible_categories')}", value="All")
                dept = st.selectbox(f"🏢 {get_text('department')}", DEPARTMENTS)

            if st.form_submit_button(f"✅ {get_text('save_scheme')}", use_container_width=True):
                if not (name and desc and benefits):
                    st.warning(t("fill_required_fields", lang))
                    return
                add_scheme(
                    {
                        "name": name,
                        "description": desc,
                        "benefits": benefits,
                        "eligible_states": states_elig,
                        "eligible_crops": crops_elig,
                        "eligible_categories": cats_elig,
                        "department": dept,
                    }
                )
                log_admin_action(admin["username"], "ADD_SCHEME", f"Added scheme: {name}")
                st.success(f"✅ {name} - {t('scheme_added_success', lang)}")
                st.rerun()

def _show_maps(lang):
    st.markdown(f"<div style='font-size:1.2rem; font-weight:600; color:#e6edf3; margin-bottom:1rem;'>🗺️ {t('map_dashboard', lang)}</div>", unsafe_allow_html=True)
    complaints = get_all_complaints()
    farmers = get_all_farmers()

    map_options = [f"🔴 {t('complaint_heatmap', lang)}", f"💧 {t('water_scarcity_zones', lang)}", f"🏛️ {t('scheme_adoption_heatmap', lang)}"]
    map_type = st.radio(t("select_map_view", lang), map_options, horizontal=True)

    m = folium.Map(location=[20.5937, 78.9629], zoom_start=5, tiles="CartoDB positron")

    if map_type == map_options[0] and complaints:
        state_counts = {}
        for c in complaints:
            if c["state"]:
                state_counts[c["state"]] = state_counts.get(c["state"], 0) + 1
        for state, count in state_counts.items():
            coords = STATE_COORDS.get(state)
            if not coords:
                continue
            color = "#f85149" if count > 5 else "#d29922" if count > 2 else "#39d353"
            folium.CircleMarker(location=coords, radius=min(count * 8 + 10, 50), color=color, fill=True, fill_opacity=0.7, popup=folium.Popup(f"<b>{state}</b><br>Complaints: {count}", max_width=200), tooltip=f"{state}: {count}").add_to(m)
        st.markdown(f"<div class='alert-info'>{t('complaint_distribution_info', lang, count=len(state_counts))}</div>", unsafe_allow_html=True)

    elif map_type == map_options[1]:
        water_scarce = {
            "Rajasthan": t("high_scarcity", lang),
            "Gujarat": t("medium_scarcity", lang),
            "Maharashtra": t("medium_scarcity", lang),
            "Andhra Pradesh": t("low_scarcity", lang),
            "Karnataka": t("medium_scarcity", lang),
            "Telangana": t("low_scarcity", lang),
            "Madhya Pradesh": t("low_scarcity", lang),
            "Uttar Pradesh": t("low_scarcity", lang),
        }
        color_map = {t("high_scarcity", lang): "#f85149", t("medium_scarcity", lang): "#d29922", t("low_scarcity", lang): "#388bfd"}
        for state, level in water_scarce.items():
            coords = STATE_COORDS.get(state)
            if not coords:
                continue
            folium.CircleMarker(location=coords, radius=20, color=color_map[level], fill=True, fill_opacity=0.6, popup=folium.Popup(f"<b>{state}</b><br>{level}", max_width=200), tooltip=f"{state}: {level}").add_to(m)
        st.markdown(
            f"<div style='display:flex; gap:1rem; margin-bottom:1rem;'><span style='color:#f85149;'>🔴 {t('high_scarcity', lang)}</span><span style='color:#d29922;'>🟡 {t('medium_scarcity', lang)}</span><span style='color:#388bfd;'>🔵 {t('low_scarcity', lang)}</span></div>",
            unsafe_allow_html=True,
        )

    elif map_type == map_options[2] and farmers:
        state_farmers = {}
        for f in farmers:
            if f["state"]:
                state_farmers[f["state"]] = state_farmers.get(f["state"], 0) + 1
        for state, count in state_farmers.items():
            coords = STATE_COORDS.get(state)
            if not coords:
                continue
            folium.CircleMarker(location=coords, radius=min(count * 10 + 8, 40), color="#39d353", fill=True, fill_opacity=0.6, popup=folium.Popup(f"<b>{state}</b><br>Farmers: {count}", max_width=200), tooltip=f"{state}: {count}").add_to(m)

    st_folium(m, width=None, height=500)


def _show_logs(lang):
    st.markdown(f"<div style='font-size:1.2rem; font-weight:600; color:#e6edf3; margin-bottom:1rem;'>🧾 {get_text('activity_log')}</div>", unsafe_allow_html=True)
    logs = get_admin_logs()
    if not logs:
        st.info("No activity logged yet.")
        return
    for log in logs:
        action_icons = {"LOGIN": "🔐", "LOGOUT": "🚪", "UPDATE_COMPLAINT": "📋", "DELETE_SCHEME": "🗑️", "EDIT_SCHEME": "✏️", "ADD_SCHEME": "➕"}
        icon = action_icons.get(log["action"], "📌")
        st.markdown(
            f"<div style='display:flex; gap:1rem; align-items:center; padding:0.6rem; border-bottom:1px solid #30363d;'><div style='font-size:1.2rem;'>{icon}</div><div style='flex:1;'><span style='color:#39d353; font-weight:600;'>{log['action']}</span><span style='color:#8b949e; font-size:0.85rem;'> — {log['details']}</span></div><div style='color:#8b949e; font-size:0.8rem;'>{log['timestamp'][:16]}</div></div>",
            unsafe_allow_html=True,
        )

