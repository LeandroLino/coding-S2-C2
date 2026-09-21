"""
Exercise 1 — storage decision assistant engine (Aulas 1 e 8).

Generic machinery only: the `Profile` value object and the
`recommend()`/`recomendar()` entry point that runs an ordered table of
rules. The rules themselves (including the catch-all default) are plain
dicts living in `ex01_recommendation/rules.py`, not a custom class
hierarchy — each rule has a `matches` predicate and four output fields
that are either a fixed string or a `profile -> str` function, resolved
lazily by `_resolve()`. Most rules only need fixed strings; only the
default rule needs to compute its outputs from the profile.
"""
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class Profile:
    """Normalized dataset profile (booleans only, English field names)."""
    fixed_schema: bool
    needs_acid: bool
    horizontal_scale: bool
    tolerates_consistency_delay: bool
    sensitive_data: bool

    @classmethod
    def from_dict(cls, data: dict) -> "Profile":
        return cls(
            fixed_schema=bool(data["schema_fixo"]),
            needs_acid=bool(data["precisa_acid"]),
            horizontal_scale=bool(data["escala_horizontal"]),
            tolerates_consistency_delay=bool(data["tolera_atraso_de_consistencia"]),
            sensitive_data=bool(data["dado_sensivel"]),
        )


def _resolve(value: Any, profile: Profile) -> str:
    """A rule's output field is either a fixed string or a function that
    computes it from the profile (used only by the default rule)."""
    return value(profile) if callable(value) else value


def recommend(profile: dict) -> dict:
    """Recommend a database, CAP priority and OWASP risk for `profile`."""
    # Local import: rules.py needs Profile from this module, so importing
    # RULES at module level here would create a circular import.
    from ex01_recommendation.rules import RULES

    p = Profile.from_dict(profile)
    rule = next(r for r in RULES if r["matches"](p))  # RULES always ends in a catch-all
    return {
        "banco": _resolve(rule["banco"], p),
        "cap": _resolve(rule["cap"], p),
        "justificativa": _resolve(rule["justificativa"], p),
        "risco_owasp": _resolve(rule["risco_owasp"], p),
    }


# Alias matching the exact function name/signature requested by the exercise.
recomendar = recommend
