import pandas as pd
import numpy as np


def generate_data_insights(df: pd.DataFrame) -> dict:
    """
    Generate deep analytical insights, statistical patterns, and automated
    recommendations for a dataset.
    """
    total_rows = len(df)
    total_cols = len(df.columns)
    if total_rows == 0 or total_cols == 0:
        return {"insights": [], "correlations": [], "summary_verdict": "Empty dataset"}

    insights = []
    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    categorical_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()

    # 1. High Missing Values Analysis
    missing_series = df.isnull().sum()
    high_missing = missing_series[missing_series / total_rows > 0.4]
    if not high_missing.empty:
        for col, cnt in high_missing.items():
            pct = round((cnt / total_rows) * 100, 1)
            insights.append({
                "type": "warning",
                "category": "Missing Data",
                "title": f"Critical Missing Rate in '{col}'",
                "description": f"Column '{col}' has {cnt} missing values ({pct}%). Consider dropping this column or imputing with a default category placeholder.",
                "column": col,
                "importance": "High"
            })

    # 2. Skewness & Distribution Insights for Numeric Columns
    for col in numeric_cols:
        non_null = df[col].dropna()
        if len(non_null) > 5:
            skew = non_null.skew()
            mean_val = float(non_null.mean())
            median_val = float(non_null.median())
            
            # Significant difference between mean and median indicates heavy skew or outliers
            if abs(skew) > 1.5:
                direction = "right (positively)" if skew > 0 else "left (negatively)"
                insights.append({
                    "type": "info",
                    "category": "Distribution Skew",
                    "title": f"High Skewness in '{col}' ({round(skew, 2)})",
                    "description": f"Values are heavily skewed to the {direction}. Mean ({round(mean_val, 2)}) diverges from Median ({round(median_val, 2)}). We recommend using Median imputation or Log transformation for modeling.",
                    "column": col,
                    "importance": "Medium"
                })

            # Check for negative values in potential non-negative columns
            neg_count = (non_null < 0).sum()
            col_lower = col.lower()
            if neg_count > 0 and any(k in col_lower for k in ["age", "salary", "price", "revenue", "count", "score", "qty"]):
                insights.append({
                    "type": "danger",
                    "category": "Domain Anomaly",
                    "title": f"Invalid Negative Values in '{col}'",
                    "description": f"Found {neg_count} negative entries in '{col}', which represents a non-negative domain. These should be converted via absolute value or replaced.",
                    "column": col,
                    "importance": "High"
                })

    # 3. Categorical Imbalance & High Cardinality
    for col in categorical_cols:
        non_null = df[col].dropna()
        if len(non_null) > 0:
            n_unique = non_null.nunique()
            ratio = n_unique / len(non_null)
            
            if ratio > 0.8 and n_unique > 20:
                insights.append({
                    "type": "info",
                    "category": "High Cardinality",
                    "title": f"Near-Unique Text Column '{col}'",
                    "description": f"Contains {n_unique} unique values across {len(non_null)} records ({round(ratio*100, 1)}% unique). Likely an Identifier, Free-Text, or UUID rather than a category.",
                    "column": col,
                    "importance": "Low"
                })
            elif n_unique <= 10:
                top_val_share = non_null.value_counts(normalize=True).iloc[0]
                if top_val_share > 0.85:
                    top_name = non_null.value_counts().index[0]
                    insights.append({
                        "type": "warning",
                        "category": "Class Imbalance",
                        "title": f"Severe Class Imbalance in '{col}'",
                        "description": f"Dominant category '{top_name}' accounts for {round(top_val_share*100, 1)}% of all entries. May lack predictive diversity.",
                        "column": col,
                        "importance": "Medium"
                    })

    # 4. Correlation Highlights (Pairs with strong relationship)
    correlations = []
    if len(numeric_cols) >= 2:
        try:
            corr_df = df[numeric_cols].corr()
            for i in range(len(numeric_cols)):
                for j in range(i + 1, len(numeric_cols)):
                    c1 = numeric_cols[i]
                    c2 = numeric_cols[j]
                    val = corr_df.loc[c1, c2]
                    if not np.isnan(val):
                        correlations.append({
                            "col1": c1,
                            "col2": c2,
                            "correlation": round(float(val), 3)
                        })
                        if abs(val) >= 0.7:
                            rel_type = "Strong Positive" if val > 0 else "Strong Negative"
                            insights.append({
                                "type": "success" if val > 0 else "info",
                                "category": "Correlation Pattern",
                                "title": f"{rel_type} Correlation: {c1} & {c2}",
                                "description": f"Correlation coefficient is {round(val, 2)}. Variations in '{c1}' strongly align with '{c2}'. Watch for multicollinearity in predictive models.",
                                "column": f"{c1} + {c2}",
                                "importance": "Medium"
                            })
        except Exception:
            pass

    # Overall Summary Verdict
    health_issues_count = len([i for i in insights if i["type"] in ["danger", "warning"]])
    if health_issues_count == 0:
        verdict = "Dataset is clean and well-structured for immediate statistical analysis and downstream workflows."
    elif health_issues_count <= 2:
        verdict = "Minor data quality findings detected. Quick remediation in Smart Clean will make this analysis-ready."
    else:
        verdict = f"{health_issues_count} significant data quality anomalies detected. Applying recommended cleaning steps is strongly advised."

    return {
        "insights": insights,
        "correlations": sorted(correlations, key=lambda x: abs(x["correlation"]), reverse=True)[:15],
        "summary_verdict": verdict,
        "total_insights": len(insights)
    }


def compute_column_distributions(df: pd.DataFrame) -> dict:
    """
    Computes histogram bins and value frequency distributions for frontend charts.
    """
    distributions = {}

    for col in df.columns:
        series = df[col]
        non_null = series.dropna()
        if len(non_null) == 0:
            continue

        if pd.api.types.is_numeric_dtype(series):
            try:
                counts, bin_edges = np.histogram(non_null, bins=min(12, max(5, non_null.nunique())))
                bins_data = []
                for i in range(len(counts)):
                    bins_data.append({
                        "range": f"{round(bin_edges[i], 1)} - {round(bin_edges[i+1], 1)}",
                        "count": int(counts[i]),
                        "midpoint": round((bin_edges[i] + bin_edges[i+1]) / 2, 2)
                    })
                
                distributions[col] = {
                    "kind": "numeric",
                    "bins": bins_data,
                    "stats": {
                        "min": round(float(non_null.min()), 2),
                        "max": round(float(non_null.max()), 2),
                        "mean": round(float(non_null.mean()), 2),
                        "median": round(float(non_null.median()), 2),
                        "std": round(float(non_null.std()), 2) if len(non_null) > 1 else 0.0,
                        "skew": round(float(non_null.skew()), 2) if len(non_null) > 2 else 0.0
                    }
                }
            except Exception:
                pass

        elif pd.api.types.is_object_dtype(series) or pd.api.types.is_categorical_dtype(series):
            try:
                top_counts = non_null.astype(str).value_counts().head(8)
                cat_data = [{"label": str(k), "count": int(v)} for k, v in top_counts.items()]
                distributions[col] = {
                    "kind": "categorical",
                    "categories": cat_data,
                    "total_unique": int(non_null.nunique())
                }
            except Exception:
                pass

    return distributions
