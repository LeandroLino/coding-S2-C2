"""
Exercise 1 demo — prints the recommendation for each sample profile from
the assignment, in the same layout as the expected output.
"""
from logic.storage_recommendation import recomendar

PERFIS = {
    "credenciais_do_SOC": {
        "schema_fixo": True,
        "precisa_acid": True,
        "escala_horizontal": False,
        "tolera_atraso_de_consistencia": False,
        "dado_sensivel": True,
    },
    "telemetria_de_sensores": {
        "schema_fixo": False,
        "precisa_acid": False,
        "escala_horizontal": True,
        "tolera_atraso_de_consistencia": True,
        "dado_sensivel": False,
    },
    "trilha_de_auditoria": {
        "schema_fixo": False,
        "precisa_acid": False,
        "escala_horizontal": True,
        "tolera_atraso_de_consistencia": False,
        "dado_sensivel": True,
    },
    "carrinho_de_licencas": {
        "schema_fixo": True,
        "precisa_acid": True,
        "escala_horizontal": False,
        "tolera_atraso_de_consistencia": False,
        "dado_sensivel": False,
    },
    "cache_de_sessoes": {
        "schema_fixo": True,
        "precisa_acid": False,
        "escala_horizontal": True,
        "tolera_atraso_de_consistencia": True,
        "dado_sensivel": True,
    },
}


def main() -> None:
    for name, profile in PERFIS.items():
        result = recomendar(profile)
        print(
            f"{name:<24} -> {result['banco']:<7} | {result['cap']} | "
            f"\"{result['justificativa']}\" | {result['risco_owasp']}"
        )


if __name__ == "__main__":
    main()
