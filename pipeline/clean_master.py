"""
pipeline/clean_master.py
Cleaning and standardizing the School Master dataset.
"""

import os
import pandas as pd
import numpy as np
from .utils import (
    get_raw_data_dir,
    get_processed_data_dir,
    normalize_school_id,
    audit_logger
)

def clean_school_master():
    raw_dir = get_raw_data_dir()
    filepath = os.path.join(raw_dir, "track4_school_master.csv")
    df = pd.read_csv(filepath)
    raw_count = len(df)

    # 1. Deduplication
    dup_count = df.duplicated().sum()
    df = df.drop_duplicates().copy()

    # 2. Normalize School ID
    df['school_id_clean'] = df['school_id'].apply(normalize_school_id)

    # 3. Clean Text: School Name
    df['school_name_clean'] = df['school_name'].astype(str).str.strip()

    # 4. Standardize School Type
    school_type_map = {
        'primary': 'Primary',
        'Primary': 'Primary',
        'upper primary': 'Upper Primary',
        'Upper Primary': 'Upper Primary',
        'secondary': 'Secondary',
        'Secondary': 'Secondary',
        'higher secondary': 'Higher Secondary',
        'Higher Secondary': 'Higher Secondary'
    }
    df['school_type_clean'] = df['school_type'].astype(str).str.strip().map(school_type_map).fillna(df['school_type'])

    # 5. Standardize Medium
    medium_map = {
        'punjabi': 'Punjabi',
        'Punjabi': 'Punjabi',
        'hindi': 'Hindi',
        'Hindi': 'Hindi',
        'english': 'English',
        'English': 'English'
    }
    df['medium_clean'] = df['medium'].astype(str).str.strip().map(medium_map).fillna(df['medium'])

    # 6. Standardize District & Imputation
    df['district_clean'] = df['district'].dropna().astype(str).str.strip().str.title()
    df['block_clean'] = df['block'].dropna().astype(str).str.strip()

    # Create Block-to-District lookup for imputation
    block_to_dist = (
        df.dropna(subset=['district_clean', 'block_clean'])
        .groupby('block_clean')['district_clean']
        .agg(lambda s: s.mode()[0] if not s.empty else np.nan)
        .to_dict()
    )

    # Log and impute missing districts
    null_dist_mask = df['district_clean'].isnull()
    for idx, row in df[null_dist_mask].iterrows():
        sid = row['school_id_clean']
        blk = row['block_clean']
        if pd.notnull(blk) and blk in block_to_dist:
            imputed_val = block_to_dist[blk]
            df.loc[idx, 'district_clean'] = imputed_val
            audit_logger.log_issue(
                'school_master', sid, 'district', 'MISSING_VALUE_IMPUTED',
                np.nan, imputed_val, 'CORRECTED'
            )
        else:
            df.loc[idx, 'district_clean'] = 'Unassigned'
            audit_logger.log_issue(
                'school_master', sid, 'district', 'UNRESOLVED_MISSING_DISTRICT',
                np.nan, 'Unassigned', 'SUSPICIOUS'
            )

    # 7. Validate Enrollment
    df['total_enrolled_students'] = pd.to_numeric(df['total_enrolled_students'], errors='coerce').fillna(0).astype(int)

    # 8. Ensure school_id uniqueness in master
    df = df.drop_duplicates(subset=['school_id_clean']).copy()

    # Build final clean schema
    clean_df = pd.DataFrame({
        'school_id': df['school_id_clean'],
        'school_name': df['school_name_clean'],
        'district': df['district_clean'],
        'block': df['block_clean'].fillna('Unassigned'),
        'total_enrolled_students': df['total_enrolled_students'],
        'school_type': df['school_type_clean'],
        'medium': df['medium_clean']
    }).sort_values('school_id').reset_index(drop=True)

    # Audit summary
    audit_logger.record_summary(
        dataset='school_master',
        total_raw=raw_count,
        total_clean=len(clean_df),
        duplicates=dup_count,
        nulls_dict={'district_imputed': int(null_dist_mask.sum())},
        anomalies_dict={'unassigned_district': int((clean_df['district'] == 'Unassigned').sum())}
    )

    # Save to processed CSV
    out_path = os.path.join(get_processed_data_dir(), "dim_school.csv")
    clean_df.to_csv(out_path, index=False)
    print(f"[pipeline] Cleaned school master: {len(clean_df)} schools saved to {out_path}")
    return clean_df

if __name__ == '__main__':
    clean_school_master()
