import os
from datetime import datetime

import plotly.graph_objects as go
import streamlit as st

from ai_logic import detect_priority, get_crop_rotation, get_irrigation_plan, route_department
from database import (
    adopt_scheme,
    create_complaint,
    get_complaints_by_farmer,
    get_farmer_by_id,
    get_matching_schemes,
    update_farmer_profile,
)
from i18n_utils import (
    language_options,
    localize_department,
    localize_free_text,
    localize_priority,
    localize_scheme_text,
    localize_status,
    localize_term,
    t,
)
from translations import CROPS, FARMER_CATEGORIES, SOIL_TYPES, STATES, WATER_SOURCES, get_text


def show():
    lang = st.session_state.get("language", "en")
    farmer = get_farmer_by_id(st.session_state.user_data["id"])
    st.session_state.user_data = farmer

    with st.sidebar:
        st.markdown(
            f"""
        <div style='text-align:center; padding:1rem 0;'>
            <div style='font-size:2.5rem;'></div>
            <div style='font-size:1rem; font-weight:600; color:#163a2f;'>{farmer['name']}</div>
            <div style='font-size:0.8rem; color:#4a7a5a;'>{farmer.get('state','') or t('state_not_set', lang)}  {farmer.get('district','') or t('district_not_set', lang)}</div>
            <div style='font-size:0.75rem; color:#2e7d32; margin-top:0.25rem;'> {farmer['phone']}</div>
        </div>
        <hr style='border:1px solid #c8e3cf;'>
        """,
            unsafe_allow_html=True,
        )

        if farmer.get("crop_type"):
            st.markdown(
                f"""
            <div class='kisan-card' style='padding:0.75rem;'>
                <div style='font-size:0.8rem; color:#4a7a5a;'>{t('current_profile', lang)}</div>
                <div style='font-size:0.85rem; color:#163a2f; margin-top:0.3rem;'>
                     {farmer.get('crop_type','')}<br>
                     {farmer.get('area_size','') or '-'} acres<br>
                     {localize_term('soil', farmer.get('soil_type','-'), lang)}<br>
                     {localize_term('water', farmer.get('water_source','-'), lang)}
                </div>
            </div>
            """,
                unsafe_allow_html=True,
            )

        st.markdown("<br>", unsafe_allow_html=True)
        options = language_options()
        keys = list(options.keys())
        new_lang = st.selectbox(
            t("language", lang),
            keys,
            format_func=lambda x: options[x],
            index=keys.index(lang) if lang in keys else 0,
        )
        if new_lang != lang:
            st.session_state.language = new_lang
            st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button(f" {get_text('logout')}", use_container_width=True):
            for key in ["logged_in", "user_type", "user_data"]:
                st.session_state[key] = None
            st.session_state.logged_in = False
            st.session_state.page = "login"
            st.rerun()

    hcol1, hcol2 = st.columns([6, 1])
    with hcol1:
        st.markdown(
            f"""
        <div style='display:flex; align-items:center; gap:1rem; margin-bottom:1.2rem;'>
            <div style='font-size:1.8rem; font-weight:700; color:#39d353;'>🌿 {get_text('dashboard')}</div>
            <div style='color:#8b949e; font-size:0.9rem;'>{get_text('welcome_farmer')}, {farmer['name']}!</div>
        </div>
        """,
            unsafe_allow_html=True,
        )
    with hcol2:
        if st.button(f"↩ {get_text('logout')}", key="farmer_logout_top", use_container_width=True):
            for key in ["logged_in", "user_type", "user_data"]:
                st.session_state[key] = None
            st.session_state.logged_in = False
            st.session_state.page = "login"
            st.rerun()

    nav_icons = {
        "tutorial": "🧭",
        "profile": "👤",
        "irrigation": "💧",
        "schemes": "🏛️",
        "complaints": "📝",
    }
    nav_items = [
        ("tutorial", _show_tutorial),
        ("profile", lambda x: _show_profile(farmer, x)),
        ("irrigation", lambda x: _show_irrigation(farmer, x)),
        ("schemes", lambda x: _show_schemes(farmer, x)),
        ("complaints", lambda x: _show_complaints(farmer, x)),
    ]
    nav_keys = [k for k, _ in nav_items]

    if "farmer_active_tab" not in st.session_state or st.session_state.farmer_active_tab not in nav_keys:
        st.session_state.farmer_active_tab = "tutorial"

    nav_cols = st.columns(len(nav_items))
    for idx, (key, _) in enumerate(nav_items):
        label = f"{nav_icons.get(key, '')} {get_text(key)}".strip()
        with nav_cols[idx]:
            if st.button(label, key=f"farmer_nav_{key}", use_container_width=True):
                st.session_state.farmer_active_tab = key

    st.markdown("<div class='green-divider'></div>", unsafe_allow_html=True)
    active_key = st.session_state.farmer_active_tab
    for key, renderer in nav_items:
        if key == active_key:
            renderer(lang)
            break


def _show_tutorial(lang):
    st.markdown(
        f"<div style='font-size:1.4rem; font-weight:600; color:#39d353; margin-bottom:1.5rem;'>🧭 {get_text('tutorial_title')}</div>",
        unsafe_allow_html=True,
    )

    steps = [
        ("1", get_text("tut_step1"), t("tutorial_desc_1", lang)),
        ("2", get_text("tut_step2"), t("tutorial_desc_2", lang)),
        ("3", get_text("tut_step3"), t("tutorial_desc_3", lang)),
        ("4", get_text("tut_step5"), t("tutorial_desc_5", lang)),
    ]
    for i, (icon, title, desc) in enumerate(steps):
        clean_title = title.split(":", 1)[1].strip() if ":" in title else title
        st.markdown(
            f"""
        <div class='kisan-card' style='display:flex; gap:1rem; align-items:flex-start;'>
            <div style='font-size:1.2rem; min-width:48px; text-align:center; color:#2e7d32; font-weight:700;'>{icon}</div>
            <div>
                <div style='font-weight:600; color:#e6edf3; margin-bottom:0.3rem;'>
                    {t('tutorial_step_prefix', lang)} {icon}: {clean_title}
                </div>
                <div style='color:#4a7a5a; font-size:0.9rem;'>{desc}</div>
            </div>
        </div>
        """,
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f"<div class='alert-success'><b>{t('quick_start', lang)}</b></div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)
    demo_stats = [
        ("", "10+", t("crops_supported", lang)),
        ("", "10+", t("govt_schemes", lang)),
        ("", "Smart", t("irrigation_ai", lang)),
        ("", "Instant", t("crop_rotation_label", lang)),
    ]
    for col, (icon, val, label) in zip([col1, col2, col3, col4], demo_stats):
        with col:
            st.markdown(
                f"""
            <div class='metric-card'>
                <div style='font-size:1.5rem;'>{icon}</div>
                <div class='metric-value'>{val}</div>
                <div class='metric-label'>{label}</div>
            </div>
            """,
                unsafe_allow_html=True,
            )


def _show_profile(farmer, lang):
    st.markdown(
        f"<div style='font-size:1.4rem; font-weight:600; color:#39d353; margin-bottom:1.5rem;'>👤 {get_text('profile')}</div>",
        unsafe_allow_html=True,
    )
    with st.form("profile_form"):
        col1, col2 = st.columns(2)
        with col1:
            state = st.selectbox(
                f" {get_text('state')}",
                STATES,
                index=STATES.index(farmer["state"]) if farmer.get("state") in STATES else 0,
                format_func=lambda x: localize_term("states", x, lang),
            )
            crop = st.selectbox(
                f" {get_text('crop_type')}",
                CROPS,
                index=CROPS.index(farmer["crop_type"]) if farmer.get("crop_type") in CROPS else 0,
                format_func=lambda x: localize_term("crops", x, lang),
            )
            soil = st.selectbox(
                f" {get_text('soil_type')}",
                SOIL_TYPES,
                index=SOIL_TYPES.index(farmer["soil_type"]) if farmer.get("soil_type") in SOIL_TYPES else 0,
                format_func=lambda x: localize_term("soil", x, lang),
            )
        with col2:
            district = st.text_input(f" {get_text('district')}", value=farmer.get("district") or "")
            area = st.number_input(
                f" {get_text('area_size')}", min_value=0.1, max_value=1000.0, value=float(farmer.get("area_size") or 1.0), step=0.5
            )
            water = st.selectbox(
                f" {get_text('water_source')}",
                WATER_SOURCES,
                index=WATER_SOURCES.index(farmer["water_source"]) if farmer.get("water_source") in WATER_SOURCES else 0,
                format_func=lambda x: localize_term("water", x, lang),
            )
            category = st.selectbox(
                f" {get_text('farmer_category')}",
                FARMER_CATEGORIES,
                index=FARMER_CATEGORIES.index(farmer["farmer_category"]) if farmer.get("farmer_category") in FARMER_CATEGORIES else 0,
                format_func=lambda x: localize_term("farmer_category", x, lang),
            )

        if st.form_submit_button(f" {get_text('save_profile')}", use_container_width=True):
            update_farmer_profile(
                farmer["id"],
                {
                    "crop_type": crop,
                    "area_size": area,
                    "soil_type": soil,
                    "water_source": water,
                    "farmer_category": category,
                    "state": state,
                    "district": district,
                },
            )
            st.session_state.user_data = get_farmer_by_id(farmer["id"])
            st.success(f" {get_text('profile_saved')}")
            st.rerun()


def _show_irrigation(farmer, lang):
    st.markdown(
        f"<div style='font-size:1.4rem; font-weight:600; color:#39d353; margin-bottom:1rem;'>💧 {get_text('irrigation')}</div>",
        unsafe_allow_html=True,
    )
    if not farmer.get("crop_type"):
        st.markdown(f"<div class='alert-warning'> {t('fill_profile_first_irrigation', lang)}</div>", unsafe_allow_html=True)
        return

    crop = farmer.get("crop_type", "Default")
    soil = farmer.get("soil_type", "Default")
    water = farmer.get("water_source", "Canal")
    area = float(farmer.get("area_size") or 1.0)

    if st.button(f" {get_text('get_plan')}", use_container_width=True):
        st.session_state["irr_plan"] = get_irrigation_plan(crop, soil, water, area, lang=lang)

    if "irr_plan" not in st.session_state:
        st.markdown(
            f"<div class='alert-info'> {localize_free_text('Click Generate Irrigation Plan to get your personalized schedule.', lang)}</div>",
            unsafe_allow_html=True,
        )
        return

    plan = st.session_state["irr_plan"]
    crop_local = localize_term("crops", crop, lang)
    st.markdown(
        f"<div style='font-size:1.1rem; font-weight:600; color:#1f5b40; margin:1rem 0;'>{get_text('irrigation_plan')} {crop_local}</div>",
        unsafe_allow_html=True,
    )

    col1, col2, col3, col4 = st.columns(4)
    metrics = [
        ("", get_text("water_required"), plan["water_per_acre"]),
        ("", get_text("frequency"), plan["frequency"]),
        ("", get_text("est_yield"), plan["estimated_yield"]),
        ("", t("best_time", lang), plan["best_time"]),
    ]
    for col, (icon, label, value) in zip([col1, col2, col3, col4], metrics):
        with col:
            st.markdown(
                f"""
            <div class='metric-card'>
                <div style='font-size:1.5rem;'>{icon}</div>
                <div style='font-size:1rem; font-weight:600; color:#2e7d32;'>{value}</div>
                <div class='metric-label'>{label}</div>
            </div>
            """,
                unsafe_allow_html=True,
            )

    if plan["efficiency_tip"]:
        st.markdown(f"<div class='alert-info'>{plan['efficiency_tip']}</div>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"** {t('irrigation_schedule_next_5', lang)}**")
        for s in plan["schedule"]:
            st.markdown(
                f"<div style='padding:0.4rem; border-left:3px solid #2e7d32; margin:0.3rem 0; color:#163a2f; font-size:0.9rem;'>{s}</div>",
                unsafe_allow_html=True,
            )
    with col2:
        st.markdown(f"** {t('crop_growth_stage_guide', lang)}**")
        for stage in plan["stages"]:
            st.markdown(
                f"<div style='padding:0.4rem; border-left:3px solid #43a047; margin:0.3rem 0; color:#4a7a5a; font-size:0.85rem;'>{stage}</div>",
                unsafe_allow_html=True,
            )

    days = [i * int(plan["freq_days"]) for i in range(1, 8)]
    water_vals = [int(plan["water_per_acre_num"]) * 0.2 for _ in days]
    fig = go.Figure()
    fig.add_trace(go.Bar(x=[localize_free_text(f"Day {d}", lang) for d in days], y=water_vals, marker_color="#43a047", name=localize_free_text("Water (L)", lang)))
    fig.update_layout(
        title=f"{t('irrigation_schedule_for', lang)} {crop_local}",
        plot_bgcolor="#ffffff",
        paper_bgcolor="#ffffff",
        font_color="#1f5b40",
        title_font_color="#2e7d32",
        xaxis=dict(gridcolor="#d8eadc", title=""),
        yaxis=dict(gridcolor="#d8eadc", title=localize_free_text("Water (L)", lang)),
        height=300,
    )
    st.plotly_chart(fig, use_container_width=True)


def _show_rotation(farmer, lang):
    st.markdown(
        f"<div style='font-size:1.4rem; font-weight:600; color:#2e7d32; margin-bottom:1rem;'> {get_text('rotation')}</div>",
        unsafe_allow_html=True,
    )
    if not farmer.get("crop_type"):
        st.markdown(f"<div class='alert-warning'> {t('fill_profile_first', lang)}</div>", unsafe_allow_html=True)
        return

    crop = farmer.get("crop_type", "Default")
    soil = farmer.get("soil_type", "Default")
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f"{t('current_crop_soil', lang)}: **{crop}** | {t('soil_label', lang)}: **{soil}**")
    with col2:
        if st.button(f" {get_text('get_rotation')}", use_container_width=True):
            st.session_state["rotation_result"] = get_crop_rotation(crop, soil, lang=lang)

    if "rotation_result" not in st.session_state:
        return
    r = st.session_state["rotation_result"]

    st.markdown(
        f"""
    <div class='kisan-card' style='border-color:#2e7d32;'>
        <div style='font-size:1.2rem; font-weight:700; color:#2e7d32; margin-bottom:1rem;'>
            {crop}   {r['next_crop']}
        </div>
        <div style='display:grid; grid-template-columns:1fr 1fr; gap:1rem;'>
            <div>
                <div style='color:#4a7a5a; font-size:0.85rem;'>{get_text('next_crop')}</div>
                <div style='color:#163a2f; font-size:1.1rem; font-weight:600;'> {r['next_crop']}</div>
            </div>
            <div>
                <div style='color:#4a7a5a; font-size:0.85rem;'>{get_text('soil_impact')}</div>
                <div style='color:#2e7d32; font-size:0.9rem;'>{r['soil_impact']}</div>
            </div>
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )
    st.markdown(
        f"""
    <div class='kisan-card'>
        <div style='color:#4a7a5a; font-size:0.85rem;'>{get_text('rotation_reason')}</div>
        <div style='color:#163a2f; margin-top:0.5rem;'> {r['reason']}</div>
    </div>
    """,
        unsafe_allow_html=True,
    )
    st.markdown(
        f"""
    <div class='kisan-card'>
        <div style='color:#4a7a5a; font-size:0.85rem;'>{t('soil_specific_tip', lang)}</div>
        <div style='color:#163a2f; margin-top:0.5rem;'> {r['soil_tip']}</div>
    </div>
    """,
        unsafe_allow_html=True,
    )
    st.markdown(f"<div class='alert-info'> {r['fallow_option']}</div>", unsafe_allow_html=True)


def _show_schemes(farmer, lang):
    st.markdown(
        f"<div style='font-size:1.4rem; font-weight:600; color:#39d353; margin-bottom:1rem;'>🏛️ {get_text('schemes')}</div>",
        unsafe_allow_html=True,
    )

    state = farmer.get("state") or "All"
    crop = farmer.get("crop_type") or "All"
    category_raw = farmer.get("farmer_category") or "All"
    category = category_raw.split("(")[0].strip() if "(" in category_raw else category_raw

    schemes = get_matching_schemes(state, crop, category)
    if not schemes:
        st.markdown(f"<div class='alert-warning'> {get_text('no_schemes')}</div>", unsafe_allow_html=True)
        return

    state_local = localize_term("states", state, lang)
    crop_local = localize_term("crops", crop, lang)
    category_local = localize_term("farmer_category", category_raw, lang)
    st.markdown(
        f"<div class='alert-success'> {t('schemes_found', lang)} <b>{len(schemes)}</b> {t('schemes_matching_profile', lang)} ({state_local}  {crop_local}  {category_local})</div>",
        unsafe_allow_html=True,
    )
    for s in schemes:
        display_name = localize_scheme_text(s["name"], lang)
        display_desc = localize_scheme_text(s["description"], lang)
        display_benefits = localize_scheme_text(s["benefits"], lang)
        display_dept = localize_department(s["department"], lang)
        stars = "*" * int(s["rating"])
        with st.expander(f" {display_name}   {s['adoption_count']} {t('farmers', lang)}"):
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"**{get_text('description')}:** {display_desc}")
                st.markdown(f"**{get_text('benefits')}:** {display_benefits}")
                st.markdown(f"**{get_text('department')}:** {display_dept}")
                st.markdown(f"**{t('eligible_states_label', lang)}:** {s['eligible_states']} | **{t('eligible_crops_label', lang)}:** {s['eligible_crops']}")
            with col2:
                st.markdown(
                    f"""
                <div class='metric-card'>
                    <div style='font-size:1.2rem; color:#2e7d32; font-weight:700;'>{s['rating']}</div>
                    <div style='font-size:0.8rem;'>{stars}</div>
                    <div style='font-size:0.75rem; color:#4a7a5a; margin-top:0.5rem;'>{s['adoption_count']:,} {t('adoptions', lang)}</div>
                </div>
                """,
                    unsafe_allow_html=True,
                )
            if st.button(f" {get_text('apply_scheme')}", key=f"adopt_{s['id']}", use_container_width=True):
                adopt_scheme(s["id"], farmer["id"])
                st.success(f" {t('interest_registered', lang)} **{display_name}**. {t('department_will_contact', lang)}")


def _show_complaints(farmer, lang):
    st.markdown(
        f"<div style='font-size:1.4rem; font-weight:600; color:#39d353; margin-bottom:1rem;'>📝 {get_text('complaints')}</div>",
        unsafe_allow_html=True,
    )

    tab1, tab2 = st.tabs([f" {get_text('submit_complaint')}", f" {get_text('my_complaints')}"])
    with tab1:
        with st.form("complaint_form"):
            title = st.text_input(f" {get_text('complaint_title')}", placeholder=t("brief_issue_title", lang))
            desc = st.text_area(f" {get_text('complaint_desc')}", placeholder=t("issue_detail_placeholder", lang), height=120)
            image = st.file_uploader(f" {get_text('upload_image')}", type=["jpg", "jpeg", "png"])

            if st.form_submit_button(f" {get_text('submit_complaint')}", use_container_width=True):
                if not (title and desc):
                    st.warning(f" {get_text('fill_all')}")
                    return

                priority = detect_priority(title, desc)
                department = route_department(title, desc)
                image_path = None
                if image:
                    os.makedirs("complaint_images", exist_ok=True)
                    image_path = f"complaint_images/{farmer['id']}_{datetime.now().strftime('%Y%m%d%H%M%S')}.jpg"
                    with open(image_path, "wb") as f:
                        f.write(image.read())

                cid = create_complaint(
                    farmer_id=farmer["id"],
                    farmer_name=farmer["name"],
                    state=farmer.get("state", ""),
                    district=farmer.get("district", ""),
                    title=title,
                    description=desc,
                    priority=priority,
                    department=department,
                    image_path=image_path,
                )
                priority_badge = {"High": "", "Medium": "", "Low": ""}
                st.success(f" {get_text('complaint_submitted')}")
                st.markdown(
                    f"""
                <div class='kisan-card' style='border-color:#2e7d32;'>
                    <div><b>{get_text('complaint_id')}:</b> <span style='color:#2e7d32; font-family:monospace;'>{cid}</span></div>
                    <div style='margin-top:0.5rem;'><b>{get_text('priority')}:</b> {priority_badge.get(priority,'')} {localize_priority(priority, lang)}</div>
                    <div><b>{t('routed_to', lang)}:</b> {department}</div>
                    <div style='color:#4a7a5a; font-size:0.85rem; margin-top:0.5rem;'>{t('track_complaint_hint', lang)}</div>
                </div>
                """,
                    unsafe_allow_html=True,
                )

    with tab2:
        complaints = get_complaints_by_farmer(farmer["id"])
        if not complaints:
            st.markdown(f"<div class='alert-info'> {get_text('no_complaints')}</div>", unsafe_allow_html=True)
            return

        st.markdown(
            f"<div style='color:#4a7a5a; margin-bottom:1rem;'>{t('total_complaints_count', lang)}: <b style='color:#2e7d32;'>{len(complaints)}</b> {t('complaints_label', lang)}</div>",
            unsafe_allow_html=True,
        )
        for c in complaints:
            priority_colors = {"High": "#f85149", "Medium": "#d29922", "Low": "#43a047"}
            status_icons = {"Submitted": "", "In Progress": "", "Resolved": ""}
            pcolor = priority_colors.get(c["priority"], "#2e7d32")
            sicon = status_icons.get(c["status"], "")

            st.markdown(
                f"""
            <div class='kisan-card'>
                <div style='display:flex; justify-content:space-between; align-items:flex-start;'>
                    <div>
                        <div style='font-weight:600; color:#163a2f;'>{c['title']}</div>
                        <div style='font-family:monospace; font-size:0.8rem; color:#2e7d32;'>{c['complaint_id']}</div>
                    </div>
                    <div style='text-align:right;'>
                        <span style='background:#f8f8f8; border:1px solid {pcolor}; color:{pcolor}; border-radius:20px; padding:0.2rem 0.6rem; font-size:0.75rem;'>{localize_priority(c['priority'], lang)}</span>
                    </div>
                </div>
                <div style='color:#4a7a5a; font-size:0.85rem; margin:0.5rem 0;'>{c['description'][:120]}{'...' if len(c['description']) > 120 else ''}</div>
                <div style='display:flex; justify-content:space-between; font-size:0.8rem; color:#4a7a5a;'>
                    <div>{sicon} {get_text('status')}: <b style='color:#163a2f;'>{localize_status(c['status'], lang)}</b></div>
                    <div> {c['department']}</div>
                    <div> {c['created_at'][:10]}</div>
                </div>
            </div>
            """,
                unsafe_allow_html=True,
            )


