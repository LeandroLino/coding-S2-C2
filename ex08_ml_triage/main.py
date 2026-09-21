"""
Exercise 8 — ML model served through an API, with auditable metrics
(Aulas 2, 4, 6 e 7).

The core lesson: model input is user input too. Every field on
`POST /api/triagem` is validated the same way any other API input
would be, before it ever reaches the classifier.

Every valid prediction (never the rejected/invalid ones) is logged to
MongoDB's `previsoes` collection with the input, the output, the
confidence and a timestamp, so the model's behavior can be audited
later (A08/A09).
"""
from datetime import datetime, timezone

from flask import jsonify, request

from diplomat.mongo import get_mongo_db
from ex08_ml_triage.model import RiskTriageModel
from ex08_ml_triage.setup_mongo import setup_mongo
from providers.app_factory import create_app
from providers.errors import json_error

FEATURE_COUNT = 4

app = create_app(__name__)
model = RiskTriageModel()


def _validate_features(payload) -> list[float]:
    """Validate the `features` field, raising ValueError with the exact
    contract message for each rejection case."""
    if not isinstance(payload, dict) or "features" not in payload:
        raise ValueError("corpo da requisição ausente ou inválido")

    features = payload["features"]
    if not isinstance(features, list):
        raise ValueError("features devem ser numéricas")
    if len(features) != FEATURE_COUNT:
        raise ValueError(f"esperadas {FEATURE_COUNT} features, recebidas {len(features)}")

    parsed = []
    for value in features:
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError("features devem ser numéricas")
        parsed.append(float(value))
    return parsed


def _record_prediction(features: list[float], risco: str, confianca: float) -> None:
    get_mongo_db().previsoes.insert_one(
        {
            "entrada": features,
            "saida": risco,
            "confianca": confianca,
            "timestamp": datetime.now(timezone.utc),
        }
    )


@app.route("/api/triagem", methods=["POST"])
def triagem():
    payload = request.get_json(silent=True)
    try:
        features = _validate_features(payload)
    except ValueError as exc:
        return json_error(str(exc), 400)

    risco, confianca = model.predict(features)
    _record_prediction(features, risco, confianca)
    return jsonify({"risco": risco, "confianca": confianca})


@app.route("/api/modelo/metricas", methods=["GET"])
def modelo_metricas():
    metrics = model.metrics
    return jsonify(
        {
            "precisao": metrics.precisao,
            "recall": metrics.recall,
            "f1": metrics.f1,
            "matriz": metrics.matriz,
            "aviso": (
                "acuracia foi omitida de proposito: classes de risco tendem a ser "
                "desbalanceadas (poucos casos de alto risco no dia a dia), e uma "
                "acuracia alta pode esconder um modelo que erra justamente as "
                "sessoes de alto risco — por isso reportamos precisao/recall/F1."
            ),
        }
    )


if __name__ == "__main__":
    setup_mongo()
    app.run(port=5000)
