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

from src.pipeline      import run_pipeline
from src.smart_analyzer import build_cleaning_plan
from src.cleaner       import apply_column_fix


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
    st.subheader("🧹 Data Cleaning")

    auto_tab, smart_tab = st.tabs(["⚡ Auto-Clean", "🧠 Smart Clean  (AI per-column)"])

    with auto_tab:
        _show_auto_clean(df)

    with smart_tab:
        _show_smart_clean(df)


# ─────────────────────────────────────────────────────────────
# TAB A — Auto-Clean (one click)
# ─────────────────────────────────────────────────────────────
def _show_auto_clean(df):
    st.markdown(
        "One-click pipeline: **dedup → trim → normalize casing → "
        "smart imputation → parse dates → fix emails → cap outliers**"
    )

    if st.button("⚡ Run Auto-Clean", use_container_width=True, type="primary", key="btn_auto"):
        with st.spinner("Running auto-clean pipeline…"):
            results = run_pipeline(df)

        cleaned_df     = results["cleaned_df"]
        report         = results["cleaning_report"]
        quality_report = results["quality_report"]

        st.session_state["cleaned_df"]      = cleaned_df
        st.session_state["cleaning_report"] = report
        st.session_state["quality_report"]  = quality_report

        st.success("✅ Auto-Clean completed!")

        # Before / After metrics
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Rows Before",    report.get("Rows Before"))
        c2.metric("Rows After",     report.get("Rows After"),
                  delta=report.get("Rows After", 0) - report.get("Rows Before", 0))
        c3.metric("Columns Before", report.get("Columns Before"))
        c4.metric("Columns After",  report.get("Columns After"),
                  delta=report.get("Columns After", 0) - report.get("Columns Before", 0))

        st.divider()
        st.subheader("📊 Pipeline Steps")
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
        "**How it works:**  \n"
        "1. Click **Analyse** — AI reads every column, detects semantic type "
        "(Age, Salary, Email, Gender…) and lists all issues.  \n"
        "2. For each issue, choose a fix from the AI-recommended options  \n"
        "   (or accept the default — already highlighted in the dropdown).  \n"
        "3. Click **Apply Selected Fixes** — preview your clean data instantly."
    )

    # ── Use the working df from session (auto-clean output if available) ──
    working_key = "smart_working_df"
    if working_key not in st.session_state:
        st.session_state[working_key] = df.copy()

    col_a, col_b = st.columns([1, 1])
    if col_a.button("🔍 Analyse Columns", use_container_width=True, key="btn_analyse"):
        with st.spinner("AI is analysing all columns…"):
            plan = build_cleaning_plan(st.session_state[working_key])
        st.session_state["smart_plan"] = plan

    if col_b.button("🔄 Reset to Original Data", use_container_width=True, key="btn_reset"):
        st.session_state[working_key] = df.copy()
        if "smart_plan" in st.session_state:
            del st.session_state["smart_plan"]
        st.info("Reset to original uploaded data.")

    if "smart_plan" not in st.session_state:
        st.info("Click **Analyse Columns** to begin.")
        return

    plan = st.session_state["smart_plan"]

    # ── Summary banner ────────────────────────────────────────────────
    issues_cols   = [p for p in plan if p["has_issues"]]
    clean_cols    = [p for p in plan if not p["has_issues"]]
    total_issues  = sum(len(p["issues"]) for p in issues_cols)

    st.divider()
    m1, m2, m3 = st.columns(3)
    m1.metric("Columns Analysed",     len(plan))
    m2.metric("Columns with Issues",  len(issues_cols))
    m3.metric("Total Issue Types",    total_issues)

    if total_issues == 0:
        st.success("🎉 No issues found! Your data looks clean and ready for analysis.")
        return

    st.divider()

    # ── Per-column issue cards + user choice selectors ────────────────
    st.subheader("🔧 Choose Your Fix for Each Issue")
    st.caption(
        "Each dropdown shows the AI-recommended fix first. "
        "Change it if you prefer a different approach."
    )

    # We collect all user choices into this dict (keyed by unique widget key)
    # We do NOT use st.form so that 'fill_custom' text inputs can appear
    # dynamically when the user switches to that option.

    user_choices = {}   # key → {column, issue_type, action, custom_value}

    for col_plan in issues_cols:
        col     = col_plan["column"]
        sem_lbl = col_plan["semantic_label"]
        dtype   = col_plan["dtype"]

        # Colour the expander header by worst issue severity
        has_red = any(
            ISSUE_ICONS.get(iss["type"], "").startswith("🔴")
            for iss in col_plan["issues"]
        )
        badge = "🔴" if has_red else "🟠"

        with st.expander(
            f"{badge}  **`{col}`**   —   {sem_lbl}   `{dtype}`",
            expanded=True
        ):
            for issue in col_plan["issues"]:
                issue_type = issue["type"]
                issue_icon = ISSUE_ICONS.get(issue_type, "⚠️")
                opts       = issue["fix_options"]      # list of (code, label)
                default_i  = next(
                    (i for i, o in enumerate(opts) if o[0] == issue["default_fix"]),
                    0
                )
                labels = [o[1] for o in opts]

                st.markdown(f"**{issue_icon}** — {issue['description']}")

                # Show sample bad values as a hint
                if issue.get("sample_bad"):
                    sample_str = ", ".join(str(v) for v in issue["sample_bad"])
                    st.caption(f"Sample values: `{sample_str}`")

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

                # Custom value input (only shown when user picks 'fill_custom')
                custom_val = None
                if chosen_action == "fill_custom":
                    custom_val = st.text_input(
                        "Enter your custom fill value:",
                        key = custom_key,
                        placeholder = "e.g. 0, N/A, Unknown …"
                    )

                user_choices[f"{col}__{issue_type}"] = {
                    "column":       col,
                    "issue_type":   issue_type,
                    "action":       chosen_action,
                    "custom_value": custom_val,
                }

                st.write("")  # spacing

    # ── Apply button ─────────────────────────────────────────────────
    st.divider()
    if st.button("✅ Apply Selected Fixes", use_container_width=True,
                 type="primary", key="btn_apply"):

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

        # Persist the cleaned df so Export tab can use it
        st.session_state[working_key]       = working_df
        st.session_state["cleaned_df"]      = working_df
        st.session_state["smart_plan"]      = build_cleaning_plan(working_df)

        # ── Results summary ───────────────────────────────────────────
        st.success(
            f"✅ Applied **{len(apply_log)}** fix(es)."
            + (f"  Skipped {skipped} (kept as-is)." if skipped else "")
        )

        if apply_log:
            st.subheader("📋 Fix Log")
            st.dataframe(
                pd.DataFrame(apply_log),
                use_container_width=True,
                hide_index=True
            )

        remaining = sum(
            len(p["issues"]) for p in st.session_state["smart_plan"] if p["has_issues"]
        )
        if remaining > 0:
            st.warning(
                f"⚠️ **{remaining}** issue type(s) still remain. "
                "The column list above has been refreshed — apply more fixes or accept as-is."
            )
        else:
            st.success("🎉 All detected issues resolved! Data is clean.")

        st.divider()
        st.subheader("📊 Cleaned Data Preview")
        st.caption(f"Showing first 10 of {len(working_df)} rows")
        st.dataframe(working_df.head(10), use_container_width=True)


    # ── Show columns that are already healthy ─────────────────────────
    if clean_cols:
        with st.expander(f"✅  {len(clean_cols)} healthy column(s) — no issues detected"):
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