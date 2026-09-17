"""
tests/test_health_check.py
Unit tests for the diagnostic and system health check utility.
"""

from scripts.system_health_check import check_dependencies, check_raw_datasets, check_duckdb_marts

def test_dependencies_check():
    ok, missing = check_dependencies()
    assert ok, f"Dependencies check failed. Missing: {missing}"

def test_raw_datasets_check():
    ok, missing = check_raw_datasets()
    assert ok, f"Raw datasets check failed. Missing: {missing}"

def test_duckdb_marts_check():
    ok, missing = check_duckdb_marts()
    assert ok, f"DuckDB analytical marts check failed. Missing: {missing}"
