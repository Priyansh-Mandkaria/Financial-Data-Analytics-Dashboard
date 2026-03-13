"""
Database Manager - SQLite connection and query helpers.
"""

import sqlite3
import os
import pandas as pd
from contextlib import contextmanager


DB_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'database')
DB_PATH = os.path.join(DB_DIR, 'financial_data.db')
SCHEMA_PATH = os.path.join(DB_DIR, 'schema.sql')


@contextmanager
def get_connection(db_path: str = DB_PATH):
    """Context-managed SQLite connection."""
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=OFF")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def initialize_database(db_path: str = DB_PATH) -> None:
    """Create database and tables from schema."""
    os.makedirs(os.path.dirname(db_path), exist_ok=True)

    # Remove existing DB for fresh start
    if os.path.exists(db_path):
        os.remove(db_path)

    with open(SCHEMA_PATH, 'r') as f:
        schema_sql = f.read()

    with get_connection(db_path) as conn:
        conn.executescript(schema_sql)

    print(f"  ✓ Database initialized: {db_path}")


def bulk_insert(df: pd.DataFrame, table_name: str, db_path: str = DB_PATH) -> int:
    """Bulk insert a DataFrame into a table. Returns number of rows inserted."""
    with get_connection(db_path) as conn:
        rows = df.to_sql(table_name, conn, if_exists='append', index=False)
    return rows if rows else len(df)


def execute_query(query: str, params: tuple = None, db_path: str = DB_PATH) -> pd.DataFrame:
    """Execute a SELECT query and return results as DataFrame."""
    with get_connection(db_path) as conn:
        if params:
            return pd.read_sql_query(query, conn, params=params)
        return pd.read_sql_query(query, conn)


def execute_statement(statement: str, params: tuple = None, db_path: str = DB_PATH) -> int:
    """Execute an INSERT/UPDATE/DELETE statement. Returns affected rows."""
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        if params:
            cursor.execute(statement, params)
        else:
            cursor.execute(statement)
        return cursor.rowcount


def get_table_counts(db_path: str = DB_PATH) -> dict:
    """Get record counts for all tables."""
    tables = ['transactions', 'ledger_entries', 'benchmarks', 'quality_log', 'anomaly_log']
    counts = {}
    with get_connection(db_path) as conn:
        for table in tables:
            try:
                cursor = conn.execute(f"SELECT COUNT(*) FROM {table}")
                counts[table] = cursor.fetchone()[0]
            except sqlite3.OperationalError:
                counts[table] = 0
    return counts
