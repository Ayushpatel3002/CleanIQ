import streamlit as st
import pandas as pd

from src.pipeline import run_pipeline


  

def show_cleaning(df):

    st.subheader("🧹 Clean Dataset")

    if st.button("🧹 Run Cleaning", use_container_width=True):

        
        results = run_pipeline(df)

        cleaned_df = results["cleaned_df"]
        report = results["cleaning_report"]
        quality_report = results["quality_report"]

        st.session_state["cleaned_df"] = cleaned_df
        st.session_state["cleaning_report"] = report
        st.session_state["quality_report"] = quality_report
        st.success("Cleaning Pipeline Executed Successfully!")


        report_df = pd.DataFrame(
            report.items(),
            columns=["Cleaning Step", "Result"]
        )

        st.subheader("📊 Cleaning Pipeline Report")

        st.dataframe(
            report_df,
            use_container_width=True,
            hide_index=True
        )

        st.subheader("📋 Cleaned Dataset Preview")

        st.dataframe(
            cleaned_df.head(10),
            use_container_width=True
        )