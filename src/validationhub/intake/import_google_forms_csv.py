"""Local CSV reader placeholder for synthetic Google Forms exports."""

import csv
from pathlib import Path


def read_google_forms_csv(path: str | Path) -> list[dict[str, str]]:
    """Read a local CSV file without connecting to Google Forms."""
    with Path(path).open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))
