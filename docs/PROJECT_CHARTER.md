# Project Charter

Project name: ValidationHub

Project phase: Open-source registry scaffold

ValidationHub code is public. Operational evidence is permissioned by default
and remains outside Git. This repository is an intake registry foundation, not
a hosted evidence service.

## Purpose

Create a safe, open-source foundation for collecting, normalizing, validating,
and curating non-confidential wet-lab feedback related to FactorForge design
artifacts.

## Scope

- Policy documents.
- JSON Schema drafts.
- Standard-library-only placeholder import helpers.
- Local tests.
- Planning-only SQL draft.
- Empty gitignored data folders.
- Registry v0: a local, gitignored, file-based store (SQLite and/or JSONL) for
  records already covered by the existing JSON Schemas, plus an append-only
  change log. See "Local File-Based Registry Exception" below for the boundary
  that keeps this distinct from the Non-Scope "live database" prohibition.

## Non-Scope

- No web app.
- No prediction model.
- No live Neon/Postgres database, and no networked/served database of any kind.
- No Google Forms or Drive connector.
- No real wet-lab data processing.
- No public publication automation.

## Local File-Based Registry Exception (Registry v0)

Registry v0 uses the following local file-based exception.

"No live database" in this charter means no networked/served database engine
(no Neon, no Postgres-as-a-service, no process listening on a port, no remote
connection string). It does not prohibit a local, gitignored, file-based store
that is read/written by local scripts only:

- SQLite file and/or JSONL files, committed to `.gitignore` exactly like the
  existing `data/` folders.
- All records must still validate against the existing JSON Schemas
  (`intake_record`, `curated_validation_record`, `public_validation_summary`, etc.).
- Changes are tracked via an append-only change log (file-based, not a DB
  trigger/audit table).
- No network listener, no ORM-managed live connection, no automatic publication.

This exception exists only to let Registry v0 move past "schema drafts with no
storage" into "schema drafts that can actually hold records locally." It does
not change the Public Output Policy, the consent/prohibited-fields rules, or
the prohibition on a hosted/live database.

## Public Output Policy

The only public-facing output is manually reviewed non-confidential summaries copied into FactorForge/VALIDATION.md when optional public-summary consent is present.

## Google Forms Privacy Boundary

This scaffold assumes automatic email collection, response summaries, file uploads, and response editing are disabled.

## Strategic Relationship to FactorForge

ValidationHub is an open-source evidence-registry implementation that can
support public-safe FactorForge validation summaries after manual review. It
does not create performance guarantees, and its code repository is not an
evidence database.

## Relationship to Future ValidationHub 101

Future work may evaluate private Neon/Postgres storage. This scaffold remains file, schema, document, and test only.

## Acceptance Criteria

The scaffold exists, tests pass locally, prohibited fields are excluded from schemas,
no networked/live database integration is added (local file-based Registry v0 per the
exception above is allowed), and public output remains manual-review only.
