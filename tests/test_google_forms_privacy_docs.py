from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_google_forms_privacy_settings_are_documented() -> None:
    text = (ROOT / "docs" / "GOOGLE_FORMS_PRIVACY.md").read_text(encoding="utf-8")
    assert "automatic email collection" in text
    assert "file uploads" in text
    assert "response editing" in text
    assert "does not connect to Google Forms" in text
