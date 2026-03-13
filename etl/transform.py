"""
ETL - Transform Module
Data cleaning, validation, standardization, and reconciliation prep.
"""

import pandas as pd
import numpy as np
import time


# Valid currency codes for validation
VALID_CURRENCIES = {'USD', 'EUR', 'GBP', 'JPY', 'CAD', 'AUD', 'CHF', 'INR'}

# Exchange rates to USD for normalization
EXCHANGE_RATES = {
    'USD': 1.0, 'EUR': 1.08, 'GBP': 1.27, 'JPY': 0.0067,
    'CAD': 0.74, 'AUD': 0.65, 'CHF': 1.13, 'INR': 0.012,
}

VALID_CATEGORIES = [
    'Revenue', 'Operating Expenses', 'Cost of Goods Sold',
    'Capital Expenditure', 'Financial', 'Tax'
]


def transform_transactions(df: pd.DataFrame) -> tuple:
    """
    Clean and transform transaction data.
    Returns (cleaned_df, issues_log_list).
    """
    print("\n  [TRANSFORM] Cleaning transaction data...")
    start = time.time()
    df = df.copy()
    issues = []
    original_count = len(df)

    # --- 1. Strip whitespace from text columns ---
    text_cols = ['category', 'subcategory', 'currency', 'transaction_type',
                 'status', 'counterparty', 'description', 'account_id', 'account_name']
    for col in text_cols:
        if col in df.columns:
            whitespace_mask = df[col].astype(str).str.strip() != df[col].astype(str)
            ws_count = whitespace_mask.sum()
            if ws_count > 0:
                issues.append({
                    'check_name': f'Whitespace in {col}',
                    'check_type': 'format',
                    'column_name': col,
                    'failed_records': int(ws_count),
                    'severity': 'low',
                    'details': f'Stripped whitespace from {ws_count} records'
                })
            df[col] = df[col].astype(str).str.strip()

    # --- 2. Standardize date formats ---
    date_col = 'transaction_date'
    null_dates = df[date_col].isna().sum()
    if null_dates > 0:
        issues.append({
            'check_name': 'Null transaction_date',
            'check_type': 'completeness',
            'column_name': date_col,
            'failed_records': int(null_dates),
            'severity': 'high',
            'details': f'{null_dates} records with null dates — filled with median date'
        })

    df[date_col] = pd.to_datetime(df[date_col], format='mixed', errors='coerce', dayfirst=False)
    median_date = df[date_col].dropna().median()
    df[date_col] = df[date_col].fillna(median_date)

    # --- 3. Handle null amounts ---
    null_amounts = df['amount'].isna().sum()
    if null_amounts > 0:
        median_amount = df['amount'].dropna().median()
        df['amount'] = df['amount'].fillna(median_amount)
        issues.append({
            'check_name': 'Null amount',
            'check_type': 'completeness',
            'column_name': 'amount',
            'failed_records': int(null_amounts),
            'severity': 'high',
            'details': f'{null_amounts} records with null amounts — filled with median ({median_amount:.2f})'
        })

    # --- 4. Fix negative credits ---
    neg_credits = (df['transaction_type'] == 'credit') & (df['amount'] < 0)
    neg_count = neg_credits.sum()
    if neg_count > 0:
        df.loc[neg_credits, 'amount'] = df.loc[neg_credits, 'amount'].abs()
        issues.append({
            'check_name': 'Negative credit amounts',
            'check_type': 'validity',
            'column_name': 'amount',
            'failed_records': int(neg_count),
            'severity': 'medium',
            'details': f'{neg_count} credit transactions had negative amounts — converted to absolute'
        })

    # --- 5. Validate & fix currencies ---
    invalid_curr = ~df['currency'].isin(VALID_CURRENCIES)
    inv_curr_count = invalid_curr.sum()
    if inv_curr_count > 0:
        df.loc[invalid_curr, 'currency'] = 'USD'
        issues.append({
            'check_name': 'Invalid currency codes',
            'check_type': 'validity',
            'column_name': 'currency',
            'failed_records': int(inv_curr_count),
            'severity': 'medium',
            'details': f'{inv_curr_count} records with invalid currencies — defaulted to USD'
        })

    # --- 6. Validate categories ---
    df.loc[df['category'] == 'None', 'category'] = np.nan
    null_cats = df['category'].isna().sum()
    if null_cats > 0:
        df['category'] = df['category'].fillna('Uncategorized')
        issues.append({
            'check_name': 'Null category',
            'check_type': 'completeness',
            'column_name': 'category',
            'failed_records': int(null_cats),
            'severity': 'medium',
            'details': f'{null_cats} records with null categories — set to Uncategorized'
        })

    # --- 7. Remove exact duplicates ---
    dup_mask = df.duplicated(subset=['transaction_date', 'account_id', 'amount',
                                     'category', 'counterparty'], keep='first')
    dup_count = dup_mask.sum()
    if dup_count > 0:
        df = df[~dup_mask].copy()
        issues.append({
            'check_name': 'Duplicate records',
            'check_type': 'uniqueness',
            'column_name': 'multiple',
            'failed_records': int(dup_count),
            'severity': 'high',
            'details': f'{dup_count} duplicate records removed'
        })

    # --- 8. Normalize amounts to USD ---
    df['amount_usd'] = df.apply(
        lambda row: round(row['amount'] * EXCHANGE_RATES.get(row['currency'], 1.0), 2),
        axis=1
    )

    elapsed = time.time() - start
    print(f"    Cleaned {original_count:,} → {len(df):,} records ({elapsed:.2f}s)")
    print(f"    Issues found: {len(issues)}")

    return df, issues


def transform_ledger(df: pd.DataFrame) -> pd.DataFrame:
    """Clean ledger entry data."""
    print("  [TRANSFORM] Cleaning ledger data...")
    df = df.copy()

    df['entry_date'] = pd.to_datetime(df['entry_date'], format='mixed', errors='coerce')
    median_date = df['entry_date'].dropna().median()
    df['entry_date'] = df['entry_date'].fillna(median_date)

    df['debit_amount'] = pd.to_numeric(df['debit_amount'], errors='coerce').fillna(0)
    df['credit_amount'] = pd.to_numeric(df['credit_amount'], errors='coerce').fillna(0)
    df['balance'] = df['credit_amount'] - df['debit_amount']

    print(f"    Cleaned {len(df):,} ledger entries")
    return df


def transform_benchmarks(df: pd.DataFrame) -> pd.DataFrame:
    """Clean benchmark data."""
    print("  [TRANSFORM] Cleaning benchmark data...")
    df = df.copy()
    df['benchmark_date'] = pd.to_datetime(df['benchmark_date'], errors='coerce')
    df['variance_pct'] = pd.to_numeric(df['variance_pct'], errors='coerce').fillna(0)
    print(f"    Cleaned {len(df):,} benchmark records")
    return df
