"""
Anomaly Detection Module
Z-score and IQR-based anomaly detection on financial transaction amounts.
"""

import pandas as pd
import numpy as np
from scipy import stats


def detect_zscore_anomalies(df: pd.DataFrame, column: str = 'amount',
                            threshold: float = 3.0) -> pd.DataFrame:
    """
    Detect anomalies using Z-score method.
    Records with |Z-score| > threshold are flagged as anomalies.
    """
    series = df[column].dropna()
    z_scores = np.abs(stats.zscore(series))

    anomaly_mask = z_scores > threshold
    anomaly_indices = series.index[anomaly_mask]

    anomalies = df.loc[anomaly_indices].copy()
    anomalies['anomaly_score'] = z_scores[anomaly_mask]
    anomalies['detection_method'] = 'z_score'
    anomalies['anomaly_type'] = 'statistical_outlier'

    mean_val = series.mean()
    std_val = series.std()
    anomalies['expected_range_low'] = round(mean_val - threshold * std_val, 2)
    anomalies['expected_range_high'] = round(mean_val + threshold * std_val, 2)
    anomalies['actual_value'] = anomalies[column]

    return anomalies


def detect_iqr_anomalies(df: pd.DataFrame, column: str = 'amount',
                         multiplier: float = 1.5) -> pd.DataFrame:
    """
    Detect anomalies using Interquartile Range (IQR) method.
    Values outside Q1 - multiplier*IQR to Q3 + multiplier*IQR are flagged.
    """
    series = df[column].dropna()
    Q1 = series.quantile(0.25)
    Q3 = series.quantile(0.75)
    IQR = Q3 - Q1

    lower_bound = Q1 - multiplier * IQR
    upper_bound = Q3 + multiplier * IQR

    anomaly_mask = (series < lower_bound) | (series > upper_bound)
    anomaly_indices = series.index[anomaly_mask]

    anomalies = df.loc[anomaly_indices].copy()
    anomalies['anomaly_score'] = anomalies[column].apply(
        lambda x: abs(x - series.median()) / IQR if IQR > 0 else 0
    )
    anomalies['detection_method'] = 'iqr'
    anomalies['anomaly_type'] = 'iqr_outlier'
    anomalies['expected_range_low'] = round(lower_bound, 2)
    anomalies['expected_range_high'] = round(upper_bound, 2)
    anomalies['actual_value'] = anomalies[column]

    return anomalies


def detect_category_anomalies(df: pd.DataFrame, column: str = 'amount') -> pd.DataFrame:
    """Detect anomalies within each category using Z-score method."""
    all_anomalies = []

    for category in df['category'].unique():
        cat_df = df[df['category'] == category]
        if len(cat_df) < 10:
            continue

        series = cat_df[column].dropna()
        if series.std() == 0:
            continue

        z_scores = np.abs(stats.zscore(series))
        anomaly_mask = z_scores > 2.5  # Slightly lower threshold within categories

        if anomaly_mask.any():
            anomaly_indices = series.index[anomaly_mask]
            anomalies = cat_df.loc[anomaly_indices].copy()
            anomalies['anomaly_score'] = z_scores[anomaly_mask]
            anomalies['detection_method'] = 'category_zscore'
            anomalies['anomaly_type'] = f'category_outlier_{category.lower().replace(" ", "_")}'

            mean_val = series.mean()
            std_val = series.std()
            anomalies['expected_range_low'] = round(mean_val - 2.5 * std_val, 2)
            anomalies['expected_range_high'] = round(mean_val + 2.5 * std_val, 2)
            anomalies['actual_value'] = anomalies[column]
            all_anomalies.append(anomalies)

    if all_anomalies:
        return pd.concat(all_anomalies, ignore_index=True)
    return pd.DataFrame()


def detect_anomalies(df: pd.DataFrame) -> pd.DataFrame:
    """
    Run all anomaly detection methods and return combined results.
    """
    print("\n  [ANOMALY] Running anomaly detection...")

    # Z-score anomalies (global)
    zscore_anomalies = detect_zscore_anomalies(df, 'amount', threshold=3.0)
    print(f"    Z-score anomalies:  {len(zscore_anomalies):>6,}")

    # IQR anomalies (global)
    iqr_anomalies = detect_iqr_anomalies(df, 'amount', multiplier=1.5)
    print(f"    IQR anomalies:      {len(iqr_anomalies):>6,}")

    # Category-level anomalies
    cat_anomalies = detect_category_anomalies(df, 'amount')
    print(f"    Category anomalies: {len(cat_anomalies):>6,}")

    # Combine and deduplicate
    all_anomalies = pd.concat([zscore_anomalies, iqr_anomalies, cat_anomalies], ignore_index=True)

    # Keep necessary columns
    output_cols = ['transaction_id', 'anomaly_type', 'anomaly_score',
                   'expected_range_low', 'expected_range_high', 'actual_value',
                   'category', 'account_id', 'detection_method']
    available_cols = [c for c in output_cols if c in all_anomalies.columns]

    if all_anomalies.empty:
        print("    No anomalies detected")
        return pd.DataFrame(columns=output_cols)

    result = all_anomalies[available_cols].drop_duplicates(
        subset=['transaction_id', 'detection_method']
    )

    print(f"    Total unique anomalies: {len(result):,}")
    return result
