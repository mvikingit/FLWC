from __future__ import annotations

from copy import deepcopy
from typing import Any

from flwc.compiler.source_license_fixtures import (
    FIXTURE_LICENSE_MANIFEST_ID,
    FIXTURE_NS,
    FIXTURE_SOURCE_ID,
    FIXTURE_SOURCE_MANIFEST_ID,
    build_valid_license_manifest,
    build_valid_source_manifest,
)
from flwc.schemas.common import ValidatorStatus
from flwc.schemas.raw_evidence import (
    FLWCRawEvidenceRecordV1,
    FLWCRawEvidenceVaultManifestV1,
    FLWCSourceDocumentIndexV1,
    MANDATORY_RAW_EVIDENCE_NON_CLAIMS,
    QuarantineStatus,
    RawTextRefPolicy,
    VaultScope,
)
from flwc.schemas.source_license import LicenseState, RawStoragePolicy, RightsScope, SourceClass, SourceTrustTier


RAW_EVIDENCE_FIXTURE_NS = FIXTURE_NS + 10
FIXTURE_VAULT_MANIFEST_ID = "synthetic_raw_evidence_vault_manifest_001"
FIXTURE_EVIDENCE_ID = "synthetic_raw_evidence_record_001"
FIXTURE_SOURCE_DOCUMENT_ID = "synthetic_doc_001"
FIXTURE_SEGMENT_REF = f"{FIXTURE_SOURCE_DOCUMENT_ID}#segment:000001"
FIXTURE_RAW_TEXT_HASH = "sha256:synthetic_raw_text_hash_001"
FIXTURE_DOCUMENT_HASH = "sha256:synthetic_document_hash_001"
FIXTURE_SEGMENT_INDEX_DIGEST = "sha256:synthetic_segment_index_digest_001"
FIXTURE_EVIDENCE_RECORD_DIGEST = "sha256:synthetic_evidence_record_digest_001"
FIXTURE_LINEAGE_DIGEST = "sha256:synthetic_raw_evidence_lineage_digest_001"
FIXTURE_DEDUPE_HASH = "sha256:synthetic_raw_evidence_dedupe_hash_001"


def build_valid_raw_evidence_vault_manifest(**overrides: Any) -> dict[str, object]:
    vault = FLWCRawEvidenceVaultManifestV1(
        vault_manifest_id=FIXTURE_VAULT_MANIFEST_ID,
        vault_scope=VaultScope.SYNTHETIC_FIXTURE_ONLY,
        source_manifest_refs=(FIXTURE_SOURCE_MANIFEST_ID,),
        license_manifest_refs=(FIXTURE_LICENSE_MANIFEST_ID,),
        source_cutoff_ns=RAW_EVIDENCE_FIXTURE_NS + 3,
        created_at_ns=RAW_EVIDENCE_FIXTURE_NS + 4,
        producer_id="flwc-b1-raw-evidence-fixture-builder",
        producer_version="0.0.0",
        raw_storage_policy_summary=((FIXTURE_SOURCE_MANIFEST_ID, RawStoragePolicy.ALLOWED_FULL_TEXT.value),),
        retention_policy_summary=((FIXTURE_SOURCE_MANIFEST_ID, "synthetic_fixture_retention_internal_only"),),
        prompt_injection_policy_summary=((FIXTURE_SOURCE_MANIFEST_ID, "not_applicable_metadata_only"),),
        evidence_record_count=1,
        evidence_record_hash_method="sha256",
        evidence_record_digest=FIXTURE_EVIDENCE_RECORD_DIGEST,
        lineage_digest=FIXTURE_LINEAGE_DIGEST,
        validation_status=ValidatorStatus.ACCEPT,
        validator_summary_ref=None,
        non_claims=MANDATORY_RAW_EVIDENCE_NON_CLAIMS,
    )
    return _with_overrides(vault.as_dict(), overrides)


def build_valid_raw_evidence_record(**overrides: Any) -> dict[str, object]:
    record = FLWCRawEvidenceRecordV1(
        evidence_id=FIXTURE_EVIDENCE_ID,
        source_manifest_ref=FIXTURE_SOURCE_MANIFEST_ID,
        license_manifest_ref=FIXTURE_LICENSE_MANIFEST_ID,
        source_id=FIXTURE_SOURCE_ID,
        source_class=SourceClass.SYNTHETIC_FIXTURE,
        source_trust_tier=SourceTrustTier.TIER_4_MANUAL_REVIEW_ONLY,
        license_state=LicenseState.ALLOWED_FULL_TEXT,
        rights_scope=RightsScope.RESEARCH_INTERNAL_ONLY,
        raw_storage_policy=RawStoragePolicy.ALLOWED_FULL_TEXT,
        retention_policy="synthetic_fixture_retention_internal_only",
        source_url_or_doc_id=FIXTURE_SOURCE_DOCUMENT_ID,
        source_revision_id="synthetic_revision_001",
        source_document_id=FIXTURE_SOURCE_DOCUMENT_ID,
        source_span_refs=(FIXTURE_SEGMENT_REF,),
        raw_text_hash=FIXTURE_RAW_TEXT_HASH,
        raw_text_ref_policy=RawTextRefPolicy.SYNTHETIC_FIXTURE_TEXT_ALLOWED,
        derived_text_hash="sha256:synthetic_derived_text_hash_001",
        publisher_timestamp_ns=FIXTURE_NS,
        source_timestamp_ns=FIXTURE_NS,
        ingest_timestamp_ns=FIXTURE_NS + 1,
        available_from_ns=FIXTURE_NS + 1,
        compiler_seen_at_ns=FIXTURE_NS + 1,
        language="en",
        country_or_region="synthetic_region",
        asset_class_scope=("synthetic_fixture",),
        prompt_injection_flags=(),
        quarantine_status=QuarantineStatus.NOT_REQUIRED,
        dedupe_hash=FIXTURE_DEDUPE_HASH,
        lineage_digest=FIXTURE_LINEAGE_DIGEST,
        validation_status=ValidatorStatus.ACCEPT,
        non_claims=MANDATORY_RAW_EVIDENCE_NON_CLAIMS,
    )
    return _with_overrides(record.as_dict(), overrides)


def build_valid_source_document_index(**overrides: Any) -> dict[str, object]:
    index = FLWCSourceDocumentIndexV1(
        source_document_id=FIXTURE_SOURCE_DOCUMENT_ID,
        source_manifest_ref=FIXTURE_SOURCE_MANIFEST_ID,
        license_manifest_ref=FIXTURE_LICENSE_MANIFEST_ID,
        document_identity_key="synthetic_doc_001:synthetic_revision_001",
        revision_id="synthetic_revision_001",
        language="en",
        publisher_timestamp_ns=FIXTURE_NS,
        source_timestamp_ns=FIXTURE_NS,
        available_from_ns=FIXTURE_NS + 1,
        segment_count=1,
        segment_hash_method="sha256",
        segment_index_digest=FIXTURE_SEGMENT_INDEX_DIGEST,
        document_hash=FIXTURE_DOCUMENT_HASH,
        raw_storage_policy=RawStoragePolicy.ALLOWED_FULL_TEXT,
        retention_policy="synthetic_fixture_retention_internal_only",
        source_trust_tier=SourceTrustTier.TIER_4_MANUAL_REVIEW_ONLY,
        license_state=LicenseState.ALLOWED_FULL_TEXT,
        rights_scope=RightsScope.RESEARCH_INTERNAL_ONLY,
        prompt_injection_flags=(),
        validation_status=ValidatorStatus.ACCEPT,
        non_claims=MANDATORY_RAW_EVIDENCE_NON_CLAIMS,
    )
    return _with_overrides(index.as_dict(), overrides)


def build_valid_raw_evidence_index_pair() -> dict[str, object]:
    return {
        "source_manifest": build_valid_source_manifest(),
        "license_manifest": build_valid_license_manifest(),
        "raw_evidence_vault_manifest": build_valid_raw_evidence_vault_manifest(),
        "raw_evidence_record": build_valid_raw_evidence_record(),
        "source_document_index": build_valid_source_document_index(),
    }


def _with_overrides(base: dict[str, object], overrides: dict[str, Any]) -> dict[str, object]:
    result = deepcopy(base)
    for key, value in overrides.items():
        result[key] = value.value if hasattr(value, "value") else value
    return result


__all__ = [
    "build_valid_raw_evidence_index_pair",
    "build_valid_raw_evidence_record",
    "build_valid_raw_evidence_vault_manifest",
    "build_valid_source_document_index",
]
