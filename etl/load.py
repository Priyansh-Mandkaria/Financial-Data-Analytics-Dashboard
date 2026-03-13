"""
ETL - Load Module
Bulk-insert cleaned DataFrames into SQLite database.
"""

import pandas as pd
import time
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.db_manager import bulk_insert, get_connection, DB_PATH


def load_transactions(df: pd.DataFrame) -> int:
    """Load cleaned transactions into the database."""
    df = df.copy()
    # Ensure date is string for SQLite
    if 'transaction_date' in df.columns:
        df['transaction_date'] = pd.to_datetime(df['transaction_date']).dt.strftime('%Y-%m-%d')

    # Select only schema columns
    cols = ['transaction_id', 'transaction_date', 'account_id', 'account_name',
            'category', 'subcategory', 'amount', 'currency', 'transaction_type',
            'status', 'counterparty', 'description']
    df_insert = df[[c for c in cols if c in df.columns]]

    start = time.time()
    count = bulk_insert(df_insert, 'transactions')
    elapsed = time.time() - start
    print(f"    Loaded {len(df_insert):>8,} transactions ({elapsed:.2f}s)")
    return count


def load_ledger_entries(df: pd.DataFrame) -> int:
    """Load cleaned ledger entries into the database."""
    df = df.copy()
    if 'entry_date' in df.columns:
        df['entry_date'] = pd.to_datetime(df['entry_date']).dt.strftime('%Y-%m-%d')

    cols = ['entry_id', 'transaction_id', 'entry_date', 'account_id',
            'debit_amount', 'credit_amount', 'balance', 'ledger_type', 'reconciled']
    df_insert = df[[c for c in cols if c in df.columns]]

    start = time.time()
    count = bulk_insert(df_insert, 'ledger_entries')
    elapsed = time.time() - start
    print(f"    Loaded {len(df_insert):>8,} ledger entries ({elapsed:.2f}s)")
    return count


def load_benchmarks(df: pd.DataFrame) -> int:
    """Load benchmark data into the database."""
    df = df.copy()
    if 'benchmark_date' in df.columns:
        df['benchmark_date'] = pd.to_datetime(df['benchmark_date']).dt.strftime('%Y-%m-%d')

    cols = ['benchmark_date', 'benchmark_name', 'category', 'expected_value',
            'actual_value', 'variance', 'variance_pct', 'status']
    df_insert = df[[c for c in cols if c in df.columns]]

    start = time.time()
    count = bulk_insert(df_insert, 'benchmarks')
    elapsed = time.time() - start
    print(f"    Loaded {len(df_insert):>8,} benchmarks ({elapsed:.2f}s)")
    return count


def load_quality_log(issues: list, table_name: str = 'transactions') -> int:
    """Load quality check results into the quality_log table."""
    if not issues:
        return 0

    records = []
    for issue in issues:
        records.append({
            'check_name': issue.get('check_name', ''),
            'check_type': issue.get('check_type', ''),
            'table_name': table_name,
            'column_name': issue.get('column_name', ''),
            'total_records': issue.get('total_records', 0),
            'passed_records': issue.get('passed_records', 0),
            'failed_records': issue.get('failed_records', 0),
            'pass_rate': issue.get('pass_rate', 0),
            'severity': issue.get('severity', 'low'),
            'details': issue.get('details', ''),
        })

    df = pd.DataFrame(records)
    count = bulk_insert(df, 'quality_log')
    print(f"    Loaded {len(records):>8,} quality log entries")
    return count


def load_anomalies(anomalies_df: pd.DataFrame) -> int:
    """Load detected anomalies into the anomaly_log table."""
    if anomalies_df is None or anomalies_df.empty:
        return 0

    cols = ['transaction_id', 'anomaly_type', 'anomaly_score',
            'expected_range_low', 'expected_range_high', 'actual_value',
            'category', 'account_id', 'detection_method']
    df_insert = anomalies_df[[c for c in cols if c in anomalies_df.columns]]

    count = bulk_insert(df_insert, 'anomaly_log')
    print(f"    Loaded {len(df_insert):>8,} anomaly records")
    return count


def load_all(data: dict, issues: list = None, anomalies: pd.DataFrame = None) -> dict:
    """Load all cleaned data into the database."""
    print("\n  [LOAD] Inserting into SQLite database...")
    start = time.time()

    counts = {}
    counts['transactions'] = load_transactions(data['transactions'])
    counts['ledger_entries'] = load_ledger_entries(data['ledger_entries'])
    counts['benchmarks'] = load_benchmarks(data['benchmarks'])

    if issues:
        counts['quality_log'] = load_quality_log(issues)

    if anomalies is not None and not anomalies.empty:
        counts['anomaly_log'] = load_anomalies(anomalies)

    elapsed = time.time() - start
    print(f"\n    Total load time: {elapsed:.2f}s")
    return counts
