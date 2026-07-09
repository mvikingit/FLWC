# WS-FLWC Engineering Constitution

**Document ID:** `WS-FLWC-ENGINEERING-CONSTITUTION-STANDALONE-2026-06-13`  
**Project:** `FLWC — Financial LLM Wiki Compiler`  
**Class:** highest engineering constitution / source-authority baseline / docs-only  
**Prepared for:** Commander  
**Prepared by:** FLWC Chief Engineer  
**Date:** 2026-06-13  
**Status:** standalone FLWC constitution / pre-development baseline  
**Current development posture:** not started  
**Current runtime posture:** not authorized by this document  
**Current external docking posture:** contract-only / consumer-defined / not runtime  

---

## 0. Constitution Verdict

```text
VERDICT:
  STANDALONE_FLWC_ENGINEERING_CONSTITUTION_ACCEPTED_AS_BASELINE

SYSTEM_IDENTITY:
  FLWC is an independent Financial LLM Wiki Compiler project.

NOT_A_DERIVATIVE_SYSTEM:
  FLWC is not a submodule of any external quant system.
  FLWC does not inherit external system architecture, runtime modules, envelope sovereignty, source contracts, transport, or admission authority.

INHERITED_DISCIPLINE_ONLY:
  FLWC may inherit institutional work discipline, quality-first delivery law,
  fail-closed engineering posture, typed contract discipline,
  cold/hot separation discipline, non-claim ledger discipline,
  and node-based delivery discipline from prior institutional engineering practice.

AUTHORITY_ROOT:
  Commander owns FLWC project authorization.
  FLWC Chief Engineer owns FLWC architecture proposals, engineering discipline,
  node design, acceptance criteria, and technical risk classification.

CURRENT_AUTHORIZATION:
  docs-only / static-contract / constitution freeze only.

CURRENT_NOT_AUTHORIZED_BY_THIS_DOCUMENT:
  source ingestion
  vendor API calls
  paid data access
  web scraping
  model calls
  local LLM runtime
  database implementation
  production service
  live stream
  external consumer runtime docking
  trading / scanner / order / execution / position sizing
  hot-path runtime kernel
  automated mutation of canonical ledgers
```

---

## 1. Purpose

This document defines the highest engineering law for the FLWC development project.

FLWC is designed as a financial text knowledge compiler. Its long-term purpose is to convert authorized financial text evidence into auditable, versioned, bitemporal, structured knowledge artifacts that can support research, review, replay, narrative analysis, and future external consumer contracts.

FLWC is not defined as a trading system. FLWC is not an order system. FLWC is not a market scanner. FLWC is not an external consumer admission engine. FLWC is not a truth oracle. FLWC is not a generic note-taking app.

The system goal is:

```text
authorized financial text sources
  -> raw evidence vault
  -> source/license manifests
  -> atomic claim ledger
  -> financial event table
  -> entity/ticker links
  -> theme/narrative state
  -> conflict dossiers
  -> human-readable wiki export
  -> candidate evidence packages
  -> optional future Text-DNA candidate packs
  -> optional future external consumer adapters
```

---

## 2. Core Identity

```text
FLWC:
  Financial LLM Wiki Compiler

PRIMARY ROLE:
  external, autonomous, financial text knowledge compiler

PRIMARY OUTPUT:
  auditable financial knowledge artifacts and candidate evidence packages

PRIMARY OPERATING MODE:
  cold / nearline / post-close / research compiler

NOT PRIMARY OPERATING MODE:
  live trading runtime
  market scanner
  execution engine
  order intent generator
  external consumer admission authority
```

One-sentence identity:

```text
FLWC compiles financial text knowledge; it does not trade, execute, or decide external context admission.
```

---

## 3. Independence Law

FLWC is independent from external systems.

```text
FLWC_INDEPENDENCE_LAW:
  FLWC owns its own source manifests, license manifests, evidence vault,
  claim ledger, event table, narrative state, wiki export, validators,
  snapshots, and candidate evidence export contracts.

EXTERNAL_CONSUMER_LAW:
  Any external system may define what it is willing to accept from FLWC.
  That external ingress contract does not govern FLWC internals.

WIRE_LAW:
  A physical cable, file transfer, API, message bus, or shared medium carries data.
  It does not carry authority.

NO_EXTERNAL_MANAGER_LAW:
  External reviewers, consumers, counterpart systems, or integration engineers
  may review FLWC boundary contracts, but they do not manage FLWC internals
  unless Commander explicitly changes project governance.
```

Correct relationship with any external consumer:

```text
FLWC owns compilation.
External consumer owns admission.
The wire carries data, not authority.
```

---

## 4. Commander / FLWC Chief Engineer Authority

```text
COMMANDER:
  final project owner
  authorizes project start
  authorizes roadmap phase transitions
  authorizes real source access
  authorizes paid/vendor/API use
  authorizes model use
  authorizes runtime experiments
  authorizes external docking
  authorizes production-adjacent surfaces

FLWC_CHIEF_ENGINEER:
  maintains this constitution
  proposes architecture
  defines node boundaries
  defines source and artifact contracts
  defines failure/refusal law
  defines acceptance gates
  classifies risk
  rejects unsafe authority escalation
  prepares docs/code delivery packages for Commander review

EXTERNAL_CONSUMER_REVIEWER:
  may define consumer-side accepted input contracts
  may reject FLWC outputs for that consumer
  may request adapter fields
  may audit boundary claims
  may not control FLWC internals by default
```

---

## 5. Delivery Discipline

```text
DELIVERY_DISCIPLINE:
  Quality first.
  Do not rush implementation for progress optics.
```

Every roadmap node or macro-node must state:

```text
1. delivery_anchor
2. upstream_accepted_input
3. downstream_consumer
4. handoff_artifact
5. non_claims
```

Additional delivery law:

```text
DOCS_ONLY_NODE_VALIDITY:
  Docs-only nodes are valid when they freeze authority, contract, boundary,
  handoff, or RED-gate criteria.

CODE_NODE_LAW:
  Code nodes intended for future live-system path must become named,
  typed, tested, fail-closed, reusable, discoverable seams.

ONE_OFF_VALIDATION_LAW:
  One-off validation code must be explicitly marked as non-reusable authority.
```

A node is not accepted because it looks complete. It is accepted only if its handoff artifact matches its delivery anchor and its non-claims are explicit.

---

## 6. Quality Bar

FLWC must be engineered for institutional-grade reliability, even during research and docs-only phases.

```text
QUALITY_BAR:
  deterministic acceptance over subjective confidence
  source-first over summary-first
  auditability over convenience
  explicit schema over implicit convention
  fail-closed over silent repair
  bitemporal time law over single timestamp convenience
  signed snapshots over mutable folders
  candidate evidence over truth assertion
  cold artifacts over runtime shortcuts
  benchmark truth over performance optics
```

Rejected behavior:

```text
REJECT:
  undocumented schema drift
  implicit authority escalation
  silent timestamp repair
  unversioned model output
  raw LLM output as truth
  unlicensed text storage
  untracked source provenance
  mutable canonical ledgers without revision trail
  candidate confidence used as fact
  one-off scripts treated as system seams
  demo code used as production authority
```

---

## 7. System Layers

### 7.1 Canonical Layer Model

```text
Layer 0: Source Boundary
  source allowlist, license status, rights scope, source timestamp policy

Layer 1: Raw Evidence Vault
  immutable source references, hashes, raw storage pointers, revision metadata

Layer 2: Normalization Layer
  document normalization, language normalization, time normalization, dedup

Layer 3: Atomic Claim Layer
  source-backed atomic claims with lifecycle and provenance

Layer 4: Financial Event Layer
  typed financial events derived from claims and evidence

Layer 5: Narrative State Layer
  theme state, conflict dossiers, entity narrative state, open questions

Layer 6: Human Wiki Export Layer
  generated Markdown / review surface, not canonical truth

Layer 7: Candidate Evidence Export Layer
  fixed-schema candidate packages for downstream consumers

Layer 8: Optional Future Tensor Candidate Layer
  Text-DNA candidate packs, not runtime unless separately authorized

Layer 9: Optional External Consumer Adapter Layer
  consumer-specific mapping, not FLWC core authority
```

### 7.2 Cold / Runtime-Facing Separation

```text
COLD_LAYER_ALLOWED:
  Markdown
  JSON / JSONL
  DuckDB
  SQLite / Postgres, if later authorized
  Parquet
  generated wiki pages
  raw evidence manifests
  audit notebooks
  vector/full-text/graph indexes for research and review

RUNTIME_FACING_REQUIREMENT_IF_FUTURE_AUTHORIZED:
  named schema
  typed structures
  fixed-width fields where possible
  finite numeric tensors
  bounded payload sizes
  explicit versioning
  fail-closed validators
  no raw text in hot payload
  no raw LLM output in hot payload
  no future outcome leakage
```

Markdown, notebook apps, JSON files, and databases may help humans review evidence. They are not by themselves canonical authority unless explicitly named as a canonical artifact with schema, manifest, hash, and acceptance gate.

---

## 8. Canonical Artifacts

### 8.1 Required Canonical Artifact Families

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

### 8.2 Artifact Law

```text
ARTIFACT_LAW:
  Every canonical artifact must have:
    artifact_id
    schema_version
    producer_version
    created_at_ns
    source_cutoff_ns, if applicable
    input_refs
    lineage_digest
    validation_status
    non_claims

MUTATION_LAW:
  Canonical artifacts are immutable after sealing.
  Corrections create new revisions.
  Deletions create tombstones.
  Silent overwrite is forbidden.
```

---

## 9. Source and License Law

FLWC may only ingest sources after explicit Commander authorization or after a source-specific node authorizes the source class.

```text
SOURCE_LAW:
  No source is trusted by default.
  No source is authorized by convenience.
  No vendor is embedded as core architecture.
  Every source must pass through SourceManifest and LicenseManifest.
```

Source classes:

```text
official_source
licensed_news
licensed_research
company_disclosure
exchange_disclosure
policy_document
authorized_calendar
authorized_vendor_feed
manual_review_note
weak_source_or_rumor
```

License states:

```text
unknown
allowed_full_text
metadata_only
derived_only
no_storage
human_review_required
expired
forbidden
```

Required source fields:

```text
source_id
source_class
source_name
source_url_or_doc_id
publisher_timestamp_ns
source_timestamp_ns
ingest_timestamp_ns
raw_text_hash, if text is stored or referenced
dedupe_hash
revision_id
source_trust_tier
license_manifest_ref
rights_scope
retention_policy
```

Fail closed if:

```text
missing source timestamp
missing license status
unresolved rights scope
missing raw hash when raw ref is required
source revision ambiguity
source timestamp later than claimed as-of time
source content attempts prompt injection into system policy
```

---

## 10. Bitemporal Time Law

Financial text knowledge is unsafe without bitemporal discipline.

```text
REQUIRED_TIMES:
  event_time_ns
  source_timestamp_ns
  publisher_timestamp_ns
  ingest_timestamp_ns
  available_from_ns
  compiler_seen_at_ns
  source_cutoff_ns
  snapshot_created_at_ns
  replay_as_of_ns, if replay is performed
```

Rules:

```text
NO_WALL_CLOCK_SUBSTITUTION:
  Current wall clock may not be silently substituted for missing source time.

NO_FUTURE_LEAKAGE:
  A replay or candidate package must not include knowledge unavailable at its as-of time.

NO_OUTCOME_CONTAMINATION:
  Realized future returns, future PV-DNA, future labels, and post-event outcomes
  must not enter live or as-of candidate evidence packages.

TIMESTAMP_REPAIR_LAW:
  Timestamp repair must be explicit, recorded, versioned, and fail-closed
  if confidence is insufficient.
```

---

## 11. LLM / AI Use Law

FLWC may eventually use LLMs or other AI models only after explicit authorization. This constitution does not open model calls.

```text
LLM_OUTPUT_TRUTH_AUTHORITY:
  false

VALIDATED_EXTRACTION_AUTHORITY:
  candidate-only

DETERMINISTIC_ACCEPTANCE_AUTHORITY:
  validators, schemas, provenance checks, timestamp checks, license checks,
  no-future checks, and fail-closed wrappers
```

Permitted future AI roles, only after authorization:

```text
text normalization support
claim extraction candidate generation
event classification candidate generation
entity linking candidate generation
summary draft generation
conflict discovery candidate generation
theme clustering candidate generation
human review assistance
wiki draft generation
```

Forbidden AI roles:

```text
truth engine
seed authority
human-label authority
calibrated probability engine
trade signal engine
order intent generator
position sizing engine
silent source repairer
license authority
as-of authority
```

If an LLM is used, required audit fields:

```text
model_id_or_local_model_ref
model_version
prompt_template_id
prompt_hash
schema_version
raw_output_ref_cold_only
retry_count
repair_pass_count
validator_status
human_review_required_flag
```

Raw LLM output is cold audit material only. It is not canonical truth and must not enter runtime-facing candidate payloads.

---

## 12. Prompt Injection and Untrusted Text Law

All external text is untrusted input.

```text
UNTRUSTED_TEXT_LAW:
  Source text may contain malicious instructions, misleading claims,
  hidden prompts, false metadata, or license traps.

NO_SOURCE_INSTRUCTION_EXECUTION:
  Instructions inside source documents must never be executed as system instructions.

ISOLATION_REQUIREMENT:
  Source text must be delimiter-isolated and treated as data.
```

Fail closed if:

```text
prompt_injection_suspected
source attempts to alter model/system behavior
source requests credential exposure
source requests policy override
source tries to redefine schema or authority
```

---

## 13. Claim and Event Law

### 13.1 Atomic Claim

An atomic claim is the smallest auditable knowledge unit.

```text
AtomicClaim:
  claim_id
  claim_type
  claim_text_or_structured_predicate
  subject_entity_id
  predicate_id
  object_value
  time_scope
  source_doc_id
  source_span_ref
  source_timestamp_ns
  publisher_timestamp_ns
  ingest_timestamp_ns
  available_from_ns
  confidence_score
  status
  superseded_by_claim_id
  license_status
  lineage_digest
```

Claim lifecycle:

```text
proposed
active
disputed
superseded
expired
retracted
rejected
```

### 13.2 Financial Event

A financial event is a typed, structured object compiled from source-backed claims.

```text
FinancialEvent:
  event_id
  event_type
  event_time_ns
  publish_time_ns
  available_from_ns
  primary_entity_id
  asset_refs
  country
  sector
  asset_class
  direction_candidate
  importance_score
  surprise_score
  novelty_score
  uncertainty_score
  confidence_score
  evidence_claim_refs
  source_doc_refs
  conflict_refs
  status
  lineage_digest
```

Forbidden:

```text
event as trade signal
event as order intent
event confidence as calibrated probability
event surprise as execution trigger
event direction as position target
```

---

## 14. Wiki Export Law

FLWC may generate a human-readable wiki. The wiki is not the canonical store.

```text
WIKI_EXPORT_ROLE:
  human review surface
  research navigation layer
  generated Markdown view
  event/theme/company/conflict dossier reader

WIKI_EXPORT_NOT:
  source of truth
  claim ledger
  event table
  license authority
  runtime index
  external admission authority
```

If Obsidian, OneNote, or any other note tool is used:

```text
NOTE_TOOL_LAW:
  note tools are optional human interfaces.
  note tools do not own canonical FLWC authority.
  generated pages may be read by humans.
  human notes must enter through review patch queue before becoming canonical.
```

---

## 15. Candidate Evidence Export Law

FLWC may export candidate evidence packages for downstream consumers. These packages are not accepted evidence until a downstream consumer validates and admits them.

```text
CANDIDATE_EVIDENCE_LAW:
  FLWC may produce candidates.
  Downstream consumers decide their own admission.
  Candidate confidence is metadata, not admission authority.
```

Minimum candidate properties:

```text
schema_version
candidate_contract_version
candidate_id
producer = FLWC
compiler_snapshot_id
candidate_sequence
event_time_ns
source_timestamp_ns
publisher_timestamp_ns
ingest_timestamp_ns
available_from_ns
source_cutoff_ns
candidate_build_as_of_ns
entity_refs
asset_refs
source_doc_id
raw_text_hash, if applicable
source_kind
source_trust_tier
source_manifest_ref
license_manifest_ref
license_status
rights_scope
atomic_claim_refs
financial_event_refs
theme_state_refs
conflict_refs
semantic_scores, if authorized
quality_flags
refusal_flags
lineage_digest
payload_policy
```

Payload policy:

```text
raw_text_in_runtime_payload = false
raw_llm_output_in_runtime_payload = false
full_rag_context_in_runtime_payload = false
future_outcome_in_payload = false
trade_signal_fields_present = false
order_intent_fields_present = false
position_target_fields_present = false
```

---

## 16. External Consumer Adapter Law

External consumers may require adapter-specific fields. Those requirements do not redefine FLWC internals.

```text
EXTERNAL_ADAPTER_LAW:
  Adapter contracts are boundary contracts.
  They translate FLWC candidate artifacts into a consumer-acceptable form.
  They do not create FLWC truth.
  They do not grant runtime or transport authority.
```

Adapter stages:

```text
FLWC canonical artifacts
  -> FLWC canonical evidence IR
  -> external consumer candidate package
  -> downstream validation/admission, outside FLWC authority
```

Forbidden:

```text
external adapter writes FLWC canonical ledger directly
external adapter mutates sealed snapshot
external adapter upgrades candidate into truth inside FLWC
external consumer requirement silently changes FLWC source law
```

---

## 17. Text-DNA Candidate Law

Text-DNA is a future optional compiled representation of financial text events. It is not a document index and not current runtime authority.

```text
TEXT_DNA_CURRENT_STATUS:
  candidate artifact only
  no runtime authorized
  no external hot-path authorized
```

If future runtime-facing Text-DNA is authorized, it must use typed, bounded, benchmarkable structures:

```text
text_event_fingerprints: float32[N, F]
bucket_offsets: int64[..., 2]
side_arrays: fixed-width structured arrays or numeric arrays
claim_ref_offsets: int64[N + 1]
claim_ref_ids: int64[M]
source_ref_ids: int64[M]
```

Rejected runtime-facing design:

```text
Markdown index
JSONL search
Python dict/list object stream
runtime DB scan
runtime string lookup loop
runtime RAG context mutation
unbounded payload
raw text vector payload
```

Benchmark law if runtime is ever authorized:

```text
benchmark required
warm-cache state declared
no disk IO in query path
no JSON parse in query path
no object iteration in query path
median/p95 reported
failure to run benchmark must output benchmark_not_accepted
```

---

## 18. Snapshot and Sealing Law

```text
SNAPSHOT_LAW:
  A FLWC snapshot is an immutable, signed, versioned compiler output.
```

Required snapshot fields:

```text
snapshot_id
created_at_ns
source_cutoff_ns
compiler_version
schema_versions
model_versions, if any
prompt_versions, if any
source_manifest_ref
license_manifest_ref
entity_map_version
input_artifact_refs
lineage_hash_tree
future_leakage_denial
no_trade_field_attestation
no_order_intent_attestation
signature
```

A snapshot must fail validation if:

```text
manifest missing
license manifest missing
lineage digest mismatch
schema version unknown
source cutoff missing
future outcome field present
trade or order field present
signature invalid
```

---

## 19. Validator Law

All canonical and candidate artifacts must pass validators before handoff.

Mandatory validator families:

```text
schema_version_validator
snapshot_integrity_validator
source_manifest_validator
license_manifest_validator
rights_scope_validator
timestamp_validator
lineage_digest_validator
entity_map_validator
claim_event_ref_validator
prompt_injection_flag_validator
no_future_outcome_validator
no_trade_field_validator
bounded_payload_validator
```

Never optional for candidate handoff:

```text
timestamp_validator
license_manifest_validator
lineage_digest_validator
no_future_outcome_validator
no_trade_field_validator
bounded_payload_validator
```

Validator output:

```text
ACCEPT
REJECT
HOLD_REVIEW
NEUTRALIZE
```

Silent repair is forbidden.

---

## 20. Failure / Refusal Law

```text
HARD_REJECT:
  schema invalid
  missing source_doc_id
  missing raw_text_hash when required
  missing source_timestamp_ns
  source_timestamp_ns > candidate_as_of_ns
  unresolved license
  forbidden license status
  signature invalid
  lineage digest mismatch
  future outcome present
  trade signal field present
  order intent field present
  raw LLM output in runtime-facing payload

NEUTRALIZE:
  stale source
  low confidence
  weak entity map
  insufficient source diversity
  duplicate evidence
  superseded claim

HOLD_REVIEW:
  high-impact conflict
  license ambiguity
  prompt injection suspected
  official/news mismatch
  entity/ticker ambiguity
  high-surprise low-verifiability event
```

Fail-closed means the system stops unsafe promotion. It does not mean the system must stop research review.

---

## 21. Security and Secret Law

```text
SECRET_LAW:
  Credentials, API keys, vendor tokens, paid-source access keys,
  model provider keys, and signing keys must never be stored in wiki pages,
  raw source text, notebook notes, generated Markdown, or prompt templates.
```

Forbidden:

```text
keys in repo
keys in Markdown
keys in Obsidian vault
keys in OneNote
keys in prompt files
keys in logs
keys in LLM context
keys in screenshots
```

Required future posture:

```text
secret manager or environment injection
least privilege
key rotation policy
audit log redaction
no secret echo in model output
```

---

## 22. Observability and Audit Law

Every non-trivial node must produce auditable outputs.

```text
AUDIT_OUTPUT_REQUIRED:
  run_id
  node_id
  input_refs
  output_refs
  schema_versions
  validator_summary
  rejection_summary
  warning_summary
  non_claims
  created_at_ns
```

No claim of success is valid without artifact evidence.

For benchmark nodes:

```text
BENCHMARK_AUDIT_REQUIRED:
  host_id or host_class
  dataset size
  dtype
  memory layout
  warm/cold state
  median latency
  p95 latency
  benchmark target
  benchmark_passed
  benchmark_not_accepted if not run
```

---

## 23. Current Non-Claim Ledger

```text
flwc_constitution_defined = true
flwc_project_development_started = false
flwc_source_ingestion_authorized = false
flwc_vendor_api_authorized = false
flwc_paid_source_access_authorized = false
flwc_web_scraping_authorized = false
flwc_model_call_authorized = false
flwc_local_llm_runtime_authorized = false
flwc_external_api_call_authorized = false
flwc_database_implementation_authorized = false
flwc_runtime_service_authorized = false
flwc_transport_authorized = false
flwc_external_consumer_docking_authorized = false
flwc_text_dna_runtime_authorized = false
flwc_trading_authority = false
flwc_scanner_authority = false
flwc_order_intent_authority = false
flwc_position_sizing_authority = false
flwc_production_ready = false
flwc_runtime_ready = false
flwc_hot_path_ready = false
```

This ledger may only be changed by an explicitly accepted node.

---

## 24. Roadmap Baseline

Every roadmap node below is preliminary. It opens no implementation authority unless Commander explicitly accepts the node.

| Node | Class | delivery_anchor | upstream_accepted_input | downstream_consumer | handoff_artifact | non_claims |
|---|---|---|---|---|---|---|
| `FLWC-A0` | docs-only | Freeze standalone constitution | Commander instruction | Commander / future FLWC nodes | `WS-FLWC Engineering Constitution` | no code, no runtime, no source ingest |
| `FLWC-A1` | docs-only | Freeze architecture blueprint | `FLWC-A0` | schema/design nodes | `FLWC architecture blueprint` | no implementation, no model call |
| `FLWC-A2` | docs-only | Define source/license manifest contracts | `FLWC-A1` | source adapter nodes | `SourceManifestV1`, `LicenseManifestV1` | no real source access |
| `FLWC-A3` | docs-only | Define raw evidence and claim/event schemas | `FLWC-A2` | compiler skeleton nodes | `RawEvidenceVaultManifestV1`, `AtomicClaimLedgerV1`, `FinancialEventTableV1` | no data ingestion |
| `FLWC-A4` | docs-only | Define candidate evidence package contract | `FLWC-A3` | adapter/export nodes | `FLWCCandidateEvidencePackageV1` | not accepted evidence, no consumer runtime |
| `FLWC-A5` | docs-only | Define validator and refusal law | `FLWC-A4` | all future code nodes | `Validator matrix and fail-closed policy` | no code yet |
| `FLWC-B0` | code-fixture only | Build reusable typed schema package | `FLWC-A5` | compiler fixture nodes | typed schema module + tests | fixture-only, no real data |
| `FLWC-B1` | code-fixture only | Build fixture compiler skeleton | `FLWC-B0` | validator nodes | deterministic fixture compiler | no model, no API, no vendor data |
| `FLWC-B2` | code-fixture only | Build validator suite | `FLWC-B1` | snapshot fixture nodes | validator outputs + tests | fixture-only, non-production |
| `FLWC-B3` | code-fixture only | Build sealed snapshot fixture | `FLWC-B2` | review/export nodes | sealed fixture snapshot | no real source claim |
| `FLWC-C0` | review gate | Authorize real source class, if any | prior accepted docs/code fixture | source adapter node | source authorization decision | default false |
| `FLWC-C1` | future code | Implement authorized source adapter | `FLWC-C0 = ACCEPT` | raw evidence pipeline | source adapter + tests | source-class-limited only |
| `FLWC-D0` | future review gate | Authorize model use, if any | accepted source/schema/validator baseline | model extraction node | model-use decision | default false |
| `FLWC-D1` | future code | Implement LLM-assisted candidate extraction | `FLWC-D0 = ACCEPT` | claim/event compiler | extraction module + audit | candidate-only, no truth authority |
| `FLWC-E0` | future docs/code | Wiki export surface | accepted claim/event artifacts | human reviewers | generated wiki vault | not canonical truth |
| `FLWC-F0` | future docs-only | Text-DNA candidate contract | accepted event table design | tensor candidate nodes | Text-DNA contract | no runtime |
| `FLWC-R0` | review gate | Runtime authorization review | mature offline system | Commander | runtime decision | default false |
| `FLWC-X0` | docs-only | External consumer adapter contract | accepted candidate contract | external consumer review | adapter contract | no external runtime |

---

## 25. Node Acceptance Template

Every future node prompt or delivery must include:

```text
NODE_ID:
NODE_CLASS:
DELIVERY_ANCHOR:
UPSTREAM_ACCEPTED_INPUT:
DOWNSTREAM_CONSUMER:
HANDOFF_ARTIFACT:
NON_CLAIMS:
AUTHORIZED_SURFACES:
FORBIDDEN_SURFACES:
VALIDATORS_REQUIRED:
TESTS_REQUIRED:
AUDIT_OUTPUTS_REQUIRED:
ROLLBACK_OR_REPAIR_POLICY:
ACCEPTANCE_CRITERIA:
```

No node may rely on implied authority from previous conversation language.

---

## 26. Artifact Naming and Versioning

```text
NAMING_LAW:
  All durable artifacts must include system prefix, artifact family,
  schema version, date or snapshot id, and status.
```

Examples:

```text
FLWCSourceManifestV1_2026-06-13.fixture.json
FLWCAtomicClaimLedgerV1_snapshot_0001.parquet
FLWCCandidateEvidencePackageV1_batch_0001.json
FLWCCompilerSnapshotV1_2026-06-13T160000Z.sealed/
```

Versioning:

```text
breaking schema change -> new schema version
non-breaking field addition -> minor schema revision
artifact correction -> new revision, not overwrite
experimental artifact -> explicit experimental tag
one-off artifact -> explicit non_reusable tag
```

---

## 27. Tooling Discipline

Tooling is subordinate to artifact law.

Allowed future categories after authorization:

```text
CLI tools
schema validators
fixture generators
snapshot sealers
wiki exporters
batch compilers
review dashboards
benchmark scripts
```

Tooling law:

```text
TOOLS_DO_NOT_CREATE_AUTHORITY:
  Tools emit evidence and artifacts.
  Authority comes from accepted schema, validators, tests, and Commander-approved node closure.
```

One-off scripts:

```text
ONE_OFF_SCRIPT_TAG_REQUIRED:
  non_reusable_authority = true
  not_a_system_seam = true
  not_future_runtime_path = true
```

---

## 28. Review Surface Law

Human review is required for ambiguous, high-impact, or low-verifiability evidence.

```text
HUMAN_REVIEW_REQUIRED_IF:
  unresolved license
  high-impact conflict
  prompt injection suspected
  source discrepancy
  low-verifiability high-surprise event
  entity/ticker ambiguity
  material timestamp repair
  model extraction uncertainty above threshold
```

Human notes are not canonical until accepted through patch queue.

```text
HUMAN_NOTE_LAW:
  human note -> review patch proposal -> validator -> accepted artifact revision
```

---

## 29. External Integration Law

Any external integration must be contract-first.

```text
EXTERNAL_INTEGRATION_SEQUENCE:
  docs-only boundary contract
  static schema
  fixture-only handoff
  validator proof
  offline snapshot proof
  runtime review gate
  explicit Commander authorization
```

Forbidden shortcuts:

```text
live feed before schema
transport before artifact contract
model call before model-use authorization
source access before license manifest
consumer docking before candidate contract
runtime before benchmark gate
```

---

## 30. Constitution Amendment Law

This constitution may be amended only by a named docs-only constitution amendment node.

```text
AMENDMENT_NODE_REQUIRED:
  node_id
  reason
  old text
  new text
  impact analysis
  affected artifacts
  non-claims
  Commander acceptance
```

No implementation node may silently alter constitutional law.

---

## 31. Carry-Forward Sentence

Use this sentence in future FLWC prompts:

> Treat FLWC as an independent Financial LLM Wiki Compiler. FLWC owns financial text compilation, source/license manifests, atomic claims, financial events, narrative state, wiki exports, candidate evidence packages, and sealed snapshots. This project inherits institutional engineering discipline and quality standards only, not any external system architecture or authority. Current status is constitution/docs-only. No source ingestion, model call, vendor API, runtime, transport, trading, scanner, order intent, production, or external docking is authorized unless a named FLWC node explicitly opens it.

---

## 32. One-Sentence Summary

**WS-FLWC is the standalone engineering constitution for building FLWC as a financial text knowledge compiler: source-first, license-aware, bitemporal, auditable, fail-closed, candidate-only, and independent from external systems.**
