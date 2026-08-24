from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_confidentiality_guardrails_warn_against_sensitive_data() -> None:
    text = (ROOT / "docs" / "CONFIDENTIALITY_GUARDRAILS.md").read_text(encoding="utf-8")
    assert "patient data" in text
    assert "confidential partner/customer information" in text
    assert "respondent identity" in text
    assert "raw sequence data" in text
    assert "manual review" in text
