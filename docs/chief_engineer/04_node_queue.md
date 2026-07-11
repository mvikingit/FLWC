# FLWC Node Queue

Completed current node:

- `FLWC_B1_SOURCE_LICENSE_SCHEMA_FIXTURE_EXPANSION_V1`
- Status: accepted and pushed to remote main `cb8980280f3687f5e2d33addfc3c376c196d5df8`.
- Scope: fixture-only A2-derived source/license schema, validator, fixture builder, and test expansion.

Next candidate:

- `FLWC_B1_RAW_EVIDENCE_VAULT_SOURCE_DOCUMENT_INDEX_FIXTURE_EXPANSION_V1`
- Status: recommended_only; not_started; not_authorized until Chief Engineer issues the next Codex prompt.
- Purpose: next B1-series fixture-only expansion for raw evidence vault and source document index contracts.
- Boundary: synthetic_fixture_only; no real source access; no source ingestion; no model call; no DuckDB seed; no runtime service; no console service; no trading/scanner/order/broker/position sizing.

Future:

- A/B extensions only after source authority.
- Validator and fixture expansion only inside explicitly opened source-authority scope.
- Runtime, console, external docking, DuckDB seed, market-data authority, and trading-adjacent work remain closed unless a future accepted source-authority node opens them.

Explicit hold:

- Real source ingestion is not authorized.
