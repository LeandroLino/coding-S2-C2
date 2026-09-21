# Auditoria — Exercício 10 (Antes e depois)

Uma linha por falha encontrada em `app_vulneravel.py`. As duas marcadas
como **(ausência)** não estão escritas em nenhum lugar do arquivo — a
falha é exatamente essa omissão.

| # | OWASP 2025 | Falha | Impacto | Correção aplicada em `app_seguro.py` |
|---|------------|-------|---------|----------------------------------------|
| 1 | A03 — Injection | `nome` concatenado direto na query `LIKE` de `/api/usuarios/buscar` | Qualquer atacante lê a tabela inteira (`' OR '1'='1`) ou executa SQL arbitrário | Query parametrizada (`%s`), nunca concatenação de string |
| 2 | A03 — Injection (XSS) | Valor de `u` interpolado sem escaping em `/perfil` | Script arbitrário roda no navegador de quem clicar no link | Template Jinja2 (`render_template`) com auto-escape padrão |
| 3 | A01 — Broken Access Control **(ausência)** | Nenhuma verificação de autenticação/autorização antes de `DELETE /api/usuarios/<id>` | Qualquer pessoa sem credencial apaga qualquer registro | Exige `X-API-Key`; 401 sem credencial, 403 com nível < 5 |
| 4 | A05 — Security Misconfiguration | `debug=True` + erro de banco não tratado em `/api/relatorio` | Traceback completo e nome de tabela interna vazam na resposta HTTP | Erro capturado pelos error handlers globais; resposta genérica `{"erro":"erro interno"}`, `debug=False` |
| 5 | A02 — Cryptographic/Sensitive Data Exposure | `SELECT *` devolve a coluna `senha` em `/api/usuarios/buscar` | Senhas de todos os usuários expostas a qualquer requisição | `SELECT` explícito, sem a coluna `senha` |
| 6 | A05 — Security Misconfiguration **(ausência)** | Nenhum header de segurança definido em lugar nenhum (sem CSP, `X-Content-Type-Options`, `X-Frame-Options`) | Facilita XSS, clickjacking e MIME-sniffing em qualquer resposta | Headers aplicados globalmente via `create_app()`/`providers/security_headers.py` |
| 7 | A07 — Identification and Authentication Failures | `SENHA_MESTRA = "Cyber@2024"` commitada em texto puro no código-fonte | Segredo exposto para qualquer um com acesso de leitura ao repositório (git log, forks, etc.) | Nenhum segredo no código; toda credencial vem de variável de ambiente (`config.Config`) |
| 8 | A09 — Security Logging and Monitoring Failures **(ausência)** | Nenhuma linha do arquivo grava log de requisição ou tentativa de acesso | Um ataque bem-sucedido não deixa nenhum rastro para investigação | `before_request`/`after_request` logam rota, método, IP e status de toda requisição |
