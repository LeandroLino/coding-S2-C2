"""
Exercise 3 setup — creates the MongoDB `eventos` collection with a TTL
index and seeds it with 200 failure events spread across the last 24
hours (Aula 2).
"""
import random
from datetime import datetime, timedelta, timezone

from diplomat.mongo import get_mongo_db

EVENT_COUNT = 200
TTL_SECONDS = 604800  # 7 days


def seed_events(count: int = EVENT_COUNT) -> None:
    """(Re)create `eventos` with a TTL index and `count` random events."""
    db = get_mongo_db()
    db.eventos.drop()  # keep this re-runnable

    reference = datetime.now(timezone.utc)
    events = [
        {
            "timestamp": reference - timedelta(seconds=random.uniform(0, 24 * 3600)),
            "tipo": "login_falho",
        }
        for _ in range(count)
    ]
    db.eventos.insert_many(events)
    db.eventos.create_index("timestamp", expireAfterSeconds=TTL_SECONDS)


if __name__ == "__main__":
    seed_events()
    print(f"MongoDB populated: {EVENT_COUNT} eventos, TTL index on timestamp ({TTL_SECONDS}s)")
