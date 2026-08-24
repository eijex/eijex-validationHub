-- ValidationHub planning-only SQL draft.
-- Do not run this file against Neon/Postgres in the current scaffold.
-- No live database connection, migration tool, or DATABASE_URL is used.

CREATE TABLE curated_validation_records_draft (
    validation_record_id TEXT PRIMARY KEY,
    schema_version TEXT NOT NULL,
    factorforge_version TEXT NOT NULL,
    optimization_profile TEXT NOT NULL,
    host_organism TEXT NOT NULL,
    protein_class TEXT NOT NULL,
    expression_system_assay_type TEXT NOT NULL,
    harvest_timepoint TEXT NOT NULL,
    replicate_category TEXT NOT NULL,
    comparison_result TEXT NOT NULL,
    expression_result TEXT NOT NULL,
    approximate_yield_range TEXT NOT NULL,
    institution_disclosure TEXT NOT NULL,
    non_confidential_construct_alias TEXT,
    non_confidential_notes TEXT,
    public_summary_consent BOOLEAN NOT NULL DEFAULT FALSE,
    review_status TEXT NOT NULL DEFAULT 'draft'
);
