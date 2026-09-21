"""
Shared JSON error handling for every Flask app in this project.

Centralizing this addresses exercise 10's requirement that a 500 response
must never leak internal details (traceback, table names, etc.) — only a
generic message. Individual routes can still raise their own specific
`json_error(...)` (e.g. "campo de ordenacao invalido") when the exercise
spec requires a precise message; these handlers are just the fallback for
uncaught cases and framework-level aborts (404 on unknown routes, etc.).
"""
from flask import Flask, jsonify
from werkzeug.exceptions import HTTPException


def json_error(message: str, status_code: int):
    """Build a standard {"erro": message} JSON response with the given status."""
    response = jsonify({"erro": message})
    response.status_code = status_code
    return response


_DEFAULT_MESSAGES = {
    400: "invalid request",
    401: "unauthorized",
    403: "forbidden",
    404: "not found",
    429: "too many requests",
}


def register_error_handlers(app: Flask) -> None:
    """Register fallback error handlers that never leak internal details."""

    @app.errorhandler(HTTPException)
    def _handle_http_exception(exc: HTTPException):
        message = _DEFAULT_MESSAGES.get(exc.code, exc.name.lower())
        return json_error(message, exc.code or 500)

    @app.errorhandler(Exception)
    def _handle_unexpected_exception(exc: Exception):
        # Log server-side for later auditing (A09), but never expose `exc`
        # details (message, traceback, table/column names) to the client.
        app.logger.exception("Unhandled exception")
        return json_error("erro interno", 500)
