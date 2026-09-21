"""
Exercise 2 — migrate normalized MySQL data into denormalized MongoDB
documents (Aulas 1, 2 e 3).

Reads `alertas` JOINed with `ativos` from MySQL (a parameterized query,
even though there are no user-supplied values here) and nests each
alert's asset data directly inside the MongoDB document, trading a JOIN
at read time for duplicated asset data across every alert document.
"""
from diplomat.mongo import get_mongo_db
from diplomat.mysql import run_query
from ex02_migration.setup_mysql import setup_mysql

_JOIN_QUERY = """
    SELECT a.tipo, a.severidade,
           t.nome AS ativo_nome, t.ip AS ativo_ip, t.criticidade AS ativo_criticidade
    FROM alertas a
    JOIN ativos t ON t.id = a.ativo_id
"""


def read_alerts_with_assets() -> list[dict]:
    """Read every alert joined with its asset from MySQL."""
    return run_query(_JOIN_QUERY)


def to_document(row: dict) -> dict:
    """Build the nested MongoDB document for one joined MySQL row."""
    return {
        "tipo": row["tipo"],
        "severidade": row["severidade"],
        "ativo": {
            "nome": row["ativo_nome"],
            "ip": row["ativo_ip"],
            "criticidade": row["ativo_criticidade"],
        },
    }


def migrate() -> None:
    setup_mysql()
    rows = read_alerts_with_assets()
    documents = [to_document(row) for row in rows]

    db = get_mongo_db()
    db.alertas.delete_many({})  # keep the script safely re-runnable
    if documents:
        db.alertas.insert_many(documents)

    mysql_count = len(rows)
    mongo_count = db.alertas.count_documents({})
    status = "MIGRAÇÃO ÍNTEGRA" if mysql_count == mongo_count else "MIGRAÇÃO DIVERGENTE"
    print(f"MySQL: {mysql_count} alertas | MongoDB: {mongo_count} documentos -> {status}")

    high_criticality = db.alertas.count_documents({"ativo.criticidade": "alta"})
    print(
        "Consulta sem JOIN: db.alertas.find({\"ativo.criticidade\": \"alta\"}) "
        f"-> {high_criticality} documentos"
    )

    print(
        "Ganha-se leitura sem JOIN: o alerta ja traz os dados do ativo embutidos.\n"
        "Perde-se em duplicacao: renomear um ativo agora exige um update_many em\n"
        "todos os alertas que o referenciam, em vez de um unico UPDATE relacional."
    )


if __name__ == "__main__":
    migrate()
