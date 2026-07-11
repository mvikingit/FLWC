from __future__ import annotations

import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from flwc.schemas.common import (
    B0_VALIDATOR_NON_CLAIMS,
    SchemaIssue,
    ValidatorResult,
    ValidatorStatus,
    ValidatorSummary,
    ensure_strings,
)
from flwc.schemas.source_license import (
    FLWCLicenseManifestV1,
    FLWCSourceManifestV1,
    LicenseState,
    MANDATORY_SOURCE_NON_CLAIMS,
    MANDATORY_SYNTHETIC_NON_CLAIMS,
    PromptInjectionPolicy,
    RawStoragePolicy,
    RightsScope,
    RuntimePayloadPolicy,
    SourceClass,
    SourceStatus,
    SourceTrustTier,
)
from flwc.validators.core import contains_secret_like_value


SCHEMA_REASON_PRIORITY = (
    "artifact_not_mapping",
    "schema_version_invalid",
    "required_field_missing",
    "field_type_invalid",
    "enum_value_invalid",
    "required_list_empty",
)

RAW_TEXT_STORAGE_POLICIES = frozenset({RawStoragePolicy.ALLOWED_FULL_TEXT, RawStoragePolicy.RAW_HASH_ONLY})
RAW_OR_DERIVED_STORAGE_POLICIES = frozenset(
    {RawStoragePolicy.ALLOWED_FULL_TEXT, RawStoragePolicy.RAW_HASH_ONLY, RawStoragePolicy.DERIVED_FIELDS_ONLY}
)
REVIEW_RETENTION_VALUES = frozenset({"unknown", "ambiguous", "human_review_required", "review_required"})
B1_SOURCE_POLICY_SENTINELS = {
    "publisher_timestamp_policy": frozenset({"fixture_timestamp_available"}),
    "source_timestamp_policy": frozenset({"fixture_timestamp_available"}),
    "revision_policy": frozenset({"fixture_revision_static"}),
    "canonical_location_policy": frozenset({"fixture_doc_id_only"}),
}
B1_LICENSE_POLICY_SENTINELS = {
    "quote_policy": frozenset({"synthetic_fixture_quotes_not_applicable"}),
    "credential_reference_policy": frozenset({"no_credentials_required"}),
    "pii_policy": frozenset({"no_pii_in_synthetic_fixture"}),
    "review_status": frozenset({"not_required", "human_review_required"}),
}
AUTHORITY_ESCALATION_POLICY_MARKERS = (
    "allowed",
    "api",
    "authorization",
    "authorized",
    "authority",
    "credential",
    "enabled",
    "export",
    "future",
    "ingest",
    "override",
    "paid",
    "permission",
    "permit",
    "prompt",
    "real_source",
    "real-source",
    "runtime",
    "scrape",
    "secret",
    "storage",
    "token",
    "vendor",
)


def validate_source_manifest(source_manifest: Mapping[str, Any]) -> dict[str, Any]:
    source, source_issues = FLWCSourceManifestV1.from_mapping(source_manifest)
    results: list[ValidatorResult] = []

    _append_schema_result(results, source_manifest, source_issues, "source_manifest_schema_validator")
    _append_source_manifest_ref_result(results, source_manifest)
    _append_license_manifest_ref_result(results, source_manifest)
    _append_source_rights_scope_result(results, source_manifest, source)
    _append_source_raw_storage_policy_result(results, source_manifest, source)
    _append_retention_policy_result(results, source_manifest, ("retention_policy",))
    _append_source_timestamp_policy_result(results, source_manifest, source)
    _append_source_policy_string_result(results, source_manifest, source)
    _append_raw_hash_reference_result(results, source_manifest)
    _append_credential_leak_result(results, source_manifest)
    _append_prompt_injection_policy_result(results, source_manifest, source)
    _append_non_claims_result(results, source_manifest, "source")
    _append_source_synthetic_fixture_scope_result(results, source_manifest, source)

    return _summary(source_manifest, results, "source")


def validate_license_manifest(license_manifest: Mapping[str, Any]) -> dict[str, Any]:
    license_, license_issues = FLWCLicenseManifestV1.from_mapping(license_manifest)
    results: list[ValidatorResult] = []

    _append_schema_result(results, license_manifest, license_issues, "license_manifest_schema_validator")
    _append_license_manifest_identity_result(results, license_manifest)
    _append_license_state_result(results, license_manifest, license_)
    _append_license_rights_scope_result(results, license_manifest, license_)
    _append_license_raw_storage_policy_result(results, license_manifest, license_)
    _append_retention_policy_result(results, license_manifest, ("retention_policy",))
    _append_license_temporal_result(results, license_manifest, license_)
    _append_license_policy_string_result(results, license_manifest, license_)
    _append_credential_leak_result(results, license_manifest)
    _append_no_runtime_payload_raw_text_result(results, license_manifest, license_)
    _append_non_claims_result(results, license_manifest, "license")

    return _summary(license_manifest, results, "license")


def validate_source_license_pair(source_manifest: Mapping[str, Any], license_manifest: Mapping[str, Any]) -> dict[str, Any]:
    source, source_issues = FLWCSourceManifestV1.from_mapping(source_manifest)
    license_, license_issues = FLWCLicenseManifestV1.from_mapping(license_manifest)
    artifact = {"source_manifest": source_manifest, "license_manifest": license_manifest}
    results: list[ValidatorResult] = []

    _append_schema_result(results, artifact, source_issues, "source_manifest_schema_validator", artifact_schema_version="FLWCSourceManifestV1")
    _append_schema_result(
        results,
        artifact,
        license_issues,
        "license_manifest_schema_validator",
        artifact_schema_version="FLWCLicenseManifestV1",
    )
    _append_source_manifest_ref_result(results, artifact, source_manifest=source_manifest)
    _append_license_manifest_identity_result(results, artifact, license_manifest=license_manifest)
    _append_source_license_pairing_result(results, artifact, source_manifest, license_manifest)
    _append_license_state_result(results, artifact, license_)
    _append_pair_rights_scope_result(results, artifact, source, license_)
    _append_pair_raw_storage_policy_result(results, artifact, source, license_)
    _append_retention_policy_result(results, artifact, ("source_manifest.retention_policy", "license_manifest.retention_policy"))
    _append_source_timestamp_policy_result(results, artifact, source, field_prefix="source_manifest")
    _append_source_policy_string_result(results, artifact, source, field_prefix="source_manifest")
    _append_license_policy_string_result(results, artifact, license_, field_prefix="license_manifest")
    _append_raw_hash_reference_result(results, artifact, source_manifest=source_manifest, field_prefix="source_manifest")
    _append_credential_leak_result(results, artifact)
    _append_prompt_injection_policy_result(results, artifact, source, field_prefix="source_manifest")
    _append_no_runtime_payload_raw_text_result(results, artifact, license_, field_prefix="license_manifest")
    _append_pair_non_claims_result(results, artifact, source_manifest, license_manifest)
    _append_pair_synthetic_fixture_scope_result(results, artifact, source, license_)

    return _summary(artifact, results, "source_license_pair")


def validate_source_manifest_file(path: str | Path) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as fh:
        return validate_source_manifest(json.load(fh))


def validate_license_manifest_file(path: str | Path) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as fh:
        return validate_license_manifest(json.load(fh))


def validate_source_license_pair_file(path: str | Path) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as fh:
        fixture = json.load(fh)
    return validate_source_license_pair(fixture["source_manifest"], fixture["license_manifest"])


def _append_schema_result(
    results: list[ValidatorResult],
    artifact: Mapping[str, Any],
    issues: tuple[SchemaIssue, ...],
    validator_id: str,
    *,
    artifact_schema_version: str | None = None,
) -> None:
    if not issues:
        results.append(_accept(artifact, validator_id, artifact_schema_version=artifact_schema_version))
        return
    results.append(
        _reject(
            artifact,
            validator_id,
            _first_schema_reason(issues),
            _issue_detail(issues),
            _issue_fields(issues),
            artifact_schema_version=artifact_schema_version,
        )
    )


def _append_source_manifest_ref_result(
    results: list[ValidatorResult],
    artifact: Mapping[str, Any],
    *,
    source_manifest: Mapping[str, Any] | None = None,
) -> None:
    manifest = source_manifest or artifact
    fields = tuple(field for field in ("source_manifest_id", "source_id") if not _is_non_empty_string(manifest.get(field)))
    if fields:
        results.append(_reject(artifact, "source_manifest_ref_validator", "source_manifest_identity_invalid", fields=fields))
        return
    results.append(_accept(artifact, "source_manifest_ref_validator"))


def _append_license_manifest_ref_result(results: list[ValidatorResult], source_manifest: Mapping[str, Any]) -> None:
    if not _is_non_empty_string(source_manifest.get("license_manifest_ref")):
        results.append(
            _reject(source_manifest, "license_manifest_ref_validator", "license_manifest_ref_missing", fields=("license_manifest_ref",))
        )
        return
    results.append(_accept(source_manifest, "license_manifest_ref_validator"))


def _append_license_manifest_identity_result(
    results: list[ValidatorResult],
    artifact: Mapping[str, Any],
    *,
    license_manifest: Mapping[str, Any] | None = None,
) -> None:
    manifest = license_manifest or artifact
    fields = tuple(field for field in ("license_manifest_id", "source_id") if not _is_non_empty_string(manifest.get(field)))
    if fields:
        results.append(_reject(artifact, "license_manifest_ref_validator", "license_manifest_identity_invalid", fields=fields))
        return
    results.append(_accept(artifact, "license_manifest_ref_validator"))


def _append_source_license_pairing_result(
    results: list[ValidatorResult],
    artifact: Mapping[str, Any],
    source_manifest: Mapping[str, Any],
    license_manifest: Mapping[str, Any],
) -> None:
    source_license_ref = source_manifest.get("license_manifest_ref")
    license_id = license_manifest.get("license_manifest_id")
    if not _is_non_empty_string(source_license_ref):
        results.append(
            _reject(artifact, "source_license_pairing_validator", "license_manifest_ref_missing", fields=("source_manifest.license_manifest_ref",))
        )
        return
    if not _is_non_empty_string(license_id) or source_license_ref != license_id:
        results.append(
            _reject(
                artifact,
                "source_license_pairing_validator",
                "license_manifest_ref_unresolved",
                fields=("source_manifest.license_manifest_ref", "license_manifest.license_manifest_id"),
            )
        )
        return
    if source_manifest.get("source_id") != license_manifest.get("source_id"):
        results.append(
            _reject(
                artifact,
                "source_license_pairing_validator",
                "source_license_source_id_mismatch",
                fields=("source_manifest.source_id", "license_manifest.source_id"),
            )
        )
        return
    results.append(_accept(artifact, "source_license_pairing_validator"))


def _append_license_state_result(
    results: list[ValidatorResult], artifact: Mapping[str, Any], license_: FLWCLicenseManifestV1 | None
) -> None:
    if license_ is None:
        results.append(_reject(artifact, "license_state_validator", "license_manifest_missing_or_invalid", fields=("license_state",)))
        return
    if license_.license_state == LicenseState.FORBIDDEN:
        results.append(_reject(artifact, "license_state_validator", "forbidden_license_state", fields=("license_state",)))
        return
    if license_.license_state == LicenseState.EXPIRED:
        results.append(_reject(artifact, "license_state_validator", "expired_license_state_for_new_promotion", fields=("license_state",)))
        return
    if license_.license_state == LicenseState.UNKNOWN and license_.raw_storage_policy in RAW_TEXT_STORAGE_POLICIES:
        results.append(
            _reject(
                artifact,
                "license_state_validator",
                "unknown_license_raw_storage_requested",
                fields=("license_state", "raw_storage_policy"),
            )
        )
        return
    if license_.license_state in {LicenseState.UNKNOWN, LicenseState.HUMAN_REVIEW_REQUIRED}:
        results.append(_hold(artifact, "license_state_validator", "license_state_requires_review", fields=("license_state",)))
        return
    results.append(_accept(artifact, "license_state_validator"))


def _append_source_rights_scope_result(
    results: list[ValidatorResult], artifact: Mapping[str, Any], source: FLWCSourceManifestV1 | None
) -> None:
    if source is None:
        results.append(_reject(artifact, "rights_scope_validator", "source_manifest_missing_or_invalid", fields=("rights_scope",)))
        return
    if source.rights_scope == RightsScope.UNKNOWN:
        results.append(_hold(artifact, "rights_scope_validator", "rights_scope_unknown_requires_review", fields=("rights_scope",)))
        return
    if source.raw_storage_policy == RawStoragePolicy.ALLOWED_FULL_TEXT and source.rights_scope == RightsScope.DERIVED_ARTIFACTS_INTERNAL_ONLY:
        results.append(
            _reject(
                artifact,
                "rights_scope_validator",
                "rights_scope_raw_storage_incompatible",
                fields=("rights_scope", "raw_storage_policy"),
            )
        )
        return
    results.append(_accept(artifact, "rights_scope_validator"))


def _append_license_rights_scope_result(
    results: list[ValidatorResult], artifact: Mapping[str, Any], license_: FLWCLicenseManifestV1 | None
) -> None:
    if license_ is None:
        results.append(_reject(artifact, "rights_scope_validator", "license_manifest_missing_or_invalid", fields=("rights_scope",)))
        return
    if license_.rights_scope == RightsScope.UNKNOWN:
        results.append(_hold(artifact, "rights_scope_validator", "rights_scope_unknown_requires_review", fields=("rights_scope",)))
        return
    if license_.raw_storage_policy == RawStoragePolicy.ALLOWED_FULL_TEXT and license_.rights_scope == RightsScope.DERIVED_ARTIFACTS_INTERNAL_ONLY:
        results.append(
            _reject(
                artifact,
                "rights_scope_validator",
                "rights_scope_raw_storage_incompatible",
                fields=("rights_scope", "raw_storage_policy"),
            )
        )
        return
    results.append(_accept(artifact, "rights_scope_validator"))


def _append_pair_rights_scope_result(
    results: list[ValidatorResult],
    artifact: Mapping[str, Any],
    source: FLWCSourceManifestV1 | None,
    license_: FLWCLicenseManifestV1 | None,
) -> None:
    if source is None or license_ is None:
        results.append(_reject(artifact, "rights_scope_validator", "source_or_license_manifest_invalid", fields=("rights_scope",)))
        return
    if source.rights_scope != license_.rights_scope:
        results.append(
            _reject(
                artifact,
                "rights_scope_validator",
                "rights_scope_mismatch",
                fields=("source_manifest.rights_scope", "license_manifest.rights_scope"),
            )
        )
        return
    if source.rights_scope == RightsScope.UNKNOWN:
        results.append(_hold(artifact, "rights_scope_validator", "rights_scope_unknown_requires_review", fields=("rights_scope",)))
        return
    if source.raw_storage_policy == RawStoragePolicy.ALLOWED_FULL_TEXT and source.rights_scope == RightsScope.DERIVED_ARTIFACTS_INTERNAL_ONLY:
        results.append(
            _reject(
                artifact,
                "rights_scope_validator",
                "rights_scope_raw_storage_incompatible",
                fields=("source_manifest.rights_scope", "source_manifest.raw_storage_policy"),
            )
        )
        return
    results.append(_accept(artifact, "rights_scope_validator"))


def _append_source_raw_storage_policy_result(
    results: list[ValidatorResult], artifact: Mapping[str, Any], source: FLWCSourceManifestV1 | None
) -> None:
    if source is None:
        results.append(_reject(artifact, "raw_storage_policy_validator", "source_manifest_missing_or_invalid", fields=("raw_storage_policy",)))
        return
    if source.raw_storage_policy in {RawStoragePolicy.HUMAN_REVIEW_REQUIRED, RawStoragePolicy.QUARANTINE_ONLY}:
        results.append(_hold(artifact, "raw_storage_policy_validator", "raw_storage_policy_requires_review", fields=("raw_storage_policy",)))
        return
    results.append(_accept(artifact, "raw_storage_policy_validator"))


def _append_license_raw_storage_policy_result(
    results: list[ValidatorResult], artifact: Mapping[str, Any], license_: FLWCLicenseManifestV1 | None
) -> None:
    if license_ is None:
        results.append(_reject(artifact, "raw_storage_policy_validator", "license_manifest_missing_or_invalid", fields=("raw_storage_policy",)))
        return
    if _storage_policy_incompatible_with_license(license_.raw_storage_policy, license_.license_state):
        results.append(
            _reject(
                artifact,
                "raw_storage_policy_validator",
                "raw_storage_policy_incompatible_with_license_state",
                fields=("raw_storage_policy", "license_state"),
            )
        )
        return
    if license_.raw_storage_policy in {RawStoragePolicy.HUMAN_REVIEW_REQUIRED, RawStoragePolicy.QUARANTINE_ONLY}:
        results.append(_hold(artifact, "raw_storage_policy_validator", "raw_storage_policy_requires_review", fields=("raw_storage_policy",)))
        return
    results.append(_accept(artifact, "raw_storage_policy_validator"))


def _append_pair_raw_storage_policy_result(
    results: list[ValidatorResult],
    artifact: Mapping[str, Any],
    source: FLWCSourceManifestV1 | None,
    license_: FLWCLicenseManifestV1 | None,
) -> None:
    if source is None or license_ is None:
        results.append(_reject(artifact, "raw_storage_policy_validator", "source_or_license_manifest_invalid", fields=("raw_storage_policy",)))
        return
    if source.raw_storage_policy != license_.raw_storage_policy:
        results.append(
            _reject(
                artifact,
                "raw_storage_policy_validator",
                "raw_storage_policy_mismatch",
                fields=("source_manifest.raw_storage_policy", "license_manifest.raw_storage_policy"),
            )
        )
        return
    if _storage_policy_incompatible_with_license(source.raw_storage_policy, license_.license_state):
        results.append(
            _reject(
                artifact,
                "raw_storage_policy_validator",
                "raw_storage_policy_incompatible_with_license_state",
                fields=("raw_storage_policy", "license_state"),
            )
        )
        return
    if source.raw_storage_policy in {RawStoragePolicy.HUMAN_REVIEW_REQUIRED, RawStoragePolicy.QUARANTINE_ONLY}:
        results.append(_hold(artifact, "raw_storage_policy_validator", "raw_storage_policy_requires_review", fields=("raw_storage_policy",)))
        return
    results.append(_accept(artifact, "raw_storage_policy_validator"))


def _append_retention_policy_result(
    results: list[ValidatorResult], artifact: Mapping[str, Any], field_refs: tuple[str, ...]
) -> None:
    invalid_fields: list[str] = []
    review_fields: list[str] = []
    for field_ref in field_refs:
        value = _nested_get(artifact, field_ref)
        if not _is_non_empty_string(value):
            invalid_fields.append(field_ref)
        elif str(value).strip().lower() in REVIEW_RETENTION_VALUES:
            review_fields.append(field_ref)
    if invalid_fields:
        results.append(_reject(artifact, "retention_policy_validator", "retention_policy_missing", fields=tuple(invalid_fields)))
        return
    if review_fields:
        results.append(_hold(artifact, "retention_policy_validator", "retention_policy_requires_review", fields=tuple(review_fields)))
        return
    results.append(_accept(artifact, "retention_policy_validator"))


def _append_source_timestamp_policy_result(
    results: list[ValidatorResult],
    artifact: Mapping[str, Any],
    source: FLWCSourceManifestV1 | None,
    *,
    field_prefix: str | None = None,
) -> None:
    fields = (
        "publisher_timestamp_ns",
        "source_timestamp_ns",
        "ingest_timestamp_ns",
        "available_from_ns",
        "compiler_seen_at_ns",
        "created_at_ns",
        "updated_at_ns",
    )
    invalid_fields = tuple(_prefixed(field_prefix, field) for field in fields if not _is_positive_int(_nested_get(artifact, _prefixed(field_prefix, field))))
    if invalid_fields:
        results.append(
            _reject(
                artifact,
                "timestamp_policy_validator",
                "timestamp_field_missing_or_invalid",
                ",".join(invalid_fields),
                invalid_fields,
            )
        )
        return
    if source and source.updated_at_ns < source.created_at_ns:
        results.append(_reject(artifact, "timestamp_policy_validator", "manifest_temporal_inconsistent", fields=("updated_at_ns", "created_at_ns")))
        return
    policy_fields = (
        _prefixed(field_prefix, "publisher_timestamp_policy"),
        _prefixed(field_prefix, "source_timestamp_policy"),
    )
    ambiguous = tuple(field for field in policy_fields if str(_nested_get(artifact, field)).lower() in {"unknown", "ambiguous"})
    if ambiguous:
        results.append(_hold(artifact, "timestamp_policy_validator", "timestamp_policy_ambiguous", fields=ambiguous))
        return
    results.append(_accept(artifact, "timestamp_policy_validator"))


def _append_license_temporal_result(
    results: list[ValidatorResult], artifact: Mapping[str, Any], license_: FLWCLicenseManifestV1 | None
) -> None:
    invalid_fields = tuple(field for field in ("created_at_ns", "updated_at_ns") if not _is_positive_int(artifact.get(field)))
    if invalid_fields:
        results.append(
            _reject(artifact, "timestamp_policy_validator", "timestamp_field_missing_or_invalid", ",".join(invalid_fields), invalid_fields)
        )
        return
    if license_ and license_.updated_at_ns < license_.created_at_ns:
        results.append(_reject(artifact, "timestamp_policy_validator", "manifest_temporal_inconsistent", fields=("updated_at_ns", "created_at_ns")))
        return
    if license_ and license_.valid_from_ns and license_.valid_until_ns and license_.valid_until_ns < license_.valid_from_ns:
        results.append(
            _reject(artifact, "timestamp_policy_validator", "manifest_temporal_inconsistent", fields=("valid_from_ns", "valid_until_ns"))
        )
        return
    results.append(_accept(artifact, "timestamp_policy_validator"))


def _append_source_policy_string_result(
    results: list[ValidatorResult],
    artifact: Mapping[str, Any],
    source: FLWCSourceManifestV1 | None,
    *,
    field_prefix: str | None = None,
) -> None:
    if source is None:
        results.append(
            _reject(
                artifact,
                "source_policy_validator",
                "source_manifest_missing_or_invalid",
                fields=tuple(_prefixed(field_prefix, field) for field in B1_SOURCE_POLICY_SENTINELS),
            )
        )
        return
    rejected, review = _classify_policy_fields(source, B1_SOURCE_POLICY_SENTINELS, field_prefix)
    if rejected:
        results.append(
            _reject(
                artifact,
                "source_policy_validator",
                "source_policy_authority_escalation_rejected",
                ",".join(rejected),
                rejected,
            )
        )
        return
    if review:
        results.append(
            _hold(
                artifact,
                "source_policy_validator",
                "source_policy_value_unrecognized_requires_review",
                ",".join(review),
                review,
            )
        )
        return
    results.append(_accept(artifact, "source_policy_validator"))


def _append_license_policy_string_result(
    results: list[ValidatorResult],
    artifact: Mapping[str, Any],
    license_: FLWCLicenseManifestV1 | None,
    *,
    field_prefix: str | None = None,
) -> None:
    if license_ is None:
        results.append(
            _reject(
                artifact,
                "license_policy_validator",
                "license_manifest_missing_or_invalid",
                fields=tuple(_prefixed(field_prefix, field) for field in B1_LICENSE_POLICY_SENTINELS),
            )
        )
        return
    rejected, review = _classify_policy_fields(license_, B1_LICENSE_POLICY_SENTINELS, field_prefix)
    if rejected:
        results.append(
            _reject(
                artifact,
                "license_policy_validator",
                "license_policy_authority_escalation_rejected",
                ",".join(rejected),
                rejected,
            )
        )
        return
    if review:
        results.append(
            _hold(
                artifact,
                "license_policy_validator",
                "license_policy_value_unrecognized_requires_review",
                ",".join(review),
                review,
            )
        )
        return
    results.append(_accept(artifact, "license_policy_validator"))


def _append_raw_hash_reference_result(
    results: list[ValidatorResult],
    artifact: Mapping[str, Any],
    *,
    source_manifest: Mapping[str, Any] | None = None,
    field_prefix: str | None = None,
) -> None:
    manifest = source_manifest or artifact
    if manifest.get("raw_text_hash_required") is True and not _is_non_empty_string(manifest.get("raw_text_hash")):
        results.append(
            _reject(
                artifact,
                "raw_hash_reference_validator",
                "raw_text_hash_missing",
                fields=(_prefixed(field_prefix, "raw_text_hash"),),
            )
        )
        return
    results.append(_accept(artifact, "raw_hash_reference_validator"))


def _append_credential_leak_result(results: list[ValidatorResult], artifact: Mapping[str, Any]) -> None:
    if contains_secret_like_value(artifact):
        results.append(_reject(artifact, "credential_leak_validator", "secret_like_value_detected"))
        return
    results.append(_accept(artifact, "credential_leak_validator"))


def _append_prompt_injection_policy_result(
    results: list[ValidatorResult],
    artifact: Mapping[str, Any],
    source: FLWCSourceManifestV1 | None,
    *,
    field_prefix: str | None = None,
) -> None:
    if source is None:
        results.append(_reject(artifact, "prompt_injection_policy_validator", "source_manifest_missing_or_invalid", fields=("prompt_injection_policy",)))
        return
    if source.prompt_injection_policy == PromptInjectionPolicy.HUMAN_REVIEW_REQUIRED:
        results.append(
            _hold(
                artifact,
                "prompt_injection_policy_validator",
                "prompt_injection_policy_requires_review",
                fields=(_prefixed(field_prefix, "prompt_injection_policy"),),
            )
        )
        return
    if source.prompt_injection_policy == PromptInjectionPolicy.QUARANTINE_ON_SUSPECTED_INJECTION:
        results.append(
            _neutralize(
                artifact,
                "prompt_injection_policy_validator",
                "prompt_injection_quarantined",
                fields=(_prefixed(field_prefix, "prompt_injection_policy"),),
            )
        )
        return
    results.append(_accept(artifact, "prompt_injection_policy_validator"))


def _append_no_runtime_payload_raw_text_result(
    results: list[ValidatorResult],
    artifact: Mapping[str, Any],
    license_: FLWCLicenseManifestV1 | None,
    *,
    field_prefix: str | None = None,
) -> None:
    if license_ is None:
        results.append(_reject(artifact, "no_runtime_payload_raw_text_validator", "license_manifest_missing_or_invalid", fields=("runtime_payload_policy",)))
        return
    if license_.runtime_payload_policy == RuntimePayloadPolicy.FUTURE_REVIEW_REQUIRED:
        results.append(
            _hold(
                artifact,
                "no_runtime_payload_raw_text_validator",
                "runtime_payload_policy_requires_review",
                fields=(_prefixed(field_prefix, "runtime_payload_policy"),),
            )
        )
        return
    results.append(_accept(artifact, "no_runtime_payload_raw_text_validator"))


def _append_non_claims_result(results: list[ValidatorResult], artifact: Mapping[str, Any], artifact_type: str) -> None:
    non_claims = set(ensure_strings(artifact.get("non_claims", [])))
    required = set(MANDATORY_SYNTHETIC_NON_CLAIMS)
    if artifact_type == "source":
        required |= set(MANDATORY_SOURCE_NON_CLAIMS)
    missing = tuple(sorted(required - non_claims))
    if missing:
        results.append(_reject(artifact, "non_claims_validator", "missing_mandatory_non_claims", ",".join(missing), ("non_claims",)))
        return
    results.append(_accept(artifact, "non_claims_validator"))


def _append_pair_non_claims_result(
    results: list[ValidatorResult],
    artifact: Mapping[str, Any],
    source_manifest: Mapping[str, Any],
    license_manifest: Mapping[str, Any],
) -> None:
    source_claims = set(ensure_strings(source_manifest.get("non_claims", [])))
    license_claims = set(ensure_strings(license_manifest.get("non_claims", [])))
    source_missing = (set(MANDATORY_SOURCE_NON_CLAIMS) | set(MANDATORY_SYNTHETIC_NON_CLAIMS)) - source_claims
    license_missing = set(MANDATORY_SYNTHETIC_NON_CLAIMS) - license_claims
    fields: list[str] = []
    if source_missing:
        fields.append("source_manifest.non_claims")
    if license_missing:
        fields.append("license_manifest.non_claims")
    if fields:
        detail = ",".join(sorted(source_missing | license_missing))
        results.append(_reject(artifact, "non_claims_validator", "missing_mandatory_non_claims", detail, tuple(fields)))
        return
    results.append(_accept(artifact, "non_claims_validator"))


def _append_source_synthetic_fixture_scope_result(
    results: list[ValidatorResult], artifact: Mapping[str, Any], source: FLWCSourceManifestV1 | None
) -> None:
    if source is None:
        results.append(_reject(artifact, "synthetic_fixture_scope_validator", "source_manifest_missing_or_invalid", fields=("source_class",)))
        return
    if source.source_class != SourceClass.SYNTHETIC_FIXTURE:
        results.append(_reject(artifact, "synthetic_fixture_scope_validator", "synthetic_fixture_scope_invalid", fields=("source_class",)))
        return
    if source.source_access_mode.value != "offline_fixture":
        results.append(_reject(artifact, "synthetic_fixture_scope_validator", "synthetic_fixture_scope_invalid", fields=("source_access_mode",)))
        return
    if source.status != SourceStatus.ACCEPTED_METADATA_ONLY:
        results.append(
            _reject(
                artifact,
                "synthetic_fixture_scope_validator",
                "synthetic_fixture_status_not_accepted_metadata_only",
                fields=("status",),
            )
        )
        return
    results.append(_accept(artifact, "synthetic_fixture_scope_validator"))


def _append_pair_synthetic_fixture_scope_result(
    results: list[ValidatorResult],
    artifact: Mapping[str, Any],
    source: FLWCSourceManifestV1 | None,
    license_: FLWCLicenseManifestV1 | None,
) -> None:
    if source is None or license_ is None:
        results.append(_reject(artifact, "synthetic_fixture_scope_validator", "source_or_license_manifest_invalid", fields=("source_class",)))
        return
    fields: list[str] = []
    if source.source_class != SourceClass.SYNTHETIC_FIXTURE:
        fields.append("source_manifest.source_class")
    if source.source_access_mode.value != "offline_fixture":
        fields.append("source_manifest.source_access_mode")
    if license_.license_state != LicenseState.ALLOWED_FULL_TEXT:
        fields.append("license_manifest.license_state")
    if source.rights_scope != RightsScope.RESEARCH_INTERNAL_ONLY or license_.rights_scope != RightsScope.RESEARCH_INTERNAL_ONLY:
        fields.extend(["source_manifest.rights_scope", "license_manifest.rights_scope"])
    if source.raw_storage_policy != RawStoragePolicy.ALLOWED_FULL_TEXT or license_.raw_storage_policy != RawStoragePolicy.ALLOWED_FULL_TEXT:
        fields.extend(["source_manifest.raw_storage_policy", "license_manifest.raw_storage_policy"])
    if source.status != SourceStatus.ACCEPTED_METADATA_ONLY:
        fields.append("source_manifest.status")
    if fields:
        field_refs = tuple(dict.fromkeys(fields))
        reason_code = (
            "synthetic_fixture_status_not_accepted_metadata_only"
            if field_refs == ("source_manifest.status",)
            else "synthetic_fixture_scope_invalid"
        )
        results.append(_reject(artifact, "synthetic_fixture_scope_validator", reason_code, ",".join(field_refs), field_refs))
        return
    results.append(_accept(artifact, "synthetic_fixture_scope_validator"))


def _classify_policy_fields(
    manifest: object,
    allowed_values_by_field: Mapping[str, frozenset[str]],
    field_prefix: str | None,
) -> tuple[tuple[str, ...], tuple[str, ...]]:
    rejected: list[str] = []
    review: list[str] = []
    for field, allowed_values in allowed_values_by_field.items():
        value = getattr(manifest, field)
        if value in allowed_values:
            continue
        field_ref = _prefixed(field_prefix, field)
        if _policy_value_has_authority_escalation_shape(value):
            rejected.append(field_ref)
        else:
            review.append(field_ref)
    return tuple(rejected), tuple(review)


def _policy_value_has_authority_escalation_shape(value: str) -> bool:
    text = value.strip().lower()
    return any(marker in text for marker in AUTHORITY_ESCALATION_POLICY_MARKERS)


def _storage_policy_incompatible_with_license(storage_policy: RawStoragePolicy, license_state: LicenseState) -> bool:
    if storage_policy == RawStoragePolicy.ALLOWED_FULL_TEXT:
        return license_state != LicenseState.ALLOWED_FULL_TEXT
    if storage_policy == RawStoragePolicy.RAW_HASH_ONLY:
        return license_state in {LicenseState.FORBIDDEN, LicenseState.EXPIRED}
    if storage_policy == RawStoragePolicy.DERIVED_FIELDS_ONLY:
        return license_state not in {LicenseState.ALLOWED_FULL_TEXT, LicenseState.DERIVED_ONLY}
    if storage_policy == RawStoragePolicy.METADATA_ONLY:
        return license_state in {LicenseState.FORBIDDEN, LicenseState.EXPIRED}
    if storage_policy == RawStoragePolicy.NO_STORAGE:
        return license_state == LicenseState.FORBIDDEN
    return False


def _summary(artifact: Mapping[str, Any], results: list[ValidatorResult], artifact_type: str) -> dict[str, Any]:
    artifact_ref = _artifact_ref(artifact, artifact_type)
    summary = ValidatorSummary.from_results(
        validator_summary_id=f"{artifact_ref}:validator_summary",
        input_artifact_refs=(artifact_ref,),
        validator_results=tuple(results),
    )
    return summary.as_dict()


def _reject(
    artifact: Mapping[str, Any],
    validator_id: str,
    reason_code: str,
    detail: str = "",
    fields: tuple[str, ...] = (),
    *,
    artifact_schema_version: str | None = None,
) -> ValidatorResult:
    return _result(artifact, validator_id, ValidatorStatus.REJECT, reason_code, detail, fields, artifact_schema_version=artifact_schema_version)


def _hold(
    artifact: Mapping[str, Any],
    validator_id: str,
    reason_code: str,
    detail: str = "",
    fields: tuple[str, ...] = (),
) -> ValidatorResult:
    return _result(artifact, validator_id, ValidatorStatus.HOLD_REVIEW, reason_code, detail, fields)


def _neutralize(
    artifact: Mapping[str, Any],
    validator_id: str,
    reason_code: str,
    detail: str = "",
    fields: tuple[str, ...] = (),
) -> ValidatorResult:
    return _result(artifact, validator_id, ValidatorStatus.NEUTRALIZE, reason_code, detail, fields)


def _accept(
    artifact: Mapping[str, Any],
    validator_id: str,
    reason_code: str = "accepted",
    *,
    artifact_schema_version: str | None = None,
) -> ValidatorResult:
    return _result(artifact, validator_id, ValidatorStatus.ACCEPT, reason_code, artifact_schema_version=artifact_schema_version)


def _result(
    artifact: Mapping[str, Any],
    validator_id: str,
    status: ValidatorStatus,
    reason_code: str,
    detail: str = "",
    fields: tuple[str, ...] = (),
    *,
    artifact_schema_version: str | None = None,
) -> ValidatorResult:
    return ValidatorResult(
        validator_id=validator_id,
        result=status,
        reason_code=reason_code,
        reason_detail_bounded=detail,
        field_refs=fields,
        artifact_ref=_artifact_ref(artifact, "generic"),
        artifact_schema_version=artifact_schema_version or _artifact_schema_version(artifact),
        input_refs=_input_refs(artifact),
        non_claims_checked=_non_claims_checked(artifact),
        non_claims=B0_VALIDATOR_NON_CLAIMS,
    )


def _artifact_ref(artifact: Mapping[str, Any], artifact_type: str) -> str:
    if "source_manifest" in artifact or "license_manifest" in artifact:
        source = artifact.get("source_manifest")
        license_ = artifact.get("license_manifest")
        source_id = source.get("source_manifest_id") if isinstance(source, Mapping) else None
        license_id = license_.get("license_manifest_id") if isinstance(license_, Mapping) else None
        return f"{source_id or 'unknown_source_manifest'}:{license_id or 'unknown_license_manifest'}"
    for field in ("source_manifest_id", "license_manifest_id", "source_id"):
        value = artifact.get(field)
        if isinstance(value, str) and value.strip():
            return value
    return f"unknown_{artifact_type}"


def _artifact_schema_version(artifact: Mapping[str, Any]) -> str:
    value = artifact.get("schema_version")
    return value if isinstance(value, str) else ""


def _input_refs(artifact: Mapping[str, Any]) -> tuple[str, ...]:
    refs: list[str] = []
    for key in ("source_manifest_id", "license_manifest_id", "license_manifest_ref", "source_id"):
        value = artifact.get(key)
        if isinstance(value, str) and value.strip():
            refs.append(value)
    for key in ("source_manifest", "license_manifest"):
        value = artifact.get(key)
        if isinstance(value, Mapping):
            refs.extend(_input_refs(value))
    return tuple(refs)


def _non_claims_checked(artifact: Mapping[str, Any]) -> tuple[str, ...]:
    claims = list(ensure_strings(artifact.get("non_claims", [])))
    for key in ("source_manifest", "license_manifest"):
        value = artifact.get(key)
        if isinstance(value, Mapping):
            claims.extend(ensure_strings(value.get("non_claims", [])))
    return tuple(sorted(set(claims)))


def _first_schema_reason(issues: tuple[SchemaIssue, ...]) -> str:
    reason_codes = {issue.reason_code for issue in issues}
    for reason_code in SCHEMA_REASON_PRIORITY:
        if reason_code in reason_codes:
            return reason_code
    return issues[0].reason_code


def _issue_fields(issues: tuple[SchemaIssue, ...]) -> tuple[str, ...]:
    fields: list[str] = []
    for issue in issues:
        fields.extend(issue.field_refs)
    return tuple(dict.fromkeys(fields))


def _issue_detail(issues: tuple[SchemaIssue, ...]) -> str:
    return "; ".join(f"{','.join(issue.field_refs)}:{issue.detail}" for issue in issues)


def _nested_get(artifact: Mapping[str, Any], field_ref: str) -> object:
    current: object = artifact
    for part in field_ref.split("."):
        if not isinstance(current, Mapping):
            return None
        current = current.get(part)
    return current


def _prefixed(prefix: str | None, field_name: str) -> str:
    return f"{prefix}.{field_name}" if prefix else field_name


def _is_non_empty_string(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _is_positive_int(value: object) -> bool:
    return type(value) is int and value > 0
