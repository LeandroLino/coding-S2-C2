"""
app_vulneravel.py — laboratório apenas. NUNCA use este padrão em produção.

Reproduz o esqueleto do enunciado (Exercício 10) com as mesmas 6 rotas e
falhas, rodando contra o `usuarios_ex10` do próprio mysql-lab do projeto.
"""
from flask import Flask, request, jsonify

from diplomat.mysql import get_mysql_connection
from ex10_before_after.setup_mysql import setup_mysql

# [FALHA 7 - A07, hardcoded credential] Segredo commitado no código-fonte,
# nunca lido de variável de ambiente. Nem precisa estar "certo" para ser
# uma falha: um segredo em texto puro no repositório já vaza no git log,
# em qualquer fork, e para qualquer um com acesso de leitura ao código.
SENHA_MESTRA = "Cyber@2024"

app = Flask(__name__)
# [FALHA 6 - A05, ausência] Nenhum header de segurança é definido em
# lugar nenhum (sem CSP, sem X-Content-Type-Options, sem X-Frame-Options).


def db():
    return get_mysql_connection()


@app.route("/api/usuarios/buscar")
def buscar():
    nome = request.args.get("nome", "")
    con = db()
    cur = con.cursor(dictionary=True)
    # [FALHA 1 - A03, SQL Injection] nome concatenado direto na query.
    cur.execute(f"SELECT * FROM usuarios_ex10 WHERE nome LIKE '%{nome}%'")
    # [FALHA 5 - A02, exposição de dado sensível] `SELECT *` devolve a
    # coluna `senha` (em texto puro) para quem quer que seja.
    return jsonify(cur.fetchall())


@app.route("/perfil")
def perfil():
    # [FALHA 2 - A03, XSS refletido] valor do usuário interpolado direto
    # no HTML, sem nenhum escaping.
    return f"<h1>Bem-vindo, {request.args.get('u', '')}</h1>"


@app.route("/api/usuarios/<int:uid>", methods=["DELETE"])
def remover(uid):
    # [FALHA 3 - A01, ausência] nenhuma verificação de autenticação ou
    # autorização antes de apagar o registro.
    con = db()
    cur = con.cursor()
    cur.execute("DELETE FROM usuarios_ex10 WHERE id = %s", (uid,))
    con.commit()
    return jsonify({"removido": uid})


@app.route("/api/relatorio")
def relatorio():
    # [FALHA 4 - A05, misconfiguration] erro de banco não tratado; com
    # debug=True o Werkzeug devolve o traceback completo (nome de tabela
    # incluso) direto na resposta HTTP.
    con = db()
    cur = con.cursor()
    cur.execute("SELECT * FROM tabela_inexistente")
    return jsonify(cur.fetchall())


# [FALHA 8 - A09, ausência] nenhuma linha deste arquivo grava log de
# requisição, tentativa de acesso ou auditoria — um ataque bem-sucedido
# aqui não deixa rastro nenhum para ser investigado depois.

if __name__ == "__main__":
    setup_mysql()
    app.run(debug=True, host="0.0.0.0")
