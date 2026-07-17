import pandas as pd
import numpy as np
import re


# --------------------------------------------------
# Remove Duplicate Rows
# --------------------------------------------------
def remove_duplicates(df):

    duplicate_count = df.duplicated().sum()

    df = df.drop_duplicates()

    return df, duplicate_count


# --------------------------------------------------
# Trim Spaces
# --------------------------------------------------
def trim_whitespace(df):

    trimmed_columns = 0

    for column in df.select_dtypes(include="object"):

        before = df[column].copy()

        df[column] = (
            df[column]
            .astype(str)
            .str.strip()
        )

        if not before.equals(df[column]):
            trimmed_columns += 1

    return df, trimmed_columns


# --------------------------------------------------
# Fill Missing Values
# --------------------------------------------------
def fill_missing_values(df):

    filled_columns = 0

    for column in df.columns:

        if df[column].isnull().sum() == 0:
            continue

        # Numeric Columns
        if pd.api.types.is_numeric_dtype(df[column]):

            df[column] = df[column].fillna(df[column].median())

            filled_columns += 1

        # Text Columns
        else:

            mode = df[column].mode()

            if not mode.empty:
                df[column] = df[column].fillna(mode[0])

                filled_columns += 1

    return df, filled_columns


# --------------------------------------------------
# Standardize Date Columns
# --------------------------------------------------
def standardize_dates(df):

    converted = 0

    keywords = [
        "date",
        "dob",
        "birth",
        "joining"
    ]

    for column in df.columns:

        name = column.lower()

        if any(word in name for word in keywords):

            try:

                df[column] = pd.to_datetime(
                    df[column],
                    errors="coerce"
                )

                converted += 1

            except Exception:
                pass

    return df, converted


# --------------------------------------------------
# Validate Email Columns
# --------------------------------------------------
def validate_email_columns(df):

    email_columns = 0

    email_pattern = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'

    for column in df.columns:

        if "email" in column.lower():

            email_columns += 1

            df[column] = df[column].astype(str).str.lower()

            df[column] = df[column].where(
                df[column].str.match(email_pattern),
                np.nan
            )

    return df, email_columns

# --------------------------------------------------
# Main Cleaning Pipeline
# --------------------------------------------------
def clean_dataset(df):
    """
    Execute the complete cleaning pipeline.
    """

    cleaned_df = df.copy()

    report = {}

    report["Rows Before"] = len(cleaned_df)

    # ----------------------------
    # Cleaning Pipeline
    # ----------------------------

    pipeline = [

        ("Duplicate Removal", remove_duplicates),

        ("Whitespace Trim", trim_whitespace),

        ("Missing Value Filling", fill_missing_values),

        ("Date Standardization", standardize_dates),

        ("Email Validation", validate_email_columns),


    ]

    # ----------------------------
    # Execute Pipeline
    # ----------------------------

    for step_name, step_function in pipeline:

        cleaned_df, result = step_function(cleaned_df)

        report[step_name] = result

    report["Rows After"] = len(cleaned_df)

    return cleaned_df, report