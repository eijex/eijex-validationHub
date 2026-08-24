"""Safe constants for the ValidationHub scaffold."""

PROHIBITED_FIELD_NAMES = (
    "raw_sequence",
    "sequence",
    "dna_sequence",
    "rna_sequence",
    "protein_sequence",
    "amino_acid_sequence",
    "construct_sequence",
    "customer_sequence",
    "proprietary_sequence",
    "sequence_hash",
    "construct_id",
    "internal_batch_id",
    "customer_construct_id",
    "protein_name",
    "submitter_name",
    "submitter_email",
    "respondent_email",
    "contact_email",
    "phone_number",
    "personal_identifier",
)

SAFE_INSTITUTION_DISCLOSURE_VALUES = ("anonymous", "disclosed", "not_provided")

SAFE_COMPARISON_RESULTS = (
    "improved",
    "equivalent",
    "reduced",
    "inconclusive",
    "no_control",
    "not_reported",
)

SAFE_EXPRESSION_RESULTS = (
    "detected",
    "not_detected",
    "weak",
    "strong",
    "inconclusive",
    "not_reported",
)

SAFE_REPLICATE_CATEGORIES = (
    "not_reported",
    "single_observation",
    "2-3 replicates",
    "4-5 replicates",
    "gt_5 replicates",
)

SAFE_APPROXIMATE_YIELD_RANGES = (
    "not_reported",
    "below_detection",
    "lt_0_01_mg_g_fw",
    "0_01_to_0_1_mg_g_fw",
    "0_1_to_1_mg_g_fw",
    "1_to_5_mg_g_fw",
    "gt_5_mg_g_fw",
    "other_coarse_range",
)
