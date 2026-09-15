"""
tests/test_sql_safety.py
Security tests verifying SQL guardrail enforcement and injection prevention.
"""

import pytest
from agent.sql_guardrails import validate_sql_query

def test_safe_queries_pass():
    safe_queries = [
        "SELECT COUNT(*) FROM dim_school;",
        "SELECT district, AVG(avg_attendance_rate_pct) FROM agg_district_summary GROUP BY district;",
        "SELECT school_name, srdri_score FROM agg_school_retention_risk ORDER BY srdri_score DESC LIMIT 10;",
        "WITH cte AS (SELECT school_id, AVG(quantity_kg) as avg_kg FROM fct_mdm_procurement GROUP BY school_id) SELECT * FROM cte;"
    ]
    for q in safe_queries:
        is_safe, err = validate_sql_query(q)
        assert is_safe, f"Safe query was wrongly rejected: {q}. Error: {err}"

def test_destructive_keywords_blocked():
    blocked_queries = [
        "DROP TABLE dim_school;",
        "DELETE FROM fct_attendance WHERE 1=1;",
        "UPDATE dim_school SET district = 'Hacked';",
        "INSERT INTO dim_school VALUES ('SCH9999', 'Fake', 'Moga', 'Block', 100, 'Primary', 'Hindi');",
        "ALTER TABLE dim_school DROP COLUMN district;",
        "TRUNCATE TABLE fct_attendance;",
        "ATTACH 'hack.db' AS malicious;"
    ]
    for q in blocked_queries:
        is_safe, err = validate_sql_query(q)
        assert not is_safe, f"Destructive query was not blocked: {q}"

def test_filesystem_access_blocked():
    fs_queries = [
        "SELECT * FROM read_csv('data/raw/track4_school_master.csv');",
        "SELECT * FROM read_parquet('/etc/passwd');",
        "SELECT * FROM write_csv('dim_school', 'out.csv');"
    ]
    for q in fs_queries:
        is_safe, err = validate_sql_query(q)
        assert not is_safe, f"Filesystem query was not blocked: {q}"

def test_unapproved_tables_blocked():
    unapproved = [
        "SELECT * FROM sqlite_master;",
        "SELECT * FROM users;",
        "SELECT * FROM information_schema.tables;"
    ]
    for q in unapproved:
        is_safe, err = validate_sql_query(q)
        assert not is_safe, f"Query accessing unapproved table was not blocked: {q}"

def test_multiple_queries_blocked():
    multi = "SELECT * FROM dim_school; DROP TABLE fct_attendance;"
    is_safe, err = validate_sql_query(multi)
    assert not is_safe, "Multi-statement injection was not blocked"
