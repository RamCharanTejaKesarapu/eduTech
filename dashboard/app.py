"""
dashboard/app.py
Main Entrypoint for Student Retention & Welfare Efficacy Tracker BI Dashboard.
TransOrg Datathon - Track 4: Education & EdTech.
"""

import os
import sys
import streamlit as st
import plotly.express as px
import pandas as pd

# Set page config
st.set_page_config(
    page_title="Student Retention & Welfare Efficacy Tracker",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load CSS
css_path = os.path.join(os.path.dirname(__file__), "styles.css")
if os.path.exists(css_path):
    with open(css_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

from components.data_loader import (
    load_district_summary,
    load_school_risk_marts,
    load_dim_school
)
from components.kpi_cards import render_kpi_card, render_page_header
from components.filters import render_sidebar_filters

from components.theme import (
    apply_editorial_theme, INK, PAPER_CARD, HAIRLINE, EARTH, BRASS, VERMILION, MOSS
)
from components.top_nav import render_top_masthead

# Top Masthead & Navigation Buttons
render_top_masthead(active_page="Overview")

# Load data
try:
    df_district = load_district_summary()
    df_schools = load_school_risk_marts()
except Exception as e:
    st.error(f"Error loading analytical data marts: {e}")
    st.stop()

# Header
render_page_header(
    title="State Overview & Retention Scorecard",
    subtitle="State Education Department Analytics & AI Decision Support Platform",
    badge="Government of Punjab • Department of School Education"
)

# Sidebar filters
filtered_schools, active_filters = render_sidebar_filters(df_schools)

# Compute dynamic state KPIs
total_schools = len(filtered_schools)
total_students = int(filtered_schools['total_enrolled_students'].sum())
avg_att_rate = float(filtered_schools['avg_attendance_rate_pct'].mean())
avg_fln_score = float(filtered_schools['avg_fln_score_pct'].mean())
avg_infra_score = float(filtered_schools['avg_infra_score'].mean())
proxy_fraud_count = int(filtered_schools['proxy_fraud_count'].sum())
total_mdm_spend = float(filtered_schools['total_mdm_cost_inr'].sum())
critical_risk_schools = int((filtered_schools['srdri_risk_level'] == 'Critical Risk').sum())
high_risk_schools = int((filtered_schools['srdri_risk_level'] == 'High Risk').sum())

# KPI Cards Row
st.markdown("### State Executive Scorecard")
col1, col2, col3, col4, col5, col6 = st.columns(6)

with col1:
    render_kpi_card("Total Schools", f"{total_schools:,}", "Inspected Institutions")
with col2:
    render_kpi_card("Total Students", f"{total_students:,}", "Active Enrollment")
with col3:
    render_kpi_card("Avg Attendance", f"{avg_att_rate:.1f}%", "Verified Weekday Log")
with col4:
    render_kpi_card("Proxy Fraud Cases", f"{proxy_fraud_count:,}", "Sunday 100% Anomalies", is_positive=False)
with col5:
    render_kpi_card("State FLN Score", f"{avg_fln_score:.1f}%", "Standardized Proficiency")
with col6:
    render_kpi_card("Total MDM Spend", f"₹{total_mdm_spend/1e6:.2f}M", "Grain Procurement Budget")

# Critical Alerts Banner
st.markdown("""
<div class="alert-box-warning">
    <b>⚠️ Executive Action Alerts:</b><br>
    • <b>Proxy Attendance Anomaly:</b> High incidence of 100% attendance recorded on Sundays in <b>Ferozepur</b> and <b>Ludhiana</b>.<br>
    • <b>Student Retention Vulnerability:</b> <b>{}</b> schools identified in <b>Critical Risk</b> status requiring immediate welfare and pedagogical intervention.
</div>
""".format(critical_risk_schools), unsafe_allow_html=True)

# Main Visualizations Row
col_left, col_right = st.columns([3, 2])

with col_left:
    st.markdown("#### District Performance & Retention Efficacy")
    # Horizontal Bar of Average Attendance and FLN Scores
    df_dist_summary = filtered_schools.groupby('district').agg(
        avg_att=('avg_attendance_rate_pct', 'mean'),
        avg_fln=('avg_fln_score_pct', 'mean'),
        total_students=('total_enrolled_students', 'sum'),
        critical_count=('srdri_risk_level', lambda x: (x == 'Critical Risk').sum())
    ).reset_index().sort_values('avg_att', ascending=True)

    fig_dist = px.bar(
        df_dist_summary,
        y='district',
        x='avg_att',
        orientation='h',
        text_auto='.1f',
        color='avg_fln',
        color_continuous_scale=['#d6c4a8', '#2b2721'],
        labels={'avg_att': 'Average Attendance (%)', 'district': 'District', 'avg_fln': 'FLN Score (%)'}
    )
    fig_dist = apply_editorial_theme(fig_dist)
    fig_dist.update_layout(
        margin={'l': 20, 'r': 20, 't': 20, 'b': 20},
        coloraxis_colorbar={'title': 'FLN %', 'tickfont': {'family': "'Newsreader', serif", 'color': INK}}
    )
    st.plotly_chart(fig_dist, use_container_width=True)

with col_right:
    st.markdown("#### School Risk Tier Distribution (SRDRI)")
    risk_counts = filtered_schools['srdri_risk_level'].value_counts().reset_index()
    risk_counts.columns = ['Risk Tier', 'Count']
    color_map = {
        'Critical Risk': VERMILION,
        'High Risk': EARTH,
        'Medium Risk': BRASS,
        'Low Risk': MOSS
    }
    fig_donut = px.pie(
        risk_counts,
        names='Risk Tier',
        values='Count',
        hole=0.55,
        color='Risk Tier',
        color_discrete_map=color_map
    )
    fig_donut = apply_editorial_theme(fig_donut)
    fig_donut.update_layout(
        margin={'l': 20, 'r': 20, 't': 20, 'b': 20},
        legend={'orientation': 'h', 'y': -0.15, 'font': {'family': "'Newsreader', serif"}}
    )
    st.plotly_chart(fig_donut, use_container_width=True)

# District Scorecard Table
st.markdown("### 📋 District Benchmarking Scorecard")
st.dataframe(
    df_district,
    column_config={
        "district": "District",
        "total_schools": st.column_config.NumberColumn("Schools", format="%d"),
        "total_enrolled_students": st.column_config.NumberColumn("Students", format="%,d"),
        "avg_attendance_rate_pct": st.column_config.ProgressColumn("Avg Attendance %", min_value=0, max_value=100, format="%.1f%%"),
        "avg_proxy_fraud_rate_pct": st.column_config.NumberColumn("Proxy Fraud %", format="%.2f%%"),
        "avg_fln_score_pct": st.column_config.ProgressColumn("FLN Score %", min_value=0, max_value=100, format="%.1f%%"),
        "avg_infra_score": st.column_config.NumberColumn("Infra Score", format="%.1f"),
        "total_mdm_spend_inr": st.column_config.NumberColumn("Total Spend (₹)", format="₹%,.0f"),
        "vulnerable_schools_count": st.column_config.NumberColumn("Vulnerable Schools", format="%d"),
        "avg_retention_proxy_pct": st.column_config.ProgressColumn("Retention Proxy", min_value=0, max_value=100, format="%.1f%%")
    },
    hide_index=True,
    use_container_width=True
)

st.markdown("---")
st.info("💡 **Navigation Guide:** Use the left sidebar to navigate across all 8 dedicated analytical modules: **Student Retention**, **Attendance & Academics**, **Mid-Day Meal**, **Infrastructure**, **School Comparison**, **Data Quality**, and the **AI Analyst**.")
