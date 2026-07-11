from __future__ import annotations

from copy import deepcopy
from typing import Any

from flwc.schemas.source_license import (
    DerivativePolicy,
    FLWCLicenseManifestV1,
    FLWCSourceManifestV1,
    LicenseState,
    PromptInjectionPolicy,
    RawStoragePolicy,
    RedistributionPolicy,
    RightsScope,
    RuntimePayloadPolicy,
    SourceAccessMode,
    SourceClass,
    SourceStatus,
    SourceTrustTier,
)


FIXTURE_NS = 1_760_000_000_000_000_000
FIXTURE_SOURCE_ID = "synthetic_source_001"
FIXTURE_SOURCE_MANIFEST_ID = "synthetic_source_manifest_001"
FIXTURE_LICENSE_MANIFEST_ID = "synthetic_license_manifest_001"

SOURCE_NON_CLAIMS = (
    "synthetic_fixture_only",
    "not_real_source",
    "not_source_ingestion",
    "not_source_access_authority",
    "not_license_authority",
    "not_truth_authority",
    "not_ingestion_authority",
    "not_runtime_authority",
    "not_trading_authority",
    "not_trade_signal",
)

LICENSE_NON_CLAIMS = (
    "synthetic_fixture_only",
    "not_real_source",
    "not_source_ingestion",
    "not_license_authority",
    "not_legal_advice",
    "not_truth_authority",
    "not_runtime_authority",
    "not_trade_signal",
)


def build_valid_source_manifest(**overrides: Any) -> dict[str, object]:
    source = FLWCSourceManifestV1(
        source_manifest_id=FIXTURE_SOURCE_MANIFEST_ID,
        source_id=FIXTURE_SOURCE_ID,
        source_class=SourceClass.SYNTHETIC_FIXTURE,
        source_name="Synthetic Fixture Source",
        source_owner_or_publisher="FLWC B1 synthetic fixture",
        source_url_or_doc_id="synthetic_doc_001",
        source_access_mode=SourceAccessMode.OFFLINE_FIXTURE,
        source_trust_tier=SourceTrustTier.TIER_4_MANUAL_REVIEW_ONLY,
        publisher_timestamp_policy="fixture_timestamp_available",
        source_timestamp_policy="fixture_timestamp_available",
        revision_policy="fixture_revision_static",
        canonical_location_policy="fixture_doc_id_only",
        license_manifest_ref=FIXTURE_LICENSE_MANIFEST_ID,
        rights_scope=RightsScope.RESEARCH_INTERNAL_ONLY,
        retention_policy="synthetic_fixture_retention_internal_only",
        raw_storage_policy=RawStoragePolicy.ALLOWED_FULL_TEXT,
        raw_text_hash_required=False,
        dedupe_hash_method="sha256",
        revision_id="synthetic_revision_001",
        source_language="en",
        country_or_region="synthetic_region",
        asset_class_scope=("synthetic_fixture",),
        prompt_injection_policy=PromptInjectionPolicy.NOT_APPLICABLE_METADATA_ONLY,
        status=SourceStatus.ACCEPTED_METADATA_ONLY,
        publisher_timestamp_ns=FIXTURE_NS,
        source_timestamp_ns=FIXTURE_NS,
        ingest_timestamp_ns=FIXTURE_NS + 1,
        available_from_ns=FIXTURE_NS + 1,
        compiler_seen_at_ns=FIXTURE_NS + 1,
        created_at_ns=FIXTURE_NS + 2,
        updated_at_ns=FIXTURE_NS + 2,
        non_claims=SOURCE_NON_CLAIMS,
    )
    return _with_overrides(source.as_dict(), overrides)


def build_valid_license_manifest(**overrides: Any) -> dict[str, object]:
    license_ = FLWCLicenseManifestV1(
        license_manifest_id=FIXTURE_LICENSE_MANIFEST_ID,
        source_id=FIXTURE_SOURCE_ID,
        license_state=LicenseState.ALLOWED_FULL_TEXT,
        rights_scope=RightsScope.RESEARCH_INTERNAL_ONLY,
        raw_storage_policy=RawStoragePolicy.ALLOWED_FULL_TEXT,
        retention_policy="synthetic_fixture_retention_internal_only",
        redistribution_policy=RedistributionPolicy.INTERNAL_ONLY,
        derivative_policy=DerivativePolicy.DERIVED_CLAIMS_ALLOWED_INTERNAL,
        quote_policy="synthetic_fixture_quotes_not_applicable",
        runtime_payload_policy=RuntimePayloadPolicy.RAW_TEXT_FORBIDDEN,
        paid_access_required=False,
        credential_required=False,
        credential_reference_policy="no_credentials_required",
        pii_policy="no_pii_in_synthetic_fixture",
        valid_from_ns=FIXTURE_NS,
        valid_until_ns=None,
        review_owner=None,
        review_status="not_required",
        refusal_reason=None,
        created_at_ns=FIXTURE_NS + 2,
        updated_at_ns=FIXTURE_NS + 2,
        non_claims=LICENSE_NON_CLAIMS,
    )
    return _with_overrides(license_.as_dict(), overrides)


def build_metadata_only_license_manifest(**overrides: Any) -> dict[str, object]:
    base = build_valid_license_manifest(
        license_manifest_id="synthetic_license_manifest_metadata_only_001",
        license_state=LicenseState.METADATA_ONLY.value,
        rights_scope=RightsScope.REVIEW_INTERNAL_ONLY.value,
        raw_storage_policy=RawStoragePolicy.METADATA_ONLY.value,
        derivative_policy=DerivativePolicy.DERIVED_METADATA_ONLY.value,
    )
    return _with_overrides(base, overrides)


def build_derived_only_license_manifest(**overrides: Any) -> dict[str, object]:
    base = build_valid_license_manifest(
        license_manifest_id="synthetic_license_manifest_derived_only_001",
        license_state=LicenseState.DERIVED_ONLY.value,
        rights_scope=RightsScope.DERIVED_ARTIFACTS_INTERNAL_ONLY.value,
        raw_storage_policy=RawStoragePolicy.DERIVED_FIELDS_ONLY.value,
        derivative_policy=DerivativePolicy.DERIVED_CLAIMS_ALLOWED_INTERNAL.value,
    )
    return _with_overrides(base, overrides)


def build_human_review_required_license_manifest(**overrides: Any) -> dict[str, object]:
    base = build_valid_license_manifest(
        license_manifest_id="synthetic_license_manifest_human_review_001",
        license_state=LicenseState.HUMAN_REVIEW_REQUIRED.value,
        raw_storage_policy=RawStoragePolicy.METADATA_ONLY.value,
        review_owner="synthetic_review_owner",
        review_status="human_review_required",
    )
    return _with_overrides(base, overrides)


def build_valid_source_license_pair() -> dict[str, object]:
    return {
        "source_manifest": build_valid_source_manifest(),
        "license_manifest": build_valid_license_manifest(),
    }


def _with_overrides(base: dict[str, object], overrides: dict[str, Any]) -> dict[str, object]:
    result = deepcopy(base)
    for key, value in overrides.items():
        result[key] = value.value if hasattr(value, "value") else value
    return result


__all__ = [
    "build_derived_only_license_manifest",
    "build_human_review_required_license_manifest",
    "build_metadata_only_license_manifest",
    "build_valid_license_manifest",
    "build_valid_source_license_pair",
    "build_valid_source_manifest",
]
