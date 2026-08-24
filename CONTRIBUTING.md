# Contributing

This open-source repository accepts code, policy, schema, documentation, and
synthetic-test changes that preserve the permissioned-data boundary.

Do not commit raw survey exports, private records, rejected records, credentials, `.env` files, database URLs, patient data, submitter identity, respondent email addresses, proprietary constructs, raw sequence data, internal batch IDs, exact confidential process parameters, or confidential customer/partner information.

Public-facing validation summaries must be manually reviewed and copied only to FactorForge/VALIDATION.md when optional public-summary consent is present.

Run local checks before committing:

```powershell
python -m pytest
python -m ruff check .
```
