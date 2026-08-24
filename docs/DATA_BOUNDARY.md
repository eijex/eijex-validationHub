# Data Boundary

DATA_BOUNDARY.md is the human-readable source of truth for allowed data, coarse-grained data, prohibited data, construct/protein identifier rules, and coarse-graining rules.

`schemas/prohibited_fields.json` is the machine-readable source of truth for prohibited field-name tests.

## Allowed Data

- FactorForge version.
- Optimization profile.
- Host organism.
- Protein class.
- Subcellular targeting category.
- Promoter category.
- Expression system / assay type.
- Native sequence control status.
- Harvest timepoint.
- Replicate category.
- Comparison result.
- Expression result.
- Approximate yield range.
- Non-confidential notes.
- Consent status.
- Optional public-summary permission.

## Avoid or Coarse-Grain

- Protein name.
- Construct nickname.
- Institution name.
- Detailed notes.

## Prohibited Data

- Raw DNA/RNA/protein sequences.
- Proprietary sequences.
- Unpublished construct sequences.
- Internal batch IDs.
- Confidential partner/customer data.
- Private customer names.
- Patient data.
- Clinical subject data.
- Submitter identity.
- Respondent email addresses.
- Phone numbers.
- Exact confidential process parameters.
- Confidential assay protocols.
- Unpublished construct-identifying labels.

## Prohibited Field Naming Rule

Do not create fields named:

- raw_sequence
- sequence
- dna_sequence
- rna_sequence
- protein_sequence
- amino_acid_sequence
- construct_sequence
- customer_sequence
- proprietary_sequence
- submitter_name
- submitter_email
- respondent_email
- contact_email
- phone_number
- personal_identifier
- construct_id
- internal_batch_id
- protein_name

`sequence_hash` has a conditional policy rather than a flat policy:

- Public intake records must not contain `sequence_hash`, because an unsalted value derived directly from raw biological material can function as a re-identification proxy.
- Internal/private artifacts may use a salted HMAC fingerprint only when it is not co-transmitted with `raw_sequence`.
- Public intake records should use `design_package_id` as the linkage key.
- `manifest_digest` is different from `sequence_hash`: it is an integrity checksum for a non-sensitive manifest only, with scope limited to `manifest_only`, and must not cover raw biological material or any biological-material-derived fingerprint.

## Construct and Protein Identifier Rule

Do not use the label `Construct ID` in this scaffold. Use only `Non-confidential construct alias` with internal field name `non_confidential_construct_alias`.

This field must never contain internal batch IDs, customer construct IDs, plasmid IDs, proprietary construct names, unpublished construct-identifying labels, or sequence-derived identifiers.

Do not use the label `Protein name` as a default public field. Use `Protein class`, such as secreted enzyme, antigen, antibody fragment, reporter, cytokine/growth factor, membrane protein, or other.

## Coarse-Graining Rules

Public and curated records should use coarse, non-confidential categories wherever possible.

Approximate yield ranges:

- not_reported
- below_detection
- lt_0_01_mg_g_fw
- 0_01_to_0_1_mg_g_fw
- 0_1_to_1_mg_g_fw
- 1_to_5_mg_g_fw
- gt_5_mg_g_fw
- other_coarse_range

Replicate categories:

- not_reported
- single_observation
- 2-3 replicates
- 4-5 replicates
- gt_5 replicates

Comparison result categories:

- improved
- equivalent
- reduced
- inconclusive
- no_control
- not_reported

Expression result categories:

- detected
- not_detected
- weak
- strong
- inconclusive
- not_reported

Do not publish exact confidential process parameters, detailed unpublished assay conditions, institution names, or precise batch-specific identifiers.
