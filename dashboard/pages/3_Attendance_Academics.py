"""
dashboard/pages/3_Attendance_Academics.py
Attendance patterns, proxy fraud forensics, and foundational literacy & numeracy (FLN) academic analysis.
"""

import os
import streamlit as st
import plotly.express as px
import pandas as pd

st.set_page_config(
    page_title="Attendance & Academics • EduTech",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load CSS
css_path = os.path.join(os.path.dirname(__file__), "..", "styles.css")
if os.path.exists(css_path):
    with open(css_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

from components.data_loader import (
    load_attendance_summary,
    load_fln_test_scores,
    load_school_risk_marts
)
from components.kpi_cards import render_kpi_card, render_page_header
from components.theme import apply_editorial_theme, INK, EARTH, BRASS, VERMILION, MOSS
from components.top_nav import render_top_masthead
from components.creator_card import render_creator_card
from components.footer import render_editorial_footer

render_top_masthead("Attendance")

render_page_header(
    title="Attendance Integrity & Academic FLN Performance",
    subtitle="Longitudinal Attendance Analysis, Proxy Fraud Forensics & FLN Competency Evaluation",
    badge="Welfare & Pedagogy Analytics"
)

df_att = load_attendance_summary()
df_fln = load_fln_test_scores()
df_schools = load_school_risk_marts()

# KPIs Row
col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    clean_mean_att = df_att[df_att['quality_status'] == 'VALID']['attendance_rate_capped'].mean() * 100
    render_kpi_card("Verified Attendance", f"{clean_mean_att:.1f}%", "Valid Weekday Average")
with col2:
    proxy_total = df_att['is_proxy_attendance'].sum()
    render_kpi_card("Proxy Fraud Cases", f"{proxy_total:,}", "Sunday 100% Attendance", is_positive=False)
with col3:
    overflow_total = df_att['is_attendance_overflow'].sum()
    render_kpi_card("Attendance Overflow", f"{overflow_total:,}", "Present > Total Enrolled", is_positive=False)
with col4:
    fln_mean = df_fln['score_percentage'].mean()
    render_kpi_card("Average FLN Score", f"{fln_mean:.1f}%", "Across All Assessments")
with col5:
    below_basic_pct = (df_fln['proficiency_tier'] == 'Below Basic (Level 1)').mean() * 100
    render_kpi_card("Below Basic Level", f"{below_basic_pct:.1f}%", "Immediate Remediation Needed", is_positive=False)

st.markdown("---")

# Section 1: Attendance Patterns & Anomaly Forensics
st.markdown("### 📅 Section 1: Attendance Trajectory & Day-of-Week Forensics")

col_a, col_b = st.columns(2)

with col_a:
    st.markdown("#### Monthly Attendance Rate Trend (2025 - 2026)")
    monthly_trend = df_att[df_att['quality_status'] == 'VALID'].groupby('month')['attendance_rate_capped'].mean().reset_index()
    monthly_trend['attendance_pct'] = (monthly_trend['attendance_rate_capped'] * 100.0).round(1)

    fig_trend = px.line(
        monthly_trend,
        x='month',
        y='attendance_pct',
        markers=True,
        labels={'month': 'Academic Month', 'attendance_pct': 'Average Attendance (%)'},
        color_discrete_sequence=[EARTH]
    )
    fig_trend = apply_editorial_theme(fig_trend)
    st.plotly_chart(fig_trend, use_container_width=True)

with col_b:
    st.markdown("#### Attendance Records by Day of Week")
    dow_counts = df_att.groupby('day_of_week').agg(
        total_records=('attendance_rate_capped', 'count'),
        proxy_fraud=('is_proxy_attendance', 'sum')
    ).reindex(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']).reset_index()

    fig_dow = px.bar(
        dow_counts,
        x='day_of_week',
        y=['total_records', 'proxy_fraud'],
        barmode='group',
        labels={'value': 'Record Count', 'day_of_week': 'Day of Week', 'variable': 'Category'},
        color_discrete_sequence=[INK, VERMILION]
    )
    fig_dow = apply_editorial_theme(fig_dow)
    fig_dow.update_layout(legend={'title': '', 'orientation': 'h', 'y': 1.15, 'font': {'family': "'Newsreader', serif"}})
    st.plotly_chart(fig_dow, use_container_width=True)

# Proxy Fraud Analysis
st.markdown("#### District Ranking: Proxy Attendance Fraud Rate")
dist_proxy = df_schools.groupby('district').agg(
    proxy_cases=('proxy_fraud_count', 'sum'),
    fraud_rate=('proxy_fraud_rate_pct', 'mean')
).reset_index().sort_values('fraud_rate', ascending=False)

fig_proxy = px.bar(
    dist_proxy,
    x='district',
    y='fraud_rate',
    text_auto='.1f',
    color='fraud_rate',
    color_continuous_scale=['#dfcbb0', '#b34f3e'],
    labels={'fraud_rate': 'Proxy Fraud Rate (%)', 'district': 'District'}
)
fig_proxy = apply_editorial_theme(fig_proxy)
fig_proxy.update_layout(coloraxis_showscale=False)
st.plotly_chart(fig_proxy, use_container_width=True)

st.markdown("---")

# Section 2: Academic FLN Performance
st.markdown("### 📚 Section 2: Foundational Literacy & Numeracy (FLN) Evaluation")

col_c, col_d = st.columns(2)

with col_c:
    st.markdown("#### Subject-Wise Average Performance (%)")
    subj_perf = df_fln.groupby('subject')['score_percentage'].agg(['mean', 'count']).reset_index().sort_values('mean', ascending=False)
    subj_perf['mean'] = subj_perf['mean'].round(1)

    fig_subj = px.bar(
        subj_perf,
        x='subject',
        y='mean',
        text_auto='.1f',
        color='subject',
        color_discrete_sequence=[INK, EARTH, BRASS, MOSS],
        labels={'mean': 'Average Score (%)', 'subject': 'Subject'}
    )
    fig_subj = apply_editorial_theme(fig_subj)
    fig_subj.update_layout(showlegend=False)
    st.plotly_chart(fig_subj, use_container_width=True)

with col_d:
    st.markdown("#### Student Proficiency Tier Distribution")
    prof_counts = df_fln['proficiency_tier'].value_counts().reindex(
        ['Distinction (Level 4)', 'Proficient (Level 3)', 'Basic (Level 2)', 'Below Basic (Level 1)']
    ).reset_index()
    prof_counts.columns = ['Proficiency Tier', 'Count']

    fig_prof = px.pie(
        prof_counts,
        names='Proficiency Tier',
        values='Count',
        hole=0.55,
        color='Proficiency Tier',
        color_discrete_map={
            'Distinction (Level 4)': MOSS,
            'Proficient (Level 3)': EARTH,
            'Basic (Level 2)': BRASS,
            'Below Basic (Level 1)': VERMILION
        }
    )
    fig_prof = apply_editorial_theme(fig_prof)
    fig_prof.update_layout(legend={'orientation': 'h', 'y': -0.15, 'font': {'family': "'Newsreader', serif"}})
    st.plotly_chart(fig_prof, use_container_width=True)

# Grade Level Analysis
st.markdown("#### FLN Score Trajectory Across Grade Levels (Grade 3 to Grade 8)")
grade_perf = df_fln.groupby(['grade', 'subject'])['score_percentage'].mean().reset_index()
grade_perf['grade'] = grade_perf['grade'].astype(str)
grade_perf = grade_perf.sort_values('grade')

fig_grade = px.bar(
    grade_perf,
    x='grade',
    y='score_percentage',
    color='subject',
    barmode='group',
    color_discrete_sequence=[INK, EARTH, BRASS, MOSS],
    labels={'grade': 'Grade Level', 'score_percentage': 'Average Score (%)', 'subject': 'Subject'}
)
fig_grade = apply_editorial_theme(fig_grade)
st.plotly_chart(fig_grade, use_container_width=True)

# Render The Architect (Creator Profile) and Project Reference Mega-Footer
render_creator_card()
render_editorial_footer()
