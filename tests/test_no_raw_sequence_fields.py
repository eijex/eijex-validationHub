import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def prohibited_fields() -> set[str]:
    data = json.loads((ROOT / "schemas" / "prohibited_fields.json").read_text(encoding="utf-8"))
    return set(data["prohibited_field_names"])


def schema_properties() -> set[str]:
    properties: set[str] = set()
    for path in (ROOT / "schemas").glob("*.schema.json"):
        schema = json.loads(path.read_text(encoding="utf-8"))
        properties.update(schema.get("properties", {}).keys())
    return properties


def test_prohibited_field_names_are_not_schema_properties() -> None:
    assert schema_properties().isdisjoint(prohibited_fields())


def test_specific_publicly_forbidden_fields_absent_from_examples() -> None:
    forbidden = {
        "sequence_hash",
        "construct_id",
        "protein_name",
        "submitter_email",
        "respondent_email",
    }
    for path in (ROOT / "examples").iterdir():
        assert forbidden.isdisjoint(path.read_text(encoding="utf-8").split(","))
