"""
Smoke test for exercise 8 — reproduces the assignment's exact test
sequence against a running server.
"""
import requests

BASE_URL = "http://127.0.0.1:5000"


def check(label: str, condition: bool) -> None:
    print(f"[{'PASS' if condition else 'FAIL'}] {label}")


def main() -> None:
    alto = requests.post(f"{BASE_URL}/api/triagem", json={"features": [12, 7, 90000, 3]})
    check("high-risk features -> 200 risco=alto", alto.status_code == 200 and alto.json().get("risco") == "alto")
    check("high-risk confidence >= 0.9", alto.json().get("confianca", 0) >= 0.9)

    baixo = requests.post(f"{BASE_URL}/api/triagem", json={"features": [0, 1, 1200, 14]})
    check("low-risk features -> 200 risco=baixo", baixo.status_code == 200 and baixo.json().get("risco") == "baixo")
    check("low-risk confidence >= 0.9", baixo.json().get("confianca", 0) >= 0.9)

    wrong_count = requests.post(f"{BASE_URL}/api/triagem", json={"features": [12, 7, 90000]})
    check(
        "wrong feature count -> 400 with exact message",
        wrong_count.status_code == 400
        and wrong_count.json().get("erro") == "esperadas 4 features, recebidas 3",
    )

    non_numeric = requests.post(f"{BASE_URL}/api/triagem", json={"features": ["12", "sete", 0, 3]})
    check(
        "non-numeric features -> 400 with exact message",
        non_numeric.status_code == 400
        and non_numeric.json().get("erro") == "features devem ser numéricas",
    )

    no_body = requests.post(f"{BASE_URL}/api/triagem")
    check("missing body -> 400", no_body.status_code == 400)

    metricas = requests.get(f"{BASE_URL}/api/modelo/metricas")
    body = metricas.json()
    check("metrics -> 200 with all expected keys", metricas.status_code == 200)
    check(
        "metrics have precisao/recall/f1/matriz/aviso, no acuracia",
        {"precisao", "recall", "f1", "matriz", "aviso"} <= body.keys() and "acuracia" not in body,
    )


if __name__ == "__main__":
    main()
