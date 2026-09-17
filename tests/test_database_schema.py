"""
tests/test_database_schema.py
Integration tests validating DuckDB analytical database schema and table integrity.
"""

import os
import pytest
import duckdb

def get_duckdb_path():
    proj_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    return os.path.join(proj_root, "data", "processed", "education_data.duckdb")

@pytest.fixture(scope="module")
def db_conn():
    db_path = get_duckdb_path()
    if not os.path.exists(db_path):
        pytest.skip("education_data.duckdb not found. Run pipeline first.")
    conn = duckdb.connect(db_path, read_only=True)
    yield conn
    conn.close()

def test_all_expected_tables_exist(db_conn):
    expected_tables = {
        'dim_school',
        'dim_vendor',
        'fct_attendance',
        'fct_infrastructure',
        'fct_mdm_procurement',
        'fct_test_scores',
        'agg_school_retention_risk',
        'agg_district_summary',
        'agg_mdm_vendor_summary',
        'fct_data_quality_log'
    }
    tables_result = db_conn.execute("SHOW TABLES;").fetchall()
    actual_tables = {row[0] for row in tables_result}
    assert expected_tables.issubset(actual_tables), f"Missing tables: {expected_tables - actual_tables}"

def test_dim_school_uniqueness(db_conn):
    count_df = db_conn.execute("""
        SELECT COUNT(*) as total_count, COUNT(DISTINCT school_id) as unique_ids
        FROM dim_school;
    """).df()
    assert count_df.iloc[0]['total_count'] == 600
    assert count_df.iloc[0]['unique_ids'] == 600

def test_retention_risk_score_bounds(db_conn):
    stats = db_conn.execute("""
        SELECT MIN(srdri_score) as min_s, MAX(srdri_score) as max_s, COUNT(*) as cnt
        FROM agg_school_retention_risk;
    """).df()
    assert stats.iloc[0]['cnt'] == 600
    assert stats.iloc[0]['min_s'] >= 0.0
    assert stats.iloc[0]['max_s'] <= 100.0

def test_attendance_rate_capped_bounds(db_conn):
    stats = db_conn.execute("""
        SELECT MIN(attendance_rate_capped) as min_r, MAX(attendance_rate_capped) as max_r
        FROM fct_attendance;
    """).df()
    assert stats.iloc[0]['min_r'] >= 0.0
    assert stats.iloc[0]['max_r'] <= 1.0

def test_vendor_aggregation_integrity(db_conn):
    vendor_df = db_conn.execute("""
        SELECT COUNT(*) as total_vendors, SUM(total_cost_inr) as total_cost
        FROM agg_mdm_vendor_summary;
    """).df()
    assert vendor_df.iloc[0]['total_vendors'] > 0
    assert vendor_df.iloc[0]['total_cost'] > 0
