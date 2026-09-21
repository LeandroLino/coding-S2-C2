"""
Exercise 1 — rule table for the storage decision assistant.

Each rule is a named, self-contained decision covering one scenario from
the assignment; the first matching rule wins. Kept separate from
`logic/storage_recommendation.py` so the decision data (what to recommend
for each scenario) is easy to read and extend independently from the
matching/fallback machinery.
"""
from logic.storage_recommendation import Profile, Rule

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
