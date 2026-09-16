"""
dashboard/pages/1_Executive_Overview.py
Executive Overview: State-level key performance metrics, district rankings, and executive KPIs.
"""

import os
import streamlit as st
import plotly.express as px
import pandas as pd

st.set_page_config(
    page_title="Executive Overview • EduTech",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load CSS
css_path = os.path.join(os.path.dirname(__file__), "..", "styles.css")
if os.path.exists(css_path):
    with open(css_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

from components.data_loader import load_district_summary, load_school_risk_marts
from components.kpi_cards import render_kpi_card, render_page_header
from components.filters import render_sidebar_filters
from components.theme import apply_editorial_theme, INK, EARTH, MOSS, VERMILION, BRASS
from components.top_nav import render_top_masthead
from components.creator_card import render_creator_card
from components.footer import render_editorial_footer

render_top_masthead("Executive")

render_page_header(
    title="Executive Overview",
    subtitle="Statewide Education Metrics, Infrastructure Quality & Welfare Distribution",
    badge="Executive Dashboard"
)

df_schools = load_school_risk_marts()
df_districts = load_district_summary()

filtered_schools, active_filters = render_sidebar_filters(df_schools)

# Top KPIs
col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    render_kpi_card("Total Schools", f"{len(filtered_schools):,}", "Inspected Institutions")
with col2:
    render_kpi_card("Total Students", f"{filtered_schools['total_enrolled_students'].sum():,}", "Active Enrolled")
with col3:
    render_kpi_card("Avg Attendance", f"{filtered_schools['avg_attendance_rate_pct'].mean():.1f}%", "Verified Logs")
with col4:
    render_kpi_card("FLN Test Score", f"{filtered_schools['avg_fln_score_pct'].mean():.1f}%", "Statewide Mean")
with col5:
    render_kpi_card("Infra Quality", f"{filtered_schools['avg_infra_score'].mean():.1f}/100", "Facility Index")

st.markdown("---")

# Visualizations Row 1
col_left, col_right = st.columns(2)

with col_left:
    st.markdown("#### District-wise Average Attendance & FLN Scores")
    dist_perf = filtered_schools.groupby('district').agg(
        attendance=('avg_attendance_rate_pct', 'mean'),
        fln=('avg_fln_score_pct', 'mean')
    ).reset_index().sort_values('attendance', ascending=False)

    fig_bar = px.bar(
        dist_perf,
        x='district',
        y=['attendance', 'fln'],
        barmode='group',
        labels={'value': 'Percentage (%)', 'variable': 'Metric', 'district': 'District'},
        color_discrete_sequence=[INK, EARTH],
        text_auto='.1f'
    )
    fig_bar = apply_editorial_theme(fig_bar)
    fig_bar.update_layout(
        legend={'title': '', 'orientation': 'h', 'y': 1.15, 'font': {'family': "'Newsreader', serif"}}
    )
    st.plotly_chart(fig_bar, use_container_width=True)

with col_right:
    st.markdown("#### Infrastructure Quality Score by District")
    dist_infra = filtered_schools.groupby('district')['avg_infra_score'].mean().reset_index().sort_values('avg_infra_score', ascending=True)
    fig_infra = px.bar(
        dist_infra,
        y='district',
        x='avg_infra_score',
        orientation='h',
        text_auto='.1f',
        color='avg_infra_score',
        color_continuous_scale=['#d6c4a8', '#9a6a3e'],
        labels={'avg_infra_score': 'Infra Score (0-100)', 'district': 'District'}
    )
    fig_infra = apply_editorial_theme(fig_infra)
    fig_infra.update_layout(coloraxis_showscale=False)
    st.plotly_chart(fig_infra, use_container_width=True)

# Visualizations Row 2
st.markdown("#### Correlation: Infrastructure Score vs Student Attendance Rate")
fig_scatter = px.scatter(
    filtered_schools,
    x='avg_infra_score',
    y='avg_attendance_rate_pct',
    color='district',
    size='total_enrolled_students',
    hover_name='school_name',
    labels={'avg_infra_score': 'Infrastructure Score (0-100)', 'avg_attendance_rate_pct': 'Attendance Rate (%)'}
)
fig_scatter = apply_editorial_theme(fig_scatter)
st.plotly_chart(fig_scatter, use_container_width=True)

# Export option
st.markdown("### 📥 Export Executive Summary")
csv_data = filtered_schools.to_csv(index=False).encode('utf-8')
st.download_button(
    label="Download Processed School Analytics CSV",
    data=csv_data,
    file_name="executive_schools_summary.csv",
    mime="text/csv"
)

# Render The Architect (Creator Profile) and Project Reference Mega-Footer
render_creator_card()
render_editorial_footer()

