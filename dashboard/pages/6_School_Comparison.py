"""
dashboard/pages/6_School_Comparison.py
Comparative benchmarking tool: side-by-side analysis of any two districts or schools.
"""

import os
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

# Load CSS
css_path = os.path.join(os.path.dirname(__file__), "..", "styles.css")
if os.path.exists(css_path):
    with open(css_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

from components.data_loader import load_district_summary, load_school_risk_marts
from components.kpi_cards import render_page_header
from components.top_nav import render_top_masthead

render_top_masthead("Compare")

render_page_header(
    title="School & District Comparison",
    subtitle="Side-by-Side Comparative Benchmarking Across Core Welfare & Academic Metrics",
    badge="Comparative Analytics"
)

df_districts = load_district_summary()
df_schools = load_school_risk_marts()

tab1, tab2 = st.tabs(["🏛️ District vs District Benchmarking", "🏫 School vs School Benchmarking"])

# TAB 1: DISTRICT COMPARISON
with tab1:
    st.markdown("### Select Two Districts to Benchmark")
    d_list = sorted(df_districts['district'].dropna().unique().tolist())

    col_d1, col_d2 = st.columns(2)
    with col_d1:
        d1 = st.selectbox("Select District A", options=d_list, index=0)
    with col_d2:
        d2 = st.selectbox("Select District B", options=d_list, index=min(1, len(d_list)-1))

    if d1 and d2:
        r1 = df_districts[df_districts['district'] == d1].iloc[0]
        r2 = df_districts[df_districts['district'] == d2].iloc[0]

        comp_metrics = [
            {"Metric": "Total Schools", "District A": f"{r1['total_schools']:,}", "District B": f"{r2['total_schools']:,}"},
            {"Metric": "Enrolled Students", "District A": f"{r1['total_enrolled_students']:,}", "District B": f"{r2['total_enrolled_students']:,}"},
            {"Metric": "Average Attendance Rate (%)", "District A": f"{r1['avg_attendance_rate_pct']:.1f}%", "District B": f"{r2['avg_attendance_rate_pct']:.1f}%"},
            {"Metric": "Proxy Fraud Rate (%)", "District A": f"{r1['avg_proxy_fraud_rate_pct']:.2f}%", "District B": f"{r2['avg_proxy_fraud_rate_pct']:.2f}%"},
            {"Metric": "FLN Academic Score (%)", "District A": f"{r1['avg_fln_score_pct']:.1f}%", "District B": f"{r2['avg_fln_score_pct']:.1f}%"},
            {"Metric": "Infrastructure Quality Score", "District A": f"{r1['avg_infra_score']:.1f}/100", "District B": f"{r2['avg_infra_score']:.1f}/100"},
            {"Metric": "Total MDM Spend (INR)", "District A": f"₹{r1['total_mdm_spend_inr']:,.0f}", "District B": f"₹{r2['total_mdm_spend_inr']:,.0f}"},
            {"Metric": "Vulnerable Schools Count", "District A": f"{r1['vulnerable_schools_count']}", "District B": f"{r2['vulnerable_schools_count']}"},
            {"Metric": "Retention Proxy Rate (%)", "District A": f"{r1['avg_retention_proxy_pct']:.1f}%", "District B": f"{r2['avg_retention_proxy_pct']:.1f}%"},
        ]

        st.markdown(f"#### Comparative Matrix: **{d1}** vs **{d2}**")
        comp_df = pd.DataFrame(comp_metrics)
        comp_df.columns = ["Performance Dimension", d1, d2]
        st.dataframe(comp_df, hide_index=True, use_container_width=True)

        # Radar Comparison
        categories = ['Attendance %', 'FLN Score %', 'Infra Score', 'Retention %']
        vals_d1 = [r1['avg_attendance_rate_pct'], r1['avg_fln_score_pct'], r1['avg_infra_score'], r1['avg_retention_proxy_pct']]
        vals_d2 = [r2['avg_attendance_rate_pct'], r2['avg_fln_score_pct'], r2['avg_infra_score'], r2['avg_retention_proxy_pct']]

        fig_radar = go.Figure()
        fig_radar.add_trace(go.Scatterpolar(r=vals_d1, theta=categories, fill='toself', name=d1, line_color='#1E3A8A'))
        fig_radar.add_trace(go.Scatterpolar(r=vals_d2, theta=categories, fill='toself', name=d2, line_color='#0D9488'))
        fig_radar.update_layout(
            polar={'radialaxis': {'visible': True, 'range': [0, 100]}},
            showlegend=True,
            paper_bgcolor='#F8FAFC'
        )
        st.plotly_chart(fig_radar, use_container_width=True)

# TAB 2: SCHOOL COMPARISON
with tab2:
    st.markdown("### Select Two Schools to Benchmark")
    df_schools['selector'] = df_schools['school_id'] + " - " + df_schools['school_name'] + " (" + df_schools['district'] + ")"
    s_list = df_schools['selector'].tolist()

    col_s1, col_s2 = st.columns(2)
    with col_s1:
        s1 = st.selectbox("Select School A", options=s_list, index=0)
    with col_s2:
        s2 = st.selectbox("Select School B", options=s_list, index=min(1, len(s_list)-1))

    if s1 and s2:
        s1_id = s1.split(" - ")[0]
        s2_id = s2.split(" - ")[0]
        sr1 = df_schools[df_schools['school_id'] == s1_id].iloc[0]
        sr2 = df_schools[df_schools['school_id'] == s2_id].iloc[0]

        school_metrics = [
            {"Dimension": "District", sr1['school_name']: sr1['district'], sr2['school_name']: sr2['district']},
            {"Dimension": "Category & Medium", sr1['school_name']: f"{sr1['school_type']} ({sr1['medium']})", sr2['school_name']: f"{sr2['school_type']} ({sr2['medium']})"},
            {"Dimension": "Enrolled Students", sr1['school_name']: f"{sr1['total_enrolled_students']:,}", sr2['school_name']: f"{sr2['total_enrolled_students']:,}"},
            {"Dimension": "Clean Attendance Rate (%)", sr1['school_name']: f"{sr1['avg_attendance_rate_pct']:.1f}%", sr2['school_name']: f"{sr2['avg_attendance_rate_pct']:.1f}%"},
            {"Dimension": "Proxy Fraud Rate (%)", sr1['school_name']: f"{sr1['proxy_fraud_rate_pct']:.1f}%", sr2['school_name']: f"{sr2['proxy_fraud_rate_pct']:.1f}%"},
            {"Dimension": "FLN Academic Score (%)", sr1['school_name']: f"{sr1['avg_fln_score_pct']:.1f}%", sr2['school_name']: f"{sr2['avg_fln_score_pct']:.1f}%"},
            {"Dimension": "Infrastructure Score (0-100)", sr1['school_name']: f"{sr1['avg_infra_score']:.1f}", sr2['school_name']: f"{sr2['avg_infra_score']:.1f}"},
            {"Dimension": "MDM Grain / Student (KG)", sr1['school_name']: f"{sr1['kg_grain_per_student']:.2f} kg", sr2['school_name']: f"{sr2['kg_grain_per_student']:.2f} kg"},
            {"Dimension": "Retention Risk Score (SRDRI)", sr1['school_name']: f"{sr1['srdri_score']:.1f} ({sr1['srdri_risk_level']})", sr2['school_name']: f"{sr2['srdri_score']:.1f} ({sr2['srdri_risk_level']})"},
            {"Dimension": "Retention Efficacy Proxy", sr1['school_name']: f"{sr1['retention_proxy_pct']:.1f}%", sr2['school_name']: f"{sr2['retention_proxy_pct']:.1f}%"},
        ]

        st.markdown("#### Side-by-Side School Diagnostic Matrix")
        s_comp_df = pd.DataFrame(school_metrics)
        st.dataframe(s_comp_df, hide_index=True, use_container_width=True)
