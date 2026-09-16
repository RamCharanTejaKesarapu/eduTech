"""
dashboard/components/top_nav.py
Editorial Top Masthead & Navigation System.
Implements the Meng To Sketchbook aesthetic (Instrument Serif, Newsreader, Warm Paper & Charcoal Ink)
with top project branding, live intelligence status, circular PFP icon button, and 9 fast page links.
"""

import os
import base64
import streamlit as st


def _get_pfp_base64() -> str:
    """Load and base64-encode the creator profile picture."""
    asset_path = os.path.join(os.path.dirname(__file__), "..", "assets", "creator_pfp.png")
    if os.path.exists(asset_path):
        with open(asset_path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    return ""


def render_top_masthead(active_page: str = "Home"):
    """
    Renders an editorial top navigation bar and project masthead
    that eliminates wasted top spacing and provides a circular PFP icon button.
    """
    pfp_b64 = _get_pfp_base64()
    pfp_img_tag = (
        f'<img src="data:image/png;base64,{pfp_b64}" alt="Architect" class="top-pfp-icon-img" />'
        if pfp_b64
        else '<span class="top-pfp-initials">RC</span>'
    )

    masthead_elements = [
        '<div class="editorial-top-masthead">',
        '<div class="top-meta-row">',
        '<span class="top-kicker">State Education Department • Government of Punjab</span>',
        '<div class="top-actions-cluster">',
        '<span class="top-live-badge">🟢 600 Schools Audited • 20,000 Records • Real-Time Warehouse</span>',
        f'<a href="#architect-section" class="top-pfp-icon-btn" title="The Architect: Ram Charan Teja">{pfp_img_tag}</a>',
        '</div>',
        '</div>',
        '<div class="top-title-row">',
        '<h1 class="top-project-title">Student Retention & Welfare Efficacy Tracker</h1>',
        '</div>',
        '</div>'
    ]
    st.markdown("".join(masthead_elements), unsafe_allow_html=True)

    # 9 wide navigation buttons across the page
    nav_cols = st.columns(9)
    with nav_cols[0]:
        st.page_link("app.py", label="Overview", icon="🏛️", use_container_width=True)
    with nav_cols[1]:
        st.page_link("pages/1_Executive_Overview.py", label="Executive", icon="📋", use_container_width=True)
    with nav_cols[2]:
        st.page_link("pages/2_Student_Retention.py", label="Retention", icon="🎯", use_container_width=True)
    with nav_cols[3]:
        st.page_link("pages/3_Attendance_Academics.py", label="Attendance", icon="📈", use_container_width=True)
    with nav_cols[4]:
        st.page_link("pages/4_Mid_Day_Meal.py", label="Meals", icon="🍲", use_container_width=True)
    with nav_cols[5]:
        st.page_link("pages/5_Infrastructure.py", label="Infra", icon="🏫", use_container_width=True)
    with nav_cols[6]:
        st.page_link("pages/6_School_Comparison.py", label="Compare", icon="⚖️", use_container_width=True)
    with nav_cols[7]:
        st.page_link("pages/7_Data_Quality.py", label="Quality", icon="🔍", use_container_width=True)
    with nav_cols[8]:
        st.page_link("pages/8_AI_Analyst.py", label="AI Agent", icon="🤖", use_container_width=True)

    st.markdown('<div class="editorial-nav-divider"></div>', unsafe_allow_html=True)
