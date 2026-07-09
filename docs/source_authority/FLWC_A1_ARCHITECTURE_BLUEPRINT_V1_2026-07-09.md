# FLWC Architecture Blueprint V1

**Document ID:** `FLWC-A1-ARCHITECTURE-BLUEPRINT-V1-2026-07-09`  
**Project:** `FLWC — Financial LLM Wiki Compiler`  
**Node:** `FLWC-A1`  
**Class:** docs-only / architecture blueprint / no implementation  
**Prepared for:** Commander  
**Prepared by:** FLWC Chief Engineer  
**Status:** source-doc candidate  
**Upstream accepted input:** `FLWC-A0 / WS-FLWC Engineering Constitution`  
**Downstream consumer:** `FLWC-A2 Source/License Manifest Contracts`  
**Posture:** docs-only; no repo; no source ingestion; no model calls; no runtime service; no trading/scanner/order authority.

---

## 0. Executive Verdict

This document freezes the first architecture blueprint for FLWC as an independent Financial LLM Wiki Compiler.

```text
FLWC_A1_ARCHITECTURE_BLUEPRINT_PROPOSED = true
FLWC_A1_OPENS_IMPLEMENTATION = false
FLWC_A1_OPENS_REPO_BOOTSTRAP = false
FLWC_A1_OPENS_CODEX = false
FLWC_A1_OPENS_SOURCE_INGESTION = false
FLWC_A1_OPENS_MODEL_CALLS = false
FLWC_A1_OPENS_DATABASE_IMPLEMENTATION = false
FLWC_A1_OPENS_RUNTIME_SERVICE = false
FLWC_A1_OPENS_TRADING_SCANNER_ORDER_AUTHORITY = false
```

FLWC compiles authorized financial text evidence into auditable, bitemporal, versioned knowledge artifacts. It does not trade, execute, generate order intent, size positions, or act as a market-data authority.

---

## 1. Architecture Principles

```text
source-first over summary-first
license-aware before storage
bitemporal before narrative
claim/event schema before wiki
candidate evidence over truth assertion
validators over model confidence
sealed snapshots over mutable folders
cold compiler before runtime-facing export
explicit non-claims over implied readiness
```

Every downstream implementation must be derived from accepted source documents, typed schemas, deterministic validators, and artifact evidence.

---

## 2. Canonical Layer Architecture

```text
Layer 0: Source Boundary
  source allowlist
  license manifest
  rights scope
  retention policy
  source timestamp law
  source trust tier

Layer 1: Raw Evidence Vault
  immutable raw references
  raw text hash if storage is authorized
  source revision metadata
  prompt-injection flags
  dedupe hashes
  no silent overwrite

Layer 2: Normalization Layer
  text normalization
  language normalization
  time normalization
  entity string normalization
  source-span segmentation
  explicit timestamp repair only when authorized

Layer 3: Atomic Claim Layer
  source-backed atomic claims
  lifecycle: proposed / active / disputed / superseded / expired / retracted / rejected
  provenance references
  source span references
  license state carried forward

Layer 4: Financial Event Layer
  typed financial events derived from evidence-backed claims
  event_time / publish_time / available_from discipline
  entity / ticker / asset references
  conflict references
  no trade signal semantics

Layer 5: Narrative State Layer
  theme state
  entity narrative state
  conflict dossiers
  open questions
  source diversity and uncertainty flags

Layer 6: Human Wiki Export Layer
  generated Markdown / review surface
  not canonical truth
  not license authority
  not claim ledger

Layer 7: Candidate Evidence Export Layer
  fixed-schema candidate evidence package
  downstream consumers decide admission
  candidate confidence is metadata, not truth

Layer 8: Optional Future Text-DNA Candidate Layer
  typed bounded candidate representation only
  no hot-path runtime until explicit future gate

Layer 9: Optional Future External Consumer Adapter Layer
  adapter contract only
  external consumer owns admission
  wire carries data, not authority
```

---

## 3. Required Canonical Artifact Families

A future FLWC implementation must eventually support these artifact families, subject to later node acceptance:

```text
FLWCSourceManifestV1
FLWCLicenseManifestV1
FLWCRawEvidenceVaultManifestV1
FLWCSourceDocumentIndexV1
FLWCAtomicClaimLedgerV1
FLWCFinancialEventTableV1
FLWCEntityTickerLinkTableV1
FLWCThemeNarrativeStateV1
FLWCConflictDossierV1
FLWCHumanReviewPatchQueueV1
FLWCCandidateEvidencePackageV1
FLWCCompilerSnapshotV1
FLWCLineageHashTreeV1
FLWCWikiExportV1
FLWCTextDNACandidatePackV1, future optional
FLWCExternalConsumerAdapterV1, future optional
```

A1 does not define final schemas. It assigns responsibility. A2-A5 must freeze schema contracts and validator/refusal law before any B0 code fixture.

---

## 4. Major Components

### 4.1 Source Registry

Responsibility:

```text
record source identity
source class
publisher timestamp policy
source trust tier
license manifest reference
rights scope
retention policy
```

Non-claims:

```text
does not authorize source access
does not fetch data
does not scrape web
does not store full text unless later authorized
```

### 4.2 License Registry

Responsibility:

```text
license state
rights scope
storage allowance
derived-only status
retention rules
expiration / revocation
human review flags
```

Fail closed on:

```text
unknown license where storage is requested
forbidden license
unresolved rights scope
expired access
```

### 4.3 Raw Evidence Vault

Responsibility:

```text
immutable evidence references
raw hash
revision hash
source-span addressing
dedupe records
prompt-injection flags
```

Storage modes:

```text
metadata_only
derived_only
allowed_full_text
no_storage
human_review_required
```

### 4.4 Normalization Engine

Responsibility:

```text
normalize document structure
normalize timestamps
normalize language variants
normalize entity strings
map source spans
deduplicate
```

Non-claim:

```text
normalization does not create truth
```

### 4.5 Atomic Claim Compiler

Responsibility:

```text
produce candidate or accepted atomic claims from source-backed spans
maintain lifecycle
carry provenance
carry license and timestamp fields
```

Required downstream validators:

```text
schema_version_validator
source_ref_validator
license_validator
timestamp_validator
lineage_validator
prompt_injection_guard
```

### 4.6 Financial Event Compiler

Responsibility:

```text
compile typed financial events from accepted claim sets
link events to entities/assets/themes
record conflict and uncertainty state
```

Forbidden semantics:

```text
event as trade signal
event as order intent
event confidence as calibrated probability
event direction as position target
```

### 4.7 Narrative and Conflict Compiler

Responsibility:

```text
track theme state
track entity narrative state
compile conflict dossiers
surface open questions
prepare human-review routes
```

### 4.8 Wiki Exporter

Responsibility:

```text
generate human-readable Markdown pages
render source-backed summaries
render conflict dossiers
render entity/theme/event pages
```

Non-claim:

```text
wiki is not canonical store
wiki is not source of truth
wiki is not runtime index
```

### 4.9 Candidate Evidence Packager

Responsibility:

```text
produce fixed-schema candidate evidence packages
include lineage digest
include timestamp and license fields
include payload policy flags
exclude raw text from runtime-facing payload
exclude trade/order/position fields
exclude future outcomes
```

### 4.10 Snapshot Sealer

Responsibility:

```text
seal compiler output
record schema versions
record source cutoff
record input refs
record lineage hash tree
record no-future and no-trade attestations
```

### 4.11 Validator Suite

Responsibility:

```text
schema validation
source manifest validation
license validation
timestamp validation
lineage validation
entity map validation
claim/event reference validation
prompt-injection flag validation
no-future validation
no-trade-field validation
bounded payload validation
```

Validator outputs:

```text
ACCEPT
REJECT
HOLD_REVIEW
NEUTRALIZE
```

---

## 5. AI / LLM Role Boundary

FLWC may use AI only after a future named node authorizes model use.

Permitted future AI roles, after authorization:

```text
candidate extraction
candidate normalization
candidate event classification
candidate entity linking
candidate conflict discovery
candidate wiki drafting
human review assistance
```

Forbidden AI roles:

```text
truth engine
license authority
source authority
as-of authority
trade signal engine
order intent generator
position sizing engine
silent repair engine
```

All raw LLM outputs are cold audit material only and must be validated before downstream use.

---

## 6. P620 Development Mapping

P620 accepted surfaces usable by later authorized nodes:

```text
/data as canonical development and artifact root
/data/strategy as future repo root
/data/artifacts as artifact evidence root
/data/models as local model storage root
Chrome FLWC Console dedicated profile opening http://127.0.0.1:18110
ChatGPT Chrome dedicated profile preserved through 127.0.0.1:18180
local LLM harness available as candidate-only development tooling
```

P620 surfaces not opened by A1:

```text
repo bootstrap
Node/npm/Vite implementation
Codex implementation prompt
DuckDB canonical seed
market-data authority cutover
production service
live trading runtime
scanner runtime
external docking
```

---

## 7. Directory Intent, Future Only

Future repo candidate:

```text
/data/strategy/flwc
```

Future source-doc archive candidate:

```text
/data/strategy/flwc/docs/source_authority/
```

Future fixture-only code layout candidate, only after A5/B0 authorization:

```text
/data/strategy/flwc/
  pyproject.toml
  README.md
  docs/
  src/flwc/
    schemas/
    validators/
    manifests/
    compiler/
    export/
  tests/
    fixtures/
    unit/
```

This is not authorization to create the repo.

---

## 8. Roadmap Gate

Required sequence:

```text
FLWC-A0 = constitution accepted
FLWC-A1 = architecture blueprint
FLWC-A2 = source/license manifest contracts
FLWC-A3 = raw evidence + claim/event schemas
FLWC-A4 = candidate evidence package contract
FLWC-A5 = validator/refusal matrix
FLWC-B0 = typed schema package, fixture-only code
```

A1 does not skip A2-A5.

---

## 9. A1 Acceptance Criteria

A1 can be accepted if:

```text
architecture layers are explicit
component responsibilities are explicit
source/license law remains upstream authority
AI/LLM boundary remains candidate-only
P620 mapping is clear but does not open implementation
repo/Codex/code/runtime non-claims are explicit
downstream A2-A5 sequence is preserved
artifact sha256 is recorded
Commander accepts the document as source authority
```

---

## 10. Non-Claims

```text
flwc_project_development_started = false
flwc_repo_created = false
flwc_code_implemented = false
flwc_codex_started = false
flwc_model_call_authorized = false
flwc_local_llm_runtime_authorized_by_A1 = false
flwc_source_ingestion_authorized = false
flwc_vendor_api_authorized = false
flwc_paid_source_access_authorized = false
flwc_web_scraping_authorized = false
flwc_database_implementation_authorized = false
flwc_runtime_service_authorized = false
flwc_external_consumer_docking_authorized = false
flwc_trading_authority = false
flwc_scanner_authority = false
flwc_order_intent_authority = false
flwc_position_sizing_authority = false
flwc_production_ready = false
flwc_live_trading_ready = false
```

---

## 11. Carry-Forward Sentence

Treat FLWC as a cold/nearline financial text knowledge compiler. Freeze source/license, evidence, claim/event, candidate package, validator, and snapshot contracts before code. Use LLMs only as candidate generators after explicit authorization. Use P620 as a development/research workstation, not as production/runtime authority.
