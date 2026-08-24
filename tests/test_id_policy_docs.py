from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_id_policy_uses_public_safe_aliases() -> None:
    text = (ROOT / "docs" / "ID_POLICY.md").read_text(encoding="utf-8")
    assert "Non-confidential construct alias" in text
    assert "non_confidential_construct_alias" in text
    assert "must not contain internal batch IDs" in text
    assert "public_validation_id" in text
