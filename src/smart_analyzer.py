"""
smart_analyzer.py
-----------------
AI-driven column intelligence engine for CleanIQ.

For every column it:
  1. Detects the semantic type (age, salary, email, gender, ...)
     using BOTH column name keywords AND content sampling.
  2. Detects all data quality issues specific to that type.
  3. Generates a ranked list of fix options with a recommended default.

Results are consumed by the interactive Smart-Clean UI.
"""

import re
import pandas as pd
import numpy as np


# ─────────────────────────────────────────────────
# Semantic Type Keyword Map
# ─────────────────────────────────────────────────
SEMANTIC_KEYWORDS = {
    "age":        ["age", "years", "yr", "age_yrs", "age_years", "yrs"],
    "salary":     ["salary", "wage", "pay", "income", "compensation",
                   "ctc", "remuneration", "earning", "package"],
    "price":      ["price", "cost", "amount", "fee", "charge", "rate",
                   "fare", "value", "revenue", "sales", "budget", "spend"],
    "count":      ["count", "quantity", "qty", "num", "number", "total",
                   "cnt", "units", "visits", "hits"],
    "percentage": ["percent", "pct", "ratio", "score", "grade",
                   "percentage", "marks", "cgpa", "gpa"],
    "name":       ["name", "firstname", "lastname", "fullname",
                   "fname", "lname", "first_name", "last_name",
                   "customer_name", "employee_name"],
    "gender":     ["gender", "sex"],
    "status":     ["status", "state", "active", "flag",
                   "is_active", "is_deleted", "has_"],
    "email":      ["email", "mail", "e_mail", "gmail"],
    "phone":      ["phone", "mobile", "contact", "telephone",
                   "cell", "fax", "ph"],
    "date":       ["date", "dob", "birth", "joining", "created",
                   "updated", "timestamp", "hired", "resigned",
                   "start_date", "end_date"],
    "id":         ["_id", "id_", " id", "key", "_ref", "_code",
                   "identifier", "emp_no", "cust_no", "order_no"],
    "zip":        ["zip", "pincode", "postal", "zipcode", "pin"],
    "address":    ["address", "addr", "street", "city", "state",
                   "location", "region", "area"],
    "category":   [],   # detected by content
}


# ─────────────────────────────────────────────────
# Detect Semantic Type
# ─────────────────────────────────────────────────
def detect_semantic_type(column_name: str, series: pd.Series) -> str:
    """
    Returns the semantic type of a column using name keywords first,
    then content-based heuristics as fallback.
    """
    col = column_name.lower().replace(" ", "_")

    for sem_type, keywords in SEMANTIC_KEYWORDS.items():
        if any(kw in col for kw in keywords):
            return sem_type

    # ── Content-based fallback ──
    if pd.api.types.is_numeric_dtype(series):
        non_null = series.dropna()
        if len(non_null) == 0:
            return "numeric"

        mn, mx = non_null.min(), non_null.max()

        # Looks like age: integer-ish, reasonable range
        if 0 <= mn and mx <= 120:
            if (non_null - non_null.round()).abs().max() < 0.5:
                return "age"

        # Looks like a percentage: 0–100
        if 0 <= mn and mx <= 100:
            return "percentage"

        return "numeric"

    elif pd.api.types.is_object_dtype(series):
        non_null = series.dropna()
        if len(non_null) == 0:
            return "text"

        # Low unique count → categorical
        if non_null.nunique() <= 15 or (non_null.nunique() / len(non_null)) < 0.05:
            return "category"

        # Sample-based email detection
        sample = non_null.head(30)
        email_hits = sample.astype(str).str.contains(
            r"@.*\.", regex=True, na=False
        ).sum()
        if email_hits / len(sample) > 0.6:
            return "email"

        # Sample-based phone detection
        phone_hits = sample.astype(str).str.match(
            r"^\+?[\d\s\-\.\(\)]{7,20}$", na=False
        ).sum()
        if phone_hits / len(sample) > 0.6:
            return "phone"

        return "text"

    elif pd.api.types.is_datetime64_any_dtype(series):
        return "date"

    return "other"


# ─────────────────────────────────────────────────
# Semantic Label (emoji + text for UI display)
# ─────────────────────────────────────────────────
SEMANTIC_LABELS = {
    "age":        "🎂 Age",
    "salary":     "💰 Salary / Income",
    "price":      "💵 Price / Amount",
    "count":      "🔢 Count / Quantity",
    "percentage": "📊 Percentage / Score",
    "name":       "👤 Name",
    "gender":     "⚧ Gender",
    "status":     "🔘 Status / Flag",
    "email":      "📧 Email",
    "phone":      "📱 Phone",
    "date":       "📅 Date",
    "id":         "🔑 ID / Key",
    "zip":        "📮 ZIP / Postal",
    "address":    "📍 Address",
    "category":   "🏷 Category",
    "numeric":    "🔢 Numeric",
    "text":       "📝 Text",
    "other":      "❓ Other",
}

def get_semantic_label(semantic_type: str) -> str:
    return SEMANTIC_LABELS.get(semantic_type, "❓ Unknown")


# ─────────────────────────────────────────────────
# Detect All Issues for One Column
# ─────────────────────────────────────────────────
def detect_column_issues(df: pd.DataFrame, column: str, semantic_type: str) -> list:
    """
    Returns a list of issue dicts. Each dict has:
        type         — issue identifier
        description  — human-readable summary
        count        — number of affected rows
        fix_options  — list of (action_code, label) tuples
        default_fix  — recommended action_code
        sample_bad   — up to 5 sample problematic values (for user context)
    """
    series = df[column]
    issues = []
    n = len(series)

    # ── 1. Missing Values ────────────────────────────────────────────
    missing = int(series.isnull().sum())
    if missing > 0:
        pct = round(missing / n * 100, 1)
        sample_bad = []

        if pd.api.types.is_numeric_dtype(series):
            med_val  = round(float(series.median()), 3)
            mean_val = round(float(series.mean()), 3)
            opts = [
                ("fill_median",  f"Fill with Median  →  {med_val}"),
                ("fill_mean",    f"Fill with Mean    →  {mean_val}"),
                ("fill_zero",    "Fill with Zero (0)"),
                ("fill_custom",  "Fill with My Own Value"),
                ("drop_rows",    "Drop Rows with Missing"),
                ("keep",         "Leave as-is"),
            ]
            default = "fill_median"
        else:
            mode_val = series.mode()
            mode_str = f'"{mode_val[0]}"' if not mode_val.empty else '"Unknown"'
            opts = [
                ("fill_mode",    f"Fill with Mode  →  {mode_str}"),
                ("fill_unknown", 'Fill with "Unknown"'),
                ("fill_custom",  "Fill with My Own Value"),
                ("drop_rows",    "Drop Rows with Missing"),
                ("keep",         "Leave as-is"),
            ]
            default = "fill_mode"

        issues.append({
            "type":        "missing",
            "description": f"{missing} missing values  ({pct}% of rows)",
            "count":       missing,
            "fix_options": opts,
            "default_fix": default,
            "sample_bad":  sample_bad,
        })

    # ── 2. Negative Values (non-negative domains) ─────────────────────
    if semantic_type in ("age", "salary", "price", "count", "percentage"):
        if pd.api.types.is_numeric_dtype(series):
            non_null = series.dropna()
            neg_mask = non_null < 0
            neg_count = int(neg_mask.sum())
            if neg_count > 0:
                sample_bad = list(non_null[neg_mask].head(5).values)
                issues.append({
                    "type":        "negative_values",
                    "description": f"{neg_count} negative values  (invalid for '{semantic_type}')",
                    "count":       neg_count,
                    "fix_options": [
                        ("abs_values",     "Take Absolute Value  →  flip sign (e.g. -25 → 25)"),
                        ("zero_negatives", "Replace Negatives with Zero"),
                        ("null_negatives", "Replace Negatives with NaN  (will be imputed)"),
                        ("drop_negatives", "Drop Rows with Negative Values"),
                        ("keep",           "Leave as-is"),
                    ],
                    "default_fix": "abs_values",
                    "sample_bad":  sample_bad,
                })

    # ── 3. Unrealistic Age ────────────────────────────────────────────
    if semantic_type == "age" and pd.api.types.is_numeric_dtype(series):
        non_null = series.dropna()
        bad_mask = (non_null < 0) | (non_null > 120)
        bad_count = int(bad_mask.sum())
        if bad_count > 0:
            sample_bad = list(non_null[bad_mask].head(5).values)
            issues.append({
                "type":        "unrealistic_age",
                "description": f"{bad_count} unrealistic ages  (outside 0–120)",
                "count":       bad_count,
                "fix_options": [
                    ("cap_age",    "Cap to Valid Range  →  clip to 0–120"),
                    ("null_age",   "Replace with NaN  (will be imputed later)"),
                    ("drop_rows",  "Drop Rows with Invalid Ages"),
                    ("keep",       "Leave as-is"),
                ],
                "default_fix": "cap_age",
                "sample_bad":  sample_bad,
            })

    # ── 4. Percentage Out of Range ────────────────────────────────────
    if semantic_type == "percentage" and pd.api.types.is_numeric_dtype(series):
        non_null = series.dropna()
        bad_mask = (non_null < 0) | (non_null > 100)
        bad_count = int(bad_mask.sum())
        if bad_count > 0:
            sample_bad = list(non_null[bad_mask].head(5).values)
            issues.append({
                "type":        "out_of_range_pct",
                "description": f"{bad_count} values outside 0–100  (invalid for percentage)",
                "count":       bad_count,
                "fix_options": [
                    ("cap_percentage", "Cap to 0–100 Range"),
                    ("null_pct",       "Replace with NaN  (will be imputed later)"),
                    ("drop_rows",      "Drop Rows with Invalid Values"),
                    ("keep",           "Leave as-is"),
                ],
                "default_fix": "cap_percentage",
                "sample_bad":  sample_bad,
            })

    # ── 5. Statistical Outliers (IQR) ─────────────────────────────────
    skip_outlier_for = ("id", "zip", "percentage", "date")
    if pd.api.types.is_numeric_dtype(series) and semantic_type not in skip_outlier_for:
        non_null = series.dropna()
        if len(non_null) >= 8:
            q1, q3 = non_null.quantile(0.25), non_null.quantile(0.75)
            iqr = q3 - q1
            if iqr > 0:
                lo = round(float(q1 - 1.5 * iqr), 3)
                hi = round(float(q3 + 1.5 * iqr), 3)
                out_mask = (non_null < lo) | (non_null > hi)
                out_count = int(out_mask.sum())
                if out_count > 0:
                    sample_bad = list(non_null[out_mask].head(5).values)
                    issues.append({
                        "type":        "outlier",
                        "description": f"{out_count} statistical outliers  (IQR: {lo} – {hi})",
                        "count":       out_count,
                        "fix_options": [
                            ("cap_iqr",       f"Winsorize  →  clip to ({lo}, {hi})"),
                            ("null_outliers",  "Replace Outliers with NaN  (will be imputed)"),
                            ("drop_outliers",  "Drop Rows with Outliers"),
                            ("keep",           "Leave as-is"),
                        ],
                        "default_fix": "cap_iqr",
                        "sample_bad":  sample_bad,
                    })

    # ── 6. Category Casing / Whitespace Inconsistency ─────────────────
    if pd.api.types.is_object_dtype(series) and semantic_type in (
        "gender", "status", "category", "address"
    ):
        unique_raw = series.dropna().unique()
        seen_norm = {}
        variant_pairs = []
        for val in unique_raw:
            key = str(val).strip().lower()
            if key in seen_norm:
                variant_pairs.append((seen_norm[key], val))
            else:
                seen_norm[key] = val
        if variant_pairs:
            sample_bad = [f'"{a}"  vs  "{b}"' for a, b in variant_pairs[:3]]
            issues.append({
                "type":        "category_inconsistency",
                "description": f"{len(variant_pairs)} category variants differing only in case / whitespace",
                "count":       len(variant_pairs),
                "fix_options": [
                    ("normalize_title", 'Normalize to Title Case  →  "Male", "Female"'),
                    ("normalize_lower", 'Normalize to Lowercase   →  "male", "female"'),
                    ("normalize_upper", 'Normalize to Uppercase   →  "MALE", "FEMALE"'),
                    ("keep",            "Leave as-is"),
                ],
                "default_fix": "normalize_title",
                "sample_bad":  sample_bad,
            })

    # ── 7. Invalid Email ──────────────────────────────────────────────
    if semantic_type == "email":
        pattern = r"^[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}$"
        non_null = series.dropna()
        if len(non_null) > 0:
            bad_mask = ~non_null.astype(str).str.strip().str.lower().str.match(pattern)
            bad_count = int(bad_mask.sum())
            if bad_count > 0:
                sample_bad = list(non_null[bad_mask].head(5).values)
                issues.append({
                    "type":        "invalid_email",
                    "description": f"{bad_count} invalid / malformed email addresses",
                    "count":       bad_count,
                    "fix_options": [
                        ("null_invalid_email", "Replace Invalid Emails with NaN"),
                        ("drop_rows",          "Drop Rows with Invalid Emails"),
                        ("keep",               "Leave as-is"),
                    ],
                    "default_fix": "null_invalid_email",
                    "sample_bad":  sample_bad,
                })

    # ── 8. Invalid Phone ──────────────────────────────────────────────
    if semantic_type == "phone":
        phone_re = r"^\+?[\d\s\-\.\(\)]{7,20}$"
        non_null = series.dropna()
        if len(non_null) > 0:
            bad_mask = ~non_null.astype(str).str.strip().str.match(phone_re)
            bad_count = int(bad_mask.sum())
            if bad_count > 0:
                sample_bad = list(non_null[bad_mask].head(5).values)
                issues.append({
                    "type":        "invalid_phone",
                    "description": f"{bad_count} invalid phone numbers (not matching standard format)",
                    "count":       bad_count,
                    "fix_options": [
                        ("null_invalid_phone", "Replace Invalid Phones with NaN"),
                        ("strip_phone_chars",  "Strip Non-Digit Characters  →  keep digits only"),
                        ("drop_rows",          "Drop Rows with Invalid Phones"),
                        ("keep",               "Leave as-is"),
                    ],
                    "default_fix": "null_invalid_phone",
                    "sample_bad":  sample_bad,
                })

    # ── 9. Near-Constant Column ───────────────────────────────────────
    if n > 0:
        top_freq = series.value_counts(normalize=True, dropna=True)
        if len(top_freq) > 0 and top_freq.iloc[0] >= 0.95:
            top_val = top_freq.index[0]
            top_pct = round(top_freq.iloc[0] * 100, 1)
            issues.append({
                "type":        "near_constant",
                "description": f'{top_pct}% of rows have the same value: "{top_val}"  (low analytical value)',
                "count":       0,
                "fix_options": [
                    ("drop_column", "Drop This Column"),
                    ("keep",        "Keep Column"),
                ],
                "default_fix": "keep",
                "sample_bad":  [],
            })

    return issues


# ─────────────────────────────────────────────────
# Build Full Cleaning Plan for All Columns
# ─────────────────────────────────────────────────
def build_cleaning_plan(df: pd.DataFrame) -> list:
    """
    Analyzes every column in the DataFrame.
    Returns a list of column-plan dicts for the Smart-Clean UI.
    """
    plan = []
    for column in df.columns:
        series = df[column]
        sem_type = detect_semantic_type(column, series)
        issues   = detect_column_issues(df, column, sem_type)
        plan.append({
            "column":         column,
            "semantic_type":  sem_type,
            "semantic_label": get_semantic_label(sem_type),
            "dtype":          str(series.dtype),
            "missing":        int(series.isnull().sum()),
            "unique":         int(series.nunique()),
            "issues":         issues,
            "has_issues":     len(issues) > 0,
        })
    return plan
