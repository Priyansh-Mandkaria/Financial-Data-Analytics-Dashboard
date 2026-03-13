"""
Synthetic Financial Data Generator
Generates 50,000+ financial records with realistic data quality issues.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import uuid
import random

# Seed for reproducibility
np.random.seed(42)
random.seed(42)

# --- Configuration ---
NUM_TRANSACTIONS = 52000
NUM_ACCOUNTS = 150
START_DATE = datetime(2023, 1, 1)
END_DATE = datetime(2025, 12, 31)
DATA_QUALITY_ISSUE_RATE = 0.05  # 5% of records will have issues
RECONCILIATION_MISMATCH_RATE = 0.02  # 2% ledger mismatches

CATEGORIES = {
    'Revenue': ['Product Sales', 'Service Revenue', 'Subscription', 'Licensing'],
    'Operating Expenses': ['Salaries', 'Rent', 'Utilities', 'Marketing', 'Insurance'],
    'Cost of Goods Sold': ['Raw Materials', 'Manufacturing', 'Shipping', 'Packaging'],
    'Capital Expenditure': ['Equipment', 'Software', 'Infrastructure', 'Vehicles'],
    'Financial': ['Interest Income', 'Interest Expense', 'Dividends', 'Forex'],
    'Tax': ['Income Tax', 'Sales Tax', 'Property Tax', 'Payroll Tax'],
}

COUNTERPARTIES = [
    'Acme Corp', 'GlobalTech Inc', 'Pinnacle Solutions', 'Vertex Systems',
    'CloudNine Ltd', 'DataStream Analytics', 'NovaPay Services', 'Apex Financial',
    'BlueSky Ventures', 'IronGate Holdings', 'Meridian Group', 'Cascade Partners',
    'Sterling & Co', 'NexGen Digital', 'PrimePath Logistics', 'Quantum Labs',
    'Redwood Capital', 'TitanForge Inc', 'VeloCity Corp', 'WavePoint Media',
    'EchoStar Systems', 'FusionBridge Ltd', 'Granite Peak Corp', 'HorizonOne',
    'InfinityLoop Tech', 'JadeStone Consulting', 'KineticEdge Solutions',
    'LightWave Networks', 'MosaicData Inc', 'OmniCore Partners',
]

CURRENCIES = ['USD', 'USD', 'USD', 'USD', 'EUR', 'GBP', 'JPY', 'CAD']  # USD-heavy
STATUSES = ['completed', 'completed', 'completed', 'completed', 'pending', 'failed', 'reversed']

BENCHMARK_NAMES = [
    'Monthly Revenue Target', 'Operating Cost Ratio', 'Gross Margin',
    'Net Profit Margin', 'Cash Flow Coverage', 'Debt-to-Equity',
    'Return on Assets', 'Working Capital Ratio',
]


def generate_account_ids(n: int) -> list:
    """Generate realistic account IDs."""
    prefixes = ['ACC', 'GL', 'AR', 'AP', 'EXP']
    accounts = []
    for i in range(n):
        prefix = random.choice(prefixes)
        accounts.append(f"{prefix}-{str(i + 1000).zfill(6)}")
    return accounts


def generate_transactions(num_records: int, accounts: list) -> pd.DataFrame:
    """Generate synthetic transaction records."""
    print(f"  Generating {num_records:,} transaction records...")

    dates = pd.date_range(START_DATE, END_DATE, periods=num_records)
    dates = dates + pd.to_timedelta(np.random.randint(-2, 3, num_records), unit='D')

    records = []
    for i in range(num_records):
        category = random.choice(list(CATEGORIES.keys()))
        subcategory = random.choice(CATEGORIES[category])

        # Amount distribution varies by category
        if category == 'Revenue':
            amount = round(np.random.lognormal(mean=8, sigma=1.5), 2)
        elif category == 'Operating Expenses':
            amount = round(np.random.lognormal(mean=7, sigma=1.2), 2)
        elif category == 'Cost of Goods Sold':
            amount = round(np.random.lognormal(mean=7.5, sigma=1.0), 2)
        elif category == 'Capital Expenditure':
            amount = round(np.random.lognormal(mean=9, sigma=1.8), 2)
        elif category == 'Financial':
            amount = round(np.random.lognormal(mean=6, sigma=2.0), 2)
        else:  # Tax
            amount = round(np.random.lognormal(mean=7, sigma=0.8), 2)

        tx_type = 'credit' if category == 'Revenue' else 'debit'

        records.append({
            'transaction_id': f"TXN-{uuid.uuid4().hex[:12].upper()}",
            'transaction_date': dates[i].strftime('%Y-%m-%d'),
            'account_id': random.choice(accounts),
            'account_name': f"Account {random.choice(accounts).split('-')[1]}",
            'category': category,
            'subcategory': subcategory,
            'amount': amount,
            'currency': random.choice(CURRENCIES),
            'transaction_type': tx_type,
            'status': random.choice(STATUSES),
            'counterparty': random.choice(COUNTERPARTIES),
            'description': f"{subcategory} - {random.choice(COUNTERPARTIES)}",
        })

    df = pd.DataFrame(records)
    return df


def inject_data_quality_issues(df: pd.DataFrame, rate: float) -> pd.DataFrame:
    """Inject realistic data quality issues into the dataset."""
    print(f"  Injecting ~{rate*100:.0f}% data quality issues...")
    df = df.copy()
    n = len(df)
    num_issues = int(n * rate)
    issue_indices = np.random.choice(n, num_issues, replace=False)

    issue_types = ['null_amount', 'null_date', 'null_category', 'duplicate',
                   'outlier_amount', 'wrong_date_format', 'negative_credit',
                   'invalid_currency', 'whitespace_category']

    for idx in issue_indices:
        issue = random.choice(issue_types)

        if issue == 'null_amount':
            df.at[idx, 'amount'] = np.nan
        elif issue == 'null_date':
            df.at[idx, 'transaction_date'] = None
        elif issue == 'null_category':
            df.at[idx, 'category'] = None
        elif issue == 'duplicate':
            # Create a duplicate of a random existing row
            dup_idx = random.randint(0, n - 1)
            for col in df.columns:
                if col != 'transaction_id':
                    df.at[idx, col] = df.at[dup_idx, col]
            df.at[idx, 'transaction_id'] = df.at[dup_idx, 'transaction_id'] + '_DUP'
        elif issue == 'outlier_amount':
            df.at[idx, 'amount'] = round(df.at[idx, 'amount'] * random.uniform(50, 200), 2)
        elif issue == 'wrong_date_format':
            if pd.notna(df.at[idx, 'transaction_date']):
                try:
                    d = pd.to_datetime(df.at[idx, 'transaction_date'])
                    df.at[idx, 'transaction_date'] = d.strftime('%d/%m/%Y')
                except Exception:
                    pass
        elif issue == 'negative_credit':
            if df.at[idx, 'transaction_type'] == 'credit':
                df.at[idx, 'amount'] = -abs(df.at[idx, 'amount'])
        elif issue == 'invalid_currency':
            df.at[idx, 'currency'] = random.choice(['XXX', 'ZZZ', '', 'US$'])
        elif issue == 'whitespace_category':
            if pd.notna(df.at[idx, 'category']):
                df.at[idx, 'category'] = '  ' + df.at[idx, 'category'] + '  '

    return df


def generate_ledger_entries(transactions_df: pd.DataFrame, mismatch_rate: float) -> pd.DataFrame:
    """Generate ledger entries from transactions with intentional mismatches."""
    print(f"  Generating ledger entries with ~{mismatch_rate*100:.0f}% mismatches...")

    completed_txns = transactions_df[transactions_df['status'] == 'completed'].copy()
    entries = []

    for _, txn in completed_txns.iterrows():
        entry_id = f"LED-{uuid.uuid4().hex[:12].upper()}"
        amount = txn['amount'] if pd.notna(txn['amount']) else 0

        debit = amount if txn['transaction_type'] == 'debit' else 0
        credit = amount if txn['transaction_type'] == 'credit' else 0

        # Inject mismatches
        if random.random() < mismatch_rate:
            mismatch_type = random.choice(['amount_diff', 'missing_entry', 'date_diff'])
            if mismatch_type == 'amount_diff':
                variance = round(amount * random.uniform(0.01, 0.15), 2)
                if debit > 0:
                    debit += variance
                else:
                    credit += variance
            elif mismatch_type == 'date_diff':
                pass  # Date will differ below
            else:
                continue  # Skip this entry entirely to simulate missing entry

        ledger_types = ['general', 'accounts_receivable', 'accounts_payable']
        entry_date = txn['transaction_date']
        if random.random() < mismatch_rate:
            try:
                d = pd.to_datetime(entry_date)
                entry_date = (d + timedelta(days=random.randint(1, 5))).strftime('%Y-%m-%d')
            except Exception:
                pass

        entries.append({
            'entry_id': entry_id,
            'transaction_id': txn['transaction_id'],
            'entry_date': entry_date,
            'account_id': txn['account_id'],
            'debit_amount': round(debit, 2),
            'credit_amount': round(credit, 2),
            'balance': round(credit - debit, 2),
            'ledger_type': random.choice(ledger_types),
            'reconciled': 0,
        })

    return pd.DataFrame(entries)


def generate_benchmarks() -> pd.DataFrame:
    """Generate monthly benchmark tracking data."""
    print("  Generating benchmark data...")

    dates = pd.date_range(START_DATE, END_DATE, freq='MS')
    records = []

    for date in dates:
        for benchmark in BENCHMARK_NAMES:
            if 'Revenue' in benchmark:
                expected = round(np.random.normal(500000, 50000), 2)
            elif 'Ratio' in benchmark or 'Margin' in benchmark:
                expected = round(np.random.normal(0.35, 0.05), 4)
            elif 'Coverage' in benchmark:
                expected = round(np.random.normal(1.5, 0.3), 4)
            else:
                expected = round(np.random.normal(0.12, 0.03), 4)

            # Actual deviates from expected
            deviation = np.random.normal(0, 0.08)
            actual = round(expected * (1 + deviation), 4)
            variance = round(actual - expected, 4)
            variance_pct = round((variance / expected) * 100, 2) if expected != 0 else 0

            if abs(variance_pct) < 5:
                status = 'within_range'
            elif abs(variance_pct) < 15:
                status = 'warning'
            else:
                status = 'critical'

            records.append({
                'benchmark_date': date.strftime('%Y-%m-%d'),
                'benchmark_name': benchmark,
                'category': benchmark.split()[0],
                'expected_value': expected,
                'actual_value': actual,
                'variance': variance,
                'variance_pct': variance_pct,
                'status': status,
            })

    return pd.DataFrame(records)


def generate_all_data(output_dir: str) -> dict:
    """Generate all synthetic data and save as CSV files."""
    os.makedirs(output_dir, exist_ok=True)
    print("\n=== Generating Synthetic Financial Data ===\n")

    # 1. Generate accounts
    accounts = generate_account_ids(NUM_ACCOUNTS)

    # 2. Generate raw transactions
    transactions_df = generate_transactions(NUM_TRANSACTIONS, accounts)

    # 3. Inject data quality issues
    transactions_df = inject_data_quality_issues(transactions_df, DATA_QUALITY_ISSUE_RATE)

    # 4. Generate ledger entries
    ledger_df = generate_ledger_entries(transactions_df, RECONCILIATION_MISMATCH_RATE)

    # 5. Generate benchmarks
    benchmarks_df = generate_benchmarks()

    # Save to CSV
    tx_path = os.path.join(output_dir, 'transactions.csv')
    ledger_path = os.path.join(output_dir, 'ledger_entries.csv')
    bench_path = os.path.join(output_dir, 'benchmarks.csv')

    transactions_df.to_csv(tx_path, index=False)
    ledger_df.to_csv(ledger_path, index=False)
    benchmarks_df.to_csv(bench_path, index=False)

    print(f"\n  ✓ Transactions:    {len(transactions_df):>8,} records → {tx_path}")
    print(f"  ✓ Ledger Entries:  {len(ledger_df):>8,} records → {ledger_path}")
    print(f"  ✓ Benchmarks:      {len(benchmarks_df):>8,} records → {bench_path}")
    print(f"\n=== Data Generation Complete ===\n")

    return {
        'transactions': transactions_df,
        'ledger_entries': ledger_df,
        'benchmarks': benchmarks_df,
    }


if __name__ == '__main__':
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    output = os.path.join(base_dir, 'data', 'raw')
    generate_all_data(output)
