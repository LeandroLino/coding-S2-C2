"""
Exercise 1 — rule table for the storage decision assistant.

Each rule is a plain dict: a `matches` predicate plus four output fields
(`banco`, `cap`, `justificativa`, `risco_owasp`). Fields are fixed strings
for the five named scenarios, and small functions for the catch-all
`default` rule at the end, whose outcome depends on which flags are set.
The first matching rule wins.
"""
from ex01_recommendation.storage_recommendation import Profile


def _cannot_tolerate_stale_reads(p: Profile) -> bool:
    """If the data is not allowed to lag behind reality, consistency must
    win over availability, regardless of which engine stores it."""
    return p.needs_acid or not p.tolerates_consistency_delay


def _default_banco(p: Profile) -> str:
    # Fixed schema + ACID needs -> joins/constraints matter more than raw
    # write throughput, so a relational engine fits better.
    needs_relational_integrity = p.fixed_schema and p.needs_acid
    return "MySQL" if needs_relational_integrity else "MongoDB"


def _default_cap(p: Profile) -> str:
    return "CP" if _cannot_tolerate_stale_reads(p) else "AP"


# Justification/OWASP text keyed by the same boolean decision used to pick
# CAP, so the default rule stays a lookup instead of an ad-hoc if/else chain.
_DEFAULT_TEXT_BY_CAP_DECISION = {
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


def _default_justificativa(p: Profile) -> str:
    return _DEFAULT_TEXT_BY_CAP_DECISION[_cannot_tolerate_stale_reads(p)][0]


def _default_risco_owasp(p: Profile) -> str:
    if p.sensitive_data:
        return "A02"  # Cryptographic Failures: sensitive data mishandled
    return _DEFAULT_TEXT_BY_CAP_DECISION[_cannot_tolerate_stale_reads(p)][1]


RULES: list[dict] = [
    {
        "name": "access_control_credentials",
        "matches": lambda p: (
            p.sensitive_data and p.needs_acid and not p.tolerates_consistency_delay
        ),
        "banco": "MySQL",
        "cap": "CP",
        "justificativa": (
            "authenticating with a stale or half-written credential is worse "
            "than the service being briefly unavailable"
        ),
        "risco_owasp": "A07",  # Identification and Authentication Failures
    },
    {
        "name": "audit_trail",
        "matches": lambda p: (
            p.sensitive_data and not p.needs_acid and not p.tolerates_consistency_delay
        ),
        "banco": "MongoDB",
        "cap": "CP",
        "justificativa": (
            "an audit record that disagrees with what actually happened is "
            "worthless as evidence, even if it was written fast"
        ),
        "risco_owasp": "A08",  # Software and Data Integrity Failures
    },
    {
        "name": "high_volume_telemetry",
        "matches": lambda p: (
            not p.sensitive_data and p.tolerates_consistency_delay and p.horizontal_scale
        ),
        "banco": "MongoDB",
        "cap": "AP",
        "justificativa": (
            "losing a second of freshness in a metric is acceptable; "
            "refusing new telemetry over a consistency check is not"
        ),
        "risco_owasp": "A09",  # Security Logging and Monitoring Failures
    },
    {
        "name": "license_inventory",
        "matches": lambda p: (
            p.needs_acid
            and p.fixed_schema
            and not p.tolerates_consistency_delay
            and not p.sensitive_data
        ),
        "banco": "MySQL",
        "cap": "CP",
        "justificativa": (
            "selling the same license twice because two writes raced each "
            "other is unacceptable, even if it means rejecting a purchase"
        ),
        "risco_owasp": "A08",  # Software and Data Integrity Failures
    },
    {
        "name": "session_cache",
        "matches": lambda p: (
            p.sensitive_data
            and not p.needs_acid
            and p.tolerates_consistency_delay
            and p.horizontal_scale
        ),
        "banco": "MongoDB",
        "cap": "AP",
        "justificativa": (
            "a session cache that is briefly stale is fine; a login page "
            "going down because one node is desynced is not"
        ),
        "risco_owasp": "A07",  # Identification and Authentication Failures
    },
    {
        "name": "default",
        "matches": lambda _p: True,
        "banco": _default_banco,
        "cap": _default_cap,
        "justificativa": _default_justificativa,
        "risco_owasp": _default_risco_owasp,
    },
]
