"""
dashboard/pages/5_Infrastructure.py
School infrastructure evaluation, amenity availability, deficit index, and inspector audit.
"""

import os
import streamlit as st
import plotly.express as px
import pandas as pd

# Load CSS
css_path = os.path.join(os.path.dirname(__file__), "..", "styles.css")
if os.path.exists(css_path):
    with open(css_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

from components.data_loader import (
    load_infra_amenity_summary,
    load_school_risk_marts,
    run_query
)
from components.kpi_cards import render_kpi_card, render_page_header
from components.theme import apply_editorial_theme, INK, EARTH, BRASS, VERMILION, MOSS
from components.top_nav import render_top_masthead

render_top_masthead("Infra")

render_page_header(
    title="School Infrastructure & Basic Amenities",
    subtitle="Audit of Key Physical Amenities, District Infrastructure Deficit Index & Attendance Correlation",
    badge="Infrastructure Monitoring"
)

df_infra_dist = load_infra_amenity_summary()
df_schools = load_school_risk_marts()

# State aggregate metrics
amenities_agg = run_query("""
    SELECT 
        ROUND(AVG(has_electricity) * 100.0, 1) AS elec_pct,
        ROUND(AVG(has_drinking_water) * 100.0, 1) AS water_pct,
        ROUND(AVG(has_functional_toilet) * 100.0, 1) AS toilet_pct,
        ROUND(AVG(has_boundary_wall) * 100.0, 1) AS wall_pct,
        ROUND(AVG(has_playground) * 100.0, 1) AS play_pct,
        ROUND(AVG(infra_score), 1) AS overall_score
    FROM fct_infrastructure;
""").iloc[0]

# KPIs
col1, col2, col3, col4, col5, col6 = st.columns(6)
with col1:
    render_kpi_card("Electricity", f"{amenities_agg['elec_pct']}%", "Functional Power Grid")
with col2:
    render_kpi_card("Drinking Water", f"{amenities_agg['water_pct']}%", "Potable Water Access")
with col3:
    render_kpi_card("Functional Toilets", f"{amenities_agg['toilet_pct']}%", "Sanitation Facilities")
with col4:
    render_kpi_card("Boundary Wall", f"{amenities_agg['wall_pct']}%", "Perimeter Security")
with col5:
    render_kpi_card("Playground", f"{amenities_agg['play_pct']}%", "Recreational Grounds")
with col6:
    render_kpi_card("Overall Quality", f"{amenities_agg['overall_score']}/100", "State Facility Index")

st.markdown("---")

col_l, col_r = st.columns(2)

with col_l:
    st.markdown("#### Amenity Functional Rate Comparison by District (%)")
    df_dist_melt = df_infra_dist.melt(
        id_vars=['district'],
        value_vars=['electricity_pct', 'drinking_water_pct', 'functional_toilet_pct', 'boundary_wall_pct', 'playground_pct'],
        var_name='Amenity',
        value_name='Coverage %'
    )
    df_dist_melt['Amenity'] = df_dist_melt['Amenity'].str.replace('_pct', '').str.replace('_', ' ').str.title()

    fig_amenity = px.bar(
        df_dist_melt,
        x='district',
        y='Coverage %',
        color='Amenity',
        barmode='group',
        labels={'district': 'District'},
        color_discrete_sequence=[INK, EARTH, BRASS, MOSS, VERMILION]
    )
    fig_amenity = apply_editorial_theme(fig_amenity)
    fig_amenity.update_layout(legend={'orientation': 'h', 'y': 1.15, 'font': {'family': "'Newsreader', serif"}})
    st.plotly_chart(fig_amenity, use_container_width=True)

with col_r:
    st.markdown("#### Infrastructure Deficit Index by District")
    df_infra_dist['deficit_index'] = (100.0 - df_infra_dist['avg_infra_score']).round(1)
    df_deficit = df_infra_dist.sort_values('deficit_index', ascending=False)

    fig_def = px.bar(
        df_deficit,
        x='district',
        y='deficit_index',
        text_auto='.1f',
        color='deficit_index',
        color_continuous_scale=['#dfcbb0', '#b34f3e'],
        labels={'deficit_index': 'Deficit Index (%)', 'district': 'District'}
    )
    fig_def = apply_editorial_theme(fig_def)
    fig_def.update_layout(coloraxis_showscale=False)
    st.plotly_chart(fig_def, use_container_width=True)

st.markdown("---")

# Comparative Attendance Impact
st.markdown("### 🔍 Observed Associations: Amenities vs Attendance & Retention")
st.markdown("""
<div class="alert-box">
    <b>Empirical Data Observation:</b> Comparing historical attendance rates between schools with and without functional basic amenities.
    Statistical differences reflect observed empirical averages in inspected government schools (causation is not inferred).
</div>
""", unsafe_allow_html=True)

col_comp1, col_comp2 = st.columns(2)

with col_comp1:
    st.markdown("#### Attendance by Electricity Availability")
    elec_comp = run_query("""
        SELECT 
            CASE WHEN i.has_electricity = 1 THEN 'Functional Electricity' ELSE 'No Electricity' END AS status,
            ROUND(AVG(a.attendance_rate_capped) * 100.0, 2) AS avg_att_pct,
            COUNT(DISTINCT a.school_id) AS school_count
        FROM fct_attendance a
        JOIN fct_infrastructure i ON a.school_id = i.school_id
        WHERE a.quality_status = 'VALID'
        GROUP BY status;
    """)
    fig_c1 = px.bar(
        elec_comp,
        x='status',
        y='avg_att_pct',
        text_auto='.2f',
        color='status',
        color_discrete_sequence=[MOSS, VERMILION],
        labels={'avg_att_pct': 'Attendance Rate (%)', 'status': 'Status'}
    )
    fig_c1 = apply_editorial_theme(fig_c1)
    fig_c1.update_layout(showlegend=False)
    st.plotly_chart(fig_c1, use_container_width=True)

with col_comp2:
    st.markdown("#### Attendance by Functional Toilet Facilities")
    toilet_comp = run_query("""
        SELECT 
            CASE WHEN i.has_functional_toilet = 1 THEN 'Functional Toilets' ELSE 'Defective / No Toilets' END AS status,
            ROUND(AVG(a.attendance_rate_capped) * 100.0, 2) AS avg_att_pct,
            COUNT(DISTINCT a.school_id) AS school_count
        FROM fct_attendance a
        JOIN fct_infrastructure i ON a.school_id = i.school_id
        WHERE a.quality_status = 'VALID'
        GROUP BY status;
    """)
    fig_c2 = px.bar(
        toilet_comp,
        x='status',
        y='avg_att_pct',
        text_auto='.2f',
        color='status',
        color_discrete_sequence=[INK, EARTH],
        labels={'avg_att_pct': 'Attendance Rate (%)', 'status': 'Status'}
    )
    fig_c2 = apply_editorial_theme(fig_c2)
    fig_c2.update_layout(showlegend=False)
    st.plotly_chart(fig_c2, use_container_width=True)

# Inspector Remarks Audit
st.markdown("### 📝 Inspector Qualitative Observations Breakdown")
remarks_df = run_query("""
    SELECT 
        remarks,
        COUNT(*) AS inspection_records,
        ROUND(AVG(infra_score), 1) AS avg_infra_score
    FROM fct_infrastructure
    GROUP BY remarks
    ORDER BY inspection_records DESC;
""")

st.dataframe(remarks_df, hide_index=True, use_container_width=True)
