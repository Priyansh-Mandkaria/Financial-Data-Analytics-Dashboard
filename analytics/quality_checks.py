"""
Data Quality Checks Module
Rule-based validation: completeness, uniqueness, range checks, format validation.
Generates a quality scorecard.
"""

import pandas as pd
import numpy as np


def check_completeness(df: pd.DataFrame, columns: list) -> list:
    """Check for null/missing values in specified columns."""
    results = []
    for col in columns:
        if col not in df.columns:
            continue
        total = len(df)
        nulls = int(df[col].isna().sum())
        passed = total - nulls
        pass_rate = round(passed / total * 100, 2) if total > 0 else 0

        severity = 'low'
        if nulls / total > 0.1:
            severity = 'critical'
        elif nulls / total > 0.05:
            severity = 'high'
        elif nulls / total > 0.01:
            severity = 'medium'

        results.append({
            'check_name': f'Completeness: {col}',
            'check_type': 'completeness',
            'table_name': 'transactions',
            'column_name': col,
            'total_records': total,
            'passed_records': passed,
            'failed_records': nulls,
            'pass_rate': pass_rate,
            'severity': severity,
            'details': f'{nulls}/{total} records missing ({100-pass_rate:.2f}% null rate)'
        })
    return results


def check_uniqueness(df: pd.DataFrame, column: str) -> dict:
    """Check for duplicate values in a column."""
    total = len(df)
    unique = df[column].nunique()
    duplicates = total - unique
    pass_rate = round(unique / total * 100, 2) if total > 0 else 0

    severity = 'low'
    if duplicates / total > 0.05:
        severity = 'high'
    elif duplicates / total > 0.01:
        severity = 'medium'

    return {
        'check_name': f'Uniqueness: {column}',
        'check_type': 'uniqueness',
        'table_name': 'transactions',
        'column_name': column,
        'total_records': total,
        'passed_records': unique,
        'failed_records': duplicates,
        'pass_rate': pass_rate,
        'severity': severity,
        'details': f'{duplicates} duplicate values found out of {total}'
    }


def check_range(df: pd.DataFrame, column: str, min_val: float = None, max_val: float = None) -> dict:
    """Check if values fall within an expected range."""
    total = len(df)
    series = df[column].dropna()

    out_of_range = 0
    if min_val is not None:
        out_of_range += int((series < min_val).sum())
    if max_val is not None:
        out_of_range += int((series > max_val).sum())

    passed = total - out_of_range
    pass_rate = round(passed / total * 100, 2) if total > 0 else 0

    severity = 'low'
    if out_of_range / total > 0.05:
        severity = 'high'
    elif out_of_range / total > 0.01:
        severity = 'medium'

    return {
        'check_name': f'Range check: {column}',
        'check_type': 'range',
        'table_name': 'transactions',
        'column_name': column,
        'total_records': total,
        'passed_records': passed,
        'failed_records': out_of_range,
        'pass_rate': pass_rate,
        'severity': severity,
        'details': f'{out_of_range} values outside range [{min_val}, {max_val}]'
    }


def check_categorical_validity(df: pd.DataFrame, column: str, valid_values: list) -> dict:
    """Check if values belong to a set of valid categories."""
    total = len(df)
    series = df[column].dropna()
    invalid = int((~series.isin(valid_values)).sum())
    passed = total - invalid
    pass_rate = round(passed / total * 100, 2) if total > 0 else 0

    severity = 'low'
    if invalid / total > 0.05:
        severity = 'high'
    elif invalid / total > 0.01:
        severity = 'medium'

    return {
        'check_name': f'Validity: {column}',
        'check_type': 'validity',
        'table_name': 'transactions',
        'column_name': column,
        'total_records': total,
        'passed_records': passed,
        'failed_records': invalid,
        'pass_rate': pass_rate,
        'severity': severity,
        'details': f'{invalid} records with invalid {column} values'
    }


def generate_quality_scorecard(results: list) -> dict:
    """Generate an overall quality scorecard from check results."""
    if not results:
        return {'overall_score': 100, 'total_checks': 0}

    total_checks = len(results)
    avg_pass_rate = np.mean([r['pass_rate'] for r in results])

    severity_counts = {'low': 0, 'medium': 0, 'high': 0, 'critical': 0}
    for r in results:
        severity_counts[r.get('severity', 'low')] += 1

    total_failed = sum(r['failed_records'] for r in results)
    total_records = sum(r['total_records'] for r in results)

    return {
        'overall_score': round(avg_pass_rate, 2),
        'total_checks': total_checks,
        'total_records_checked': total_records,
        'total_issues_found': total_failed,
        'severity_breakdown': severity_counts,
        'checks_passed': sum(1 for r in results if r['pass_rate'] >= 99),
        'checks_warning': sum(1 for r in results if 95 <= r['pass_rate'] < 99),
        'checks_failed': sum(1 for r in results if r['pass_rate'] < 95),
    }


def run_quality_checks(df: pd.DataFrame, transform_issues: list = None) -> list:
    """Run all quality checks on the transaction data."""
    print("\n  [QUALITY] Running data quality checks...")

    results = []

    # Include issues found during transformation
    if transform_issues:
        for issue in transform_issues:
            issue.setdefault('table_name', 'transactions')
            issue.setdefault('total_records', len(df))
            issue.setdefault('passed_records', len(df) - issue.get('failed_records', 0))
            issue.setdefault('pass_rate', round(
                issue['passed_records'] / issue['total_records'] * 100, 2
            ) if issue['total_records'] > 0 else 0)
            results.append(issue)

    # Completeness checks
    key_columns = ['transaction_id', 'transaction_date', 'account_id',
                   'category', 'amount', 'currency', 'status']
    results.extend(check_completeness(df, key_columns))

    # Uniqueness check
    results.append(check_uniqueness(df, 'transaction_id'))

    # Range checks
    results.append(check_range(df, 'amount', min_val=0, max_val=10000000))

    # Categorical validity
    valid_categories = ['Revenue', 'Operating Expenses', 'Cost of Goods Sold',
                        'Capital Expenditure', 'Financial', 'Tax', 'Uncategorized']
    results.append(check_categorical_validity(df, 'category', valid_categories))

    valid_statuses = ['completed', 'pending', 'failed', 'reversed']
    results.append(check_categorical_validity(df, 'status', valid_statuses))

    valid_currencies = ['USD', 'EUR', 'GBP', 'JPY', 'CAD', 'AUD', 'CHF', 'INR']
    results.append(check_categorical_validity(df, 'currency', valid_currencies))

    valid_types = ['credit', 'debit']
    results.append(check_categorical_validity(df, 'transaction_type', valid_types))

    # Generate scorecard
    scorecard = generate_quality_scorecard(results)
    print(f"    Quality Score: {scorecard['overall_score']:.1f}%")
    print(f"    Checks Run: {scorecard['total_checks']}")
    print(f"    Issues Found: {scorecard['total_issues_found']:,}")
    print(f"    Severity: {scorecard['severity_breakdown']}")

    return results
