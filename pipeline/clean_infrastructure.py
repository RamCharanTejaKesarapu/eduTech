"""
pipeline/clean_infrastructure.py
Cleaning, standardizing 22-boolean representations, and scoring school infrastructure.
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

AMENITY_COLS = [
    'has_electricity',
    'has_drinking_water',
    'has_functional_toilet',
    'has_boundary_wall',
    'has_playground'
]

def clean_school_infrastructure():
    raw_dir = get_raw_data_dir()
    filepath = os.path.join(raw_dir, "track4_school_infrastructure.csv")
    df = pd.read_csv(filepath)
    raw_count = len(df)

    # 1. Deduplication
    dup_count = df.duplicated().sum()
    df = df.drop_duplicates().copy()

    # 2. Normalize school_id
    df['school_id_clean'] = df['school_id'].apply(normalize_school_id)

    # 3. Parse Dates
    df['inspection_date'] = parse_date_to_iso(df['date'])

    # 4. Standardize Booleans
    boolean_clean_cols = {}
    null_counts = {}
    for col in AMENITY_COLS:
        clean_col = f"{col}_clean"
        df[clean_col] = df[col].apply(normalize_boolean)
        boolean_clean_cols[col] = clean_col
        null_counts[col] = int(df[clean_col].isnull().sum())

    # 5. Calculate Infrastructure Quality Score (0 to 100)
    # Average of available amenities * 100
    clean_col_names = list(boolean_clean_cols.values())
    df['amenities_functional_count'] = df[clean_col_names].sum(axis=1)
    df['amenities_evaluated_count'] = df[clean_col_names].notnull().sum(axis=1)

    df['infra_score'] = np.where(
        df['amenities_evaluated_count'] > 0,
        (df['amenities_functional_count'] / df['amenities_evaluated_count']) * 100.0,
        np.nan
    ).round(2)

    df['infra_deficit_index'] = (100.0 - df['infra_score']).round(2)

    # 6. Clean Text: Remarks & Inspector
    df['inspector_name_clean'] = df['inspector_name'].fillna('Unrecorded').astype(str).str.strip()
    df['remarks_clean'] = df['remarks'].fillna('No remarks').astype(str).str.strip()

    clean_df = pd.DataFrame({
        'inspection_id': df['inspection_id'].astype(str).str.strip(),
        'inspection_date': df['inspection_date'],
        'school_id': df['school_id_clean'],
        'has_electricity': df['has_electricity_clean'],
        'has_drinking_water': df['has_drinking_water_clean'],
        'has_functional_toilet': df['has_functional_toilet_clean'],
        'has_boundary_wall': df['has_boundary_wall_clean'],
        'has_playground': df['has_playground_clean'],
        'infra_score': df['infra_score'],
        'infra_deficit_index': df['infra_deficit_index'],
        'inspector_name': df['inspector_name_clean'],
        'remarks': df['remarks_clean']
    }).sort_values(['inspection_date', 'school_id']).reset_index(drop=True)

    audit_logger.record_summary(
        dataset='school_infrastructure',
        total_raw=raw_count,
        total_clean=len(clean_df),
        duplicates=dup_count,
        nulls_dict=null_counts,
        anomalies_dict={
            'average_infra_score': float(clean_df['infra_score'].mean()),
            'schools_zero_score': int((clean_df['infra_score'] == 0).sum())
        }
    )

    out_path = os.path.join(get_processed_data_dir(), "fct_infrastructure.csv")
    clean_df.to_csv(out_path, index=False)
    print(f"[pipeline] Cleaned infrastructure: {len(clean_df)} inspections saved to {out_path}")
    return clean_df

if __name__ == '__main__':
    clean_school_infrastructure()
