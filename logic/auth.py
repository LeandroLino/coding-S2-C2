"""
API-key based authentication shared across exercises (6, 8, 9...).

Looks up the caller in MySQL using a parameterized query — never string
concatenation — and distinguishes 401 (unknown identity) from 403
(known identity, insufficient privilege), per exercise 6's requirement.
"""
from dataclasses import dataclass
from typing import Optional

from flask import request

from diplomat.mysql import get_mysql_connection


@dataclass
class Analyst:
    id: int
    name: str
    level: int


def get_authenticated_analyst() -> Optional[Analyst]:
    """Return the Analyst for the X-API-Key header, or None if missing/invalid."""
    api_key = request.headers.get("X-API-Key")
    if not api_key:
        return None

    conn = get_mysql_connection()
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute(
            "SELECT id, name, level FROM analysts WHERE api_key = %s",
            (api_key,),
        )
        row = cur.fetchone()
    finally:
        conn.close()

    if row is None:
        return None
    return Analyst(id=row["id"], name=row["name"], level=row["level"])
