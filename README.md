# ValidationHub

ValidationHub is an open-source evidence-registry foundation for collecting,
normalizing, validating, and curating non-confidential wet-lab feedback linked
to FactorForge design artifacts.

## Open Code, Permissioned Data

The software, schemas, policies, tests, and synthetic examples in this
repository are public. Raw sequences, partner records, personal information,
and permissioned experimental evidence must remain outside the repository.
Public validation summaries require explicit consent and manual review.

## Public Output Policy

The only public-facing validation artifact is a manually curated summary copied
into FactorForge/VALIDATION.md. ValidationHub does not auto-publish summaries or
push permissioned records to public repositories.

## Current Scope

This scaffold creates a safe intake-registry foundation: documents, JSON Schema drafts (including `validationhub_intake_draft_v0.1.json`), placeholder standard-library-only import helpers, local tests, a planning-only SQL draft, and empty gitignored data folders. A local, gitignored, file-based Registry v0 (SQLite/JSONL only — no networked database) is in scope per the Local File-Based Registry Exception in `docs/PROJECT_CHARTER.md`.

Registry v0 is implemented as a standard-library SQLite append-only ledger. See `docs/REGISTRY_V0.md` for the local-only CLI, FASTA/registry-constant SHA-256 tracking, and public-safe wet-lab feedback schema boundary.

Current Status: v0.1.0 registry scaffold (docs + schemas + tests) complete.
The prohibited-field policy treats `sequence_hash` as conditionally prohibited
(see `docs/SCHEMA_VERSIONING.md` and `schemas/prohibited_fields.json`). No
partner documents or real evidence records are included.

## What This Project Is

- An open-source evidence registry foundation.
- A safe policy and schema workspace for non-confidential wet-lab feedback.
- A local-first scaffold for permissioned evidence storage planning.

## What This Project Is Not

- It is not full ValidationHub.
- It is not a web app.
- It is not a prediction model.
- It is not a regulatory compliance system.
- It is not a clinical or patient data system.
- It is not a proprietary construct repository.
- It is not a public performance-claim generator.

## Data Boundary Warning

Do not submit or commit patient data, confidential partner/customer data, proprietary sequences, unpublished construct sequences, internal batch IDs, raw DNA/RNA/protein sequences, submitter identity, respondent email addresses, or exact confidential process parameters.

See docs/DATA_BOUNDARY.md before adding any schema or record field.

## Google Forms Privacy Warning

This scaffold assumes Google Forms automatic email collection, response summaries, file uploads, and response editing are disabled.

## SQL / Neon Status

This scaffold does not connect to Neon/Postgres or any live database. Database integration is reserved for a later explicit change.

## Quick Setup

```powershell
python -m pip install -e ".[dev]"
python -m pytest
```

No `.env`, API keys, database URLs, or external services are used in this scaffold.

## Repository Structure

- `docs/`: evidence policies, public-boundary guidance, and registry notes.
- `schemas/`: JSON Schema drafts (intake, curated, public summary, Google Forms, intake draft v0.1) and the prohibited field registry.
- `src/validationhub/`: standard-library-only placeholder intake helpers.
- `tests/`: local policy, schema, and scaffold checks.
- `examples/`: synthetic non-sensitive examples only.
- `db/`: planning-only Postgres draft for later work (no live connection).
- `data/`: gitignored private intake folders with `.gitkeep` placeholders.

## Repository boundary

Only source code, public schemas, documentation, and synthetic examples belong
in Git. Runtime databases, raw form exports, partner documents, and evidence
records must use permissioned storage outside this repository.

## Public Summary Disclaimer

Public validation summaries are user-submitted wet-lab feedback summaries. They are not controlled validation studies, regulatory claims, or guarantees of FactorForge performance.

## License

ValidationHub is licensed under GNU AGPL v3.0. This license applies to the
software and repository content; it does not grant rights to third-party
research records that are intentionally excluded from the repository.
