from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_open_code_permissioned_data_policy_is_prominent() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    license_text = (ROOT / "LICENSE").read_text(encoding="utf-8")
    assert "Open Code, Permissioned Data" in readme
    assert "GNU AFFERO GENERAL PUBLIC LICENSE" in license_text
    assert "partner records" in readme
