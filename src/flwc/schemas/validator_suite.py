from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from enum import Enum

from flwc.schemas.common import SchemaIssue, ValidatorStatus


class ValidatorFamily(str, Enum):
    SCHEMA = "schema"
    SOURCE_MANIFEST = "source_manifest"
    LICENSE_MANIFEST = "license_manifest"
    SOURCE_LICENSE_PAIRING = "source_license_pairing"
    RIGHTS_SCOPE = "rights_scope"
    RAW_STORAGE_POLICY = "raw_storage_policy"
    TIMESTAMP = "timestamp"
    AVAILABLE_FROM_ASOF = "available_from_asof"
    LINEAGE_DIGEST = "lineage_digest"
    SOURCE_SPAN = "source_span"
    CLAIM_EVENT_REF = "claim_event_ref"
    ENTITY_ASSET_LINK = "entity_asset_link"
    PAYLOAD_POLICY = "payload_policy"
    BOUNDED_PAYLOAD = "bounded_payload"
    RAW_TEXT_DENIAL = "raw_text_denial"
    RAW_LLM_OUTPUT_DENIAL = "raw_llm_output_denial"
    FUTURE_OUTCOME_DENIAL = "future_outcome_denial"
    TRADE_FIELD_DENIAL = "trade_field_denial"
    ORDER_INTENT_DENIAL = "order_intent_denial"
    POSITION_TARGET_DENIAL = "position_target_denial"
    CREDENTIAL_LEAK = "credential_leak"
    PROMPT_INJECTION = "prompt_injection"
    NON_CLAIMS = "non_claims"
    SNAPSHOT_INTEGRITY_FUTURE = "snapshot_integrity_future"
    HUMAN_REVIEW_ROUTE = "human_review_route"


class ValidatorScope(str, Enum):
    SOURCE_MANIFEST = "source_manifest"
    LICENSE_MANIFEST = "license_manifest"
    RAW_EVIDENCE_RECORD = "raw_evidence_record"
    SOURCE_DOCUMENT_INDEX = "source_document_index"
    ATOMIC_CLAIM = "atomic_claim"
    FINANCIAL_EVENT = "financial_event"
    CANDIDATE_EVIDENCE_PACKAGE = "candidate_evidence_package"
    CANDIDATE_EVIDENCE_RECORD = "candidate_evidence_record"
    CANDIDATE_PAYLOAD_POLICY = "candidate_payload_policy"
    COMPILER_SNAPSHOT_FUTURE = "compiler_snapshot_future"
    SYNTHETIC_FIXTURE = "synthetic_fixture"


class PrimaryRefusalFamily(str, Enum):
    SCHEMA_INVALID = "schema_invalid"
    SOURCE_MISSING = "source_missing"
    LICENSE_MISSING = "license_missing"
    SOURCE_LICENSE_MISMATCH = "source_license_mismatch"
    RIGHTS_SCOPE_INVALID = "rights_scope_invalid"
    STORAGE_POLICY_INVALID = "storage_policy_invalid"
    TIMESTAMP_INVALID = "timestamp_invalid"
    AS_OF_VIOLATION = "as_of_violation"
    LINEAGE_MISMATCH = "lineage_mismatch"
    PROMPT_INJECTION = "prompt_injection"
    CREDENTIAL_LEAK = "credential_leak"
    RAW_TEXT_DENIAL = "raw_text_denial"
    RAW_LLM_OUTPUT_DENIAL = "raw_llm_output_denial"
    FUTURE_OUTCOME = "future_outcome"
    TRADE_FIELD = "trade_field"
    ORDER_INTENT = "order_intent"
    POSITION_TARGET = "position_target"
    UNBOUNDED_PAYLOAD = "unbounded_payload"
    MISSING_NON_CLAIMS = "missing_non_claims"
    ENTITY_MAPPING_AMBIGUOUS = "entity_mapping_ambiguous"
    SOURCE_QUALITY_LOW = "source_quality_low"
    DUPLICATE_OR_STALE = "duplicate_or_stale"
    UNKNOWN = "unknown"


class ReviewStatus(str, Enum):
    NOT_REQUIRED = "not_required"
    HOLD_REVIEW = "hold_review"
    HUMAN_REVIEW_REQUIRED = "human_review_required"
    LEGAL_REVIEW_REQUIRED = "legal_review_required"
    SOURCE_REVIEW_REQUIRED = "source_review_required"
    TIMESTAMP_REVIEW_REQUIRED = "timestamp_review_required"
    ENTITY_REVIEW_REQUIRED = "entity_review_required"
    COMMANDER_REVIEW_REQUIRED = "commander_review_required"
    REJECTED_FINAL = "rejected_final"
    NEUTRALIZED_FINAL = "neutralized_final"
    ACCEPTED_AFTER_FUTURE_REVIEW_PATCH_REQUIRED = "accepted_after_future_review_patch_required"


MANDATORY_VALIDATOR_SUITE_NON_CLAIMS = (
    "synthetic_fixture_only",
    "not_real_source",
    "not_source_ingestion",
    "not_truth_authority",
    "not_runtime_authority",
    "not_external_consumer_docking",
    "not_trade_signal",
    "not_order_intent",
    "not_position_sizing",
    "not_real_claim_ledger",
    "not_real_event_table",
    "not_canonical_snapshot",
    "not_snapshot_sealing",
    "not_wiki_export",
)


@dataclass(frozen=True)
class FLWCRefusalRecordV1:
    refusal_id: str
    refusal_version: str
    artifact_ref: str
    artifact_schema_version: str
    validator_result_refs: tuple[str, ...]
    aggregate_result: ValidatorStatus
    primary_refusal_family: PrimaryRefusalFamily
    reason_codes: tuple[str, ...]
    field_refs: tuple[str, ...]
    source_manifest_refs: tuple[str, ...]
    license_manifest_refs: tuple[str, ...]
    timestamp_refs: tuple[str, ...]
    lineage_digest: str | None
    review_status: ReviewStatus
    review_owner: str | None
    created_at_ns: int
    non_claims: tuple[str, ...]
    schema_version: str = "FLWCRefusalRecordV1"

    @classmethod
    def from_mapping(cls, value: object) -> tuple["FLWCRefusalRecordV1 | None", tuple[SchemaIssue, ...]]:
        if not isinstance(value, Mapping):
            return None, (SchemaIssue("artifact_not_mapping", ("$",), "refusal record must be a JSON object"),)

        issues: list[SchemaIssue] = []
        schema_version = _require_exact_string(value, "schema_version", "FLWCRefusalRecordV1", issues)
        refusal_id = _require_string(value, "refusal_id", issues)
        refusal_version = _require_string(value, "refusal_version", issues)
        artifact_ref = _require_string(value, "artifact_ref", issues)
        artifact_schema_version = _require_string(value, "artifact_schema_version", issues)
        validator_result_refs = _require_string_list(value, "validator_result_refs", issues, non_empty=True)
        aggregate_result = _require_enum(value, "aggregate_result", ValidatorStatus, issues)
        primary_refusal_family = _require_enum(value, "primary_refusal_family", PrimaryRefusalFamily, issues)
        reason_codes = _require_string_list(value, "reason_codes", issues, non_empty=True)
        field_refs = _require_string_list(value, "field_refs", issues, non_empty=False)
        source_manifest_refs = _require_string_list(value, "source_manifest_refs", issues, non_empty=False)
        license_manifest_refs = _require_string_list(value, "license_manifest_refs", issues, non_empty=False)
        timestamp_refs = _require_string_list(value, "timestamp_refs", issues, non_empty=False)
        lineage_digest = _require_optional_string(value, "lineage_digest", issues)
        review_status = _require_enum(value, "review_status", ReviewStatus, issues)
        review_owner = _require_optional_string(value, "review_owner", issues)
        created_at_ns = _require_positive_int(value, "created_at_ns", issues)
        non_claims = _require_string_list(value, "non_claims", issues, non_empty=True)
        if issues:
            return None, tuple(issues)
        return (
            cls(
                schema_version=schema_version,
                refusal_id=refusal_id,
                refusal_version=refusal_version,
                artifact_ref=artifact_ref,
                artifact_schema_version=artifact_schema_version,
                validator_result_refs=validator_result_refs,
                aggregate_result=aggregate_result,
                primary_refusal_family=primary_refusal_family,
                reason_codes=reason_codes,
                field_refs=field_refs,
                source_manifest_refs=source_manifest_refs,
                license_manifest_refs=license_manifest_refs,
                timestamp_refs=timestamp_refs,
                lineage_digest=lineage_digest,
                review_status=review_status,
                review_owner=review_owner,
                created_at_ns=created_at_ns,
                non_claims=non_claims,
            ),
            (),
        )

    def as_dict(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "refusal_id": self.refusal_id,
            "refusal_version": self.refusal_version,
            "artifact_ref": self.artifact_ref,
            "artifact_schema_version": self.artifact_schema_version,
            "validator_result_refs": list(self.validator_result_refs),
            "aggregate_result": self.aggregate_result.value,
            "primary_refusal_family": self.primary_refusal_family.value,
            "reason_codes": list(self.reason_codes),
            "field_refs": list(self.field_refs),
            "source_manifest_refs": list(self.source_manifest_refs),
            "license_manifest_refs": list(self.license_manifest_refs),
            "timestamp_refs": list(self.timestamp_refs),
            "lineage_digest": self.lineage_digest,
            "review_status": self.review_status.value,
            "review_owner": self.review_owner,
            "created_at_ns": self.created_at_ns,
            "non_claims": list(self.non_claims),
        }


def _require_exact_string(value: Mapping[str, object], field: str, expected: str, issues: list[SchemaIssue]) -> str:
    raw = value.get(field)
    if raw != expected:
        issues.append(SchemaIssue("schema_version_invalid", (field,), f"expected {expected}"))
        return ""
    return expected


def _require_string(value: Mapping[str, object], field: str, issues: list[SchemaIssue]) -> str:
    raw = value.get(field)
    if not isinstance(raw, str) or not raw.strip():
        issues.append(SchemaIssue("required_field_missing", (field,), "non-empty string required"))
        return ""
    return raw


def _require_optional_string(value: Mapping[str, object], field: str, issues: list[SchemaIssue]) -> str | None:
    raw = value.get(field)
    if raw is None:
        return None
    if not isinstance(raw, str) or not raw.strip():
        issues.append(SchemaIssue("field_type_invalid", (field,), "null or non-empty string required"))
        return None
    return raw


def _require_positive_int(value: Mapping[str, object], field: str, issues: list[SchemaIssue]) -> int:
    raw = value.get(field)
    if type(raw) is not int or raw <= 0:
        issues.append(SchemaIssue("field_type_invalid", (field,), "positive int required"))
        return 0
    return raw


def _require_string_list(
    value: Mapping[str, object], field: str, issues: list[SchemaIssue], *, non_empty: bool
) -> tuple[str, ...]:
    raw = value.get(field)
    if not isinstance(raw, list) or any(not isinstance(item, str) or not item.strip() for item in raw):
        issues.append(SchemaIssue("field_type_invalid", (field,), "list of non-empty strings required"))
        return ()
    if non_empty and not raw:
        issues.append(SchemaIssue("required_list_empty", (field,), "non-empty list required"))
        return ()
    return tuple(raw)


def _require_enum(value: Mapping[str, object], field: str, enum_type: type[Enum], issues: list[SchemaIssue]):
    raw = value.get(field)
    try:
        return enum_type(raw)
    except ValueError:
        issues.append(SchemaIssue("enum_value_invalid", (field,), f"invalid {field}"))
        first_value = next(iter(enum_type))
        return first_value


__all__ = [
    "FLWCRefusalRecordV1",
    "MANDATORY_VALIDATOR_SUITE_NON_CLAIMS",
    "PrimaryRefusalFamily",
    "ReviewStatus",
    "ValidatorFamily",
    "ValidatorScope",
]
