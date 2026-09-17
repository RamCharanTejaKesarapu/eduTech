#!/usr/bin/env python3
"""
scripts/system_health_check.py
Comprehensive diagnostic and health check tool for the EduTech platform.
Verifies runtime dependencies, raw dataset availability, analytical marts, and test suite.
"""

import sys
import os

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

def check_dependencies():
    required_packages = [
        'streamlit', 'duckdb', 'pandas', 'plotly', 'openpyxl', 'pytest', 'numpy', 'statsmodels'
    ]
    missing = []
    for pkg in required_packages:
        try:
            __import__(pkg)
        except ImportError:
            missing.append(pkg)
    return len(missing) == 0, missing

def check_raw_datasets():
    from pipeline.utils import get_raw_data_dir
    try:
        raw_dir = get_raw_data_dir()
    except Exception as e:
        return False, str(e)

    expected_files = [
        "track4_school_master.csv",
        "track4_student_attendance.csv",
        "track4_school_infrastructure.csv",
        "track4_mid_day_meal_procurement.xlsx",
        "track4_test_scores.json"
    ]
    missing = [f for f in expected_files if not os.path.exists(os.path.join(raw_dir, f))]
    return len(missing) == 0, missing

def check_duckdb_marts():
    import duckdb
    db_path = os.path.join(PROJECT_ROOT, "data", "processed", "education_data.duckdb")
    if not os.path.exists(db_path):
        return False, "Database file not found at data/processed/education_data.duckdb"

    required_tables = [
        'dim_school', 'dim_vendor', 'fct_attendance', 'fct_infrastructure',
        'fct_mdm_procurement', 'fct_test_scores', 'agg_school_retention_risk'
    ]
    try:
        con = duckdb.connect(db_path, read_only=True)
        tables = [r[0] for r in con.execute("SHOW TABLES;").fetchall()]
        con.close()
        missing = [t for t in required_tables if t not in tables]
        return len(missing) == 0, missing
    except Exception as e:
        return False, str(e)

def run_diagnostics():
    print("=" * 60)
    print("EduTech Platform — System Diagnostic & Health Check")
    print("=" * 60)

    # 1. Dependencies
    dep_ok, dep_missing = check_dependencies()
    status_str = "PASS" if dep_ok else f"FAIL (Missing: {dep_missing})"
    print(f"[{status_str}] Python Dependencies")

    # 2. Raw Datasets
    raw_ok, raw_missing = check_raw_datasets()
    status_str = "PASS" if raw_ok else f"FAIL (Missing: {raw_missing})"
    print(f"[{status_str}] Raw Dataset Assets")

    # 3. DuckDB Marts
    db_ok, db_missing = check_duckdb_marts()
    status_str = "PASS" if db_ok else f"FAIL (Missing: {db_missing})"
    print(f"[{status_str}] DuckDB Analytical Marts")

    all_passed = dep_ok and raw_ok and db_ok
    print("=" * 60)
    if all_passed:
        print("ALL DIAGNOSTIC CHECKS PASSED: Platform is fully operational!")
        return 0
    else:
        print("ONE OR MORE CHECKS FAILED: Please inspect errors above.")
        return 1

if __name__ == '__main__':
    sys.exit(run_diagnostics())
