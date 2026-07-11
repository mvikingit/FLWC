from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from enum import Enum
from typing import Any

from flwc.schemas.common import SchemaIssue


class SourceClass(str, Enum):
    OFFICIAL_SOURCE = "official_source"
    LICENSED_NEWS = "licensed_news"
    LICENSED_RESEARCH = "licensed_research"
    COMPANY_DISCLOSURE = "company_disclosure"
    EXCHANGE_DISCLOSURE = "exchange_disclosure"
    POLICY_DOCUMENT = "policy_document"
    AUTHORIZED_CALENDAR = "authorized_calendar"
    AUTHORIZED_VENDOR_FEED = "authorized_vendor_feed"
    MANUAL_REVIEW_NOTE = "manual_review_note"
    SYNTHETIC_FIXTURE = "synthetic_fixture"
    WEAK_SOURCE_OR_RUMOR = "weak_source_or_rumor"
    UNKNOWN = "unknown"


class SourceTrustTier(str, Enum):
    TIER_0_OFFICIAL_PRIMARY = "tier_0_official_primary"
    TIER_1_REGULATED_OR_EXCHANGE = "tier_1_regulated_or_exchange"
    TIER_2_LICENSED_PROFESSIONAL = "tier_2_licensed_professional"
    TIER_3_REPUTABLE_SECONDARY = "tier_3_reputable_secondary"
    TIER_4_MANUAL_REVIEW_ONLY = "tier_4_manual_review_only"
    TIER_5_WEAK_OR_RUMOR = "tier_5_weak_or_rumor"
    TIER_UNKNOWN = "tier_unknown"


class LicenseState(str, Enum):
    UNKNOWN = "unknown"
    ALLOWED_FULL_TEXT = "allowed_full_text"
    METADATA_ONLY = "metadata_only"
    DERIVED_ONLY = "derived_only"
    NO_STORAGE = "no_storage"
    HUMAN_REVIEW_REQUIRED = "human_review_required"
    EXPIRED = "expired"
    FORBIDDEN = "forbidden"


class RawStoragePolicy(str, Enum):
    METADATA_ONLY = "metadata_only"
    RAW_HASH_ONLY = "raw_hash_only"
    ALLOWED_FULL_TEXT = "allowed_full_text"
    DERIVED_FIELDS_ONLY = "derived_fields_only"
    NO_STORAGE = "no_storage"
    QUARANTINE_ONLY = "quarantine_only"
    HUMAN_REVIEW_REQUIRED = "human_review_required"


class RightsScope(str, Enum):
    RESEARCH_INTERNAL_ONLY = "research_internal_only"
    REVIEW_INTERNAL_ONLY = "review_internal_only"
    DERIVED_ARTIFACTS_INTERNAL_ONLY = "derived_artifacts_internal_only"
    REDISTRIBUTION_FORBIDDEN = "redistribution_forbidden"
    PUBLIC_REDISTRIBUTION_ALLOWED = "public_redistribution_allowed"
    RUNTIME_PAYLOAD_FORBIDDEN = "runtime_payload_forbidden"
    UNKNOWN = "unknown"


class SourceAccessMode(str, Enum):
    MANUAL_METADATA_ONLY = "manual_metadata_only"
    OFFLINE_FIXTURE = "offline_fixture"
    PUBLIC_WEB_FUTURE_AUTHORIZATION_REQUIRED = "public_web_future_authorization_required"
    LICENSED_TERMINAL_FUTURE_AUTHORIZATION_REQUIRED = "licensed_terminal_future_authorization_required"
    VENDOR_API_FUTURE_AUTHORIZATION_REQUIRED = "vendor_api_future_authorization_required"
    PAID_RESEARCH_FUTURE_AUTHORIZATION_REQUIRED = "paid_research_future_authorization_required"


class SourceStatus(str, Enum):
    PROPOSED = "proposed"
    ACCEPTED_METADATA_ONLY = "accepted_metadata_only"
    AUTHORIZED_BY_FUTURE_SOURCE_NODE = "authorized_by_future_source_node"
    HOLD_REVIEW = "hold_review"
    DEPRECATED = "deprecated"
    REVOKED = "revoked"
    REJECTED = "rejected"


class RedistributionPolicy(str, Enum):
    FORBIDDEN = "forbidden"
    INTERNAL_ONLY = "internal_only"
    PUBLIC_ALLOWED_IF_SOURCE_ALLOWS = "public_allowed_if_source_allows"
    UNKNOWN = "unknown"


class DerivativePolicy(str, Enum):
    DERIVED_METADATA_ONLY = "derived_metadata_only"
    DERIVED_CLAIMS_ALLOWED_INTERNAL = "derived_claims_allowed_internal"
    DERIVED_EVENTS_ALLOWED_INTERNAL = "derived_events_allowed_internal"
    DERIVED_TEXT_FORBIDDEN = "derived_text_forbidden"
    UNKNOWN = "unknown"


class RuntimePayloadPolicy(str, Enum):
    RAW_TEXT_FORBIDDEN = "raw_text_forbidden"
    DERIVED_FIELDS_ONLY = "derived_fields_only"
    CANDIDATE_PACKAGE_METADATA_ONLY = "candidate_package_metadata_only"
    FUTURE_REVIEW_REQUIRED = "future_review_required"


class PromptInjectionPolicy(str, Enum):
    NOT_APPLICABLE_METADATA_ONLY = "not_applicable_metadata_only"
    UNTRUSTED_TEXT_ISOLATED = "untrusted_text_isolated"
    PROMPT_INJECTION_SCAN_REQUIRED = "prompt_injection_scan_required"
    QUARANTINE_ON_SUSPECTED_INJECTION = "quarantine_on_suspected_injection"
    HUMAN_REVIEW_REQUIRED = "human_review_required"


SOURCE_REQUIRED_STRING_FIELDS = (
    "source_manifest_id",
    "source_id",
    "source_name",
    "source_owner_or_publisher",
    "source_url_or_doc_id",
    "publisher_timestamp_policy",
    "source_timestamp_policy",
    "revision_policy",
    "canonical_location_policy",
    "license_manifest_ref",
    "retention_policy",
    "dedupe_hash_method",
)

SOURCE_OPTIONAL_STRING_FIELDS = (
    "revision_id",
    "source_language",
    "country_or_region",
    "raw_text_hash",
)

SOURCE_REQUIRED_POSITIVE_INT_FIELDS = (
    "publisher_timestamp_ns",
    "source_timestamp_ns",
    "ingest_timestamp_ns",
    "available_from_ns",
    "compiler_seen_at_ns",
    "created_at_ns",
    "updated_at_ns",
)

LICENSE_REQUIRED_STRING_FIELDS = (
    "license_manifest_id",
    "source_id",
    "retention_policy",
    "quote_policy",
    "credential_reference_policy",
    "pii_policy",
    "review_status",
)

LICENSE_OPTIONAL_STRING_FIELDS = (
    "review_owner",
    "refusal_reason",
)

LICENSE_REQUIRED_BOOL_FIELDS = (
    "paid_access_required",
    "credential_required",
)

LICENSE_OPTIONAL_POSITIVE_INT_FIELDS = (
    "valid_from_ns",
    "valid_until_ns",
)

LICENSE_REQUIRED_POSITIVE_INT_FIELDS = (
    "created_at_ns",
    "updated_at_ns",
)

MANDATORY_SOURCE_NON_CLAIMS = (
    "not_source_access_authority",
    "not_license_authority",
    "not_truth_authority",
    "not_ingestion_authority",
    "not_runtime_authority",
    "not_trading_authority",
)

MANDATORY_SYNTHETIC_NON_CLAIMS = (
    "synthetic_fixture_only",
    "not_real_source",
    "not_source_ingestion",
    "not_truth_authority",
    "not_runtime_authority",
    "not_trade_signal",
)


@dataclass(frozen=True)
class FLWCSourceManifestV1:
    source_manifest_id: str
    source_id: str
    source_class: SourceClass
    source_name: str
    source_owner_or_publisher: str
    source_url_or_doc_id: str
    source_access_mode: SourceAccessMode
    source_trust_tier: SourceTrustTier
    publisher_timestamp_policy: str
    source_timestamp_policy: str
    revision_policy: str
    canonical_location_policy: str
    license_manifest_ref: str
    rights_scope: RightsScope
    retention_policy: str
    raw_storage_policy: RawStoragePolicy
    raw_text_hash_required: bool
    dedupe_hash_method: str
    revision_id: str | None
    source_language: str | None
    country_or_region: str | None
    asset_class_scope: tuple[str, ...]
    prompt_injection_policy: PromptInjectionPolicy
    status: SourceStatus
    publisher_timestamp_ns: int
    source_timestamp_ns: int
    ingest_timestamp_ns: int
    available_from_ns: int
    compiler_seen_at_ns: int
    created_at_ns: int
    updated_at_ns: int
    non_claims: tuple[str, ...]
    raw_text_hash: str | None = None
    schema_version: str = "FLWCSourceManifestV1"

    @classmethod
    def from_mapping(cls, value: object) -> tuple["FLWCSourceManifestV1 | None", tuple[SchemaIssue, ...]]:
        if not isinstance(value, Mapping):
            return None, (SchemaIssue("artifact_not_mapping", ("$",), "source manifest must be a JSON object"),)

        issues: list[SchemaIssue] = []
        schema_version = _require_exact_string(value, "schema_version", "FLWCSourceManifestV1", issues)
        strings = {field: _require_string(value, field, issues) for field in SOURCE_REQUIRED_STRING_FIELDS}
        optional_strings = {field: _require_optional_string(value, field, issues) for field in SOURCE_OPTIONAL_STRING_FIELDS}
        positive_ints = {field: _require_positive_int(value, field, issues) for field in SOURCE_REQUIRED_POSITIVE_INT_FIELDS}
        source_class = _require_enum(value, "source_class", SourceClass, issues)
        source_access_mode = _require_enum(value, "source_access_mode", SourceAccessMode, issues)
        source_trust_tier = _require_enum(value, "source_trust_tier", SourceTrustTier, issues)
        rights_scope = _require_enum(value, "rights_scope", RightsScope, issues)
        raw_storage_policy = _require_enum(value, "raw_storage_policy", RawStoragePolicy, issues)
        prompt_injection_policy = _require_enum(value, "prompt_injection_policy", PromptInjectionPolicy, issues)
        status = _require_enum(value, "status", SourceStatus, issues)
        raw_text_hash_required = _require_bool(value, "raw_text_hash_required", issues)
        asset_class_scope = _require_string_list(value, "asset_class_scope", issues, non_empty=True)
        non_claims = _require_string_list(value, "non_claims", issues, non_empty=True)

        if issues:
            return None, tuple(issues)

        return (
            cls(
                schema_version=schema_version,
                source_manifest_id=strings["source_manifest_id"],
                source_id=strings["source_id"],
                source_class=source_class,
                source_name=strings["source_name"],
                source_owner_or_publisher=strings["source_owner_or_publisher"],
                source_url_or_doc_id=strings["source_url_or_doc_id"],
                source_access_mode=source_access_mode,
                source_trust_tier=source_trust_tier,
                publisher_timestamp_policy=strings["publisher_timestamp_policy"],
                source_timestamp_policy=strings["source_timestamp_policy"],
                revision_policy=strings["revision_policy"],
                canonical_location_policy=strings["canonical_location_policy"],
                license_manifest_ref=strings["license_manifest_ref"],
                rights_scope=rights_scope,
                retention_policy=strings["retention_policy"],
                raw_storage_policy=raw_storage_policy,
                raw_text_hash_required=raw_text_hash_required,
                dedupe_hash_method=strings["dedupe_hash_method"],
                revision_id=optional_strings["revision_id"],
                source_language=optional_strings["source_language"],
                country_or_region=optional_strings["country_or_region"],
                asset_class_scope=asset_class_scope,
                prompt_injection_policy=prompt_injection_policy,
                status=status,
                publisher_timestamp_ns=positive_ints["publisher_timestamp_ns"],
                source_timestamp_ns=positive_ints["source_timestamp_ns"],
                ingest_timestamp_ns=positive_ints["ingest_timestamp_ns"],
                available_from_ns=positive_ints["available_from_ns"],
                compiler_seen_at_ns=positive_ints["compiler_seen_at_ns"],
                created_at_ns=positive_ints["created_at_ns"],
                updated_at_ns=positive_ints["updated_at_ns"],
                non_claims=non_claims,
                raw_text_hash=optional_strings["raw_text_hash"],
            ),
            (),
        )

    def as_dict(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "source_manifest_id": self.source_manifest_id,
            "source_id": self.source_id,
            "source_class": self.source_class.value,
            "source_name": self.source_name,
            "source_owner_or_publisher": self.source_owner_or_publisher,
            "source_url_or_doc_id": self.source_url_or_doc_id,
            "source_access_mode": self.source_access_mode.value,
            "source_trust_tier": self.source_trust_tier.value,
            "publisher_timestamp_policy": self.publisher_timestamp_policy,
            "source_timestamp_policy": self.source_timestamp_policy,
            "revision_policy": self.revision_policy,
            "canonical_location_policy": self.canonical_location_policy,
            "license_manifest_ref": self.license_manifest_ref,
            "rights_scope": self.rights_scope.value,
            "retention_policy": self.retention_policy,
            "raw_storage_policy": self.raw_storage_policy.value,
            "raw_text_hash_required": self.raw_text_hash_required,
            "dedupe_hash_method": self.dedupe_hash_method,
            "revision_id": self.revision_id,
            "source_language": self.source_language,
            "country_or_region": self.country_or_region,
            "asset_class_scope": list(self.asset_class_scope),
            "prompt_injection_policy": self.prompt_injection_policy.value,
            "status": self.status.value,
            "publisher_timestamp_ns": self.publisher_timestamp_ns,
            "source_timestamp_ns": self.source_timestamp_ns,
            "ingest_timestamp_ns": self.ingest_timestamp_ns,
            "available_from_ns": self.available_from_ns,
            "compiler_seen_at_ns": self.compiler_seen_at_ns,
            "created_at_ns": self.created_at_ns,
            "updated_at_ns": self.updated_at_ns,
            "non_claims": list(self.non_claims),
            "raw_text_hash": self.raw_text_hash,
        }


@dataclass(frozen=True)
class FLWCLicenseManifestV1:
    license_manifest_id: str
    source_id: str
    license_state: LicenseState
    rights_scope: RightsScope
    raw_storage_policy: RawStoragePolicy
    retention_policy: str
    redistribution_policy: RedistributionPolicy
    derivative_policy: DerivativePolicy
    quote_policy: str
    runtime_payload_policy: RuntimePayloadPolicy
    paid_access_required: bool
    credential_required: bool
    credential_reference_policy: str
    pii_policy: str
    valid_from_ns: int | None
    valid_until_ns: int | None
    review_owner: str | None
    review_status: str
    refusal_reason: str | None
    created_at_ns: int
    updated_at_ns: int
    non_claims: tuple[str, ...]
    schema_version: str = "FLWCLicenseManifestV1"

    @classmethod
    def from_mapping(cls, value: object) -> tuple["FLWCLicenseManifestV1 | None", tuple[SchemaIssue, ...]]:
        if not isinstance(value, Mapping):
            return None, (SchemaIssue("artifact_not_mapping", ("$",), "license manifest must be a JSON object"),)

        issues: list[SchemaIssue] = []
        schema_version = _require_exact_string(value, "schema_version", "FLWCLicenseManifestV1", issues)
        strings = {field: _require_string(value, field, issues) for field in LICENSE_REQUIRED_STRING_FIELDS}
        optional_strings = {field: _require_optional_string(value, field, issues) for field in LICENSE_OPTIONAL_STRING_FIELDS}
        bools = {field: _require_bool(value, field, issues) for field in LICENSE_REQUIRED_BOOL_FIELDS}
        optional_ints = {field: _require_optional_positive_int(value, field, issues) for field in LICENSE_OPTIONAL_POSITIVE_INT_FIELDS}
        positive_ints = {field: _require_positive_int(value, field, issues) for field in LICENSE_REQUIRED_POSITIVE_INT_FIELDS}
        license_state = _require_enum(value, "license_state", LicenseState, issues)
        rights_scope = _require_enum(value, "rights_scope", RightsScope, issues)
        raw_storage_policy = _require_enum(value, "raw_storage_policy", RawStoragePolicy, issues)
        redistribution_policy = _require_enum(value, "redistribution_policy", RedistributionPolicy, issues)
        derivative_policy = _require_enum(value, "derivative_policy", DerivativePolicy, issues)
        runtime_payload_policy = _require_enum(value, "runtime_payload_policy", RuntimePayloadPolicy, issues)
        non_claims = _require_string_list(value, "non_claims", issues, non_empty=True)

        if issues:
            return None, tuple(issues)

        return (
            cls(
                schema_version=schema_version,
                license_manifest_id=strings["license_manifest_id"],
                source_id=strings["source_id"],
                license_state=license_state,
                rights_scope=rights_scope,
                raw_storage_policy=raw_storage_policy,
                retention_policy=strings["retention_policy"],
                redistribution_policy=redistribution_policy,
                derivative_policy=derivative_policy,
                quote_policy=strings["quote_policy"],
                runtime_payload_policy=runtime_payload_policy,
                paid_access_required=bools["paid_access_required"],
                credential_required=bools["credential_required"],
                credential_reference_policy=strings["credential_reference_policy"],
                pii_policy=strings["pii_policy"],
                valid_from_ns=optional_ints["valid_from_ns"],
                valid_until_ns=optional_ints["valid_until_ns"],
                review_owner=optional_strings["review_owner"],
                review_status=strings["review_status"],
                refusal_reason=optional_strings["refusal_reason"],
                created_at_ns=positive_ints["created_at_ns"],
                updated_at_ns=positive_ints["updated_at_ns"],
                non_claims=non_claims,
            ),
            (),
        )

    def as_dict(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "license_manifest_id": self.license_manifest_id,
            "source_id": self.source_id,
            "license_state": self.license_state.value,
            "rights_scope": self.rights_scope.value,
            "raw_storage_policy": self.raw_storage_policy.value,
            "retention_policy": self.retention_policy,
            "redistribution_policy": self.redistribution_policy.value,
            "derivative_policy": self.derivative_policy.value,
            "quote_policy": self.quote_policy,
            "runtime_payload_policy": self.runtime_payload_policy.value,
            "paid_access_required": self.paid_access_required,
            "credential_required": self.credential_required,
            "credential_reference_policy": self.credential_reference_policy,
            "pii_policy": self.pii_policy,
            "valid_from_ns": self.valid_from_ns,
            "valid_until_ns": self.valid_until_ns,
            "review_owner": self.review_owner,
            "review_status": self.review_status,
            "refusal_reason": self.refusal_reason,
            "created_at_ns": self.created_at_ns,
            "updated_at_ns": self.updated_at_ns,
            "non_claims": list(self.non_claims),
        }


def _field(prefix: str | None, field_name: str) -> str:
    return f"{prefix}.{field_name}" if prefix else field_name


def _missing(value: Mapping[str, Any], field_name: str, issues: list[SchemaIssue], *, field_prefix: str | None = None) -> bool:
    if field_name not in value:
        issues.append(SchemaIssue("required_field_missing", (_field(field_prefix, field_name),), "required field missing"))
        return True
    return False


def _require_string(value: Mapping[str, Any], field_name: str, issues: list[SchemaIssue], *, field_prefix: str | None = None) -> str:
    if _missing(value, field_name, issues, field_prefix=field_prefix):
        return ""
    field_value = value[field_name]
    if not isinstance(field_value, str) or not field_value.strip():
        issues.append(SchemaIssue("field_type_invalid", (_field(field_prefix, field_name),), "expected non-empty string"))
        return ""
    return field_value


def _require_exact_string(
    value: Mapping[str, Any],
    field_name: str,
    expected: str,
    issues: list[SchemaIssue],
    *,
    field_prefix: str | None = None,
) -> str:
    field_value = _require_string(value, field_name, issues, field_prefix=field_prefix)
    if field_value and field_value != expected:
        issues.append(SchemaIssue("schema_version_invalid", (_field(field_prefix, field_name),), f"expected {expected}"))
    return field_value


def _require_optional_string(
    value: Mapping[str, Any], field_name: str, issues: list[SchemaIssue], *, field_prefix: str | None = None
) -> str | None:
    if field_name not in value:
        return None
    field_value = value[field_name]
    if field_value is None:
        return None
    if not isinstance(field_value, str) or not field_value.strip():
        issues.append(SchemaIssue("field_type_invalid", (_field(field_prefix, field_name),), "expected string or null"))
        return None
    return field_value


def _require_bool(value: Mapping[str, Any], field_name: str, issues: list[SchemaIssue]) -> bool:
    if _missing(value, field_name, issues):
        return False
    field_value = value[field_name]
    if type(field_value) is not bool:
        issues.append(SchemaIssue("field_type_invalid", (field_name,), "expected boolean"))
        return False
    return field_value


def _require_positive_int(value: Mapping[str, Any], field_name: str, issues: list[SchemaIssue]) -> int:
    if _missing(value, field_name, issues):
        return 0
    field_value = value[field_name]
    if type(field_value) is not int or field_value <= 0:
        issues.append(SchemaIssue("field_type_invalid", (field_name,), "expected positive integer"))
        return 0
    return field_value


def _require_optional_positive_int(value: Mapping[str, Any], field_name: str, issues: list[SchemaIssue]) -> int | None:
    if field_name not in value:
        return None
    field_value = value[field_name]
    if field_value is None:
        return None
    if type(field_value) is not int or field_value <= 0:
        issues.append(SchemaIssue("field_type_invalid", (field_name,), "expected positive integer or null"))
        return None
    return field_value


def _require_string_list(
    value: Mapping[str, Any],
    field_name: str,
    issues: list[SchemaIssue],
    *,
    non_empty: bool,
) -> tuple[str, ...]:
    if _missing(value, field_name, issues):
        return ()
    field_value = value[field_name]
    if not isinstance(field_value, list) or any(not isinstance(item, str) or not item.strip() for item in field_value):
        issues.append(SchemaIssue("field_type_invalid", (field_name,), "expected list of non-empty strings"))
        return ()
    if non_empty and not field_value:
        issues.append(SchemaIssue("required_list_empty", (field_name,), "expected non-empty list"))
    return tuple(field_value)


def _require_enum(value: Mapping[str, Any], field_name: str, enum_type: type[Enum], issues: list[SchemaIssue]) -> Any:
    raw_value = _require_string(value, field_name, issues)
    if not raw_value:
        return None
    try:
        return enum_type(raw_value)
    except ValueError:
        issues.append(SchemaIssue("enum_value_invalid", (field_name,), f"unsupported value {raw_value}"))
        return None


__all__ = [
    "DerivativePolicy",
    "FLWCLicenseManifestV1",
    "FLWCSourceManifestV1",
    "LicenseState",
    "MANDATORY_SOURCE_NON_CLAIMS",
    "MANDATORY_SYNTHETIC_NON_CLAIMS",
    "PromptInjectionPolicy",
    "RawStoragePolicy",
    "RedistributionPolicy",
    "RightsScope",
    "RuntimePayloadPolicy",
    "SourceAccessMode",
    "SourceClass",
    "SourceStatus",
    "SourceTrustTier",
]
