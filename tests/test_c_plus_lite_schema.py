import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator
from referencing import Registry, Resource
from referencing.jsonschema import DRAFT202012

ROOT = Path(__file__).resolve().parents[1]
SCHEMAS = ROOT / "schemas"
EXAMPLES = ROOT / "examples"


def load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def validator_for(schema_name: str) -> Draft202012Validator:
    schema = load_json(SCHEMAS / schema_name)
    resources = []
    for path in SCHEMAS.glob("*.schema.json"):
        resource = Resource.from_contents(
            load_json(path),
            default_specification=DRAFT202012,
        )
        resources.append((path.name, resource))
        resources.append((f"{SCHEMAS.as_uri()}/{path.name}", resource))
    return Draft202012Validator(schema, registry=Registry().with_resources(resources))


def prohibited_field_names() -> set[str]:
    data = load_json(SCHEMAS / "prohibited_fields.json")
    names = set(data["prohibited_field_names"])
    names.update(data["conditionally_prohibited_field_names"])
    return names


def curated_fixture() -> dict[str, object]:
    return load_json(EXAMPLES / "curated_validation_record_c_plus_lite_example.json")


def benchmark_fixture() -> dict[str, object]:
    return load_json(EXAMPLES / "benchmark_evidence_reference_example.json")


def test_curated_c_plus_lite_example_validates() -> None:
    validator_for("curated_validation_record.schema.json").validate(curated_fixture())


def test_benchmark_evidence_reference_example_validates() -> None:
    validator_for("benchmark_evidence_reference.schema.json").validate(benchmark_fixture())


def test_design_reference_fields_are_required() -> None:
    schema = load_json(SCHEMAS / "design_reference.schema.json")
    assert set(schema["required"]) == {
        "reference_type",
        "design_package_id",
        "factorforge_version",
    }


def test_benchmark_manifest_digest_scope_is_manifest_only() -> None:
    schema = load_json(SCHEMAS / "benchmark_evidence_reference.schema.json")
    scope = schema["properties"]["manifest_digest"]["properties"]["scope"]
    assert scope == {"type": "string", "const": "manifest_only"}


def test_curated_provenance_relation_type_is_restricted() -> None:
    schema = load_json(SCHEMAS / "curated_validation_record.schema.json")
    relation_type = schema["properties"]["provenance_relations"]["items"]["properties"][
        "relation_type"
    ]
    assert relation_type == {"type": "string", "enum": ["wasDerivedFrom"]}


@pytest.mark.parametrize("field_name", sorted(prohibited_field_names()))
def test_curated_new_nested_objects_reject_prohibited_field_names(field_name: str) -> None:
    record = curated_fixture()
    record["design_reference"][field_name] = "blocked"
    errors = list(validator_for("curated_validation_record.schema.json").iter_errors(record))
    assert errors


@pytest.mark.parametrize("field_name", sorted(prohibited_field_names()))
def test_curated_provenance_relations_reject_prohibited_field_names(field_name: str) -> None:
    record = curated_fixture()
    record["provenance_relations"][0][field_name] = "blocked"
    errors = list(validator_for("curated_validation_record.schema.json").iter_errors(record))
    assert errors


@pytest.mark.parametrize("field_name", sorted(prohibited_field_names()))
def test_benchmark_reference_rejects_prohibited_field_names(field_name: str) -> None:
    record = benchmark_fixture()
    record["manifest_digest"][field_name] = "blocked"
    errors = list(
        validator_for("benchmark_evidence_reference.schema.json").iter_errors(record)
    )
    assert errors
