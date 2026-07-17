import streamlit as st
import io

import pandas as pd

from src.exporter import export_to_mysql

def show_export():

    st.subheader("💾 Export Data")

    if "cleaned_df" not in st.session_state:

        st.info("🧹 Run the cleaning pipeline first.")

        return

    cleaned_df = st.session_state["cleaned_df"]

    # -----------------------------------
    # CSV Download
    # -----------------------------------

    csv = cleaned_df.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="📥 Download Cleaned CSV",
        data=csv,
        file_name="cleaned_dataset.csv",
        mime="text/csv",
        use_container_width=True
    )

    # -----------------------------------
    # Excel Download
    # -----------------------------------

    excel_buffer = io.BytesIO()

    with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:

        cleaned_df.to_excel(
            writer,
            index=False,
            sheet_name="Cleaned Data"
        )

    st.download_button(
        label="📥 Download Cleaned Excel",
        data=excel_buffer.getvalue(),
        file_name="cleaned_dataset.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True
    )

    st.divider()

    st.subheader("🗄 Export to MySQL")

    host = st.text_input(
    "Host",
    value="localhost"
)

    user = st.text_input(
    "Username"
)

    password = st.text_input(
    "Password",
    type="password"
)

    database = st.text_input(
    "Database"
)

    table_name = st.text_input(
    "Table Name",
    value="cleaned_data"
)

    if st.button(
        "🚀 Export to MySQL",
        use_container_width=True
    ):

        try:

            rows = export_to_mysql(
                cleaned_df,
                host,
                user,
                password,
                database,
                table_name
            )

            st.success(
                f"Successfully exported {rows} rows!"
            )

        except Exception as e:

            st.error(str(e))