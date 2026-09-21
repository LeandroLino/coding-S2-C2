"""
Exercise 6 — broken access control / IDOR (Aulas 3, 6 e 8/A01).

Every analyst can only see their **own** incidents; only level >= 5 can
delete any incident. Authentication is by the `X-API-Key` header,
validated in MySQL with a parameterized query (`logic.auth`).

401 vs 403: 401 means "I don't know who you are" (missing/invalid key);
403 means "I know who you are, and you can't do that". A 403 body
never reveals whether the target incident exists or who owns it —
only a generic denial message.
"""
from diplomat.mysql import run_query, run_write
from ex06_broken_access.setup_mysql import setup_mysql
from logic.auth import get_authenticated_analyst
from providers.app_factory import create_app
from providers.errors import json_error

app = create_app(__name__)

MIN_LEVEL_TO_DELETE = 5

_INCIDENT_COLUMNS = "id, dono_id, titulo, severidade, status"


@app.route("/api/incidentes/<int:incident_id>", methods=["GET"])
def get_incident(incident_id: int):
    analyst = get_authenticated_analyst()
    if analyst is None:
        return json_error("não autenticado", 401)

    rows = run_query(f"SELECT {_INCIDENT_COLUMNS} FROM incidentes WHERE id = %s", (incident_id,))
    if not rows:
        return json_error("incidente não encontrado", 404)

    incident = rows[0]
    if incident["dono_id"] != analyst.id:
        return json_error("acesso negado", 403)

    return {"incidente": incident}, 200


@app.route("/api/incidentes", methods=["GET"])
def list_incidents():
    analyst = get_authenticated_analyst()
    if analyst is None:
        return json_error("não autenticado", 401)

    rows = run_query(
        f"SELECT {_INCIDENT_COLUMNS} FROM incidentes WHERE dono_id = %s", (analyst.id,)
    )
    return {"incidentes": rows}, 200


@app.route("/api/incidentes/<int:incident_id>", methods=["DELETE"])
def delete_incident(incident_id: int):
    analyst = get_authenticated_analyst()
    if analyst is None:
        return json_error("não autenticado", 401)
    if analyst.level < MIN_LEVEL_TO_DELETE:
        return json_error("acesso negado", 403)

    rows = run_query("SELECT id FROM incidentes WHERE id = %s", (incident_id,))
    if not rows:
        return json_error("incidente não encontrado", 404)

    run_write("DELETE FROM incidentes WHERE id = %s", (incident_id,))
    return {"status": "removido"}, 200


if __name__ == "__main__":
    setup_mysql()
    app.run(port=5000)
