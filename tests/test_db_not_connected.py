from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_no_database_dependencies_or_runtime_config() -> None:
    config = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    text = config.split("[project.optional-dependencies]", 1)[0].lower()
    for dependency in ("sqlalchemy", "psycopg", "asyncpg", "alembic", "prisma", "drizzle", "neon"):
        assert dependency not in text
    assert not (ROOT / ".env").exists()
    assert not (ROOT / ".env.example").exists()
    assert 'postgres = [' in config
    assert "eijex-db-core==0.1.2" in config.split("[project.optional-dependencies]", 1)[1]


def test_db_plan_says_planning_only() -> None:
    plan = (ROOT / "docs" / "DB_PLAN.md").read_text(encoding="utf-8")
    draft = (ROOT / "db" / "schema_draft.sql").read_text(encoding="utf-8")
    assert "No live DB connection is used" in plan
    assert "planning-only SQL draft" in draft
    assert "DATABASE_URL" in draft
