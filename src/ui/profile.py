import streamlit as st

from src.profiler import analyze_columns
from src.health import health_label


def show_profile(df, summary, health_score):

    st.success("✅ Dataset Loaded Successfully!")

    # -----------------------------------------------
    # Dataset Summary Metrics
    # -----------------------------------------------
    st.subheader("📊 Dataset Summary")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Rows",            summary["Rows"])
    col2.metric("Columns",         summary["Columns"])
    col3.metric("Missing Values",  summary["Missing Values"])
    col4.metric("Duplicate Rows",  summary["Duplicate Rows"])

    col5, col6, col7, col8 = st.columns(4)
    col5.metric("Memory (MB)",    summary["Memory Usage (MB)"])
    col6.metric("Numeric Cols",   summary["Numeric Columns"])
    col7.metric("Categorical Cols", summary["Categorical Columns"])
    col8.metric("Missing %",      f"{summary.get('Missing %', 0)}%")

    st.divider()

    # -----------------------------------------------
    # Health Score
    # -----------------------------------------------
    st.subheader("🩺 Dataset Health")

    label = health_label(health_score)

    col_score, col_label = st.columns([1, 3])
    col_score.metric("Health Score", f"{health_score} / 100")
    col_label.metric("Status", label)

    st.progress(health_score / 100)

    if health_score < 50:
        st.error(
            "⚠️ This dataset has significant quality issues. "
            "Run the **Clean** tab to fix missing values, duplicates, and outliers."
        )
    elif health_score < 75:
        st.warning(
            "🟡 This dataset has moderate quality issues. "
            "Consider running the **Clean** tab to improve accuracy."
        )
    else:
        st.success("🟢 This dataset looks healthy and ready for analysis.")

    st.divider()

    # -----------------------------------------------
    # Dataset Preview
    # -----------------------------------------------
    st.subheader("📋 Dataset Preview")
    st.caption(f"Showing first 10 of {len(df)} rows")
    st.dataframe(df.head(10), use_container_width=True)

    st.divider()

    # -----------------------------------------------
    # Column Intelligence
    # -----------------------------------------------
    st.subheader("🔍 Column Intelligence")
    st.caption(
        "Automatically detects primary keys, date columns, "
        "email/phone fields, and missing value severity."
    )

    column_report = analyze_columns(df)

    st.dataframe(
        column_report,
        use_container_width=True,
        hide_index=True
    )