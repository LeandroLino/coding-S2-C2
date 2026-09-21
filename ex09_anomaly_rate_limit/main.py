"""
Exercise 9 — Rate limiting guided by anomaly detection (Aulas 2, 4, 6
e 8/A09). The API becomes its own data source: every request is logged,
aggregated per IP, and IsolationForest decides who behaves like an
attacker.
"""
from datetime import datetime, timezone

from flask import g, jsonify, request

from diplomat.mongo import get_mongo_db
from ex09_anomaly_rate_limit.anomaly import analyze_traffic, is_ip_blocked, print_analysis
from ex09_anomaly_rate_limit.setup_mongo import setup_mongo
from providers.app_factory import create_app
from providers.errors import json_error

app = create_app(__name__)


def _client_ip() -> str:
    # X-Forwarded-For lets the test script simulate different source IPs
    # against a single local server; falls back to the real socket address.
    forwarded = request.headers.get("X-Forwarded-For")
    return forwarded.split(",")[0].strip() if forwarded else request.remote_addr


@app.before_request
def block_or_log_request():
    ip = _client_ip()
    if is_ip_blocked(ip):
        response = json_error("muitas requisições", 429)
        response.headers["Retry-After"] = "60"
        return response

    result = get_mongo_db().acessos.insert_one(
        {
            "ip": ip,
            "rota": request.path,
            "metodo": request.method,
            "timestamp": datetime.now(timezone.utc),
        }
    )
    g.access_log_id = result.inserted_id


@app.after_request
def complete_request_log(response):
    access_log_id = getattr(g, "access_log_id", None)
    if access_log_id is not None:
        get_mongo_db().acessos.update_one(
            {"_id": access_log_id}, {"$set": {"status": response.status_code}}
        )
    return response


@app.route("/api/ping")
def ping():
    return jsonify({"pong": True})


@app.route("/api/dados")
def dados():
    return jsonify({"dados": [1, 2, 3]})


@app.route("/api/seguranca/analisar", methods=["POST"])
def analisar_seguranca():
    behaviors = analyze_traffic()
    print_analysis(behaviors)
    return jsonify(
        [
            {
                "ip": b.ip,
                "req_por_minuto": round(b.req_por_minuto, 2),
                "taxa_4xx": round(b.taxa_4xx, 2),
                "rotas_distintas": b.rotas_distintas,
                "resultado": "anomalia" if b.anomalo else "normal",
            }
            for b in behaviors
        ]
    )


if __name__ == "__main__":
    setup_mongo()
    app.run(port=5000)
