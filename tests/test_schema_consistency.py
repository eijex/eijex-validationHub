import csv
import json
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
SCHEMAS = ROOT / "schemas"


def load_prohibited_fields() -> set[str]:
    data = json.loads((SCHEMAS / "prohibited_fields.json").read_text(encoding="utf-8"))
    return set(data["prohibited_field_names"])


def load_schema(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def test_schema_files_are_valid_json_schema_with_closed_properties() -> None:
    for path in SCHEMAS.glob("*.schema.json"):
        schema = load_schema(path)
        Draft202012Validator.check_schema(schema)
        assert schema.get("additionalProperties") is False, path


def test_prohibited_field_names_do_not_appear_as_schema_properties() -> None:
    prohibited = load_prohibited_fields()
    for path in SCHEMAS.glob("*.schema.json"):
        schema = load_schema(path)
        properties = set(schema.get("properties", {}))
        assert properties.isdisjoint(prohibited), path


def test_specific_forbidden_tokens_absent_from_schema_json() -> None:
    forbidden = {
        "sequence_hash",
        "construct_id",
        "protein_name",
        "submitter_name",
        "submitter_email",
        "respondent_email",
        "contact_email",
        "phone_number",
        "personal_identifier",
    }
    for path in SCHEMAS.glob("*.schema.json"):
        text = path.read_text(encoding="utf-8")
        assert forbidden.isdisjoint({token for token in forbidden if token in text}), path


def test_public_validation_summary_schema_is_public_safe() -> None:
    schema = load_schema(SCHEMAS / "public_validation_summary.schema.json")
    properties = set(schema["properties"])
    forbidden = {
        "temporary_submission_id",
        "intake_record_uuid",
        "validation_record_id",
        "non_confidential_construct_alias",
        "review_status",
        "reviewer_notes",
    }
    assert properties.isdisjoint(forbidden)
    assert {"public_validation_id", "disclaimer"}.issubset(properties)


def test_google_forms_sample_header_matches_schema_properties() -> None:
    schema = load_schema(SCHEMAS / "google_forms_response.schema.json")
    expected = set(schema["properties"])
    with (ROOT / "examples" / "google_forms_sample.csv").open(
        "r",
        encoding="utf-8",
        newline="",
    ) as handle:
        header = next(csv.reader(handle))
    assert set(header) == expected
