# Setup Notes

ValidationHub runs locally and does not require a hosted database.

```powershell
python -m pip install -e ".[dev]"
python -m pytest -q
python -m ruff check .
```

Do not place runtime databases, form exports, credentials, sequences, partner
documents, or evidence records in the repository. Local SQLite files and the
`data/` runtime directories are ignored by Git.
