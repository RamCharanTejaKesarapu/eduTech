"""
dashboard/pages/2_Student_Retention.py
Student Retention & Dropout Risk Indicator (SRDRI) analytical drilldown.
"""

import os
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

st.set_page_config(
    page_title="Student Retention • EduTech",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load CSS
css_path = os.path.join(os.path.dirname(__file__), "..", "styles.css")
if os.path.exists(css_path):
    with open(css_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

from components.data_loader import load_school_risk_marts
from components.kpi_cards import render_kpi_card, render_page_header
from components.filters import render_sidebar_filters
from components.theme import apply_editorial_theme, INK, EARTH, BRASS, VERMILION, MOSS
from components.top_nav import render_top_masthead
from components.creator_card import render_creator_card
from components.footer import render_editorial_footer

render_top_masthead("Retention")

render_page_header(
    title="Student Retention & Risk Analytics",
    subtitle="Multi-Factor Student Retention & Dropout Risk Indicator (SRDRI) Framework",
    badge="Retention & Early Warning System"
)

# Methodological Disclaimer
st.markdown("""
<div class="alert-box">
    <b>📖 Analytical Rigor & Methodology Notice:</b><br>
    The raw state datasets do not contain explicit individual dropout survey flags. In accordance with data integrity guidelines,
    we compute an objective, multi-factor <b>Student Retention & Dropout Risk Indicator (SRDRI)</b> based on:
    <b>Chronic Absenteeism (40%)</b>, <b>FLN Academic Deficits (30%)</b>, <b>Infrastructure Deprivation (15%)</b>, and <b>MDM Grain Irregularity (15%)</b>.
    This metric provides an actionable administrative early warning indicator, not a deterministic machine learning claim.
</div>
""", unsafe_allow_html=True)

df_schools = load_school_risk_marts()
filtered_schools, active_filters = render_sidebar_filters(df_schools)

# KPIs
critical_count = int((filtered_schools['srdri_risk_level'] == 'Critical Risk').sum())
high_count = int((filtered_schools['srdri_risk_level'] == 'High Risk').sum())
avg_risk_score = float(filtered_schools['srdri_score'].mean())
avg_retention_proxy = float(filtered_schools['retention_proxy_pct'].mean())

col1, col2, col3, col4 = st.columns(4)
with col1:
    render_kpi_card("Critical Risk Schools", f"{critical_count:,}", "Immediate Action Required", is_positive=False)
with col2:
    render_kpi_card("High Risk Schools", f"{high_count:,}", "Targeted Monitoring", is_positive=False)
with col3:
    render_kpi_card("Average Risk Score", f"{avg_risk_score:.1f}/100", "Statewide Mean SRDRI")
with col4:
    render_kpi_card("Retention Efficacy Proxy", f"{avg_retention_proxy:.1f}%", "Composite Retention Index")

st.markdown("---")

col_l, col_r = st.columns(2)

risk_palette = {
    'Critical Risk': VERMILION,
    'High Risk': EARTH,
    'Medium Risk': BRASS,
    'Low Risk': MOSS
}

with col_l:
    st.markdown("#### Distribution of School Risk Levels")
    risk_summary = filtered_schools['srdri_risk_level'].value_counts().reindex(
        ['Critical Risk', 'High Risk', 'Medium Risk', 'Low Risk']
    ).fillna(0).reset_index()
    risk_summary.columns = ['Risk Tier', 'Count']

    fig_bar = px.bar(
        risk_summary,
        x='Risk Tier',
        y='Count',
        color='Risk Tier',
        color_discrete_map=risk_palette,
        text_auto=True
    )
    fig_bar = apply_editorial_theme(fig_bar)
    fig_bar.update_layout(showlegend=False)
    st.plotly_chart(fig_bar, use_container_width=True)

with col_r:
    st.markdown("#### Risk Factors Breakdown by District")
    dist_factors = filtered_schools.groupby('district').agg(
        absenteeism=('risk_component_absenteeism', 'mean'),
        academic=('risk_component_academic', 'mean'),
        infra=('risk_component_infrastructure', 'mean'),
        mdm=('risk_component_mdm', 'mean')
    ).reset_index()

    fig_stack = px.bar(
        dist_factors,
        x='district',
        y=['absenteeism', 'academic', 'infra', 'mdm'],
        labels={'value': 'Risk Contribution', 'variable': 'Component', 'district': 'District'},
        color_discrete_sequence=[VERMILION, EARTH, INK, MOSS]
    )
    fig_stack = apply_editorial_theme(fig_stack)
    fig_stack.update_layout(legend={'orientation': 'h', 'y': 1.15, 'font': {'family': "'Newsreader', serif"}})
    st.plotly_chart(fig_stack, use_container_width=True)

# Scatter plot
st.markdown("#### Correlation: Attendance Rate vs Academic FLN Score (By Risk Tier)")
fig_scatter = px.scatter(
    filtered_schools,
    x='avg_attendance_rate_pct',
    y='avg_fln_score_pct',
    color='srdri_risk_level',
    size='total_enrolled_students',
    hover_name='school_name',
    hover_data=['district', 'srdri_score', 'kg_grain_per_student'],
    color_discrete_map=risk_palette,
    labels={'avg_attendance_rate_pct': 'Clean Attendance Rate (%)', 'avg_fln_score_pct': 'FLN Academic Score (%)'}
)
fig_scatter = apply_editorial_theme(fig_scatter)
st.plotly_chart(fig_scatter, use_container_width=True)

# School Inspector Drilldown
st.markdown("### 🔎 Individual School Risk Diagnosis")
school_options = filtered_schools[['school_id', 'school_name', 'district']].copy()
school_options['display'] = school_options['school_id'] + " - " + school_options['school_name'] + " (" + school_options['district'] + ")"
selected_school_display = st.selectbox("Select School to Inspect Component Profile", options=school_options['display'].tolist())

if selected_school_display:
    sel_id = selected_school_display.split(" - ")[0]
    school_row = filtered_schools[filtered_schools['school_id'] == sel_id].iloc[0]

    sc1, sc2, sc3, sc4 = st.columns(4)
    with sc1:
        st.metric("Absenteeism Risk", f"{school_row['risk_component_absenteeism']:.1f}/100")
    with sc2:
        st.metric("Academic Deficit Risk", f"{school_row['risk_component_academic']:.1f}/100")
    with sc3:
        st.metric("Infrastructure Deficit", f"{school_row['risk_component_infrastructure']:.1f}/100")
    with sc4:
        st.metric("MDM Disruption Risk", f"{school_row['risk_component_mdm']:.1f}/100")

    st.markdown(f"**Overall SRDRI Score:** `{school_row['srdri_score']:.1f}` | **Status:** `{school_row['srdri_risk_level']}` | **Enrollment:** `{school_row['total_enrolled_students']}`")

# Vulnerable Schools Table
st.markdown("### ⚠️ Top 20 Most Vulnerable Schools Register")
vulnerable_df = filtered_schools[filtered_schools['srdri_risk_level'].isin(['Critical Risk', 'High Risk'])][
    ['school_id', 'school_name', 'district', 'srdri_score', 'srdri_risk_level', 'avg_attendance_rate_pct', 'avg_fln_score_pct', 'avg_infra_score', 'kg_grain_per_student']
].head(20)

st.dataframe(vulnerable_df, hide_index=True, use_container_width=True)

# Render The Architect (Creator Profile) and Project Reference Mega-Footer
render_creator_card()
render_editorial_footer()

