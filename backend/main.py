import sys
from pathlib import Path
import io
import uuid
import re
from typing import Optional, List, Dict, Any

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import pandas as pd
import numpy as np

from src.cleaner import clean_dataset, apply_column_fix
from src.profiler import dataset_summary, analyze_columns
from src.health import calculate_health_score, health_label
from src.smart_analyzer import build_cleaning_plan
from src.validator import (
    detect_outliers,
    detect_invalid_emails,
    detect_phone_numbers,
    detect_category_inconsistency,
    detect_constant_columns
)
from backend.services.insights import generate_data_insights, compute_column_distributions
from backend.services.pdf_report import generate_pdf_report

app = FastAPI(title="CleanIQ API", version="2.0.0", description="Backend Engine for CleanIQ")

# CORS middleware for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory session store for datasets
# Structure: { id: { "name": str, "original": df, "current": df, "history": [df], "fix_log": [] } }
DATASETS: Dict[str, Dict[str, Any]] = {}


import json

def clean_for_json(obj):
    if isinstance(obj, float):
        if np.isnan(obj) or np.isinf(obj):
            return None
        return obj
    elif isinstance(obj, dict):
        return {k: clean_for_json(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [clean_for_json(v) for v in obj]
    return obj


def serialize_df(df: pd.DataFrame, limit: int = 50) -> Dict[str, Any]:
    """Helper to convert DataFrame preview to JSON-safe structure."""
    df_head = df.head(limit).copy()
    
    # Format datetimes to strings
    for col in df_head.select_dtypes(include=["datetime", "datetimetz"]).columns:
        df_head[col] = df_head[col].astype(str)

    # pandas to_json natively converts NaN and inf to null
    records_json = df_head.to_json(orient="records", date_format="iso")
    records = json.loads(records_json)

    return {
        "columns": df.columns.tolist(),
        "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
        "total_rows": len(df),
        "total_columns": len(df.columns),
        "rows": records
    }


def run_quality_checks(df: pd.DataFrame) -> Dict[str, Any]:
    return {
        "Outliers Remaining": detect_outliers(df),
        "Invalid Emails": detect_invalid_emails(df),
        "Invalid Phone Numbers": detect_phone_numbers(df),
        "Category Inconsistencies": detect_category_inconsistency(df),
        "Constant Columns": detect_constant_columns(df)
    }


# -------------------------------------------------------------
# Request Models
# -------------------------------------------------------------
class FixRequest(BaseModel):
    column: str
    issue_type: str
    fix_action: str
    custom_value: Optional[str] = None


class FindReplaceRequest(BaseModel):
    find_value: str
    replace_value: str
    columns: Optional[List[str]] = None  # None or empty = all columns
    is_regex: bool = False
    match_case: bool = False


# -------------------------------------------------------------
# Endpoints
# -------------------------------------------------------------

@app.get("/api/health")
def api_health():
    return {"status": "ok", "app": "CleanIQ Backend Engine"}


@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    filename = file.filename or "dataset.csv"
    contents = await file.read()
    
    try:
        if filename.lower().endswith(".csv"):
            try:
                df = pd.read_csv(io.BytesIO(contents), encoding="utf-8")
            except UnicodeDecodeError:
                df = pd.read_csv(io.BytesIO(contents), encoding="latin-1")
        elif filename.lower().endswith((".xlsx", ".xls")):
            df = pd.read_excel(io.BytesIO(contents))
        else:
            raise HTTPException(status_code=400, detail="Unsupported file format. Please upload CSV or Excel.")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse file: {str(e)}")

    dataset_id = str(uuid.uuid4())
    DATASETS[dataset_id] = {
        "name": filename,
        "original": df.copy(),
        "current": df.copy(),
        "history": [df.copy()],
        "fix_log": []
    }

    summary = dataset_summary(df)
    score = calculate_health_score(summary)

    return {
        "dataset_id": dataset_id,
        "filename": filename,
        "summary": summary,
        "health_score": score,
        "health_label": health_label(score),
        "preview": serialize_df(df, limit=20)
    }


@app.post("/api/load-demo")
def load_demo_dataset():
    """Loads a pre-built rich dataset with real-world dirty data patterns for instant testing."""
    np.random.seed(42)
    n = 250
    
    names = ["Alice Smith", "bob jones", "BOB JONES", "Charlie Brown", "Diana Prince", "Evan Wright", None]
    genders = ["Male", "male", "MALE", "Female", "female", "FEMALE", None]
    departments = ["Engineering", "engineering", "HR", "hr", "Marketing", "Sales", "Finance", None]
    emails = ["alice@company.com", "invalid_email@", "charlie#domain.com", "diana@corp.org", None, "evan@tech.io"]
    phones = ["+91-98765-43210", "1234567890", "(555) 234-5678", "invalid_phone", "9876543210", None]
    
    demo_df = pd.DataFrame({
        "Employee_ID": [1000 + i for i in range(n)],
        "Full_Name": np.random.choice(names, size=n),
        "Age": np.random.choice([22, 28, 35, 42, 55, -5, -12, 135, None], size=n),
        "Salary": np.random.choice([45000, 62000, 78000, 95000, -2000, 99999999, None], size=n),
        "Email": np.random.choice(emails, size=n),
        "Phone": np.random.choice(phones, size=n),
        "Gender": np.random.choice(genders, size=n),
        "Department": np.random.choice(departments, size=n),
        "Performance_Score": np.random.choice([75.5, 88.0, 92.5, 64.0, 105.0, -10.0, None], size=n),
        "Joining_Date": np.random.choice(["2021-03-15", "2020-07-20", "2022-11-01", "not-a-date", None], size=n),
        "System_Flag": ["Active"] * n  # Near constant column test
    })

    dataset_id = str(uuid.uuid4())
    DATASETS[dataset_id] = {
        "name": "Global_Enterprise_Staff_2026.csv",
        "original": demo_df.copy(),
        "current": demo_df.copy(),
        "history": [demo_df.copy()],
        "fix_log": []
    }

    summary = dataset_summary(demo_df)
    score = calculate_health_score(summary)

    return {
        "dataset_id": dataset_id,
        "filename": "Global_Enterprise_Staff_2026.csv",
        "summary": summary,
        "health_score": score,
        "health_label": health_label(score),
        "preview": serialize_df(demo_df, limit=20)
    }


@app.get("/api/dataset/{dataset_id}/data")
def get_dataset_data(dataset_id: str, limit: int = 100):
    if dataset_id not in DATASETS:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    df = DATASETS[dataset_id]["current"]
    summary = dataset_summary(df)
    score = calculate_health_score(summary)

    return {
        "dataset_id": dataset_id,
        "name": DATASETS[dataset_id]["name"],
        "summary": summary,
        "health_score": score,
        "health_label": health_label(score),
        "preview": serialize_df(df, limit=limit),
        "can_undo": len(DATASETS[dataset_id]["history"]) > 1,
        "fix_log": DATASETS[dataset_id]["fix_log"]
    }


@app.get("/api/dataset/{dataset_id}/columns")
def get_columns_analysis(dataset_id: str):
    if dataset_id not in DATASETS:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    df = DATASETS[dataset_id]["current"]
    cols_df = analyze_columns(df)
    return {"columns": cols_df.to_dict(orient="records")}


@app.get("/api/dataset/{dataset_id}/distributions")
def get_distributions(dataset_id: str):
    if dataset_id not in DATASETS:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    df = DATASETS[dataset_id]["current"]
    return {"distributions": compute_column_distributions(df)}


@app.get("/api/dataset/{dataset_id}/insights")
def get_insights(dataset_id: str):
    if dataset_id not in DATASETS:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    df = DATASETS[dataset_id]["current"]
    return generate_data_insights(df)


@app.get("/api/dataset/{dataset_id}/smart-plan")
def get_smart_plan(dataset_id: str):
    if dataset_id not in DATASETS:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    df = DATASETS[dataset_id]["current"]
    plan = build_cleaning_plan(df)
    return {"plan": plan}


@app.post("/api/dataset/{dataset_id}/apply-fix")
def apply_fix(dataset_id: str, req: FixRequest):
    if dataset_id not in DATASETS:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    session = DATASETS[dataset_id]
    current_df = session["current"]
    
    # Save previous state in history
    session["history"].append(current_df.copy())
    
    # Execute single column fix
    updated_df, desc = apply_column_fix(
        current_df,
        column=req.column,
        issue_type=req.issue_type,
        fix_action=req.fix_action,
        custom_value=req.custom_value
    )
    
    session["current"] = updated_df
    session["fix_log"].append({
        "Column": req.column,
        "Issue": req.issue_type,
        "Action": req.fix_action,
        "Fix Applied": desc
    })

    summary = dataset_summary(updated_df)
    score = calculate_health_score(summary)

    return {
        "success": True,
        "message": desc,
        "summary": summary,
        "health_score": score,
        "health_label": health_label(score),
        "preview": serialize_df(updated_df, limit=20),
        "can_undo": len(session["history"]) > 1,
        "fix_log": session["fix_log"]
    }


@app.post("/api/dataset/{dataset_id}/auto-clean")
def auto_clean(dataset_id: str):
    if dataset_id not in DATASETS:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    session = DATASETS[dataset_id]
    current_df = session["current"]
    session["history"].append(current_df.copy())

    cleaned_df, report = clean_dataset(current_df)
    session["current"] = cleaned_df
    
    for step, res in report.items():
        if step not in ["Rows Before", "Rows After", "Columns Before", "Columns After"]:
            session["fix_log"].append({
                "Column": "All / Pipeline",
                "Issue": "Auto-Clean",
                "Action": step,
                "Fix Applied": str(res)
            })

    summary = dataset_summary(cleaned_df)
    score = calculate_health_score(summary)

    return {
        "success": True,
        "report": report,
        "summary": summary,
        "health_score": score,
        "health_label": health_label(score),
        "preview": serialize_df(cleaned_df, limit=20),
        "can_undo": len(session["history"]) > 1,
        "fix_log": session["fix_log"]
    }


@app.post("/api/dataset/{dataset_id}/undo")
def undo_fix(dataset_id: str):
    if dataset_id not in DATASETS:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    session = DATASETS[dataset_id]
    if len(session["history"]) <= 1:
        raise HTTPException(status_code=400, detail="Nothing to undo.")
    
    # Pop the last state
    previous_df = session["history"].pop()
    session["current"] = previous_df
    if session["fix_log"]:
        session["fix_log"].pop()

    summary = dataset_summary(previous_df)
    score = calculate_health_score(summary)

    return {
        "success": True,
        "message": "Reverted to previous dataset state.",
        "summary": summary,
        "health_score": score,
        "health_label": health_label(score),
        "preview": serialize_df(previous_df, limit=20),
        "can_undo": len(session["history"]) > 1,
        "fix_log": session["fix_log"]
    }


@app.post("/api/dataset/{dataset_id}/reset")
def reset_dataset(dataset_id: str):
    if dataset_id not in DATASETS:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    session = DATASETS[dataset_id]
    original = session["original"].copy()
    session["history"] = [original.copy()]
    session["current"] = original.copy()
    session["fix_log"] = []

    summary = dataset_summary(original)
    score = calculate_health_score(summary)

    return {
        "success": True,
        "message": "Reset dataset to originally uploaded raw state.",
        "summary": summary,
        "health_score": score,
        "health_label": health_label(score),
        "preview": serialize_df(original, limit=20),
        "can_undo": False,
        "fix_log": []
    }


@app.post("/api/dataset/{dataset_id}/find-replace")
def find_and_replace(dataset_id: str, req: FindReplaceRequest):
    if dataset_id not in DATASETS:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    session = DATASETS[dataset_id]
    df = session["current"].copy()
    session["history"].append(df.copy())

    target_cols = req.columns if req.columns and len(req.columns) > 0 else df.columns.tolist()
    total_replaced = 0

    replace_target = np.nan if req.replace_value in ["", "null", "NaN", "NAN", "None"] else req.replace_value

    for col in target_cols:
        if col not in df.columns:
            continue
        
        # Exact match or regex match
        if req.is_regex:
            mask = df[col].astype(str).str.contains(req.find_value, regex=True, case=req.match_case, na=False)
            total_replaced += int(mask.sum())
            df[col] = df[col].astype(str).str.replace(req.find_value, str(replace_target) if not pd.isna(replace_target) else "", regex=True)
            if pd.isna(replace_target):
                df.loc[mask, col] = np.nan
        else:
            if req.match_case:
                mask = df[col].astype(str) == req.find_value
            else:
                mask = df[col].astype(str).str.lower() == req.find_value.lower()
            
            total_replaced += int(mask.sum())
            df.loc[mask, col] = replace_target

    session["current"] = df
    desc = f"Replaced {total_replaced} occurrences of '{req.find_value}' with '{req.replace_value}' across {len(target_cols)} column(s)."
    session["fix_log"].append({
        "Column": ", ".join(target_cols[:3]) + ("..." if len(target_cols) > 3 else ""),
        "Issue": "Find & Replace",
        "Action": f"'{req.find_value}' -> '{req.replace_value}'",
        "Fix Applied": desc
    })

    summary = dataset_summary(df)
    score = calculate_health_score(summary)

    return {
        "success": True,
        "message": desc,
        "replaced_count": total_replaced,
        "summary": summary,
        "health_score": score,
        "health_label": health_label(score),
        "preview": serialize_df(df, limit=20),
        "can_undo": True,
        "fix_log": session["fix_log"]
    }


@app.get("/api/dataset/{dataset_id}/compare")
def compare_before_after(dataset_id: str, limit: int = 50):
    if dataset_id not in DATASETS:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    session = DATASETS[dataset_id]
    orig_df = session["original"]
    curr_df = session["current"]

    rows_before = len(orig_df)
    rows_after = len(curr_df)
    cols_before = len(orig_df.columns)
    cols_after = len(curr_df.columns)

    # Calculate modified cells for overlapping rows and columns
    common_cols = [c for c in orig_df.columns if c in curr_df.columns]
    common_len = min(rows_before, rows_after)
    
    diff_cells_count = 0
    diff_preview = []

    for i in range(min(common_len, limit)):
        row_orig = orig_df.iloc[i]
        row_curr = curr_df.iloc[i]
        row_diff = {"row_index": i, "has_diff": False, "fields": {}}

        for c in common_cols:
            v1 = row_orig[c]
            v2 = row_curr[c]
            
            # Check equality accounting for NaN
            is_different = False
            if pd.isna(v1) and pd.isna(v2):
                is_different = False
            elif pd.isna(v1) != pd.isna(v2):
                is_different = True
            elif str(v1) != str(v2):
                is_different = True

            if is_different:
                diff_cells_count += 1
                row_diff["has_diff"] = True

            row_diff["fields"][c] = {
                "before": str(v1) if not pd.isna(v1) else "null",
                "after": str(v2) if not pd.isna(v2) else "null",
                "changed": is_different
            }
        diff_preview.append(row_diff)

    return {
        "stats": {
            "rows_before": rows_before,
            "rows_after": rows_after,
            "rows_delta": rows_after - rows_before,
            "columns_before": cols_before,
            "columns_after": cols_after,
            "diff_cells_in_sample": diff_cells_count,
            "common_columns": common_cols
        },
        "diff_sample": diff_preview
    }


@app.get("/api/dataset/{dataset_id}/quality-report")
def get_quality_report(dataset_id: str):
    if dataset_id not in DATASETS:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    df = DATASETS[dataset_id]["current"]
    checks = run_quality_checks(df)
    return {"quality_report": checks}


@app.get("/api/dataset/{dataset_id}/export/{format_type}")
def export_dataset(dataset_id: str, format_type: str):
    if dataset_id not in DATASETS:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    session = DATASETS[dataset_id]
    df = session["current"]
    base_name = Path(session["name"]).stem

    if format_type == "csv":
        csv_bytes = df.to_csv(index=False).encode("utf-8")
        return StreamingResponse(
            io.BytesIO(csv_bytes),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={base_name}_cleaned.csv"}
        )

    elif format_type == "excel":
        excel_buffer = io.BytesIO()
        with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="CleanedData")
        excel_buffer.seek(0)
        return StreamingResponse(
            excel_buffer,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={base_name}_cleaned.xlsx"}
        )

    elif format_type == "json":
        json_str = df.to_json(orient="records", indent=2)
        return StreamingResponse(
            io.BytesIO(json_str.encode("utf-8")),
            media_type="application/json",
            headers={"Content-Disposition": f"attachment; filename={base_name}_cleaned.json"}
        )

    elif format_type == "pdf":
        summary = dataset_summary(df)
        score = calculate_health_score(summary)
        quality = run_quality_checks(df)
        pdf_data = generate_pdf_report(
            dataset_name=session["name"],
            summary=summary,
            health_score=score,
            fix_log=session["fix_log"],
            quality_report=quality
        )
        return StreamingResponse(
            io.BytesIO(pdf_data),
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={base_name}_CleanIQ_Report.pdf"}
        )

    else:
        raise HTTPException(status_code=400, detail="Invalid format. Supported formats: csv, excel, json, pdf")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
