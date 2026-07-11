# FLWC Repository Agent Instructions

This repository is part of FLWC-QEP: the Financial LLM Wiki Compiler engineering program.

## Authority

Chief Engineer final verdict is required for node acceptance.

Codex summaries, local test passes, CI passes, GitHub checks, push success, and local LLM outputs are evidence only. They are not final acceptance.

Commander owns sensitive authorization surfaces. The FLWC Chief Engineer owns node boundaries, technical verdicts, acceptance criteria, non-claim preservation, and next-node prompts.

## Source Authority

Accepted source authority documents under `docs/source_authority/` are read-only by default.

Do not modify `docs/source_authority/` unless a named docs-only amendment node explicitly authorizes that mutation.

If repository comments, implementation details, tests, or generated artifacts conflict with accepted source authority documents, stop and report HOLD rather than silently choosing one.

## Default Forbidden Surfaces

Unless a named FLWC node explicitly authorizes the surface, do not open or implement:

- real source ingestion
- vendor API access
- paid source access
- web scraping
- browser profile, cookie, session, or token access
- secret migration or secret inspection
- model calls or local LLM calls
- raw LLM output as truth authority
- DuckDB canonical seed
- market-data authority cutover
- database authority
- runtime service
- FLWC Console real service on port 18110
- persistent LLM service
- production service
- live trading
- market scanner
- broker, execution, or order intent
- position sizing
- external consumer docking
- hot-path runtime kernel
- automated mutation of canonical ledgers

## Secrets

Never read, print, commit, log, screenshot, copy, or place in prompts or artifacts:

- API keys
- vendor tokens
- model-provider credentials
- broker or exchange credentials
- SSH private keys
- browser cookies, sessions, or tokens
- Codex authentication files
- signing keys
- environment secret values

Allowed evidence is limited to metadata such as file existence, mode, owner, size, public-key fingerprint, public hashes, and redacted command lines when a node explicitly asks for such evidence.

## Codex Operating Rules

Codex A may implement only inside the prompt boundary.

Codex B is read-only unless explicitly reassigned by a later Chief Engineer prompt.

Codex must not by default:

- install dependencies
- fetch, pull, push, merge, rebase, reset, clean, checkout, or switch branches
- configure remotes
- start services
- use network access
- call models or local LLMs
- inspect secrets
- alter source authority docs
- claim production, runtime, market-data, or trading readiness

## Testing and Evidence

A passing test suite is evidence, not acceptance.

A node cannot be accepted from chat summary alone, Codex summary alone, CI pass alone, or GitHub push alone.

Non-trivial nodes must preserve explicit non-claims and provide bounded evidence for changed files, tests, validation results, forbidden-surface checks, and residual risks.

## FLWC Non-Claim Baseline

FLWC compiles financial text knowledge. It does not trade, execute, route orders, size positions, act as a scanner, or decide external consumer admission.

Unless a later named node explicitly authorizes otherwise, this repository remains fixture-only / typed-schema / deterministic-validator / synthetic-fixture development for current B-series work.

Current default non-claims:

- not production-ready
- not live-trading-ready
- not market-data authority
- not real-source-ingestion authority
- not vendor-API authority
- not paid-source authority
- not web-scraping authority
- not model-output truth authority
- not runtime service authority
- not FLWC Console service authority
- not external consumer docking authority
- not trading authority
- not scanner authority
- not order-intent authority
- not position-sizing authority
- not broker-integration authority
