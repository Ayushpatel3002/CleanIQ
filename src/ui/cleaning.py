"""
cleaning.py  —  Smart Clean UI
================================
Two sub-tabs:
  ⚡ Auto-Clean   — one-click full pipeline
  🧠 Smart Clean  — AI reads every column, shows issues,
                    user picks the fix per issue, then applies
"""

import streamlit as st
import pandas as pd
import numpy as np

from src.pipeline       import run_pipeline
from src.smart_analyzer import build_cleaning_plan
from src.cleaner        import apply_column_fix


# ─────────────────────────────────────────────────────────────
# Helper: format pipeline result values for display
# ─────────────────────────────────────────────────────────────
def _fmt(value):
    if isinstance(value, dict):
        parts = []
        for k, v in value.items():
            parts.append(f"{k}: {', '.join(v) if isinstance(v, list) else v}")
        return " | ".join(parts)
    if isinstance(value, list):
        return ", ".join(str(x) for x in value) if value else "None"
    return str(value)


# ─────────────────────────────────────────────────────────────
# Issue-type badge colour
# ─────────────────────────────────────────────────────────────
ISSUE_ICONS = {
    "missing":               "🟡 Missing Values",
    "negative_values":       "🔴 Negative Values",
    "unrealistic_age":       "🔴 Unrealistic Age",
    "out_of_range_pct":      "🔴 Out-of-Range %",
    "outlier":               "🟠 Statistical Outlier",
    "category_inconsistency":"🟡 Casing Inconsistency",
    "invalid_email":         "🔴 Invalid Email",
    "invalid_phone":         "🟠 Invalid Phone",
    "near_constant":         "🔵 Near-Constant Column",
}


# ─────────────────────────────────────────────────────────────
# Main entry point  (called from app.py)
# ─────────────────────────────────────────────────────────────
def show_cleaning(df):
    st.subheader("🧹 Autonomous Data Remediation Engine")

    auto_tab, smart_tab = st.tabs(["⚡ 1-Click Auto-Clean", "🧠 Interactive Smart Clean (AI Per-Column)"])

    with auto_tab:
        _show_auto_clean(df)

    with smart_tab:
        _show_smart_clean(df)


# ─────────────────────────────────────────────────────────────
# TAB A — Auto-Clean (one click)
# ─────────────────────────────────────────────────────────────
def _show_auto_clean(df):
    st.markdown(
        "One-click pipeline: **standardize column headers → dedup → trim → normalize casing → "
        "smart imputation → parse dates → validate emails → cap extreme outliers**"
    )

    if st.button("⚡ Run Full Auto-Clean Pipeline", use_container_width=True, type="primary", key="btn_auto"):
        with st.spinner("Executing autonomous cleaning pipeline…"):
            results = run_pipeline(df)

        cleaned_df     = results["cleaned_df"]
        report         = results["cleaning_report"]
        quality_report = results["quality_report"]

        st.session_state["cleaned_df"]      = cleaned_df
        st.session_state["cleaning_report"] = report
        st.session_state["quality_report"]  = quality_report
        st.session_state["fix_log"] = [
            {"Column": "Pipeline", "Issue": "Auto-Clean", "Fix Applied": f"{k}: {_fmt(v)}"}
            for k, v in report.items()
            if k not in ["Rows Before", "Rows After", "Columns Before", "Columns After"]
        ]

        st.success("✅ Auto-Clean executed successfully!")

        # Before / After metrics
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Rows Before",    report.get("Rows Before"))
        c2.metric("Rows After",     report.get("Rows After"),
                  delta=report.get("Rows After", 0) - report.get("Rows Before", 0))
        c3.metric("Columns Before", report.get("Columns Before"))
        c4.metric("Columns After",  report.get("Columns After"),
                  delta=report.get("Columns After", 0) - report.get("Columns Before", 0))

        st.divider()
        st.subheader("📊 Pipeline Execution Summary")
        skip = {"Rows Before", "Rows After", "Columns Before", "Columns After"}
        rows = [{"Step": k, "Result": _fmt(v)} for k, v in report.items() if k not in skip]
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

        st.divider()
        st.subheader("📋 Cleaned Data Preview")
        st.caption(f"Showing first 10 of {len(cleaned_df)} rows")
        st.dataframe(cleaned_df.head(10), use_container_width=True)


# ─────────────────────────────────────────────────────────────
# TAB B — Smart Clean (per-column interactive)
# ─────────────────────────────────────────────────────────────
def _show_smart_clean(df):

    st.markdown(
        "**Interactive Remediation:**  \n"
        "1. Click **Analyse Columns** — AI inspects domain semantics (Age, Salary, Email, Gender…) and flags invalid entries.  \n"
        "2. For each detected anomaly, choose your preferred remediation policy (AI default is pre-selected).  \n"
        "3. Click **Apply Selected Fixes** to transform your dataset."
    )

    # Working df from session
    working_key = "smart_working_df"
    if working_key not in st.session_state:
        st.session_state[working_key] = df.copy()

    col_a, col_b = st.columns([1, 1])
    if col_a.button("🔍 Analyse Columns", use_container_width=True, key="btn_analyse"):
        with st.spinner("AI is inspecting all columns…"):
            plan = build_cleaning_plan(st.session_state[working_key])
        st.session_state["smart_plan"] = plan

    if col_b.button("🔄 Reset to Original Upload", use_container_width=True, key="btn_reset"):
        st.session_state[working_key] = df.copy()
        if "smart_plan" in st.session_state:
            del st.session_state["smart_plan"]
        st.info("Reset to original uploaded data.")

    # ── Global Find & Replace Tool ────────────────────────────────────
    with st.expander("🔍 Global Find & Replace Utility", expanded=False):
        st.caption("Search and replace placeholder values (e.g. 'N/A', '?', '-999', or typos) across your dataset.")
        fr_col1, fr_col2, fr_col3 = st.columns(3)
        with fr_col1:
            find_val = st.text_input("Find Value:", placeholder="e.g. N/A, ?, null", key="fr_find")
        with fr_col2:
            replace_val = st.text_input("Replace With:", placeholder="e.g. 0, Unknown, or leave empty for null", key="fr_replace")
        with fr_col3:
            target_cols = st.multiselect("Apply to Columns (Empty = All):", options=st.session_state[working_key].columns.tolist(), key="fr_cols")

        if st.button("🚀 Execute Find & Replace", key="btn_exec_fr", use_container_width=True):
            if find_val:
                work_df = st.session_state[working_key].copy()
                cols_to_search = target_cols if target_cols else work_df.columns.tolist()
                rep_target = np.nan if replace_val in ["", "null", "NaN", "None"] else replace_val
                
                total_rep = 0
                for c in cols_to_search:
                    mask = work_df[c].astype(str).str.lower() == find_val.lower()
                    total_rep += int(mask.sum())
                    work_df.loc[mask, c] = rep_target

                st.session_state[working_key] = work_df
                st.session_state["cleaned_df"] = work_df
                st.session_state["smart_plan"] = build_cleaning_plan(work_df)
                st.success(f"🎉 Replaced {total_rep} occurrences of '{find_val}' with '{replace_val}' across {len(cols_to_search)} column(s)!")

    if "smart_plan" not in st.session_state:
        st.info("Click **Analyse Columns** to inspect anomalies.")
        return

    plan = st.session_state["smart_plan"]

    # ── Summary banner ────────────────────────────────────────────────
    issues_cols   = [p for p in plan if p["has_issues"]]
    clean_cols    = [p for p in plan if not p["has_issues"]]
    total_issues  = sum(len(p["issues"]) for p in issues_cols)

    st.divider()
    m1, m2, m3 = st.columns(3)
    m1.metric("Columns Inspected",     len(plan))
    m2.metric("Columns with Issues",  len(issues_cols))
    m3.metric("Total Anomaly Types",   total_issues)

    if total_issues == 0:
        st.success("🎉 Zero anomalies detected! Dataset is completely clean.")
        return

    st.divider()

    # ── Per-column issue cards + user choice selectors ────────────────
    st.subheader("🔧 Choose Remediation Policy for Each Anomaly")
    st.caption("Each dropdown has the AI-recommended default pre-selected. Modify any option to customize.")

    user_choices = {}

    for col_plan in issues_cols:
        col     = col_plan["column"]
        sem_lbl = col_plan["semantic_label"]
        dtype   = col_plan["dtype"]

        has_red = any(
            ISSUE_ICONS.get(iss["type"], "").startswith("🔴")
            for iss in col_plan["issues"]
        )
        badge = "🔴" if has_red else "🟠"

        with st.expander(f"{badge}  **`{col}`**   —   {sem_lbl}   `{dtype}`", expanded=True):
            for issue in col_plan["issues"]:
                issue_type = issue["type"]
                issue_icon = ISSUE_ICONS.get(issue_type, "⚠️")
                opts       = issue["fix_options"]
                default_i  = next(
                    (i for i, o in enumerate(opts) if o[0] == issue["default_fix"]),
                    0
                )
                labels = [o[1] for o in opts]

                st.markdown(f"**{issue_icon}** — {issue['description']}")

                if issue.get("sample_bad"):
                    sample_str = ", ".join(str(v) for v in issue["sample_bad"])
                    st.caption(f"Sample erroneous entries: `{sample_str}`")

                widget_key    = f"sel_{col}_{issue_type}"
                custom_key    = f"cus_{col}_{issue_type}"

                chosen_label  = st.selectbox(
                    label          = "Action",
                    options        = labels,
                    index          = default_i,
                    key            = widget_key,
                    label_visibility = "collapsed",
                )
                chosen_action = opts[labels.index(chosen_label)][0]

                custom_val = None
                if chosen_action == "fill_custom":
                    custom_val = st.text_input(
                        "Enter custom fill value:",
                        key = custom_key,
                        placeholder = "e.g. 0, N/A, Unknown …"
                    )

                user_choices[f"{col}__{issue_type}"] = {
                    "column":       col,
                    "issue_type":   issue_type,
                    "action":       chosen_action,
                    "custom_value": custom_val,
                }
                st.write("")

    # ── Apply button ─────────────────────────────────────────────────
    st.divider()
    if st.button("✅ Apply Selected Fixes", use_container_width=True, type="primary", key="btn_apply"):

        working_df = st.session_state[working_key].copy()
        apply_log  = []
        skipped    = 0

        for key, choice in user_choices.items():
            col        = choice["column"]
            issue_type = choice["issue_type"]
            action     = choice["action"]
            custom_val = choice["custom_value"]

            if action == "keep":
                skipped += 1
                continue

            working_df, description = apply_column_fix(
                working_df, col, issue_type, action, custom_val
            )
            apply_log.append({
                "Column":        col,
                "Issue":         ISSUE_ICONS.get(issue_type, issue_type),
                "Fix Applied":   description,
            })

        st.session_state[working_key]       = working_df
        st.session_state["cleaned_df"]      = working_df
        st.session_state["smart_plan"]      = build_cleaning_plan(working_df)
        st.session_state["fix_log"]         = apply_log

        st.success(
            f"✅ Applied **{len(apply_log)}** fix(es)."
            + (f"  Skipped {skipped} (kept as-is)." if skipped else "")
        )

        if apply_log:
            st.subheader("📋 Fix Execution Log")
            st.dataframe(pd.DataFrame(apply_log), use_container_width=True, hide_index=True)

        remaining = sum(
            len(p["issues"]) for p in st.session_state["smart_plan"] if p["has_issues"]
        )
        if remaining > 0:
            st.warning(
                f"⚠️ **{remaining}** anomaly type(s) remaining. "
                "You can continue applying fixes or export your cleaned data."
            )
        else:
            st.success("🎉 All detected issues resolved! Data is clean.")

        st.divider()
        st.subheader("📊 Cleaned Data Preview")
        st.caption(f"Showing first 10 of {len(working_df)} rows")
        st.dataframe(working_df.head(10), use_container_width=True)

    # ── Healthy columns accordion ─────────────────────────────────────
    if clean_cols:
        with st.expander(f"✅  {len(clean_cols)} healthy column(s) — zero anomalies"):
            healthy_df = pd.DataFrame([
                {
                    "Column":         p["column"],
                    "Semantic Type":  p["semantic_label"],
                    "Dtype":          p["dtype"],
                    "Unique Values":  p["unique"],
                    "Missing":        p["missing"],
                }
                for p in clean_cols
            ])
            st.dataframe(healthy_df, use_container_width=True, hide_index=True)