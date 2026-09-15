"""
dashboard/pages/7_Data_Quality.py
Data Quality, Pipeline Forensics & Audit Report.
Exhibits transparent before/after transformation metrics, anomaly classifications, and audit logs.
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

from components.data_loader import load_data_quality_log, run_query
from components.kpi_cards import render_kpi_card, render_page_header
from components.top_nav import render_top_masthead

render_top_masthead("Quality")

render_page_header(
    title="Data Quality & Pipeline Audit",
    subtitle="End-to-End Data Quality Assurance, Deduplication, Anomaly Classification & Audit Ledger",
    badge="Data Governance & Verification"
)

# Pipeline Summary Metrics
k1, k2, k3, k4 = st.columns(4)
with k1:
    render_kpi_card("Total Raw Ingested", "44,928", "Across All 5 Datasets")
with k2:
    render_kpi_card("Cleaned Records", "43,600", "Loaded into DuckDB")
with k3:
    render_kpi_card("Duplicates Purged", "1,328", "Exact Duplicate Rows Removed")
with k4:
    render_kpi_card("Anomalies Handled", "4,755", "Corrected & Flagged", is_positive=False)

st.markdown("---")

# Section 1: Before/After Pipeline Audit Matrix
st.markdown("### 📊 Dataset Cleaning & Normalization Audit Matrix")

audit_matrix = [
    {
        "Dataset": "track4_school_master.csv",
        "Raw Rows": 618,
        "Clean Rows": 600,
        "Duplicates Removed": 18,
        "Key Data Quality Problems Identified": "Inconsistent casing ('patiala' vs 'Patiala'), 23 missing districts, 64 missing blocks.",
        "Applied Cleaning & Normalization Treatment": "Regex-normalized school_id to 'SCH%04d'. Imputed 21 missing districts via block mode; assigned 'Unassigned' to 2 unresolved schools."
    },
    {
        "Dataset": "track4_student_attendance.csv",
        "Raw Rows": 20800,
        "Clean Rows": 20000,
        "Duplicates Removed": 800,
        "Key Data Quality Problems Identified": "425 null record IDs; 5 messy ID variants; 806 attendance overflow cases (present > total); 979 Sunday 100% attendance cases.",
        "Applied Cleaning & Normalization Treatment": "Generated surrogate IDs; Roman numeral grades to digits; flagged proxy attendance and overflow; capped rates for clean analysis."
    },
    {
        "Dataset": "track4_school_infrastructure.csv",
        "Raw Rows": 3150,
        "Clean Rows": 3000,
        "Duplicates Removed": 150,
        "Key Data Quality Problems Identified": "22 multilingual/messy boolean strings ('Hai', 'Nahi', 'haan', 'Kharab', 'Working', 'Broken', '1', '0').",
        "Applied Cleaning & Normalization Treatment": "Mapped 100% of non-null variants into standardized binary (1/0); formulated Infrastructure Quality Score (0-100) and Deficit Index."
    },
    {
        "Dataset": "track4_mid_day_meal_procurement.xlsx",
        "Raw Rows": 12360,
        "Clean Rows": 12000,
        "Duplicates Removed": 360,
        "Key Data Quality Problems Identified": "1,895 embedded unit strings ('14.9 kg'); mixed units ('50kg Bags', 'Sacks', 'Grams', 'KG'); messy currency strings ('Rs. 1,600', '₹1,317', '336/-').",
        "Applied Cleaning & Normalization Treatment": "Standardized all quantities to KG (1 bag = 50 kg; grams / 1,000); stripped currency symbols to clean floats; mapped 12 vendors into 4 groups."
    },
    {
        "Dataset": "track4_test_scores.json",
        "Raw Rows": 8000,
        "Clean Rows": 8000,
        "Duplicates Removed": 0,
        "Key Data Quality Problems Identified": "6 distinct grading scales ('Letter Grade', 'CGPA', 'Raw Marks', 'Percentage', 'pct', '%'); mixed subjects ('Math', 'Ganit', 'Mathematics').",
        "Applied Cleaning & Normalization Treatment": "Mapped Letter Grades to midpoints (A+=95, A=85, B=75, C=65, D=55, E=45); CGPA * 10; raw marks to %; unified subject names."
    }
]

st.dataframe(pd.DataFrame(audit_matrix), hide_index=True, use_container_width=True)

st.markdown("---")

# Section 2: Visual Breakdown of Detected Anomaly Types
col_v1, col_v2 = st.columns(2)

with col_v1:
    st.markdown("#### Distribution of Anomaly Forensics")
    anomaly_counts = pd.DataFrame([
        {"Anomaly Type": "Sunday Proxy Fraud (100% Att)", "Count": 979},
        {"Anomaly Type": "Attendance Overflow (Present > Total)", "Count": 806},
        {"Anomaly Type": "Sunday MDM Procurements", "Count": 1736},
        {"Anomaly Type": "Embedded Quantity Units in String", "Count": 1895},
        {"Anomaly Type": "Currency Formatting Cleanup", "Count": 8020},
        {"Anomaly Type": "Missing Record IDs Imputed", "Count": 425},
        {"Anomaly Type": "Missing Districts Imputed via Block", "Count": 21}
    ]).sort_values('Count', ascending=True)

    fig_anom = px.bar(
        anomaly_counts,
        y='Anomaly Type',
        x='Count',
        orientation='h',
        text_auto=True,
        color='Count',
        color_continuous_scale=['#93C5FD', '#1E3A8A']
    )
    fig_anom.update_layout(paper_bgcolor='#F8FAFC', plot_bgcolor='#FFFFFF', coloraxis_showscale=False)
    st.plotly_chart(fig_anom, use_container_width=True)

with col_v2:
    st.markdown("#### Attendance Record Quality Status Breakdown")
    status_df = run_query("""
        SELECT quality_status, COUNT(*) AS count
        FROM fct_attendance
        GROUP BY quality_status;
    """)

    fig_status = px.pie(
        status_df,
        names='quality_status',
        values='count',
        hole=0.45,
        color='quality_status',
        color_discrete_map={
            'VALID': '#10B981',
            'SUSPICIOUS_PROXY': '#EF4444',
            'INVALID_OVERFLOW': '#F97316',
            'SUSPICIOUS_SUNDAY': '#FBBF24'
        }
    )
    fig_status.update_layout(paper_bgcolor='#F8FAFC', legend={'orientation': 'h', 'y': -0.1})
    st.plotly_chart(fig_status, use_container_width=True)

st.markdown("---")

# Section 3: Interactive Data Quality Audit Log
st.markdown("### 📜 Real-Time Data Quality Audit Ledger")
st.markdown("Below is the record-level ledger tracking every correction, anomaly flagging, and normalization event:")

df_audit = load_data_quality_log()

if not df_audit.empty:
    status_filter = st.multiselect(
        "Filter by Quality Status",
        options=df_audit['quality_status'].dropna().unique().tolist(),
        default=[]
    )
    if status_filter:
        df_audit = df_audit[df_audit['quality_status'].isin(status_filter)]

    st.dataframe(df_audit, hide_index=True, use_container_width=True)

    # Download button
    csv_audit = df_audit.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download Complete Quality Audit CSV",
        data=csv_audit,
        file_name="data_quality_audit_log.csv",
        mime="text/csv"
    )
else:
    st.info("Quality audit records are recorded in the data pipeline audit log.")
