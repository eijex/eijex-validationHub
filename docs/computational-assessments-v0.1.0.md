# Local computational assessments

Version: 0.1.0

`validationhub.computational_evidence.ComputationalEvidenceStore` is a private local SQLite store for minimal existing-CDS computational evidence. It is separate from Registry v0 FASTA artifacts and from wet-lab measurements. It requires an explicitly supplied path outside repository roots when used through the AgentOS task API.

Each task has one immutable assessment with opaque task, run and assessment IDs plus an internal subject digest. Identical repeated persistence returns the existing assessment ID; conflicting runs, subjects or evidence are rejected. The evidence field allowlist excludes sequences, paths, construct names, private metrics and wet-lab outcomes. No approval or public projection is generated.

AgentOS owns workflow and approval enforcement. ValidationHub owns this assessment persistence contract. An assessment record alone is not workflow success: the AgentOS lookup also requires a completed central task and matching succeeded trace. Cross-store commit inconsistencies require manual reconciliation.

This implementation neither modifies the shared PostgreSQL schema nor imports synthetic computational checks as experimental measurements. It is an opt-in implementation that has not been deployed or published.
