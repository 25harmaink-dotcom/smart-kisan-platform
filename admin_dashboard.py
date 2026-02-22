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

# ── Light theme palette (matches app-wide CSS) ─────────────────────────────────
G      = "#2e7d32"
DG     = "#1b5e20"
M      = "#4a7a5a"
B      = "#c8e3cf"
BG     = "#f3fbf4"
BG2    = "#e7f6ea"
CARD   = "#ffffff"
SHADOW = "0 4px 16px rgba(30,90,50,0.09)"

STATE_COORDS = {
    "Andhra Pradesh":[15.91,79.74],"Assam":[26.20,92.94],"Bihar":[25.10,85.31],
    "Chhattisgarh":[21.28,81.87],"Gujarat":[22.26,71.19],"Haryana":[29.06,76.09],
    "Himachal Pradesh":[31.10,77.17],"Jharkhand":[23.61,85.28],"Karnataka":[15.32,75.71],
    "Kerala":[10.85,76.27],"Madhya Pradesh":[22.97,78.66],"Maharashtra":[19.75,75.71],
    "Manipur":[24.66,93.91],"Odisha":[20.95,85.10],"Punjab":[31.15,75.34],
    "Rajasthan":[27.02,74.22],"Tamil Nadu":[11.13,78.66],"Telangana":[18.11,79.02],
    "Uttar Pradesh":[26.85,80.95],"Uttarakhand":[30.07,79.02],"West Bengal":[22.99,87.85],
    "Delhi":[28.70,77.10],"Goa":[15.30,74.12],"Meghalaya":[25.47,91.37],
}

# ── Helpers ────────────────────────────────────────────────────────────────────

def _lc(fig):
    """Apply light theme to every Plotly figure."""
    fig.update_layout(
        plot_bgcolor=CARD,
        paper_bgcolor=BG,
        font_color=M,
        title_font_color=G,
        title_font_size=14,
        margin=dict(t=48, b=12, l=12, r=12),
        xaxis=dict(gridcolor=B, linecolor=B, tickfont=dict(color=M), zerolinecolor=B),
        yaxis=dict(gridcolor=B, linecolor=B, tickfont=dict(color=M), zerolinecolor=B),
        legend=dict(font=dict(color=M, size=11), bgcolor=CARD, bordercolor=B),
        coloraxis_colorbar=dict(tickfont=dict(color=M), title=dict(font=dict(color=M))),
    )
    return fig


def _title(text):
    st.markdown(
        f"<div style='font-size:1.25rem;font-weight:700;color:{G};"
        f"margin-bottom:1rem;padding-bottom:0.5rem;"
        f"border-bottom:2px solid {B};'>{text}</div>",
        unsafe_allow_html=True,
    )


def _card_metric(icon, label, value, color):
    return (
        f"<div style='background:{CARD};border:1px solid {B};border-radius:14px;"
        f"padding:1.4rem;text-align:center;box-shadow:{SHADOW};'>"
        f"<div style='font-size:1.8rem;margin-bottom:0.4rem;'>{icon}</div>"
        f"<div style='font-size:1.9rem;font-weight:700;color:{color};'>{value}</div>"
        f"<div style='font-size:0.82rem;color:{M};margin-top:0.3rem;font-weight:500;'>{label}</div>"
        f"</div>"
    )


# ── Main entry ─────────────────────────────────────────────────────────────────

def show():
    lang  = st.session_state.get("language", "en")
    admin = st.session_state.user_data

    # ── Sidebar ────────────────────────────────────────────────────────────────
    with st.sidebar:
        st.markdown(
            f"""
            <div style='text-align:center;padding:1.4rem 0 1rem;'>
                <div style='font-size:2.8rem;'>🔧</div>
                <div style='font-size:1rem;font-weight:700;color:{G};margin-top:0.3rem;'>
                    {t('admin_panel', lang)}
                </div>
                <div style='font-size:0.78rem;color:{M};margin-top:0.2rem;'>
                    Smart KisanJal
                </div>
                <div style='font-size:0.75rem;color:{M};margin-top:0.4rem;
                    background:{BG2};border-radius:8px;padding:0.3rem 0.6rem;
                    border:1px solid {B};display:inline-block;'>
                    👤 {admin.get("username","admin")}
                </div>
            </div>
            <hr style='border:1px solid {B};margin:0 0 1rem;'>
            """,
            unsafe_allow_html=True,
        )

        opts = language_options()
        keys = list(opts.keys())
        nl = st.selectbox(
            t("language", lang), keys,
            format_func=lambda x: opts[x],
            index=keys.index(lang) if lang in keys else 0,
        )
        if nl != lang:
            st.session_state.language = nl
            st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)

    # ── Page header ───────────────────────────────────────────────────────────
    st.markdown(
        f"""
        <div style='background:{CARD};border:1px solid {B};border-radius:16px;
            padding:1.4rem 1.8rem;margin-bottom:1.6rem;box-shadow:{SHADOW};
            display:flex;align-items:center;gap:1rem;'>
            <div style='font-size:2rem;'>🔧</div>
            <div>
                <div style='font-size:1.6rem;font-weight:700;color:{G};'>
                    {get_text('admin_dashboard')}
                </div>
                <div style='font-size:0.85rem;color:{M};'>
                    Smart KisanJal &nbsp;·&nbsp; {t('admin_panel', lang)}
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Tabs ──────────────────────────────────────────────────────────────────
    tabs = st.tabs([
        f"📊 {get_text('overview')}",
        f"📋 {get_text('manage_complaints')}",
        f"🏛️ {get_text('manage_schemes')}",
        f"🗺️ {get_text('map_view')}",
    ])
    with tabs[0]: _show_overview(lang)
    with tabs[1]: _show_complaints_mgmt(admin, lang)
    with tabs[2]: _show_schemes_mgmt(admin, lang)
    with tabs[3]: _show_maps(lang)


# ── Overview ───────────────────────────────────────────────────────────────────

def _show_overview(lang):
    stats = get_stats()
    _title(f"📊 {t('platform_overview', lang)}")

    resolution_rate = round(
        (stats["resolved_complaints"] / stats["total_complaints"] * 100)
        if stats["total_complaints"] > 0 else 0, 1
    )
    avg_adopt = (
        round(stats["total_adoptions"] / stats["total_schemes"])
        if stats["total_schemes"] > 0 else 0
    )

    # ── Metric cards ──────────────────────────────────────────────────────────
    cols = st.columns(4)
    metrics = [
        ("👨‍🌾", get_text("total_farmers"),    stats["total_farmers"],       G),
        ("📋",   get_text("total_complaints"),  stats["total_complaints"],    "#1565c0"),
        ("✅",   get_text("resolved"),          stats["resolved_complaints"], "#388e3c"),
        ("🏛️",  "Total Schemes",               stats["total_schemes"],       "#e65100"),
    ]
    for col, (icon, label, val, color) in zip(cols, metrics):
        col.markdown(_card_metric(icon, label, val, color), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    complaints     = get_all_complaints()
    adoption_trend = get_scheme_adoption_trend()

    # ── Charts row 1 ─────────────────────────────────────────────────────────
    cl, cr = st.columns(2)

    with cl:
        st.markdown(
            f"<div style='background:{CARD};border:1px solid {B};border-radius:14px;"
            f"padding:1rem 1.2rem 0.5rem;box-shadow:{SHADOW};'>",
            unsafe_allow_html=True,
        )
        if complaints:
            df  = pd.DataFrame(complaints)
            pc  = df["priority"].value_counts().reset_index()
            pc.columns = ["priority", "count"]
            fig = px.pie(
                pc, names="priority", values="count",
                title="Complaints by Priority",
                color="priority",
                color_discrete_map={"High": "#e53935", "Medium": "#fb8c00", "Low": "#43a047"},
            )
            _lc(fig)
            fig.update_traces(textfont_color="#163a2f")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No complaints yet.")
        st.markdown("</div>", unsafe_allow_html=True)

    with cr:
        st.markdown(
            f"<div style='background:{CARD};border:1px solid {B};border-radius:14px;"
            f"padding:1rem 1.2rem 0.5rem;box-shadow:{SHADOW};'>",
            unsafe_allow_html=True,
        )
        if adoption_trend:
            df2  = pd.DataFrame(adoption_trend).sort_values("adoption_count", ascending=True)
            fig2 = px.bar(
                df2, x="adoption_count", y="name", orientation="h",
                title="Top Schemes by Adoption",
                color="adoption_count",
                color_continuous_scale=[[0, "#c8e6c9"], [0.5, "#66bb6a"], [1, "#1b5e20"]],
                labels={"adoption_count": "Adoptions", "name": ""},
            )
            _lc(fig2)
            fig2.update_layout(
                yaxis=dict(tickfont=dict(size=10, color=M)),
                coloraxis_colorbar=dict(
                    tickfont=dict(color=M),
                    title=dict(text="Adoptions", font=dict(color=M)),
                ),
            )
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("No scheme data yet.")
        st.markdown("</div>", unsafe_allow_html=True)

    # ── Charts row 2 ─────────────────────────────────────────────────────────
    cl2, cr2 = st.columns(2)

    with cl2:
        st.markdown(
            f"<div style='background:{CARD};border:1px solid {B};border-radius:14px;"
            f"padding:1rem 1.2rem 0.5rem;box-shadow:{SHADOW};'>",
            unsafe_allow_html=True,
        )
        if complaints:
            df   = pd.DataFrame(complaints)
            sc   = df["status"].value_counts().reset_index()
            sc.columns = ["status", "count"]
            fig3 = px.bar(
                sc, x="status", y="count",
                title="Complaints by Status",
                color="count",
                color_continuous_scale=[[0, "#c8e6c9"], [0.5, "#43a047"], [1, "#1b5e20"]],
            )
            _lc(fig3)
            fig3.update_layout(coloraxis_showscale=False)
            st.plotly_chart(fig3, use_container_width=True)
        else:
            st.info("No complaints yet.")
        st.markdown("</div>", unsafe_allow_html=True)

    with cr2:
        st.markdown(
            f"""
            <div style='background:{CARD};border:1px solid {B};border-radius:14px;
                padding:1.6rem 1.8rem;box-shadow:{SHADOW};'>
                <div style='font-size:1rem;font-weight:700;color:{G};margin-bottom:1.4rem;'>
                    ⚡ Quick Stats
                </div>
                <div style='display:grid;grid-template-columns:1fr 1fr;gap:1.2rem;'>
                    <div style='background:{BG2};border:1px solid {B};border-radius:10px;padding:1rem;'>
                        <div style='font-size:0.72rem;color:{M};font-weight:600;
                            text-transform:uppercase;letter-spacing:0.5px;'>Resolution Rate</div>
                        <div style='font-size:1.8rem;font-weight:700;color:{G};margin-top:0.25rem;'>
                            {resolution_rate}%</div>
                    </div>
                    <div style='background:#fff5f5;border:1px solid #ffcdd2;border-radius:10px;padding:1rem;'>
                        <div style='font-size:0.72rem;color:#c62828;font-weight:600;
                            text-transform:uppercase;letter-spacing:0.5px;'>High Priority</div>
                        <div style='font-size:1.8rem;font-weight:700;color:#e53935;margin-top:0.25rem;'>
                            {stats.get("high_priority", 0)}</div>
                    </div>
                    <div style='background:#fff8f0;border:1px solid #ffe0b2;border-radius:10px;padding:1rem;'>
                        <div style='font-size:0.72rem;color:#e65100;font-weight:600;
                            text-transform:uppercase;letter-spacing:0.5px;'>Total Schemes</div>
                        <div style='font-size:1.8rem;font-weight:700;color:#e65100;margin-top:0.25rem;'>
                            {stats["total_schemes"]}</div>
                    </div>
                    <div style='background:#e8f4fd;border:1px solid #bbdefb;border-radius:10px;padding:1rem;'>
                        <div style='font-size:0.72rem;color:#1565c0;font-weight:600;
                            text-transform:uppercase;letter-spacing:0.5px;'>Avg Adoptions/Scheme</div>
                        <div style='font-size:1.8rem;font-weight:700;color:#1565c0;margin-top:0.25rem;'>
                            {avg_adopt:,}</div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


# ── Complaints Management ──────────────────────────────────────────────────────

def _show_complaints_mgmt(admin, lang):
    _title(f"📋 {t('complaint_management', lang)}")
    complaints = get_all_complaints()
    if not complaints:
        st.info(t("no_complaints_yet", lang))
        return

    sv = [t("all", lang), t("submitted", lang), t("in_progress", lang), t("resolved_status", lang)]
    pv = [t("all", lang), t("high", lang), t("medium", lang), t("low", lang)]

    st.markdown(
        f"<div style='background:{BG2};border:1px solid {B};border-radius:12px;"
        f"padding:1rem 1.2rem;margin-bottom:1rem;'>",
        unsafe_allow_html=True,
    )
    c1, c2, c3 = st.columns(3)
    with c1: fs = st.selectbox(t("filter_by_status", lang), sv)
    with c2: fp = st.selectbox(t("filter_by_priority", lang), pv)
    with c3:
        states = sorted(set(c["state"] for c in complaints if c["state"]))
        fst = st.selectbox(t("filter_by_state", lang), [t("all", lang)] + states)
    st.markdown("</div>", unsafe_allow_html=True)

    sr = {t("submitted", lang): "Submitted", t("in_progress", lang): "In Progress",
          t("resolved_status", lang): "Resolved", t("all", lang): "All"}
    pr = {t("high", lang): "High", t("medium", lang): "Medium",
          t("low", lang): "Low", t("all", lang): "All"}

    filtered = [
        c for c in complaints
        if (sr[fs] == "All" or c["status"] == sr[fs])
        and (pr[fp] == "All" or c["priority"] == pr[fp])
        and (fst == t("all", lang) or c["state"] == fst)
    ]

    st.markdown(
        f"<div style='color:{M};margin-bottom:1rem;font-size:0.9rem;'>"
        f"{t('showing_count_complaints', lang)} "
        f"<b style='color:{G};'>{len(filtered)}</b> "
        f"{t('complaints_label', lang)}</div>",
        unsafe_allow_html=True,
    )

    pc = {"High": "#e53935", "Medium": "#fb8c00", "Low": "#43a047"}
    pb = {"High": "#fff5f5", "Medium": "#fff8f0", "Low": "#f1fdf2"}
    si = {"Submitted": "📨", "In Progress": "⚙️", "Resolved": "✅"}

    for c in filtered:
        pcolor = pc.get(c["priority"], "#43a047")
        pbg    = pb.get(c["priority"], "#f1fdf2")
        sicon  = si.get(c["status"], "📨")
        with st.expander(
            f"{sicon} [{localize_priority(c['priority'], lang)}] "
            f"{c['complaint_id']} — {c['title'][:55]}"
        ):
            cc1, cc2 = st.columns([2, 1])
            with cc1:
                st.markdown(
                    f"**{get_text('farmer')}:** {c['farmer_name']}  |  "
                    f"**{get_text('state')}:** {c['state']}  |  "
                    f"**{get_text('district')}:** {c['district']}"
                )
                st.markdown(f"**{get_text('complaint_desc')}:** {c['description']}")
                st.markdown(
                    f"**{t('filed', lang)}:** {c['created_at'][:16]}  |  "
                    f"**{t('updated', lang)}:** {c['updated_at'][:16]}"
                )
                if c.get("image_path") and os.path.exists(c["image_path"]):
                    st.image(c["image_path"], width=300)
            with cc2:
                st.markdown(
                    f"<div style='background:{pbg};border:1px solid {pcolor}55;"
                    f"border-radius:10px;padding:1rem;text-align:center;margin-bottom:0.8rem;'>"
                    f"<div style='color:{pcolor};font-weight:700;font-size:1.05rem;'>"
                    f"{localize_priority(c['priority'], lang)}</div>"
                    f"<div style='color:{M};font-size:0.75rem;margin-top:0.2rem;'>"
                    f"{t('ai_priority', lang)}</div></div>",
                    unsafe_allow_html=True,
                )
                sopts = ["Submitted", "In Progress", "Resolved"]
                ns = st.selectbox(
                    get_text("update_status"),
                    [localize_status(x, lang) for x in sopts],
                    index=sopts.index(c["status"]),
                    key=f"status_{c['complaint_id']}",
                )
                rs = {localize_status(x, lang): x for x in sopts}
                nd = st.selectbox(
                    t("reassign_dept", lang), DEPARTMENTS,
                    index=DEPARTMENTS.index(c["department"]) if c["department"] in DEPARTMENTS else 0,
                    key=f"dept_{c['complaint_id']}",
                )
                if st.button(
                    f"💾 {get_text('update_status')}",
                    key=f"upd_{c['complaint_id']}",
                    use_container_width=True,
                ):
                    update_complaint_status(c["complaint_id"], rs[ns], nd)
                    log_admin_action(admin["username"], "UPDATE_COMPLAINT",
                                     f"{c['complaint_id']} -> {rs[ns]}")
                    st.success(f"✅ {t('updated_success', lang)}")
                    st.rerun()


# ── Schemes Management ─────────────────────────────────────────────────────────

def _show_schemes_mgmt(admin, lang):
    _title(t("scheme_management", lang))
    tab1, tab2 = st.tabs([
        t("view_manage", lang),
        t("add_new_scheme_tab", lang),
    ])

    with tab1:
        for s in get_all_schemes():
            display_name = localize_scheme_text(s["name"], lang)
            display_desc = localize_scheme_text(s["description"], lang)
            display_benefits = localize_scheme_text(s["benefits"], lang)
            display_dept = localize_department(s["department"], lang)

            title = f"{display_name} - {s['adoption_count']:,} {t('adoptions', lang)} | Rating {s['rating']}"
            st.markdown(
                f"<div style='background:{CARD}; border:1px solid {B}; border-radius:12px; padding:0.7rem 1rem; margin:0.6rem 0; font-weight:600; color:{DG};'>{title}</div>",
                unsafe_allow_html=True,
            )

            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"**{get_text('description')}:** {display_desc}")
                st.markdown(f"**{get_text('benefits')}:** {display_benefits}")
                st.markdown(f"**{get_text('department')}:** {display_dept}")
                st.markdown(
                    f"**{t('eligible_states_label', lang)}:** {s['eligible_states']} | "
                    f"**{t('eligible_crops_label', lang)}:** {s['eligible_crops']} | "
                    f"**{get_text('farmer_category')}:** {s['eligible_categories']}"
                )

            with col2:
                if st.button(get_text("delete_scheme"), key=f"del_{s['id']}", use_container_width=True):
                    delete_scheme(s["id"])
                    log_admin_action(admin["username"], "DELETE_SCHEME", s["name"])
                    st.success(t("deleted", lang))
                    st.rerun()

            with st.form(f"edit_{s['id']}"):
                st.markdown(
                    f"<div style='font-size:0.9rem;font-weight:600;color:{G};margin-bottom:0.7rem;'>Edit Scheme</div>",
                    unsafe_allow_html=True,
                )
                ec1, ec2 = st.columns(2)
                with ec1:
                    en = st.text_input(t("name_label", lang), value=s["name"])
                    ed = st.text_area(get_text("description"), value=s["description"], height=80)
                    eb = st.text_area(t("benefits_label", lang), value=s["benefits"], height=80)
                with ec2:
                    est = st.text_input(t("eligible_states_label", lang), value=s["eligible_states"])
                    ec = st.text_input(t("eligible_crops_label", lang), value=s["eligible_crops"])
                    eca = st.text_input(get_text("eligible_categories"), value=s["eligible_categories"])
                    edp = st.text_input(get_text("department"), value=s["department"])
                if st.form_submit_button(t("save_changes", lang), use_container_width=True):
                    update_scheme(
                        s["id"],
                        {
                            "name": en,
                            "description": ed,
                            "benefits": eb,
                            "eligible_states": est,
                            "eligible_crops": ec,
                            "eligible_categories": eca,
                            "department": edp,
                        },
                    )
                    log_admin_action(admin["username"], "EDIT_SCHEME", en)
                    st.success(t("scheme_updated", lang))
                    st.rerun()

    with tab2:
        st.markdown(
            f"<div style='background:{BG2};border:1px solid {B};border-radius:12px;"
            f"padding:1rem 1.2rem;margin-bottom:1rem;font-size:0.9rem;color:{M};'>"
            f"{t('add_new_govt_scheme', lang)}</div>",
            unsafe_allow_html=True,
        )
        with st.form("add_scheme"):
            ac1, ac2 = st.columns(2)
            with ac1:
                name = st.text_input(get_text("scheme_name"))
                desc = st.text_area(get_text("description"), height=100)
                bens = st.text_area(get_text("benefits"), height=100)
            with ac2:
                asts = st.text_input(get_text("eligible_states"), value="All")
                acr = st.text_input(get_text("eligible_crops"), value="All")
                acat = st.text_input(get_text("eligible_categories"), value="All")
                adpt = st.selectbox(get_text("department"), DEPARTMENTS)
            if st.form_submit_button(get_text("save_scheme"), use_container_width=True):
                if not (name and desc and bens):
                    st.warning(t("fill_required_fields", lang))
                else:
                    add_scheme(
                        {
                            "name": name,
                            "description": desc,
                            "benefits": bens,
                            "eligible_states": asts,
                            "eligible_crops": acr,
                            "eligible_categories": acat,
                            "department": adpt,
                        }
                    )
                    log_admin_action(admin["username"], "ADD_SCHEME", name)
                    st.success(f"{name} - {t('scheme_added_success', lang)}")
                    st.rerun()

def _show_maps(lang):
    _title(f"🗺️ {t('map_dashboard', lang)}")
    complaints = get_all_complaints()
    farmers    = get_all_farmers()

    map_opts = [
        f"🔴 {t('complaint_heatmap', lang)}",
        f"💧 {t('water_scarcity_zones', lang)}",
        f"🏛️ {t('scheme_adoption_heatmap', lang)}",
    ]
    mt = st.radio(t("select_map_view", lang), map_opts, horizontal=True)

    m = folium.Map(location=[20.59, 78.96], zoom_start=5, tiles="CartoDB positron")

    if mt == map_opts[0] and complaints:
        sc = {}
        for c in complaints:
            if c["state"]:
                sc[c["state"]] = sc.get(c["state"], 0) + 1
        for state, count in sc.items():
            co = STATE_COORDS.get(state)
            if not co:
                continue
            color = "#e53935" if count > 5 else "#fb8c00" if count > 2 else "#43a047"
            folium.CircleMarker(
                co, radius=min(count * 8 + 10, 50),
                color=color, fill=True, fill_opacity=0.7,
                popup=folium.Popup(f"<b>{state}</b><br>Complaints: {count}", max_width=200),
            ).add_to(m)

    elif mt == map_opts[1]:
        ws = {
            "Rajasthan": t("high_scarcity", lang),
            "Gujarat": t("medium_scarcity", lang),
            "Maharashtra": t("medium_scarcity", lang),
            "Andhra Pradesh": t("low_scarcity", lang),
            "Karnataka": t("medium_scarcity", lang),
        }
        cm = {
            t("high_scarcity", lang): "#e53935",
            t("medium_scarcity", lang): "#fb8c00",
            t("low_scarcity", lang): "#1565c0",
        }
        for state, level in ws.items():
            co = STATE_COORDS.get(state)
            if co:
                folium.CircleMarker(
                    co, radius=20, color=cm[level], fill=True, fill_opacity=0.6,
                    popup=folium.Popup(f"<b>{state}</b><br>{level}", max_width=200),
                ).add_to(m)

    elif mt == map_opts[2] and farmers:
        sf = {}
        for f in farmers:
            if f["state"]:
                sf[f["state"]] = sf.get(f["state"], 0) + 1
        for state, count in sf.items():
            co = STATE_COORDS.get(state)
            if co:
                folium.CircleMarker(
                    co, radius=min(count * 10 + 8, 40),
                    color="#43a047", fill=True, fill_opacity=0.6,
                    popup=folium.Popup(f"<b>{state}</b><br>Farmers: {count}", max_width=200),
                ).add_to(m)

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

