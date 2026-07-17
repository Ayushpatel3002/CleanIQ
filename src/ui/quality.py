import streamlit as st
import pandas as pd


def show_quality():

    st.subheader("🔍 Data Quality Assessment")

    if "quality_report" not in st.session_state:

        st.info("🧹 Run the cleaning pipeline first.")

        return

    quality_report = st.session_state["quality_report"]

    validation_report = []

    # -----------------------------
    # Loop through every validation
    # -----------------------------
    for check_name, report in quality_report.items():

        for column, findings in report.items():

            validation_report.append({

                "Check": check_name,

                "Column": column,

                "Findings": findings

            })

    validation_df = pd.DataFrame(validation_report)

    st.dataframe(
        validation_df,
        use_container_width=True,
        hide_index=True
    )