from __future__ import annotations

import json
import re
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
from flwc.schemas.raw_evidence import (
    FLWCRawEvidenceRecordV1,
    FLWCRawEvidenceVaultManifestV1,
    FLWCSourceDocumentIndexV1,
    MANDATORY_RAW_EVIDENCE_NON_CLAIMS,
    QuarantineStatus,
    RawTextRefPolicy,
    VaultScope,
)
from flwc.schemas.source_license import (
    FLWCLicenseManifestV1,
    FLWCSourceManifestV1,
    LicenseState,
    PromptInjectionPolicy,
    RawStoragePolicy,
    RightsScope,
    SourceClass,
    SourceTrustTier,
)
from flwc.validators.core import contains_secret_like_value
from flwc.validators.source_license import validate_source_license_pair


SCHEMA_REASON_PRIORITY = (
    "artifact_not_mapping",
    "schema_version_invalid",
    "required_field_missing",
    "field_type_invalid",
    "enum_value_invalid",
    "required_list_empty",
    "required_map_empty",
)
RAW_TEXT_REFERENCE_POLICIES_REQUIRING_HASH = frozenset(
    {
        RawTextRefPolicy.RAW_HASH_ONLY,
        RawTextRefPolicy.RAW_TEXT_ALLOWED_INTERNAL,
        RawTextRefPolicy.QUARANTINE_ONLY,
        RawTextRefPolicy.SYNTHETIC_FIXTURE_TEXT_ALLOWED,
    }
)
RAW_TEXT_STORAGE_POLICIES = frozenset({RawStoragePolicy.ALLOWED_FULL_TEXT, RawStoragePolicy.RAW_HASH_ONLY})
REVIEW_RETENTION_VALUES = frozenset({"unknown", "ambiguous", "human_review_required", "review_required"})
INLINE_RAW_TEXT_PAYLOAD_KEYS = frozenset(
    {
        "article_text",
        "document_text",
        "full_rag_context",
        "full_text",
        "llm_output",
        "model_raw_output",
        "rag_context",
        "raw_llm_output",
        "raw_payload",
        "raw_text",
        "source_text",
    }
)
FORBIDDEN_BOUNDARY_KEYS = frozenset(
    {
        "atomic_claim_ref",
        "atomic_claim_refs",
        "claim_id",
        "claim_ledger_id",
        "claim_ledger_refs",
        "claim_text",
        "duckdb_seed",
        "event_id",
        "event_table_id",
        "event_time_ns",
        "execution_instruction",
        "external_consumer_adapter",
        "financial_event_ref",
        "financial_event_refs",
        "future_outcome",
        "market_data_authority",
        "model_output",
        "order_intent",
        "position_sizing",
        "position_target",
        "runtime_payload",
        "runtime_service",
        "scanner_signal",
        "source_adapter",
        "source_ingestion",
        "trade_signal",
        "vendor_adapter",
        "wiki_export",
    }
)
SEGMENT_REF_RE = re.compile(r"^(?P<doc>.+)#segment:(?P<segment>\d{6,})$")
SPAN_REF_RE = re.compile(r"^(?P<doc>.+)#span:(?P<start>\d{6,})-(?P<end>\d{6,})$")


def validate_raw_evidence_vault_manifest(vault_manifest: Mapping[str, Any]) -> dict[str, Any]:
    vault, vault_issues = FLWCRawEvidenceVaultManifestV1.from_mapping(vault_manifest)
    results: list[ValidatorResult] = []

    _append_schema_result(results, vault_manifest, vault_issues, "raw_evidence_schema_validator")
    _append_vault_ref_result(results, vault_manifest)
    _append_vault_raw_storage_summary_result(results, vault_manifest, vault)
    _append_vault_retention_policy_result(results, vault_manifest, vault)
    _append_vault_timestamp_result(results, vault_manifest, vault)
    _append_lineage_digest_result(results, vault_manifest, "lineage_digest")
    _append_raw_text_payload_denial_result(results, vault_manifest)
    _append_credential_leak_result(results, vault_manifest)
    _append_non_claims_result(results, vault_manifest)
    _append_vault_synthetic_fixture_scope_result(results, vault_manifest, vault)
    _append_forbidden_boundary_result(results, vault_manifest)

    return _summary(vault_manifest, results, "raw_evidence_vault_manifest")


def validate_raw_evidence_record(raw_evidence_record: Mapping[str, Any]) -> dict[str, Any]:
    record, record_issues = FLWCRawEvidenceRecordV1.from_mapping(raw_evidence_record)
    results: list[ValidatorResult] = []

    _append_schema_result(results, raw_evidence_record, record_issues, "raw_evidence_schema_validator")
    _append_record_ref_result(results, raw_evidence_record)
    _append_record_rights_scope_result(results, raw_evidence_record, record)
    _append_record_raw_storage_policy_result(results, raw_evidence_record, record)
    _append_record_retention_policy_result(results, raw_evidence_record, record)
    _append_record_timestamp_result(results, raw_evidence_record, record)
    _append_record_raw_hash_reference_result(results, raw_evidence_record, record)
    _append_record_source_span_ref_result(results, raw_evidence_record, record)
    _append_lineage_digest_result(results, raw_evidence_record, "lineage_digest")
    _append_record_prompt_injection_result(results, raw_evidence_record, record)
    _append_raw_text_payload_denial_result(results, raw_evidence_record)
    _append_credential_leak_result(results, raw_evidence_record)
    _append_non_claims_result(results, raw_evidence_record)
    _append_record_synthetic_fixture_scope_result(results, raw_evidence_record, record)
    _append_forbidden_boundary_result(results, raw_evidence_record)

    return _summary(raw_evidence_record, results, "raw_evidence_record")


def validate_source_document_index(source_document_index: Mapping[str, Any]) -> dict[str, Any]:
    index, index_issues = FLWCSourceDocumentIndexV1.from_mapping(source_document_index)
    results: list[ValidatorResult] = []

    _append_schema_result(results, source_document_index, index_issues, "source_document_index_schema_validator")
    _append_index_ref_result(results, source_document_index)
    _append_index_rights_scope_result(results, source_document_index, index)
    _append_index_raw_storage_policy_result(results, source_document_index, index)
    _append_index_retention_policy_result(results, source_document_index, index)
    _append_index_timestamp_result(results, source_document_index, index)
    _append_index_hash_reference_result(results, source_document_index, index)
    _append_lineage_digest_result(results, source_document_index, "segment_index_digest")
    _append_index_prompt_injection_result(results, source_document_index, index)
    _append_raw_text_payload_denial_result(results, source_document_index)
    _append_credential_leak_result(results, source_document_index)
    _append_non_claims_result(results, source_document_index)
    _append_index_synthetic_fixture_scope_result(results, source_document_index, index)
    _append_forbidden_boundary_result(results, source_document_index)

    return _summary(source_document_index, results, "source_document_index")


def validate_raw_evidence_index_pair(
    raw_evidence_vault_manifest: Mapping[str, Any],
    raw_evidence_record: Mapping[str, Any],
    source_document_index: Mapping[str, Any],
    source_manifest: Mapping[str, Any],
    license_manifest: Mapping[str, Any],
) -> dict[str, Any]:
    vault, vault_issues = FLWCRawEvidenceVaultManifestV1.from_mapping(raw_evidence_vault_manifest)
    record, record_issues = FLWCRawEvidenceRecordV1.from_mapping(raw_evidence_record)
    index, index_issues = FLWCSourceDocumentIndexV1.from_mapping(source_document_index)
    source, source_issues = FLWCSourceManifestV1.from_mapping(source_manifest)
    license_, license_issues = FLWCLicenseManifestV1.from_mapping(license_manifest)
    artifact = {
        "raw_evidence_vault_manifest": raw_evidence_vault_manifest,
        "raw_evidence_record": raw_evidence_record,
        "source_document_index": source_document_index,
        "source_manifest": source_manifest,
        "license_manifest": license_manifest,
    }
    results: list[ValidatorResult] = []

    _append_schema_result(
        results,
        artifact,
        vault_issues,
        "raw_evidence_schema_validator",
        artifact_schema_version="FLWCRawEvidenceVaultManifestV1",
    )
    _append_schema_result(
        results,
        artifact,
        record_issues,
        "raw_evidence_record_schema_validator",
        artifact_schema_version="FLWCRawEvidenceRecordV1",
    )
    _append_schema_result(
        results,
        artifact,
        index_issues,
        "source_document_index_schema_validator",
        artifact_schema_version="FLWCSourceDocumentIndexV1",
    )
    _append_schema_result(
        results,
        artifact,
        source_issues,
        "source_manifest_schema_validator",
        artifact_schema_version="FLWCSourceManifestV1",
    )
    _append_schema_result(
        results,
        artifact,
        license_issues,
        "license_manifest_schema_validator",
        artifact_schema_version="FLWCLicenseManifestV1",
    )
    _append_pair_source_license_validation_result(results, artifact, source_manifest, license_manifest)
    _append_pair_ref_consistency_result(results, artifact, vault, record, index, source, license_)
    _append_pair_rights_scope_result(results, artifact, record, index, source, license_)
    _append_pair_raw_storage_policy_result(results, artifact, vault, record, index, source, license_)
    _append_pair_retention_policy_result(results, artifact, vault, source, license_)
    _append_pair_timestamp_result(results, artifact, vault, record, index)
    _append_pair_raw_hash_reference_result(results, artifact, record, index)
    _append_pair_source_span_ref_result(results, artifact, record, index)
    _append_pair_lineage_digest_result(results, artifact, vault, record, index)
    _append_pair_prompt_injection_result(results, artifact, vault, record, source)
    _append_raw_text_payload_denial_result(results, artifact)
    _append_credential_leak_result(results, artifact)
    _append_pair_non_claims_result(results, artifact)
    _append_pair_synthetic_fixture_scope_result(results, artifact, vault, record, index)
    _append_forbidden_boundary_result(results, artifact)

    return _summary(artifact, results, "raw_evidence_index_pair")


def validate_raw_evidence_vault_manifest_file(path: str | Path) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as fh:
        return validate_raw_evidence_vault_manifest(json.load(fh))


def validate_raw_evidence_record_file(path: str | Path) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as fh:
        return validate_raw_evidence_record(json.load(fh))


def validate_source_document_index_file(path: str | Path) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as fh:
        return validate_source_document_index(json.load(fh))


def validate_raw_evidence_index_pair_file(path: str | Path) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as fh:
        fixture = json.load(fh)
    return validate_raw_evidence_index_pair(
        fixture["raw_evidence_vault_manifest"],
        fixture["raw_evidence_record"],
        fixture["source_document_index"],
        fixture["source_manifest"],
        fixture["license_manifest"],
    )


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


def _append_vault_ref_result(results: list[ValidatorResult], artifact: Mapping[str, Any]) -> None:
    invalid = _empty_list_fields(artifact, ("source_manifest_refs", "license_manifest_refs"))
    if invalid:
        results.append(_reject(artifact, "source_manifest_ref_validator", "input_refs_missing", fields=invalid))
        return
    results.append(_accept(artifact, "source_manifest_ref_validator"))
    results.append(_accept(artifact, "license_manifest_ref_validator"))


def _append_record_ref_result(results: list[ValidatorResult], artifact: Mapping[str, Any]) -> None:
    missing_source = not _is_non_empty_string(artifact.get("source_manifest_ref"))
    missing_license = not _is_non_empty_string(artifact.get("license_manifest_ref"))
    if missing_source:
        results.append(
            _reject(artifact, "source_manifest_ref_validator", "source_manifest_ref_missing", fields=("source_manifest_ref",))
        )
    else:
        results.append(_accept(artifact, "source_manifest_ref_validator"))
    if missing_license:
        results.append(
            _reject(artifact, "license_manifest_ref_validator", "license_manifest_ref_missing", fields=("license_manifest_ref",))
        )
    else:
        results.append(_accept(artifact, "license_manifest_ref_validator"))


def _append_index_ref_result(results: list[ValidatorResult], artifact: Mapping[str, Any]) -> None:
    missing_source = not _is_non_empty_string(artifact.get("source_manifest_ref"))
    missing_license = not _is_non_empty_string(artifact.get("license_manifest_ref"))
    if missing_source:
        results.append(
            _reject(artifact, "source_manifest_ref_validator", "source_manifest_ref_missing", fields=("source_manifest_ref",))
        )
    else:
        results.append(_accept(artifact, "source_manifest_ref_validator"))
    if missing_license:
        results.append(
            _reject(artifact, "license_manifest_ref_validator", "license_manifest_ref_missing", fields=("license_manifest_ref",))
        )
    else:
        results.append(_accept(artifact, "license_manifest_ref_validator"))


def _append_vault_raw_storage_summary_result(
    results: list[ValidatorResult], artifact: Mapping[str, Any], vault: FLWCRawEvidenceVaultManifestV1 | None
) -> None:
    if vault is None:
        results.append(_reject(artifact, "raw_storage_policy_validator", "raw_evidence_vault_manifest_invalid", fields=("raw_storage_policy_summary",)))
        return
    invalid_fields = tuple(
        f"raw_storage_policy_summary.{key}"
        for key, value in vault.raw_storage_policy_summary
        if value not in {policy.value for policy in RawStoragePolicy}
    )
    if invalid_fields:
        results.append(_reject(artifact, "raw_storage_policy_validator", "raw_storage_policy_summary_invalid", fields=invalid_fields))
        return
    results.append(_accept(artifact, "raw_storage_policy_validator"))


def _append_record_rights_scope_result(
    results: list[ValidatorResult], artifact: Mapping[str, Any], record: FLWCRawEvidenceRecordV1 | None
) -> None:
    if record is None:
        results.append(_reject(artifact, "rights_scope_validator", "raw_evidence_record_invalid", fields=("rights_scope",)))
        return
    if record.rights_scope == RightsScope.UNKNOWN:
        results.append(_hold(artifact, "rights_scope_validator", "rights_scope_unknown_requires_review", fields=("rights_scope",)))
        return
    if record.raw_storage_policy == RawStoragePolicy.ALLOWED_FULL_TEXT and record.rights_scope == RightsScope.DERIVED_ARTIFACTS_INTERNAL_ONLY:
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


def _append_index_rights_scope_result(
    results: list[ValidatorResult], artifact: Mapping[str, Any], index: FLWCSourceDocumentIndexV1 | None
) -> None:
    if index is None:
        results.append(_reject(artifact, "rights_scope_validator", "source_document_index_invalid", fields=("rights_scope",)))
        return
    if index.rights_scope == RightsScope.UNKNOWN:
        results.append(_hold(artifact, "rights_scope_validator", "rights_scope_unknown_requires_review", fields=("rights_scope",)))
        return
    if index.raw_storage_policy == RawStoragePolicy.ALLOWED_FULL_TEXT and index.rights_scope == RightsScope.DERIVED_ARTIFACTS_INTERNAL_ONLY:
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


def _append_record_raw_storage_policy_result(
    results: list[ValidatorResult], artifact: Mapping[str, Any], record: FLWCRawEvidenceRecordV1 | None
) -> None:
    if record is None:
        results.append(_reject(artifact, "raw_storage_policy_validator", "raw_evidence_record_invalid", fields=("raw_storage_policy",)))
        return
    if _storage_policy_incompatible_with_license(record.raw_storage_policy, record.license_state):
        results.append(
            _reject(
                artifact,
                "raw_storage_policy_validator",
                "raw_storage_policy_incompatible_with_license_state",
                fields=("raw_storage_policy", "license_state"),
            )
        )
        return
    if record.raw_storage_policy in {RawStoragePolicy.HUMAN_REVIEW_REQUIRED, RawStoragePolicy.QUARANTINE_ONLY}:
        results.append(_hold(artifact, "raw_storage_policy_validator", "raw_storage_policy_requires_review", fields=("raw_storage_policy",)))
        return
    results.append(_accept(artifact, "raw_storage_policy_validator"))


def _append_index_raw_storage_policy_result(
    results: list[ValidatorResult], artifact: Mapping[str, Any], index: FLWCSourceDocumentIndexV1 | None
) -> None:
    if index is None:
        results.append(_reject(artifact, "raw_storage_policy_validator", "source_document_index_invalid", fields=("raw_storage_policy",)))
        return
    if _storage_policy_incompatible_with_license(index.raw_storage_policy, index.license_state):
        results.append(
            _reject(
                artifact,
                "raw_storage_policy_validator",
                "raw_storage_policy_incompatible_with_license_state",
                fields=("raw_storage_policy", "license_state"),
            )
        )
        return
    if index.raw_storage_policy in {RawStoragePolicy.HUMAN_REVIEW_REQUIRED, RawStoragePolicy.QUARANTINE_ONLY}:
        results.append(_hold(artifact, "raw_storage_policy_validator", "raw_storage_policy_requires_review", fields=("raw_storage_policy",)))
        return
    results.append(_accept(artifact, "raw_storage_policy_validator"))


def _append_vault_retention_policy_result(
    results: list[ValidatorResult], artifact: Mapping[str, Any], vault: FLWCRawEvidenceVaultManifestV1 | None
) -> None:
    if vault is None:
        results.append(_reject(artifact, "retention_policy_validator", "raw_evidence_vault_manifest_invalid", fields=("retention_policy_summary",)))
        return
    if not vault.retention_policy_summary:
        results.append(_reject(artifact, "retention_policy_validator", "retention_policy_missing", fields=("retention_policy_summary",)))
        return
    review = tuple(
        f"retention_policy_summary.{key}"
        for key, value in vault.retention_policy_summary
        if value.strip().lower() in REVIEW_RETENTION_VALUES
    )
    if review:
        results.append(_hold(artifact, "retention_policy_validator", "retention_policy_requires_review", fields=review))
        return
    results.append(_accept(artifact, "retention_policy_validator"))


def _append_record_retention_policy_result(
    results: list[ValidatorResult], artifact: Mapping[str, Any], record: FLWCRawEvidenceRecordV1 | None
) -> None:
    if record is None:
        results.append(_reject(artifact, "retention_policy_validator", "raw_evidence_record_invalid", fields=("retention_policy",)))
        return
    if not _is_non_empty_string(record.retention_policy):
        results.append(_reject(artifact, "retention_policy_validator", "retention_policy_missing", fields=("retention_policy",)))
        return
    if record.retention_policy.strip().lower() in REVIEW_RETENTION_VALUES:
        results.append(_hold(artifact, "retention_policy_validator", "retention_policy_requires_review", fields=("retention_policy",)))
        return
    results.append(_accept(artifact, "retention_policy_validator"))


def _append_index_retention_policy_result(
    results: list[ValidatorResult], artifact: Mapping[str, Any], index: FLWCSourceDocumentIndexV1 | None
) -> None:
    if index is None:
        results.append(_reject(artifact, "retention_policy_validator", "source_document_index_invalid", fields=("retention_policy",)))
        return
    if not _is_non_empty_string(index.retention_policy):
        results.append(_reject(artifact, "retention_policy_validator", "retention_policy_missing", fields=("retention_policy",)))
        return
    if index.retention_policy.strip().lower() in REVIEW_RETENTION_VALUES:
        results.append(_hold(artifact, "retention_policy_validator", "retention_policy_requires_review", fields=("retention_policy",)))
        return
    results.append(_accept(artifact, "retention_policy_validator"))


def _append_vault_timestamp_result(
    results: list[ValidatorResult], artifact: Mapping[str, Any], vault: FLWCRawEvidenceVaultManifestV1 | None
) -> None:
    invalid = tuple(field for field in ("source_cutoff_ns", "created_at_ns") if not _is_positive_int(artifact.get(field)))
    if invalid:
        results.append(_reject(artifact, "timestamp_validator", "timestamp_field_missing_or_invalid", ",".join(invalid), invalid))
        return
    if vault and vault.created_at_ns < vault.source_cutoff_ns:
        results.append(_reject(artifact, "timestamp_validator", "manifest_temporal_inconsistent", fields=("created_at_ns", "source_cutoff_ns")))
        return
    results.append(_accept(artifact, "timestamp_validator"))


def _append_record_timestamp_result(
    results: list[ValidatorResult], artifact: Mapping[str, Any], record: FLWCRawEvidenceRecordV1 | None
) -> None:
    invalid = tuple(
        field
        for field in ("ingest_timestamp_ns", "available_from_ns", "compiler_seen_at_ns")
        if not _is_positive_int(artifact.get(field))
    )
    if invalid:
        results.append(_reject(artifact, "timestamp_validator", "timestamp_field_missing_or_invalid", ",".join(invalid), invalid))
        return
    if record is None:
        results.append(_reject(artifact, "timestamp_validator", "raw_evidence_record_invalid", fields=("source_timestamp_ns",)))
        return
    if record.source_timestamp_ns is None:
        results.append(_reject(artifact, "timestamp_validator", "source_timestamp_missing", fields=("source_timestamp_ns",)))
        return
    if record.compiler_seen_at_ns < record.available_from_ns:
        results.append(_reject(artifact, "available_from_asof_validator", "available_from_after_compiler_seen", fields=("available_from_ns", "compiler_seen_at_ns")))
        return
    results.append(_accept(artifact, "timestamp_validator"))
    results.append(_accept(artifact, "available_from_asof_validator"))


def _append_index_timestamp_result(
    results: list[ValidatorResult], artifact: Mapping[str, Any], index: FLWCSourceDocumentIndexV1 | None
) -> None:
    invalid = tuple(field for field in ("available_from_ns",) if not _is_positive_int(artifact.get(field)))
    if invalid:
        results.append(_reject(artifact, "timestamp_validator", "timestamp_field_missing_or_invalid", ",".join(invalid), invalid))
        return
    if index is None:
        results.append(_reject(artifact, "timestamp_validator", "source_document_index_invalid", fields=("source_timestamp_ns",)))
        return
    if index.source_timestamp_ns is None:
        results.append(_reject(artifact, "timestamp_validator", "source_timestamp_missing", fields=("source_timestamp_ns",)))
        return
    results.append(_accept(artifact, "timestamp_validator"))
    results.append(_accept(artifact, "available_from_asof_validator"))


def _append_record_raw_hash_reference_result(
    results: list[ValidatorResult], artifact: Mapping[str, Any], record: FLWCRawEvidenceRecordV1 | None
) -> None:
    if record is None:
        results.append(_reject(artifact, "raw_hash_reference_validator", "raw_evidence_record_invalid", fields=("raw_text_hash",)))
        return
    if record.raw_text_ref_policy in RAW_TEXT_REFERENCE_POLICIES_REQUIRING_HASH and not _is_non_empty_string(record.raw_text_hash):
        results.append(_reject(artifact, "raw_hash_reference_validator", "raw_text_hash_missing", fields=("raw_text_hash",)))
        return
    results.append(_accept(artifact, "raw_hash_reference_validator"))


def _append_index_hash_reference_result(
    results: list[ValidatorResult], artifact: Mapping[str, Any], index: FLWCSourceDocumentIndexV1 | None
) -> None:
    if index is None:
        results.append(_reject(artifact, "raw_hash_reference_validator", "source_document_index_invalid", fields=("document_hash",)))
        return
    if index.raw_storage_policy in RAW_TEXT_STORAGE_POLICIES and not _is_non_empty_string(index.document_hash):
        results.append(_reject(artifact, "raw_hash_reference_validator", "document_hash_missing", fields=("document_hash",)))
        return
    results.append(_accept(artifact, "raw_hash_reference_validator"))


def _append_record_source_span_ref_result(
    results: list[ValidatorResult], artifact: Mapping[str, Any], record: FLWCRawEvidenceRecordV1 | None
) -> None:
    if record is None:
        results.append(_reject(artifact, "source_span_ref_validator", "raw_evidence_record_invalid", fields=("source_span_refs",)))
        return
    invalid = tuple(ref for ref in record.source_span_refs if _parse_span_ref(ref, record.source_document_id) is None)
    if invalid:
        results.append(_reject(artifact, "source_span_ref_validator", "source_span_ref_invalid", ",".join(invalid), ("source_span_refs",)))
        return
    results.append(_accept(artifact, "source_span_ref_validator"))


def _append_lineage_digest_result(results: list[ValidatorResult], artifact: Mapping[str, Any], field_name: str) -> None:
    if not _is_non_empty_string(artifact.get(field_name)):
        results.append(_reject(artifact, "lineage_digest_validator", "lineage_digest_missing", fields=(field_name,)))
        return
    results.append(_accept(artifact, "lineage_digest_validator"))


def _append_record_prompt_injection_result(
    results: list[ValidatorResult], artifact: Mapping[str, Any], record: FLWCRawEvidenceRecordV1 | None
) -> None:
    if record is None:
        results.append(_reject(artifact, "prompt_injection_flag_validator", "raw_evidence_record_invalid", fields=("prompt_injection_flags",)))
        return
    if record.prompt_injection_flags and record.quarantine_status != QuarantineStatus.QUARANTINED_FOR_PROMPT_INJECTION:
        results.append(
            _reject(
                artifact,
                "prompt_injection_flag_validator",
                "prompt_injection_quarantine_missing",
                fields=("prompt_injection_flags", "quarantine_status"),
            )
        )
        return
    if record.prompt_injection_flags:
        results.append(
            _hold(
                artifact,
                "prompt_injection_flag_validator",
                "prompt_injection_quarantined",
                fields=("prompt_injection_flags", "quarantine_status"),
            )
        )
        return
    results.append(_accept(artifact, "prompt_injection_flag_validator"))


def _append_index_prompt_injection_result(
    results: list[ValidatorResult], artifact: Mapping[str, Any], index: FLWCSourceDocumentIndexV1 | None
) -> None:
    if index is None:
        results.append(_reject(artifact, "prompt_injection_flag_validator", "source_document_index_invalid", fields=("prompt_injection_flags",)))
        return
    if index.prompt_injection_flags:
        results.append(
            _reject(
                artifact,
                "prompt_injection_flag_validator",
                "prompt_injection_quarantine_missing",
                fields=("prompt_injection_flags",),
            )
        )
        return
    results.append(_accept(artifact, "prompt_injection_flag_validator"))


def _append_raw_text_payload_denial_result(results: list[ValidatorResult], artifact: Mapping[str, Any]) -> None:
    fields = tuple(_find_inline_raw_text_payload_keys(artifact))
    if fields:
        results.append(
            _reject(
                artifact,
                "raw_text_payload_denial_validator",
                "raw_text_payload_field_present",
                ",".join(fields),
                fields,
            )
        )
        return
    results.append(_accept(artifact, "raw_text_payload_denial_validator"))


def _append_credential_leak_result(results: list[ValidatorResult], artifact: Mapping[str, Any]) -> None:
    if contains_secret_like_value(artifact):
        results.append(_reject(artifact, "credential_leak_validator", "secret_like_value_detected"))
        return
    results.append(_accept(artifact, "credential_leak_validator"))


def _append_non_claims_result(results: list[ValidatorResult], artifact: Mapping[str, Any]) -> None:
    claims = set(ensure_strings(artifact.get("non_claims", [])))
    missing = tuple(sorted(set(MANDATORY_RAW_EVIDENCE_NON_CLAIMS) - claims))
    if missing:
        results.append(_reject(artifact, "non_claims_validator", "missing_mandatory_non_claims", ",".join(missing), ("non_claims",)))
        return
    results.append(_accept(artifact, "non_claims_validator"))


def _append_vault_synthetic_fixture_scope_result(
    results: list[ValidatorResult], artifact: Mapping[str, Any], vault: FLWCRawEvidenceVaultManifestV1 | None
) -> None:
    if vault is None:
        results.append(_reject(artifact, "synthetic_fixture_scope_validator", "raw_evidence_vault_manifest_invalid", fields=("vault_scope",)))
        return
    fields: list[str] = []
    if vault.vault_scope != VaultScope.SYNTHETIC_FIXTURE_ONLY:
        fields.append("vault_scope")
    if vault.validation_status != ValidatorStatus.ACCEPT:
        fields.append("validation_status")
    if fields:
        results.append(_reject(artifact, "synthetic_fixture_scope_validator", "synthetic_fixture_scope_invalid", ",".join(fields), tuple(fields)))
        return
    results.append(_accept(artifact, "synthetic_fixture_scope_validator"))


def _append_record_synthetic_fixture_scope_result(
    results: list[ValidatorResult], artifact: Mapping[str, Any], record: FLWCRawEvidenceRecordV1 | None
) -> None:
    if record is None:
        results.append(_reject(artifact, "synthetic_fixture_scope_validator", "raw_evidence_record_invalid", fields=("source_class",)))
        return
    fields: list[str] = []
    if record.source_class != SourceClass.SYNTHETIC_FIXTURE:
        fields.append("source_class")
    if record.license_state != LicenseState.ALLOWED_FULL_TEXT:
        fields.append("license_state")
    if record.rights_scope != RightsScope.RESEARCH_INTERNAL_ONLY:
        fields.append("rights_scope")
    if record.raw_storage_policy != RawStoragePolicy.ALLOWED_FULL_TEXT:
        fields.append("raw_storage_policy")
    if record.raw_text_ref_policy != RawTextRefPolicy.SYNTHETIC_FIXTURE_TEXT_ALLOWED:
        fields.append("raw_text_ref_policy")
    if record.validation_status != ValidatorStatus.ACCEPT:
        fields.append("validation_status")
    if _looks_like_live_url(record.source_url_or_doc_id):
        fields.append("source_url_or_doc_id")
    if fields:
        field_refs = tuple(dict.fromkeys(fields))
        results.append(
            _reject(artifact, "synthetic_fixture_scope_validator", "synthetic_fixture_scope_invalid", ",".join(field_refs), field_refs)
        )
        return
    results.append(_accept(artifact, "synthetic_fixture_scope_validator"))


def _append_index_synthetic_fixture_scope_result(
    results: list[ValidatorResult], artifact: Mapping[str, Any], index: FLWCSourceDocumentIndexV1 | None
) -> None:
    if index is None:
        results.append(_reject(artifact, "synthetic_fixture_scope_validator", "source_document_index_invalid", fields=("validation_status",)))
        return
    fields: list[str] = []
    if index.source_trust_tier != SourceTrustTier.TIER_4_MANUAL_REVIEW_ONLY:
        fields.append("source_trust_tier")
    if index.license_state != LicenseState.ALLOWED_FULL_TEXT:
        fields.append("license_state")
    if index.rights_scope != RightsScope.RESEARCH_INTERNAL_ONLY:
        fields.append("rights_scope")
    if index.raw_storage_policy != RawStoragePolicy.ALLOWED_FULL_TEXT:
        fields.append("raw_storage_policy")
    if index.validation_status != ValidatorStatus.ACCEPT:
        fields.append("validation_status")
    if fields:
        field_refs = tuple(dict.fromkeys(fields))
        results.append(
            _reject(artifact, "synthetic_fixture_scope_validator", "synthetic_fixture_scope_invalid", ",".join(field_refs), field_refs)
        )
        return
    results.append(_accept(artifact, "synthetic_fixture_scope_validator"))


def _append_forbidden_boundary_result(results: list[ValidatorResult], artifact: Mapping[str, Any]) -> None:
    fields = tuple(_find_forbidden_boundary_keys(artifact))
    if fields:
        results.append(_reject(artifact, "no_trade_field_validator", "forbidden_boundary_field_present", ",".join(fields), fields))
        return
    results.append(_accept(artifact, "no_trade_field_validator"))


def _append_pair_source_license_validation_result(
    results: list[ValidatorResult],
    artifact: Mapping[str, Any],
    source_manifest: Mapping[str, Any],
    license_manifest: Mapping[str, Any],
) -> None:
    source_license_summary = validate_source_license_pair(source_manifest, license_manifest)
    aggregate = source_license_summary["aggregate_result"]
    if aggregate == ValidatorStatus.ACCEPT.value:
        results.append(_accept(artifact, "source_license_pairing_validator"))
        return
    if aggregate == ValidatorStatus.REJECT.value:
        results.append(_reject(artifact, "source_license_pairing_validator", "source_license_pair_not_accepted", str(aggregate)))
        return
    if aggregate == ValidatorStatus.HOLD_REVIEW.value:
        results.append(_hold(artifact, "source_license_pairing_validator", "source_license_pair_requires_review", str(aggregate)))
        return
    results.append(_neutralize(artifact, "source_license_pairing_validator", "source_license_pair_neutralized", str(aggregate)))


def _append_pair_ref_consistency_result(
    results: list[ValidatorResult],
    artifact: Mapping[str, Any],
    vault: FLWCRawEvidenceVaultManifestV1 | None,
    record: FLWCRawEvidenceRecordV1 | None,
    index: FLWCSourceDocumentIndexV1 | None,
    source: FLWCSourceManifestV1 | None,
    license_: FLWCLicenseManifestV1 | None,
) -> None:
    if None in (vault, record, index, source, license_):
        results.append(_reject(artifact, "source_manifest_ref_validator", "raw_evidence_pair_artifact_invalid"))
        return
    fields: list[str] = []
    assert vault is not None and record is not None and index is not None and source is not None and license_ is not None
    if record.source_manifest_ref != source.source_manifest_id:
        fields.append("raw_evidence_record.source_manifest_ref")
    if index.source_manifest_ref != source.source_manifest_id:
        fields.append("source_document_index.source_manifest_ref")
    if source.source_manifest_id not in vault.source_manifest_refs:
        fields.append("raw_evidence_vault_manifest.source_manifest_refs")
    if record.license_manifest_ref != license_.license_manifest_id:
        fields.append("raw_evidence_record.license_manifest_ref")
    if index.license_manifest_ref != license_.license_manifest_id:
        fields.append("source_document_index.license_manifest_ref")
    if license_.license_manifest_id not in vault.license_manifest_refs:
        fields.append("raw_evidence_vault_manifest.license_manifest_refs")
    if record.source_id != source.source_id or license_.source_id != source.source_id:
        fields.extend(("raw_evidence_record.source_id", "source_manifest.source_id", "license_manifest.source_id"))
    if record.source_trust_tier != source.source_trust_tier:
        fields.extend(("raw_evidence_record.source_trust_tier", "source_manifest.source_trust_tier"))
    if index.source_trust_tier != source.source_trust_tier:
        fields.extend(("source_document_index.source_trust_tier", "source_manifest.source_trust_tier"))
    if record.license_state != license_.license_state:
        fields.extend(("raw_evidence_record.license_state", "license_manifest.license_state"))
    if index.license_state != license_.license_state:
        fields.extend(("source_document_index.license_state", "license_manifest.license_state"))
    if record.source_document_id != index.source_document_id:
        fields.extend(("raw_evidence_record.source_document_id", "source_document_index.source_document_id"))
    if record.source_url_or_doc_id != source.source_url_or_doc_id:
        fields.extend(("raw_evidence_record.source_url_or_doc_id", "source_manifest.source_url_or_doc_id"))
    if vault.evidence_record_count != 1:
        fields.append("raw_evidence_vault_manifest.evidence_record_count")
    if fields:
        field_refs = tuple(dict.fromkeys(fields))
        results.append(
            _reject(
                artifact,
                "source_manifest_ref_validator",
                "raw_evidence_source_document_ref_mismatch",
                ",".join(field_refs),
                field_refs,
            )
        )
        return
    results.append(_accept(artifact, "source_manifest_ref_validator"))
    results.append(_accept(artifact, "license_manifest_ref_validator"))


def _append_pair_rights_scope_result(
    results: list[ValidatorResult],
    artifact: Mapping[str, Any],
    record: FLWCRawEvidenceRecordV1 | None,
    index: FLWCSourceDocumentIndexV1 | None,
    source: FLWCSourceManifestV1 | None,
    license_: FLWCLicenseManifestV1 | None,
) -> None:
    if None in (record, index, source, license_):
        results.append(_reject(artifact, "rights_scope_validator", "raw_evidence_pair_artifact_invalid", fields=("rights_scope",)))
        return
    assert record is not None and index is not None and source is not None and license_ is not None
    values = (record.rights_scope, index.rights_scope, source.rights_scope, license_.rights_scope)
    if len(set(values)) != 1:
        results.append(
            _reject(
                artifact,
                "rights_scope_validator",
                "rights_scope_mismatch",
                fields=(
                    "raw_evidence_record.rights_scope",
                    "source_document_index.rights_scope",
                    "source_manifest.rights_scope",
                    "license_manifest.rights_scope",
                ),
            )
        )
        return
    _append_record_rights_scope_result(results, artifact, record)


def _append_pair_raw_storage_policy_result(
    results: list[ValidatorResult],
    artifact: Mapping[str, Any],
    vault: FLWCRawEvidenceVaultManifestV1 | None,
    record: FLWCRawEvidenceRecordV1 | None,
    index: FLWCSourceDocumentIndexV1 | None,
    source: FLWCSourceManifestV1 | None,
    license_: FLWCLicenseManifestV1 | None,
) -> None:
    if None in (vault, record, index, source, license_):
        results.append(_reject(artifact, "raw_storage_policy_validator", "raw_evidence_pair_artifact_invalid", fields=("raw_storage_policy",)))
        return
    assert vault is not None and record is not None and index is not None and source is not None and license_ is not None
    values = (record.raw_storage_policy, index.raw_storage_policy, source.raw_storage_policy, license_.raw_storage_policy)
    if len(set(values)) != 1:
        results.append(
            _reject(
                artifact,
                "raw_storage_policy_validator",
                "raw_storage_policy_mismatch",
                fields=(
                    "raw_evidence_record.raw_storage_policy",
                    "source_document_index.raw_storage_policy",
                    "source_manifest.raw_storage_policy",
                    "license_manifest.raw_storage_policy",
                ),
            )
        )
        return
    summary_value = dict(vault.raw_storage_policy_summary).get(source.source_manifest_id)
    if summary_value != source.raw_storage_policy.value:
        results.append(
            _reject(
                artifact,
                "raw_storage_policy_validator",
                "raw_storage_policy_summary_mismatch",
                fields=("raw_evidence_vault_manifest.raw_storage_policy_summary",),
            )
        )
        return
    _append_record_raw_storage_policy_result(results, artifact, record)


def _append_pair_retention_policy_result(
    results: list[ValidatorResult],
    artifact: Mapping[str, Any],
    vault: FLWCRawEvidenceVaultManifestV1 | None,
    source: FLWCSourceManifestV1 | None,
    license_: FLWCLicenseManifestV1 | None,
) -> None:
    raw_record = artifact.get("raw_evidence_record")
    raw_index = artifact.get("source_document_index")
    record_retention = raw_record.get("retention_policy") if isinstance(raw_record, Mapping) else None
    index_retention = raw_index.get("retention_policy") if isinstance(raw_index, Mapping) else None
    if None in (vault, source, license_):
        results.append(_reject(artifact, "retention_policy_validator", "raw_evidence_pair_artifact_invalid", fields=("retention_policy",)))
        return
    assert vault is not None and source is not None and license_ is not None
    fields: list[str] = []
    if not _is_non_empty_string(source.retention_policy):
        fields.append("source_manifest.retention_policy")
    if not _is_non_empty_string(license_.retention_policy):
        fields.append("license_manifest.retention_policy")
    summary_value = dict(vault.retention_policy_summary).get(source.source_manifest_id)
    if not _is_non_empty_string(record_retention):
        fields.append("raw_evidence_record.retention_policy")
    if not _is_non_empty_string(index_retention):
        fields.append("source_document_index.retention_policy")
    if (
        summary_value != source.retention_policy
        or summary_value != license_.retention_policy
        or record_retention != source.retention_policy
        or index_retention != source.retention_policy
    ):
        fields.append("raw_evidence_vault_manifest.retention_policy_summary")
    if fields:
        field_refs = tuple(dict.fromkeys(fields))
        results.append(_reject(artifact, "retention_policy_validator", "retention_policy_missing", fields=field_refs))
        return
    review = tuple(
        field
        for field, value in (
            ("source_manifest.retention_policy", source.retention_policy),
            ("license_manifest.retention_policy", license_.retention_policy),
            ("raw_evidence_vault_manifest.retention_policy_summary", summary_value or ""),
            ("raw_evidence_record.retention_policy", str(record_retention or "")),
            ("source_document_index.retention_policy", str(index_retention or "")),
        )
        if value.strip().lower() in REVIEW_RETENTION_VALUES
    )
    if review:
        results.append(_hold(artifact, "retention_policy_validator", "retention_policy_requires_review", fields=review))
        return
    results.append(_accept(artifact, "retention_policy_validator"))


def _append_pair_timestamp_result(
    results: list[ValidatorResult],
    artifact: Mapping[str, Any],
    vault: FLWCRawEvidenceVaultManifestV1 | None,
    record: FLWCRawEvidenceRecordV1 | None,
    index: FLWCSourceDocumentIndexV1 | None,
) -> None:
    if None in (vault, record, index):
        results.append(_reject(artifact, "timestamp_validator", "raw_evidence_pair_artifact_invalid", fields=("source_timestamp_ns",)))
        return
    assert vault is not None and record is not None and index is not None
    fields: list[str] = []
    if record.source_timestamp_ns is None:
        fields.append("raw_evidence_record.source_timestamp_ns")
    if index.source_timestamp_ns is None:
        fields.append("source_document_index.source_timestamp_ns")
    if fields:
        results.append(_reject(artifact, "timestamp_validator", "source_timestamp_missing", fields=tuple(fields)))
        return
    assert record.source_timestamp_ns is not None and index.source_timestamp_ns is not None
    if (
        record.available_from_ns > vault.source_cutoff_ns
        or index.available_from_ns > vault.source_cutoff_ns
        or record.source_timestamp_ns > vault.source_cutoff_ns
        or index.source_timestamp_ns > vault.source_cutoff_ns
    ):
        results.append(
            _reject(
                artifact,
                "available_from_asof_validator",
                "available_from_after_source_cutoff",
                fields=(
                    "raw_evidence_vault_manifest.source_cutoff_ns",
                    "raw_evidence_record.available_from_ns",
                    "source_document_index.available_from_ns",
                ),
            )
        )
        return
    results.append(_accept(artifact, "timestamp_validator"))
    results.append(_accept(artifact, "available_from_asof_validator"))


def _append_pair_raw_hash_reference_result(
    results: list[ValidatorResult],
    artifact: Mapping[str, Any],
    record: FLWCRawEvidenceRecordV1 | None,
    index: FLWCSourceDocumentIndexV1 | None,
) -> None:
    if record is None or index is None:
        results.append(_reject(artifact, "raw_hash_reference_validator", "raw_evidence_pair_artifact_invalid", fields=("raw_text_hash",)))
        return
    fields: list[str] = []
    if record.raw_text_ref_policy in RAW_TEXT_REFERENCE_POLICIES_REQUIRING_HASH and not _is_non_empty_string(record.raw_text_hash):
        fields.append("raw_evidence_record.raw_text_hash")
    if index.raw_storage_policy in RAW_TEXT_STORAGE_POLICIES and not _is_non_empty_string(index.document_hash):
        fields.append("source_document_index.document_hash")
    if fields:
        field_refs = tuple(fields)
        results.append(_reject(artifact, "raw_hash_reference_validator", "raw_text_hash_missing", ",".join(field_refs), field_refs))
        return
    results.append(_accept(artifact, "raw_hash_reference_validator"))


def _append_pair_source_span_ref_result(
    results: list[ValidatorResult],
    artifact: Mapping[str, Any],
    record: FLWCRawEvidenceRecordV1 | None,
    index: FLWCSourceDocumentIndexV1 | None,
) -> None:
    if record is None or index is None:
        results.append(_reject(artifact, "source_span_ref_validator", "raw_evidence_pair_artifact_invalid", fields=("source_span_refs",)))
        return
    invalid: list[str] = []
    out_of_range: list[str] = []
    for ref in record.source_span_refs:
        parsed = _parse_span_ref(ref, index.source_document_id)
        if parsed is None:
            invalid.append(ref)
            continue
        start, end = parsed
        if start < 1 or end < start or end > index.segment_count:
            out_of_range.append(ref)
    if invalid:
        results.append(_reject(artifact, "source_span_ref_validator", "source_span_ref_invalid", ",".join(invalid), ("raw_evidence_record.source_span_refs",)))
        return
    if out_of_range:
        results.append(
            _reject(
                artifact,
                "source_span_ref_validator",
                "source_document_segment_ref_invalid",
                ",".join(out_of_range),
                ("raw_evidence_record.source_span_refs", "source_document_index.segment_count"),
            )
        )
        return
    results.append(_accept(artifact, "source_span_ref_validator"))


def _append_pair_lineage_digest_result(
    results: list[ValidatorResult],
    artifact: Mapping[str, Any],
    vault: FLWCRawEvidenceVaultManifestV1 | None,
    record: FLWCRawEvidenceRecordV1 | None,
    index: FLWCSourceDocumentIndexV1 | None,
) -> None:
    fields: list[str] = []
    if vault is None or not _is_non_empty_string(vault.lineage_digest):
        fields.append("raw_evidence_vault_manifest.lineage_digest")
    if record is None or not _is_non_empty_string(record.lineage_digest):
        fields.append("raw_evidence_record.lineage_digest")
    if index is None or not _is_non_empty_string(index.segment_index_digest):
        fields.append("source_document_index.segment_index_digest")
    if fields:
        field_refs = tuple(fields)
        results.append(_reject(artifact, "lineage_digest_validator", "lineage_digest_missing", ",".join(field_refs), field_refs))
        return
    results.append(_accept(artifact, "lineage_digest_validator"))


def _append_pair_prompt_injection_result(
    results: list[ValidatorResult],
    artifact: Mapping[str, Any],
    vault: FLWCRawEvidenceVaultManifestV1 | None,
    record: FLWCRawEvidenceRecordV1 | None,
    source: FLWCSourceManifestV1 | None,
) -> None:
    if record is None or source is None or vault is None:
        results.append(_reject(artifact, "prompt_injection_flag_validator", "raw_evidence_pair_artifact_invalid", fields=("prompt_injection_flags",)))
        return
    raw_index = artifact.get("source_document_index")
    index_flags = ensure_strings(raw_index.get("prompt_injection_flags", []) if isinstance(raw_index, Mapping) else [])
    summary_value = dict(vault.prompt_injection_policy_summary).get(source.source_manifest_id)
    if summary_value != source.prompt_injection_policy.value:
        results.append(
            _reject(
                artifact,
                "prompt_injection_flag_validator",
                "prompt_injection_policy_summary_mismatch",
                fields=("raw_evidence_vault_manifest.prompt_injection_policy_summary", "source_manifest.prompt_injection_policy"),
            )
        )
        return
    if record.prompt_injection_flags and record.quarantine_status != QuarantineStatus.QUARANTINED_FOR_PROMPT_INJECTION:
        results.append(
            _reject(
                artifact,
                "prompt_injection_flag_validator",
                "prompt_injection_quarantine_missing",
                fields=("raw_evidence_record.prompt_injection_flags", "raw_evidence_record.quarantine_status"),
            )
        )
        return
    if index_flags:
        results.append(
            _reject(
                artifact,
                "prompt_injection_flag_validator",
                "prompt_injection_quarantine_missing",
                fields=("source_document_index.prompt_injection_flags",),
            )
        )
        return
    if record.prompt_injection_flags or source.prompt_injection_policy == PromptInjectionPolicy.QUARANTINE_ON_SUSPECTED_INJECTION:
        results.append(
            _hold(
                artifact,
                "prompt_injection_flag_validator",
                "prompt_injection_quarantined",
                fields=("raw_evidence_record.prompt_injection_flags", "raw_evidence_record.quarantine_status"),
            )
        )
        return
    results.append(_accept(artifact, "prompt_injection_flag_validator"))


def _append_pair_non_claims_result(results: list[ValidatorResult], artifact: Mapping[str, Any]) -> None:
    fields: list[str] = []
    missing: set[str] = set()
    for field in ("raw_evidence_vault_manifest", "raw_evidence_record", "source_document_index"):
        value = artifact.get(field)
        claims = set(ensure_strings(value.get("non_claims", []) if isinstance(value, Mapping) else []))
        local_missing = set(MANDATORY_RAW_EVIDENCE_NON_CLAIMS) - claims
        if local_missing:
            fields.append(f"{field}.non_claims")
            missing |= local_missing
    if fields:
        results.append(_reject(artifact, "non_claims_validator", "missing_mandatory_non_claims", ",".join(sorted(missing)), tuple(fields)))
        return
    results.append(_accept(artifact, "non_claims_validator"))


def _append_pair_synthetic_fixture_scope_result(
    results: list[ValidatorResult],
    artifact: Mapping[str, Any],
    vault: FLWCRawEvidenceVaultManifestV1 | None,
    record: FLWCRawEvidenceRecordV1 | None,
    index: FLWCSourceDocumentIndexV1 | None,
) -> None:
    if vault is None or record is None or index is None:
        results.append(_reject(artifact, "synthetic_fixture_scope_validator", "raw_evidence_pair_artifact_invalid", fields=("vault_scope",)))
        return
    fields: list[str] = []
    if vault.vault_scope != VaultScope.SYNTHETIC_FIXTURE_ONLY:
        fields.append("raw_evidence_vault_manifest.vault_scope")
    if vault.validation_status != ValidatorStatus.ACCEPT:
        fields.append("raw_evidence_vault_manifest.validation_status")
    if record.source_class != SourceClass.SYNTHETIC_FIXTURE:
        fields.append("raw_evidence_record.source_class")
    if record.license_state != LicenseState.ALLOWED_FULL_TEXT:
        fields.append("raw_evidence_record.license_state")
    if record.rights_scope != RightsScope.RESEARCH_INTERNAL_ONLY:
        fields.append("raw_evidence_record.rights_scope")
    if record.raw_storage_policy != RawStoragePolicy.ALLOWED_FULL_TEXT:
        fields.append("raw_evidence_record.raw_storage_policy")
    if record.raw_text_ref_policy != RawTextRefPolicy.SYNTHETIC_FIXTURE_TEXT_ALLOWED:
        fields.append("raw_evidence_record.raw_text_ref_policy")
    if record.validation_status != ValidatorStatus.ACCEPT:
        fields.append("raw_evidence_record.validation_status")
    if _looks_like_live_url(record.source_url_or_doc_id):
        fields.append("raw_evidence_record.source_url_or_doc_id")
    if index.source_trust_tier != SourceTrustTier.TIER_4_MANUAL_REVIEW_ONLY:
        fields.append("source_document_index.source_trust_tier")
    if index.license_state != LicenseState.ALLOWED_FULL_TEXT:
        fields.append("source_document_index.license_state")
    if index.rights_scope != RightsScope.RESEARCH_INTERNAL_ONLY:
        fields.append("source_document_index.rights_scope")
    if index.raw_storage_policy != RawStoragePolicy.ALLOWED_FULL_TEXT:
        fields.append("source_document_index.raw_storage_policy")
    if index.validation_status != ValidatorStatus.ACCEPT:
        fields.append("source_document_index.validation_status")
    if fields:
        field_refs = tuple(dict.fromkeys(fields))
        results.append(
            _reject(artifact, "synthetic_fixture_scope_validator", "synthetic_fixture_scope_invalid", ",".join(field_refs), field_refs)
        )
        return
    results.append(_accept(artifact, "synthetic_fixture_scope_validator"))


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
    if "raw_evidence_vault_manifest" in artifact:
        vault = artifact.get("raw_evidence_vault_manifest")
        record = artifact.get("raw_evidence_record")
        index = artifact.get("source_document_index")
        vault_id = vault.get("vault_manifest_id") if isinstance(vault, Mapping) else None
        evidence_id = record.get("evidence_id") if isinstance(record, Mapping) else None
        doc_id = index.get("source_document_id") if isinstance(index, Mapping) else None
        return f"{vault_id or 'unknown_vault'}:{evidence_id or 'unknown_evidence'}:{doc_id or 'unknown_document'}"
    for field in ("vault_manifest_id", "evidence_id", "source_document_id", "source_manifest_ref", "license_manifest_ref"):
        value = artifact.get(field)
        if isinstance(value, str) and value.strip():
            return value
    return f"unknown_{artifact_type}"


def _artifact_schema_version(artifact: Mapping[str, Any]) -> str:
    value = artifact.get("schema_version")
    return value if isinstance(value, str) else ""


def _input_refs(artifact: Mapping[str, Any]) -> tuple[str, ...]:
    refs: list[str] = []
    for key in (
        "vault_manifest_id",
        "evidence_id",
        "source_document_id",
        "source_manifest_ref",
        "license_manifest_ref",
        "source_manifest_id",
        "license_manifest_id",
        "source_id",
    ):
        value = artifact.get(key)
        if isinstance(value, str) and value.strip():
            refs.append(value)
    for key in ("raw_evidence_vault_manifest", "raw_evidence_record", "source_document_index", "source_manifest", "license_manifest"):
        value = artifact.get(key)
        if isinstance(value, Mapping):
            refs.extend(_input_refs(value))
    return tuple(refs)


def _non_claims_checked(artifact: Mapping[str, Any]) -> tuple[str, ...]:
    claims = list(ensure_strings(artifact.get("non_claims", [])))
    for key in ("raw_evidence_vault_manifest", "raw_evidence_record", "source_document_index", "source_manifest", "license_manifest"):
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


def _empty_list_fields(artifact: Mapping[str, Any], fields: tuple[str, ...]) -> tuple[str, ...]:
    return tuple(
        field
        for field in fields
        if not isinstance(artifact.get(field), list) or not artifact.get(field) or any(not _is_non_empty_string(item) for item in artifact[field])
    )


def _parse_span_ref(value: str, source_document_id: str) -> tuple[int, int] | None:
    segment_match = SEGMENT_REF_RE.fullmatch(value)
    if segment_match:
        if segment_match.group("doc") != source_document_id:
            return None
        segment = int(segment_match.group("segment"))
        return segment, segment
    span_match = SPAN_REF_RE.fullmatch(value)
    if not span_match or span_match.group("doc") != source_document_id:
        return None
    return int(span_match.group("start")), int(span_match.group("end"))


def _find_forbidden_boundary_keys(value: object, prefix: str = "") -> tuple[str, ...]:
    fields: list[str] = []
    if isinstance(value, Mapping):
        for key, item in value.items():
            key_text = str(key)
            field_ref = f"{prefix}.{key_text}" if prefix else key_text
            if key_text in FORBIDDEN_BOUNDARY_KEYS:
                fields.append(field_ref)
            fields.extend(_find_forbidden_boundary_keys(item, field_ref))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            fields.extend(_find_forbidden_boundary_keys(item, f"{prefix}[{index}]"))
    return tuple(fields)


def _find_inline_raw_text_payload_keys(value: object, prefix: str = "") -> tuple[str, ...]:
    fields: list[str] = []
    if isinstance(value, Mapping):
        for key, item in value.items():
            key_text = str(key)
            field_ref = f"{prefix}.{key_text}" if prefix else key_text
            if key_text in INLINE_RAW_TEXT_PAYLOAD_KEYS:
                fields.append(field_ref)
            fields.extend(_find_inline_raw_text_payload_keys(item, field_ref))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            fields.extend(_find_inline_raw_text_payload_keys(item, f"{prefix}[{index}]"))
    return tuple(fields)


def _looks_like_live_url(value: str) -> bool:
    return value.strip().lower().startswith(("http://", "https://"))


def _is_non_empty_string(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _is_positive_int(value: object) -> bool:
    return type(value) is int and value > 0


__all__ = [
    "validate_raw_evidence_index_pair",
    "validate_raw_evidence_index_pair_file",
    "validate_raw_evidence_record",
    "validate_raw_evidence_record_file",
    "validate_raw_evidence_vault_manifest",
    "validate_raw_evidence_vault_manifest_file",
    "validate_source_document_index",
    "validate_source_document_index_file",
]
