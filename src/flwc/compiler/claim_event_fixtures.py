from __future__ import annotations

from copy import deepcopy
from typing import Any

from flwc.compiler.raw_evidence_fixtures import (
    FIXTURE_EVIDENCE_ID,
    FIXTURE_SEGMENT_REF,
    FIXTURE_SOURCE_DOCUMENT_ID,
    RAW_EVIDENCE_FIXTURE_NS,
    build_valid_raw_evidence_index_pair,
)
from flwc.compiler.source_license_fixtures import (
    FIXTURE_LICENSE_MANIFEST_ID,
    FIXTURE_NS,
    FIXTURE_SOURCE_MANIFEST_ID,
)
from flwc.schemas.claim_event import (
    ClaimExtractionMethod,
    ClaimStatus,
    ClaimType,
    EventDerivationMethod,
    EventDirectionCandidate,
    FLWCAtomicClaimLedgerV1,
    FLWCAtomicClaimV1,
    FLWCFinancialEventTableV1,
    FLWCFinancialEventV1,
    FinancialEventStatus,
    FinancialEventType,
    MANDATORY_CLAIM_EVENT_NON_CLAIMS,
)
from flwc.schemas.common import ValidatorStatus
from flwc.schemas.source_license import LicenseState, RawStoragePolicy, RightsScope, SourceTrustTier


CLAIM_EVENT_FIXTURE_NS = RAW_EVIDENCE_FIXTURE_NS + 10
FIXTURE_CLAIM_LEDGER_ID = "synthetic_atomic_claim_ledger_001"
FIXTURE_CLAIM_ID = "synthetic_atomic_claim_001"
FIXTURE_EVENT_TABLE_ID = "synthetic_financial_event_table_001"
FIXTURE_EVENT_ID = "synthetic_financial_event_001"
FIXTURE_ENTITY_ID = "synthetic_entity_001"
FIXTURE_ASSET_REF = "synthetic_asset_ref_001"
FIXTURE_CLAIM_DIGEST = "sha256:synthetic_claim_digest_001"
FIXTURE_EVENT_DIGEST = "sha256:synthetic_event_digest_001"
FIXTURE_CLAIM_LINEAGE_DIGEST = "sha256:synthetic_claim_lineage_digest_001"
FIXTURE_EVENT_LINEAGE_DIGEST = "sha256:synthetic_event_lineage_digest_001"


def build_valid_atomic_claim_ledger(**overrides: Any) -> dict[str, object]:
    ledger = FLWCAtomicClaimLedgerV1(
        claim_ledger_id=FIXTURE_CLAIM_LEDGER_ID,
        claim_ledger_version="v1",
        source_cutoff_ns=CLAIM_EVENT_FIXTURE_NS + 3,
        created_at_ns=CLAIM_EVENT_FIXTURE_NS + 4,
        producer_id="flwc-b1-claim-event-fixture-builder",
        producer_version="0.0.0",
        claim_count=1,
        claim_digest=FIXTURE_CLAIM_DIGEST,
        input_evidence_refs=(FIXTURE_EVIDENCE_ID,),
        input_source_manifest_refs=(FIXTURE_SOURCE_MANIFEST_ID,),
        input_license_manifest_refs=(FIXTURE_LICENSE_MANIFEST_ID,),
        lineage_digest=FIXTURE_CLAIM_LINEAGE_DIGEST,
        validation_status=ValidatorStatus.ACCEPT,
        validator_summary_ref=None,
        non_claims=MANDATORY_CLAIM_EVENT_NON_CLAIMS,
    )
    return _with_overrides(ledger.as_dict(), overrides)


def build_valid_atomic_claim(**overrides: Any) -> dict[str, object]:
    claim = FLWCAtomicClaimV1(
        claim_id=FIXTURE_CLAIM_ID,
        claim_version="v1",
        claim_type=ClaimType.GUIDANCE_STATEMENT,
        claim_text_or_structured_predicate="synthetic fixture predicate only",
        subject_entity_id=FIXTURE_ENTITY_ID,
        predicate_id="synthetic_guidance_update_predicate",
        object_value={"synthetic_value": "fixture_only"},
        object_unit=None,
        time_scope={"as_of_ns": FIXTURE_NS},
        source_document_id=FIXTURE_SOURCE_DOCUMENT_ID,
        source_span_refs=(FIXTURE_SEGMENT_REF,),
        raw_evidence_refs=(FIXTURE_EVIDENCE_ID,),
        source_manifest_ref=FIXTURE_SOURCE_MANIFEST_ID,
        license_manifest_ref=FIXTURE_LICENSE_MANIFEST_ID,
        license_state=LicenseState.ALLOWED_FULL_TEXT,
        rights_scope=RightsScope.RESEARCH_INTERNAL_ONLY,
        raw_storage_policy=RawStoragePolicy.ALLOWED_FULL_TEXT,
        retention_policy="synthetic_fixture_retention_internal_only",
        source_trust_tier=SourceTrustTier.TIER_4_MANUAL_REVIEW_ONLY,
        prompt_injection_flags=(),
        publisher_timestamp_ns=FIXTURE_NS,
        source_timestamp_ns=FIXTURE_NS,
        ingest_timestamp_ns=FIXTURE_NS + 1,
        available_from_ns=FIXTURE_NS + 1,
        compiler_seen_at_ns=FIXTURE_NS + 1,
        confidence_score=0.0,
        extraction_method=ClaimExtractionMethod.MANUAL_FIXTURE,
        model_ref=None,
        prompt_template_ref=None,
        human_review_ref=None,
        status=ClaimStatus.PROPOSED,
        superseded_by_claim_id=None,
        dispute_refs=(),
        lineage_digest=FIXTURE_CLAIM_LINEAGE_DIGEST,
        validation_status=ValidatorStatus.ACCEPT,
        non_claims=MANDATORY_CLAIM_EVENT_NON_CLAIMS,
    )
    return _with_overrides(claim.as_dict(), overrides)


def build_valid_financial_event_table(**overrides: Any) -> dict[str, object]:
    event_table = FLWCFinancialEventTableV1(
        event_table_id=FIXTURE_EVENT_TABLE_ID,
        event_table_version="v1",
        source_cutoff_ns=CLAIM_EVENT_FIXTURE_NS + 3,
        created_at_ns=CLAIM_EVENT_FIXTURE_NS + 4,
        producer_id="flwc-b1-claim-event-fixture-builder",
        producer_version="0.0.0",
        event_count=1,
        event_digest=FIXTURE_EVENT_DIGEST,
        input_claim_ledger_refs=(FIXTURE_CLAIM_LEDGER_ID,),
        input_source_manifest_refs=(FIXTURE_SOURCE_MANIFEST_ID,),
        input_license_manifest_refs=(FIXTURE_LICENSE_MANIFEST_ID,),
        lineage_digest=FIXTURE_EVENT_LINEAGE_DIGEST,
        validation_status=ValidatorStatus.ACCEPT,
        validator_summary_ref=None,
        non_claims=MANDATORY_CLAIM_EVENT_NON_CLAIMS,
    )
    return _with_overrides(event_table.as_dict(), overrides)


def build_valid_financial_event(**overrides: Any) -> dict[str, object]:
    event = FLWCFinancialEventV1(
        event_id=FIXTURE_EVENT_ID,
        event_version="v1",
        event_type=FinancialEventType.GUIDANCE_UPDATE,
        event_time_ns=FIXTURE_NS,
        publish_time_ns=FIXTURE_NS,
        source_timestamp_ns=FIXTURE_NS,
        available_from_ns=FIXTURE_NS + 1,
        compiler_seen_at_ns=FIXTURE_NS + 1,
        primary_entity_id=FIXTURE_ENTITY_ID,
        asset_refs=(FIXTURE_ASSET_REF,),
        country_or_region="synthetic_region",
        sector="synthetic_sector",
        asset_class="synthetic_fixture",
        evidence_claim_refs=(FIXTURE_CLAIM_ID,),
        source_document_refs=(FIXTURE_SOURCE_DOCUMENT_ID,),
        raw_evidence_refs=(FIXTURE_EVIDENCE_ID,),
        source_manifest_refs=(FIXTURE_SOURCE_MANIFEST_ID,),
        license_manifest_refs=(FIXTURE_LICENSE_MANIFEST_ID,),
        license_state_summary=((FIXTURE_LICENSE_MANIFEST_ID, LicenseState.ALLOWED_FULL_TEXT.value),),
        rights_scope_summary=((FIXTURE_LICENSE_MANIFEST_ID, RightsScope.RESEARCH_INTERNAL_ONLY.value),),
        raw_storage_policy=RawStoragePolicy.ALLOWED_FULL_TEXT,
        retention_policy="synthetic_fixture_retention_internal_only",
        source_trust_tier=SourceTrustTier.TIER_4_MANUAL_REVIEW_ONLY,
        prompt_injection_flags=(),
        direction_candidate=EventDirectionCandidate.NOT_APPLICABLE,
        importance_score=None,
        surprise_score=None,
        novelty_score=None,
        uncertainty_score=None,
        confidence_score=0.0,
        conflict_refs=(),
        status=FinancialEventStatus.PROPOSED,
        event_derivation_method=EventDerivationMethod.CLAIM_SET_COMPILER,
        lineage_digest=FIXTURE_EVENT_LINEAGE_DIGEST,
        validation_status=ValidatorStatus.ACCEPT,
        non_claims=MANDATORY_CLAIM_EVENT_NON_CLAIMS,
    )
    return _with_overrides(event.as_dict(), overrides)


def build_valid_claim_event_pair() -> dict[str, object]:
    return {
        "atomic_claim": build_valid_atomic_claim(),
        "financial_event": build_valid_financial_event(),
    }


def build_valid_claim_event_compiler_output() -> dict[str, object]:
    output = build_valid_raw_evidence_index_pair()
    output.update(
        {
            "atomic_claim_ledger": build_valid_atomic_claim_ledger(),
            "atomic_claim": build_valid_atomic_claim(),
            "financial_event_table": build_valid_financial_event_table(),
            "financial_event": build_valid_financial_event(),
        }
    )
    return output


def _with_overrides(base: dict[str, object], overrides: dict[str, Any]) -> dict[str, object]:
    result = deepcopy(base)
    for key, value in overrides.items():
        result[key] = value.value if hasattr(value, "value") else value
    return result


__all__ = [
    "build_valid_atomic_claim",
    "build_valid_atomic_claim_ledger",
    "build_valid_claim_event_compiler_output",
    "build_valid_claim_event_pair",
    "build_valid_financial_event",
    "build_valid_financial_event_table",
]
