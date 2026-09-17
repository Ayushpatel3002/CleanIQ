# 🧹 CleanIQ — AI-Powered Autonomous Data Cleaning & Intelligence Platform

[![React](https://img.shields.io/badge/Frontend-React%2018%20%7C%20TypeScript%20%7C%20Tailwind-61DAFB?style=flat-square&logo=react)](https://reactjs.org/)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI%20%7C%20Python%203.11+-009688?style=flat-square&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Pandas](https://img.shields.io/badge/Data%20Engine-Pandas%20%7C%20NumPy-150458?style=flat-square&logo=pandas)](https://pandas.pydata.org/)
[![Vite](https://img.shields.io/badge/Build-Vite%206-646CFF?style=flat-square&logo=vite)](https://vitejs.dev/)
[![Streamlit Demo](https://img.shields.io/badge/Live%20Demo-Streamlit%20Cloud-FF4B4B?style=flat-square&logo=streamlit)](https://cleaniq-ayush.streamlit.app/)

> **CleanIQ** is a full-fledged, modern data cleaning & analytics platform designed to automate data profiling, detect semantic anomalies (negative ages, malformed emails, invalid phones, extreme outliers), provide interactive user remediation, and export publication-ready datasets with executive audit reports.

---

## 🌐 Live Demos & Links

- **Streamlit Prototype App**: [https://cleaniq-ayush.streamlit.app/](https://cleaniq-ayush.streamlit.app/)
- **Full-Stack Web App**: Runs locally on `http://localhost:3000` with FastAPI on `http://127.0.0.1:8000`

---

## 🌟 Key Features

### 1. 📊 Overview & Dataset Profile
- **Dataset Health Index**: Instant 0–100 quality score with circular progress and status indicators.
- **Summary Metrics**: Rows, Columns, Missing count/%, Duplicate rows, Memory footprint (MB), Numeric/Categorical/Datetime counts.
- **AI Column Intelligence**: Automated detection of Primary Keys, Phone numbers, Dates, Emails, and severe missingness.
- **Live Data Preview**: Responsive, high-performance data grid with null highlighting.

### 2. 📈 Interactive Visual Distributions & Skewness
- **Numeric Histograms (Recharts)**: Frequency bins, min/max/mean/median/std dev, and automated skewness analysis (e.g. *Right-skewed tail → Median fill recommended*).
- **Categorical Breakdowns**: Horizontal frequency bars with unique counts and percentage shares.

### 3. 💡 Deep Data Insights
- **Autonomous Quality Verdict**: Executive summary of data readiness.
- **Domain Anomaly Alerts**: Flags negative values in non-negative domains (Age, Salary, Price, etc.).
- **Distribution & Missingness Warnings**: High cardinality and severe class imbalance detection.
- **Feature Correlation Engine**: Pearson correlation matrix highlighting strong positive and negative relationships.

### 4. 🧠 Interactive Smart Clean (AI Per-Column Remediation)
- **Domain Semantic Type Detection**: Age, Salary, Email, Phone, Gender, Status, Percentage, Date, etc.
- **Customizable Policy Selectors**: Choose from ranked fix options with AI recommended defaults pre-selected.
- **Custom Fill Value Support**: Dynamically input user-defined replacement values.
- **Global Find & Replace Utility**: Regex and exact match search across all columns or target columns.
- **Audit Trail & Fix Log**: Detailed log tracking every single remediation step applied.
- **Multi-Step Undo Stack**: Revert any action at any time with one click.

### 5. 🔄 Before vs After Side-by-Side Diff
- Visual comparison of original raw data vs cleaned state.
- Modified and imputed cells highlighted in amber.
- Row-level status badges (*Modified* vs *Identical*).

### 6. 🔍 Quality & Sanity Audit
- Expandable accordions for Outliers (IQR fences), Malformed Emails, Invalid Phone formats, Casing variants, and Constant columns.

### 7. 💾 Multi-Format Export & Integration
- **Direct Downloads**: Cleaned `.csv`, formatted Excel `.xlsx`, `.json` records.
- **Executive Audit PDF**: Download formal PDF summary reports containing health scores, fix logs, and quality checks.
- **Database Streaming**: Export directly to MySQL / MariaDB, PostgreSQL, or Data Warehouses.

---

## 🚀 How to Run Locally

### 1. Clone the Repository
```bash
git clone https://github.com/Ayushpatel3002/CleanIQ.git
cd CleanIQ
```

### 2. Setup Backend & Python Environment
```bash
# Create and activate virtual environment
python -m venv venv
venv\Scripts\activate  # On macOS/Linux: source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start FastAPI Backend Server
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
```
> API Swagger Documentation will be accessible at: `http://127.0.0.1:8000/docs`

### 3. Setup Frontend (React 18 + Vite)
```bash
cd frontend
npm install
npm run dev
```
> CleanIQ Web Platform will open at: **`http://localhost:3000`**

### 4. Alternative: Run Classic Streamlit App
```bash
streamlit run app.py
```

---

## 🏗 Architecture & Tech Stack

| Layer | Technologies |
|---|---|
| **Frontend UI** | React 18, TypeScript, Tailwind CSS, Lucide Icons, Recharts |
| **Build & Tooling** | Vite 6, PostCSS, Autoprefixer |
| **Backend API** | FastAPI, Starlette, Pydantic v2, Uvicorn |
| **Data Engine** | Pandas, NumPy, OpenPyXL, SQLAlchemy, ReportLab |
| **Cloud Deployment** | Streamlit Community Cloud (Classic), Docker ready |

---

## 👨‍💻 Author

**Ayush Patel**
- GitHub: [@Ayushpatel3002](https://github.com/Ayushpatel3002)
- Live Prototype: [cleaniq-ayush.streamlit.app](https://cleaniq-ayush.streamlit.app/)
