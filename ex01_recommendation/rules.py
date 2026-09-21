"""
Exercise 1 — rule table for the storage decision assistant.

Each rule is a named, self-contained decision covering one scenario from
the assignment; the first matching rule wins. The last entry is a
catch-all default rule (`matches` always True), so the "what if nothing
named matches" case lives here as data, alongside the named rules,
instead of as separate fallback machinery in the engine module.
"""
from logic.storage_recommendation import Profile, Rule, const


def _default_database(p: Profile) -> str:
    # Fixed schema + ACID needs -> joins/constraints matter more than raw
    # write throughput, so a relational engine fits better.
    needs_relational_integrity = p.fixed_schema and p.needs_acid
    return "MySQL" if needs_relational_integrity else "MongoDB"


def _default_cap(p: Profile) -> str:
    # If the data is not allowed to lag behind reality, consistency must
    # win over availability, regardless of which engine stores it.
    cannot_tolerate_stale_reads = p.needs_acid or not p.tolerates_consistency_delay
    return "CP" if cannot_tolerate_stale_reads else "AP"


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


def _default_justification(p: Profile) -> str:
    cannot_tolerate_stale_reads = p.needs_acid or not p.tolerates_consistency_delay
    return _DEFAULT_TEXT_BY_CAP_DECISION[cannot_tolerate_stale_reads][0]


def _default_owasp_risk(p: Profile) -> str:
    if p.sensitive_data:
        return "A02"  # Cryptographic Failures: sensitive data mishandled
    cannot_tolerate_stale_reads = p.needs_acid or not p.tolerates_consistency_delay
    return _DEFAULT_TEXT_BY_CAP_DECISION[cannot_tolerate_stale_reads][1]


RULES: list[Rule] = [
    Rule(
        name="access_control_credentials",
        matches=lambda p: (
            p.sensitive_data and p.needs_acid and not p.tolerates_consistency_delay
        ),
        database=const("MySQL"),
        cap=const("CP"),
        justification=const(
            "authenticating with a stale or half-written credential is worse "
            "than the service being briefly unavailable"
        ),
        owasp_risk=const("A07"),  # Identification and Authentication Failures
    ),
    Rule(
        name="audit_trail",
        matches=lambda p: (
            p.sensitive_data and not p.needs_acid and not p.tolerates_consistency_delay
        ),
        database=const("MongoDB"),
        cap=const("CP"),
        justification=const(
            "an audit record that disagrees with what actually happened is "
            "worthless as evidence, even if it was written fast"
        ),
        owasp_risk=const("A08"),  # Software and Data Integrity Failures
    ),
    Rule(
        name="high_volume_telemetry",
        matches=lambda p: (
            not p.sensitive_data and p.tolerates_consistency_delay and p.horizontal_scale
        ),
        database=const("MongoDB"),
        cap=const("AP"),
        justification=const(
            "losing a second of freshness in a metric is acceptable; "
            "refusing new telemetry over a consistency check is not"
        ),
        owasp_risk=const("A09"),  # Security Logging and Monitoring Failures
    ),
    Rule(
        name="license_inventory",
        matches=lambda p: (
            p.needs_acid
            and p.fixed_schema
            and not p.tolerates_consistency_delay
            and not p.sensitive_data
        ),
        database=const("MySQL"),
        cap=const("CP"),
        justification=const(
            "selling the same license twice because two writes raced each "
            "other is unacceptable, even if it means rejecting a purchase"
        ),
        owasp_risk=const("A08"),  # Software and Data Integrity Failures
    ),
    Rule(
        name="session_cache",
        matches=lambda p: (
            p.sensitive_data
            and not p.needs_acid
            and p.tolerates_consistency_delay
            and p.horizontal_scale
        ),
        database=const("MongoDB"),
        cap=const("AP"),
        justification=const(
            "a session cache that is briefly stale is fine; a login page "
            "going down because one node is desynced is not"
        ),
        owasp_risk=const("A07"),  # Identification and Authentication Failures
    ),
    Rule(
        name="default",
        matches=lambda _p: True,
        database=_default_database,
        cap=_default_cap,
        justification=_default_justification,
        owasp_risk=_default_owasp_risk,
    ),
]
