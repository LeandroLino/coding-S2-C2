"""
Exercise 1 — Storage decision assistant (Aulas 1 e 8).

`recommend(profile)` — aliased as `recomendar` to match the exercise's
required function name — takes a dataset profile and returns a reasoned
recommendation: which database engine to use, which side of the CAP
theorem to prioritize, and which OWASP risk a wrong choice would create.

Implemented as an ordered rule table instead of scattered `if` statements:
each rule is a named, self-contained decision with its own justification,
so the reasoning is explicit and traceable to a single named cause.
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
    name: str
    matches: Callable[[Profile], bool]
    database: str
    cap: str
    justification: str
    owasp_risk: str


def _needs_relational_integrity(p: Profile) -> bool:
    """Fixed schema + ACID needs -> joins/constraints matter more than raw
    write throughput, so a relational engine fits better."""
    return p.fixed_schema and p.needs_acid


def _cannot_tolerate_stale_reads(p: Profile) -> bool:
    """If the data is not allowed to lag behind reality, consistency must
    win over availability, regardless of which engine stores it."""
    return p.needs_acid or not p.tolerates_consistency_delay


def _pick_database(p: Profile) -> str:
    return "MySQL" if _needs_relational_integrity(p) else "MongoDB"


def _pick_cap(p: Profile) -> str:
    return "CP" if _cannot_tolerate_stale_reads(p) else "AP"


# Fallback text keyed by the same boolean decision used to pick CAP, so the
# default path stays a lookup instead of an ad-hoc if/else chain.
_FALLBACK_BY_CAP_DECISION = {
    True: (
        "accepting a write that later needs a silent correction is "
        "unacceptable here; the system must reject it instead",
        "A08",  # Software and Data Integrity Failures
    ),
    False: (
        "rejecting a valid request just to keep every replica perfectly in "
        "sync is worse than a few seconds of staleness",
        "A09",  # Security Logging and Monitoring Failures
    ),
}


def _default_recommendation(p: Profile) -> Rule:
    """Fallback for any profile not covered by a named rule above: derive
    the recommendation compositionally from the same base decisions."""
    justification, owasp_risk = _FALLBACK_BY_CAP_DECISION[_cannot_tolerate_stale_reads(p)]
    owasp_risk = "A02" if p.sensitive_data else owasp_risk  # Cryptographic Failures
    return Rule(
        name="default",
        matches=lambda _: True,
        database=_pick_database(p),
        cap=_pick_cap(p),
        justification=justification,
        owasp_risk=owasp_risk,
    )


def recommend(profile: dict) -> dict:
    """Recommend a database, CAP priority and OWASP risk for `profile`."""
    # Local import: `rules.py` imports Profile/Rule from this module, so
    # importing RULES at module level here would create a circular import.
    from ex01_recommendation.rules import RULES

    p = Profile.from_dict(profile)
    rule = next((r for r in RULES if r.matches(p)), None) or _default_recommendation(p)
    return {
        "banco": rule.database,
        "cap": rule.cap,
        "justificativa": rule.justification,
        "risco_owasp": rule.owasp_risk,
    }


# Alias matching the exact function name/signature requested by the exercise.
recomendar = recommend
