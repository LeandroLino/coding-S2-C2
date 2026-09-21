"""MySQL connection helper shared across all exercises.

Exercise code should not call `cursor.execute(...)` directly — use the
`run_query`/`run_write`/`run_many` helpers below so every query is
parameterized and connections are always opened/committed/closed
consistently in one place.
"""
import mysql.connector
from mysql.connector import MySQLConnection

from config import Config


def get_mysql_connection() -> MySQLConnection:
    """Return a new MySQL connection using credentials from environment vars."""
    return mysql.connector.connect(
        host=Config.MYSQL_HOST,
        port=Config.MYSQL_PORT,
        user=Config.MYSQL_USER,
        password=Config.MYSQL_PASSWORD,
        database=Config.MYSQL_DATABASE,
    )


def run_query(sql: str, params: tuple = ()) -> list[dict]:
    """Run a parameterized SELECT and return every row as a dict."""
    conn = get_mysql_connection()
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute(sql, params)
        return cur.fetchall()
    finally:
        conn.close()


def run_write(sql: str, params: tuple = ()) -> int:
    """Run one parameterized write statement (INSERT/UPDATE/DELETE/DDL).

    Commits and returns the number of affected rows.
    """
    conn = get_mysql_connection()
    try:
        cur = conn.cursor()
        cur.execute(sql, params)
        conn.commit()
        return cur.rowcount
    finally:
        conn.close()


def run_many(sql: str, seq_of_params: list[tuple]) -> int:
    """Run one parameterized statement against many rows (batched insert).

    Commits and returns the number of affected rows.
    """
    conn = get_mysql_connection()
    try:
        cur = conn.cursor()
        cur.executemany(sql, seq_of_params)
        conn.commit()
        return cur.rowcount
    finally:
        conn.close()
