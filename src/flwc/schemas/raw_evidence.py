from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from enum import Enum
from typing import Any

from flwc.schemas.common import SchemaIssue, ValidatorStatus
from flwc.schemas.source_license import (
    LicenseState,
    RawStoragePolicy,
    RightsScope,
    SourceClass,
    SourceTrustTier,
)


class VaultScope(str, Enum):
    SYNTHETIC_FIXTURE_ONLY = "synthetic_fixture_only"
    METADATA_ONLY = "metadata_only"
    QUARANTINE_REVIEW = "quarantine_review"
    AUTHORIZED_SOURCE_FUTURE_NODE_ONLY = "authorized_source_future_node_only"


class RawTextRefPolicy(str, Enum):
    NO_RAW_TEXT_STORED = "no_raw_text_stored"
    RAW_HASH_ONLY = "raw_hash_only"
    RAW_TEXT_ALLOWED_INTERNAL = "raw_text_allowed_internal"
    DERIVED_FIELDS_ONLY = "derived_fields_only"
    QUARANTINE_ONLY = "quarantine_only"
    SYNTHETIC_FIXTURE_TEXT_ALLOWED = "synthetic_fixture_text_allowed"


class QuarantineStatus(str, Enum):
    NOT_REQUIRED = "not_required"
    QUARANTINED_FOR_LICENSE = "quarantined_for_license"
    QUARANTINED_FOR_PROMPT_INJECTION = "quarantined_for_prompt_injection"
    QUARANTINED_FOR_TIMESTAMP = "quarantined_for_timestamp"
    QUARANTINED_FOR_IDENTITY = "quarantined_for_identity"
    RELEASED_BY_REVIEW = "released_by_review"
    REJECTED = "rejected"


VAULT_STRING_FIELDS = (
    "vault_manifest_id",
    "producer_id",
    "producer_version",
    "evidence_record_hash_method",
    "evidence_record_digest",
    "lineage_digest",
)

VAULT_REF_LIST_FIELDS = ("source_manifest_refs", "license_manifest_refs")
VAULT_MAP_FIELDS = ("raw_storage_policy_summary", "retention_policy_summary", "prompt_injection_policy_summary")
VAULT_POSITIVE_INT_FIELDS = ("source_cutoff_ns", "created_at_ns")
VAULT_NONNEGATIVE_INT_FIELDS = ("evidence_record_count",)

RECORD_STRING_FIELDS = (
    "evidence_id",
    "source_manifest_ref",
    "license_manifest_ref",
    "source_id",
    "retention_policy",
    "source_url_or_doc_id",
    "source_document_id",
    "dedupe_hash",
    "lineage_digest",
)

RECORD_OPTIONAL_STRING_FIELDS = (
    "source_revision_id",
    "raw_text_hash",
    "derived_text_hash",
    "language",
    "country_or_region",
)

RECORD_REQUIRED_POSITIVE_INT_FIELDS = ("ingest_timestamp_ns", "available_from_ns", "compiler_seen_at_ns")
RECORD_OPTIONAL_POSITIVE_INT_FIELDS = ("publisher_timestamp_ns", "source_timestamp_ns")
RECORD_LIST_FIELDS = ("source_span_refs", "asset_class_scope")
RECORD_OPTIONAL_LIST_FIELDS = ("prompt_injection_flags",)

INDEX_STRING_FIELDS = (
    "source_document_id",
    "source_manifest_ref",
    "license_manifest_ref",
    "document_identity_key",
    "segment_hash_method",
    "segment_index_digest",
    "retention_policy",
)

INDEX_OPTIONAL_STRING_FIELDS = ("revision_id", "language", "document_hash")
INDEX_REQUIRED_POSITIVE_INT_FIELDS = ("available_from_ns", "segment_count")
INDEX_OPTIONAL_POSITIVE_INT_FIELDS = ("publisher_timestamp_ns", "source_timestamp_ns")

MANDATORY_RAW_EVIDENCE_NON_CLAIMS = (
    "synthetic_fixture_only",
    "not_real_source",
    "not_source_ingestion",
    "not_real_source_ingestion",
    "not_license_authority",
    "not_truth_authority",
    "not_market_data_authority",
    "not_runtime_authority",
    "not_trading_authority",
    "not_trade_signal",
    "not_order_intent",
    "not_position_sizing",
    "not_claim_ledger",
    "not_event_table",
)


@dataclass(frozen=True)
class FLWCRawEvidenceVaultManifestV1:
    vault_manifest_id: str
    vault_scope: VaultScope
    source_manifest_refs: tuple[str, ...]
    license_manifest_refs: tuple[str, ...]
    source_cutoff_ns: int
    created_at_ns: int
    producer_id: str
    producer_version: str
    raw_storage_policy_summary: tuple[tuple[str, str], ...]
    retention_policy_summary: tuple[tuple[str, str], ...]
    prompt_injection_policy_summary: tuple[tuple[str, str], ...]
    evidence_record_count: int
    evidence_record_hash_method: str
    evidence_record_digest: str
    lineage_digest: str
    validation_status: ValidatorStatus
    validator_summary_ref: str | None
    non_claims: tuple[str, ...]
    schema_version: str = "FLWCRawEvidenceVaultManifestV1"

    @classmethod
    def from_mapping(
        cls, value: object
    ) -> tuple["FLWCRawEvidenceVaultManifestV1 | None", tuple[SchemaIssue, ...]]:
        if not isinstance(value, Mapping):
            return None, (SchemaIssue("artifact_not_mapping", ("$",), "raw evidence vault manifest must be a JSON object"),)

        issues: list[SchemaIssue] = []
        schema_version = _require_exact_string(value, "schema_version", "FLWCRawEvidenceVaultManifestV1", issues)
        strings = {field: _require_string(value, field, issues) for field in VAULT_STRING_FIELDS}
        ref_lists = {field: _require_string_list(value, field, issues, non_empty=True) for field in VAULT_REF_LIST_FIELDS}
        summaries = {field: _require_string_map(value, field, issues, non_empty=True) for field in VAULT_MAP_FIELDS}
        positive_ints = {field: _require_positive_int(value, field, issues) for field in VAULT_POSITIVE_INT_FIELDS}
        nonnegative_ints = {
            field: _require_nonnegative_int(value, field, issues) for field in VAULT_NONNEGATIVE_INT_FIELDS
        }
        vault_scope = _require_enum(value, "vault_scope", VaultScope, issues)
        validation_status = _require_enum(value, "validation_status", ValidatorStatus, issues)
        validator_summary_ref = _require_optional_string(value, "validator_summary_ref", issues)
        non_claims = _require_string_list(value, "non_claims", issues, non_empty=True)

        if issues:
            return None, tuple(issues)

        return (
            cls(
                schema_version=schema_version,
                vault_manifest_id=strings["vault_manifest_id"],
                vault_scope=vault_scope,
                source_manifest_refs=ref_lists["source_manifest_refs"],
                license_manifest_refs=ref_lists["license_manifest_refs"],
                source_cutoff_ns=positive_ints["source_cutoff_ns"],
                created_at_ns=positive_ints["created_at_ns"],
                producer_id=strings["producer_id"],
                producer_version=strings["producer_version"],
                raw_storage_policy_summary=summaries["raw_storage_policy_summary"],
                retention_policy_summary=summaries["retention_policy_summary"],
                prompt_injection_policy_summary=summaries["prompt_injection_policy_summary"],
                evidence_record_count=nonnegative_ints["evidence_record_count"],
                evidence_record_hash_method=strings["evidence_record_hash_method"],
                evidence_record_digest=strings["evidence_record_digest"],
                lineage_digest=strings["lineage_digest"],
                validation_status=validation_status,
                validator_summary_ref=validator_summary_ref,
                non_claims=non_claims,
            ),
            (),
        )

    def as_dict(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "vault_manifest_id": self.vault_manifest_id,
            "vault_scope": self.vault_scope.value,
            "source_manifest_refs": list(self.source_manifest_refs),
            "license_manifest_refs": list(self.license_manifest_refs),
            "source_cutoff_ns": self.source_cutoff_ns,
            "created_at_ns": self.created_at_ns,
            "producer_id": self.producer_id,
            "producer_version": self.producer_version,
            "raw_storage_policy_summary": dict(self.raw_storage_policy_summary),
            "retention_policy_summary": dict(self.retention_policy_summary),
            "prompt_injection_policy_summary": dict(self.prompt_injection_policy_summary),
            "evidence_record_count": self.evidence_record_count,
            "evidence_record_hash_method": self.evidence_record_hash_method,
            "evidence_record_digest": self.evidence_record_digest,
            "lineage_digest": self.lineage_digest,
            "validation_status": self.validation_status.value,
            "validator_summary_ref": self.validator_summary_ref,
            "non_claims": list(self.non_claims),
        }


@dataclass(frozen=True)
class FLWCRawEvidenceRecordV1:
    evidence_id: str
    source_manifest_ref: str
    license_manifest_ref: str
    source_id: str
    source_class: SourceClass
    source_trust_tier: SourceTrustTier
    license_state: LicenseState
    rights_scope: RightsScope
    raw_storage_policy: RawStoragePolicy
    retention_policy: str
    source_url_or_doc_id: str
    source_revision_id: str | None
    source_document_id: str
    source_span_refs: tuple[str, ...]
    raw_text_hash: str | None
    raw_text_ref_policy: RawTextRefPolicy
    derived_text_hash: str | None
    publisher_timestamp_ns: int | None
    source_timestamp_ns: int | None
    ingest_timestamp_ns: int
    available_from_ns: int
    compiler_seen_at_ns: int
    language: str | None
    country_or_region: str | None
    asset_class_scope: tuple[str, ...]
    prompt_injection_flags: tuple[str, ...]
    quarantine_status: QuarantineStatus
    dedupe_hash: str
    lineage_digest: str
    validation_status: ValidatorStatus
    non_claims: tuple[str, ...]
    schema_version: str = "FLWCRawEvidenceRecordV1"

    @classmethod
    def from_mapping(cls, value: object) -> tuple["FLWCRawEvidenceRecordV1 | None", tuple[SchemaIssue, ...]]:
        if not isinstance(value, Mapping):
            return None, (SchemaIssue("artifact_not_mapping", ("$",), "raw evidence record must be a JSON object"),)

        issues: list[SchemaIssue] = []
        schema_version = _require_exact_string(value, "schema_version", "FLWCRawEvidenceRecordV1", issues)
        strings = {field: _require_string(value, field, issues) for field in RECORD_STRING_FIELDS}
        optional_strings = {field: _require_optional_string(value, field, issues) for field in RECORD_OPTIONAL_STRING_FIELDS}
        positive_ints = {field: _require_positive_int(value, field, issues) for field in RECORD_REQUIRED_POSITIVE_INT_FIELDS}
        optional_ints = {
            field: _require_optional_positive_int(value, field, issues) for field in RECORD_OPTIONAL_POSITIVE_INT_FIELDS
        }
        lists = {field: _require_string_list(value, field, issues, non_empty=True) for field in RECORD_LIST_FIELDS}
        optional_lists = {
            field: _require_string_list(value, field, issues, non_empty=False) for field in RECORD_OPTIONAL_LIST_FIELDS
        }
        source_class = _require_enum(value, "source_class", SourceClass, issues)
        source_trust_tier = _require_enum(value, "source_trust_tier", SourceTrustTier, issues)
        license_state = _require_enum(value, "license_state", LicenseState, issues)
        rights_scope = _require_enum(value, "rights_scope", RightsScope, issues)
        raw_storage_policy = _require_enum(value, "raw_storage_policy", RawStoragePolicy, issues)
        raw_text_ref_policy = _require_enum(value, "raw_text_ref_policy", RawTextRefPolicy, issues)
        quarantine_status = _require_enum(value, "quarantine_status", QuarantineStatus, issues)
        validation_status = _require_enum(value, "validation_status", ValidatorStatus, issues)
        non_claims = _require_string_list(value, "non_claims", issues, non_empty=True)

        if issues:
            return None, tuple(issues)

        return (
            cls(
                schema_version=schema_version,
                evidence_id=strings["evidence_id"],
                source_manifest_ref=strings["source_manifest_ref"],
                license_manifest_ref=strings["license_manifest_ref"],
                source_id=strings["source_id"],
                source_class=source_class,
                source_trust_tier=source_trust_tier,
                license_state=license_state,
                rights_scope=rights_scope,
                raw_storage_policy=raw_storage_policy,
                retention_policy=strings["retention_policy"],
                source_url_or_doc_id=strings["source_url_or_doc_id"],
                source_revision_id=optional_strings["source_revision_id"],
                source_document_id=strings["source_document_id"],
                source_span_refs=lists["source_span_refs"],
                raw_text_hash=optional_strings["raw_text_hash"],
                raw_text_ref_policy=raw_text_ref_policy,
                derived_text_hash=optional_strings["derived_text_hash"],
                publisher_timestamp_ns=optional_ints["publisher_timestamp_ns"],
                source_timestamp_ns=optional_ints["source_timestamp_ns"],
                ingest_timestamp_ns=positive_ints["ingest_timestamp_ns"],
                available_from_ns=positive_ints["available_from_ns"],
                compiler_seen_at_ns=positive_ints["compiler_seen_at_ns"],
                language=optional_strings["language"],
                country_or_region=optional_strings["country_or_region"],
                asset_class_scope=lists["asset_class_scope"],
                prompt_injection_flags=optional_lists["prompt_injection_flags"],
                quarantine_status=quarantine_status,
                dedupe_hash=strings["dedupe_hash"],
                lineage_digest=strings["lineage_digest"],
                validation_status=validation_status,
                non_claims=non_claims,
            ),
            (),
        )

    def as_dict(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "evidence_id": self.evidence_id,
            "source_manifest_ref": self.source_manifest_ref,
            "license_manifest_ref": self.license_manifest_ref,
            "source_id": self.source_id,
            "source_class": self.source_class.value,
            "source_trust_tier": self.source_trust_tier.value,
            "license_state": self.license_state.value,
            "rights_scope": self.rights_scope.value,
            "raw_storage_policy": self.raw_storage_policy.value,
            "retention_policy": self.retention_policy,
            "source_url_or_doc_id": self.source_url_or_doc_id,
            "source_revision_id": self.source_revision_id,
            "source_document_id": self.source_document_id,
            "source_span_refs": list(self.source_span_refs),
            "raw_text_hash": self.raw_text_hash,
            "raw_text_ref_policy": self.raw_text_ref_policy.value,
            "derived_text_hash": self.derived_text_hash,
            "publisher_timestamp_ns": self.publisher_timestamp_ns,
            "source_timestamp_ns": self.source_timestamp_ns,
            "ingest_timestamp_ns": self.ingest_timestamp_ns,
            "available_from_ns": self.available_from_ns,
            "compiler_seen_at_ns": self.compiler_seen_at_ns,
            "language": self.language,
            "country_or_region": self.country_or_region,
            "asset_class_scope": list(self.asset_class_scope),
            "prompt_injection_flags": list(self.prompt_injection_flags),
            "quarantine_status": self.quarantine_status.value,
            "dedupe_hash": self.dedupe_hash,
            "lineage_digest": self.lineage_digest,
            "validation_status": self.validation_status.value,
            "non_claims": list(self.non_claims),
        }


@dataclass(frozen=True)
class FLWCSourceDocumentIndexV1:
    source_document_id: str
    source_manifest_ref: str
    license_manifest_ref: str
    document_identity_key: str
    revision_id: str | None
    language: str | None
    publisher_timestamp_ns: int | None
    source_timestamp_ns: int | None
    available_from_ns: int
    segment_count: int
    segment_hash_method: str
    segment_index_digest: str
    document_hash: str | None
    raw_storage_policy: RawStoragePolicy
    retention_policy: str
    source_trust_tier: SourceTrustTier
    license_state: LicenseState
    rights_scope: RightsScope
    prompt_injection_flags: tuple[str, ...]
    validation_status: ValidatorStatus
    non_claims: tuple[str, ...]
    schema_version: str = "FLWCSourceDocumentIndexV1"

    @classmethod
    def from_mapping(cls, value: object) -> tuple["FLWCSourceDocumentIndexV1 | None", tuple[SchemaIssue, ...]]:
        if not isinstance(value, Mapping):
            return None, (SchemaIssue("artifact_not_mapping", ("$",), "source document index must be a JSON object"),)

        issues: list[SchemaIssue] = []
        schema_version = _require_exact_string(value, "schema_version", "FLWCSourceDocumentIndexV1", issues)
        strings = {field: _require_string(value, field, issues) for field in INDEX_STRING_FIELDS}
        optional_strings = {field: _require_optional_string(value, field, issues) for field in INDEX_OPTIONAL_STRING_FIELDS}
        positive_ints = {field: _require_positive_int(value, field, issues) for field in INDEX_REQUIRED_POSITIVE_INT_FIELDS}
        optional_ints = {
            field: _require_optional_positive_int(value, field, issues) for field in INDEX_OPTIONAL_POSITIVE_INT_FIELDS
        }
        raw_storage_policy = _require_enum(value, "raw_storage_policy", RawStoragePolicy, issues)
        source_trust_tier = _require_enum(value, "source_trust_tier", SourceTrustTier, issues)
        license_state = _require_enum(value, "license_state", LicenseState, issues)
        rights_scope = _require_enum(value, "rights_scope", RightsScope, issues)
        prompt_injection_flags = _require_string_list(value, "prompt_injection_flags", issues, non_empty=False)
        validation_status = _require_enum(value, "validation_status", ValidatorStatus, issues)
        non_claims = _require_string_list(value, "non_claims", issues, non_empty=True)

        if issues:
            return None, tuple(issues)

        return (
            cls(
                schema_version=schema_version,
                source_document_id=strings["source_document_id"],
                source_manifest_ref=strings["source_manifest_ref"],
                license_manifest_ref=strings["license_manifest_ref"],
                document_identity_key=strings["document_identity_key"],
                revision_id=optional_strings["revision_id"],
                language=optional_strings["language"],
                publisher_timestamp_ns=optional_ints["publisher_timestamp_ns"],
                source_timestamp_ns=optional_ints["source_timestamp_ns"],
                available_from_ns=positive_ints["available_from_ns"],
                segment_count=positive_ints["segment_count"],
                segment_hash_method=strings["segment_hash_method"],
                segment_index_digest=strings["segment_index_digest"],
                document_hash=optional_strings["document_hash"],
                raw_storage_policy=raw_storage_policy,
                retention_policy=strings["retention_policy"],
                source_trust_tier=source_trust_tier,
                license_state=license_state,
                rights_scope=rights_scope,
                prompt_injection_flags=prompt_injection_flags,
                validation_status=validation_status,
                non_claims=non_claims,
            ),
            (),
        )

    def as_dict(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "source_document_id": self.source_document_id,
            "source_manifest_ref": self.source_manifest_ref,
            "license_manifest_ref": self.license_manifest_ref,
            "document_identity_key": self.document_identity_key,
            "revision_id": self.revision_id,
            "language": self.language,
            "publisher_timestamp_ns": self.publisher_timestamp_ns,
            "source_timestamp_ns": self.source_timestamp_ns,
            "available_from_ns": self.available_from_ns,
            "segment_count": self.segment_count,
            "segment_hash_method": self.segment_hash_method,
            "segment_index_digest": self.segment_index_digest,
            "document_hash": self.document_hash,
            "raw_storage_policy": self.raw_storage_policy.value,
            "retention_policy": self.retention_policy,
            "source_trust_tier": self.source_trust_tier.value,
            "license_state": self.license_state.value,
            "rights_scope": self.rights_scope.value,
            "prompt_injection_flags": list(self.prompt_injection_flags),
            "validation_status": self.validation_status.value,
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


def _require_nonnegative_int(value: Mapping[str, Any], field_name: str, issues: list[SchemaIssue]) -> int:
    if _missing(value, field_name, issues):
        return 0
    field_value = value[field_name]
    if type(field_value) is not int or field_value < 0:
        issues.append(SchemaIssue("field_type_invalid", (field_name,), "expected non-negative integer"))
        return 0
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


def _require_string_map(
    value: Mapping[str, Any],
    field_name: str,
    issues: list[SchemaIssue],
    *,
    non_empty: bool,
) -> tuple[tuple[str, str], ...]:
    if _missing(value, field_name, issues):
        return ()
    field_value = value[field_name]
    if not isinstance(field_value, Mapping):
        issues.append(SchemaIssue("field_type_invalid", (field_name,), "expected map of non-empty strings"))
        return ()
    items: list[tuple[str, str]] = []
    for key, item in field_value.items():
        if not isinstance(key, str) or not key.strip() or not isinstance(item, str) or not item.strip():
            issues.append(SchemaIssue("field_type_invalid", (field_name,), "expected map of non-empty strings"))
            return ()
        items.append((key, item))
    if non_empty and not items:
        issues.append(SchemaIssue("required_map_empty", (field_name,), "expected non-empty map"))
    return tuple(sorted(items))


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
    "FLWCRawEvidenceRecordV1",
    "FLWCRawEvidenceVaultManifestV1",
    "FLWCSourceDocumentIndexV1",
    "MANDATORY_RAW_EVIDENCE_NON_CLAIMS",
    "QuarantineStatus",
    "RawTextRefPolicy",
    "VaultScope",
]
