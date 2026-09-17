import pandas as pd


# --------------------------------------------------
# Detect Primary Key
# --------------------------------------------------
def detect_primary_key(series):
    """
    Detect if a column looks like a Primary Key.
    Must be fully unique, no nulls, and not a float column.
    """
    total_rows = len(series)
    unique_values = series.nunique()
    missing = series.isnull().sum()

    if unique_values == total_rows and missing == 0:
        return True

    return False


# --------------------------------------------------
# Detect Date Column by Name
# --------------------------------------------------
def detect_date_column(column_name):
    """
    Detect possible Date columns by their name keywords.
    """
    keywords = [
        "date", "dob", "birth", "joining",
        "created", "updated", "timestamp",
        "time", "year", "month", "day"
    ]
    column_name = column_name.lower()
    return any(word in column_name for word in keywords)


# --------------------------------------------------
# Detect Date Column by Content (smart sampling)
# --------------------------------------------------
def detect_date_content(series, sample_size=50, threshold=0.7):
    """
    Detect if a column's values look like dates by sampling
    and attempting to parse them — catches columns named
    generically like 'col1' or 'field_3'.
    Only applies to object/string dtype columns.
    """
    if not pd.api.types.is_object_dtype(series):
        return False

    sample = series.dropna().head(sample_size)

    if len(sample) == 0:
        return False

    try:
        parsed = pd.to_datetime(sample, errors="coerce")
        success_rate = parsed.notnull().sum() / len(sample)
        return success_rate >= threshold
    except Exception:
        return False


# --------------------------------------------------
# Calculate Missing Percentage
# --------------------------------------------------
def calculate_missing_percentage(series):
    """
    Returns the percentage of missing values in a series.
    """
    if len(series) == 0:
        return 0.0
    return round((series.isnull().sum() / len(series)) * 100, 2)


# --------------------------------------------------
# Detect Email Column by Name
# --------------------------------------------------
def detect_email_column(column_name):
    """
    Detect possible email columns by name keywords.
    """
    keywords = ["email", "mail", "gmail", "e-mail"]
    column_name = column_name.lower()
    return any(word in column_name for word in keywords)


# --------------------------------------------------
# Detect Phone Column by Name
# --------------------------------------------------
def detect_phone_column(column_name):
    """
    Detect possible phone number columns by name keywords.
    """
    keywords = ["phone", "mobile", "contact", "telephone", "cell", "fax"]
    column_name = column_name.lower()
    return any(word in column_name for word in keywords)
