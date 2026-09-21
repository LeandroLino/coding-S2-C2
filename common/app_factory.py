"""
Flask application factory shared by every exercise (5 onward).

Every exercise app should be created through `create_app()` instead of
instantiating `Flask(__name__)` directly, so security headers and safe
error handling are applied consistently everywhere.
"""
from flask import Flask

from common.errors import register_error_handlers
from common.security_headers import apply_security_headers


def create_app(import_name: str) -> Flask:
    """Create a Flask app with shared security headers and error handlers."""
    app = Flask(import_name)
    apply_security_headers(app)
    register_error_handlers(app)
    return app
