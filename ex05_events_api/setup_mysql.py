"""
Exercise 5 setup — creates and populates the MySQL `eventos` table used
by the sortable events API (Aulas 3, 6, 7 e 8/A05).
"""
import random
from datetime import datetime, timedelta

from diplomat.mysql import run_many, run_write

SEVERIDADES = ["baixa", "media", "alta", "critica"]
EVENT_COUNT = 150


def _random_event(i: int, reference: datetime) -> tuple:
    severidade = random.choice(SEVERIDADES)
    ip_origem = f"10.0.0.{random.randint(1, 254)}"
    criado_em = reference - timedelta(minutes=random.randint(0, 60 * 24))
    return (i, severidade, ip_origem, criado_em)


def setup_mysql() -> None:
    """(Re)create and populate `eventos`, so this is re-runnable."""
    run_write("DROP TABLE IF EXISTS eventos")
    run_write(
        """
        CREATE TABLE eventos (
            id INT PRIMARY KEY,
            severidade VARCHAR(20) NOT NULL,
            ip_origem VARCHAR(45) NOT NULL,
            criado_em DATETIME NOT NULL
        )
        """
    )
    reference = datetime.now()
    events = [_random_event(i, reference) for i in range(1, EVENT_COUNT + 1)]
    run_many(
        "INSERT INTO eventos (id, severidade, ip_origem, criado_em) VALUES (%s, %s, %s, %s)",
        events,
    )


if __name__ == "__main__":
    setup_mysql()
    print(f"MySQL populated: {EVENT_COUNT} eventos")
