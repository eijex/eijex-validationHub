"""Normalize local survey rows into safe dictionaries."""

from typing import Any


def normalize_boolean(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"true", "yes", "y", "1"}


def normalize_row(row: dict[str, Any]) -> dict[str, Any]:
    normalized = {
        key: value.strip() if isinstance(value, str) else value
        for key, value in row.items()
    }
    for key in (
        "consent_right_to_share",
        "consent_no_prohibited_data",
        "consent_internal_use",
        "consent_public_summary",
    ):
        if key in normalized:
            normalized[key] = normalize_boolean(normalized[key])
    return normalized
