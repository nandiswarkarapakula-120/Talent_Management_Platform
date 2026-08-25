"""
TalentSphere Elevate - UI Helper Components
Reusable rendering functions used across all dashboards.
"""

import streamlit as st
import os


def load_css():
    css_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "style.css")
    with open(css_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


def hero(title, subtitle, emoji="🚀"):
    st.markdown(f"""
    <div class="ts-hero">
        <h1>{emoji} {title}</h1>
        <p>{subtitle}</p>
    </div>
    """, unsafe_allow_html=True)


def section_title(text):
    st.markdown(f'<div class="section-title">{text}</div>', unsafe_allow_html=True)


def kpi_card(icon, value, label, col=None):
    target = col if col else st
    target.markdown(f"""
    <div class="kpi-card">
        <span class="kpi-icon">{icon}</span>
        <p class="kpi-value">{value}</p>
        <p class="kpi-label">{label}</p>
    </div>
    """, unsafe_allow_html=True)


def glass_card_open():
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)


def glass_card_close():
    st.markdown('</div>', unsafe_allow_html=True)


def badge(text, kind="info"):
    return f'<span class="badge badge-{kind}">{text}</span>'


def module_card_html(icon, title, desc):
    return f"""
    <div class="module-card">
        <span class="module-icon">{icon}</span>
        <div class="module-title">{title}</div>
        <div class="module-desc">{desc}</div>
    </div>
    """


def render_module_grid(modules, cols=4, key_prefix="mod"):
    """modules: list of dicts {icon, title, desc, key}"""
    rows = [modules[i:i + cols] for i in range(0, len(modules), cols)]
    for row in rows:
        columns = st.columns(len(row))
        for col, m in zip(columns, row):
            with col:
                st.markdown(module_card_html(m["icon"], m["title"], m["desc"]), unsafe_allow_html=True)
                if st.button("Open →", key=f"{key_prefix}_{m['key']}", use_container_width=True):
                    st.session_state.active_module = m["key"]
                    st.rerun()
