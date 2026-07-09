You are operating inside `/data/strategy/flwc`, the FLWC B0 fixture-only typed schema package repo.

Authority boundary:
- Use only the accepted source-authority docs in `docs/source_authority/`.
- Keep work fixture-only and synthetic-only.
- Do not ingest real financial sources.
- Do not call vendor APIs, paid data sources, browsers, web scraping, DuckDB canonical DBs, market-data services, or live runtimes.
- Do not request, read, print, or store secrets, browser sessions, tokens, SSH private keys, API keys, broker keys, or model-provider credentials.
- Do not add trading, order intent, position sizing, scanner, broker, or execution fields.
- Raw LLM output has no truth authority.

Task:
1. Inspect the current scaffold.
2. Strengthen the dataclass/schema scaffolding for A2-A5 fixture contracts.
3. Improve deterministic validators for synthetic fixture packages.
4. Add or improve standard-library unit tests only.
5. Keep dependencies minimal; do not install packages unless explicitly authorized.
6. Run `PYTHONPATH=src python3 -m unittest discover -s tests/unit`.
7. Summarize changes and non-claims.

Acceptance:
- All tests pass.
- No real source ingestion.
- No model calls beyond this Codex coding session.
- No production/runtime/live-trading/market-data authority claims.
