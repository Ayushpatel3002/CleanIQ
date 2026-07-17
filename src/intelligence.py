def detect_primary_key(series):
    """
    Detect if a column looks like a Primary Key.
    """

    total_rows = len(series)

    unique_values = series.nunique()

    missing = series.isnull().sum()

    if unique_values == total_rows and missing == 0:
        return True

    return False

def detect_date_column(column_name):
    """
    Detect possible Date columns.
    """

    keywords = [

        "date",

        "dob",

        "birth",

        "joining"

    ]

    column_name = column_name.lower()

    return any(word in column_name for word in keywords)

def calculate_missing_percentage(series):

    return round(

        (series.isnull().sum()/len(series))*100,

        2

    )
def detect_email_column(column_name):
    """
    Detect possible email columns.
    """

    keywords = [
        "email",
        "mail",
        "gmail"
    ]

    column_name = column_name.lower()

    return any(word in column_name for word in keywords)
def detect_phone_column(column_name):
    """
    Detect possible phone number columns.
    """

    keywords = [
        "phone",
        "mobile",
        "contact",
        "telephone"
    ]

    column_name = column_name.lower()

    return any(word in column_name for word in keywords)
