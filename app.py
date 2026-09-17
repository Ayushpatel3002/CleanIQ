import streamlit as st
import pandas as pd

from src.profiler import (
    load_dataset,
    dataset_summary,
    analyze_columns
)
from src.health import calculate_health_score, health_label
from src.cleaner import clean_dataset
from src.demo_data import get_demo_dataset

from src.ui.profile import show_profile
from src.ui.distributions import show_distributions
from src.ui.insights import show_insights
from src.ui.cleaning import show_cleaning
from src.ui.compare import show_comparison
from src.ui.quality import show_quality
from src.ui.export import show_export

# -----------------------------
# Page Configuration
# -----------------------------
st.set_page_config(
    page_title="CleanIQ — AI-Powered Data Cleaning Platform",
    page_icon="🧹",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# -----------------------------
# Custom Styling
# -----------------------------
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 800;
        background: linear-gradient(90deg, #6366f1, #a855f7, #ec4899);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0px;
    }
    .badge-pill {
        display: inline-block;
        padding: 2px 10px;
        font-size: 11px;
        font-weight: 600;
        border-radius: 9999px;
        background-color: rgba(99, 102, 241, 0.15);
        color: #818cf8;
        border: 1px solid rgba(99, 102, 241, 0.3);
        margin-bottom: 12px;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------
# Header
# -----------------------------
col_h1, col_h2 = st.columns([3, 1])
with col_h1:
    st.markdown('<p class="main-header">🧹 CleanIQ</p>', unsafe_allow_html=True)
    st.markdown('<span class="badge-pill">AI-POWERED AUTONOMOUS DATA CLEANING & INTELLIGENCE</span>', unsafe_allow_html=True)
    st.caption("Standardize values, detect semantic anomalies (negative ages, bad emails), inspect distributions, and export publication-ready datasets.")

# -----------------------------
# Upload & Demo Dataset Controls
# -----------------------------
with st.container():
    c_up1, c_up2 = st.columns([2, 1])
    with c_up1:
        uploaded_file = st.file_uploader(
            "📂 Upload CSV or Excel File:",
            type=["csv", "xlsx"],
            help="Upload your dataset to profile, inspect, and clean."
        )
    with c_up2:
        st.write("Or test instantly with 1-click:")
        if st.button("⚡ Load Sample Enterprise Dataset", use_container_width=True, type="secondary"):
            demo_df = get_demo_dataset()
            st.session_state["raw_df"] = demo_df.copy()
            st.session_state["dataset_name"] = "Enterprise_Staff_Sample.csv"
            if "cleaned_df" in st.session_state:
                del st.session_state["cleaned_df"]
            if "smart_working_df" in st.session_state:
                del st.session_state["smart_working_df"]
            if "smart_plan" in st.session_state:
                del st.session_state["smart_plan"]
            st.success("🎉 Loaded 250 records with real-world anomalies (negative ages, bad emails, outliers)!")
            st.rerun()

# -----------------------------
# State Management
# -----------------------------
if uploaded_file is not None:
    # If a new file is uploaded, update session state
    if st.session_state.get("last_uploaded_name") != uploaded_file.name:
        st.session_state["raw_df"] = load_dataset(uploaded_file)
        st.session_state["dataset_name"] = uploaded_file.name
        st.session_state["last_uploaded_name"] = uploaded_file.name
        if "cleaned_df" in st.session_state:
            del st.session_state["cleaned_df"]
        if "smart_working_df" in st.session_state:
            del st.session_state["smart_working_df"]
        if "smart_plan" in st.session_state:
            del st.session_state["smart_plan"]

if "raw_df" in st.session_state:
    df = st.session_state["raw_df"]
    dataset_name = st.session_state.get("dataset_name", "Dataset")

    # Current working dataframe (either cleaned or raw)
    current_df = st.session_state.get("cleaned_df", df)

    summary = dataset_summary(current_df)
    health_score = calculate_health_score(summary)

    # -----------------------------
    # 7 Feature Tabs
    # -----------------------------
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "📊 Profile",
        "📈 Distributions",
        "💡 Deep Insights",
        "🧠 Smart Clean",
        "🔄 Before vs After",
        "🔍 Quality Audit",
        "💾 Export & PDF"
    ])

    # TAB 1: Profile
    with tab1:
        show_profile(current_df, summary, health_score)

    # TAB 2: Distributions & Skewness
    with tab2:
        show_distributions(current_df)

    # TAB 3: Deep Insights
    with tab3:
        show_insights(current_df)

    # TAB 4: Smart Clean & Remediation
    with tab4:
        show_cleaning(df)

    # TAB 5: Before vs After Diff
    with tab5:
        if "cleaned_df" in st.session_state:
            show_comparison(df, st.session_state["cleaned_df"])
        else:
            st.info("ℹ️ Run either 1-Click Auto Clean or apply fixes in Smart Clean to inspect before vs after diffs.")

    # TAB 6: Quality Audit
    with tab6:
        show_quality()

    # TAB 7: Export & PDF Report
    with tab7:
        show_export()

else:
    st.info("👆 Please upload a CSV / Excel file or click **'⚡ Load Sample Enterprise Dataset'** above to explore all features.")