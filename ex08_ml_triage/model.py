"""
Risk-triage model for exercise 8.

The model is trained once, from a synthetic dataset built with a fixed
seed (reproducibility), against a labeling rule that mimics a simple
SOC heuristic: many failed logins, many distinct ports touched, a lot
of outbound bytes, and activity in the middle of the night all push a
session towards "alto" risk. A small amount of label noise is added so
the classifier — and its metrics — aren't trivially perfect.

Features, in this fixed order: [falhas_login, portas_distintas,
bytes_saida, hora_do_dia].
"""
from dataclasses import dataclass

import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import confusion_matrix, f1_score, precision_score, recall_score
from sklearn.model_selection import train_test_split

RANDOM_STATE = 42
N_SAMPLES = 2000
RISK_LABELS = {0: "baixo", 1: "alto"}


def _risk_score(falhas_login: float, portas_distintas: float, bytes_saida: float, hora_do_dia: float) -> float:
    """Heuristic used only to label synthetic training data."""
    score = falhas_login * 3 + portas_distintas * 2 + bytes_saida / 2000
    if hora_do_dia < 6:
        score += 10
    return score


def _build_training_data() -> tuple[np.ndarray, np.ndarray]:
    rng = np.random.default_rng(RANDOM_STATE)
    falhas_login = rng.integers(0, 20, N_SAMPLES)
    portas_distintas = rng.integers(0, 15, N_SAMPLES)
    bytes_saida = rng.integers(100, 100_000, N_SAMPLES)
    hora_do_dia = rng.integers(0, 24, N_SAMPLES)

    features = np.column_stack([falhas_login, portas_distintas, bytes_saida, hora_do_dia]).astype(float)
    scores = np.array(
        [_risk_score(*row) for row in features]
    )
    labels = (scores > 60).astype(int)

    # Flip a small share of labels so the model faces some ambiguity,
    # instead of learning a perfectly separable rule.
    noise_mask = rng.random(N_SAMPLES) < 0.05
    labels[noise_mask] = 1 - labels[noise_mask]

    return features, labels


@dataclass
class ModelMetrics:
    precisao: float
    recall: float
    f1: float
    matriz: list[list[int]]


class RiskTriageModel:
    """Wraps a trained classifier plus its held-out evaluation metrics."""

    def __init__(self) -> None:
        features, labels = _build_training_data()
        x_train, x_test, y_train, y_test = train_test_split(
            features, labels, test_size=0.2, random_state=RANDOM_STATE, stratify=labels
        )

        self._classifier = RandomForestClassifier(n_estimators=200, random_state=RANDOM_STATE)
        self._classifier.fit(x_train, y_train)

        y_pred = self._classifier.predict(x_test)
        self._metrics = ModelMetrics(
            precisao=round(float(precision_score(y_test, y_pred)), 2),
            recall=round(float(recall_score(y_test, y_pred)), 2),
            f1=round(float(f1_score(y_test, y_pred)), 2),
            matriz=confusion_matrix(y_test, y_pred, labels=[0, 1]).tolist(),
        )

    def predict(self, features: list[float]) -> tuple[str, float]:
        """Return (risco, confianca) for one feature vector."""
        row = np.array(features).reshape(1, -1)
        predicted_class = int(self._classifier.predict(row)[0])
        confidence = float(self._classifier.predict_proba(row)[0][predicted_class])
        return RISK_LABELS[predicted_class], round(confidence, 2)

    @property
    def metrics(self) -> ModelMetrics:
        return self._metrics
