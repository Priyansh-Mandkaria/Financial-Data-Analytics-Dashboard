"""
ETL Pipeline Orchestrator
Runs the full Extract → Transform → Load pipeline with timing metrics.
"""

import time
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.generate_data import generate_all_data
from database.db_manager import initialize_database, get_table_counts
from etl.extract import extract_all
from etl.transform import transform_transactions, transform_ledger, transform_benchmarks
from etl.load import load_all
from analytics.quality_checks import run_quality_checks
from analytics.anomaly_detection import detect_anomalies
from analytics.reconciliation import run_reconciliation


def simulate_manual_baseline(num_records: int) -> float:
    """Simulate how long manual processing would take (for comparison metrics)."""
    # Estimate: manual processing ~0.5s per 100 records (spreadsheet-based)
    manual_time = (num_records / 100) * 0.5
    return manual_time


def run_pipeline(base_dir: str = None) -> dict:
    """
    Execute the full ETL pipeline.
    Returns metrics dictionary.
    """
    if base_dir is None:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    raw_dir = os.path.join(base_dir, 'data', 'raw')
    metrics = {}

    print("=" * 65)
    print("   FINANCIAL DATA ANALYTICS — ETL PIPELINE")
    print("=" * 65)

    pipeline_start = time.time()

    # ── Step 1: Generate Data ──
    step_start = time.time()
    raw_data = generate_all_data(raw_dir)
    metrics['generate_time'] = time.time() - step_start

    # ── Step 2: Initialize Database ──
    step_start = time.time()
    initialize_database()
    metrics['db_init_time'] = time.time() - step_start

    # ── Step 3: Extract ──
    step_start = time.time()
    extracted = extract_all(raw_dir)
    metrics['extract_time'] = time.time() - step_start

    # ── Step 4: Transform ──
    step_start = time.time()
    cleaned_transactions, transform_issues = transform_transactions(extracted['transactions'])
    cleaned_ledger = transform_ledger(extracted['ledger_entries'])
    cleaned_benchmarks = transform_benchmarks(extracted['benchmarks'])
    metrics['transform_time'] = time.time() - step_start

    # ── Step 5: Analytics (pre-load) ──
    step_start = time.time()
    quality_results = run_quality_checks(cleaned_transactions, transform_issues)
    anomalies_df = detect_anomalies(cleaned_transactions)
    recon_results = run_reconciliation(cleaned_transactions, cleaned_ledger)
    metrics['analytics_time'] = time.time() - step_start

    # ── Step 6: Load ──
    step_start = time.time()
    cleaned_data = {
        'transactions': cleaned_transactions,
        'ledger_entries': cleaned_ledger,
        'benchmarks': cleaned_benchmarks,
    }
    load_counts = load_all(cleaned_data, quality_results, anomalies_df)
    metrics['load_time'] = time.time() - step_start

    # ── Pipeline Summary ──
    pipeline_elapsed = time.time() - pipeline_start
    metrics['total_pipeline_time'] = pipeline_elapsed

    total_records = sum(len(df) for df in cleaned_data.values())
    manual_estimate = simulate_manual_baseline(total_records)
    metrics['manual_estimate'] = manual_estimate
    metrics['time_savings_pct'] = round((1 - pipeline_elapsed / manual_estimate) * 100, 1)

    # Get final DB counts
    db_counts = get_table_counts()
    metrics['db_counts'] = db_counts

    print("\n" + "=" * 65)
    print("   PIPELINE SUMMARY")
    print("=" * 65)
    print(f"\n  Total Records Processed:  {total_records:>10,}")
    print(f"  Pipeline Execution Time:  {pipeline_elapsed:>10.2f}s")
    print(f"  Manual Estimate:          {manual_estimate:>10.2f}s")
    print(f"  Time Savings:             {metrics['time_savings_pct']:>9}%")
    print(f"\n  Database Record Counts:")
    for table, count in db_counts.items():
        print(f"    {table:<20} {count:>8,}")
    print(f"\n  Step Timings:")
    print(f"    Data Generation:   {metrics['generate_time']:>8.2f}s")
    print(f"    DB Initialization: {metrics['db_init_time']:>8.2f}s")
    print(f"    Extraction:        {metrics['extract_time']:>8.2f}s")
    print(f"    Transformation:    {metrics['transform_time']:>8.2f}s")
    print(f"    Analytics:         {metrics['analytics_time']:>8.2f}s")
    print(f"    Loading:           {metrics['load_time']:>8.2f}s")
    print("\n" + "=" * 65)

    return metrics


if __name__ == '__main__':
    run_pipeline()
