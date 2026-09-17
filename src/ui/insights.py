import streamlit as st
import pandas as pd
import plotly.express as px
from backend.services.insights import generate_data_insights

def show_insights(df: pd.DataFrame):
    st.subheader("💡 Autonomous Deep Data Insights & Anomaly Discovery")
    st.caption("Automated detection of statistical skewness, domain constraint violations, and feature correlations.")

    insights_data = generate_data_insights(df)
    insights = insights_data.get("insights", [])
    correlations = insights_data.get("correlations", [])
    verdict = insights_data.get("summary_verdict", "")

    # Verdict Box
    st.info(f"📋 **Data Quality Verdict:** {verdict}")

    # Insights Cards Grid
    if insights:
        st.write(f"### 🔍 Discovered Findings & Statistical Anomalies ({len(insights)})")
        
        for item in insights:
            category = item.get("category", "General")
            title = item.get("title", "")
            desc = item.get("description", "")
            col = item.get("column", "")
            imp = item.get("importance", "Medium")
            type_ = item.get("type", "info")

            icon = "🚨" if type_ == "danger" else "⚠️" if type_ == "warning" else "✅" if type_ == "success" else "ℹ️"
            
            with st.expander(f"{icon} **[{category}]** {title} — `{col}`", expanded=(type_ in ["danger", "warning"])):
                st.write(desc)
                st.caption(f"Importance: **{imp}** | Targeted Feature: `{col}`")
    else:
        st.success("🎉 No severe anomalies or quality issues discovered. Dataset is well-structured!")

    # Correlations Section
    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    if len(numeric_cols) >= 2:
        st.divider()
        st.write("### 🔗 Feature Correlation Relationships")
        
        corr_matrix = df[numeric_cols].corr()
        
        fig = px.imshow(
            corr_matrix,
            text_auto=True,
            aspect="auto",
            title="Pearson Correlation Heatmap",
            color_continuous_scale="RdBu_r"
        )
        fig.update_layout(template="plotly_dark", height=450)
        st.plotly_chart(fig, use_container_width=True)

        if correlations:
            st.write("#### Strongest Feature Relationships")
            corr_df = pd.DataFrame(correlations)
            corr_df.columns = ["Feature 1", "Feature 2", "Pearson Correlation"]
            st.dataframe(corr_df, use_container_width=True, hide_index=True)
