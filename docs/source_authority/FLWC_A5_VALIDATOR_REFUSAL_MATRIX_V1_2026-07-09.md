# FLWC Validator / Refusal Matrix V1

**Document ID:** `FLWC-A5-VALIDATOR-REFUSAL-MATRIX-V1-2026-07-09`  
**Project:** `FLWC — Financial LLM Wiki Compiler`  
**Node:** `FLWC-A5`  
**Class:** docs-only / validator and refusal law / no code / no repo / no Codex  
**Prepared for:** Commander  
**Prepared by:** FLWC Chief Engineer  
**Status:** source-doc candidate  
**Upstream accepted input:** `FLWC-A4 Candidate Evidence Package Contract V1`  
**Downstream consumer:** `FLWC-B0 Typed Schema Package / Fixture-Only Code Proposal`  
**Posture:** docs-only; no repo; no source ingestion; no web scraping; no vendor API; no paid source access; no model calls; no database implementation; no runtime service; no external consumer docking; no trading/scanner/order authority.

---

## 0. Executive Verdict

This document freezes the first FLWC validator and refusal law baseline.

```text
FLWC_A5_VALIDATOR_REFUSAL_MATRIX_PROPOSED = true
FLWC_A5_OPENS_CODE = false
FLWC_A5_OPENS_REPO_BOOTSTRAP = false
FLWC_A5_OPENS_CODEX = false
FLWC_A5_OPENS_MODEL_CALLS = false
FLWC_A5_OPENS_REAL_SOURCE_ACCESS = false
FLWC_A5_OPENS_SOURCE_INGESTION = false
FLWC_A5_OPENS_VENDOR_API = false
FLWC_A5_OPENS_PAID_SOURCE_ACCESS = false
FLWC_A5_OPENS_WEB_SCRAPING = false
FLWC_A5_OPENS_DATABASE_IMPLEMENTATION = false
FLWC_A5_OPENS_RUNTIME_SERVICE = false
FLWC_A5_OPENS_EXTERNAL_DOCKING = false
FLWC_A5_OPENS_TRADING_SCANNER_ORDER_AUTHORITY = false
```

A5 defines how FLWC artifacts must be accepted, rejected, held for review, or neutralized. A5 does not create code. A5 does not create a repository. A5 does not start Codex. A5 is the last docs-only gate before any future `FLWC-B0` fixture-only code proposal.

---

## 1. Validator Principles

```text
fail_closed_over_silent_repair
deterministic_validator_over_model_confidence
schema_first_before_semantics
source_license_before_payload
as_of_before_replay
lineage_before_promotion
no_future_before_export
no_trade_no_order_no_position_before_handoff
bounded_payload_before_transport
refusal_record_before_drop
non_claims_before_acceptance
```

Validator output is authority only inside the accepted node scope. A validator may permit a candidate artifact to move to the next review state; it does not create truth, trading authority, source authority, license authority, runtime authority, or external admission authority.

---

## 2. Validator Output Enumeration

Every validator returns exactly one of:

```text
ACCEPT
REJECT
HOLD_REVIEW
NEUTRALIZE
```

Meaning:

```text
ACCEPT:
  The artifact satisfies this validator for the current node scope.

REJECT:
  The artifact violates a hard safety, schema, source, license, timestamp, lineage, payload, credential, future-leakage, or trading-boundary rule.

HOLD_REVIEW:
  The artifact is not safe to promote automatically and requires human review, source/legal review, timestamp review, entity review, or Commander review.

NEUTRALIZE:
  The artifact may be retained as audit material or duplicate/stale/non-promotable material, but it must not be promoted or exported as active candidate evidence.
```

Aggregation law:

```text
if any validator returns REJECT:
  aggregate_result = REJECT

else if any validator returns HOLD_REVIEW:
  aggregate_result = HOLD_REVIEW

else if any validator returns NEUTRALIZE:
  aggregate_result = NEUTRALIZE

else:
  aggregate_result = ACCEPT
```

No validator may silently repair an artifact while returning `ACCEPT`.

---

## 3. Canonical Validator Record Schemas

A5 defines schema responsibilities only. Final executable types are future B0 work.

### 3.1 FLWCValidatorSpecV1

Minimum required fields:

```yaml
schema_version: FLWCValidatorSpecV1
validator_id: string
validator_version: string
validator_family: enum
validator_scope: enum
input_schema_versions: list[string]
required_fields: list[string]
forbidden_fields: list[string]
hard_reject_conditions: list[string]
hold_review_conditions: list[string]
neutralize_conditions: list[string]
output_enum: list[string]
non_claims: list[string]
```

Allowed `validator_family` values:

```text
schema
source_manifest
license_manifest
source_license_pairing
rights_scope
raw_storage_policy
timestamp
available_from_asof
lineage_digest
source_span
claim_event_ref
entity_asset_link
payload_policy
bounded_payload
raw_text_denial
raw_llm_output_denial
future_outcome_denial
trade_field_denial
order_intent_denial
position_target_denial
credential_leak
prompt_injection
non_claims
snapshot_integrity_future
human_review_route
```

Allowed `validator_scope` values:

```text
source_manifest
license_manifest
raw_evidence_record
source_document_index
atomic_claim
financial_event
candidate_evidence_package
candidate_evidence_record
candidate_payload_policy
compiler_snapshot_future
synthetic_fixture
```

### 3.2 FLWCValidatorResultV1

Minimum required fields:

```yaml
schema_version: FLWCValidatorResultV1
validator_id: string
validator_version: string
artifact_ref: string
artifact_schema_version: string
run_id: string
run_started_at_ns: int
run_completed_at_ns: int
result: enum
reason_code: string
reason_detail_bounded: string
field_refs: list[string]
input_refs: list[string]
lineage_digest_checked: string | null
non_claims_checked: list[string]
refusal_record_ref: string | null
review_route_ref: string | null
producer_id: string
non_claims: list[string]
```

Allowed `result` values:

```text
ACCEPT
REJECT
HOLD_REVIEW
NEUTRALIZE
```

### 3.3 FLWCRefusalRecordV1

Minimum required fields:

```yaml
schema_version: FLWCRefusalRecordV1
refusal_id: string
refusal_version: string
artifact_ref: string
artifact_schema_version: string
validator_result_refs: list[string]
aggregate_result: enum
primary_refusal_family: enum
reason_codes: list[string]
field_refs: list[string]
source_manifest_refs: list[string]
license_manifest_refs: list[string]
timestamp_refs: list[string]
lineage_digest: string | null
review_status: enum
review_owner: string | null
created_at_ns: int
non_claims: list[string]
```

Allowed `primary_refusal_family` values:

```text
schema_invalid
source_missing
license_missing
source_license_mismatch
rights_scope_invalid
storage_policy_invalid
timestamp_invalid
as_of_violation
lineage_mismatch
prompt_injection
credential_leak
raw_text_denial
raw_llm_output_denial
future_outcome
trade_field
order_intent
position_target
unbounded_payload
missing_non_claims
entity_mapping_ambiguous
source_quality_low
duplicate_or_stale
unknown
```

Allowed `review_status` values:

```text
not_required
hold_review
human_review_required
legal_review_required
source_review_required
timestamp_review_required
entity_review_required
commander_review_required
rejected_final
neutralized_final
accepted_after_future_review_patch_required
```

### 3.4 FLWCValidatorSummaryV1

Minimum required fields:

```yaml
schema_version: FLWCValidatorSummaryV1
validator_summary_id: string
run_id: string
input_artifact_refs: list[string]
validator_result_refs: list[string]
refusal_record_refs: list[string]
accepted_count: int
rejected_count: int
hold_review_count: int
neutralized_count: int
aggregate_result: enum
created_at_ns: int
producer_id: string
producer_version: string
non_claims: list[string]
```

---

## 4. Required Validator Families

A5 freezes these mandatory validator families for future FLWC artifact promotion and candidate handoff.

```text
schema_version_validator
source_manifest_ref_validator
license_manifest_ref_validator
source_license_pairing_validator
rights_scope_validator
raw_storage_policy_validator
retention_policy_validator
timestamp_validator
available_from_asof_validator
lineage_digest_validator
source_span_ref_validator
claim_event_ref_validator
entity_asset_link_validator
payload_policy_validator
bounded_payload_validator
raw_text_payload_denial_validator
raw_llm_output_denial_validator
full_rag_context_denial_validator
future_outcome_denial_validator
no_trade_field_validator
no_order_intent_validator
no_position_target_validator
broker_execution_field_denial_validator
credential_leak_validator
prompt_injection_flag_validator
non_claims_validator
review_route_validator
synthetic_fixture_scope_validator
```

Mandatory for every runtime-facing or external-consumer future candidate:

```text
schema_version_validator
source_manifest_ref_validator
license_manifest_ref_validator
source_license_pairing_validator
timestamp_validator
available_from_asof_validator
lineage_digest_validator
payload_policy_validator
bounded_payload_validator
raw_text_payload_denial_validator
raw_llm_output_denial_validator
future_outcome_denial_validator
no_trade_field_validator
no_order_intent_validator
no_position_target_validator
credential_leak_validator
non_claims_validator
```

---

## 5. Hard-Reject Matrix

A validator must return `REJECT` for any of these conditions.

### 5.1 Schema / Required Field

```text
schema_version missing
schema_version unsupported
required field missing
field type invalid
enum value invalid
artifact id missing
producer id missing
created_at_ns missing
non_claims missing
```

### 5.2 Source / License

```text
source_manifest_ref missing
license_manifest_ref missing
source_manifest unresolved
license_manifest unresolved
source_id mismatch between source and license manifests
license_state = forbidden
license_state = expired for new ingestion or new promotion
license_state = unknown and raw/full text storage requested
rights_scope = unknown for runtime-facing candidate
raw_storage_policy incompatible with license_state
retention_policy missing
credential value appears in any source/license field
```

### 5.3 Timestamp / As-Of

```text
source_timestamp_ns missing where required
publisher_timestamp_ns silently replaced by wall clock
available_from_ns missing
candidate_build_as_of_ns missing for candidate package
source_cutoff_ns missing
available_from_ns > candidate_build_as_of_ns
source_timestamp_ns > replay_as_of_ns
event_time_ns inferred without derivation policy
future outcome field present
```

### 5.4 Lineage / References

```text
lineage_digest missing
lineage_digest mismatch
input refs missing
source_span_refs missing for source-derived claim
atomic_claim_refs missing where financial_event derives from claims
candidate package references artifact outside source_cutoff_ns
source document segment ref invalid
```

### 5.5 Payload Safety

```text
payload_policy missing
runtime_payload_bounded = false
max_payload_bytes missing or <= 0
payload exceeds max_payload_bytes
raw_text_in_payload = true outside synthetic_fixture_payload
raw_llm_output_in_payload = true
full_rag_context_in_payload = true
future_outcome_in_payload = true
trade_signal_fields_present = true
order_intent_fields_present = true
position_target_fields_present = true
broker_or_execution_fields_present = true
```

### 5.6 Security / Prompt Injection

```text
credential value detected
API key detected
browser session token detected
SSH private key material detected
source text instruction attempts to alter schema or authority
source text requests credential exposure
source text requests policy override
source instruction is executed as system instruction
prompt_injection_suspected and quarantine missing
```

### 5.7 Trading Boundary

```text
trade signal field present
order intent field present
position target field present
broker routing field present
execution instruction present
position sizing field present
market data authority claim present without explicit authority node
```

---

## 6. Hold-Review Matrix

A validator must return `HOLD_REVIEW` for any of these conditions unless another validator already returns `REJECT`.

```text
license_state = unknown without raw text request
license_state = human_review_required
rights_scope = unknown for non-runtime internal review candidate
timestamp ambiguous
publisher identity ambiguous
source revision ambiguous
source diversity insufficient for high-impact claim
official source conflicts with licensed news or secondary source
entity/ticker mapping ambiguous
country/region mapping ambiguous
high-impact conflict
prompt injection suspected but isolated and quarantined
weak source or rumor
low-verifiability high-surprise event
external consumer candidate without accepted adapter contract
human review note attempts canonical promotion without review patch queue
```

Review route must be explicit.

---

## 7. Neutralize Matrix

A validator may return `NEUTRALIZE` for non-promotable but auditable material.

```text
duplicate evidence
duplicate candidate
superseded claim
superseded event
stale source
low source diversity
weak entity map
low-verifiability low-impact candidate
synthetic fixture outside requested fixture set
candidate replaced by newer lineage digest
source revision superseded by newer revision
```

Neutralized artifacts remain audit material and must not be promoted as active evidence.

---

## 8. Artifact-Specific Validator Requirements

### 8.1 FLWCSourceManifestV1

Required validators:

```text
schema_version_validator
source_manifest_ref_validator
license_manifest_ref_validator
source_license_pairing_validator
rights_scope_validator
raw_storage_policy_validator
retention_policy_validator
timestamp_validator
credential_leak_validator
prompt_injection_flag_validator
non_claims_validator
```

### 8.2 FLWCLicenseManifestV1

Required validators:

```text
schema_version_validator
license_manifest_ref_validator
rights_scope_validator
raw_storage_policy_validator
retention_policy_validator
credential_leak_validator
non_claims_validator
```

### 8.3 FLWCRawEvidenceRecordV1

Required validators:

```text
schema_version_validator
source_manifest_ref_validator
license_manifest_ref_validator
source_license_pairing_validator
rights_scope_validator
raw_storage_policy_validator
timestamp_validator
available_from_asof_validator
source_span_ref_validator
lineage_digest_validator
prompt_injection_flag_validator
credential_leak_validator
non_claims_validator
```

### 8.4 FLWCAtomicClaimV1

Required validators:

```text
schema_version_validator
source_manifest_ref_validator
license_manifest_ref_validator
source_license_pairing_validator
timestamp_validator
available_from_asof_validator
source_span_ref_validator
lineage_digest_validator
prompt_injection_flag_validator
no_future_outcome_validator
no_trade_field_validator
credential_leak_validator
non_claims_validator
```

### 8.5 FLWCFinancialEventV1

Required validators:

```text
schema_version_validator
claim_event_ref_validator
source_manifest_ref_validator
license_manifest_ref_validator
timestamp_validator
available_from_asof_validator
lineage_digest_validator
entity_asset_link_validator
no_future_outcome_validator
no_trade_field_validator
no_order_intent_validator
no_position_target_validator
credential_leak_validator
non_claims_validator
```

### 8.6 FLWCCandidateEvidencePackageV1

Required validators:

```text
schema_version_validator
source_manifest_ref_validator
license_manifest_ref_validator
source_license_pairing_validator
timestamp_validator
available_from_asof_validator
lineage_digest_validator
payload_policy_validator
bounded_payload_validator
raw_text_payload_denial_validator
raw_llm_output_denial_validator
full_rag_context_denial_validator
future_outcome_denial_validator
no_trade_field_validator
no_order_intent_validator
no_position_target_validator
broker_execution_field_denial_validator
credential_leak_validator
prompt_injection_flag_validator
non_claims_validator
```

---

## 9. Repair and Review Law

```text
silent_repair_authorized = false
wall_clock_timestamp_substitution_authorized = false
license_guessing_authorized = false
entity_mapping_guess_promotion_authorized = false
model_confidence_promotion_authorized = false
raw_llm_output_promotion_authorized = false
```

Allowed future repair categories, only with explicit record:

```text
schema_fixture_repair_for_synthetic_fixtures
timestamp_review_patch
source_license_review_patch
entity_mapping_review_patch
human_review_patch_queue
tombstone_and_new_revision
```

Every repair must create a new artifact revision or a review patch artifact. Silent overwrite is forbidden.

---

## 10. Prompt Injection Refusal Law

All source text and all model output are untrusted input.

Hard reject or quarantine if:

```text
source attempts to modify system prompt
source attempts to redefine FLWC schema
source requests credential disclosure
source requests policy override
source instructs model to ignore validators
source attempts to promote itself as authority
model output contains instructions to bypass validators
model output requests access to secrets
```

Source instructions must never execute as system instructions.

---

## 11. LLM Output Validator Law

If a future model-use node is accepted, every model output must carry:

```text
model_id_or_local_model_ref
model_version
prompt_template_ref
prompt_hash
schema_version
raw_output_ref_cold_only
validator_status
non_claims
```

Hard reject if:

```text
raw LLM output enters runtime-facing payload
raw LLM output is treated as truth authority
model output contains trade/order/position semantics
model output lacks non_claims
model output lacks source refs for source-backed claims
model output uses unavailable future facts
```

LLM output can only be candidate-only input to deterministic validators.

---

## 12. Synthetic Fixture Validator Law

Synthetic fixtures are allowed for contract and validator testing.

Fixture requirements:

```text
source_class = synthetic_fixture
package_scope = synthetic_fixture_only
license_state = allowed_full_text
rights_scope = research_internal_only
raw_storage_policy = allowed_full_text
non_claims include synthetic_fixture_only and not_real_source
```

Hard reject fixture if:

```text
synthetic fixture claims to be real source
synthetic fixture enters production/runtime authority
synthetic fixture omits non_claims
synthetic fixture contains broker/API/secret material
```

---

## 13. B0 Downstream Gate

A5 does not authorize B0 by itself. It only creates the final docs-only prerequisite.

Future `FLWC-B0` may be proposed only after Commander accepts A5 as source authority.

B0 maximum initial scope:

```text
typed schema package
fixture-only validators
synthetic fixtures only
local unit tests
no real data
no source ingestion
no model calls
no runtime service
no external docking
no trading/scanner/order authority
```

B0 must not start until a separate Commander authorization explicitly opens:

```text
FLWC_B0_TYPED_SCHEMA_PACKAGE_FIXTURE_ONLY_REPO_BOOTSTRAP
```

---

## 14. P620 Mapping

A5 may write docs-only artifacts under:

```text
/data/artifacts/flwc_authority
```

Future repo source-doc archive remains future-only until B0 authorization:

```text
/data/strategy/flwc/docs/source_authority/
```

A5 does not authorize:

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

## 15. A5 Acceptance Criteria

A5 can be accepted if:

```text
validator output enum is explicit.
validator result schema responsibilities are explicit.
refusal record schema responsibilities are explicit.
validator summary responsibilities are explicit.
hard-reject matrix is explicit.
hold-review matrix is explicit.
neutralize matrix is explicit.
artifact-specific validators are explicit.
source/license validators carry A2 forward.
raw evidence, claim, and event validators carry A3 forward.
candidate package validators carry A4 forward.
raw text and raw LLM output denial are explicit.
future outcome denial is explicit.
trade/order/position/broker fields remain forbidden.
prompt injection refusal law is explicit.
silent repair remains forbidden.
B0 downstream gate is fixture-only and separately authorized.
repo/Codex/code/runtime non-claims are explicit.
artifact sha256 is recorded.
Commander accepts the document as source authority.
```

---

## 16. Non-Claims

```text
flwc_a5_validator_refusal_matrix_defined = true
flwc_a5_validator_refusal_matrix_accepted = false
flwc_repo_created = false
flwc_code_implemented = false
flwc_codex_started = false
flwc_b0_authorized = false
flwc_real_source_access_authorized = false
flwc_source_ingestion_authorized = false
flwc_vendor_api_authorized = false
flwc_paid_source_access_authorized = false
flwc_web_scraping_authorized = false
flwc_model_call_authorized = false
flwc_local_llm_runtime_authorized_by_A5 = false
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

## 17. Carry-Forward Sentence

Treat FLWC validators as deterministic, fail-closed, source/license-aware, as-of-disciplined, lineage-backed acceptance gates. No artifact may promote silently. No source text, model output, candidate package, wiki page, event, claim, snapshot, or downstream handoff may bypass schema, source, license, timestamp, lineage, no-future, no-trade/no-order/no-position, bounded-payload, credential-leak, prompt-injection, and non-claim validators.
