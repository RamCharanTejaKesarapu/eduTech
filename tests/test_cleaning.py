"""
tests/test_cleaning.py
Unit tests for data normalization, cleaning, and validation functions.
"""

import pytest
import numpy as np
import pandas as pd
from pipeline.utils import normalize_school_id, normalize_boolean, parse_date_to_iso
from pipeline.clean_attendance import normalize_grade
from pipeline.clean_mdm import parse_mdm_quantity, parse_mdm_cost
from pipeline.clean_test_scores import normalize_fln_score

def test_normalize_school_id():
    assert normalize_school_id("SCH0050") == "SCH0050"
    assert normalize_school_id("SCH-0596") == "SCH0596"
    assert normalize_school_id("sch_0054") == "SCH0054"
    assert normalize_school_id("S0433") == "SCH0433"
    assert normalize_school_id("208") == "SCH0208"
    assert normalize_school_id("1001") == "SCH1001"
    assert normalize_school_id(None) is None
    assert normalize_school_id(np.nan) is None

def test_normalize_boolean():
    # Positive set
    positives = ['True', 'true', 'YES', 'yes', 'Y', 'y', '1', 'Hai', 'haan', 'Haan', 'H', 'Functional', 'Working', 'Available']
    for val in positives:
        assert normalize_boolean(val) == 1, f"Failed on positive {val}"

    # Negative set
    negatives = ['False', 'false', 'NO', 'no', 'N', 'n', '0', 'Nahi', 'nahi hai', 'na', 'Broken', 'Kharab', 'Under Repair', 'Not Available']
    for val in negatives:
        assert normalize_boolean(val) == 0, f"Failed on negative {val}"

    # Missing values
    assert normalize_boolean(None) is None
    assert normalize_boolean(np.nan) is None

def test_parse_mdm_quantity():
    # Embedded string
    assert parse_mdm_quantity("14.9 kg", None) == 14.9
    assert parse_mdm_quantity("30.6 kg", np.nan) == 30.6

    # 50kg Bags / Sacks / Bori
    assert parse_mdm_quantity(0.5, "50kg Bags") == 25.0
    assert parse_mdm_quantity(1.0, "Bags") == 50.0
    assert parse_mdm_quantity(1.2, "Bori") == 60.0
    assert parse_mdm_quantity(0.2, "Sacks") == 10.0

    # Grams
    assert parse_mdm_quantity(25000, "Grams") == 25.0
    assert parse_mdm_quantity(10000, "g") == 10.0
    assert parse_mdm_quantity(60000, "grams") == 60.0

    # KG
    assert parse_mdm_quantity(40.5, "KG") == 40.5
    assert parse_mdm_quantity(12.0, "kg") == 12.0

def test_parse_mdm_cost():
    assert parse_mdm_cost("Rs. 1,600") == 1600.0
    assert parse_mdm_cost("₹1,317") == 1317.0
    assert parse_mdm_cost("336/-") == 336.0
    assert parse_mdm_cost(2450) == 2450.0
    assert parse_mdm_cost("4,992/-") == 4992.0
    assert np.isnan(parse_mdm_cost(None))

def test_normalize_fln_score():
    # Letter grades
    assert normalize_fln_score('A+', 'Letter Grade') == 95.0
    assert normalize_fln_score('A', 'Letter Grade') == 85.0
    assert normalize_fln_score('B', 'Letter Grade') == 75.0
    assert normalize_fln_score('C', 'Letter Grade') == 65.0
    assert normalize_fln_score('D', 'Letter Grade') == 55.0
    assert normalize_fln_score('E', 'Letter Grade') == 45.0

    # CGPA
    assert normalize_fln_score('8.5', 'CGPA') == 85.0
    assert normalize_fln_score('4.0', 'CGPA') == 40.0

    # Raw Marks
    assert normalize_fln_score('20/25', 'Raw Marks') == 80.0
    assert normalize_fln_score('45/50', 'Raw Marks') == 90.0
    assert normalize_fln_score('72/100', 'Raw Marks') == 72.0

    # Percentages
    assert normalize_fln_score('63.4%', 'Percentage') == 63.4
    assert normalize_fln_score('88.1%', 'pct') == 88.1
    assert normalize_fln_score('77.3%', '%') == 77.3

def test_parse_date_to_iso():
    # ISO and delimited formats
    assert parse_date_to_iso("2024-03-15") == "2024-03-15"
    assert parse_date_to_iso("15-03-2024") == "2024-03-15"
    assert parse_date_to_iso("2024/03/15") == "2024-03-15"
    assert parse_date_to_iso(None) is None
    assert parse_date_to_iso(np.nan) is None

    # Series handling
    series = pd.Series(["2024-01-10", "2024-02-20", None])
    res = parse_date_to_iso(series)
    assert res.iloc[0] == "2024-01-10"
    assert res.iloc[1] == "2024-02-20"
    assert pd.isna(res.iloc[2])

def test_normalize_grade():
    # Roman numeral mapping
    assert normalize_grade("I") == "1"
    assert normalize_grade("V") == "5"
    assert normalize_grade("X") == "10"
    assert normalize_grade("  IV  ") == "4"

    # Digits and unchanged strings
    assert normalize_grade("1") == "1"
    assert normalize_grade("10") == "10"
    assert normalize_grade(None) is None
    assert normalize_grade(np.nan) is None

