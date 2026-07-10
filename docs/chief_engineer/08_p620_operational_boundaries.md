# P620 Operational Boundaries

P620 posture:

- development and research workstation
- not production
- not live trading
- not market-data authority
- not runtime authority

Storage boundary:

- `/data` is the canonical development and artifact root for FLWC work.
- Current FLWC repository: `/data/strategy/flwc`.

Accepted routes and surfaces:

- Codex via `codex-lsdserv` / `18180`.
- GitHub via `github.com-p620-lsdserv443`.
- FLWC Console Chrome direct/no-proxy to `http://127.0.0.1:18110`.
- FLWC Console real service on 18110 is not accepted.

Local LLM roles:

- candidate generation only when a node authorizes it
- cold-audit only when a node authorizes it
- not truth authority
- not source authority
- not validator authority
- not Chief Engineer verdict authority

Secret boundary:

- no secrets in Git
- no secrets in logs
- no secrets in prompts
- no secrets in screenshots
- no secrets in LLM context
- no browser session/token migration
- no SSH private key exposure

No source ingestion, vendor API, paid source access, web scraping, DuckDB seed, runtime service, external docking, trading/scanner/order/position, broker, execution, or market-data authority is opened by this state pack.
