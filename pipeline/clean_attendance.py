"""
pipeline/clean_attendance.py
Cleaning, validating, and anomaly-flagging student attendance records.
"""

import os
import pandas as pd
import numpy as np
from .utils import (
    get_raw_data_dir,
    get_processed_data_dir,
    normalize_school_id,
    normalize_boolean,
    parse_date_to_iso,
    audit_logger
)

ROMAN_TO_INT_GRADE = {
    'I': '1', 'II': '2', 'III': '3', 'IV': '4', 'V': '5',
    'VI': '6', 'VII': '7', 'VIII': '8', 'IX': '9', 'X': '10',
    '1': '1', '2': '2', '3': '3', '4': '4', '5': '5',
    '6': '6', '7': '7', '8': '8', '9': '9', '10': '10'
}

def clean_student_attendance():
    raw_dir = get_raw_data_dir()
    filepath = os.path.join(raw_dir, "track4_student_attendance.csv")
    df = pd.read_csv(filepath)
    raw_count = len(df)

    # 1. Deduplication
    dup_count = df.duplicated().sum()
    df = df.drop_duplicates().copy()

    # 2. Impute missing record_id
    null_record_ids = df['record_id'].isnull().sum()
    missing_rec_mask = df['record_id'].isnull()
    imputed_rec_ids = [f"ATT_GEN_{i:06d}" for i in range(1, missing_rec_mask.sum() + 1)]
    df.loc[missing_rec_mask, 'record_id'] = imputed_rec_ids

    # 3. Normalize school_id
    df['school_id_clean'] = df['school_id'].apply(normalize_school_id)

    # 4. Parse Dates & Day of Week
    parsed_dates = pd.to_datetime(df['date'], format='mixed', errors='coerce')
    df['attendance_date'] = parsed_dates.dt.strftime('%Y-%m-%d')
    df['day_of_week'] = parsed_dates.dt.day_name()
    df['is_sunday'] = df['day_of_week'] == 'Sunday'

    # 5. Normalize Grade
    df['grade_clean'] = df['grade'].astype(str).str.strip().map(ROMAN_TO_INT_GRADE).fillna(df['grade'].astype(str).str.strip())

    # 6. Numeric Counts & Validation
    df['total_students'] = pd.to_numeric(df['total_students'], errors='coerce').fillna(0).astype(int)
    df['present_students'] = pd.to_numeric(df['present_students'], errors='coerce').fillna(0).astype(int)

    # 7. Anomaly Flags
    # Overflow anomaly: present > total
    df['is_attendance_overflow'] = df['present_students'] > df['total_students']

    # Proxy fraud: 100% attendance on Sunday
    df['is_proxy_attendance'] = df['is_sunday'] & (df['present_students'] == df['total_students'])

    # Attendance Rate calculation
    df['attendance_rate_raw'] = np.where(
        df['total_students'] > 0,
        df['present_students'] / df['total_students'],
        0.0
    )
    df['attendance_rate_capped'] = np.minimum(df['attendance_rate_raw'], 1.0)

    # Classification status
    conditions = [
        df['is_proxy_attendance'],
        df['is_attendance_overflow'],
        df['is_sunday'],
    ]
    choices = [
        'SUSPICIOUS_PROXY',
        'INVALID_OVERFLOW',
        'SUSPICIOUS_SUNDAY'
    ]
    df['quality_status'] = np.select(conditions, choices, default='VALID')

    # Log anomalies into audit
    for _, row in df[df['is_proxy_attendance']].head(10).iterrows():
        audit_logger.log_issue(
            'student_attendance', row['record_id'], 'present_students',
            'PROXY_ATTENDANCE_SUNDAY_100PCT',
            f"Date: {row['attendance_date']}, Present: {row['present_students']}/{row['total_students']}",
            'Flagged as SUSPICIOUS_PROXY', 'SUSPICIOUS'
        )

    for _, row in df[df['is_attendance_overflow']].head(10).iterrows():
        audit_logger.log_issue(
            'student_attendance', row['record_id'], 'present_students',
            'OVERFLOW_PRESENT_EXCEEDS_TOTAL',
            f"Present: {row['present_students']} > Total: {row['total_students']}",
            'Flagged as INVALID_OVERFLOW', 'INVALID'
        )

    # 8. Normalize Teacher Present (Boolean)
    df['teacher_present_bool'] = df['teacher_present'].apply(normalize_boolean)

    # 9. Standardize Marked By
    marked_by_map = {
        'HM': 'Headmaster',
        'Headmaster': 'Headmaster',
        'Class Teacher': 'Class Teacher',
        'Admin': 'Admin',
        'Clerk': 'Clerk'
    }
    df['marked_by_clean'] = df['marked_by'].dropna().astype(str).str.strip().map(marked_by_map).fillna(df['marked_by'].fillna('Unrecorded'))

    clean_df = pd.DataFrame({
        'record_id': df['record_id'],
        'attendance_date': df['attendance_date'],
        'day_of_week': df['day_of_week'],
        'school_id': df['school_id_clean'],
        'grade': df['grade_clean'],
        'total_students': df['total_students'],
        'present_students': df['present_students'],
        'attendance_rate_raw': df['attendance_rate_raw'].round(4),
        'attendance_rate_capped': df['attendance_rate_capped'].round(4),
        'teacher_present': df['teacher_present_bool'],
        'marked_by': df['marked_by_clean'],
        'is_sunday': df['is_sunday'].astype(int),
        'is_proxy_attendance': df['is_proxy_attendance'].astype(int),
        'is_attendance_overflow': df['is_attendance_overflow'].astype(int),
        'quality_status': df['quality_status']
    }).sort_values(['attendance_date', 'school_id']).reset_index(drop=True)

    audit_logger.record_summary(
        dataset='student_attendance',
        total_raw=raw_count,
        total_clean=len(clean_df),
        duplicates=dup_count,
        nulls_dict={'missing_record_ids': int(null_record_ids)},
        anomalies_dict={
            'proxy_fraud_count': int(df['is_proxy_attendance'].sum()),
            'overflow_count': int(df['is_attendance_overflow'].sum()),
            'sunday_records_count': int(df['is_sunday'].sum())
        }
    )

    out_path = os.path.join(get_processed_data_dir(), "fct_attendance.csv")
    clean_df.to_csv(out_path, index=False)
    print(f"[pipeline] Cleaned attendance: {len(clean_df)} records saved to {out_path}")
    return clean_df

if __name__ == '__main__':
    clean_student_attendance()
