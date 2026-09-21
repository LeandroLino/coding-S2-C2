"""
Exercise 4 — privilege-change transaction with an audit trail (Aulas
2, 3 e 8/A09).

`alterar_nivel` only commits a `usuarios.nivel_acesso` change when
every rule passes; every attempt — accepted or refused — is recorded
in the Mongo `auditoria` collection, because an attack that leaves no
trace is an invisible attack (A09).

This function needs manual commit/rollback control across multiple
statements in one transaction, so it uses `get_mysql_connection`
directly instead of the single-shot `run_query`/`run_write` helpers:
the transaction itself is the mechanic being exercised here, not
something to hide behind a generic wrapper.
"""
from datetime import datetime, timezone

from diplomat.mongo import get_mongo_db
from diplomat.mysql import get_mysql_connection
from ex04_audit_trail.setup_mysql import setup_mysql

MIN_NIVEL_PARA_ALTERAR = 5


def _fetch_user(cur, user_id: int) -> dict | None:
    cur.execute("SELECT nome, nivel_acesso FROM usuarios WHERE id = %s", (user_id,))
    return cur.fetchone()


def registrar_auditoria(
    admin_id: int, alvo_id: int, nivel_anterior: int | None, novo_nivel: int, resultado: str
) -> None:
    """Record every attempt (accepted or refused) in the Mongo audit trail."""
    db = get_mongo_db()
    db.auditoria.insert_one(
        {
            "quem": admin_id,
            "alvo": alvo_id,
            "nivel_anterior": nivel_anterior,
            "nivel_novo": novo_nivel,
            "resultado": resultado,
            "timestamp": datetime.now(timezone.utc),
        }
    )


def alterar_nivel(admin_id: int, alvo_id: int, novo_nivel: int) -> dict:
    """Change `alvo_id`'s access level within a transaction, if allowed.

    Returns a dict describing the outcome for display purposes.
    """
    conn = get_mysql_connection()
    try:
        cur = conn.cursor(dictionary=True)
        admin = _fetch_user(cur, admin_id)
        alvo = _fetch_user(cur, alvo_id)
        nivel_anterior = alvo["nivel_acesso"] if alvo else None
        nivel_atual = nivel_anterior

        if admin is None or admin["nivel_acesso"] < MIN_NIVEL_PARA_ALTERAR:
            resultado, motivo = "RECUSADO", "admin sem privilégio"
        elif admin_id == alvo_id:
            resultado, motivo = "RECUSADO", "auto-promoção"
        elif alvo is None:
            resultado, motivo = "RECUSADO", "alvo inexistente"
        else:
            cur.execute(
                "UPDATE usuarios SET nivel_acesso = %s WHERE id = %s", (novo_nivel, alvo_id)
            )
            conn.commit()
            resultado, motivo = "OK", None
            nivel_atual = novo_nivel

        if resultado == "RECUSADO":
            conn.rollback()
    finally:
        conn.close()

    registrar_auditoria(admin_id, alvo_id, nivel_anterior, novo_nivel, resultado)

    return {
        "resultado": resultado,
        "motivo": motivo,
        "alvo_nome": alvo["nome"] if alvo else None,
        "nivel_anterior": nivel_anterior,
        "nivel_atual": nivel_atual,
    }


def _print_attempt(admin_id: int, alvo_id: int, novo_nivel: int, outcome: dict) -> None:
    call = f"alterar_nivel({admin_id}, {alvo_id}, {novo_nivel})"
    nome = outcome["alvo_nome"].capitalize() if outcome["alvo_nome"] else None
    if outcome["resultado"] == "OK":
        print(f"{call} -> OK. commit. {nome}: {outcome['nivel_anterior']} -> {novo_nivel}")
    elif nome is None:
        print(f"{call} -> RECUSADO ({outcome['motivo']}). rollback.")
    else:
        print(f"{call} -> RECUSADO ({outcome['motivo']}). rollback. {nome}: {outcome['nivel_atual']}")


def run_demo() -> None:
    setup_mysql()
    get_mongo_db().auditoria.delete_many({})  # keep this re-runnable

    tentativas = [(1, 2, 4), (2, 3, 5), (1, 1, 9), (1, 99, 3)]
    for admin_id, alvo_id, novo_nivel in tentativas:
        outcome = alterar_nivel(admin_id, alvo_id, novo_nivel)
        _print_attempt(admin_id, alvo_id, novo_nivel, outcome)

    db = get_mongo_db()
    total = db.auditoria.count_documents({})
    recusados = db.auditoria.count_documents({"resultado": "RECUSADO"})
    print(f"\nTrilha de auditoria ao final: {total} documentos "
          f"({total - recusados} sucesso, {recusados} recusas)")
    print(f'db.auditoria.count_documents({{"resultado":"RECUSADO"}}) -> {recusados}')


if __name__ == "__main__":
    run_demo()
