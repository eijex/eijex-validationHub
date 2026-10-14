# Optional shared PostgreSQL adapter

The default registry has no network connection or ORM dependency. The opt-in
`postgres` extra supports reviewed, minimal permissioned measurements in the
shared EIJEX schema. It does not approve, publish, or certify evidence.

Build the independently versioned `eijex-db-core` wheel and supply it to pip:

```powershell
pip install --find-links PATH_TO_APPROVED_WHEEL_BUNDLE ".[postgres,dev]"
```

The extra pins `eijex-db-core==0.1.2`; this wheel is not assumed to exist on PyPI.
No workstation file URL is embedded. Default scaffold installation needs no wheel.

Set `VALIDATIONHUB_DATABASE_URL` explicitly only for a provisioned permissioned
PostgreSQL database. Apply `python -m eijex_db_core.migrate upgrade head` using its
explicit `EIJEX_DATABASE_URL`; schema head is `b331f0a6d9c1`. Importing the adapter
does not create an engine, inspect credentials, or connect to a server.

`ingest_wetlab_csv` requires registered `operator_id`, canonical `AssayType`,
registered candidate identities for candidate arms, explicit role/type/unit and
finite nonnegative measurement values. Zero is retained. Unknown fields are
rejected; raw sequences and identifying free-text metadata are not accepted.
The transaction rolls back the entire batch on an invalid FK or write failure.

Tests use only `EIJEX_TEST_DATABASE_URL` on localhost with a database name ending
in `_test`, pinned migrations and an outer rollback transaction. They never fall
back to `DATABASE_URL`, create a competing schema, or modify a production DB.
