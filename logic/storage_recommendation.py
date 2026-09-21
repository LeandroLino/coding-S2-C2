"""
Exercise 1 — storage decision assistant engine (Aulas 1 e 8).

Generic matching machinery only: the profile model, the rule shape, and
the `recommend()`/`recomendar()` entry point that runs an ordered rule
table. The actual rules -- including the catch-all default -- live in
`ex01_recommendation/rules.py`, since they are this exercise's decision
data, not generic engine logic. The default is just another `Rule` whose
`matches` always returns True, so there is no separate "fallback" concept.
"""
from dataclasses import dataclass
from typing import Callable


@dataclass(frozen=True)
class Profile:
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


@dataclass(frozen=True)
class Rule:
    """A named decision: `matches` decides if it applies to a profile; the
    remaining fields compute each output value from that same profile."""
    name: str
    matches: Callable[[Profile], bool]
    database: Callable[[Profile], str]
    cap: Callable[[Profile], str]
    justification: Callable[[Profile], str]
    owasp_risk: Callable[[Profile], str]


def const(value: str) -> Callable[[Profile], str]:
    """Wrap a fixed value as a Profile -> value function, for rules whose
    outcome does not depend on which flags triggered the match."""
    return lambda _p: value


def recommend(profile: dict) -> dict:
    """Recommend a database, CAP priority and OWASP risk for `profile`."""
    # Local import: rules.py imports Profile/Rule from this module, so
    # importing RULES at module level here would create a circular import.
    from ex01_recommendation.rules import RULES

    p = Profile.from_dict(profile)
    rule = next(r for r in RULES if r.matches(p))  # RULES always ends in a catch-all
    return {
        "banco": rule.database(p),
        "cap": rule.cap(p),
        "justificativa": rule.justification(p),
        "risco_owasp": rule.owasp_risk(p),
    }


# Alias matching the exact function name/signature requested by the exercise.
recomendar = recommend
