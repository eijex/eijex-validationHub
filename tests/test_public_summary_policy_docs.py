from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_public_summary_policy_is_manual_only() -> None:
    text = (ROOT / "docs" / "PUBLIC_VALIDATION_LOG_POLICY.md").read_text(encoding="utf-8")
    assert "FactorForge/VALIDATION.md" in text
    assert "manually reviewed" in text
    assert "must not automatically publish" in text
    assert "not controlled validation studies" in text
    assert "not guarantees" in text
