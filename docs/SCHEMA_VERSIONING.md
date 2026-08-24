# Schema Versioning

Initial schema drafts use version `0.1.0`.

Schema changes must preserve the data boundary and update tests when accepted fields change.

Breaking changes require a new schema version, migration notes, and fixture-based comparison before any future production use.

The prohibited field registry in `schemas/prohibited_fields.json` must remain aligned with docs/DATA_BOUNDARY.md.

## Current Schema Versions

- `curated_validation_record.schema.json`: `0.2.0`. This version adds the C+ lite `design_reference`, `provenance_relations`, and opaque curation metadata fields.
- `design_reference.schema.json`: initial `0.1` embedded-reference contract. It is versioned through the parent curated record schema.
- `benchmark_evidence_reference.schema.json`: `0.1.0`. This is a standalone pointer record for benchmark manifest evidence and must remain separate from wet-lab curated records.
