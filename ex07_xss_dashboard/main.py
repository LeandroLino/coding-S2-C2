"""
Exercise 7 — XSS where nobody looks: inside the attribute (Aulas 6, 7
e 8/A05).

`/dashboard` renders incidents from MongoDB through Jinja2's default
auto-escaping, which protects both HTML text content and the `alt`
attribute value. `/dashboard-inseguro` disables that escaping with
`|safe` to show, side by side, what breaks: a `<script>` tag renders as
a literal string on the safe page but executes as markup on the
insecure one, and a value that tries to break out of the `alt`
attribute (`x" onerror="..."`) stays inert as text on the safe page but
escapes the attribute on the insecure one.

A single misplaced `|safe` on trusted-looking data is enough to
reopen this hole — auto-escaping only protects what it is never told
to skip.

The shared `create_app()` factory already sets
`Content-Security-Policy: default-src 'self'` on every response
(providers/security_headers.py), so no extra header wiring is needed
here.
"""
from flask import render_template

from diplomat.mongo import get_mongo_db
from ex07_xss_dashboard.setup_mongo import setup_mongo
from providers.app_factory import create_app

app = create_app(__name__)


def _load_incidentes() -> list[dict]:
    return list(get_mongo_db().incidentes.find({}, {"_id": 0}))


@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html", incidentes=_load_incidentes())


@app.route("/dashboard-inseguro")
def dashboard_inseguro():
    return render_template("dashboard_insecure.html", incidentes=_load_incidentes())


if __name__ == "__main__":
    setup_mongo()
    app.run(port=5000)
