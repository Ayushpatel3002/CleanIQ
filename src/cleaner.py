import pandas as pd
import numpy as np
import re


# --------------------------------------------------
# Standardize Column Names
# --------------------------------------------------
def standardize_column_names(df):
    original = list(df.columns)
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(r'\s+', '_', regex=True)
        .str.replace(r'[^a-z0-9_]', '', regex=True)
        .str.replace(r'_+', '_', regex=True)
        .str.strip('_')
    )
    renamed = sum(1 for a, b in zip(original, df.columns) if a != b)
    return df, renamed


# --------------------------------------------------
# Remove Duplicate Rows
# --------------------------------------------------
def remove_duplicates(df):
    duplicate_count = int(df.duplicated().sum())
    df = df.drop_duplicates().reset_index(drop=True)
    return df, duplicate_count


# --------------------------------------------------
# Trim Whitespace (NaN-safe and Mixed-type safe)
# --------------------------------------------------
def trim_whitespace(df):
    trimmed_columns = 0
    for column in df.select_dtypes(include="object").columns:
        before = df[column].copy()
        df[column] = df[column].apply(lambda x: x.strip() if isinstance(x, str) else x)
        if not before.equals(df[column]):
            trimmed_columns += 1
    return df, trimmed_columns


# --------------------------------------------------
# Normalize Text Casing for Categorical Columns
# --------------------------------------------------
def normalize_text_casing(df):
    normalized_columns = 0
    for column in df.select_dtypes(include="object").columns:
        non_null = df[column].dropna()
        if len(non_null) == 0:
            continue
        n_unique = non_null.nunique()
        cardinality_ratio = n_unique / len(non_null)
        if n_unique <= 30 or cardinality_ratio < 0.05:
            before = df[column].copy()
            df[column] = df[column].apply(lambda x: x.strip().title() if isinstance(x, str) else x)
            if not before.equals(df[column]):
                normalized_columns += 1
    return df, normalized_columns


# --------------------------------------------------
# Smart Missing Value Imputation
# --------------------------------------------------
def fill_missing_values(df):
    filled_columns = 0
    dropped_columns = []
    total_rows = len(df)

    for column in list(df.columns):
        missing_count = df[column].isnull().sum()
        if missing_count == 0:
            continue
        missing_pct = (missing_count / total_rows) * 100

        if missing_pct > 60:
            df.drop(columns=[column], inplace=True)
            dropped_columns.append(column)
            continue

        if pd.api.types.is_numeric_dtype(df[column]):
            skewness = df[column].skew()
            if abs(skewness) > 1.0:
                fill_val = df[column].median()
            else:
                fill_val = df[column].mean()
            df[column] = df[column].fillna(fill_val)
            filled_columns += 1

        elif pd.api.types.is_bool_dtype(df[column]):
            mode = df[column].mode()
            if not mode.empty:
                df[column] = df[column].fillna(mode[0])
            filled_columns += 1

        else:
            non_null = df[column].dropna()
            n_unique = non_null.nunique()
            cardinality_ratio = n_unique / len(non_null) if len(non_null) > 0 else 1
            if cardinality_ratio > 0.5 or n_unique > 50:
                df[column] = df[column].fillna("Unknown")
            else:
                mode = df[column].mode()
                if not mode.empty:
                    df[column] = df[column].fillna(mode[0])
            filled_columns += 1

    result = {
        "Columns Filled": filled_columns,
        "Columns Dropped (>60% missing)": len(dropped_columns),
        "Dropped": dropped_columns if dropped_columns else "None"
    }
    return df, result


# --------------------------------------------------
# Standardize Date Columns
# --------------------------------------------------
def standardize_dates(df):
    converted = 0
    keywords = [
        "date", "dob", "birth", "joining",
        "created", "updated", "timestamp", "time", "year", "month"
    ]
    for column in df.columns:
        name = column.lower()
        if any(word in name for word in keywords):
            try:
                df[column] = pd.to_datetime(df[column], errors="coerce")
                converted += 1
            except Exception:
                pass
    return df, converted


# --------------------------------------------------
# Validate & Clean Email Columns
# --------------------------------------------------
def validate_email_columns(df):
    email_columns = 0
    email_pattern = r'^[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}$'
    for column in df.columns:
        if "email" in column.lower() or "mail" in column.lower():
            email_columns += 1
            non_null_mask = df[column].notna()
            df.loc[non_null_mask, column] = (
                df.loc[non_null_mask, column]
                .astype(str)
                .str.lower()
                .str.strip()
            )
            invalid_mask = non_null_mask & ~df[column].str.match(email_pattern, na=False)
            df.loc[invalid_mask, column] = np.nan
    return df, email_columns


# --------------------------------------------------
# Cap Outliers (Winsorization at IQR fences)
# --------------------------------------------------
def cap_outliers(df):
    capped_columns = 0
    numeric_columns = df.select_dtypes(include="number").columns
    for column in numeric_columns:
        if df[column].isnull().all():
            continue
        q1 = df[column].quantile(0.25)
        q3 = df[column].quantile(0.75)
        iqr = q3 - q1
        if iqr == 0:
            continue
        lower_fence = q1 - 1.5 * iqr
        upper_fence = q3 + 1.5 * iqr
        outlier_count = ((df[column] < lower_fence) | (df[column] > upper_fence)).sum()
        if outlier_count > 0:
            df[column] = df[column].clip(lower=lower_fence, upper=upper_fence)
            capped_columns += 1
    return df, capped_columns


# --------------------------------------------------
# Main Auto-Clean Pipeline
# --------------------------------------------------
def clean_dataset(df):
    """
    Full auto-cleaning pipeline:
      1. Standardize column names
      2. Remove duplicates
      3. Trim whitespace
      4. Normalize text casing
      5. Smart missing value imputation
      6. Parse date columns
      7. Validate & clean emails
      8. Cap outliers (Winsorization)
    """
    cleaned_df = df.copy()
    report = {}

    report["Rows Before"] = len(cleaned_df)
    report["Columns Before"] = len(cleaned_df.columns)

    pipeline = [
        ("Column Name Standardization", standardize_column_names),
        ("Duplicate Removal",           remove_duplicates),
        ("Whitespace Trim",             trim_whitespace),
        ("Text Casing Normalization",   normalize_text_casing),
        ("Missing Value Imputation",    fill_missing_values),
        ("Date Standardization",        standardize_dates),
        ("Email Validation",            validate_email_columns),
        ("Outlier Capping",             cap_outliers),
    ]

    for step_name, step_function in pipeline:
        cleaned_df, result = step_function(cleaned_df)
        report[step_name] = result

    report["Rows After"]    = len(cleaned_df)
    report["Columns After"] = len(cleaned_df.columns)

    return cleaned_df, report


# --------------------------------------------------
# Per-Column Fix Engine  (used by Smart Clean UI)
# --------------------------------------------------
def apply_column_fix(df, column, issue_type, fix_action, custom_value=None):
    """
    Apply ONE specific fix action to ONE column for ONE issue type.
    Called repeatedly by the Smart Clean UI based on user choices.

    Returns (modified_df, description_string).
    """
    df = df.copy()

    # column may have been dropped by an earlier fix
    if column not in df.columns:
        return df, f"Column '{column}' no longer exists (already dropped)"

    series = df[column]

    if fix_action == "keep":
        return df, "Kept as-is (no change)"

    # ── Missing Values ────────────────────────────────────────────────
    if issue_type == "missing":

        if fix_action == "fill_median":
            val = series.median()
            cnt = int(series.isnull().sum())
            df[column] = series.fillna(val)
            return df, f"Filled {cnt} nulls with median = {round(float(val), 3)}"

        elif fix_action == "fill_mean":
            val = series.mean()
            cnt = int(series.isnull().sum())
            df[column] = series.fillna(val)
            return df, f"Filled {cnt} nulls with mean = {round(float(val), 3)}"

        elif fix_action == "fill_zero":
            cnt = int(series.isnull().sum())
            df[column] = series.fillna(0)
            return df, f"Filled {cnt} nulls with 0"

        elif fix_action == "fill_mode":
            mode = series.mode()
            if not mode.empty:
                cnt = int(series.isnull().sum())
                df[column] = series.fillna(mode[0])
                return df, f'Filled {cnt} nulls with mode = "{mode[0]}"'
            return df, "Mode not found — no change"

        elif fix_action == "fill_unknown":
            cnt = int(series.isnull().sum())
            df[column] = series.fillna("Unknown")
            return df, f'Filled {cnt} nulls with "Unknown"'

        elif fix_action == "fill_custom":
            if custom_value is not None and str(custom_value).strip() != "":
                try:
                    val = float(custom_value) if pd.api.types.is_numeric_dtype(series) else custom_value
                    cnt = int(series.isnull().sum())
                    df[column] = series.fillna(val)
                    return df, f'Filled {cnt} nulls with custom value "{val}"'
                except ValueError:
                    return df, f'Invalid custom value "{custom_value}" — no change'
            return df, "No custom value provided — no change"

        elif fix_action == "drop_rows":
            before = len(df)
            df = df.dropna(subset=[column]).reset_index(drop=True)
            return df, f"Dropped {before - len(df)} rows where '{column}' was null"

    # ── Negative Values ───────────────────────────────────────────────
    elif issue_type == "negative_values":
        neg_count = int((series.dropna() < 0).sum())

        if fix_action == "abs_values":
            df[column] = series.abs()
            return df, f"Flipped sign on {neg_count} negative values (absolute value)"

        elif fix_action == "zero_negatives":
            df.loc[df[column] < 0, column] = 0
            return df, f"Replaced {neg_count} negatives with 0"

        elif fix_action == "null_negatives":
            df.loc[df[column] < 0, column] = np.nan
            return df, f"Replaced {neg_count} negatives with NaN"

        elif fix_action == "drop_negatives":
            before = len(df)
            df = df[df[column] >= 0].reset_index(drop=True)
            return df, f"Dropped {before - len(df)} rows with negative values"

    # ── Unrealistic Age ───────────────────────────────────────────────
    elif issue_type == "unrealistic_age":
        bad_mask = (df[column] < 0) | (df[column] > 120)
        bad_count = int(bad_mask.sum())

        if fix_action == "cap_age":
            df[column] = df[column].clip(lower=0, upper=120)
            return df, f"Capped {bad_count} values to valid age range [0, 120]"

        elif fix_action == "null_age":
            df.loc[bad_mask, column] = np.nan
            return df, f"Replaced {bad_count} unrealistic ages with NaN"

        elif fix_action == "drop_rows":
            before = len(df)
            df = df[~bad_mask].reset_index(drop=True)
            return df, f"Dropped {before - len(df)} rows with unrealistic ages"

    # ── Percentage Out of Range ───────────────────────────────────────
    elif issue_type == "out_of_range_pct":
        bad_mask = (df[column] < 0) | (df[column] > 100)
        bad_count = int(bad_mask.sum())

        if fix_action == "cap_percentage":
            df[column] = df[column].clip(lower=0, upper=100)
            return df, f"Capped {bad_count} values to valid percentage range [0, 100]"

        elif fix_action == "null_pct":
            df.loc[bad_mask, column] = np.nan
            return df, f"Replaced {bad_count} out-of-range values with NaN"

        elif fix_action == "drop_rows":
            before = len(df)
            df = df[~bad_mask].reset_index(drop=True)
            return df, f"Dropped {before - len(df)} rows"

    # ── Statistical Outliers ──────────────────────────────────────────
    elif issue_type == "outlier":
        q1 = series.quantile(0.25)
        q3 = series.quantile(0.75)
        iqr = q3 - q1
        lo  = q1 - 1.5 * iqr
        hi  = q3 + 1.5 * iqr
        out_mask  = (series < lo) | (series > hi)
        out_count = int(out_mask.sum())

        if fix_action == "cap_iqr":
            df[column] = series.clip(lower=lo, upper=hi)
            return df, f"Winsorized {out_count} outliers to ({round(float(lo), 2)}, {round(float(hi), 2)})"

        elif fix_action == "null_outliers":
            df.loc[out_mask, column] = np.nan
            return df, f"Replaced {out_count} outliers with NaN"

        elif fix_action == "drop_outliers":
            before = len(df)
            df = df[~out_mask].reset_index(drop=True)
            return df, f"Dropped {before - len(df)} outlier rows"

    # ── Category Casing Inconsistency ────────────────────────────────
    elif issue_type == "category_inconsistency":

        if fix_action == "normalize_title":
            df[column] = df[column].str.strip().str.title()
            return df, "Normalized to Title Case"

        elif fix_action == "normalize_lower":
            df[column] = df[column].str.strip().str.lower()
            return df, "Normalized to Lowercase"

        elif fix_action == "normalize_upper":
            df[column] = df[column].str.strip().str.upper()
            return df, "Normalized to Uppercase"

    # ── Invalid Email ─────────────────────────────────────────────────
    elif issue_type == "invalid_email":
        pattern = r'^[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}$'
        non_null_mask = df[column].notna()
        bad_mask  = non_null_mask & ~df[column].astype(str).str.strip().str.lower().str.match(pattern)
        bad_count = int(bad_mask.sum())

        if fix_action == "null_invalid_email":
            df.loc[bad_mask, column] = np.nan
            return df, f"Replaced {bad_count} invalid emails with NaN"

        elif fix_action == "drop_rows":
            before = len(df)
            df = df[~bad_mask].reset_index(drop=True)
            return df, f"Dropped {before - len(df)} rows with invalid emails"

    # ── Invalid Phone ─────────────────────────────────────────────────
    elif issue_type == "invalid_phone":
        phone_re  = r'^\+?[\d\s\-\.\(\)]{7,20}$'
        non_null_mask = df[column].notna()
        bad_mask  = non_null_mask & ~df[column].astype(str).str.strip().str.match(phone_re)
        bad_count = int(bad_mask.sum())

        if fix_action == "null_invalid_phone":
            df.loc[bad_mask, column] = np.nan
            return df, f"Replaced {bad_count} invalid phones with NaN"

        elif fix_action == "strip_phone_chars":
            df[column] = df[column].astype(str).str.replace(r'[^\d+]', '', regex=True)
            return df, "Stripped non-digit characters from phone numbers"

        elif fix_action == "drop_rows":
            before = len(df)
            df = df[~bad_mask].reset_index(drop=True)
            return df, f"Dropped {before - len(df)} rows with invalid phones"

    # ── Near-Constant Column ──────────────────────────────────────────
    elif issue_type == "near_constant":
        if fix_action == "drop_column":
            df = df.drop(columns=[column])
            return df, f"Dropped column '{column}' (near-constant, low analytical value)"

    return df, f"No matching action for issue='{issue_type}', action='{fix_action}'"