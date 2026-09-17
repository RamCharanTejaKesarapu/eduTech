"""
tests/test_dashboard_filters.py
Unit tests for dashboard filter components and DataFrame slicing logic.
"""

import pandas as pd
import pytest
from dashboard.components.filters import filter_school_dataframe, is_filter_active

@pytest.fixture
def sample_schools():
    return pd.DataFrame({
        'school_id': ['SCH0001', 'SCH0002', 'SCH0003', 'SCH0004'],
        'school_name': ['Govt High Patiala', 'Govt Primary Ludhiana', 'Govt Sr Sec Moga', 'Model School Patiala'],
        'district': ['Patiala', 'Ludhiana', 'Moga', 'Patiala'],
        'school_type': ['High', 'Primary', 'Higher Secondary', 'Primary'],
        'medium': ['Punjabi', 'English', 'Hindi', 'Punjabi']
    })

def test_filter_by_district(sample_schools):
    res = filter_school_dataframe(sample_schools, districts=['Patiala'])
    assert len(res) == 2
    assert set(res['district']) == {'Patiala'}

def test_filter_by_multiple_criteria(sample_schools):
    res = filter_school_dataframe(
        sample_schools,
        districts=['Patiala'],
        types=['Primary']
    )
    assert len(res) == 1
    assert res.iloc[0]['school_name'] == 'Model School Patiala'

def test_filter_no_matches(sample_schools):
    res = filter_school_dataframe(sample_schools, districts=['NonExistent'])
    assert len(res) == 0

def test_filter_empty_leaves_unchanged(sample_schools):
    res = filter_school_dataframe(sample_schools)
    assert len(res) == len(sample_schools)

def test_is_filter_active():
    assert not is_filter_active({'districts': [], 'types': [], 'mediums': []})
    assert is_filter_active({'districts': ['Patiala'], 'types': [], 'mediums': []})
    assert is_filter_active({'districts': [], 'types': ['Primary'], 'mediums': []})
