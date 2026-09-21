"""MySQL connection helper shared across all exercises."""
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
