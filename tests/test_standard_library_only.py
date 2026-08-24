import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src" / "validationhub"

ALLOWED_IMPORT_ROOTS = {
    "__future__",
    "argparse",
    "contextlib",
    "csv",
    "hashlib",
    "json",
    "pathlib",
    "re",
    "sqlite3",
    "dataclasses",
    "typing",
    "datetime",
    "uuid",
    "validationhub",
}

DISALLOWED_IMPORT_ROOTS = {
    "pandas",
    "openpyxl",
    "numpy",
    "sqlalchemy",
    "psycopg",
    "asyncpg",
    "alembic",
    "pydantic",
    "frictionless",
    "great_expectations",
    "requests",
    "httpx",
}


def import_roots(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    roots: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            roots.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            roots.add(node.module.split(".")[0])
    return roots


def test_placeholder_source_uses_only_allowed_imports() -> None:
    failures: dict[str, set[str]] = {}
    for path in SRC.rglob("*.py"):
        roots = import_roots(path)
        invalid = (roots - ALLOWED_IMPORT_ROOTS) | (roots & DISALLOWED_IMPORT_ROOTS)
        if invalid:
            failures[str(path.relative_to(ROOT))] = invalid
    assert failures == {}
