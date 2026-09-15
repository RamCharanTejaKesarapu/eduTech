"""
dashboard/components/kpi_cards.py
Reusable HTML and CSS styled KPI cards for government BI dashboards.
"""

import streamlit as st

def render_kpi_card(title: str, value: str, subtitle: str = "", delta: str = None, is_positive: bool = True):
    delta_html = ""
    if delta:
        color = "#059669" if is_positive else "#DC2626"
        arrow = "▲" if is_positive else "▼"
        delta_html = f"<div style='font-size: 12px; color: {color}; font-weight: 600; margin-top: 4px;'>{arrow} {delta}</div>"

    html = f"""
    <div class="kpi-card">
        <div class="kpi-title">{title}</div>
        <div class="kpi-value">{value}</div>
        <div class="kpi-subtitle">{subtitle}</div>
        {delta_html}
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

def render_page_header(title: str, subtitle: str, badge: str = "Department of School Education"):
    html = f"""
    <div class="gov-header">
        <div class="gov-badge">{badge}</div>
        <h1>{title}</h1>
        <p>{subtitle}</p>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)
