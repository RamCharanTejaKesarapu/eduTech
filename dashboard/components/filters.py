"""
dashboard/components/filters.py
Sidebar filters component for the Streamlit dashboard.
"""

from typing import Tuple, Dict, List, Any, Optional
import streamlit as st
import pandas as pd

def filter_school_dataframe(
    df: pd.DataFrame,
    districts: Optional[List[str]] = None,
    types: Optional[List[str]] = None,
    mediums: Optional[List[str]] = None
) -> pd.DataFrame:
    """
    Applies multi-dimensional analytical filters across school master dataset.
    """
    filtered = df.copy()
    if districts:
        filtered = filtered[filtered['district'].isin(districts)]
    if types:
        filtered = filtered[filtered['school_type'].isin(types)]
    if mediums:
        filtered = filtered[filtered['medium'].isin(mediums)]
    return filtered

def is_filter_active(active_filters: Dict[str, Any]) -> bool:
    """
    Returns True if any filter criteria (districts, types, mediums) has selections.
    """
    return any(bool(v) for v in active_filters.values())

def render_sidebar_filters(df_schools: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Any]]:
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

    active_filters = {
        'districts': selected_districts,
        'types': selected_types,
        'mediums': selected_mediums
    }

    filtered_df = filter_school_dataframe(
        df_schools,
        districts=selected_districts,
        types=selected_types,
        mediums=selected_mediums
    )

    st.sidebar.markdown("---")
    filter_status = "*(Filtered)*" if is_filter_active(active_filters) else "*(All)*"
    st.sidebar.markdown(f"**Schools Selected:** `{len(filtered_df):,} / {len(df_schools):,}` {filter_status}")

    sidebar_html = [
        '<div style="background: rgba(253, 251, 247, 0.95); border: 1px solid rgba(43, 39, 33, 0.12); border-left: 3px solid #b8332a; border-radius: 8px; padding: 14px; margin-top: 15px; box-shadow: 0 2px 8px rgba(43, 39, 33, 0.04);">',
        '<div style="font-family: var(--font); font-size: 9.5px; letter-spacing: 0.14em; color: #b8332a; text-transform: uppercase; font-weight: 700; margin-bottom: 4px;">06 — The Architect 創造主</div>',
        '<div style="font-family: var(--font-display); font-size: 18px; color: #2b2721; font-weight: 400; margin-bottom: 2px;">Ram Charan Teja</div>',
        '<div style="font-family: var(--font); font-size: 11px; color: #6e6659; margin-bottom: 8px;"><code>@LUN0895</code> • ✉ luno97802@gmail.com</div>',
        '<div style="font-family: var(--font); font-size: 11px; color: #5a5348; line-height: 1.45; margin-bottom: 12px;">Full-Stack AI Systems Architect & Data Engineer. Sole creator of the EduTech platform.</div>',
        '<a href="https://github.com/RamCharanTejaKesarapu/eduTech" target="_blank" style="display: block; text-align: center; background: #2b2721; color: #fdfbf7; font-size: 10.5px; font-weight: 600; padding: 7px 10px; border-radius: 4px; text-decoration: none; letter-spacing: 0.04em;">VIEW CREATOR REPO ↗</a>',
        '</div>'
    ]
    st.sidebar.markdown("".join(sidebar_html), unsafe_allow_html=True)

    return filtered_df, active_filters
