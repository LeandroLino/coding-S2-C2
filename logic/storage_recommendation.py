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


# Ordered, named rules covering the scenarios described in the exercise.
# The first matching rule wins; unmatched profiles fall back to
# `_default_recommendation`, which derives the same decision compositionally.
RULES: list[Rule] = [
    Rule(
        name="access_control_credentials",
        matches=lambda p: (
            p.sensitive_data and p.needs_acid and not p.tolerates_consistency_delay
        ),
        database="MySQL",
        cap="CP",
        justification=(
            "authenticating with a stale or half-written credential is worse "
            "than the service being briefly unavailable"
        ),
        owasp_risk="A07",  # Identification and Authentication Failures
    ),
    Rule(
        name="audit_trail",
        matches=lambda p: (
            p.sensitive_data and not p.needs_acid and not p.tolerates_consistency_delay
        ),
        database="MongoDB",
        cap="CP",
        justification=(
            "an audit record that disagrees with what actually happened is "
            "worthless as evidence, even if it was written fast"
        ),
        owasp_risk="A08",  # Software and Data Integrity Failures
    ),
    Rule(
        name="high_volume_telemetry",
        matches=lambda p: (
            not p.sensitive_data and p.tolerates_consistency_delay and p.horizontal_scale
        ),
        database="MongoDB",
        cap="AP",
        justification=(
            "losing a second of freshness in a metric is acceptable; "
            "refusing new telemetry over a consistency check is not"
        ),
        owasp_risk="A09",  # Security Logging and Monitoring Failures
    ),
    Rule(
        name="license_inventory",
        matches=lambda p: (
            p.needs_acid
            and p.fixed_schema
            and not p.tolerates_consistency_delay
            and not p.sensitive_data
        ),
        database="MySQL",
        cap="CP",
        justification=(
            "selling the same license twice because two writes raced each "
            "other is unacceptable, even if it means rejecting a purchase"
        ),
        owasp_risk="A08",  # Software and Data Integrity Failures
    ),
    Rule(
        name="session_cache",
        matches=lambda p: (
            p.sensitive_data
            and not p.needs_acid
            and p.tolerates_consistency_delay
            and p.horizontal_scale
        ),
        database="MongoDB",
        cap="AP",
        justification=(
            "a session cache that is briefly stale is fine; a login page "
            "going down because one node is desynced is not"
        ),
        owasp_risk="A07",  # Identification and Authentication Failures
    ),
]

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
