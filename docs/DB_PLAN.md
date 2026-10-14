# Database Plan

Neon/Postgres is a candidate private storage backend for future work.

The current scaffold remains file, schema, document, and test only. No live DB connection is used by default. The explicitly optional measurement adapter is documented in [POSTGRES_ADAPTER.md](POSTGRES_ADAPTER.md).

**Registry v0 (decided 2026-06-21)**: a local, gitignored SQLite file and/or JSONL files
are in scope now, as a minimal storage layer for records that already validate against
the existing JSON Schemas. This is not a "live DB" under `PROJECT_CHARTER.md`'s
definition (no network listener, no remote connection). See
`docs/PROJECT_CHARTER.md` → "Local File-Based Registry Exception" for the exact boundary.

No raw CSV, rejected records, curated private records, or public summary candidates should be committed.

Job 368 implements the narrow optional measurement adapter; hosted services and wider evidence operations remain separate work.

Future DB scope may include a private Neon Postgres project, migrations, curated validation records, rejected-record metadata, consent audit records, public summary candidates, and an append-only audit trail.

Future DB work must continue to exclude raw sequence storage, patient data, confidential customer/partner data, and automatic public publication.
