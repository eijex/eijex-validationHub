# ValidationHub Registry v0

Status: local-only Registry v0 foundation.

Registry v0 is a SQLite/JSON-safe evidence ledger for private ValidationHub work. It is designed for CPU-only local development and uses Python standard-library runtime code only.

## Boundary

Registry v0 stores hashes and coarse metadata. It must not store or print raw DNA/RNA/protein sequences, collaborator-private construct labels, internal batch IDs, contact details, exact confidential process parameters, or public unsalted `sequence_hash` values.

A FASTA file may be read locally to compute SHA-256, but only the digest, size, role, and a public-safe label are inserted into SQLite.

## Tables

- `registry_meta`: schema version.
- `registry_events`: append-only event stream. Every event stores `payload_hash`, `prev_event_hash`, and `event_hash` for tamper-evident chaining.
- `artifacts`: input FASTA, output FASTA, and registry-constant hash records. No raw content columns exist.
- `wet_lab_feedback_public_safe`: public-safe coarse feedback records derived from the public `wet_lab_result.yml` template.

Corrections should be represented by new events/records and `supersedes_*` references where available, not by editing prior records.

## Runtime commands

```bash
PYTHONPATH=src python scripts/validationhub_registry.py init --db data/registry_v0/local.sqlite3
PYTHONPATH=src python scripts/validationhub_registry.py constants-hash --root .
PYTHONPATH=src python scripts/validationhub_registry.py register-constants --db data/registry_v0/local.sqlite3 --root .
PYTHONPATH=src python scripts/validationhub_registry.py register-fasta --db data/registry_v0/local.sqlite3 --fasta path/to/file.fasta --role input_fasta --label public-safe-label
PYTHONPATH=src python scripts/validationhub_registry.py self-test --db data/registry_v0/local.sqlite3
```

`data/registry_v0/` and SQLite sidecar files are gitignored.

## Public-safe wet-lab feedback schema

The accepted public-safe fields mirror the public GitHub Issue template at `factorforge/.github/ISSUE_TEMPLATE/wet_lab_result.yml`:

- Issue-template `version` is canonicalized to registry field `factorforge_version`.
- `profile`
- `host`
- `protein_class`
- `assay_category`
- `comparison_result`
- `expression_result`
- optional `replicate_category`
- optional `non_confidential_notes`
- confirmations: `public_safe_confirmation`; optional local Registry v0 review guards `feedback_boundary_confirmation` and `maintainer_review_confirmation` may also be supplied when an internal review step records them.

The validator rejects prohibited/private field names from `docs/DATA_BOUNDARY.md` / `schemas/prohibited_fields.json`, including raw sequence fields, construct IDs, internal batch IDs, contact fields, and public `sequence_hash`.

These records are user-provided coarse feedback summaries only. They are not controlled validation studies, regulatory claims, clinical endorsements, wet-lab proof, expression guarantees, or yield-improvement claims.
