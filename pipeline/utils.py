"""
pipeline/utils.py
Common normalization, validation, and logging utilities for the Data Pipeline.
"""

import os
import re
import pandas as pd
import numpy as np
from datetime import datetime

# Root and directory helpers
def get_project_root():
    return os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

def get_raw_data_dir():
    root = get_project_root()
    candidates = [
        os.path.join(root, "data", "raw"),
        os.path.join(root, "track4_education_dataset_files (1)"),
        os.path.join(root, "..", "track4_education_dataset_files (1)")
    ]
    for c in candidates:
        if os.path.exists(c):
            return os.path.abspath(c)
    raise FileNotFoundError("Could not locate raw datasets directory.")

def get_processed_data_dir():
    root = get_project_root()
    proc_dir = os.path.join(root, "data", "processed")
    os.makedirs(proc_dir, exist_ok=True)
    return proc_dir

# School ID normalizer
def normalize_school_id(val):
    """
    Standardizes any school ID format into canonical 'SCHxxxx' (4-digit padded).
    Examples:
      'SCH0050'   -> 'SCH0050'
      'SCH-0596'  -> 'SCH0596'
      'sch_0054'  -> 'SCH0054'
      'S0433'     -> 'SCH0433'
      '208'       -> 'SCH0208'
      1001        -> 'SCH1001'
    """
    if pd.isna(val) or val is None:
        return None
    s = str(val).strip()
    digits = re.findall(r"\d+", s)
    if digits:
        return f"SCH{int(digits[0]):04d}"
    return s.upper()

# Boolean normalizer
POSITIVE_BOOLEAN_STRINGS = {
    'true', 'yes', 'y', '1', 'hai', 'haan', 'h', 'functional', 'working', 'available'
}

NEGATIVE_BOOLEAN_STRINGS = {
    'false', 'no', 'n', '0', 'nahi', 'nahi hai', 'na', 'broken', 'kharab', 'under repair', 'not available'
}

def normalize_boolean(val):
    """
    Maps 22 multilingual/messy representations into 1 (True), 0 (False), or None (Missing).
    """
    if pd.isna(val) or val is None:
        return None
    s = str(val).strip().lower()
    if s in POSITIVE_BOOLEAN_STRINGS:
        return 1
    if s in NEGATIVE_BOOLEAN_STRINGS:
        return 0
    return None

# Date parser
def parse_date_to_iso(series):
    """
    Parses mixed date strings (DD.MM.YYYY, MM-DD-YYYY, YYYY/MM/DD, DD-Mon-YYYY) into ISO YYYY-MM-DD.
    """
    parsed = pd.to_datetime(series, format='mixed', errors='coerce')
    return parsed.dt.strftime('%Y-%m-%d')

# Data Quality Audit Logger
class DataQualityAudit:
    def __init__(self):
        self.logs = []
        self.summary = {}

    def log_issue(self, dataset, record_id, column, issue_type, raw_value, corrected_value, status):
        self.logs.append({
            'dataset': dataset,
            'record_id': str(record_id),
            'column_name': column,
            'issue_type': issue_type,
            'raw_value': str(raw_value),
            'corrected_value': str(corrected_value),
            'quality_status': status,  # VALID, CORRECTED, SUSPICIOUS, INVALID
            'timestamp': datetime.now().isoformat()
        })

    def record_summary(self, dataset, total_raw, total_clean, duplicates, nulls_dict, anomalies_dict):
        self.summary[dataset] = {
            'total_raw_records': total_raw,
            'total_clean_records': total_clean,
            'duplicate_records_removed': duplicates,
            'null_counts': nulls_dict,
            'anomalies_detected': anomalies_dict
        }

    def to_dataframe(self):
        return pd.DataFrame(self.logs)

# Singleton audit instance
audit_logger = DataQualityAudit()
