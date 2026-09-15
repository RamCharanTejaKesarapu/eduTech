"""
tests/test_metrics.py
Unit tests for business metrics, proxy fraud calculation, and SRDRI scoring.
"""

import pytest
import os
import duckdb

def get_duckdb_con():
    proj_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    db_path = os.path.join(proj_root, "data", "processed", "education_data.duckdb")
    return duckdb.connect(db_path, read_only=True)

def test_database_entities_exist():
    con = get_duckdb_con()
    tables = [t[0] for t in con.execute("SHOW TABLES;").fetchall()]
    expected = [
        'dim_school', 'dim_vendor', 'fct_attendance',
        'fct_infrastructure', 'fct_mdm_procurement',
        'fct_test_scores', 'agg_school_retention_risk', 'agg_district_summary'
    ]
    for exp in expected:
        assert exp in tables, f"Expected table '{exp}' missing from DuckDB."
    con.close()

def test_school_count_and_uniqueness():
    con = get_duckdb_con()
    cnt = con.execute("SELECT COUNT(*), COUNT(DISTINCT school_id) FROM dim_school;").fetchone()
    assert cnt[0] == 600, f"Expected exactly 600 schools, found {cnt[0]}"
    assert cnt[0] == cnt[1], "School IDs are not unique in dim_school"
    con.close()

def test_proxy_attendance_metrics():
    con = get_duckdb_con()
    res = con.execute("""
        SELECT 
            SUM(is_proxy_attendance) AS proxy_fraud,
            SUM(is_attendance_overflow) AS overflow,
            COUNT(*) AS total
        FROM fct_attendance;
    """).fetchone()
    con.close()

    # Raw had 1,019, minus 40 duplicate records removed during deduplication = 979 clean proxy records
    assert res[0] == 979, f"Expected 979 clean proxy attendance fraud records, found {res[0]}"
    assert res[1] == 806, f"Expected 806 clean overflow records, found {res[1]}"
    assert res[2] == 20000, f"Expected 20,000 clean attendance records, found {res[2]}"

def test_srdri_risk_formula_bounds():
    con = get_duckdb_con()
    scores = con.execute("""
        SELECT 
            MIN(srdri_score), 
            MAX(srdri_score),
            AVG(srdri_score),
            COUNT(DISTINCT srdri_risk_level)
        FROM agg_school_retention_risk;
    """).fetchone()
    con.close()

    assert scores[0] >= 0.0, "SRDRI minimum score below 0"
    assert scores[1] <= 100.0, "SRDRI maximum score above 100"
    assert scores[3] >= 3, "Expected at least 3 distinct risk levels represented in schools"
