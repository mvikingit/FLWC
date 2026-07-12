from __future__ import annotations

import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from flwc.schemas.common import (
    B0_VALIDATOR_NON_CLAIMS,
    B0_VALIDATOR_PRODUCER_ID,
    B0_VALIDATOR_PRODUCER_VERSION,
    B0_VALIDATOR_RUN_ID,
    B0_VALIDATOR_RUN_NS,
    ValidatorResult,
    ValidatorStatus,
    ValidatorSummary,
)
from flwc.schemas.validator_suite import (
    FLWCRefusalRecordV1,
    MANDATORY_VALIDATOR_SUITE_NON_CLAIMS,
    PrimaryRefusalFamily,
    ReviewStatus,
)
from flwc.validators.claim_event import validate_claim_event_compiler_output
from flwc.validators.core import aggregate_validator_results
from flwc.validators.raw_evidence import validate_raw_evidence_index_pair
from flwc.validators.source_license import validate_source_license_pair


VALIDATOR_SUITE_SUMMARY_ID = "flwc-b2-validator-suite-summary-001"
VALIDATOR_SUITE_ARTIFACT_REF = "flwc-b2-synthetic-validator-suite-packet-001"
VALIDATOR_SUITE_SCHEMA_VERSION = "FLWCValidatorSuitePacketV1"
REFUSAL_VERSION = "FLWC-B2-RefusalRecord-0.0.0"

REQUIRED_SUITE_FIELDS = (
    "source_manifest",
    "license_manifest",
    "raw_evidence_vault_manifest",
    "raw_evidence_record",
    "source_document_index",
    "atomic_claim_ledger",
    "atomic_claim",
    "financial_event_table",
    "financial_event",
)


def validate_fixture_suite_packet(packet: Mapping[str, Any]) -> dict[str, Any]:
    results: list[ValidatorResult] = []
    component_summaries: list[dict[str, Any]] = []

    missing = tuple(field for field in REQUIRED_SUITE_FIELDS if field not in packet or not isinstance(packet.get(field), Mapping))
    if missing:
        results.append(
            _suite_result(
                ValidatorStatus.REJECT,
                "validator_suite_packet_schema_validator",
                "required_field_missing",
                ",".join(missing),
                missing,
            )
        )
    else:
        results.append(_suite_result(ValidatorStatus.ACCEPT, "validator_suite_packet_schema_validator", "accepted"))
        source_license_summary = validate_source_license_pair(packet["source_manifest"], packet["license_manifest"])
        raw_evidence_summary = validate_raw_evidence_index_pair(
            packet["raw_evidence_vault_manifest"],
            packet["raw_evidence_record"],
            packet["source_document_index"],
            packet["source_manifest"],
            packet["license_manifest"],
        )
        claim_event_summary = validate_claim_event_compiler_output(
            packet["atomic_claim_ledger"],
            packet["atomic_claim"],
            packet["financial_event_table"],
            packet["financial_event"],
            packet["raw_evidence_vault_manifest"],
            packet["raw_evidence_record"],
            packet["source_document_index"],
            packet["source_manifest"],
            packet["license_manifest"],
        )
        component_summaries = [source_license_summary, raw_evidence_summary, claim_event_summary]
        for summary in component_summaries:
            results.extend(_validator_results_from_summary(summary))

    aggregate = aggregate_validator_results(results)
    refusal_records = (
        (
            build_refusal_record_from_results(
                results,
                aggregate_result=aggregate,
                artifact_ref=VALIDATOR_SUITE_ARTIFACT_REF,
                packet=packet,
            ),
        )
        if aggregate != ValidatorStatus.ACCEPT
        else ()
    )
    summary = ValidatorSummary(
        validator_summary_id=VALIDATOR_SUITE_SUMMARY_ID,
        run_id=B0_VALIDATOR_RUN_ID,
        input_artifact_refs=_input_artifact_refs(packet),
        validator_results=tuple(results),
        aggregate_result=aggregate,
        refusal_record_refs=tuple(record.refusal_id for record in refusal_records),
        created_at_ns=B0_VALIDATOR_RUN_NS,
        producer_id=B0_VALIDATOR_PRODUCER_ID,
        producer_version=B0_VALIDATOR_PRODUCER_VERSION,
        non_claims=MANDATORY_VALIDATOR_SUITE_NON_CLAIMS,
    )
    output = summary.as_dict()
    output["schema_version"] = "FLWCValidatorSummaryV1"
    output["component_summaries"] = _bounded_component_summaries(component_summaries)
    output["refusal_records"] = [record.as_dict() for record in refusal_records]
    return output


def validate_fixture_suite_packet_file(path: str | Path) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as fh:
        return validate_fixture_suite_packet(json.load(fh))


def build_refusal_record_from_results(
    results: tuple[ValidatorResult, ...] | list[ValidatorResult],
    *,
    aggregate_result: ValidatorStatus | None = None,
    artifact_ref: str = VALIDATOR_SUITE_ARTIFACT_REF,
    packet: Mapping[str, Any] | None = None,
) -> FLWCRefusalRecordV1:
    aggregate = aggregate_result or aggregate_validator_results(results)
    non_accepting = tuple(result for result in results if result.result != ValidatorStatus.ACCEPT)
    primary = _primary_result(non_accepting)
    reason_codes = _unique(result.reason_code for result in non_accepting)
    field_refs = _unique(field for result in non_accepting for field in result.field_refs)[:32]
    return FLWCRefusalRecordV1(
        refusal_id=f"{artifact_ref}:refusal:{aggregate.value.lower()}",
        refusal_version=REFUSAL_VERSION,
        artifact_ref=artifact_ref,
        artifact_schema_version=VALIDATOR_SUITE_SCHEMA_VERSION,
        validator_result_refs=tuple(result.result_ref() for result in non_accepting),
        aggregate_result=aggregate,
        primary_refusal_family=_primary_refusal_family(primary),
        reason_codes=reason_codes,
        field_refs=field_refs,
        source_manifest_refs=_refs_for_suffix(packet, "source_manifest", "source_manifest_id"),
        license_manifest_refs=_refs_for_suffix(packet, "license_manifest", "license_manifest_id"),
        timestamp_refs=_timestamp_refs(field_refs),
        lineage_digest=_first_lineage_digest(packet),
        review_status=_review_status_for_aggregate(aggregate),
        review_owner=None,
        created_at_ns=B0_VALIDATOR_RUN_NS,
        non_claims=MANDATORY_VALIDATOR_SUITE_NON_CLAIMS,
    )


def _validator_results_from_summary(summary: Mapping[str, Any]) -> tuple[ValidatorResult, ...]:
    return tuple(_validator_result_from_mapping(result) for result in summary.get("validator_results", []))


def _validator_result_from_mapping(value: Mapping[str, Any]) -> ValidatorResult:
    return ValidatorResult(
        validator_id=str(value.get("validator_id", "")),
        result=ValidatorStatus(str(value.get("result", ValidatorStatus.REJECT.value))),
        reason_code=str(value.get("reason_code", "")),
        reason_detail_bounded=str(value.get("reason_detail_bounded", ""))[:512],
        field_refs=tuple(str(item) for item in value.get("field_refs", [])),
        validator_version=str(value.get("validator_version", "")),
        artifact_ref=str(value.get("artifact_ref", "")),
        artifact_schema_version=str(value.get("artifact_schema_version", "")),
        run_id=str(value.get("run_id", B0_VALIDATOR_RUN_ID)),
        run_started_at_ns=int(value.get("run_started_at_ns", B0_VALIDATOR_RUN_NS)),
        run_completed_at_ns=int(value.get("run_completed_at_ns", B0_VALIDATOR_RUN_NS)),
        input_refs=tuple(str(item) for item in value.get("input_refs", [])),
        lineage_digest_checked=value.get("lineage_digest_checked") if isinstance(value.get("lineage_digest_checked"), str) else None,
        non_claims_checked=tuple(str(item) for item in value.get("non_claims_checked", [])),
        refusal_record_ref=value.get("refusal_record_ref") if isinstance(value.get("refusal_record_ref"), str) else None,
        review_route_ref=value.get("review_route_ref") if isinstance(value.get("review_route_ref"), str) else None,
        producer_id=str(value.get("producer_id", B0_VALIDATOR_PRODUCER_ID)),
        non_claims=tuple(str(item) for item in value.get("non_claims", B0_VALIDATOR_NON_CLAIMS)),
    )


def _suite_result(
    status: ValidatorStatus, validator_id: str, reason_code: str, detail: str = "", fields: tuple[str, ...] = ()
) -> ValidatorResult:
    return ValidatorResult(
        validator_id=validator_id,
        result=status,
        reason_code=reason_code,
        reason_detail_bounded=detail,
        field_refs=fields,
        artifact_ref=VALIDATOR_SUITE_ARTIFACT_REF,
        artifact_schema_version=VALIDATOR_SUITE_SCHEMA_VERSION,
        input_refs=(VALIDATOR_SUITE_ARTIFACT_REF,),
        non_claims_checked=MANDATORY_VALIDATOR_SUITE_NON_CLAIMS,
        non_claims=B0_VALIDATOR_NON_CLAIMS,
    )


def _primary_result(results: tuple[ValidatorResult, ...]) -> ValidatorResult | None:
    if not results:
        return None
    order = {
        ValidatorStatus.REJECT: 3,
        ValidatorStatus.HOLD_REVIEW: 2,
        ValidatorStatus.NEUTRALIZE: 1,
        ValidatorStatus.ACCEPT: 0,
    }
    return max(results, key=lambda result: order[result.result])


def _primary_refusal_family(result: ValidatorResult | None) -> PrimaryRefusalFamily:
    if result is None:
        return PrimaryRefusalFamily.UNKNOWN
    text = f"{result.validator_id}:{result.reason_code}:{','.join(result.field_refs)}".lower()
    if "non_claim" in text:
        return PrimaryRefusalFamily.MISSING_NON_CLAIMS
    if "secret" in text or "credential" in text:
        return PrimaryRefusalFamily.CREDENTIAL_LEAK
    if "model_output" in text or "llm" in text:
        return PrimaryRefusalFamily.RAW_LLM_OUTPUT_DENIAL
    if "raw_text" in text or "document_text" in text or "source_text" in text or "full_text" in text:
        return PrimaryRefusalFamily.RAW_TEXT_DENIAL
    if "future_outcome" in text:
        return PrimaryRefusalFamily.FUTURE_OUTCOME
    if "order_intent" in text:
        return PrimaryRefusalFamily.ORDER_INTENT
    if "position_target" in text:
        return PrimaryRefusalFamily.POSITION_TARGET
    if "trade" in text or "broker" in text or "execution" in text or "forbidden_boundary" in text:
        return PrimaryRefusalFamily.TRADE_FIELD
    if "source_license" in text or "license_manifest_ref" in text or "source_id_mismatch" in text:
        return PrimaryRefusalFamily.SOURCE_LICENSE_MISMATCH
    if "source_manifest_ref" in text or "source_span" in text:
        return PrimaryRefusalFamily.SOURCE_MISSING
    if "license_manifest_ref" in text or "license_state" in text:
        return PrimaryRefusalFamily.LICENSE_MISSING
    if "rights_scope" in text:
        return PrimaryRefusalFamily.RIGHTS_SCOPE_INVALID
    if "raw_storage" in text or "retention_policy" in text:
        return PrimaryRefusalFamily.STORAGE_POLICY_INVALID
    if "available_from" in text or "asof" in text or "source_cutoff" in text:
        return PrimaryRefusalFamily.AS_OF_VIOLATION
    if "timestamp" in text or "_ns" in text:
        return PrimaryRefusalFamily.TIMESTAMP_INVALID
    if "lineage" in text:
        return PrimaryRefusalFamily.LINEAGE_MISMATCH
    if "prompt_injection" in text:
        return PrimaryRefusalFamily.PROMPT_INJECTION
    if "schema" in text or "required_field" in text or "field_type" in text or "enum" in text:
        return PrimaryRefusalFamily.SCHEMA_INVALID
    return PrimaryRefusalFamily.UNKNOWN


def _review_status_for_aggregate(aggregate: ValidatorStatus) -> ReviewStatus:
    if aggregate == ValidatorStatus.REJECT:
        return ReviewStatus.REJECTED_FINAL
    if aggregate == ValidatorStatus.HOLD_REVIEW:
        return ReviewStatus.HOLD_REVIEW
    if aggregate == ValidatorStatus.NEUTRALIZE:
        return ReviewStatus.NEUTRALIZED_FINAL
    return ReviewStatus.NOT_REQUIRED


def _input_artifact_refs(packet: Mapping[str, Any]) -> tuple[str, ...]:
    refs = _refs_for_suffix(packet, "source_manifest", "source_manifest_id")
    refs += _refs_for_suffix(packet, "license_manifest", "license_manifest_id")
    refs += _refs_for_suffix(packet, "raw_evidence_vault_manifest", "vault_manifest_id")
    refs += _refs_for_suffix(packet, "raw_evidence_record", "evidence_id")
    refs += _refs_for_suffix(packet, "source_document_index", "source_document_id")
    refs += _refs_for_suffix(packet, "atomic_claim_ledger", "claim_ledger_id")
    refs += _refs_for_suffix(packet, "atomic_claim", "claim_id")
    refs += _refs_for_suffix(packet, "financial_event_table", "event_table_id")
    refs += _refs_for_suffix(packet, "financial_event", "event_id")
    return refs or (VALIDATOR_SUITE_ARTIFACT_REF,)


def _refs_for_suffix(packet: Mapping[str, Any] | None, object_key: str, id_key: str) -> tuple[str, ...]:
    if not isinstance(packet, Mapping):
        return ()
    value = packet.get(object_key)
    if not isinstance(value, Mapping):
        return ()
    ref = value.get(id_key)
    return (ref,) if isinstance(ref, str) and ref.strip() else ()


def _timestamp_refs(field_refs: tuple[str, ...]) -> tuple[str, ...]:
    return tuple(ref for ref in field_refs if "timestamp" in ref or ref.endswith("_ns") or "source_cutoff" in ref)


def _first_lineage_digest(value: object) -> str | None:
    if isinstance(value, Mapping):
        raw = value.get("lineage_digest")
        if isinstance(raw, str) and raw.strip():
            return raw
        for nested in value.values():
            found = _first_lineage_digest(nested)
            if found:
                return found
    if isinstance(value, list):
        for nested in value:
            found = _first_lineage_digest(nested)
            if found:
                return found
    return None


def _unique(values: Any) -> tuple[str, ...]:
    items: list[str] = []
    for value in values:
        text = str(value)
        if text and text not in items:
            items.append(text)
    return tuple(items)


def _bounded_component_summaries(component_summaries: list[dict[str, Any]]) -> list[dict[str, object]]:
    bounded: list[dict[str, object]] = []
    for summary in component_summaries:
        bounded.append(
            {
                "validator_summary_id": summary.get("validator_summary_id"),
                "aggregate_result": summary.get("aggregate_result"),
                "accepted_count": summary.get("accepted_count"),
                "rejected_count": summary.get("rejected_count"),
                "hold_review_count": summary.get("hold_review_count"),
                "neutralized_count": summary.get("neutralized_count"),
                "validator_result_refs": summary.get("validator_result_refs", []),
            }
        )
    return bounded


__all__ = [
    "build_refusal_record_from_results",
    "validate_fixture_suite_packet",
    "validate_fixture_suite_packet_file",
]
