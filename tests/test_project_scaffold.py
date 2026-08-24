from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_required_scaffold_paths_exist() -> None:
    required_paths = [
        "README.md",
        "pyproject.toml",
        ".gitignore",
        "LICENSE",
        "SECURITY.md",
        "CONTRIBUTING.md",
        "db/README.md",
        "db/schema_draft.sql",
        "docs/PROJECT_CHARTER.md",
        "docs/DATA_BOUNDARY.md",
        "docs/CONSENT_POLICY.md",
        "docs/CONFIDENTIALITY_GUARDRAILS.md",
        "docs/PUBLIC_VALIDATION_LOG_POLICY.md",
        "docs/WETLAB_VALIDATION_INTAKE.md",
        "docs/GOOGLE_FORMS_PRIVACY.md",
        "docs/CROSS_REPO_LINKS.md",
        "docs/MCP_CONTEXT.md",
        "docs/DB_PLAN.md",
        "docs/ID_POLICY.md",
        "docs/DATA_RETENTION.md",
        "docs/MANUAL_PUBLICATION_WORKFLOW.md",
        "docs/SCHEMA_VERSIONING.md",
        "docs/REVIEW_CHECKLIST.md",
        "docs/OPEN_SOURCE_REFERENCES.md",
        "docs/SETUP_NOTES.md",
        "schemas/prohibited_fields.json",
        "schemas/google_forms_response.schema.json",
        "schemas/intake_record.schema.json",
        "schemas/validation_survey_record.schema.json",
        "schemas/curated_validation_record.schema.json",
        "schemas/public_validation_summary.schema.json",
        "src/validationhub/__init__.py",
        "src/validationhub/models.py",
        "src/validationhub/constants.py",
        "src/validationhub/intake/__init__.py",
        "src/validationhub/intake/import_google_forms_csv.py",
        "src/validationhub/intake/normalize_survey.py",
        "src/validationhub/intake/consent_checks.py",
        "src/validationhub/intake/confidentiality_checks.py",
        "src/validationhub/intake/public_summary_export.py",
        "examples/google_forms_sample.csv",
        "examples/public_summary_example.md",
        "data/raw/.gitkeep",
        "data/curated/.gitkeep",
        "data/rejected/.gitkeep",
        "data/public_candidates/.gitkeep",
    ]
    missing = [path for path in required_paths if not (ROOT / path).exists()]
    assert missing == []


def test_no_forbidden_directories_or_automation() -> None:
    assert not (ROOT / "docs" / "docs").exists()
    workflows = ROOT / ".github" / "workflows"
    assert {path.name for path in workflows.glob("*.yml")} <= {"ci.yml"}
    assert not (ROOT / ".env").exists()
    assert not (ROOT / ".env.example").exists()


def test_text_files_are_utf8_lf_no_bom_final_newline() -> None:
    suffixes = {".md", ".json", ".py", ".sql", ".csv", ".toml"}
    named = {".gitattributes", ".gitignore", "LICENSE"}
    generated_dirs = {".git", ".pytest_cache", ".ruff_cache", "validationhub.egg-info"}
    for path in ROOT.rglob("*"):
        if generated_dirs.intersection(path.parts) or not path.is_file():
            continue
        if path.suffix not in suffixes and path.name not in named:
            continue
        data = path.read_bytes()
        assert not data.startswith(b"\xef\xbb\xbf"), path
        assert b"\r\n" not in data, path
        assert data.endswith(b"\n"), path
        data.decode("utf-8")
