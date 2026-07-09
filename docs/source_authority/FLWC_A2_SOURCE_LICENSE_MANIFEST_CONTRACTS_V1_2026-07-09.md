# FLWC Source / License Manifest Contracts V1

**Document ID:** `FLWC-A2-SOURCE-LICENSE-MANIFEST-CONTRACTS-V1-2026-07-09`  
**Project:** `FLWC — Financial LLM Wiki Compiler`  
**Node:** `FLWC-A2`  
**Class:** docs-only / source-license manifest contracts / no real source access  
**Prepared for:** Commander  
**Prepared by:** FLWC Chief Engineer  
**Status:** source-doc candidate  
**Upstream accepted input:** `FLWC-A1 Architecture Blueprint V1`  
**Downstream consumer:** `FLWC-A3 Raw Evidence + Claim/Event Schemas`  
**Posture:** docs-only; no repo; no source ingestion; no web scraping; no vendor API; no paid source access; no model calls; no runtime service; no trading/scanner/order authority.

---

## 0. Executive Verdict

This document freezes the first FLWC source and license manifest contract baseline.

```text
FLWC_A2_SOURCE_LICENSE_MANIFEST_CONTRACTS_PROPOSED = true
FLWC_A2_OPENS_REAL_SOURCE_ACCESS = false
FLWC_A2_OPENS_VENDOR_API = false
FLWC_A2_OPENS_PAID_SOURCE_ACCESS = false
FLWC_A2_OPENS_WEB_SCRAPING = false
FLWC_A2_OPENS_SOURCE_INGESTION = false
FLWC_A2_OPENS_REPO_BOOTSTRAP = false
FLWC_A2_OPENS_CODEX = false
FLWC_A2_OPENS_MODEL_CALLS = false
FLWC_A2_OPENS_DATABASE_IMPLEMENTATION = false
FLWC_A2_OPENS_RUNTIME_SERVICE = false
FLWC_A2_OPENS_TRADING_SCANNER_ORDER_AUTHORITY = false
```

A2 defines what must be known about a source and its rights before any later node may ingest, store, derive from, summarize, export, or package that source. A2 is contract authority only. It does not authorize access to any real data source.

---

## 1. Contract Principles

```text
source identity before text
license state before storage
rights scope before derivative artifact
timestamp law before claim/event compilation
retention law before raw vault design
prompt-injection law before model or parser exposure
source class is metadata, not trust
license unknown means fail-closed for storage
manifest references over implicit paths
artifact evidence over verbal source claims
```

Definitions:

```text
source_manifest = identity, provenance, timestamp, revision, trust, and access metadata
license_manifest = rights, storage, derivative, retention, redistribution, and expiry metadata
source_ref = manifest-backed pointer, not permission to fetch
license_ref = manifest-backed rights state, not legal advice
raw_text_hash = integrity evidence, not storage authorization
source_class = classification, not truth authority
source_trust_tier = review hint, not admission authority
```

---

## 2. Source Class Enumeration

`FLWCSourceClassV1`:

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
synthetic_fixture
weak_source_or_rumor
unknown
```

Rules:

```text
official_source is not automatically truth.
licensed_news is not automatically storable.
manual_review_note is not canonical until patch-queue accepted.
synthetic_fixture may be used for tests only.
weak_source_or_rumor must not promote without explicit review.
unknown must fail closed for canonical promotion.
```

---

## 3. Source Trust Tier Enumeration

`FLWCSourceTrustTierV1`:

```text
tier_0_official_primary
tier_1_regulated_or_exchange
tier_2_licensed_professional
tier_3_reputable_secondary
tier_4_manual_review_only
tier_5_weak_or_rumor
tier_unknown
```

Trust tier is a review and routing hint. It is not claim truth authority.

---

## 4. License State Enumeration

`FLWCLicenseStateV1`:

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

Promotion rules:

```text
unknown:
  may record source metadata only; no raw text storage; no canonical promotion without review.

allowed_full_text:
  may store full text only if rights_scope and retention_policy also allow it.

metadata_only:
  may store source metadata and hashes; raw text must not be stored.

derived_only:
  may store bounded derived fields if derivation policy allows it; raw text must not be stored.

no_storage:
  may not store raw text or derived text; source metadata only.

human_review_required:
  must HOLD_REVIEW before use.

expired:
  must reject new ingestion and mark existing derived artifacts for retention review.

forbidden:
  must hard reject storage and promotion.
```

---

## 5. Storage Policy Enumeration

`FLWCRawStoragePolicyV1`:

```text
metadata_only
raw_hash_only
allowed_full_text
derived_fields_only
no_storage
quarantine_only
human_review_required
```

Rules:

```text
raw_storage_policy must be compatible with license_state.
allowed_full_text requires explicit license_state = allowed_full_text.
derived_fields_only requires license_state in {allowed_full_text, derived_only}.
metadata_only is the default safe fallback.
quarantine_only may be used for prompt-injection or rights ambiguity review.
```

---

## 6. Rights Scope Enumeration

`FLWCRightsScopeV1`:

```text
research_internal_only
review_internal_only
derived_artifacts_internal_only
redistribution_forbidden
public_redistribution_allowed
runtime_payload_forbidden
unknown
```

Default:

```text
rights_scope = unknown
runtime_payload_forbidden = true unless explicitly overridden by future source node
```

---

## 7. Source Timestamp Policy

Required timestamp fields for source manifests:

```text
publisher_timestamp_ns
source_timestamp_ns
ingest_timestamp_ns
available_from_ns
compiler_seen_at_ns
```

Rules:

```text
publisher_timestamp_ns may be absent only if source policy declares it unavailable.
source_timestamp_ns must not be silently replaced by wall-clock time.
ingest_timestamp_ns records FLWC observation time, not event time.
available_from_ns must support replay/as-of filtering.
missing timestamps must HOLD_REVIEW or REJECT according to validator policy.
```

---

## 8. FLWCSourceManifestV1 Contract

Minimum required fields:

```yaml
schema_version: FLWCSourceManifestV1
source_manifest_id: string
source_id: string
source_class: FLWCSourceClassV1
source_name: string
source_owner_or_publisher: string
source_url_or_doc_id: string
source_access_mode: enum
source_trust_tier: FLWCSourceTrustTierV1
publisher_timestamp_policy: enum
source_timestamp_policy: enum
revision_policy: enum
canonical_location_policy: enum
license_manifest_ref: string
rights_scope: FLWCRightsScopeV1
retention_policy: string
raw_storage_policy: FLWCRawStoragePolicyV1
raw_text_hash_required: boolean
dedupe_hash_method: string
revision_id: string | null
source_language: string | null
country_or_region: string | null
asset_class_scope: list[string]
prompt_injection_policy: enum
status: enum
created_at_ns: int
updated_at_ns: int
non_claims: list[string]
```

Allowed `source_access_mode` values:

```text
manual_metadata_only
offline_fixture
public_web_future_authorization_required
licensed_terminal_future_authorization_required
vendor_api_future_authorization_required
paid_research_future_authorization_required
```

Allowed `status` values:

```text
proposed
accepted_metadata_only
authorized_by_future_source_node
hold_review
deprecated
revoked
rejected
```

Mandatory non-claims for any source manifest created before real source authorization:

```text
not_source_access_authority
not_license_authority
not_truth_authority
not_ingestion_authority
not_runtime_authority
not_trading_authority
```

---

## 9. FLWCLicenseManifestV1 Contract

Minimum required fields:

```yaml
schema_version: FLWCLicenseManifestV1
license_manifest_id: string
source_id: string
license_state: FLWCLicenseStateV1
rights_scope: FLWCRightsScopeV1
raw_storage_policy: FLWCRawStoragePolicyV1
retention_policy: string
redistribution_policy: enum
derivative_policy: enum
quote_policy: enum
runtime_payload_policy: enum
paid_access_required: boolean
credential_required: boolean
credential_reference_policy: enum
pii_policy: enum
valid_from_ns: int | null
valid_until_ns: int | null
review_owner: string | null
review_status: enum
refusal_reason: string | null
created_at_ns: int
updated_at_ns: int
non_claims: list[string]
```

Allowed `redistribution_policy` values:

```text
forbidden
internal_only
public_allowed_if_source_allows
unknown
```

Allowed `derivative_policy` values:

```text
derived_metadata_only
derived_claims_allowed_internal
derived_events_allowed_internal
derived_text_forbidden
unknown
```

Allowed `runtime_payload_policy` values:

```text
raw_text_forbidden
derived_fields_only
candidate_package_metadata_only
future_review_required
```

Credential law:

```text
credential_reference_policy must never contain credential values.
credential material must not enter manifests, Markdown, repo, logs, screenshots, prompts, or artifacts.
Only secret-manager reference names or environment injection labels may be recorded by future nodes.
```

---

## 10. Manifest Pairing Law

Every `FLWCSourceManifestV1` must reference exactly one active `FLWCLicenseManifestV1` for the same `source_id`.

Validation requirements:

```text
source_manifest.license_manifest_ref resolves
source_manifest.source_id == license_manifest.source_id
source_manifest.raw_storage_policy compatible with license_manifest.license_state
source_manifest.rights_scope compatible with license_manifest.rights_scope
retention policy present on both manifests
runtime payload policy forbids raw text unless future node explicitly overrides
```

Fail closed if:

```text
missing license_manifest_ref
unresolved license_manifest_ref
source/license source_id mismatch
unknown license with raw storage requested
forbidden license
expired license for new ingestion
rights scope unknown for runtime-facing candidate
credential value appears in any field
```

---

## 11. Prompt Injection and Untrusted Text Manifest Flags

`prompt_injection_policy` values:

```text
not_applicable_metadata_only
untrusted_text_isolated
prompt_injection_scan_required
quarantine_on_suspected_injection
human_review_required
```

Future raw evidence nodes must carry prompt-injection flags forward into the raw evidence vault and candidate package validators.

A2 does not scan real text and does not execute any source instruction.

---

## 12. Refusal / Validator Matrix

Validator outputs:

```text
ACCEPT
REJECT
HOLD_REVIEW
NEUTRALIZE
```

Required validators for A2-derived artifacts:

```text
source_manifest_schema_validator
license_manifest_schema_validator
source_license_pairing_validator
rights_scope_validator
raw_storage_policy_validator
retention_policy_validator
timestamp_policy_validator
credential_leak_validator
prompt_injection_policy_validator
no_runtime_payload_raw_text_validator
non_claims_validator
```

Hard reject:

```text
schema invalid
credential value detected
forbidden license
unknown license with raw/full-text storage requested
source/license mismatch
runtime payload policy permits raw text without future authorization
missing non_claims
```

Hold review:

```text
license_state = unknown
license_state = human_review_required
rights_scope = unknown
timestamp policy ambiguous
retention policy ambiguous
publisher/source identity ambiguous
```

Neutralize:

```text
weak_source_or_rumor
stale source policy
low trust tier without source diversity
prompt injection suspected but isolated for review
```

---

## 13. Synthetic Fixture Policy

A2 may use synthetic fixture manifests only to test schemas and validators.

Synthetic fixture source class:

```text
source_class = synthetic_fixture
license_state = allowed_full_text
rights_scope = research_internal_only
raw_storage_policy = allowed_full_text
status = accepted_metadata_only
```

Mandatory fixture non-claims:

```text
synthetic_fixture_only
not_real_source
not_source_ingestion
not_truth_authority
not_runtime_authority
not_trade_signal
```

---

## 14. P620 Mapping

A2 may write docs-only artifacts under:

```text
/data/artifacts/flwc_authority
```

Future repo source-doc archive candidate remains future-only:

```text
/data/strategy/flwc/docs/source_authority/
```

A2 does not authorize:

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

## 15. Downstream A3 Requirements

A3 may define raw evidence, claim, and event schemas only after A2 is accepted.

A3 must consume:

```text
FLWCSourceManifestV1
FLWCLicenseManifestV1
FLWCSourceClassV1
FLWCLicenseStateV1
FLWCRawStoragePolicyV1
FLWCRightsScopeV1
source/license pairing validator law
credential leak refusal law
runtime raw-text denial law
```

A3 must not ingest real data unless a later C0 source authorization gate opens a source class.

---

## 16. A2 Acceptance Criteria

A2 can be accepted if:

```text
SourceManifestV1 responsibilities are explicit.
LicenseManifestV1 responsibilities are explicit.
source/license pairing law is explicit.
license states and storage policies are explicit.
rights scope and retention law are explicit.
credential leakage is hard-rejected.
prompt-injection handling is explicit.
real source access remains closed.
repo/Codex/code/runtime non-claims are explicit.
A3 downstream contract is clear.
artifact sha256 is recorded.
Commander accepts the document as source authority.
```

---

## 17. Non-Claims

```text
flwc_a2_source_license_contracts_defined = true
flwc_a2_source_license_contracts_accepted = false
flwc_real_source_access_authorized = false
flwc_source_ingestion_authorized = false
flwc_vendor_api_authorized = false
flwc_paid_source_access_authorized = false
flwc_web_scraping_authorized = false
flwc_model_call_authorized = false
flwc_local_llm_runtime_authorized_by_A2 = false
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

## 18. Carry-Forward Sentence

Treat source and license manifests as mandatory authority gates. No source text may be ingested, stored, compiled, exported, summarized, model-processed, or runtime-packaged unless the source identity, license state, rights scope, storage policy, retention policy, timestamp policy, prompt-injection posture, and non-claims are manifest-backed and validator-accepted.
