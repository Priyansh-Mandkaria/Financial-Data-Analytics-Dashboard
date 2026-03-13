"""
ETL - Extract Module
Reads raw CSV/Excel files into Pandas DataFrames.
"""

import pandas as pd
import os
import time


def extract_csv(file_path: str) -> pd.DataFrame:
    """Extract data from a CSV file."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Source file not found: {file_path}")

    start = time.time()
    df = pd.read_csv(file_path)
    elapsed = time.time() - start

    print(f"    Extracted {len(df):>8,} rows from {os.path.basename(file_path)} ({elapsed:.2f}s)")
    return df


def extract_all(raw_dir: str) -> dict:
    """Extract all raw data files from the data directory."""
    print("\n  [EXTRACT] Reading source files...")

    files = {
        'transactions': os.path.join(raw_dir, 'transactions.csv'),
        'ledger_entries': os.path.join(raw_dir, 'ledger_entries.csv'),
        'benchmarks': os.path.join(raw_dir, 'benchmarks.csv'),
    }

    dataframes = {}
    for name, path in files.items():
        dataframes[name] = extract_csv(path)

    total = sum(len(df) for df in dataframes.values())
    print(f"    Total records extracted: {total:,}")
    return dataframes
