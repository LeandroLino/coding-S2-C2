"""
Security headers shared by every Flask app in this project (exercises 5-10).

Applying these consistently addresses OWASP A05 (Security Misconfiguration)
and reduces the blast radius of XSS/clickjacking even if a template mistake
slips through.
"""
from flask import Flask, Response


SECURITY_HEADERS = {
    "Content-Security-Policy": "default-src 'self'",
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
}


def apply_security_headers(app: Flask) -> None:
    """Register an after_request hook that adds standard security headers."""

    @app.after_request
    def _add_security_headers(response: Response) -> Response:
        for header, value in SECURITY_HEADERS.items():
            response.headers.setdefault(header, value)
        return response
