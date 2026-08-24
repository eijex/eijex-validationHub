# MCP Context

ValidationHub is a private evidence-registry scaffold for FactorForge wet-lab feedback.

This scaffold does not deploy an MCP server, connect to external services, connect to Neon/Postgres, or process real data.

Any future MCP/data-boundary integration must preserve:

- Private-by-default storage.
- No patient data.
- No confidential partner/customer data.
- No raw sequence storage.
- Manual public publication only.
