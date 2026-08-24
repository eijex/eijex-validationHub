from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_manual_publication_workflow_forbids_automation() -> None:
    text = (ROOT / "docs" / "MANUAL_PUBLICATION_WORKFLOW.md").read_text(encoding="utf-8")
    assert "Public publication is manual only" in text
    assert "optional public-summary consent is true" in text
    assert "Manually copy" in text
    assert "must not auto-publish" in text
