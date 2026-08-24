"""Consent checks for placeholder intake records."""


REQUIRED_CONSENT_FIELDS = (
    "consent_right_to_share",
    "consent_no_prohibited_data",
    "consent_internal_use",
)


def has_required_consent(record: dict[str, object]) -> bool:
    return all(record.get(field) is True for field in REQUIRED_CONSENT_FIELDS)


def has_public_summary_consent(record: dict[str, object]) -> bool:
    return record.get("consent_public_summary") is True
