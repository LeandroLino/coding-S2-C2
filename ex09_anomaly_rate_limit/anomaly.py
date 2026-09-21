"""
Anomaly-driven traffic analysis for exercise 9.

Aggregation (group/count/distinct-routes/time-window) runs entirely in
MongoDB, not in a Python loop — the app only receives one row per IP,
already reduced to the three behavioral features IsolationForest needs.
"""
from dataclasses import dataclass
from datetime import datetime, timezone

import numpy as np
from sklearn.ensemble import IsolationForest

from diplomat.mongo import get_mongo_db

CONTAMINATION = 0.2
RANDOM_STATE = 42

_AGGREGATION_PIPELINE = [
    {
        "$group": {
            "_id": "$ip",
            "total": {"$sum": 1},
            "erros_4xx": {
                "$sum": {
                    "$cond": [
                        {"$and": [{"$gte": ["$status", 400]}, {"$lt": ["$status", 500]}]},
                        1,
                        0,
                    ]
                }
            },
            "rotas": {"$addToSet": "$rota"},
            "primeiro": {"$min": "$timestamp"},
            "ultimo": {"$max": "$timestamp"},
        }
    },
    {
        "$project": {
            "_id": 0,
            "ip": "$_id",
            "total": 1,
            "erros_4xx": 1,
            "rotas_distintas": {"$size": "$rotas"},
            # At least 1 second, so a burst within the same second doesn't divide by zero.
            "janela_segundos": {
                "$max": [{"$divide": [{"$subtract": ["$ultimo", "$primeiro"]}, 1000]}, 1]
            },
        }
    },
    {
        "$project": {
            "ip": 1,
            "rotas_distintas": 1,
            "taxa_4xx": {"$divide": ["$erros_4xx", "$total"]},
            "req_por_minuto": {"$divide": ["$total", {"$divide": ["$janela_segundos", 60]}]},
        }
    },
]


@dataclass
class IpBehavior:
    ip: str
    req_por_minuto: float
    taxa_4xx: float
    rotas_distintas: int
    anomalo: bool


def _aggregate_access_by_ip() -> list[dict]:
    return list(get_mongo_db().acessos.aggregate(_AGGREGATION_PIPELINE))


def analyze_traffic() -> list[IpBehavior]:
    """Aggregate `acessos` by IP, flag anomalies with IsolationForest, and
    persist the blocked IPs to `bloqueados`.

    Blocking by anomaly instead of a fixed rule is a trade-off, not a free
    win: a burst of legitimate traffic (e.g. a real user retrying after a
    slow network) can look just as unusual as an attacker, so a false
    positive here locks out a real user instead of just rejecting one
    oversized request.
    """
    rows = _aggregate_access_by_ip()
    if not rows:
        return []

    features = np.array(
        [[row["req_por_minuto"], row["taxa_4xx"], row["rotas_distintas"]] for row in rows]
    )
    forest = IsolationForest(contamination=CONTAMINATION, random_state=RANDOM_STATE)
    predictions = forest.fit_predict(features)

    db = get_mongo_db()
    behaviors = []
    for row, prediction in zip(rows, predictions):
        is_anomaly = prediction == -1
        behaviors.append(
            IpBehavior(
                ip=row["ip"],
                req_por_minuto=row["req_por_minuto"],
                taxa_4xx=row["taxa_4xx"],
                rotas_distintas=row["rotas_distintas"],
                anomalo=is_anomaly,
            )
        )
        if is_anomaly:
            db.bloqueados.update_one(
                {"ip": row["ip"]},
                {"$set": {"ip": row["ip"], "bloqueado_em": datetime.now(timezone.utc)}},
                upsert=True,
            )
    return behaviors


def print_analysis(behaviors: list[IpBehavior]) -> None:
    print("=== Análise de acessos ===")
    for behavior in behaviors:
        stats = f"[ {behavior.req_por_minuto:.1f} req/min | 4xx {behavior.taxa_4xx:.2f} | {behavior.rotas_distintas} rotas]"
        if behavior.anomalo:
            print(f"{behavior.ip:<15}{stats}  -> ANOMALIA -> bloqueado")
        else:
            print(f"{behavior.ip:<15}{stats}  -> normal")


def is_ip_blocked(ip: str) -> bool:
    return get_mongo_db().bloqueados.count_documents({"ip": ip}) > 0
