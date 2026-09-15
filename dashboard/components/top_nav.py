"""
dashboard/components/top_nav.py
Editorial Top Masthead & Navigation System.
Implements the Meng To Sketchbook aesthetic (Instrument Serif, Newsreader, Warm Paper & Charcoal Ink)
and utilizes top space for project branding, live intelligence status, and one-click navigation buttons.
"""

import streamlit as st

def render_top_masthead(active_page: str = "Home"):
    """
    Renders an editorial top navigation bar and project masthead
    that eliminates wasted top spacing and unifies navigation across all pages.
    """
    st.markdown("""
    <div class="editorial-top-masthead">
        <div class="top-meta-row">
            <span class="top-kicker">State Education Department • Government of Punjab</span>
            <span class="top-live-badge">🟢 600 Schools Audited • 20,000 Records • Real-Time Warehouse</span>
        </div>
        <div class="top-title-row">
            <h1 class="top-project-title">Student Retention & Welfare Efficacy Tracker</h1>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Fast Navigation Bar using Streamlit's native st.page_link
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
