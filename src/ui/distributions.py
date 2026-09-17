import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

def show_distributions(df: pd.DataFrame):
    st.subheader("📈 Interactive Data Distributions & Skewness")
    st.caption("Inspect statistical spreads, frequency bins, outlier tails, and category balances.")

    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    categorical_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()

    all_cols = df.columns.tolist()
    if not all_cols:
        st.info("No columns available to plot.")
        return

    selected_col = st.selectbox(
        "🎯 Select Column to Analyze Distribution:",
        options=all_cols,
        index=0
    )

    series = df[selected_col]
    non_null = series.dropna()

    if len(non_null) == 0:
        st.warning(f"Column '{selected_col}' contains only null values.")
        return

    if pd.api.types.is_numeric_dtype(series):
        # Numeric Column: Stats & Histogram
        skew_val = float(non_null.skew()) if len(non_null) > 2 else 0.0
        mean_val = float(non_null.mean())
        median_val = float(non_null.median())
        is_skewed = abs(skew_val) > 1.0

        # Stats Cards
        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("Min", round(float(non_null.min()), 2))
        c2.metric("Mean", round(mean_val, 2))
        c3.metric("Median", round(median_val, 2))
        c4.metric("Max", round(float(non_null.max()), 2))
        c5.metric("Skewness", round(skew_val, 2), delta="Skewed" if is_skewed else "Normal", delta_color="inverse" if is_skewed else "normal")

        if is_skewed:
            st.warning(f"⚠️ **High Skewness Detected ({round(skew_val, 2)})**: The mean deviates from the median due to extreme values or long tails. Imputing with **Median** is strongly recommended.")
        else:
            st.success(f"✅ **Symmetric Distribution ({round(skew_val, 2)})**: Values are relatively well-balanced. Imputing with **Mean** is safe.")

        # Plotly Histogram with Mean and Median lines
        fig = px.histogram(
            df,
            x=selected_col,
            nbins=min(25, max(5, non_null.nunique())),
            title=f"Histogram Frequency Distribution for '{selected_col}'",
            color_discrete_sequence=["#6366f1"]
        )
        fig.add_vline(x=mean_val, line_dash="dash", line_color="#ef4444", annotation_text=f"Mean: {round(mean_val, 1)}", annotation_position="top right")
        fig.add_vline(x=median_val, line_dash="dash", line_color="#10b981", annotation_text=f"Median: {round(median_val, 1)}", annotation_position="top left")
        fig.update_layout(
            template="plotly_dark",
            margin=dict(l=20, r=20, t=40, b=20),
            height=380
        )
        st.plotly_chart(fig, use_container_width=True)

    else:
        # Categorical Column: Frequency Bar Chart
        top_counts = non_null.astype(str).value_counts().head(12).reset_index()
        top_counts.columns = ["Category", "Count"]

        c1, c2 = st.columns([1, 2])
        with c1:
            st.metric("Unique Categories", non_null.nunique())
            st.dataframe(top_counts, use_container_width=True, hide_index=True)

        with c2:
            fig = px.bar(
                top_counts,
                x="Count",
                y="Category",
                orientation="h",
                title=f"Top Categories Frequency in '{selected_col}'",
                color="Count",
                color_continuous_scale="Viridis"
            )
            fig.update_layout(
                template="plotly_dark",
                yaxis=dict(autorange="reversed"),
                margin=dict(l=20, r=20, t=40, b=20),
                height=380
            )
            st.plotly_chart(fig, use_container_width=True)
