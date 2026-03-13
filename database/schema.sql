-- Financial Data Analytics Dashboard - Database Schema

CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    transaction_id TEXT UNIQUE,
    transaction_date DATE NOT NULL,
    account_id TEXT NOT NULL,
    account_name TEXT,
    category TEXT NOT NULL,
    subcategory TEXT,
    amount REAL NOT NULL,
    currency TEXT DEFAULT 'USD',
    transaction_type TEXT CHECK(transaction_type IN ('credit', 'debit')),
    status TEXT CHECK(status IN ('completed', 'pending', 'failed', 'reversed')),
    counterparty TEXT,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS ledger_entries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    entry_id TEXT UNIQUE,
    transaction_id TEXT,
    entry_date DATE NOT NULL,
    account_id TEXT NOT NULL,
    debit_amount REAL DEFAULT 0,
    credit_amount REAL DEFAULT 0,
    balance REAL,
    ledger_type TEXT CHECK(ledger_type IN ('general', 'accounts_receivable', 'accounts_payable')),
    reconciled INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (transaction_id) REFERENCES transactions(transaction_id)
);

CREATE TABLE IF NOT EXISTS benchmarks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    benchmark_date DATE NOT NULL,
    benchmark_name TEXT NOT NULL,
    category TEXT,
    expected_value REAL NOT NULL,
    actual_value REAL,
    variance REAL,
    variance_pct REAL,
    status TEXT CHECK(status IN ('within_range', 'warning', 'critical')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS quality_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    check_name TEXT NOT NULL,
    check_type TEXT NOT NULL,
    table_name TEXT NOT NULL,
    column_name TEXT,
    total_records INTEGER,
    passed_records INTEGER,
    failed_records INTEGER,
    pass_rate REAL,
    severity TEXT CHECK(severity IN ('low', 'medium', 'high', 'critical')),
    details TEXT,
    checked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS anomaly_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    transaction_id TEXT,
    anomaly_type TEXT NOT NULL,
    anomaly_score REAL,
    expected_range_low REAL,
    expected_range_high REAL,
    actual_value REAL,
    category TEXT,
    account_id TEXT,
    detection_method TEXT,
    detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (transaction_id) REFERENCES transactions(transaction_id)
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_transactions_date ON transactions(transaction_date);
CREATE INDEX IF NOT EXISTS idx_transactions_account ON transactions(account_id);
CREATE INDEX IF NOT EXISTS idx_transactions_category ON transactions(category);
CREATE INDEX IF NOT EXISTS idx_transactions_status ON transactions(status);
CREATE INDEX IF NOT EXISTS idx_ledger_transaction ON ledger_entries(transaction_id);
CREATE INDEX IF NOT EXISTS idx_ledger_date ON ledger_entries(entry_date);
CREATE INDEX IF NOT EXISTS idx_benchmarks_date ON benchmarks(benchmark_date);
CREATE INDEX IF NOT EXISTS idx_anomaly_transaction ON anomaly_log(transaction_id);
