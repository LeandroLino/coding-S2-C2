"""
app_seguro.py — versão corrigida do Exercício 10.

Mesmas rotas de `app_vulneravel.py`, com cada uma das 8 falhas do
`auditoria.md` corrigida:

1/5. Query parametrizada e SELECT explícito sem a coluna `senha`.
2. `perfil.html` usa Jinja2 (escape por padrão) em vez de f-string.
3. DELETE exige `X-API-Key`: 401 sem credencial, 403 com nível < 5.
4. Erro de banco tratado -> resposta genérica (sem traceback/nome de
   tabela), via os error handlers já compartilhados do projeto.
6. Headers de segurança (CSP, X-Content-Type-Options, X-Frame-Options)
   aplicados globalmente por `create_app()`.
7. Nenhum segredo hardcoded — toda credencial vem de variável de ambiente
   (`config.Config`), e a autenticação usa `api_key` armazenada no banco.
8. Cada requisição é logada (rota, método, IP, status) para auditoria.
"""
import logging

from flask import g, jsonify, render_template, request

from diplomat.mysql import run_query, run_write
from ex10_before_after.setup_mysql import setup_mysql
from providers.app_factory import create_app
from providers.errors import json_error

REQUIRED_LEVEL_TO_DELETE = 5

app = create_app(__name__)

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
logger = logging.getLogger("ex10_audit")


@app.before_request
def start_request_log():
    g.request_ip = request.headers.get("X-Forwarded-For", request.remote_addr)


@app.after_request
def finish_request_log(response):
    logger.info(
        "%s %s ip=%s status=%s", request.method, request.path, g.get("request_ip"), response.status_code
    )
    return response


def _authenticate(required_level: int):
    """Return (user, None) on success, or (None, error_response) otherwise."""
    api_key = request.headers.get("X-API-Key")
    if not api_key:
        return None, json_error("não autorizado", 401)

    rows = run_query("SELECT * FROM usuarios_ex10 WHERE api_key = %s", (api_key,))
    if not rows:
        return None, json_error("não autorizado", 401)

    user = rows[0]
    if user["nivel_acesso"] < required_level:
        return None, json_error("acesso negado", 403)
    return user, None


@app.route("/api/usuarios/buscar")
def search_users():
    nome = request.args.get("nome", "")
    rows = run_query(
        "SELECT id, nome, email, nivel_acesso FROM usuarios_ex10 WHERE nome LIKE %s",
        (f"%{nome}%",),
    )
    return jsonify(rows)


@app.route("/perfil")
def profile():
    return render_template("perfil.html", user=request.args.get("u", ""))


@app.route("/api/usuarios/<int:uid>", methods=["DELETE"])
def delete_user(uid):
    _, error = _authenticate(REQUIRED_LEVEL_TO_DELETE)
    if error is not None:
        return error

    affected = run_write("DELETE FROM usuarios_ex10 WHERE id = %s", (uid,))
    if affected == 0:
        return json_error("usuário não encontrado", 404)
    return jsonify({"removido": uid})


@app.route("/api/relatorio")
def report():
    # A falha original (consultar uma tabela inexistente) é mantida de
    # propósito para provar a defesa: o erro ainda acontece, mas o
    # register_error_handlers global garante que só "erro interno" sai
    # daqui, nunca o traceback ou o nome da tabela.
    run_query("SELECT * FROM tabela_inexistente")
    return jsonify([])


if __name__ == "__main__":
    setup_mysql()
    app.run(port=5000)
