"""
Exercise 7 setup — seeds the MongoDB `incidentes` collection with two
XSS payloads used to prove the dashboard escapes both text content and
attribute values (Aulas 6, 7 e 8/A05).
"""
from diplomat.mongo import get_mongo_db

# p1 breaks out with a <script> tag; rendered as a table cell (text context).
# p2 has no <script> at all — it breaks out of an HTML *attribute* instead.
PAYLOAD_SCRIPT_TAG = "<script>alert('xss1')</script>"
PAYLOAD_ATTRIBUTE_BREAKOUT = "x\" onerror=\"alert('xss2')"

INCIDENTES = [
    {"titulo": PAYLOAD_SCRIPT_TAG, "ativo": "SRV-WEB01"},
    {"titulo": "Alerta de phishing", "ativo": PAYLOAD_ATTRIBUTE_BREAKOUT},
]


def setup_mongo() -> None:
    """(Re)create and populate `incidentes`, so this is re-runnable."""
    db = get_mongo_db()
    db.incidentes.drop()
    db.incidentes.insert_many(INCIDENTES)


if __name__ == "__main__":
    setup_mongo()
    print(f"MongoDB populated: {len(INCIDENTES)} incidentes")
