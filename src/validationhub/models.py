"""Small standard-library models for local placeholder records."""

from dataclasses import dataclass


@dataclass(frozen=True)
class ValidationSurveyRecord:
    schema_version: str
    factorforge_version: str
    optimization_profile: str
    host_organism: str
    protein_class: str
    expression_system_assay_type: str
    harvest_timepoint: str
    replicate_category: str
    comparison_result: str
    expression_result: str
    approximate_yield_range: str
    consent_right_to_share: bool
    consent_no_prohibited_data: bool
    consent_internal_use: bool
    consent_public_summary: bool
    subcellular_targeting_category: str = ""
    promoter_category: str = ""
    native_sequence_control_status: str = ""
    non_confidential_construct_alias: str = ""
    non_confidential_notes: str = ""
