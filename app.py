import streamlit as st
import pandas as pd

from src.profiler import (
    load_dataset,
    dataset_summary,
    analyze_columns
)

from src.health import calculate_health_score

from src.cleaner import clean_dataset

from src.ui.export import show_export

from src.validator import (
    detect_outliers,
    detect_invalid_emails,
    detect_phone_numbers,
    detect_category_inconsistency
)

from src.ui.profile import show_profile

from src.ui.cleaning import show_cleaning

from src.ui.quality import show_quality

# -----------------------------
# Page Configuration
# -----------------------------
st.set_page_config(
    page_title="CleanIQ",
    page_icon="🧹",
    layout="wide"
)

# -----------------------------
# Title
# -----------------------------
st.title("🧹 CleanIQ")
st.subheader("AI-Powered Data Cleaning Platform")

# -----------------------------
# Upload
# -----------------------------
uploaded_file = st.file_uploader(
    "📂 Upload CSV or Excel File",
    type=["csv", "xlsx"]
)

if uploaded_file is not None:

    # -----------------------------
    # Load Dataset
    # -----------------------------
    df = load_dataset(uploaded_file)

    summary = dataset_summary(df)

    health_score = calculate_health_score(summary)

    # -----------------------------
    # Tabs
    # -----------------------------
    tab1, tab2, tab3, tab4 = st.tabs(
        [
            "📊 Profile",
            "🧹 Clean",
            "🔍 Quality Report",
            "💾 Export"
        ]
    )

    # ============================================================
    # TAB 1 : PROFILE
    # ============================================================
    

    with tab1:

            show_profile(
            df,
            summary,
            health_score
        )

    # ============================================================
    # TAB 2 : CLEAN
    # ============================================================
    with tab2:

        show_cleaning(df)

    # ============================================================
    # TAB 3 : QUALITY REPORT
    # ============================================================
    with tab3:
         
          show_quality()

    # ============================================================
    # TAB 4 : EXPORT
    # ============================================================
    with tab4:

        show_export()