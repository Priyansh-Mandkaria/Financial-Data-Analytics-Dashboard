"""
Reconciliation Module
Cross-match transactions against ledger entries, flag discrepancies.
"""

import pandas as pd
import numpy as np


def match_transactions_to_ledger(transactions_df: pd.DataFrame,
                                  ledger_df: pd.DataFrame,
                                  tolerance: float = 0.01) -> dict:
    """
    Match transactions to ledger entries and identify discrepancies.

    Returns a dict with:
        - matched: DataFrame of successfully matched records
        - unmatched_transactions: transactions with no ledger entry
        - unmatched_ledger: ledger entries with no matching transaction
        - amount_mismatches: matched but amounts differ
        - date_mismatches: matched but dates differ
        - summary: overall reconciliation summary
    """
    print("\n  [RECONCILIATION] Cross-matching transactions ↔ ledger entries...")

    # Merge on transaction_id
    merged = transactions_df.merge(
        ledger_df,
        on='transaction_id',
        how='outer',
        suffixes=('_txn', '_led'),
        indicator=True
    )

    # Categorize matches
    both = merged[merged['_merge'] == 'both'].copy()
    txn_only = merged[merged['_merge'] == 'left_only'].copy()
    led_only = merged[merged['_merge'] == 'right_only'].copy()

    # --- Check amount mismatches ---
    amount_mismatches = pd.DataFrame()
    if not both.empty and 'amount' in both.columns:
        # Compare transaction amount to ledger debit/credit
        both['ledger_amount'] = both.apply(
            lambda row: row.get('debit_amount', 0) if row.get('debit_amount', 0) > 0
            else row.get('credit_amount', 0),
            axis=1
        )
        both['amount_diff'] = abs(both['amount'] - both['ledger_amount'])
        amount_mismatches = both[both['amount_diff'] > tolerance].copy()

    # --- Check date mismatches ---
    date_mismatches = pd.DataFrame()
    if not both.empty:
        txn_date_col = 'transaction_date' if 'transaction_date' in both.columns else None
        led_date_col = 'entry_date' if 'entry_date' in both.columns else None

        if txn_date_col and led_date_col:
            both[txn_date_col] = pd.to_datetime(both[txn_date_col], errors='coerce')
            both[led_date_col] = pd.to_datetime(both[led_date_col], errors='coerce')
            both['date_diff_days'] = abs(
                (both[txn_date_col] - both[led_date_col]).dt.days
            )
            date_mismatches = both[both['date_diff_days'] > 0].copy()

    # --- Perfectly matched ---
    matched = both[
        (both.get('amount_diff', pd.Series([0])) <= tolerance)
    ].copy() if 'amount_diff' in both.columns else both.copy()

    # --- Summary ---
    total_txns = len(transactions_df)
    total_ledger = len(ledger_df)
    total_matched = len(both)
    match_rate = round(total_matched / total_txns * 100, 2) if total_txns > 0 else 0

    summary = {
        'total_transactions': total_txns,
        'total_ledger_entries': total_ledger,
        'matched_records': total_matched,
        'match_rate_pct': match_rate,
        'unmatched_transactions': len(txn_only),
        'unmatched_ledger_entries': len(led_only),
        'amount_mismatches': len(amount_mismatches),
        'date_mismatches': len(date_mismatches),
        'perfect_matches': total_matched - len(amount_mismatches),
    }

    print(f"    Total Transactions:     {total_txns:>8,}")
    print(f"    Total Ledger Entries:    {total_ledger:>8,}")
    print(f"    Matched Records:        {total_matched:>8,} ({match_rate}%)")
    print(f"    Unmatched Transactions: {len(txn_only):>8,}")
    print(f"    Unmatched Ledger:       {len(led_only):>8,}")
    print(f"    Amount Mismatches:      {len(amount_mismatches):>8,}")
    print(f"    Date Mismatches:        {len(date_mismatches):>8,}")

    return {
        'matched': matched,
        'unmatched_transactions': txn_only,
        'unmatched_ledger': led_only,
        'amount_mismatches': amount_mismatches,
        'date_mismatches': date_mismatches,
        'summary': summary,
    }


def run_reconciliation(transactions_df: pd.DataFrame,
                       ledger_df: pd.DataFrame) -> dict:
    """Run the full reconciliation process."""
    # Filter to completed transactions only for reconciliation
    completed = transactions_df[
        transactions_df['status'] == 'completed'
    ].copy() if 'status' in transactions_df.columns else transactions_df.copy()

    results = match_transactions_to_ledger(completed, ledger_df)
    return results
