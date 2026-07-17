def calculate_health_score(summary):
    """
    Calculate dataset health score.
    """

    score = 100

    # Missing Values
    if summary["Missing Values"] > 0:
        score -= 20

    # Duplicate Rows
    if summary["Duplicate Rows"] > 0:
        score -= 15

    # No Numeric Columns
    if summary["Numeric Columns"] == 0:
        score -= 10

    if score < 0:
        score = 0

    return score