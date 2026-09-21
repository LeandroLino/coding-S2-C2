"""
Exercise 8 setup — Mongo side only: the `previsoes` collection just needs
to start empty so the "2 previsoes validas" check in the assignment is
reproducible on every run (no fixture rows to seed here, unlike the
other exercises).
"""
from diplomat.mongo import get_mongo_db


def setup_mongo() -> None:
    """Drop `previsoes` so each run starts from a clean audit trail."""
    get_mongo_db().previsoes.drop()


if __name__ == "__main__":
    setup_mongo()
    print("MongoDB ready: previsoes collection cleared")
