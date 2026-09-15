"""
pipeline/clean_test_scores.py
Cleaning, multi-scale FLN test score normalization into percentage, and academic proficiency categorization.
"""

import os
import json
import re
import pandas as pd
import numpy as np
from .utils import (
    get_raw_data_dir,
    get_processed_data_dir,
    normalize_school_id,
    audit_logger
)

SUBJECT_MAP = {
    'Math': 'Mathematics',
    'Mathematics': 'Mathematics',
    'Ganit': 'Mathematics',
    'Science': 'Science',
    'English': 'English',
    'Hindi': 'Hindi',
    'Punjabi': 'Punjabi',
    'EVS': 'EVS'
}

LETTER_GRADE_MAP = {
    'A+': 95.0,
    'A': 85.0,
    'B': 75.0,
    'C': 65.0,
    'D': 55.0,
    'E': 45.0
}

def normalize_fln_score(raw_score, grading_scale):
    """
    Normalizes Letter Grades, CGPA, Raw Marks, and Percentages to a 0-100% scale.
    """
    if pd.isna(raw_score) or raw_score is None:
        return np.nan

    scale = str(grading_scale).strip()
    s = str(raw_score).strip()

    if scale == 'Letter Grade':
        return LETTER_GRADE_MAP.get(s, 65.0)

    elif scale in ['%', 'pct', 'Percentage']:
        cleaned = re.sub(r'[\%\s]', '', s)
        try:
            return float(cleaned)
        except ValueError:
            return np.nan

    elif scale == 'CGPA':
        try:
            return float(s) * 10.0
        except ValueError:
            return np.nan

    elif scale == 'Raw Marks':
        if '/' in s:
            parts = s.split('/')
            try:
                num = float(parts[0].strip())
                denom = float(parts[1].strip())
                return (num / denom * 100.0) if denom > 0 else np.nan
            except (ValueError, ZeroDivisionError):
                return np.nan
        else:
            try:
                return float(s)
            except ValueError:
                return np.nan

    # Fallback attempt
    try:
        cleaned = re.sub(r'[^\d\.]', '', s)
        val = float(cleaned)
        return val * 10.0 if val <= 10.0 else val
    except ValueError:
        return np.nan

def clean_test_scores():
    raw_dir = get_raw_data_dir()
    filepath = os.path.join(raw_dir, "track4_test_scores.json")
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    df = pd.DataFrame(data)
    raw_count = len(df)

    # 1. Deduplication
    dup_count = df.duplicated().sum()
    df = df.drop_duplicates().copy()

    # 2. Normalize school_id
    df['school_id_clean'] = df['school_id'].apply(normalize_school_id)

    # 3. Parse Dates
    parsed_dates = pd.to_datetime(df['date'], format='mixed', errors='coerce')
    df['assessment_date'] = parsed_dates.dt.strftime('%Y-%m-%d')

    # 4. Standardize Subject
    df['subject_clean'] = df['subject'].astype(str).str.strip().map(SUBJECT_MAP).fillna(df['subject'])

    # 5. Standardize Score to Percentage (0 to 100)
    df['score_percentage'] = [
        normalize_fln_score(score, scale)
        for score, scale in zip(df['avg_score'], df['grading_scale'])
    ]
    df['score_percentage'] = df['score_percentage'].round(2)

    # 6. Academic Proficiency Tier
    conditions = [
        df['score_percentage'] >= 75.0,
        (df['score_percentage'] >= 60.0) & (df['score_percentage'] < 75.0),
        (df['score_percentage'] >= 45.0) & (df['score_percentage'] < 60.0),
        df['score_percentage'] < 45.0
    ]
    choices = [
        'Distinction (Level 4)',
        'Proficient (Level 3)',
        'Basic (Level 2)',
        'Below Basic (Level 1)'
    ]
    df['proficiency_tier'] = np.select(conditions, choices, default='Unclassified')

    # 7. Total Students Assessed
    df['total_students_assessed'] = pd.to_numeric(df['total_students_assessed'], errors='coerce').fillna(0).astype(int)

    clean_df = pd.DataFrame({
        'assessment_id': df['assessment_id'].astype(str).str.strip(),
        'assessment_date': df['assessment_date'],
        'school_id': df['school_id_clean'],
        'grade': df['grade'].astype(str).str.strip(),
        'subject': df['subject_clean'],
        'original_scale': df['grading_scale'].astype(str).str.strip(),
        'original_score': df['avg_score'].astype(str).str.strip(),
        'max_marks': df['max_marks'].astype(str).str.strip(),
        'score_percentage': df['score_percentage'],
        'proficiency_tier': df['proficiency_tier'],
        'total_students_assessed': df['total_students_assessed']
    }).sort_values(['assessment_date', 'school_id']).reset_index(drop=True)

    audit_logger.record_summary(
        dataset='test_scores',
        total_raw=raw_count,
        total_clean=len(clean_df),
        duplicates=dup_count,
        nulls_dict={'unparseable_scores': int(clean_df['score_percentage'].isnull().sum())},
        anomalies_dict={
            'average_fln_percentage': float(clean_df['score_percentage'].mean()),
            'below_basic_count': int((clean_df['proficiency_tier'] == 'Below Basic (Level 1)').sum())
        }
    )

    out_path = os.path.join(get_processed_data_dir(), "fct_test_scores.csv")
    clean_df.to_csv(out_path, index=False)
    print(f"[pipeline] Cleaned test scores: {len(clean_df)} assessments saved to {out_path}")
    return clean_df

if __name__ == '__main__':
    clean_test_scores()
