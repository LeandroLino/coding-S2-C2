"""MongoDB connection helper shared across all exercises."""
from pymongo import MongoClient
from pymongo.database import Database

from config import Config

_client: MongoClient | None = None


def get_mongo_client() -> MongoClient:
    """Return a singleton MongoClient (reused across calls in the same process)."""
    global _client
    if _client is None:
        _client = MongoClient(Config.MONGO_URI)
    return _client


def get_mongo_db() -> Database:
    """Return the default application database."""
    return get_mongo_client()[Config.MONGO_DATABASE]
