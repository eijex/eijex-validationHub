from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_consent_policy_defines_required_and_optional_consent() -> None:
    text = (ROOT / "docs" / "CONSENT_POLICY.md").read_text(encoding="utf-8")
    assert "right to share" in text
    assert "no prohibited or confidential data" in text
    assert "internal FactorForge development use" in text
    assert "optional public-summary consent" in text
    assert "manual human review" in text
