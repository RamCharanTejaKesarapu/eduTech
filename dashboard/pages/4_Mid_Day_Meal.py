"""
dashboard/pages/4_Mid_Day_Meal.py
Mid-Day Meal (MDM) welfare scheme efficacy, procurement volume, cost efficiency, and vendor forensics.
"""

import os
import streamlit as st
import plotly.express as px
import pandas as pd

st.set_page_config(
    page_title="Mid-Day Meal Efficacy • EduTech",
    page_icon="🍲",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load CSS
css_path = os.path.join(os.path.dirname(__file__), "..", "styles.css")
if os.path.exists(css_path):
    with open(css_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

from components.data_loader import (
    load_mdm_grain_summary,
    load_vendor_summary,
    load_school_risk_marts,
    run_query
)
from components.kpi_cards import render_kpi_card, render_page_header
from components.theme import apply_editorial_theme, INK, EARTH, BRASS, VERMILION, MOSS
from components.top_nav import render_top_masthead
from components.creator_card import render_creator_card
from components.footer import render_editorial_footer

render_top_masthead("Meals")

render_page_header(
    title="Mid-Day Meal (MDM) Efficacy & Supply Chain",
    subtitle="Grain Procurement Logistics, Food Security per Enrolled Student & Vendor Audit",
    badge="Welfare Schemes Monitoring"
)

df_grain = load_mdm_grain_summary()
df_vendors = load_vendor_summary()
df_schools = load_school_risk_marts()

# Query totals
mdm_totals = run_query("""
    SELECT 
        SUM(quantity_kg) AS total_kg,
        SUM(total_cost_inr) AS total_cost,
        AVG(cost_per_kg) AS avg_cost,
        SUM(is_sunday_procurement) AS sunday_procurements,
        COUNT(*) AS total_orders
    FROM fct_mdm_procurement;
""").iloc[0]

# KPIs
col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    render_kpi_card("Total Grain Procured", f"{mdm_totals['total_kg']/1e3:.1f} Tonnes", f"{mdm_totals['total_kg']:,.0f} KG")
with col2:
    render_kpi_card("Total Procurement Spend", f"₹{mdm_totals['total_cost']/1e6:.2f}M", "Consolidated Budget")
with col3:
    render_kpi_card("Average Cost / KG", f"₹{mdm_totals['avg_cost']:.2f}", "Across All Staples")
with col4:
    render_kpi_card("Sunday Deliveries", f"{int(mdm_totals['sunday_procurements']):,}", "School Closed Anomalies", is_positive=False)
with col5:
    mean_kg_student = df_schools['kg_grain_per_student'].mean()
    render_kpi_card("Grain / Student Ratio", f"{mean_kg_student:.2f} KG", "Two-Year Aggregate Mean")

st.markdown("---")

col_left, col_right = st.columns(2)

with col_left:
    st.markdown("#### Procurement Volume & Spend by Staple Food Category")
    fig_grain = px.bar(
        df_grain,
        x='food_category',
        y='total_kg',
        text_auto='.1f',
        color='food_category',
        color_discrete_sequence=[INK, EARTH, BRASS, MOSS],
        labels={'food_category': 'Food Category', 'total_kg': 'Total Quantity (KG)'}
    )
    fig_grain = apply_editorial_theme(fig_grain)
    fig_grain.update_layout(showlegend=False)
    st.plotly_chart(fig_grain, use_container_width=True)

with col_right:
    st.markdown("#### Vendor Syndicate Spend Distribution (INR)")
    vendor_group_df = df_vendors.groupby('vendor_group')['total_cost_inr'].sum().reset_index()
    fig_vendor_pie = px.pie(
        vendor_group_df,
        names='vendor_group',
        values='total_cost_inr',
        hole=0.55,
        color_discrete_sequence=[INK, EARTH, BRASS, MOSS, VERMILION]
    )
    fig_vendor_pie = apply_editorial_theme(fig_vendor_pie)
    fig_vendor_pie.update_layout(legend={'orientation': 'h', 'y': -0.15, 'font': {'family': "'Newsreader', serif"}})
    st.plotly_chart(fig_vendor_pie, use_container_width=True)

# Vendor Performance Ranking Table
st.markdown("### 🏢 Vendor Performance & Supply Audit")
st.dataframe(
    df_vendors,
    column_config={
        "vendor_name": "Vendor Business Entity",
        "vendor_group": "Parent Syndicate",
        "total_procurement_records": st.column_config.NumberColumn("Procurements", format="%d"),
        "total_volume_kg": st.column_config.NumberColumn("Total Supplied (KG)", format="%,.1f kg"),
        "total_cost_inr": st.column_config.NumberColumn("Total Billed (₹)", format="₹%,.0f"),
        "avg_cost_per_kg": st.column_config.NumberColumn("Avg Unit Cost (₹/kg)", format="₹%.2f"),
        "sunday_procurements_count": st.column_config.NumberColumn("Sunday Orders", format="%d"),
        "sunday_procurement_rate_pct": st.column_config.NumberColumn("Sunday Anomaly %", format="%.1f%%")
    },
    hide_index=True,
    use_container_width=True
)

st.markdown("---")

# Per-Student Supply & Wastage Risk Analysis
st.markdown("### ⚖️ Grain Supplied per Enrolled Student (Wastage vs Deficit Forensics)")
st.markdown("""
Normative Mid-Day Meal grain guidelines allocate approximately 100g to 150g per student per school day.
Extreme outliers (over 8 kg/student over the observation period) indicate potential stock hoarding or ghost procurement,
while values below 1.5 kg/student indicate critical nutritional deficit.
""")

col_hist, col_top_waste = st.columns(2)

with col_hist:
    st.markdown("#### Distribution of KG Grain per Enrolled Student")
    fig_hist = px.histogram(
        df_schools,
        x='kg_grain_per_student',
        nbins=30,
        color_discrete_sequence=['#0D9488'],
        labels={'kg_grain_per_student': 'Grain Supplied per Student (KG)'}
    )
    fig_hist.update_layout(paper_bgcolor='#F8FAFC', plot_bgcolor='#FFFFFF')
    st.plotly_chart(fig_hist, use_container_width=True)

with col_top_waste:
    st.markdown("#### Top 10 Schools: Highest Disproportionate Procurement")
    top_proc = df_schools.sort_values('kg_grain_per_student', ascending=False)[
        ['school_name', 'district', 'total_enrolled_students', 'total_grain_kg', 'kg_grain_per_student']
    ].head(10)
    fig_top_p = px.bar(
        top_proc,
        y='school_name',
        x='kg_grain_per_student',
        orientation='h',
        text_auto='.1f',
        color='kg_grain_per_student',
        color_continuous_scale=['#FED7AA', '#EA580C'],
        labels={'kg_grain_per_student': 'KG / Student', 'school_name': 'School'}
    )
    fig_top_p.update_layout(paper_bgcolor='#F8FAFC', plot_bgcolor='#FFFFFF', coloraxis_showscale=False)
    st.plotly_chart(fig_top_p, use_container_width=True)

# Render The Architect (Creator Profile) and Project Reference Mega-Footer
render_creator_card()
render_editorial_footer()
