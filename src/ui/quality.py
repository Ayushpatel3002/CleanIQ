import streamlit as st
import pandas as pd


def show_quality():

    st.subheader("🔍 Data Quality Assessment")

    if "quality_report" not in st.session_state:
        st.info("🧹 Run the cleaning pipeline first (in the **Clean** tab).")
        return

    quality_report = st.session_state["quality_report"]

    # -----------------------------------------------
    # Summary: total issues across all checks
    # -----------------------------------------------
    total_issues = 0
    for check_name, report in quality_report.items():
        for column, findings in report.items():
            if isinstance(findings, (int, float)) and findings > 0:
                total_issues += findings

    if total_issues == 0:
        st.success("🎉 No quality issues detected! Your data looks clean and ready for analysis.")
    else:
        st.warning(f"⚠️ {total_issues} total quality finding(s) detected across all checks.")

    st.divider()

    # -----------------------------------------------
    # Per-check breakdown
    # -----------------------------------------------
    for check_name, report in quality_report.items():

        if not report:
            continue

        # Flatten to rows
        rows = []
        for column, findings in report.items():
            if isinstance(findings, (int, float)):
                status = "✅ OK" if findings == 0 else f"⚠️ {findings} issue(s)"
                rows.append({
                    "Column":   column,
                    "Findings": findings,
                    "Status":   status
                })
            else:
                # String findings (e.g. constant column descriptions)
                rows.append({
                    "Column":   column,
                    "Findings": findings,
                    "Status":   "ℹ️ Note"
                })

        if not rows:
            continue

        check_df = pd.DataFrame(rows)
        issues_in_check = check_df["Findings"].apply(
            lambda x: x if isinstance(x, (int, float)) else 1
        ).sum()

        with st.expander(
            f"{'⚠️' if issues_in_check > 0 else '✅'} {check_name}  "
            f"— {len(rows)} column(s) checked",
            expanded=issues_in_check > 0
        ):
            st.dataframe(check_df, use_container_width=True, hide_index=True)

    st.divider()

    # -----------------------------------------------
    # Flat full table (all checks combined)
    # -----------------------------------------------
    st.subheader("📋 Full Quality Report Table")

    all_rows = []
    for check_name, report in quality_report.items():
        for column, findings in report.items():
            if isinstance(findings, (int, float)):
                status = "✅ OK" if findings == 0 else "⚠️ Issues Found"
            else:
                status = "ℹ️ Note"
            all_rows.append({
                "Check":    check_name,
                "Column":   column,
                "Findings": findings,
                "Status":   status
            })

    if all_rows:
        all_df = pd.DataFrame(all_rows)
        st.dataframe(all_df, use_container_width=True, hide_index=True)