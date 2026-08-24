"""Simple prohibited-field checks for local placeholder records."""

from validationhub.constants import PROHIBITED_FIELD_NAMES


def find_prohibited_fields(record: dict[str, object]) -> list[str]:
    return sorted(field for field in record if field in PROHIBITED_FIELD_NAMES)


def is_public_safe_shape(record: dict[str, object]) -> bool:
    return not find_prohibited_fields(record)
