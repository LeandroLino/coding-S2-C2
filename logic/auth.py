"""
API-key based authentication shared across exercises (6, 8, 9...).

Looks up the caller in MySQL using a parameterized query — never string
concatenation — and distinguishes 401 (unknown identity) from 403
(known identity, insufficient privilege), per exercise 6's requirement.
"""
from dataclasses import dataclass
from typing import Optional

from flask import request

from diplomat.mysql import run_query


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

    rows = run_query("SELECT id, nome, nivel FROM analistas WHERE api_key = %s", (api_key,))
    if not rows:
        return None
    row = rows[0]
    return Analyst(id=row["id"], name=row["nome"], level=row["nivel"])
