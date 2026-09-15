"""
dashboard/components/filters.py
Sidebar filters component for the Streamlit dashboard.
"""

import streamlit as st
import pandas as pd

def render_sidebar_filters(df_schools: pd.DataFrame):
    st.sidebar.markdown("### 🔍 Global Analytical Filters")

    # 1. District filter
    all_districts = sorted(df_schools['district'].dropna().unique().tolist())
    selected_districts = st.sidebar.multiselect(
        "Select Districts",
        options=all_districts,
        default=[]
    )

    # 2. School Type filter
    all_types = sorted(df_schools['school_type'].dropna().unique().tolist())
    selected_types = st.sidebar.multiselect(
        "School Category",
        options=all_types,
        default=[]
    )

    # 3. Medium filter
    all_mediums = sorted(df_schools['medium'].dropna().unique().tolist())
    selected_mediums = st.sidebar.multiselect(
        "Medium of Instruction",
        options=all_mediums,
        default=[]
    )

    filtered_df = df_schools.copy()
    if selected_districts:
        filtered_df = filtered_df[filtered_df['district'].isin(selected_districts)]
    if selected_types:
        filtered_df = filtered_df[filtered_df['school_type'].isin(selected_types)]
    if selected_mediums:
        filtered_df = filtered_df[filtered_df['medium'].isin(selected_mediums)]

    active_filters = {
        'districts': selected_districts,
        'types': selected_types,
        'mediums': selected_mediums
    }

    st.sidebar.markdown("---")
    st.sidebar.markdown(f"**Schools Selected:** `{len(filtered_df):,} / {len(df_schools):,}`")

    return filtered_df, active_filters
