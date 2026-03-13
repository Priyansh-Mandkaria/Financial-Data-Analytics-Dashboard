# Financial Data Analytics Dashboard

> End-to-end financial data analytics platform featuring automated ETL pipelines, anomaly detection, reconciliation engine, and interactive dashboards.

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-2.2-150458?logo=pandas&logoColor=white)
![SQL](https://img.shields.io/badge/SQLite-3-003B57?logo=sqlite&logoColor=white)
![Plotly](https://img.shields.io/badge/Plotly_Dash-2.18-3F4F75?logo=plotly&logoColor=white)

## Key Highlights

- **50,000+ financial records** processed with data validation, reconciliation, and quality checks
- **Automated ETL pipeline** reducing manual data processing by 40%
- **Interactive dashboards** for benchmark tracking and anomaly detection
- **Root cause analysis** on data discrepancies with documented SOPs

## Tech Stack

| Technology | Usage |
|---|---|
| Python 3.10+ | Core language |
| Pandas & NumPy | Data manipulation and analysis |
| SQLite | Relational database with optimized queries |
| Plotly Dash | Interactive web dashboard |
| SciPy | Statistical anomaly detection |
| OpenPyXL | Automated Excel report generation |
| Power BI | Business intelligence dashboards (connects to SQLite DB) |

## Project Structure

```
├── run.py                        # Entry point (pipeline + dashboard)
├── data/
│   └── generate_data.py          # Synthetic data generator (52K+ records)
├── database/
│   ├── schema.sql                # SQLite schema (5 tables, indexed)
│   └── db_manager.py             # Connection pooling & query helpers
├── etl/
│   ├── pipeline.py               # ETL orchestrator with timing metrics
│   ├── extract.py                # CSV/Excel data ingestion
│   ├── transform.py              # Cleaning, validation, normalization
│   └── load.py                   # Bulk SQLite inserts
├── analytics/
│   ├── quality_checks.py         # Data quality scorecard
│   ├── anomaly_detection.py      # Z-score & IQR outlier detection
│   └── reconciliation.py         # Transaction-ledger matching
├── dashboard/
│   ├── app.py                    # Dash app with dark-theme UI
│   ├── layouts.py                # 4-page layouts
│   └── callbacks.py              # Interactive SQL-driven callbacks
├── reports/
│   └── excel_report.py           # Formatted Excel workbook generator
└── docs/
    └── SOP_Root_Cause_Analysis.md
```

## Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/Priyansh-Mandkaria/Financial-Data-Analytics-Dashboard.git
cd Financial-Data-Analytics-Dashboard

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run full pipeline + launch dashboard
python run.py

# 4. Open dashboard
# → http://127.0.0.1:8050
```

### Other Run Modes

```bash
python run.py --pipeline-only      # Run ETL without dashboard
python run.py --dashboard-only     # Launch dashboard (requires prior pipeline run)
python run.py --report-only        # Generate Excel report only
python run.py --port 8080          # Use custom port
python run.py --debug              # Enable hot-reload for development
```

## Dashboard Pages

### 1. Executive Overview
- KPI cards: total records, volume, avg transaction, completion rate, anomaly rate, quality score
- Monthly revenue vs. expense trend line chart
- Category distribution and status breakdown
- Top 10 counterparties by volume

### 2. Data Quality
- Quality scorecard with pass/fail rates per check
- Severity distribution (low / medium / high / critical)
- Detailed quality log table with conditional formatting

### 3. Anomaly Detection
- Z-score and IQR outlier scatter plots
- Anomaly breakdown by category and detection method
- Monthly anomaly timeline trend

### 4. Reconciliation
- Transaction-to-ledger match rate and waterfall chart
- Match status pie chart (perfect / mismatch / unmatched)
- Monthly discrepancy trend with dual axes

## ETL Pipeline

The automated pipeline processes data through 4 stages:

1. **Extract** — Read CSV source files into DataFrames
2. **Transform** — Clean, validate, deduplicate, normalize to USD
3. **Analyze** — Run quality checks, detect anomalies, reconcile ledger entries
4. **Load** — Bulk-insert into SQLite with timing metrics

Pipeline output includes a comparison against manual processing baseline, demonstrating **~40% time savings**.

## Power BI Integration

After running the pipeline, connect Power BI Desktop to the SQLite database:

1. Open Power BI Desktop
2. Get Data → ODBC → Connect to `database/financial_data.db`
3. Import tables: `transactions`, `ledger_entries`, `benchmarks`, `quality_log`, `anomaly_log`
4. Build dashboards using the pre-cleaned, analysis-ready data

## Excel Reports

Auto-generated reports include 6 sheets:
- Executive Summary
- Transaction Details
- Quality Report (with severity highlighting)
- Anomalies (sorted by score)
- Reconciliation Summary
- Benchmark Tracking (with status formatting)

## License

MIT