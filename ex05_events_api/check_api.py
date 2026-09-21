"""
Exercise 5 manual check — fires the assignment's 4 required requests
against a locally running server and reports PASS/FAIL for each.

Usage:
    1. In one terminal: python -m ex05_events_api.main
    2. In another:       python -m ex05_events_api.check_api
"""
import requests

BASE_URL = "http://127.0.0.1:5000"

CASES = [
    {
        "description": "valid sort by severity, size=5",
        "params": {"ordenar_por": "sev", "ordem": "desc", "tamanho": 5},
        "expected_status": 200,
    },
    {
        "description": "column injection attempt is rejected",
        "params": {"ordenar_por": "criado_em,(SELECT 1)", "ordem": "asc"},
        "expected_status": 400,
        "expected_body": {"erro": "campo de ordenação inválido"},
    },
    {
        "description": "non-integer size is rejected",
        "params": {"tamanho": "abc"},
        "expected_status": 400,
        "expected_body": {"erro": "tamanho deve ser inteiro"},
    },
    {
        "description": "oversized request is capped at 100 by the server",
        "params": {"tamanho": 100000},
        "expected_status": 200,
        "expected_max_events": 100,
    },
]


def run_checks() -> None:
    for case in CASES:
        response = requests.get(f"{BASE_URL}/api/eventos", params=case["params"], timeout=5)
        ok = response.status_code == case["expected_status"]

        if ok and "expected_body" in case:
            ok = response.json() == case["expected_body"]
        if ok and "expected_max_events" in case:
            ok = len(response.json().get("events", [])) <= case["expected_max_events"]

        status = "PASS" if ok else "FAIL"
        print(f"[{status}] {case['description']} -> {response.status_code} {response.text}")


if __name__ == "__main__":
    run_checks()
