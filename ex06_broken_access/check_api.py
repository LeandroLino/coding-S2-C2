"""
Exercise 6 manual check — fires the assignment's 8 required requests
against a locally running server and reports PASS/FAIL for each.

Usage:
    1. In one terminal: python -m ex06_broken_access.main
    2. In another:       python -m ex06_broken_access.check_api

Note: this deletes incident 2 as part of the test (case 6). Restart the
server (step 1) before re-running the checks, since main.py reseeds
analistas/incidentes from scratch on every startup.
"""
import requests

BASE_URL = "http://127.0.0.1:5000"

CASES = [
    {
        "description": "owner reads their own incident",
        "method": "GET",
        "path": "/api/incidentes/1",
        "headers": {"X-API-Key": "key-ana-001"},
        "expected_status": 200,
    },
    {
        "description": "IDOR blocked: non-owner reads someone else's incident",
        "method": "GET",
        "path": "/api/incidentes/1",
        "headers": {"X-API-Key": "key-bruno-002"},
        "expected_status": 403,
    },
    {
        "description": "no X-API-Key header at all",
        "method": "GET",
        "path": "/api/incidentes/1",
        "headers": {},
        "expected_status": 401,
    },
    {
        "description": "unknown X-API-Key",
        "method": "GET",
        "path": "/api/incidentes/1",
        "headers": {"X-API-Key": "key-inexistente"},
        "expected_status": 401,
    },
    {
        "description": "list is scoped to the caller (only their own incidents)",
        "method": "GET",
        "path": "/api/incidentes",
        "headers": {"X-API-Key": "key-bruno-002"},
        "expected_status": 200,
    },
    {
        "description": "level 5 can delete an incident they don't own",
        "method": "DELETE",
        "path": "/api/incidentes/2",
        "headers": {"X-API-Key": "key-ana-001"},
        "expected_status": 200,
    },
    {
        "description": "level below 5 cannot delete, even their own",
        "method": "DELETE",
        "path": "/api/incidentes/1",
        "headers": {"X-API-Key": "key-bruno-002"},
        "expected_status": 403,
    },
    {
        "description": "non-existent incident",
        "method": "GET",
        "path": "/api/incidentes/999",
        "headers": {"X-API-Key": "key-ana-001"},
        "expected_status": 404,
    },
]


def run_checks() -> None:
    for case in CASES:
        response = requests.request(
            case["method"], f"{BASE_URL}{case['path']}", headers=case["headers"], timeout=5
        )
        ok = response.status_code == case["expected_status"]
        status = "PASS" if ok else "FAIL"
        print(f"[{status}] {case['description']} -> {response.status_code} {response.text}")


if __name__ == "__main__":
    run_checks()
