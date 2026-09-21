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

MIN_LEVEL_TO_ALTER = 5


def _fetch_user(cur, user_id: int) -> dict | None:
    cur.execute("SELECT nome, nivel_acesso FROM usuarios WHERE id = %s", (user_id,))
    return cur.fetchone()


def record_audit(
    admin_id: int, target_id: int, previous_level: int | None, new_level: int, result: str
) -> None:
    """Record every attempt (accepted or refused) in the Mongo audit trail."""
    db = get_mongo_db()
    db.auditoria.insert_one(
        {
            "quem": admin_id,
            "alvo": target_id,
            "nivel_anterior": previous_level,
            "nivel_novo": new_level,
            "resultado": result,
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
        target = _fetch_user(cur, alvo_id)
        previous_level = target["nivel_acesso"] if target else None
        current_level = previous_level

        if admin is None or admin["nivel_acesso"] < MIN_LEVEL_TO_ALTER:
            result, reason = "RECUSADO", "admin sem privilégio"
        elif admin_id == alvo_id:
            result, reason = "RECUSADO", "auto-promoção"
        elif target is None:
            result, reason = "RECUSADO", "alvo inexistente"
        else:
            cur.execute(
                "UPDATE usuarios SET nivel_acesso = %s WHERE id = %s", (novo_nivel, alvo_id)
            )
            conn.commit()
            result, reason = "OK", None
            current_level = novo_nivel

        if result == "RECUSADO":
            conn.rollback()
    finally:
        conn.close()

    record_audit(admin_id, alvo_id, previous_level, novo_nivel, result)

    return {
        "result": result,
        "reason": reason,
        "target_name": target["nome"] if target else None,
        "previous_level": previous_level,
        "current_level": current_level,
    }


def _print_attempt(admin_id: int, alvo_id: int, novo_nivel: int, outcome: dict) -> None:
    call = f"alterar_nivel({admin_id}, {alvo_id}, {novo_nivel})"
    name = outcome["target_name"].capitalize() if outcome["target_name"] else None
    if outcome["result"] == "OK":
        print(f"{call} -> OK. commit. {name}: {outcome['previous_level']} -> {novo_nivel}")
    elif name is None:
        print(f"{call} -> RECUSADO ({outcome['reason']}). rollback.")
    else:
        print(f"{call} -> RECUSADO ({outcome['reason']}). rollback. {name}: {outcome['current_level']}")


def run_demo() -> None:
    setup_mysql()
    get_mongo_db().auditoria.delete_many({})  # keep this re-runnable

    attempts = [(1, 2, 4), (2, 3, 5), (1, 1, 9), (1, 99, 3)]
    for admin_id, alvo_id, novo_nivel in attempts:
        outcome = alterar_nivel(admin_id, alvo_id, novo_nivel)
        _print_attempt(admin_id, alvo_id, novo_nivel, outcome)

    db = get_mongo_db()
    total = db.auditoria.count_documents({})
    refused = db.auditoria.count_documents({"resultado": "RECUSADO"})
    print(f"\nTrilha de auditoria ao final: {total} documentos "
          f"({total - refused} sucesso, {refused} recusas)")
    print(f'db.auditoria.count_documents({{"resultado":"RECUSADO"}}) -> {refused}')


if __name__ == "__main__":
    run_demo()
