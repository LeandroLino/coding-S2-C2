"""
Exercise 3 — TTL retention and hourly failure distribution (Aula 2).

A SOC does not keep logs forever nor look at raw totals — it looks at
the time window. `eventos` carries a TTL index so old events expire on
their own, and the report below aggregates failures by hour of day to
show when they concentrate.
"""
from diplomat.mongo import get_mongo_db
from ex03_retention.setup_mongo import TTL_SECONDS, seed_events

BAR_CHAR = "█"
BAR_MAX_WIDTH = 40


def failures_by_hour() -> list[dict]:
    """Aggregate `eventos` into a count per hour of day, sorted by hour."""
    db = get_mongo_db()
    pipeline = [
        {"$group": {"_id": {"$hour": "$timestamp"}, "total": {"$sum": 1}}},
        {"$sort": {"_id": 1}},
    ]
    return list(db.eventos.aggregate(pipeline))


def report() -> None:
    seed_events()
    counts = failures_by_hour()

    print("=== Falhas por hora (últimas 24h) ===")
    peak = max(counts, key=lambda c: c["total"])
    highest_total = peak["total"]
    for c in counts:
        hour, total = c["_id"], c["total"]
        bar_length = max(1, round(total / highest_total * BAR_MAX_WIDTH))
        marker = "   <- pico" if hour == peak["_id"] else ""
        print(f"{hour:02d}h | {BAR_CHAR * bar_length} {total}{marker}")

    print(f"Hora de pico: {peak['_id']:02d}h ({highest_total} falhas)")
    ttl_days = TTL_SECONDS // 86400
    print(
        f"Índice TTL ativo: eventos com mais de {ttl_days} dias serão removidos automaticamente."
    )
    print(
        "Comentário: o TTL é uma decisão de segurança porque limita por quanto "
        "tempo dados sensíveis de eventos ficam expostos a vazamento, não apenas "
        "quanto espaço em disco é economizado."
    )


if __name__ == "__main__":
    report()
