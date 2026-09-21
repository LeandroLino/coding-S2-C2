# CP2 — Coding for Security (Cumulative, 2nd Semester)

Shared project structure for the 10 exercises (SQL/NoSQL, MongoDB, MySQL,
Machine Learning, Flask APIs, OWASP Top 10 defenses).

## Structure

- `config.py` — reads credentials/settings from environment variables (`.env`).
- `diplomat/mysql.py` — shared MySQL connection helper.
- `diplomat/mongo.py` — shared MongoDB connection helper.
- `adapters/validators.py` — whitelist and input validation helpers.
- `common/security_headers.py` — CSP/security headers applied to every Flask app.
- `common/errors.py` — standard `{"erro": ...}` JSON error responses; never leaks internal details on 500.
- `common/app_factory.py` — `create_app()` factory wiring security headers + error handlers for every exercise app.
- `logic/auth.py` — shared X-API-Key authentication logic (MySQL-backed).
- `seed/` — scripts to populate MySQL/MongoDB with sample data.
- `ex01_recommendation/` ... `ex10_challenge/` — one folder per exercise.

## Setup

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env   # then fill in real credentials
```

Requires `mongo-lab` and `mysql-lab` Docker containers running (see course
lab environment guide). Credentials must never be hardcoded in source files.
