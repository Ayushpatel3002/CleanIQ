from src.cleaner import clean_dataset

from src.validator import (
    detect_outliers,
    detect_invalid_emails,
    detect_phone_numbers,
    detect_category_inconsistency
)


def run_pipeline(df):
    """
    Execute the complete data preparation pipeline.
    """

    # ----------------------------
    # Cleaning
    # ----------------------------

    cleaned_df, cleaning_report = clean_dataset(df)

    # ----------------------------
    # Validation
    # ----------------------------

    quality_report = {

        "Outliers": detect_outliers(cleaned_df),

        "Invalid Emails": detect_invalid_emails(cleaned_df),

        "Invalid Phone Numbers": detect_phone_numbers(cleaned_df),

        "Category Issues": detect_category_inconsistency(cleaned_df)

    }

    return {

        "cleaned_df": cleaned_df,

        "cleaning_report": cleaning_report,

        "quality_report": quality_report

    }