from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_open_source_references_preserve_private_license_boundary() -> None:
    text = (ROOT / "docs" / "OPEN_SOURCE_REFERENCES.md").read_text(encoding="utf-8")
    assert "private and proprietary" in text
    assert "No open-source license is granted" in text
    assert "no third-party code is copied" in text
