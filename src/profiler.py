import pandas as pd

from src.intelligence import (
    detect_primary_key,
    detect_date_column,
    detect_date_content,
    calculate_missing_percentage,
    detect_email_column,
    detect_phone_column
)


# --------------------------------------------------
# Load Dataset
# --------------------------------------------------
def load_dataset(uploaded_file):
    """
    Load CSV or Excel dataset into a pandas DataFrame.
    Handles common encoding issues for CSV files.
    """
    file_name = uploaded_file.name.lower()

    if file_name.endswith(".csv"):
        try:
            df = pd.read_csv(uploaded_file, encoding="utf-8")
        except UnicodeDecodeError:
            uploaded_file.seek(0)
            df = pd.read_csv(uploaded_file, encoding="latin-1")

    elif file_name.endswith(".xlsx"):
        df = pd.read_excel(uploaded_file)

    else:
        raise ValueError("Unsupported file format. Please upload a CSV or Excel file.")

    return df


# --------------------------------------------------
# Dataset Summary
# --------------------------------------------------
def dataset_summary(df):
    """
    Returns key dataset statistics as a dictionary.
    """
    total_cells = df.shape[0] * df.shape[1]
    missing_total = int(df.isnull().sum().sum())

    summary = {
        "Rows":                  df.shape[0],
        "Columns":               df.shape[1],
        "Total Cells":           total_cells,
        "Missing Values":        missing_total,
        "Missing %":             round((missing_total / total_cells * 100), 2) if total_cells > 0 else 0,
        "Duplicate Rows":        int(df.duplicated().sum()),
        "Memory Usage (MB)":     round(df.memory_usage(deep=True).sum() / 1024 ** 2, 2),
        "Numeric Columns":       len(df.select_dtypes(include="number").columns),
        "Categorical Columns":   len(df.select_dtypes(include="object").columns),
        "Datetime Columns":      len(df.select_dtypes(include="datetime").columns),
    }

    return summary


# --------------------------------------------------
# Column-Level Analysis
# --------------------------------------------------
def analyze_columns(df):
    """
    Analyze every column and produce per-column intelligence:
    data type, missing count, unique values, and a smart recommendation.

    BUG FIX: recommendation logic is now correctly INSIDE the for-loop.
    """
    column_info = []

    for column in df.columns:

        missing_pct = calculate_missing_percentage(df[column])

        info = {
            "Column":         column,
            "Data Type":      str(df[column].dtype),
            "Missing Values": int(df[column].isnull().sum()),
            "Missing %":      f"{missing_pct}%",
            "Unique Values":  int(df[column].nunique()),
            "Recommendation": "Healthy ✅"  # default — overridden below
        }

        # ---- Recommendation Rules (in priority order) ----

        if detect_primary_key(df[column]):
            recommendation = "Looks like Primary Key 🔑"

        elif detect_date_column(column) or detect_date_content(df[column]):
            recommendation = "Convert to Datetime 📅"

        elif detect_email_column(column):
            recommendation = "Validate Email Format 📧"

        elif detect_phone_column(column):
            recommendation = "Validate Phone Numbers 📱"

        elif missing_pct > 60:
            recommendation = "Very High Missing — Consider Dropping ❌"

        elif missing_pct > 30:
            recommendation = "High Missing Values ⚠️"

        elif df[column].isnull().sum() > 0:
            recommendation = "Contains Missing Values — Will Be Filled ⚠️"

        else:
            recommendation = "Healthy ✅"

        info["Recommendation"] = recommendation
        column_info.append(info)

    return pd.DataFrame(column_info)
