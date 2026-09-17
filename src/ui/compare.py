import streamlit as st
import pandas as pd
import numpy as np

def show_comparison(original_df: pd.DataFrame, cleaned_df: pd.DataFrame):
    st.subheader("🔄 Side-by-Side Visual Diff & Audit")
    st.caption("Compare original raw data with cleaned dataset state. Modified cells are highlighted in yellow.")

    rows_before = len(original_df)
    rows_after = len(cleaned_df)
    cols_before = len(original_df.columns)
    cols_after = len(cleaned_df.columns)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Rows Before", rows_before)
    c2.metric("Rows After", rows_after, delta=rows_after - rows_before)
    c3.metric("Columns Before", cols_before)
    c4.metric("Columns After", cols_after, delta=cols_after - cols_before)

    st.divider()

    # Find common columns and sample length
    common_cols = [c for c in original_df.columns if c in cleaned_df.columns]
    sample_size = min(50, len(original_df), len(cleaned_df))

    if sample_size == 0 or not common_cols:
        st.info("No overlapping records to compare.")
        return

    # Check which cells changed in sample
    orig_sub = original_df.iloc[:sample_size][common_cols].copy()
    clean_sub = cleaned_df.iloc[:sample_size][common_cols].copy()

    # Create a boolean mask of changes
    mask = pd.DataFrame(False, index=orig_sub.index, columns=common_cols)
    for col in common_cols:
        s1 = orig_sub[col]
        s2 = clean_sub[col]
        # Diff accounting for nulls
        both_null = s1.isna() & s2.isna()
        diff = (s1.astype(str) != s2.astype(str)) & ~both_null
        mask[col] = diff

    total_changed_cells = mask.sum().sum()
    rows_with_changes = mask.any(axis=1).sum()

    st.write(f"**Sample Audit ({sample_size} rows):** Found **{total_changed_cells} modified cells** across **{rows_with_changes} rows**.")

    # Highlighting function for Streamlit dataframe
    def highlight_diff(data):
        # returns styles matching the shape of data
        styles = pd.DataFrame('', index=data.index, columns=data.columns)
        for col in common_cols:
            styles[col] = np.where(mask[col], 'background-color: rgba(234, 179, 8, 0.3); color: #fef08a; font-weight: bold;', '')
        return styles

    st.write("#### 📋 Cleaned Data with Transformation Highlights")
    st.dataframe(
        clean_sub.style.apply(highlight_diff, axis=None),
        use_container_width=True
    )

    st.caption("Highlighted cells indicate values that were cleaned, imputed, or transformed from the original state.")
