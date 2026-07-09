# FLWC Candidate Evidence Package Contract V1

**Document ID:** `FLWC-A4-CANDIDATE-EVIDENCE-PACKAGE-CONTRACT-V1-2026-07-09`  
**Project:** `FLWC — Financial LLM Wiki Compiler`  
**Node:** `FLWC-A4`  
**Class:** docs-only / candidate evidence package contract / no accepted evidence admission / no consumer runtime  
**Prepared for:** Commander  
**Prepared by:** FLWC Chief Engineer  
**Status:** source-doc candidate  
**Upstream accepted input:** `FLWC-A3 Raw Evidence + Claim/Event Schemas V1`  
**Downstream consumer:** `FLWC-A5 Validator / Refusal Matrix`  
**Posture:** docs-only; no repo; no real source access; no source ingestion; no web scraping; no vendor API; no paid source access; no model calls; no database implementation; no runtime service; no external consumer docking; no trading/scanner/order authority.

---

## 0. Executive Verdict

This document freezes the first FLWC candidate evidence package contract baseline.

```text
FLWC_A4_CANDIDATE_EVIDENCE_PACKAGE_CONTRACT_PROPOSED = true
FLWC_A4_OPENS_ACCEPTED_EVIDENCE_ADMISSION = false
FLWC_A4_OPENS_CONSUMER_RUNTIME = false
FLWC_A4_OPENS_EXTERNAL_DOCKING = false
FLWC_A4_OPENS_REAL_SOURCE_ACCESS = false
FLWC_A4_OPENS_SOURCE_INGESTION = false
FLWC_A4_OPENS_VENDOR_API = false
FLWC_A4_OPENS_PAID_SOURCE_ACCESS = false
FLWC_A4_OPENS_WEB_SCRAPING = false
FLWC_A4_OPENS_REPO_BOOTSTRAP = false
FLWC_A4_OPENS_CODEX = false
FLWC_A4_OPENS_MODEL_CALLS = false
FLWC_A4_OPENS_DATABASE_IMPLEMENTATION = false
FLWC_A4_OPENS_RUNTIME_SERVICE = false
FLWC_A4_OPENS_TRADING_SCANNER_ORDER_AUTHORITY = false
```

A4 defines how FLWC packages source-backed, validator-routed candidate knowledge for later review or downstream consumers. A candidate evidence package is not accepted evidence. It is not truth authority. It is not a trade signal. It is not order intent. It is not position sizing. It is not runtime admission authority.

---

## 1. Contract Principles

```text
candidate package over accepted evidence
source/license carry-forward over implicit provenance
as-of eligibility before export
bounded payload before transport
raw-text denial before runtime-facing fields
lineage digest before handoff
refusal flags over silent omission
consumer admission remains outside FLWC core
no trade/order/position semantics
no future outcome leakage
```

A4 is a boundary contract. It does not decide what any downstream consumer must accept.

---

## 2. Upstream A3 Carry-Forward

A4 consumes these A3 artifacts and laws:

```text
FLWCRawEvidenceVaultManifestV1
FLWCRawEvidenceRecordV1
FLWCSourceDocumentIndexV1
FLWCAtomicClaimLedgerV1
FLWCAtomicClaimV1
FLWCFinancialEventTableV1
FLWCFinancialEventV1
A3 validator matrix
A2 source/license manifest law
bitemporal time law
no-trade/no-order/no-position law
non-claims law
```

Every candidate package must preserve:

```text
source_manifest_refs
license_manifest_refs
license_state_summary
rights_scope_summary
raw_storage_policy_summary
source_trust_tier_summary
prompt_injection_flags
source_cutoff_ns
candidate_build_as_of_ns
lineage_digest
payload_policy
non_claims
```

---

## 3. FLWCCandidateEvidencePackageV1

Purpose:

```text
Represent a bounded, manifest-backed candidate evidence package for human review, wiki review surfaces, or future external consumer adapters.
```

Package-level minimum required fields:

```yaml
schema_version: FLWCCandidateEvidencePackageV1
candidate_package_id: string
candidate_contract_version: string
producer_id: string
producer_version: string
compiler_snapshot_ref: string | null
candidate_build_as_of_ns: int
source_cutoff_ns: int
created_at_ns: int
package_sequence: int
package_scope: enum
package_status: enum
candidate_count: int
candidate_digest: string
input_raw_evidence_vault_manifest_refs: list[string]
input_raw_evidence_record_refs: list[string]
input_source_document_index_refs: list[string]
input_claim_ledger_refs: list[string]
input_event_table_refs: list[string]
source_manifest_refs: list[string]
license_manifest_refs: list[string]
license_state_summary: map[string, string]
rights_scope_summary: map[string, string]
raw_storage_policy_summary: map[string, string]
payload_policy: FLWCCandidatePayloadPolicyV1
refusal_summary_ref: string | null
validator_summary_ref: string | null
lineage_digest: string
validation_status: enum
non_claims: list[string]
```

Allowed `package_scope` values:

```text
synthetic_fixture_only
human_review_candidate
wiki_review_candidate
external_consumer_candidate_future_authorization_required
snapshot_export_candidate
quarantine_review_candidate
```

Allowed `package_status` values:

```text
proposed
hold_review
validated_candidate
rejected
neutralized
superseded
expired
```

Mandatory package non-claims:

```text
not_accepted_evidence
not_truth_authority
not_source_authority
not_license_authority
not_runtime_authority
not_external_admission_authority
not_trade_signal
not_order_intent
not_position_sizing
not_market_data_authority
```

---

## 4. FLWCCandidateEvidenceRecordV1

Purpose:

```text
Represent one bounded candidate evidence record inside a package.
```

Minimum required fields:

```yaml
schema_version: FLWCCandidateEvidenceRecordV1
candidate_id: string
candidate_version: string
candidate_sequence: int
candidate_kind: enum
candidate_status: enum
candidate_build_as_of_ns: int
source_cutoff_ns: int
event_time_ns: int | null
source_timestamp_ns: int | null
publisher_timestamp_ns: int | null
ingest_timestamp_ns: int
available_from_ns: int
compiler_seen_at_ns: int
primary_entity_id: string | null
entity_refs: list[string]
asset_refs: list[string]
country_or_region: string | null
sector: string | null
asset_class: string | null
source_document_refs: list[string]
source_span_refs: list[string]
raw_evidence_refs: list[string]
atomic_claim_refs: list[string]
financial_event_refs: list[string]
theme_state_refs: list[string]
conflict_refs: list[string]
source_manifest_refs: list[string]
license_manifest_refs: list[string]
license_state_summary: map[string, string]
rights_scope_summary: map[string, string]
source_trust_tier_summary: map[string, string]
prompt_injection_flags: list[string]
quality_flags: list[string]
refusal_flags: list[string]
semantic_scores: map[string, float] | null
candidate_payload: object
payload_policy: FLWCCandidatePayloadPolicyV1
lineage_digest: string
validation_status: enum
validator_summary_ref: string | null
non_claims: list[string]
```

Allowed `candidate_kind` values:

```text
raw_evidence_candidate
atomic_claim_candidate
financial_event_candidate
entity_asset_link_candidate
narrative_state_candidate
conflict_dossier_candidate
wiki_review_candidate
text_dna_candidate_future_authorization_required
external_adapter_candidate_future_authorization_required
other
```

Allowed `candidate_status` values:

```text
proposed
validated_candidate
hold_review
rejected
neutralized
superseded
expired
quarantined
```

Rules:

```text
validated_candidate means schema and validator gates passed for candidate export only.
validated_candidate does not mean accepted evidence.
hold_review must preserve review reason.
rejected and neutralized records must preserve refusal_flags.
```

---

## 5. FLWCCandidatePayloadPolicyV1

Purpose:

```text
Declare payload safety constraints that every package and record must obey.
```

Minimum required fields:

```yaml
schema_version: FLWCCandidatePayloadPolicyV1
raw_text_in_payload: boolean
raw_llm_output_in_payload: boolean
full_rag_context_in_payload: boolean
future_outcome_in_payload: boolean
trade_signal_fields_present: boolean
order_intent_fields_present: boolean
position_target_fields_present: boolean
broker_or_execution_fields_present: boolean
runtime_payload_bounded: boolean
max_payload_bytes: int
allowed_payload_classes: list[string]
redaction_policy_ref: string | null
```

Default required values:

```text
raw_text_in_payload = false
raw_llm_output_in_payload = false
full_rag_context_in_payload = false
future_outcome_in_payload = false
trade_signal_fields_present = false
order_intent_fields_present = false
position_target_fields_present = false
broker_or_execution_fields_present = false
runtime_payload_bounded = true
```

Allowed payload classes:

```text
manifest_refs_only
claim_event_refs_only
bounded_derived_fields
bounded_review_summary
validator_flags_only
synthetic_fixture_payload
```

Hard reject if:

```text
raw text appears in runtime-facing payload
raw LLM output appears in candidate payload
future outcome appears in candidate payload
trade signal field appears
order intent field appears
position target field appears
broker/execution field appears
payload size is unbounded
payload policy is missing
```

---

## 6. Candidate Payload Content Rules

Candidate payloads may include only bounded derived fields or references that are allowed by source/license policy.

Permitted future payload examples, subject to validators:

```text
atomic_claim_ref
financial_event_ref
source_document_ref
source_span_ref
raw_evidence_ref
bounded structured predicate
bounded event descriptor
bounded conflict summary
quality flags
refusal flags
lineage digest
```

Forbidden payload examples:

```text
full source text
full RAG context
browser/session/token material
credentials
raw model output
future realized return
future label
trade signal
target position
order action
broker routing field
```

---

## 7. As-Of and Replay Eligibility

A candidate package is replay-eligible only if:

```text
candidate_build_as_of_ns is present.
source_cutoff_ns is present.
available_from_ns for every included record is <= candidate_build_as_of_ns.
source_timestamp_ns is not later than replay_as_of_ns when replay is performed.
future outcome fields are absent.
lineage_digest covers all included refs.
```

Fail closed if:

```text
available_from_ns > candidate_build_as_of_ns
source_timestamp_ns > replay_as_of_ns
missing source_cutoff_ns
missing lineage_digest
future outcome contamination detected
```

---

## 8. Source / License Carry-Forward

Every package and record must carry source/license references forward from A2 and A3.

Required fields:

```text
source_manifest_refs
license_manifest_refs
license_state_summary
rights_scope_summary
raw_storage_policy_summary
source_trust_tier_summary
prompt_injection_flags
retention_policy_summary, package-level if applicable
```

Fail closed if:

```text
source manifest missing
license manifest missing
source/license mismatch
forbidden license
unknown license with raw or full text requested
rights scope unknown for external-consumer candidate
runtime payload policy permits raw text
credential value appears in any field
```

---

## 9. Refusal and Review Routing Fields

Required review/refusal fields where applicable:

```text
review_status
review_reason
review_owner
refusal_flags
validator_summary_ref
refusal_summary_ref
conflict_refs
prompt_injection_flags
```

Allowed `review_status` values:

```text
not_required
hold_review
human_review_required
accepted_after_review_future_patch_node_required
rejected_after_review
neutralized_after_review
```

Human notes remain non-canonical unless accepted by a future review patch queue node.

---

## 10. Minimal A4 Validator Set

A4 defines minimum validators for candidate package contract compliance. A5 will freeze the full validator/refusal matrix.

Required A4 validators:

```text
candidate_package_schema_validator
candidate_record_schema_validator
payload_policy_validator
source_manifest_ref_validator
license_manifest_ref_validator
source_license_pairing_validator
rights_scope_validator
raw_storage_policy_validator
timestamp_validator
available_from_asof_validator
lineage_digest_validator
raw_text_payload_denial_validator
raw_llm_output_denial_validator
future_outcome_denial_validator
no_trade_field_validator
no_order_intent_validator
no_position_target_validator
credential_leak_validator
prompt_injection_flag_validator
non_claims_validator
bounded_payload_validator
```

Validator outputs:

```text
ACCEPT
REJECT
HOLD_REVIEW
NEUTRALIZE
```

---

## 11. A4 Refusal Baseline

Hard reject:

```text
schema invalid
payload policy missing
source manifest missing
license manifest missing
source/license mismatch
forbidden license
unknown license with raw/full text requested
raw text in payload
raw LLM output in payload
full RAG context in payload
future outcome in payload
trade signal field present
order intent field present
position target field present
broker/execution field present
credential value detected
lineage digest mismatch
unbounded payload
missing non_claims
```

Hold review:

```text
license_state = unknown
license_state = human_review_required
rights_scope = unknown
timestamp ambiguous
publisher identity ambiguous
entity/ticker mapping ambiguous
high-impact conflict
prompt injection suspected
weak source or rumor
external consumer candidate without explicit consumer adapter contract
```

Neutralize:

```text
duplicate candidate
superseded candidate
stale source
low source diversity
weak entity map
low-verifiability high-surprise candidate
```

---

## 12. Synthetic Fixture Policy

A4 may use synthetic fixture candidate packages only for contract and validator testing.

Synthetic fixture requirements:

```text
package_scope = synthetic_fixture_only
candidate_kind may use any A4-defined kind for schema tests
source_class = synthetic_fixture
license_state = allowed_full_text
rights_scope = research_internal_only
raw_storage_policy = allowed_full_text
payload_policy.raw_text_in_payload may be true only for synthetic_fixture_payload and never for runtime-facing payload
```

Mandatory synthetic fixture non-claims:

```text
synthetic_fixture_only
not_real_source
not_source_ingestion
not_truth_authority
not_accepted_evidence
not_runtime_authority
not_external_admission_authority
not_trade_signal
not_order_intent
not_position_sizing
not_market_data_authority
```

---

## 13. External Consumer Boundary

A4 packages may be designed for future external consumers, but A4 does not dock to any external system.

Boundary law:

```text
FLWC produces candidate packages.
External consumers decide admission.
A candidate package remains candidate-only until a downstream consumer validates and accepts it under its own contract.
The wire carries data, not authority.
```

A4 does not authorize:

```text
external API
transport
message bus
consumer runtime
external admission
broker integration
scanner integration
trading integration
```

---

## 14. P620 Mapping

A4 may write docs-only artifacts under:

```text
/data/artifacts/flwc_authority
```

Future repo source-doc archive remains future-only:

```text
/data/strategy/flwc/docs/source_authority/
```

A4 does not authorize:

```text
/data/strategy/flwc creation
Git repo initialization
Codex session
Node/npm/Vite installation
DuckDB canonical DB seed
market-data authority cutover
real FLWC Console service on 18110
persistent LLM service
source ingestion
model calls
```

---

## 15. Downstream A5 Requirements

A5 may define the full validator and refusal law only after A4 is accepted.

A5 must consume:

```text
FLWCCandidateEvidencePackageV1
FLWCCandidateEvidenceRecordV1
FLWCCandidatePayloadPolicyV1
A4 refusal baseline
A3 raw evidence / claim / event schemas
A2 source/license law
bitemporal time law
payload denial law
no-future law
no-trade/no-order/no-position law
non-claims law
```

A5 must not create code. A5 must not create repo. A5 must not start Codex. A5 is the last docs-only gate before any B0 fixture-only code proposal.

---

## 16. A4 Acceptance Criteria

A4 can be accepted if:

```text
Candidate package envelope is explicit.
Candidate record schema is explicit.
Payload policy is explicit.
Source/license carry-forward is explicit.
As-of/replay eligibility is explicit.
Raw text and raw LLM output denial are explicit.
Trade/order/position fields remain forbidden.
External consumer boundary remains candidate-only.
Minimal A4 validator set is explicit.
A5 downstream contract is clear.
Real source access remains closed.
Repo/Codex/code/runtime non-claims are explicit.
Artifact sha256 is recorded.
Commander accepts the document as source authority.
```

---

## 17. Non-Claims

```text
flwc_a4_candidate_evidence_package_contract_defined = true
flwc_a4_candidate_evidence_package_contract_accepted = false
flwc_accepted_evidence_admission_authorized = false
flwc_external_consumer_runtime_authorized = false
flwc_external_docking_authorized = false
flwc_real_source_access_authorized = false
flwc_source_ingestion_authorized = false
flwc_vendor_api_authorized = false
flwc_paid_source_access_authorized = false
flwc_web_scraping_authorized = false
flwc_model_call_authorized = false
flwc_local_llm_runtime_authorized_by_A4 = false
flwc_database_implementation_authorized = false
flwc_runtime_service_authorized = false
flwc_repo_created = false
flwc_code_implemented = false
flwc_codex_started = false
flwc_trading_authority = false
flwc_scanner_authority = false
flwc_order_intent_authority = false
flwc_position_sizing_authority = false
flwc_production_ready = false
flwc_live_trading_ready = false
```

---

## 18. Carry-Forward Sentence

Treat FLWC candidate evidence packages as bounded, manifest-backed, as-of-disciplined, lineage-hashed, validator-gated, candidate-only handoff artifacts. No candidate package is accepted evidence, truth authority, source authority, license authority, runtime admission, trade signal, order intent, or position sizing. Downstream consumers decide admission under their own contracts.
