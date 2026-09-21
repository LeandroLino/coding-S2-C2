"""
Reusable input validators.

Centralizing "identifier vs data" validation here (exercise 5's core lesson):
placeholders (%s) parametrize *data*, never identifiers like column names.
Column/order names must always go through an explicit whitelist.
"""
from typing import Any


def validate_whitelisted_value(value: str, allowed: dict[str, str]) -> str:
    """Return the mapped safe value for `value`, or raise ValueError if not allowed."""
    if value not in allowed:
        raise ValueError(f"invalid value: {value!r}")
    return allowed[value]


def validate_positive_int(value: Any, *, max_value: int | None = None) -> int:
    """Parse `value` as a positive int, optionally capped at `max_value`."""
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        raise ValueError("value must be an integer")
    if parsed <= 0:
        raise ValueError("value must be positive")
    if max_value is not None:
        parsed = min(parsed, max_value)
    return parsed


def validate_numeric_features(features: Any, expected_length: int) -> list[float]:
    """Validate a list of numeric features for ML model input (exercise 8)."""
    if not isinstance(features, list):
        raise ValueError("features must be a list")
    if len(features) != expected_length:
        raise ValueError(f"expected {expected_length} features, got {len(features)}")
    result = []
    for f in features:
        if isinstance(f, bool) or not isinstance(f, (int, float)):
            raise ValueError("features must be numeric")
        result.append(float(f))
    return result
