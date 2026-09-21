"""
Exercise 5 — the ORDER BY that %s doesn't protect (Aulas 3, 6, 7 e
8/A05).

`%s` parameterizes *data* (values), never *identifiers* (column/table
names). `LIMIT %s` works because a row count is data — the driver can
bind it as a literal. `ORDER BY %s` cannot work the same way: MySQL
needs an identifier in that position, so the driver would either bind
it as a quoted string literal (a no-op, ignored as sort key) or, if the
query were built by string concatenation instead, open a straight SQL
injection. The fix is a closed whitelist that maps a small set of
public names to the one and only real column each is allowed to mean.
"""
from datetime import datetime

from flask import request

from adapters.validators import validate_positive_int, validate_whitelisted_value
from diplomat.mysql import run_query
from ex05_events_api.setup_mysql import setup_mysql
from providers.app_factory import create_app
from providers.errors import json_error

app = create_app(__name__)

COLUNAS = {"data": "criado_em", "sev": "severidade", "ip": "ip_origem"}
ORDEM = {"asc": "ASC", "desc": "DESC"}
DEFAULT_TAMANHO = 10
MAX_TAMANHO = 100


@app.route("/api/eventos", methods=["GET"])
def listar_eventos():
    try:
        coluna = validate_whitelisted_value(request.args.get("ordenar_por", "data"), COLUNAS)
    except ValueError:
        return json_error("campo de ordenação inválido", 400)

    try:
        direcao = validate_whitelisted_value(request.args.get("ordem", "asc"), ORDEM)
    except ValueError:
        return json_error("ordem inválida", 400)

    try:
        tamanho = validate_positive_int(
            request.args.get("tamanho", DEFAULT_TAMANHO), max_value=MAX_TAMANHO
        )
    except ValueError:
        return json_error("tamanho deve ser inteiro", 400)

    # `coluna`/`direcao` only ever hold whitelisted literals at this point,
    # so interpolating them here is safe; `tamanho` is real data and still
    # goes through a parameterized placeholder.
    query = f"SELECT * FROM eventos ORDER BY {coluna} {direcao} LIMIT %s"
    rows = run_query(query, (tamanho,))
    for row in rows:
        if isinstance(row.get("criado_em"), datetime):
            row["criado_em"] = row["criado_em"].isoformat()

    return {"eventos": rows}, 200


if __name__ == "__main__":
    setup_mysql()
    app.run(port=5000)
