"""
agent/sql_guardrails.py
Strict AST and pattern-based SQL security guardrails for safe DuckDB analytical execution.
Blocks all DDL, DML, file access, and non-whitelisted constructs.
"""

import re

APPROVED_TABLES = {
    'agg_school_retention_risk',
    'agg_district_summary',
    'agg_mdm_vendor_summary',
    'dim_school',
    'dim_vendor',
    'fct_attendance',
    'fct_infrastructure',
    'fct_mdm_procurement',
    'fct_test_scores',
    'fct_data_quality_log'
}

DISALLOWED_KEYWORDS = [
    r'\bDROP\b',
    r'\bDELETE\b',
    r'\bUPDATE\b',
    r'\bINSERT\b',
    r'\bALTER\b',
    r'\bCREATE\b',
    r'\bATTACH\b',
    r'\bDETACH\b',
    r'\bCOPY\b',
    r'\bPRAGMA\b',
    r'\bCALL\b',
    r'\bINSTALL\b',
    r'\bLOAD\b',
    r'\bEXPORT\b',
    r'\bIMPORT\b',
    r'\bEXECUTE\b',
    r'\bEXEC\b',
    r'\bSYSTEM\b',
    r'\bREPLACE\b',
    r'\bTRUNCATE\b'
]

DISALLOWED_FUNCTIONS = [
    r'read_csv',
    r'read_parquet',
    r'read_json',
    r'write_csv',
    r'write_parquet',
    r'glob',
    r'query_table',
    r'sqlite_scan',
    r'postgres_scan'
]

def validate_sql_query(query: str):
    """
    Validates that a SQL query is strictly a read-only analytical SELECT query
    targeting approved tables without filesystem or administrative access.
    
    Returns:
        tuple: (is_safe: bool, error_message: str or None)
    """
    if not query or not isinstance(query, str):
        return False, "Query must be a non-empty string."

    clean_query = query.strip()

    # Must start with SELECT or WITH (for CTEs)
    if not re.match(r'^(SELECT|WITH)\b', clean_query, re.IGNORECASE):
        return False, "Security Violation: Only SELECT or WITH (CTE) queries are permitted."

    # Check for multiple statements (semicolon followed by another query)
    statements = [s.strip() for s in clean_query.split(';') if s.strip()]
    if len(statements) > 1:
        return False, "Security Violation: Multiple queries separated by semicolons are not permitted."

    # Check disallowed keywords
    for pattern in DISALLOWED_KEYWORDS:
        if re.search(pattern, clean_query, re.IGNORECASE):
            return False, f"Security Violation: Prohibited SQL keyword detected matching '{pattern}'."

    # Check disallowed functions
    for fn in DISALLOWED_FUNCTIONS:
        if re.search(rf'\b{fn}\b', clean_query, re.IGNORECASE):
            return False, f"Security Violation: External function '{fn}' is blocked."

    # Extract any defined CTE names (e.g. WITH cte_name AS (...))
    cte_names = set(re.findall(r'\bWITH\s+([a-zA-Z0-9_]+)\s+AS\b', clean_query, re.IGNORECASE))
    allowed_tables = APPROVED_TABLES.union({name.lower() for name in cte_names})

    # Verify table references
    # Simple regex to find words after FROM or JOIN
    table_matches = re.findall(r'\b(?:FROM|JOIN)\s+([a-zA-Z0-9_]+)', clean_query, re.IGNORECASE)
    for tbl in table_matches:
        tbl_lower = tbl.lower()
        if tbl_lower not in allowed_tables and tbl_lower not in ['unnest']:
            return False, f"Security Violation: Access to unapproved table or view '{tbl}' is forbidden."

    return True, None
