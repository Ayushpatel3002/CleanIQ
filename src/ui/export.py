import streamlit as st
import io
import pandas as pd
from src.exporter import export_to_mysql
from src.health import calculate_health_score
from src.profiler import dataset_summary
from backend.services.pdf_report import generate_pdf_report
from src.validator import (
    detect_outliers,
    detect_invalid_emails,
    detect_phone_numbers,
    detect_category_inconsistency,
    detect_constant_columns
)

def show_export():
    st.subheader("💾 Export & Production Integration Hub")
    st.caption("Export publication-ready data in CSV, Excel, JSON formats or download an Executive PDF Audit Report.")

    if "cleaned_df" not in st.session_state:
        st.info("🧹 Run the cleaning pipeline or smart remediation first.")
        return

    cleaned_df = st.session_state["cleaned_df"]
    fix_log = st.session_state.get("fix_log", [])

    st.write("### 📥 Direct File Downloads")
    c1, c2, c3, c4 = st.columns(4)

    # 1. CSV Download
    with c1:
        csv_bytes = cleaned_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 Download CSV",
            data=csv_bytes,
            file_name="cleaned_dataset.csv",
            mime="text/csv",
            use_container_width=True
        )

    # 2. Excel Download
    with c2:
        excel_buffer = io.BytesIO()
        with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:
            cleaned_df.to_excel(writer, index=False, sheet_name="CleanedData")
        st.download_button(
            label="📥 Download Excel (.xlsx)",
            data=excel_buffer.getvalue(),
            file_name="cleaned_dataset.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )

    # 3. JSON Download
    with c3:
        json_str = cleaned_df.to_json(orient="records", indent=2)
        st.download_button(
            label="📥 Download JSON",
            data=json_str.encode("utf-8"),
            file_name="cleaned_dataset.json",
            mime="application/json",
            use_container_width=True
        )

    # 4. PDF Audit Report Download
    with c4:
        summary = dataset_summary(cleaned_df)
        score = calculate_health_score(summary)
        quality_report = {
            "Outliers Remaining": detect_outliers(cleaned_df),
            "Invalid Emails": detect_invalid_emails(cleaned_df),
            "Invalid Phone Numbers": detect_phone_numbers(cleaned_df),
            "Category Inconsistencies": detect_category_inconsistency(cleaned_df),
            "Constant Columns": detect_constant_columns(cleaned_df)
        }
        
        pdf_bytes = generate_pdf_report(
            dataset_name=st.session_state.get("dataset_name", "CleanIQ_Dataset"),
            summary=summary,
            health_score=score,
            fix_log=fix_log,
            quality_report=quality_report
        )
        
        st.download_button(
            label="📄 Download PDF Audit",
            data=pdf_bytes,
            file_name="CleanIQ_Quality_Audit_Report.pdf",
            mime="application/pdf",
            use_container_width=True
        )

    st.divider()

    # MySQL Integration Section
    st.write("### 🗄️ Stream Directly to MySQL / MariaDB")
    
    col_a, col_b = st.columns(2)
    with col_a:
        host = st.text_input("Database Host", value="localhost")
        user = st.text_input("Database Username", value="root")
        password = st.text_input("Database Password", type="password")
    
    with col_b:
        database = st.text_input("Database Name", value="analytics_db")
        table_name = st.text_input("Destination Table Name", value="cleaned_data")

    if st.button("🚀 Push Table to MySQL", use_container_width=True, type="primary"):
        try:
            with st.spinner("Connecting and streaming records to MySQL..."):
                rows = export_to_mysql(cleaned_df, host, user, password, database, table_name)
            st.success(f"🎉 Successfully streamed {rows} rows into table '{table_name}' on {host}!")
        except Exception as e:
            st.error(f"MySQL Export Error: {str(e)}")