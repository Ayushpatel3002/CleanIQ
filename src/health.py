def calculate_health_score(summary):
    """
    Calculates a data quality health score from 0 to 100.

    BUG FIX: Old scoring was binary (1 missing value = -20, same as 90% missing).
    New scoring is PROPORTIONAL — penalizes based on actual % of issues,
    with different max penalties per category.

    Scoring breakdown:
      - Missing values:   up to -35 pts (proportional to % of missing cells)
      - Duplicate rows:   up to -25 pts (proportional to % of duplicate rows)
      - No numeric cols:  -5  pts flat  (limits analytical value)
      - High cardinality: no penalty (informational only)
    """
    score = 100.0

    rows    = summary.get("Rows", 1) or 1
    columns = summary.get("Columns", 1) or 1

    # -------------------------------------------------------
    # Penalty 1: Missing Values (proportional, max -35 pts)
    # -------------------------------------------------------
    missing_total = summary.get("Missing Values", 0)
    total_cells   = rows * columns

    if missing_total > 0 and total_cells > 0:
        missing_pct = (missing_total / total_cells) * 100
        # Scales from 0 at 0% missing to -35 at 100% missing
        missing_penalty = min(35, missing_pct * 0.35)
        score -= missing_penalty

    # -------------------------------------------------------
    # Penalty 2: Duplicate Rows (proportional, max -25 pts)
    # -------------------------------------------------------
    duplicate_rows = summary.get("Duplicate Rows", 0)

    if duplicate_rows > 0:
        dup_pct = (duplicate_rows / rows) * 100
        dup_penalty = min(25, dup_pct * 0.5)
        score -= dup_penalty

    # -------------------------------------------------------
    # Penalty 3: No Numeric Columns (flat, -5 pts)
    # -------------------------------------------------------
    if summary.get("Numeric Columns", 0) == 0:
        score -= 5

    # Clamp to [0, 100]
    return max(0, round(score, 1))


def health_label(score):
    """
    Returns a human-readable label for a health score.
    """
    if score >= 90:
        return "Excellent 🟢"
    elif score >= 75:
        return "Good 🟡"
    elif score >= 50:
        return "Fair 🟠"
    else:
        return "Poor 🔴"