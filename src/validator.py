import pandas as pd
import re


# --------------------------------------------------
# Detect Outliers (IQR Method) — Detection Only
# --------------------------------------------------
def detect_outliers(df):
    """
    Detects outliers in all numeric columns using the IQR method.
    Returns a dict of {column: outlier_count}.
    Note: Actual capping/removal is done by the cleaner (cap_outliers).
    """
    report = {}
    numeric_columns = df.select_dtypes(include="number").columns

    for column in numeric_columns:
        if df[column].isnull().all():
            continue

        q1 = df[column].quantile(0.25)
        q3 = df[column].quantile(0.75)
        iqr = q3 - q1

        if iqr == 0:
            report[column] = 0
            continue

        lower = q1 - 1.5 * iqr
        upper = q3 + 1.5 * iqr

        outlier_count = int(
            ((df[column] < lower) | (df[column] > upper)).sum()
        )
        report[column] = outlier_count

    return report


# --------------------------------------------------
# Detect Invalid Emails (NaN-safe)
# --------------------------------------------------
def detect_invalid_emails(df):
    """
    Counts invalid email entries in email columns.
    BUG FIX: Skips actual NaN rows so they are not counted as 'invalid'.
    """
    report = {}
    email_pattern = r'^[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}$'

    for column in df.columns:
        if "email" not in column.lower() and "mail" not in column.lower():
            continue

        # Only evaluate non-null entries
        non_null = df[column].dropna()

        invalid = int(
            (~non_null
             .astype(str)
             .str.strip()
             .str.lower()
             .str.match(email_pattern))
            .sum()
        ) if len(non_null) > 0 else 0

        report[column] = invalid

    return report


# --------------------------------------------------
# Detect Invalid Phone Numbers (flexible regex)
# --------------------------------------------------
def detect_phone_numbers(df):
    """
    Validates phone number columns using a flexible regex.
    BUG FIX: Old code only accepted exactly 10-digit numbers.
    New regex handles: +91-XXXXX-XXXXX, (123) 456-7890,
    international formats, separators, country codes.
    """
    report = {}

    phone_keywords = ["phone", "mobile", "contact", "telephone", "cell", "fax"]

    # Accepts 7–15 digits with optional +, spaces, dashes, dots, parentheses
    phone_pattern = r'^\+?[\d\s\-\.\(\)]{7,20}$'

    for column in df.columns:
        if not any(word in column.lower() for word in phone_keywords):
            continue

        non_null = df[column].dropna()

        invalid = int(
            (~non_null
             .astype(str)
             .str.strip()
             .str.match(phone_pattern))
            .sum()
        )

        report[column] = invalid

    return report


# --------------------------------------------------
# Detect Inconsistent Categories (case/whitespace variants)
# --------------------------------------------------
def detect_category_inconsistency(df):
    """
    Detects columns that have the same value spelled differently due to
    different casing or extra whitespace (e.g. 'male', 'Male', 'MALE').
    Returns count of variant duplicates per column.
    """
    report = {}
    text_columns = df.select_dtypes(include="object").columns

    for column in text_columns:
        unique_raw = df[column].dropna().unique()
        normalized_seen = {}
        inconsistent = 0

        for value in unique_raw:
            clean = str(value).strip().lower()
            if clean in normalized_seen:
                inconsistent += 1
            else:
                normalized_seen[clean] = value

        report[column] = inconsistent

    return report


# --------------------------------------------------
# Detect Constant / Near-Constant Columns
# --------------------------------------------------
def detect_constant_columns(df, threshold=0.99):
    """
    Detects columns where a single value makes up >= threshold% of rows.
    These columns add little analytical value.
    """
    report = {}
    for column in df.columns:
        n = len(df[column].dropna())
        if n == 0:
            continue
        top_freq = df[column].value_counts(normalize=True).iloc[0]
        if top_freq >= threshold:
            report[column] = f"{round(top_freq * 100, 1)}% same value"
    return report