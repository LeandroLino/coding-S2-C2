"""
Smoke test for exercise 9 — reproduces the assignment's traffic script:
a normal IP with spaced valid requests, a hostile IP bursting requests
(many to nonexistent routes), then triggers the anomaly analysis and
confirms the hostile IP gets rate-limited afterwards.
"""
import time

import requests

BASE_URL = "http://127.0.0.1:5000"
NORMAL_IP = "192.168.1.10"
HOSTILE_IP = "185.220.101.1"


def check(label: str, condition: bool) -> None:
    print(f"[{'PASS' if condition else 'FAIL'}] {label}")


def generate_traffic() -> None:
    for _ in range(5):
        requests.get(f"{BASE_URL}/api/ping", headers={"X-Forwarded-For": NORMAL_IP})
        time.sleep(0.2)

    for i in range(60):
        path = f"/api/rota-inexistente-{i}" if i < 40 else "/api/ping"
        requests.get(f"{BASE_URL}{path}", headers={"X-Forwarded-For": HOSTILE_IP})


def main() -> None:
    normal_ping = requests.get(f"{BASE_URL}/api/ping", headers={"X-Forwarded-For": NORMAL_IP})
    check("normal IP request -> 200", normal_ping.status_code == 200)

    generate_traffic()

    analysis = requests.post(f"{BASE_URL}/api/seguranca/analisar")
    check("analysis endpoint -> 200", analysis.status_code == 200)
    results = {row["ip"]: row for row in analysis.json()}

    check("normal IP flagged as normal", results.get(NORMAL_IP, {}).get("resultado") == "normal")
    check("hostile IP flagged as anomalia", results.get(HOSTILE_IP, {}).get("resultado") == "anomalia")

    blocked = requests.get(f"{BASE_URL}/api/ping", headers={"X-Forwarded-For": HOSTILE_IP})
    check(
        "hostile IP now gets 429 with exact message",
        blocked.status_code == 429 and blocked.json().get("erro") == "muitas requisições",
    )
    check("blocked response has Retry-After: 60", blocked.headers.get("Retry-After") == "60")

    still_ok = requests.get(f"{BASE_URL}/api/ping", headers={"X-Forwarded-For": NORMAL_IP})
    check("normal IP still allowed after blocking", still_ok.status_code == 200)


if __name__ == "__main__":
    main()
