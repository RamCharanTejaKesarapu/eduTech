"""
dashboard/components/data_loader.py
Cached data access helpers using DuckDB for optimal Streamlit performance.
"""

import os
import duckdb
import pandas as pd
import streamlit as st

def get_duckdb_path():
    proj_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    return os.path.join(proj_root, "data", "processed", "education_data.duckdb")

@st.cache_resource
def get_db_connection():
    db_path = get_duckdb_path()
    if not os.path.exists(db_path):
        # Fallback: run pipeline if db missing
        import sys
        proj_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        if proj_root not in sys.path:
            sys.path.insert(0, proj_root)
        from pipeline.run_pipeline import run_pipeline
        run_pipeline()
    return duckdb.connect(db_path, read_only=True)

def run_query(query: str, params=None) -> pd.DataFrame:
    con = get_db_connection()
    if params:
        return con.execute(query, params).df()
    return con.execute(query).df()

@st.cache_data(ttl=600)
def load_district_summary() -> pd.DataFrame:
    return run_query("SELECT * FROM agg_district_summary ORDER BY vulnerable_schools_count DESC, avg_srdri_score DESC;")

@st.cache_data(ttl=600)
def load_school_risk_marts() -> pd.DataFrame:
    return run_query("SELECT * FROM agg_school_retention_risk ORDER BY srdri_score DESC;")

@st.cache_data(ttl=600)
def load_dim_school() -> pd.DataFrame:
    return run_query("SELECT * FROM dim_school ORDER BY school_id;")

@st.cache_data(ttl=600)
def load_vendor_summary() -> pd.DataFrame:
    return run_query("SELECT * FROM agg_mdm_vendor_summary ORDER BY total_cost_inr DESC;")

@st.cache_data(ttl=600)
def load_attendance_summary() -> pd.DataFrame:
    return run_query("""
        SELECT 
            strftime(attendance_date, '%Y-%m') AS month,
            day_of_week,
            is_sunday,
            is_proxy_attendance,
            is_attendance_overflow,
            attendance_rate_capped,
            quality_status
        FROM fct_attendance;
    """)

@st.cache_data(ttl=600)
def load_fln_test_scores() -> pd.DataFrame:
    return run_query("""
        SELECT 
            grade,
            subject,
            original_scale,
            score_percentage,
            proficiency_tier
        FROM fct_test_scores;
    """)

@st.cache_data(ttl=600)
def load_infra_amenity_summary() -> pd.DataFrame:
    return run_query("""
        SELECT 
            s.district,
            ROUND(AVG(i.has_electricity) * 100.0, 1) AS electricity_pct,
            ROUND(AVG(i.has_drinking_water) * 100.0, 1) AS drinking_water_pct,
            ROUND(AVG(i.has_functional_toilet) * 100.0, 1) AS functional_toilet_pct,
            ROUND(AVG(i.has_boundary_wall) * 100.0, 1) AS boundary_wall_pct,
            ROUND(AVG(i.has_playground) * 100.0, 1) AS playground_pct,
            ROUND(AVG(i.infra_score), 1) AS avg_infra_score
        FROM fct_infrastructure i
        JOIN dim_school s ON i.school_id = s.school_id
        GROUP BY s.district
        ORDER BY avg_infra_score ASC;
    """)

@st.cache_data(ttl=600)
def load_mdm_grain_summary() -> pd.DataFrame:
    return run_query("""
        SELECT 
            food_category,
            ROUND(SUM(quantity_kg), 1) AS total_kg,
            ROUND(SUM(total_cost_inr), 1) AS total_cost_inr,
            ROUND(AVG(cost_per_kg), 1) AS avg_cost_per_kg
        FROM fct_mdm_procurement
        GROUP BY food_category
        ORDER BY total_kg DESC;
    """)

@st.cache_data(ttl=600)
def load_data_quality_log() -> pd.DataFrame:
    return run_query("SELECT * FROM fct_data_quality_log ORDER BY timestamp DESC LIMIT 500;")
