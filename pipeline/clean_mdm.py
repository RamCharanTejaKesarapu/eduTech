"""
pipeline/clean_mdm.py
Cleaning, standardizing grain quantities into KG, parsing currency, and resolving vendor syndicates.
"""

import os
import re
import pandas as pd
import numpy as np
from .utils import (
    get_raw_data_dir,
    get_processed_data_dir,
    normalize_school_id,
    audit_logger
)

VENDOR_CANONICAL_MAP = {
    'sharma traders pvt ltd': 'Sharma Traders',
    'Sharma Traders': 'Sharma Traders',
    'Sharma & Sons': 'Sharma & Sons',
    'goyal mill': 'Goyal Rice Mill',
    'Goyal Rice Mill': 'Goyal Rice Mill',
    'Goyal Enterprises': 'Goyal Enterprises',
    'kumar general store': 'Kumar General Store',
    'Kumar Supplies': 'Kumar Supplies',
    'Kumar & Co.': 'Kumar & Co.',
    'Singh Brothers': 'Singh Brothers',
    'Singh Agro': 'Singh Agro',
    'S. Agro Works': 'S. Agro Works'
}

VENDOR_GROUP_MAP = {
    'Sharma Traders': 'Sharma Group',
    'Sharma & Sons': 'Sharma Group',
    'Goyal Rice Mill': 'Goyal Group',
    'Goyal Enterprises': 'Goyal Group',
    'Kumar General Store': 'Kumar Group',
    'Kumar Supplies': 'Kumar Supplies Group',
    'Kumar & Co.': 'Kumar Group',
    'Singh Brothers': 'Singh Group',
    'Singh Agro': 'Singh Group',
    'S. Agro Works': 'Singh Group'
}

GRAIN_MAP = {
    'RICE': 'Rice',
    'Rice': 'Rice',
    'Chawal': 'Rice',
    'chawal': 'Rice',
    'WHEAT': 'Wheat',
    'Wheat': 'Wheat',
    'gehun': 'Wheat',
    'Gehun': 'Wheat',
    'Atta': 'Wheat',
    'Sarson Tel': 'Mustard Oil',
    'Mustard Oil': 'Mustard Oil',
    'Cooking Oil': 'Mustard Oil',
    'Oil': 'Mustard Oil',
    'Pulses': 'Pulses / Dal',
    'dal': 'Pulses / Dal',
    'Daal': 'Pulses / Dal',
    'Dal': 'Pulses / Dal',
    'Lentils': 'Pulses / Dal'
}

PAYMENT_MAP = {
    'Paid': 'PAID',
    'paid': 'PAID',
    'Cleared': 'PAID',
    'Due': 'DUE',
    'Pending': 'PENDING',
    'PENDING': 'PENDING'
}

def parse_mdm_quantity(raw_qty, raw_unit):
    """
    Parses and standardizes all MDM grain quantities into Kilograms (KG).
    - Embedded strings like '14.9 kg' -> 14.9
    - Grams / g -> qty / 1000.0
    - Sacks / Bags / Bori -> qty * 50.0
    - Direct KG / Kgs -> qty
    """
    if pd.isna(raw_qty) or raw_qty is None:
        return np.nan

    # Check for embedded unit string
    if isinstance(raw_qty, str):
        s = raw_qty.strip()
        match = re.search(r"([\d\.]+)", s)
        if match:
            return float(match.group(1))
        return np.nan

    # Numeric quantity
    try:
        val = float(raw_qty)
    except (ValueError, TypeError):
        return np.nan

    unit_str = str(raw_unit).strip() if pd.notnull(raw_unit) else ''
    
    if unit_str in ['Grams', 'grams', 'g']:
        return val / 1000.0
    elif unit_str in ['50kg Bags', 'Bags', 'Bori', 'Sacks', 'bags']:
        return val * 50.0
    else:
        # Default or KG / kg / Kgs / KGS
        return val

def parse_mdm_cost(raw_cost):
    """
    Strips currency symbols (₹, Rs.), commas, slashes, and whitespace into float.
    """
    if pd.isna(raw_cost) or raw_cost is None:
        return np.nan
    s = str(raw_cost).strip()
    s = re.sub(r"[Rs\.\₹\,\/\-\s]", "", s)
    try:
        return float(s)
    except (ValueError, TypeError):
        return np.nan

def clean_mid_day_meal():
    raw_dir = get_raw_data_dir()
    filepath = os.path.join(raw_dir, "track4_mid_day_meal_procurement.xlsx")
    df = pd.read_excel(filepath)
    raw_count = len(df)

    # 1. Deduplication
    dup_count = df.duplicated().sum()
    df = df.drop_duplicates().copy()

    # 2. Normalize school_id
    df['school_id_clean'] = df['school_id'].apply(normalize_school_id)

    # 3. Parse Dates
    parsed_dates = pd.to_datetime(df['date'], format='mixed', errors='coerce')
    df['procurement_date'] = parsed_dates.dt.strftime('%Y-%m-%d')
    df['day_of_week'] = parsed_dates.dt.day_name()
    df['is_sunday_procurement'] = (df['day_of_week'] == 'Sunday').astype(int)

    # 4. Standardize Vendor
    df['vendor_name_clean'] = df['vendor_name'].astype(str).str.strip().map(VENDOR_CANONICAL_MAP).fillna(df['vendor_name'])
    df['vendor_group'] = df['vendor_name_clean'].map(VENDOR_GROUP_MAP).fillna('Other Vendors')

    # 5. Standardize Grain
    df['food_category'] = df['grain_type'].astype(str).str.strip().map(GRAIN_MAP).fillna('Other Staple')

    # 6. Parse and Standardize Quantity into KG
    df['quantity_kg'] = [
        parse_mdm_quantity(q, u)
        for q, u in zip(df['quantity'], df['unit'])
    ]
    df['quantity_kg'] = df['quantity_kg'].round(3)

    # 7. Clean Total Cost
    df['total_cost_inr'] = df['total_cost'].apply(parse_mdm_cost).round(2)

    # Calculate unit cost per kg where both cost and qty exist
    df['cost_per_kg'] = np.where(
        (df['quantity_kg'] > 0) & (df['total_cost_inr'].notnull()),
        df['total_cost_inr'] / df['quantity_kg'],
        np.nan
    ).round(2)

    # 8. Standardize Payment Status
    df['payment_status_clean'] = df['payment_status'].dropna().astype(str).str.strip().map(PAYMENT_MAP).fillna('PENDING')

    # Build clean table
    clean_df = pd.DataFrame({
        'procurement_id': df['procurement_id'].astype(str).str.strip(),
        'procurement_date': df['procurement_date'],
        'day_of_week': df['day_of_week'],
        'is_sunday_procurement': df['is_sunday_procurement'],
        'school_id': df['school_id_clean'],
        'vendor_name': df['vendor_name_clean'],
        'vendor_group': df['vendor_group'],
        'food_category': df['food_category'],
        'raw_grain_type': df['grain_type'].astype(str).str.strip(),
        'quantity_kg': df['quantity_kg'],
        'total_cost_inr': df['total_cost_inr'],
        'cost_per_kg': df['cost_per_kg'],
        'payment_status': df['payment_status_clean']
    }).sort_values(['procurement_date', 'school_id']).reset_index(drop=True)

    # Create Dimension Table: dim_vendor
    vendor_df = clean_df[['vendor_name', 'vendor_group']].drop_duplicates().sort_values('vendor_name').reset_index(drop=True)
    vendor_df['vendor_id'] = [f"VND{i:03d}" for i in range(1, len(vendor_df) + 1)]
    vendor_df = vendor_df[['vendor_id', 'vendor_name', 'vendor_group']]

    audit_logger.record_summary(
        dataset='mid_day_meal',
        total_raw=raw_count,
        total_clean=len(clean_df),
        duplicates=dup_count,
        nulls_dict={
            'null_quantity': int(clean_df['quantity_kg'].isnull().sum()),
            'null_cost': int(clean_df['total_cost_inr'].isnull().sum())
        },
        anomalies_dict={
            'sunday_procurement_count': int(clean_df['is_sunday_procurement'].sum()),
            'total_spend_inr': float(clean_df['total_cost_inr'].sum()),
            'total_volume_kg': float(clean_df['quantity_kg'].sum())
        }
    )

    proc_dir = get_processed_data_dir()
    out_path = os.path.join(proc_dir, "fct_mdm_procurement.csv")
    vendor_path = os.path.join(proc_dir, "dim_vendor.csv")
    clean_df.to_csv(out_path, index=False)
    vendor_df.to_csv(vendor_path, index=False)
    print(f"[pipeline] Cleaned MDM: {len(clean_df)} procurements saved to {out_path}")
    print(f"[pipeline] Created vendor dimension: {len(vendor_df)} vendors saved to {vendor_path}")
    return clean_df, vendor_df

if __name__ == '__main__':
    clean_mid_day_meal()
