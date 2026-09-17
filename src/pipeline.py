from src.cleaner import clean_dataset

from src.validator import (
    detect_outliers,
    detect_invalid_emails,
    detect_phone_numbers,
    detect_category_inconsistency,
    detect_constant_columns,
)


def run_pipeline(df):
    """
    Execute the complete data preparation pipeline:
      1. Cleaning  — dedup, trim, normalize, impute, dates, emails, outliers
      2. Validation — outlier counts, invalid emails, bad phones, inconsistencies,
                      constant columns
    """

    # ----------------------------
    # Cleaning
    # ----------------------------
    cleaned_df, cleaning_report = clean_dataset(df)

    # ----------------------------
    # Post-clean Validation
    # ----------------------------
    quality_report = {
        "Outliers Remaining":         detect_outliers(cleaned_df),
        "Invalid Emails":             detect_invalid_emails(cleaned_df),
        "Invalid Phone Numbers":      detect_phone_numbers(cleaned_df),
        "Category Inconsistencies":   detect_category_inconsistency(cleaned_df),
        "Constant / Near-Constant":   detect_constant_columns(cleaned_df),
    }

    return {
        "cleaned_df":      cleaned_df,
        "cleaning_report": cleaning_report,
        "quality_report":  quality_report,
    }