# Standard Operating Procedure: Root Cause Analysis for Data Discrepancies

## 1. Purpose

This SOP defines the process for investigating and resolving data discrepancies identified through the Financial Data Analytics Dashboard. It ensures consistent, documented investigation of data quality issues, reconciliation mismatches, and anomalies.

## 2. Scope

Applies to all data discrepancies detected via:
- **Data Quality Checks** — null values, duplicates, format errors, range violations
- **Anomaly Detection** — statistical outliers (Z-score, IQR)
- **Reconciliation** — transaction-ledger mismatches

## 3. Severity Classification

| Severity | Criteria | Response Time |
|----------|----------|---------------|
| **Critical** | >5% records affected, financial impact >$100K | 4 hours |
| **High** | 1-5% records affected, financial impact $10K-$100K | 24 hours |
| **Medium** | 0.1-1% records affected, minimal financial impact | 72 hours |
| **Low** | <0.1% records affected, cosmetic/format issues | Next sprint |

## 4. Investigation Steps

### Step 1: Identify and Log
1. Record the discrepancy type, affected records count, and source system
2. Create a ticket with severity classification
3. Capture dashboard screenshots documenting the issue

### Step 2: Isolate the Data
1. Query affected records: filter by date range, category, account
2. Export to a working spreadsheet for detailed analysis
3. Compare against source systems (ERP, CRM, bank feeds)

### Step 3: Root Cause Categories

| Category | Common Causes | Investigation Focus |
|----------|--------------|-------------------|
| **Source Data** | Manual entry errors, system bugs, API failures | Check source system logs and input forms |
| **ETL Process** | Transformation logic errors, mapping issues | Review pipeline logs and transformation rules |
| **Timing** | Late-arriving data, timezone mismatches | Compare timestamps across systems |
| **Duplicate** | Multiple submissions, retry logic, batch reprocessing | Check transaction IDs and dedup logic |
| **Format** | Date format variations, currency codes, encoding | Validate input file formats and parsers |

### Step 4: Determine Impact
1. Calculate financial impact (sum of affected amounts)
2. Identify downstream reports/systems affected
3. Assess regulatory reporting implications

### Step 5: Remediate
1. Apply data corrections (manual patches or re-run ETL)
2. Validate corrections against source of truth
3. Re-run quality checks to confirm resolution

### Step 6: Prevent Recurrence
1. Add validation rule to `analytics/quality_checks.py`
2. Update ETL transformation logic in `etl/transform.py`
3. Add monitoring alert threshold

## 5. Documentation Template

```
DISCREPANCY REPORT
==================
Date Identified  : [YYYY-MM-DD]
Reported By      : [Name]
Severity         : [Critical/High/Medium/Low]
Ticket ID        : [JIRA/Ticket #]

DESCRIPTION
-----------
[Brief description of the discrepancy]

AFFECTED DATA
--------------
Records Affected : [Count]
Date Range       : [Start] to [End]
Categories       : [List]
Financial Impact : $[Amount]

ROOT CAUSE
----------
Category         : [Source Data / ETL / Timing / Duplicate / Format]
Details          : [Detailed explanation]
Source System    : [System name]

RESOLUTION
----------
Action Taken     : [Description]
Validated By     : [Name]
Validation Date  : [YYYY-MM-DD]

PREVENTION
----------
Rule Added       : [Yes/No — description]
ETL Updated      : [Yes/No — description]
Monitoring Added : [Yes/No — threshold]
```

## 6. Escalation Path

1. **Analyst** → Initial investigation and documentation
2. **Data Engineer** → ETL fixes and pipeline updates
3. **Finance Manager** → Financial impact assessment
4. **Compliance** → Regulatory reporting implications (if applicable)

## 7. Review Schedule

- **Weekly**: Review open discrepancy tickets
- **Monthly**: Analyze discrepancy trends and update quality rules
- **Quarterly**: Full SOP review and process improvement
