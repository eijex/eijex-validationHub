from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from validationhub.registry_v0 import (
    PUBLIC_WET_LAB_ALLOWED_FIELDS,
    PUBLIC_WET_LAB_REQUIRED_FIELDS,
    PUBLIC_WET_LAB_TEMPLATE_FIELD_ALIASES,
    RegistryError,
    initialize_registry,
    register_fasta_artifact,
    register_public_wet_lab_feedback,
    register_registry_constants,
    registry_constants_hash,
    registry_summary,
    validate_public_wet_lab_feedback,
    verify_event_chain,
)

SAFE_FEEDBACK = {
    "factorforge_version": "3.4.2",
    "profile": "balanced",
    "host": "N. benthamiana agroinfiltration",
    "protein_class": "Antigen",
    "assay_category": "Protein detection assay",
    "comparison_result": "Inconclusive",
    "expression_result": "Signal observed",
    "replicate_category": "Single experiment",
    "non_confidential_notes": "Coarse public-safe summary only.",
    "public_safe_confirmation": True,
    "feedback_boundary_confirmation": True,
    "maintainer_review_confirmation": True,
}


def write_synthetic_fasta(path: Path) -> None:
    path.write_text(">synthetic-public-safe-fixture\nATGGCTGCTTAA\n", encoding="utf-8")


def test_initialize_registry_creates_genesis_event(tmp_path: Path) -> None:
    db = tmp_path / "registry.sqlite3"
    head = initialize_registry(db)

    assert len(head) == 64
    assert verify_event_chain(db)
    assert registry_summary(db)["events"] == 1


def test_register_fasta_hash_only_does_not_persist_sequence(tmp_path: Path) -> None:
    db = tmp_path / "registry.sqlite3"
    fasta = tmp_path / "input.fasta"
    write_synthetic_fasta(fasta)

    result = register_fasta_artifact(db, fasta, role="input_fasta", label="synthetic-input")

    assert result.role == "input_fasta"
    assert len(result.sha256) == 64
    raw_db = db.read_bytes()
    assert b"ATGGCTGCTTAA" not in raw_db
    assert b"synthetic-public-safe-fixture" not in raw_db
    assert verify_event_chain(db)


def test_register_output_fasta_and_constants_are_append_only_events(tmp_path: Path) -> None:
    root = Path(__file__).resolve().parents[1]
    db = tmp_path / "registry.sqlite3"
    fasta = tmp_path / "output.fasta"
    write_synthetic_fasta(fasta)

    register_fasta_artifact(db, fasta, role="output_fasta", label="synthetic-output")
    register_registry_constants(db, root)
    summary = registry_summary(db)

    assert summary["artifacts"] == 2
    assert summary["events"] == 3  # genesis + two append events
    assert verify_event_chain(db)


def test_registry_constants_hash_is_deterministic() -> None:
    root = Path(__file__).resolve().parents[1]

    first = registry_constants_hash(root)
    second = registry_constants_hash(root)

    assert first == second
    assert len(first.constants_hash) == 64
    assert any(path.endswith("schemas/prohibited_fields.json") for path, _sha in first.files)


def test_registry_constants_hash_fails_closed_for_missing_policy_file(tmp_path: Path) -> None:
    with pytest.raises(RegistryError, match="constants path is missing"):
        registry_constants_hash(tmp_path, ("missing-policy.json",))


def test_public_wet_lab_feedback_accepts_only_public_safe_fields() -> None:
    clean = validate_public_wet_lab_feedback(SAFE_FEEDBACK)

    assert clean["profile"] == "balanced"
    assert clean["public_safe_confirmation"] is True


def test_public_wet_lab_template_version_alias_is_canonicalized() -> None:
    template_payload = dict(SAFE_FEEDBACK)
    template_payload["version"] = template_payload.pop("factorforge_version")

    clean = validate_public_wet_lab_feedback(template_payload)

    assert clean["factorforge_version"] == "3.4.2"
    assert "version" not in clean


def test_wet_lab_template_fields_stay_mapped_to_registry_fields() -> None:
    root = Path(__file__).resolve().parents[2]
    template = root / "factorforge" / ".github" / "ISSUE_TEMPLATE" / "wet_lab_result.yml"
    if not template.exists():
        pytest.skip("optional sibling FactorForge checkout is not available")
    template_text = template.read_text(encoding="utf-8")
    lines = template_text.splitlines()
    template_ids = {
        line.split(":", 1)[1].strip()
        for line in lines
        if line.strip().startswith("id: ")
    }
    required_template_ids = set()
    for index, line in enumerate(lines):
        if not line.strip().startswith("id: "):
            continue
        field_id = line.split(":", 1)[1].strip()
        following = []
        for block_line in lines[index + 1 :]:
            if block_line.startswith("  - type:"):
                break
            following.append(block_line)
        block = "\n".join(following)
        if "required: true" in block:
            required_template_ids.add(field_id)

    registry_template_ids = {
        field
        for field in PUBLIC_WET_LAB_ALLOWED_FIELDS
        if field not in PUBLIC_WET_LAB_TEMPLATE_FIELD_ALIASES.values()
    } | set(PUBLIC_WET_LAB_TEMPLATE_FIELD_ALIASES)
    registry_required_template_ids = {
        field
        for field in PUBLIC_WET_LAB_REQUIRED_FIELDS
        if field not in PUBLIC_WET_LAB_TEMPLATE_FIELD_ALIASES.values()
    } | set(PUBLIC_WET_LAB_TEMPLATE_FIELD_ALIASES)

    assert template_ids <= registry_template_ids
    assert required_template_ids == registry_required_template_ids
    assert {
        "feedback_boundary_confirmation",
        "maintainer_review_confirmation",
    } <= PUBLIC_WET_LAB_ALLOWED_FIELDS


def test_public_wet_lab_feedback_rejects_raw_sequence_and_sequence_hash() -> None:
    unsafe = dict(SAFE_FEEDBACK)
    unsafe["raw_sequence"] = "ATGGCTGCTTAA"
    with pytest.raises(RegistryError, match="prohibited fields"):
        validate_public_wet_lab_feedback(unsafe)

    unsafe_hash = dict(SAFE_FEEDBACK)
    unsafe_hash["sequence_hash"] = "0" * 64
    with pytest.raises(RegistryError, match="prohibited fields"):
        validate_public_wet_lab_feedback(unsafe_hash)


def test_register_public_feedback_stores_canonical_record_hash(tmp_path: Path) -> None:
    db = tmp_path / "registry.sqlite3"

    feedback_id = register_public_wet_lab_feedback(db, SAFE_FEEDBACK)

    assert feedback_id
    assert registry_summary(db)["public_feedback"] == 1
    with sqlite3.connect(db) as conn:
        text = conn.execute("SELECT record_json FROM wet_lab_feedback_public_safe").fetchone()[0]
    assert "raw_sequence" not in text
    assert "controlled validation" not in text.lower()


def test_private_identifying_artifact_label_is_rejected(tmp_path: Path) -> None:
    db = tmp_path / "registry.sqlite3"
    fasta = tmp_path / "input.fasta"
    write_synthetic_fasta(fasta)

    with pytest.raises(RegistryError, match="public-safe"):
        register_fasta_artifact(db, fasta, role="input_fasta", label="synthetic-private-input")
