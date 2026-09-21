"""
Exercise 9 setup — Mongo side only: `acessos` (raw request log) and
`bloqueados` (anomaly-blocked IPs) both start empty so every run is a
clean slate for the traffic script.
"""
from diplomat.mongo import get_mongo_db


def setup_mongo() -> None:
    db = get_mongo_db()
    db.acessos.drop()
    db.bloqueados.drop()


if __name__ == "__main__":
    setup_mongo()
    print("MongoDB ready: acessos and bloqueados collections cleared")
