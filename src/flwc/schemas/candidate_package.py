from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class PackageScope(str, Enum):
    SYNTHETIC_FIXTURE_ONLY = "synthetic_fixture_only"
    HUMAN_REVIEW_CANDIDATE = "human_review_candidate"
    WIKI_REVIEW_CANDIDATE = "wiki_review_candidate"
    EXTERNAL_CONSUMER_CANDIDATE_FUTURE_AUTHORIZATION_REQUIRED = "external_consumer_candidate_future_authorization_required"
    SNAPSHOT_EXPORT_CANDIDATE = "snapshot_export_candidate"
    QUARANTINE_REVIEW_CANDIDATE = "quarantine_review_candidate"


class PackageStatus(str, Enum):
    PROPOSED = "proposed"
    HOLD_REVIEW = "hold_review"
    VALIDATED_CANDIDATE = "validated_candidate"
    REJECTED = "rejected"
    NEUTRALIZED = "neutralized"
    SUPERSEDED = "superseded"
    EXPIRED = "expired"


class PayloadClass(str, Enum):
    MANIFEST_REFS_ONLY = "manifest_refs_only"
    CLAIM_EVENT_REFS_ONLY = "claim_event_refs_only"
    BOUNDED_DERIVED_FIELDS = "bounded_derived_fields"
    BOUNDED_REVIEW_SUMMARY = "bounded_review_summary"
    VALIDATOR_FLAGS_ONLY = "validator_flags_only"
    SYNTHETIC_FIXTURE_PAYLOAD = "synthetic_fixture_payload"


PAYLOAD_FALSE_FLAGS = (
    "raw_text_in_payload",
    "raw_llm_output_in_payload",
    "full_rag_context_in_payload",
    "future_outcome_in_payload",
    "trade_signal_fields_present",
    "order_intent_fields_present",
    "position_target_fields_present",
    "broker_or_execution_fields_present",
)

PACKAGE_REF_LIST_FIELDS = (
    "input_raw_evidence_vault_manifest_refs",
    "input_raw_evidence_record_refs",
    "input_source_document_index_refs",
    "input_claim_ledger_refs",
    "input_event_table_refs",
    "source_manifest_refs",
    "license_manifest_refs",
)

PACKAGE_OPTIONAL_STRING_FIELDS = (
    "compiler_snapshot_ref",
    "refusal_summary_ref",
    "validator_summary_ref",
)

PACKAGE_STRING_FIELDS = (
    "candidate_package_id",
    "candidate_contract_version",
    "producer_id",
    "producer_version",
    "candidate_digest",
    "lineage_digest",
)

PACKAGE_POSITIVE_INT_FIELDS = (
    "candidate_build_as_of_ns",
    "source_cutoff_ns",
    "created_at_ns",
    "package_sequence",
)

PACKAGE_NONNEGATIVE_INT_FIELDS = ("candidate_count",)

PACKAGE_MAP_FIELDS = (
    "license_state_summary",
    "rights_scope_summary",
    "raw_storage_policy_summary",
)

MANDATORY_PACKAGE_NON_CLAIMS = (
    "not_accepted_evidence",
    "not_truth_authority",
    "not_source_authority",
    "not_license_authority",
    "not_runtime_authority",
    "not_external_admission_authority",
    "not_trade_signal",
    "not_order_intent",
    "not_position_sizing",
    "not_market_data_authority",
)

MANDATORY_SYNTHETIC_NON_CLAIMS = (
    "synthetic_fixture_only",
    "not_real_source",
    "not_source_ingestion",
)


@dataclass(frozen=True)
class SchemaIssue:
    reason_code: str
    field_refs: tuple[str, ...]
    detail: str = ""


@dataclass(frozen=True)
class FLWCCandidatePayloadPolicyV1:
    raw_text_in_payload: bool
    raw_llm_output_in_payload: bool
    full_rag_context_in_payload: bool
    future_outcome_in_payload: bool
    trade_signal_fields_present: bool
    order_intent_fields_present: bool
    position_target_fields_present: bool
    broker_or_execution_fields_present: bool
    runtime_payload_bounded: bool
    max_payload_bytes: int
    allowed_payload_classes: tuple[PayloadClass, ...]
    redaction_policy_ref: str | None
    schema_version: str = "FLWCCandidatePayloadPolicyV1"

    @classmethod
    def from_mapping(
        cls, value: object, *, field_prefix: str = "payload_policy"
    ) -> tuple["FLWCCandidatePayloadPolicyV1 | None", tuple[SchemaIssue, ...]]:
        issues: list[SchemaIssue] = []
        if not isinstance(value, Mapping):
            return None, (SchemaIssue("required_field_missing", (field_prefix,), "payload_policy missing or invalid"),)

        schema_version = _require_exact_string(
            value,
            "schema_version",
            "FLWCCandidatePayloadPolicyV1",
            issues,
            field_prefix=field_prefix,
        )
        bool_values = {
            field: _require_bool(value, field, issues, field_prefix=field_prefix)
            for field in (*PAYLOAD_FALSE_FLAGS, "runtime_payload_bounded")
        }
        max_payload_bytes = _require_positive_int(value, "max_payload_bytes", issues, field_prefix=field_prefix)
        allowed_payload_classes = _require_payload_classes(value, "allowed_payload_classes", issues, field_prefix=field_prefix)
        redaction_policy_ref = _require_optional_string(value, "redaction_policy_ref", issues, field_prefix=field_prefix)

        if issues:
            return None, tuple(issues)

        return (
            cls(
                schema_version=schema_version,
                raw_text_in_payload=bool_values["raw_text_in_payload"],
                raw_llm_output_in_payload=bool_values["raw_llm_output_in_payload"],
                full_rag_context_in_payload=bool_values["full_rag_context_in_payload"],
                future_outcome_in_payload=bool_values["future_outcome_in_payload"],
                trade_signal_fields_present=bool_values["trade_signal_fields_present"],
                order_intent_fields_present=bool_values["order_intent_fields_present"],
                position_target_fields_present=bool_values["position_target_fields_present"],
                broker_or_execution_fields_present=bool_values["broker_or_execution_fields_present"],
                runtime_payload_bounded=bool_values["runtime_payload_bounded"],
                max_payload_bytes=max_payload_bytes,
                allowed_payload_classes=allowed_payload_classes,
                redaction_policy_ref=redaction_policy_ref,
            ),
            (),
        )

    def unsafe_true_flags(self) -> tuple[str, ...]:
        return tuple(field for field in PAYLOAD_FALSE_FLAGS if getattr(self, field) is not False)


@dataclass(frozen=True)
class FLWCCandidateEvidencePackageV1:
    candidate_package_id: str
    candidate_contract_version: str
    producer_id: str
    producer_version: str
    compiler_snapshot_ref: str | None
    candidate_build_as_of_ns: int
    source_cutoff_ns: int
    created_at_ns: int
    package_sequence: int
    package_scope: PackageScope
    package_status: PackageStatus
    candidate_count: int
    candidate_digest: str
    input_raw_evidence_vault_manifest_refs: tuple[str, ...]
    input_raw_evidence_record_refs: tuple[str, ...]
    input_source_document_index_refs: tuple[str, ...]
    input_claim_ledger_refs: tuple[str, ...]
    input_event_table_refs: tuple[str, ...]
    source_manifest_refs: tuple[str, ...]
    license_manifest_refs: tuple[str, ...]
    license_state_summary: Mapping[str, str]
    rights_scope_summary: Mapping[str, str]
    raw_storage_policy_summary: Mapping[str, str]
    payload_policy: FLWCCandidatePayloadPolicyV1
    refusal_summary_ref: str | None
    validator_summary_ref: str | None
    lineage_digest: str
    validation_status: PackageStatus
    non_claims: tuple[str, ...]
    schema_version: str = "FLWCCandidateEvidencePackageV1"
    schema_issues: tuple[SchemaIssue, ...] = field(default_factory=tuple)

    @classmethod
    def from_mapping(
        cls, value: object
    ) -> tuple["FLWCCandidateEvidencePackageV1 | None", tuple[SchemaIssue, ...]]:
        if not isinstance(value, Mapping):
            return None, (SchemaIssue("artifact_not_mapping", ("$",), "candidate package must be a JSON object"),)

        issues: list[SchemaIssue] = []
        schema_version = _require_exact_string(value, "schema_version", "FLWCCandidateEvidencePackageV1", issues)
        strings = {field: _require_string(value, field, issues) for field in PACKAGE_STRING_FIELDS}
        optional_strings = {field: _require_optional_string(value, field, issues) for field in PACKAGE_OPTIONAL_STRING_FIELDS}
        positive_ints = {field: _require_positive_int(value, field, issues) for field in PACKAGE_POSITIVE_INT_FIELDS}
        nonnegative_ints = {field: _require_nonnegative_int(value, field, issues) for field in PACKAGE_NONNEGATIVE_INT_FIELDS}
        ref_lists = {field: _require_string_list(value, field, issues, non_empty=True) for field in PACKAGE_REF_LIST_FIELDS}
        maps = {field: _require_string_map(value, field, issues, non_empty=True) for field in PACKAGE_MAP_FIELDS}
        package_scope = _require_enum(value, "package_scope", PackageScope, issues)
        package_status = _require_enum(value, "package_status", PackageStatus, issues)
        validation_status = _require_enum(value, "validation_status", PackageStatus, issues)
        non_claims = _require_string_list(value, "non_claims", issues, non_empty=True)
        payload_policy, payload_issues = FLWCCandidatePayloadPolicyV1.from_mapping(value.get("payload_policy"))
        issues.extend(payload_issues)

        if issues:
            return None, tuple(issues)

        return (
            cls(
                schema_version=schema_version,
                candidate_package_id=strings["candidate_package_id"],
                candidate_contract_version=strings["candidate_contract_version"],
                producer_id=strings["producer_id"],
                producer_version=strings["producer_version"],
                compiler_snapshot_ref=optional_strings["compiler_snapshot_ref"],
                candidate_build_as_of_ns=positive_ints["candidate_build_as_of_ns"],
                source_cutoff_ns=positive_ints["source_cutoff_ns"],
                created_at_ns=positive_ints["created_at_ns"],
                package_sequence=positive_ints["package_sequence"],
                package_scope=package_scope,
                package_status=package_status,
                candidate_count=nonnegative_ints["candidate_count"],
                candidate_digest=strings["candidate_digest"],
                input_raw_evidence_vault_manifest_refs=ref_lists["input_raw_evidence_vault_manifest_refs"],
                input_raw_evidence_record_refs=ref_lists["input_raw_evidence_record_refs"],
                input_source_document_index_refs=ref_lists["input_source_document_index_refs"],
                input_claim_ledger_refs=ref_lists["input_claim_ledger_refs"],
                input_event_table_refs=ref_lists["input_event_table_refs"],
                source_manifest_refs=ref_lists["source_manifest_refs"],
                license_manifest_refs=ref_lists["license_manifest_refs"],
                license_state_summary=maps["license_state_summary"],
                rights_scope_summary=maps["rights_scope_summary"],
                raw_storage_policy_summary=maps["raw_storage_policy_summary"],
                payload_policy=payload_policy,
                refusal_summary_ref=optional_strings["refusal_summary_ref"],
                validator_summary_ref=optional_strings["validator_summary_ref"],
                lineage_digest=strings["lineage_digest"],
                validation_status=validation_status,
                non_claims=non_claims,
            ),
            (),
        )


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
    if _missing(value, field_name, issues, field_prefix=field_prefix):
        return None
    field_value = value[field_name]
    if field_value is None:
        return None
    if not isinstance(field_value, str) or not field_value.strip():
        issues.append(SchemaIssue("field_type_invalid", (_field(field_prefix, field_name),), "expected string or null"))
        return None
    return field_value


def _require_bool(value: Mapping[str, Any], field_name: str, issues: list[SchemaIssue], *, field_prefix: str | None = None) -> bool:
    if _missing(value, field_name, issues, field_prefix=field_prefix):
        return False
    field_value = value[field_name]
    if type(field_value) is not bool:
        issues.append(SchemaIssue("field_type_invalid", (_field(field_prefix, field_name),), "expected boolean"))
        return False
    return field_value


def _require_positive_int(
    value: Mapping[str, Any], field_name: str, issues: list[SchemaIssue], *, field_prefix: str | None = None
) -> int:
    if _missing(value, field_name, issues, field_prefix=field_prefix):
        return 0
    field_value = value[field_name]
    if type(field_value) is not int or field_value <= 0:
        issues.append(SchemaIssue("field_type_invalid", (_field(field_prefix, field_name),), "expected positive integer"))
        return 0
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
    field_prefix: str | None = None,
) -> tuple[str, ...]:
    if _missing(value, field_name, issues, field_prefix=field_prefix):
        return ()
    field_value = value[field_name]
    full_field = _field(field_prefix, field_name)
    if not isinstance(field_value, list) or any(not isinstance(item, str) or not item.strip() for item in field_value):
        issues.append(SchemaIssue("field_type_invalid", (full_field,), "expected list of non-empty strings"))
        return ()
    if non_empty and not field_value:
        issues.append(SchemaIssue("required_list_empty", (full_field,), "expected non-empty list"))
    return tuple(field_value)


def _require_string_map(
    value: Mapping[str, Any], field_name: str, issues: list[SchemaIssue], *, non_empty: bool
) -> Mapping[str, str]:
    if _missing(value, field_name, issues):
        return {}
    field_value = value[field_name]
    if not isinstance(field_value, Mapping):
        issues.append(SchemaIssue("field_type_invalid", (field_name,), "expected map[string,string]"))
        return {}
    if non_empty and not field_value:
        issues.append(SchemaIssue("required_map_empty", (field_name,), "expected non-empty map"))
        return {}
    if any(not isinstance(key, str) or not key.strip() or not isinstance(item, str) or not item.strip() for key, item in field_value.items()):
        issues.append(SchemaIssue("field_type_invalid", (field_name,), "expected map[string,string]"))
        return {}
    return dict(field_value)


def _require_enum(value: Mapping[str, Any], field_name: str, enum_type: type[Enum], issues: list[SchemaIssue]) -> Any:
    raw_value = _require_string(value, field_name, issues)
    if not raw_value:
        return None
    try:
        return enum_type(raw_value)
    except ValueError:
        issues.append(SchemaIssue("enum_value_invalid", (field_name,), f"unsupported value {raw_value}"))
        return None


def _require_payload_classes(
    value: Mapping[str, Any], field_name: str, issues: list[SchemaIssue], *, field_prefix: str
) -> tuple[PayloadClass, ...]:
    raw_classes = _require_string_list(value, field_name, issues, non_empty=True, field_prefix=field_prefix)
    payload_classes: list[PayloadClass] = []
    for index, raw_class in enumerate(raw_classes):
        try:
            payload_classes.append(PayloadClass(raw_class))
        except ValueError:
            issues.append(
                SchemaIssue(
                    "enum_value_invalid",
                    (f"{field_prefix}.{field_name}[{index}]",),
                    f"unsupported payload class {raw_class}",
                )
            )
    return tuple(payload_classes)


__all__ = [
    "FLWCCandidateEvidencePackageV1",
    "FLWCCandidatePayloadPolicyV1",
    "MANDATORY_PACKAGE_NON_CLAIMS",
    "MANDATORY_SYNTHETIC_NON_CLAIMS",
    "PACKAGE_REF_LIST_FIELDS",
    "PAYLOAD_FALSE_FLAGS",
    "PackageScope",
    "PackageStatus",
    "PayloadClass",
    "SchemaIssue",
]
