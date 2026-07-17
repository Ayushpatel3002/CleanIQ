import streamlit as st

from src.profiler import analyze_columns


def show_profile(df, summary, health_score):

    st.success("Dataset Loaded Successfully!")

    st.subheader("📊 Dataset Summary")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Rows", summary["Rows"])
    col2.metric("Columns", summary["Columns"])
    col3.metric("Missing Values", summary["Missing Values"])
    col4.metric("Duplicate Rows", summary["Duplicate Rows"])

    col5, col6, col7, col8 = st.columns(4)

    col5.metric("Memory (MB)", summary["Memory Usage (MB)"])
    col6.metric("Numeric", summary["Numeric Columns"])
    col7.metric("Categorical", summary["Categorical Columns"])
    col8.metric("Datetime", summary["Datetime Columns"])

    st.divider()

    st.subheader("🩺 Dataset Health")

    st.metric(
        "Health Score",
        f"{health_score}/100"
    )

    st.progress(health_score / 100)

    st.divider()

    st.subheader("📋 Dataset Preview")

    st.dataframe(
        df.head(10),
        use_container_width=True
    )

    st.divider()

    st.subheader("🔍 Column Intelligence")

    column_report = analyze_columns(df)

    st.dataframe(
        column_report,
        use_container_width=True
    )