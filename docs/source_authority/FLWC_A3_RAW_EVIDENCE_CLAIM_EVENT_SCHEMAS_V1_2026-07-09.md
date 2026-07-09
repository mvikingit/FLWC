# FLWC Raw Evidence + Claim/Event Schemas V1

**Document ID:** `FLWC-A3-RAW-EVIDENCE-CLAIM-EVENT-SCHEMAS-V1-2026-07-09`  
**Project:** `FLWC — Financial LLM Wiki Compiler`  
**Node:** `FLWC-A3`  
**Class:** docs-only / raw evidence + claim/event schema contracts / no data ingestion  
**Prepared for:** Commander  
**Prepared by:** FLWC Chief Engineer  
**Status:** source-doc candidate  
**Upstream accepted input:** `FLWC-A2 Source / License Manifest Contracts V1`  
**Downstream consumer:** `FLWC-A4 Candidate Evidence Package Contract`  
**Posture:** docs-only; no repo; no real source access; no source ingestion; no web scraping; no vendor API; no paid source access; no model calls; no database implementation; no runtime service; no trading/scanner/order authority.

---

## 0. Executive Verdict

This document freezes the first FLWC raw evidence, atomic claim, and financial event schema contract baseline.

```text
FLWC_A3_RAW_EVIDENCE_CLAIM_EVENT_SCHEMAS_PROPOSED = true
FLWC_A3_OPENS_REAL_SOURCE_ACCESS = false
FLWC_A3_OPENS_SOURCE_INGESTION = false
FLWC_A3_OPENS_VENDOR_API = false
FLWC_A3_OPENS_PAID_SOURCE_ACCESS = false
FLWC_A3_OPENS_WEB_SCRAPING = false
FLWC_A3_OPENS_REPO_BOOTSTRAP = false
FLWC_A3_OPENS_CODEX = false
FLWC_A3_OPENS_MODEL_CALLS = false
FLWC_A3_OPENS_DATABASE_IMPLEMENTATION = false
FLWC_A3_OPENS_RUNTIME_SERVICE = false
FLWC_A3_OPENS_TRADING_SCANNER_ORDER_AUTHORITY = false
```

A3 defines canonical schema responsibilities for raw evidence references, source document indexes, atomic claims, and financial events. It does not authorize ingestion of real source text. It does not create a database. It does not create code. It does not run a model.

---

## 1. Schema Principles

```text
manifest-backed evidence before claim
license state carried forward into every evidence-derived artifact
bitemporal timestamps before event compilation
source span references before summaries
lineage digest before promotion
claim lifecycle before narrative
event derivation from claims, not from model confidence
candidate status over truth assertion
no silent timestamp repair
no raw text in future runtime payload
```

Schema output is not authority by itself. Authority requires accepted source/license manifests, schema validation, timestamp validation, lineage validation, non-claim validation, and future node acceptance.

---

## 2. Upstream A2 Carry-Forward

A3 consumes these A2 contracts:

```text
FLWCSourceManifestV1
FLWCLicenseManifestV1
FLWCSourceClassV1
FLWCSourceTrustTierV1
FLWCLicenseStateV1
FLWCRawStoragePolicyV1
FLWCRightsScopeV1
source/license pairing law
credential leakage hard-reject law
runtime raw-text denial law
prompt-injection policy law
```

Every A3 artifact that references source material must carry:

```text
source_manifest_ref
license_manifest_ref
license_state
rights_scope
raw_storage_policy
retention_policy
source_trust_tier
prompt_injection_flags
non_claims
```

---

## 3. Time Law

Required time fields:

```text
event_time_ns
source_timestamp_ns
publisher_timestamp_ns
ingest_timestamp_ns
available_from_ns
compiler_seen_at_ns
source_cutoff_ns
snapshot_created_at_ns, future snapshot only
replay_as_of_ns, if replay is performed
```

Rules:

```text
source_timestamp_ns must not be silently replaced by current wall clock.
event_time_ns must not be inferred without a recorded derivation policy.
available_from_ns controls replay/as-of eligibility.
publisher_timestamp_ns records publisher-visible time when available.
ingest_timestamp_ns records FLWC observation time, not event time.
compiler_seen_at_ns records compiler observation of the source reference or evidence record.
missing or ambiguous material timestamps must HOLD_REVIEW or REJECT according to validator policy.
```

---

## 4. FLWCRawEvidenceVaultManifestV1

Purpose:

```text
Describe an immutable raw evidence vault snapshot or vault partition without authorizing real source ingestion.
```

Minimum required fields:

```yaml
schema_version: FLWCRawEvidenceVaultManifestV1
vault_manifest_id: string
vault_scope: enum
source_manifest_refs: list[string]
license_manifest_refs: list[string]
source_cutoff_ns: int
created_at_ns: int
producer_id: string
producer_version: string
raw_storage_policy_summary: map[string, string]
retention_policy_summary: map[string, string]
prompt_injection_policy_summary: map[string, string]
evidence_record_count: int
evidence_record_hash_method: string
evidence_record_digest: string
lineage_digest: string
validation_status: enum
validator_summary_ref: string | null
non_claims: list[string]
```

Allowed `vault_scope` values:

```text
synthetic_fixture_only
metadata_only
quarantine_review
authorized_source_future_node_only
```

Mandatory non-claims before a future real-source node:

```text
not_real_source_ingestion
not_license_authority
not_truth_authority
not_runtime_authority
not_trading_authority
```

---

## 5. FLWCRawEvidenceRecordV1

Purpose:

```text
Represent a manifest-backed raw evidence reference or synthetic fixture record.
```

Minimum required fields:

```yaml
schema_version: FLWCRawEvidenceRecordV1
evidence_id: string
source_manifest_ref: string
license_manifest_ref: string
source_id: string
source_class: FLWCSourceClassV1
source_trust_tier: FLWCSourceTrustTierV1
license_state: FLWCLicenseStateV1
rights_scope: FLWCRightsScopeV1
raw_storage_policy: FLWCRawStoragePolicyV1
source_url_or_doc_id: string
source_revision_id: string | null
source_document_id: string
source_span_refs: list[string]
raw_text_hash: string | null
raw_text_ref_policy: enum
derived_text_hash: string | null
publisher_timestamp_ns: int | null
source_timestamp_ns: int | null
ingest_timestamp_ns: int
available_from_ns: int
compiler_seen_at_ns: int
language: string | null
country_or_region: string | null
asset_class_scope: list[string]
prompt_injection_flags: list[string]
quarantine_status: enum
dedupe_hash: string
lineage_digest: string
validation_status: enum
non_claims: list[string]
```

Allowed `raw_text_ref_policy` values:

```text
no_raw_text_stored
raw_hash_only
raw_text_allowed_internal
derived_fields_only
quarantine_only
synthetic_fixture_text_allowed
```

Allowed `quarantine_status` values:

```text
not_required
quarantined_for_license
quarantined_for_prompt_injection
quarantined_for_timestamp
quarantined_for_identity
released_by_review
rejected
```

Fail closed if:

```text
license_state is unknown and raw_text_ref_policy stores raw text
credential value appears in any field
source_manifest_ref is missing
license_manifest_ref is missing
source_timestamp_ns is missing where required
available_from_ns is later than replay_as_of_ns for replay
raw_text_hash is missing when raw text is stored or referenced
prompt_injection_flags require quarantine and quarantine_status is not quarantined
```

---

## 6. FLWCSourceDocumentIndexV1

Purpose:

```text
Provide deterministic source document addressing for evidence spans and future wiki/review surfaces.
```

Minimum required fields:

```yaml
schema_version: FLWCSourceDocumentIndexV1
source_document_id: string
source_manifest_ref: string
license_manifest_ref: string
document_identity_key: string
revision_id: string | null
language: string | null
publisher_timestamp_ns: int | null
source_timestamp_ns: int | null
available_from_ns: int
segment_count: int
segment_hash_method: string
segment_index_digest: string
document_hash: string | null
raw_storage_policy: FLWCRawStoragePolicyV1
rights_scope: FLWCRightsScopeV1
validation_status: enum
non_claims: list[string]
```

Segment reference format:

```text
source_document_id#segment:<zero_padded_segment_id>
source_document_id#span:<start_segment_id>-<end_segment_id>
```

Rules:

```text
Segment IDs must be stable for a given source revision.
Segment hashes must be deterministic.
Segment text need not be stored when license forbids storage.
```

---

## 7. FLWCAtomicClaimLedgerV1

Purpose:

```text
Represent a versioned ledger of atomic claims derived from evidence-backed source spans.
```

Ledger-level minimum required fields:

```yaml
schema_version: FLWCAtomicClaimLedgerV1
claim_ledger_id: string
claim_ledger_version: string
source_cutoff_ns: int
created_at_ns: int
producer_id: string
producer_version: string
claim_count: int
claim_digest: string
input_evidence_refs: list[string]
input_source_manifest_refs: list[string]
input_license_manifest_refs: list[string]
lineage_digest: string
validation_status: enum
validator_summary_ref: string | null
non_claims: list[string]
```

Mandatory non-claims:

```text
not_truth_oracle
not_trade_signal
not_order_intent
not_position_sizing
not_runtime_authority
```

---

## 8. FLWCAtomicClaimV1

Purpose:

```text
Represent the smallest auditable knowledge unit.
```

Minimum required fields:

```yaml
schema_version: FLWCAtomicClaimV1
claim_id: string
claim_version: string
claim_type: enum
claim_text_or_structured_predicate: string
subject_entity_id: string | null
predicate_id: string
object_value: scalar | object | list | null
object_unit: string | null
time_scope: object | null
source_document_id: string
source_span_refs: list[string]
raw_evidence_refs: list[string]
source_manifest_ref: string
license_manifest_ref: string
license_state: FLWCLicenseStateV1
rights_scope: FLWCRightsScopeV1
publisher_timestamp_ns: int | null
source_timestamp_ns: int | null
ingest_timestamp_ns: int
available_from_ns: int
compiler_seen_at_ns: int
confidence_score: float | null
extraction_method: enum
model_ref: string | null
prompt_template_ref: string | null
human_review_ref: string | null
status: enum
superseded_by_claim_id: string | null
dispute_refs: list[string]
lineage_digest: string
validation_status: enum
non_claims: list[string]
```

Allowed `claim_type` values:

```text
entity_attribute
financial_metric
corporate_action
guidance_statement
calendar_statement
policy_statement
market_structure_statement
risk_disclosure
management_commentary
macro_observation
supply_chain_statement
legal_regulatory_statement
conflict_or_dispute
other
```

Allowed `extraction_method` values:

```text
manual_fixture
deterministic_parser
llm_candidate_future_authorization_required
human_review_patch
external_import_future_authorization_required
```

Allowed `status` values:

```text
proposed
active
disputed
superseded
expired
retracted
rejected
hold_review
neutralized
```

Rules:

```text
confidence_score is metadata, not truth authority.
llm_candidate_future_authorization_required cannot be used until a future model-use node authorizes model calls.
active status requires validators to accept source, license, timestamp, lineage, and non-claims.
rejected and neutralized claims must preserve refusal reason in validator summary.
```

---

## 9. FLWCFinancialEventTableV1

Purpose:

```text
Represent typed financial events derived from evidence-backed claims.
```

Table-level minimum required fields:

```yaml
schema_version: FLWCFinancialEventTableV1
event_table_id: string
event_table_version: string
source_cutoff_ns: int
created_at_ns: int
producer_id: string
producer_version: string
event_count: int
event_digest: string
input_claim_ledger_refs: list[string]
input_source_manifest_refs: list[string]
input_license_manifest_refs: list[string]
lineage_digest: string
validation_status: enum
validator_summary_ref: string | null
non_claims: list[string]
```

Mandatory non-claims:

```text
not_trade_signal
not_order_intent
not_position_sizing
not_calibrated_probability
not_execution_trigger
not_market_data_authority
```

---

## 10. FLWCFinancialEventV1

Purpose:

```text
Represent an auditable typed event compiled from accepted or review-routed claims.
```

Minimum required fields:

```yaml
schema_version: FLWCFinancialEventV1
event_id: string
event_version: string
event_type: enum
event_time_ns: int | null
publish_time_ns: int | null
source_timestamp_ns: int | null
available_from_ns: int
compiler_seen_at_ns: int
primary_entity_id: string | null
asset_refs: list[string]
country_or_region: string | null
sector: string | null
asset_class: string | null
evidence_claim_refs: list[string]
source_document_refs: list[string]
raw_evidence_refs: list[string]
source_manifest_refs: list[string]
license_manifest_refs: list[string]
license_state_summary: map[string, string]
rights_scope_summary: map[string, string]
direction_candidate: enum | null
importance_score: float | null
surprise_score: float | null
novelty_score: float | null
uncertainty_score: float | null
confidence_score: float | null
conflict_refs: list[string]
status: enum
event_derivation_method: enum
lineage_digest: string
validation_status: enum
non_claims: list[string]
```

Allowed `event_type` values:

```text
earnings_release
guidance_update
corporate_action
management_change
regulatory_action
legal_action
policy_decision
macro_data_release
supply_chain_event
product_launch_or_delay
financing_or_debt_event
rating_action
mna_event
risk_disclosure_event
calendar_event
market_structure_event
rumor_or_unverified_event
other
```

Allowed `direction_candidate` values:

```text
positive_candidate
negative_candidate
mixed_candidate
neutral_candidate
unknown
not_applicable
```

Allowed `status` values:

```text
proposed
active
disputed
superseded
expired
retracted
rejected
hold_review
neutralized
```

Allowed `event_derivation_method` values:

```text
manual_fixture
deterministic_rule
claim_set_compiler
llm_candidate_future_authorization_required
human_review_patch
```

Rules:

```text
direction_candidate is not a trade signal.
importance_score is not a sizing input.
surprise_score is not an execution trigger.
confidence_score is not a calibrated probability.
rumor_or_unverified_event must not promote without review.
```

---

## 11. Entity / Asset Link Contract Placeholder

A3 defines only minimal event-link placeholders. Full entity/ticker master design is a future node unless explicitly opened.

Minimum placeholder fields:

```yaml
entity_id: string
entity_type: enum
entity_name: string
ticker_or_asset_ref: string | null
country_or_region: string | null
exchange_or_venue: string | null
valid_from_ns: int | null
valid_until_ns: int | null
mapping_status: enum
source_manifest_ref: string | null
license_manifest_ref: string | null
validation_status: enum
non_claims: list[string]
```

Non-claims:

```text
not_security_master_authority
not_market_data_authority
not_trading_universe_authority
```

---

## 12. Conflict and Review Routing

A3 artifacts must support review routing.

Required conflict fields where applicable:

```text
conflict_refs
dispute_refs
review_status
review_reason
review_owner
validator_summary_ref
refusal_reason
```

Review statuses:

```text
not_required
hold_review
human_review_required
accepted_after_review
rejected_after_review
neutralized_after_review
```

Human notes are not canonical until accepted by a future patch-queue node.

---

## 13. Prompt-Injection and Untrusted Text Flags

Required flags:

```text
untrusted_text_isolated
prompt_injection_scan_required
prompt_injection_suspected
quarantined_for_prompt_injection
source_instruction_neutralized
human_review_required
```

Rules:

```text
Source text must be treated as data.
Source instructions must never execute as system instructions.
Any source text that attempts to alter schema, policy, credentials, runtime, or model behavior must be quarantined or rejected.
```

---

## 14. Validator Matrix

Validator outputs:

```text
ACCEPT
REJECT
HOLD_REVIEW
NEUTRALIZE
```

Required validators for A3 artifacts:

```text
raw_evidence_schema_validator
source_document_index_schema_validator
atomic_claim_schema_validator
financial_event_schema_validator
source_manifest_ref_validator
license_manifest_ref_validator
source_license_pairing_validator
rights_scope_validator
raw_storage_policy_validator
timestamp_validator
available_from_asof_validator
lineage_digest_validator
source_span_ref_validator
claim_event_ref_validator
entity_asset_link_placeholder_validator
prompt_injection_flag_validator
no_future_outcome_validator
no_trade_field_validator
non_claims_validator
credential_leak_validator
```

Hard reject:

```text
schema invalid
credential value detected
source manifest missing
license manifest missing
source/license mismatch
forbidden license
unknown license with raw/full text storage requested
missing required timestamp
source timestamp later than replay_as_of_ns
future outcome field present
trade signal field present
order intent field present
position target field present
raw LLM output in runtime-facing field
lineage digest mismatch
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
```

Neutralize:

```text
duplicate evidence
superseded claim
stale source
low source diversity
weak entity map
low-verifiability high-surprise event
```

---

## 15. Synthetic Fixture Policy

A3 may use synthetic fixture records for schema and validator testing.

Synthetic fixture requirements:

```text
source_class = synthetic_fixture
license_state = allowed_full_text
rights_scope = research_internal_only
raw_storage_policy = allowed_full_text
raw_text_ref_policy = synthetic_fixture_text_allowed
extraction_method = manual_fixture or deterministic_parser
event_derivation_method = manual_fixture or deterministic_rule
```

Mandatory fixture non-claims:

```text
synthetic_fixture_only
not_real_source
not_source_ingestion
not_truth_authority
not_market_data_authority
not_runtime_authority
not_trade_signal
not_order_intent
not_position_sizing
```

---

## 16. P620 Mapping

A3 may write docs-only artifacts under:

```text
/data/artifacts/flwc_authority
```

Future repo source-doc archive remains future-only:

```text
/data/strategy/flwc/docs/source_authority/
```

A3 does not authorize:

```text
/data/strategy/flwc creation
Git repo initialization
Codex session
Node/npm/Vite installation
DuckDB canonical DB seed
market-data authority cutover
real FLWC Console service on 18110
persistent LLM service
```

---

## 17. Downstream A4 Requirements

A4 may define candidate evidence package contract only after A3 is accepted.

A4 must consume:

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

A4 must not define accepted evidence admission for any downstream consumer. Candidate package remains candidate-only.

---

## 18. A3 Acceptance Criteria

A3 can be accepted if:

```text
raw evidence vault and record schemas are explicit.
source document index schema is explicit.
atomic claim ledger and claim schema are explicit.
financial event table and event schema are explicit.
A2 source/license fields are carried forward.
bitemporal time fields are explicit.
prompt-injection flags are explicit.
claim/event lifecycle is explicit.
trade/order/position semantics remain forbidden.
validator matrix is explicit.
real data ingestion remains closed.
repo/Codex/code/runtime non-claims are explicit.
A4 downstream contract is clear.
artifact sha256 is recorded.
Commander accepts the document as source authority.
```

---

## 19. Non-Claims

```text
flwc_a3_raw_evidence_claim_event_schemas_defined = true
flwc_a3_raw_evidence_claim_event_schemas_accepted = false
flwc_real_source_access_authorized = false
flwc_source_ingestion_authorized = false
flwc_vendor_api_authorized = false
flwc_paid_source_access_authorized = false
flwc_web_scraping_authorized = false
flwc_model_call_authorized = false
flwc_local_llm_runtime_authorized_by_A3 = false
flwc_database_implementation_authorized = false
flwc_runtime_service_authorized = false
flwc_repo_created = false
flwc_code_implemented = false
flwc_codex_started = false
flwc_external_consumer_docking_authorized = false
flwc_trading_authority = false
flwc_scanner_authority = false
flwc_order_intent_authority = false
flwc_position_sizing_authority = false
flwc_production_ready = false
flwc_live_trading_ready = false
```

---

## 20. Carry-Forward Sentence

Treat raw evidence, source document index, atomic claims, and financial events as manifest-backed, timestamp-disciplined, lineage-hashed, validator-gated candidates until accepted by named FLWC nodes. No source text may become claim, event, narrative, wiki, candidate package, runtime payload, or downstream evidence unless source/license references, rights scope, storage policy, timestamps, source spans, lineage digest, non-claims, and validators are accepted.
