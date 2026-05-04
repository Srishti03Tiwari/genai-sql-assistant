# database/db_connection.py
import sqlite3
import pandas as pd
from config import DB_PATH


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def run_query(sql: str) -> pd.DataFrame:
    conn = get_connection()
    try:
        df = pd.read_sql_query(sql, conn)
        return df
    finally:
        conn.close()


def get_schema_as_text() -> str:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cursor.fetchall()]

    schema_parts = []
    for table in tables:
        cursor.execute(f"PRAGMA table_info({table});")
        cols = cursor.fetchall()
        col_defs = ", ".join(f"{c[1]} ({c[2]})" for c in cols)
        schema_parts.append(f"Table: {table}\nColumns: {col_defs}")

    conn.close()
    return "\n\n".join(schema_parts)