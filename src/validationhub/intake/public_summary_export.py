"""Manual-review public summary candidate formatter."""

DISCLAIMER = (
    "These entries are user-submitted wet-lab feedback summaries. "
    "They are not controlled validation studies, regulatory claims, "
    "or guarantees of FactorForge performance."
)


PUBLIC_FIELDS = (
    "public_validation_id",
    "factorforge_version",
    "host_organism",
    "optimization_profile",
    "protein_class",
    "expression_system_assay_type",
    "harvest_timepoint",
    "replicate_category",
    "comparison_result",
    "expression_result",
    "approximate_yield_range",
    "non_confidential_notes",
)


def build_public_summary(record: dict[str, object]) -> dict[str, object]:
    summary = {field: record.get(field, "") for field in PUBLIC_FIELDS}
    summary["disclaimer"] = DISCLAIMER
    return summary
