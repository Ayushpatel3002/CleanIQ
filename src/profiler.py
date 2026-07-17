import pandas as pd

from src.intelligence import (
    detect_primary_key,
    detect_date_column,
    calculate_missing_percentage,
    detect_email_column,
    detect_phone_column
)

def load_dataset(uploaded_file):
    """
    Load CSV or Excel dataset.
    """

    file_name = uploaded_file.name.lower()

    if file_name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)

    elif file_name.endswith(".xlsx"):
        df = pd.read_excel(uploaded_file)

    else:
        raise ValueError("Unsupported file format")

    return df


def dataset_summary(df):
    """
    Returns important dataset statistics.
    """

    summary = {

        "Rows": df.shape[0],

        "Columns": df.shape[1],

        "Missing Values": df.isnull().sum().sum(),

        "Duplicate Rows": df.duplicated().sum(),

        "Memory Usage (MB)": round(
            df.memory_usage(deep=True).sum()/1024**2,
            2
        ),

        "Numeric Columns":
            len(df.select_dtypes(include="number").columns),

        "Categorical Columns":
            len(df.select_dtypes(include="object").columns),

        "Datetime Columns":
            len(df.select_dtypes(include="datetime").columns)
    }

    return summary

def analyze_columns(df):
    """
    Analyze every column in the dataset.
    """

    column_info = []

    for column in df.columns:

        info = {

            "Column": column,

            "Data Type": str(df[column].dtype),

            "Missing Values": df[column].isnull().sum(),

            "Unique Values": df[column].nunique(),

            "Recommendation": "Healthy ✅"

        }

        # Default recommendation
    recommendation = "Healthy ✅"

    # Rule 1 - Primary Key
    if detect_primary_key(df[column]):
     recommendation = "Looks like Primary Key 🔑"

    # Rule 2 - Date Column
    elif detect_date_column(column):
        recommendation = "Convert to Datetime 📅"

    # Rule 3 - Email column
    elif detect_email_column(column):
        recommendation = "Validate Email Format 📧"

    # Rule 4 - Phone number Column
    elif detect_phone_column(column):
        recommendation = "Validate Phone Numbers 📱"    

    # Rule 5 - Missing Values
    elif calculate_missing_percentage(df[column]) > 30:
        recommendation = "High Missing Values ⚠"

    elif df[column].isnull().sum() > 0:
        recommendation = "Contains Missing Values ⚠"

    info["Recommendation"] = recommendation

    column_info.append(info)

    return pd.DataFrame(column_info)

