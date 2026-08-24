from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_schema_versioning_mentions_registry_and_comparison() -> None:
    text = (ROOT / "docs" / "SCHEMA_VERSIONING.md").read_text(encoding="utf-8")
    assert "0.1.0" in text
    assert "prohibited_fields.json" in text
    assert "fixture-based comparison" in text
