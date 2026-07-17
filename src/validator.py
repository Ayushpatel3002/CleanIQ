import pandas as pd
import re


# ----------------------------------------
# Detect Outliers (IQR Method)
# ----------------------------------------

def detect_outliers(df):

    report = {}

    numeric_columns = df.select_dtypes(include="number").columns

    for column in numeric_columns:

        q1 = df[column].quantile(0.25)
        q3 = df[column].quantile(0.75)

        iqr = q3 - q1

        lower = q1 - 1.5 * iqr
        upper = q3 + 1.5 * iqr

        outliers = df[
            (df[column] < lower) |
            (df[column] > upper)
        ]

        report[column] = len(outliers)

    return report


# ----------------------------------------
# Detect Invalid Emails
# ----------------------------------------

def detect_invalid_emails(df):

    report = {}

    email_pattern = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'

    for column in df.columns:

        if "email" not in column.lower():
            continue

        invalid = (
            ~df[column]
            .astype(str)
            .str.match(email_pattern)
        ).sum()

        report[column] = invalid

    return report


# ----------------------------------------
# Detect Phone Columns
# ----------------------------------------

def detect_phone_numbers(df):

    report = {}

    phone_columns = [

        "phone",
        "mobile",
        "contact"

    ]

    for column in df.columns:

        if any(word in column.lower() for word in phone_columns):

            invalid = (
                df[column]
                .astype(str)
                .str.len() != 10
            ).sum()

            report[column] = invalid

    return report


# ----------------------------------------
# Detect Inconsistent Categories
# ----------------------------------------

def detect_category_inconsistency(df):

    report = {}

    text_columns = df.select_dtypes(include="object").columns

    for column in text_columns:

        unique = df[column].dropna().unique()

        normalized = set()

        inconsistent = 0

        for value in unique:

            clean = str(value).strip().lower()

            if clean in normalized:

                inconsistent += 1

            normalized.add(clean)

        report[column] = inconsistent

    return report