from __future__ import annotations

import json
import re
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from flwc.schemas.claim_event import (
    ClaimExtractionMethod,
    ClaimStatus,
    ClaimType,
    EventDerivationMethod,
    FLWCAtomicClaimLedgerV1,
    FLWCAtomicClaimV1,
    FLWCFinancialEventTableV1,
    FLWCFinancialEventV1,
    FinancialEventStatus,
    FinancialEventType,
    MANDATORY_CLAIM_EVENT_NON_CLAIMS,
)
from flwc.schemas.common import (
    B0_VALIDATOR_NON_CLAIMS,
    SchemaIssue,
    ValidatorResult,
    ValidatorStatus,
    ValidatorSummary,
    ensure_strings,
)
from flwc.schemas.raw_evidence import FLWCRawEvidenceRecordV1, FLWCRawEvidenceVaultManifestV1, FLWCSourceDocumentIndexV1
from flwc.schemas.source_license import (
    FLWCLicenseManifestV1,
    FLWCSourceManifestV1,
    LicenseState,
    RawStoragePolicy,
    RightsScope,
    SourceTrustTier,
)
from flwc.validators.core import contains_secret_like_value
from flwc.validators.raw_evidence import validate_raw_evidence_index_pair


SCHEMA_REASON_PRIORITY = (
    "artifact_not_mapping",
    "schema_version_invalid",
    "required_field_missing",
    "field_type_invalid",
    "enum_value_invalid",
    "required_list_empty",
    "required_map_empty",
)
INLINE_RAW_TEXT_PAYLOAD_KEYS = frozenset(
    {
        "article_text",
        "document_text",
        "full_rag_context",
        "full_text",
        "llm_output",
        "model_output",
        "model_raw_output",
        "rag_context",
        "raw_model_output",
        "raw_llm_output",
        "raw_payload",
        "raw_text",
        "source_text",
    }
)
FUTURE_OUTCOME_KEYS = frozenset(
    {
        "future_outcome",
        "future_price",
        "future_return",
        "future_revenue",
        "future_eps",
        "price_target_future",
        "outcome_forecast_authority",
    }
)
TRADE_FIELD_KEYS = frozenset(
    {
        "buy_sell_signal",
        "market_signal",
        "scanner_signal",
        "trade_recommendation",
        "trade_signal",
        "trading_signal",
    }
)
ORDER_INTENT_KEYS = frozenset(
    {
        "order",
        "order_intent",
        "order_side",
        "order_type",
        "routing_instruction",
    }
)
POSITION_TARGET_KEYS = frozenset(
    {
        "position_size",
        "position_sizing",
        "position_target",
        "target_position",
        "target_weight",
    }
)
BROKER_EXECUTION_KEYS = frozenset(
    {
        "broker",
        "broker_execution",
        "broker_route",
        "execution_instruction",
        "execution_trigger",
    }
)
AUTHORITY_BOUNDARY_KEYS = frozenset(
    {
        "calibrated_probability",
        "confidence_score_as_truth_authority",
        "confidence_score_as_trade_signal",
        "duckdb_seed",
        "external_consumer_adapter",
        "market_data_authority",
        "model_extraction",
        "model_output_truth_authority",
        "production_payload",
        "runtime_payload",
        "runtime_service",
        "source_adapter",
        "source_ingestion",
        "truth_authority",
        "vendor_adapter",
        "wiki_export",
    }
)
PROMPT_INJECTION_KEYS = frozenset(
    {
        "prompt_injection_suspected",
        "source_instruction_executed",
        "system_prompt_override",
    }
)
SEGMENT_REF_RE = re.compile(r"^(?P<doc>.+)#segment:(?P<segment>\d{6,})$")
SPAN_REF_RE = re.compile(r"^(?P<doc>.+)#span:(?P<start>\d{6,})-(?P<end>\d{6,})$")


def validate_atomic_claim_ledger(atomic_claim_ledger: Mapping[str, Any]) -> dict[str, Any]:
    ledger, ledger_issues = FLWCAtomicClaimLedgerV1.from_mapping(atomic_claim_ledger)
    results: list[ValidatorResult] = []

    _append_schema_result(results, atomic_claim_ledger, ledger_issues, "atomic_claim_schema_validator")
    _append_ledger_ref_result(results, atomic_claim_ledger, ledger)
    _append_ledger_timestamp_result(results, atomic_claim_ledger, ledger)
    _append_lineage_digest_result(results, atomic_claim_ledger, "lineage_digest")
    _append_boundary_denial_results(results, atomic_claim_ledger)
    _append_credential_leak_result(results, atomic_claim_ledger)
    _append_non_claims_result(results, atomic_claim_ledger)
    _append_ledger_synthetic_fixture_scope_result(results, atomic_claim_ledger, ledger)

    return _summary(atomic_claim_ledger, results, "atomic_claim_ledger")


def validate_atomic_claim(atomic_claim: Mapping[str, Any]) -> dict[str, Any]:
    claim, claim_issues = FLWCAtomicClaimV1.from_mapping(atomic_claim)
    results: list[ValidatorResult] = []

    _append_schema_result(results, atomic_claim, claim_issues, "atomic_claim_schema_validator")
    _append_claim_ref_result(results, atomic_claim, claim)
    _append_claim_carry_forward_result(results, atomic_claim, claim)
    _append_claim_timestamp_result(results, atomic_claim, claim)
    _append_claim_source_span_ref_result(results, atomic_claim, claim)
    _append_lineage_digest_result(results, atomic_claim, "lineage_digest")
    _append_prompt_injection_result(results, atomic_claim)
    _append_boundary_denial_results(results, atomic_claim)
    _append_credential_leak_result(results, atomic_claim)
    _append_non_claims_result(results, atomic_claim)
    _append_claim_synthetic_fixture_scope_result(results, atomic_claim, claim)

    return _summary(atomic_claim, results, "atomic_claim")


def validate_financial_event_table(financial_event_table: Mapping[str, Any]) -> dict[str, Any]:
    event_table, event_table_issues = FLWCFinancialEventTableV1.from_mapping(financial_event_table)
    results: list[ValidatorResult] = []

    _append_schema_result(results, financial_event_table, event_table_issues, "financial_event_schema_validator")
    _append_event_table_ref_result(results, financial_event_table, event_table)
    _append_event_table_timestamp_result(results, financial_event_table, event_table)
    _append_lineage_digest_result(results, financial_event_table, "lineage_digest")
    _append_boundary_denial_results(results, financial_event_table)
    _append_credential_leak_result(results, financial_event_table)
    _append_non_claims_result(results, financial_event_table)
    _append_event_table_synthetic_fixture_scope_result(results, financial_event_table, event_table)

    return _summary(financial_event_table, results, "financial_event_table")


def validate_financial_event(financial_event: Mapping[str, Any]) -> dict[str, Any]:
    event, event_issues = FLWCFinancialEventV1.from_mapping(financial_event)
    results: list[ValidatorResult] = []

    _append_schema_result(results, financial_event, event_issues, "financial_event_schema_validator")
    _append_event_ref_result(results, financial_event, event)
    _append_event_carry_forward_result(results, financial_event, event)
    _append_event_timestamp_result(results, financial_event, event)
    _append_lineage_digest_result(results, financial_event, "lineage_digest")
    _append_event_entity_asset_placeholder_result(results, financial_event, event)
    _append_prompt_injection_result(results, financial_event)
    _append_boundary_denial_results(results, financial_event)
    _append_credential_leak_result(results, financial_event)
    _append_non_claims_result(results, financial_event)
    _append_event_synthetic_fixture_scope_result(results, financial_event, event)

    return _summary(financial_event, results, "financial_event")


def validate_claim_event_pair(atomic_claim: Mapping[str, Any], financial_event: Mapping[str, Any]) -> dict[str, Any]:
    claim, claim_issues = FLWCAtomicClaimV1.from_mapping(atomic_claim)
    event, event_issues = FLWCFinancialEventV1.from_mapping(financial_event)
    artifact = {"atomic_claim": atomic_claim, "financial_event": financial_event}
    results: list[ValidatorResult] = []

    _append_schema_result(results, artifact, claim_issues, "atomic_claim_schema_validator", artifact_schema_version="FLWCAtomicClaimV1")
    _append_schema_result(
        results, artifact, event_issues, "financial_event_schema_validator", artifact_schema_version="FLWCFinancialEventV1"
    )
    _append_claim_event_pair_ref_result(results, artifact, claim, event)
    _append_claim_event_pair_carry_forward_result(results, artifact, claim, event)
    _append_claim_event_pair_timestamp_result(results, artifact, claim, event)
    _append_claim_event_pair_lineage_result(results, artifact, claim, event)
    _append_boundary_denial_results(results, artifact)
    _append_credential_leak_result(results, artifact)
    _append_pair_non_claims_result(results, artifact, ("atomic_claim", "financial_event"))
    _append_claim_event_pair_synthetic_scope_result(results, artifact, claim, event)

    return _summary(artifact, results, "claim_event_pair")


def validate_claim_event_compiler_output(
    atomic_claim_ledger: Mapping[str, Any],
    atomic_claim: Mapping[str, Any],
    financial_event_table: Mapping[str, Any],
    financial_event: Mapping[str, Any],
    raw_evidence_vault_manifest: Mapping[str, Any],
    raw_evidence_record: Mapping[str, Any],
    source_document_index: Mapping[str, Any],
    source_manifest: Mapping[str, Any],
    license_manifest: Mapping[str, Any],
) -> dict[str, Any]:
    ledger, ledger_issues = FLWCAtomicClaimLedgerV1.from_mapping(atomic_claim_ledger)
    claim, claim_issues = FLWCAtomicClaimV1.from_mapping(atomic_claim)
    event_table, event_table_issues = FLWCFinancialEventTableV1.from_mapping(financial_event_table)
    event, event_issues = FLWCFinancialEventV1.from_mapping(financial_event)
    vault, vault_issues = FLWCRawEvidenceVaultManifestV1.from_mapping(raw_evidence_vault_manifest)
    record, record_issues = FLWCRawEvidenceRecordV1.from_mapping(raw_evidence_record)
    index, index_issues = FLWCSourceDocumentIndexV1.from_mapping(source_document_index)
    source, source_issues = FLWCSourceManifestV1.from_mapping(source_manifest)
    license_, license_issues = FLWCLicenseManifestV1.from_mapping(license_manifest)
    artifact = {
        "atomic_claim_ledger": atomic_claim_ledger,
        "atomic_claim": atomic_claim,
        "financial_event_table": financial_event_table,
        "financial_event": financial_event,
        "raw_evidence_vault_manifest": raw_evidence_vault_manifest,
        "raw_evidence_record": raw_evidence_record,
        "source_document_index": source_document_index,
        "source_manifest": source_manifest,
        "license_manifest": license_manifest,
    }
    results: list[ValidatorResult] = []

    _append_schema_result(
        results, artifact, ledger_issues, "atomic_claim_ledger_schema_validator", artifact_schema_version="FLWCAtomicClaimLedgerV1"
    )
    _append_schema_result(results, artifact, claim_issues, "atomic_claim_schema_validator", artifact_schema_version="FLWCAtomicClaimV1")
    _append_schema_result(
        results,
        artifact,
        event_table_issues,
        "financial_event_table_schema_validator",
        artifact_schema_version="FLWCFinancialEventTableV1",
    )
    _append_schema_result(
        results, artifact, event_issues, "financial_event_schema_validator", artifact_schema_version="FLWCFinancialEventV1"
    )
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
        results, artifact, source_issues, "source_manifest_schema_validator", artifact_schema_version="FLWCSourceManifestV1"
    )
    _append_schema_result(
        results, artifact, license_issues, "license_manifest_schema_validator", artifact_schema_version="FLWCLicenseManifestV1"
    )
    _append_raw_evidence_pair_validation_result(
        results, artifact, raw_evidence_vault_manifest, raw_evidence_record, source_document_index, source_manifest, license_manifest
    )
    _append_compiler_output_ref_result(results, artifact, ledger, claim, event_table, event, vault, record, index, source, license_)
    _append_compiler_output_carry_forward_result(results, artifact, claim, event, record, index, source, license_)
    _append_compiler_output_timestamp_result(results, artifact, ledger, claim, event_table, event, record, index)
    _append_compiler_output_source_span_result(results, artifact, claim, index)
    _append_compiler_output_lineage_result(results, artifact, ledger, claim, event_table, event)
    _append_compiler_output_prompt_injection_result(results, artifact, record, index)
    _append_boundary_denial_results(results, artifact)
    _append_credential_leak_result(results, artifact)
    _append_pair_non_claims_result(results, artifact, ("atomic_claim_ledger", "atomic_claim", "financial_event_table", "financial_event"))
    _append_compiler_output_synthetic_scope_result(results, artifact, ledger, claim, event_table, event)

    return _summary(artifact, results, "claim_event_compiler_output")


def validate_atomic_claim_file(path: str | Path) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as fh:
        return validate_atomic_claim(json.load(fh))


def validate_atomic_claim_ledger_file(path: str | Path) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as fh:
        return validate_atomic_claim_ledger(json.load(fh))


def validate_financial_event_file(path: str | Path) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as fh:
        return validate_financial_event(json.load(fh))


def validate_financial_event_table_file(path: str | Path) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as fh:
        return validate_financial_event_table(json.load(fh))


def validate_claim_event_pair_file(path: str | Path) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as fh:
        fixture = json.load(fh)
    return validate_claim_event_pair(fixture["atomic_claim"], fixture["financial_event"])


def validate_claim_event_compiler_output_file(path: str | Path) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as fh:
        fixture = json.load(fh)
    return validate_claim_event_compiler_output(
        fixture["atomic_claim_ledger"],
        fixture["atomic_claim"],
        fixture["financial_event_table"],
        fixture["financial_event"],
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


def _append_ledger_ref_result(
    results: list[ValidatorResult], artifact: Mapping[str, Any], ledger: FLWCAtomicClaimLedgerV1 | None
) -> None:
    if ledger is None:
        results.append(_reject(artifact, "source_manifest_ref_validator", "atomic_claim_ledger_invalid"))
        return
    if not ledger.input_evidence_refs:
        results.append(_reject(artifact, "claim_event_ref_validator", "input_evidence_refs_missing", fields=("input_evidence_refs",)))
        return
    results.append(_accept(artifact, "claim_event_ref_validator"))
    results.append(_accept(artifact, "source_manifest_ref_validator"))
    results.append(_accept(artifact, "license_manifest_ref_validator"))


def _append_claim_ref_result(results: list[ValidatorResult], artifact: Mapping[str, Any], claim: FLWCAtomicClaimV1 | None) -> None:
    if claim is None:
        results.append(_reject(artifact, "source_manifest_ref_validator", "atomic_claim_invalid"))
        return
    results.append(_accept(artifact, "source_manifest_ref_validator"))
    results.append(_accept(artifact, "license_manifest_ref_validator"))
    results.append(_accept(artifact, "claim_event_ref_validator"))


def _append_event_table_ref_result(
    results: list[ValidatorResult], artifact: Mapping[str, Any], event_table: FLWCFinancialEventTableV1 | None
) -> None:
    if event_table is None:
        results.append(_reject(artifact, "claim_event_ref_validator", "financial_event_table_invalid"))
        return
    results.append(_accept(artifact, "claim_event_ref_validator"))
    results.append(_accept(artifact, "source_manifest_ref_validator"))
    results.append(_accept(artifact, "license_manifest_ref_validator"))


def _append_event_ref_result(results: list[ValidatorResult], artifact: Mapping[str, Any], event: FLWCFinancialEventV1 | None) -> None:
    if event is None:
        results.append(_reject(artifact, "claim_event_ref_validator", "financial_event_invalid"))
        return
    results.append(_accept(artifact, "claim_event_ref_validator"))
    results.append(_accept(artifact, "source_manifest_ref_validator"))
    results.append(_accept(artifact, "license_manifest_ref_validator"))


def _append_claim_carry_forward_result(
    results: list[ValidatorResult], artifact: Mapping[str, Any], claim: FLWCAtomicClaimV1 | None
) -> None:
    if claim is None:
        results.append(_reject(artifact, "raw_storage_policy_validator", "atomic_claim_invalid"))
        return
    fields: list[str] = []
    if claim.prompt_injection_flags:
        fields.append("prompt_injection_flags")
    if fields:
        field_refs = tuple(fields)
        results.append(_reject(artifact, "prompt_injection_flag_validator", "prompt_injection_quarantine_missing", ",".join(field_refs), field_refs))
        return
    results.append(_accept(artifact, "raw_storage_policy_validator"))
    results.append(_accept(artifact, "retention_policy_validator"))


def _append_event_carry_forward_result(
    results: list[ValidatorResult], artifact: Mapping[str, Any], event: FLWCFinancialEventV1 | None
) -> None:
    if event is None:
        results.append(_reject(artifact, "raw_storage_policy_validator", "financial_event_invalid"))
        return
    fields: list[str] = []
    if event.prompt_injection_flags:
        fields.append("prompt_injection_flags")
    if fields:
        field_refs = tuple(fields)
        results.append(_reject(artifact, "prompt_injection_flag_validator", "prompt_injection_quarantine_missing", ",".join(field_refs), field_refs))
        return
    results.append(_accept(artifact, "raw_storage_policy_validator"))
    results.append(_accept(artifact, "retention_policy_validator"))


def _append_ledger_timestamp_result(
    results: list[ValidatorResult], artifact: Mapping[str, Any], ledger: FLWCAtomicClaimLedgerV1 | None
) -> None:
    if ledger is None:
        results.append(_reject(artifact, "timestamp_validator", "atomic_claim_ledger_invalid"))
        return
    results.append(_accept(artifact, "timestamp_validator"))
    results.append(_accept(artifact, "available_from_asof_validator"))


def _append_claim_timestamp_result(results: list[ValidatorResult], artifact: Mapping[str, Any], claim: FLWCAtomicClaimV1 | None) -> None:
    if claim is None:
        results.append(_reject(artifact, "timestamp_validator", "atomic_claim_invalid"))
        return
    if claim.source_timestamp_ns is None:
        results.append(_reject(artifact, "timestamp_validator", "source_timestamp_missing", fields=("source_timestamp_ns",)))
        return
    if claim.available_from_ns > claim.compiler_seen_at_ns:
        results.append(
            _reject(
                artifact,
                "available_from_asof_validator",
                "available_from_after_compiler_seen",
                fields=("available_from_ns", "compiler_seen_at_ns"),
            )
        )
        return
    results.append(_accept(artifact, "timestamp_validator"))
    results.append(_accept(artifact, "available_from_asof_validator"))


def _append_event_table_timestamp_result(
    results: list[ValidatorResult], artifact: Mapping[str, Any], event_table: FLWCFinancialEventTableV1 | None
) -> None:
    if event_table is None:
        results.append(_reject(artifact, "timestamp_validator", "financial_event_table_invalid"))
        return
    results.append(_accept(artifact, "timestamp_validator"))
    results.append(_accept(artifact, "available_from_asof_validator"))


def _append_event_timestamp_result(results: list[ValidatorResult], artifact: Mapping[str, Any], event: FLWCFinancialEventV1 | None) -> None:
    if event is None:
        results.append(_reject(artifact, "timestamp_validator", "financial_event_invalid"))
        return
    if event.source_timestamp_ns is None:
        results.append(_reject(artifact, "timestamp_validator", "source_timestamp_missing", fields=("source_timestamp_ns",)))
        return
    if event.available_from_ns > event.compiler_seen_at_ns:
        results.append(
            _reject(
                artifact,
                "available_from_asof_validator",
                "available_from_after_compiler_seen",
                fields=("available_from_ns", "compiler_seen_at_ns"),
            )
        )
        return
    if event.event_time_ns is not None and event.event_time_ns > event.compiler_seen_at_ns:
        results.append(_reject(artifact, "no_future_outcome_validator", "future_outcome_field_present", fields=("event_time_ns",)))
        return
    results.append(_accept(artifact, "timestamp_validator"))
    results.append(_accept(artifact, "available_from_asof_validator"))


def _append_claim_source_span_ref_result(
    results: list[ValidatorResult], artifact: Mapping[str, Any], claim: FLWCAtomicClaimV1 | None
) -> None:
    if claim is None:
        results.append(_reject(artifact, "source_span_ref_validator", "atomic_claim_invalid", fields=("source_span_refs",)))
        return
    invalid = tuple(ref for ref in claim.source_span_refs if _parse_span_ref(ref, claim.source_document_id) is None)
    if invalid:
        results.append(_reject(artifact, "source_span_ref_validator", "source_span_ref_invalid", ",".join(invalid), ("source_span_refs",)))
        return
    results.append(_accept(artifact, "source_span_ref_validator"))


def _append_lineage_digest_result(results: list[ValidatorResult], artifact: Mapping[str, Any], field_name: str) -> None:
    if not _is_non_empty_string(artifact.get(field_name)):
        results.append(_reject(artifact, "lineage_digest_validator", "lineage_digest_missing", fields=(field_name,)))
        return
    results.append(_accept(artifact, "lineage_digest_validator"))


def _append_event_entity_asset_placeholder_result(
    results: list[ValidatorResult], artifact: Mapping[str, Any], event: FLWCFinancialEventV1 | None
) -> None:
    if event is None:
        results.append(_reject(artifact, "entity_asset_link_validator", "financial_event_invalid", fields=("asset_refs",)))
        return
    if event.event_type == FinancialEventType.RUMOR_OR_UNVERIFIED_EVENT and event.status != FinancialEventStatus.HOLD_REVIEW:
        results.append(_hold(artifact, "entity_asset_link_validator", "rumor_event_requires_review", fields=("event_type", "status")))
        return
    results.append(_accept(artifact, "entity_asset_link_validator"))


def _append_prompt_injection_result(results: list[ValidatorResult], artifact: Mapping[str, Any]) -> None:
    fields = tuple(_find_keys(artifact, PROMPT_INJECTION_KEYS) + _find_nonempty_prompt_injection_flag_fields(artifact))
    if fields:
        results.append(
            _reject(
                artifact,
                "prompt_injection_flag_validator",
                "prompt_injection_quarantine_missing",
                ",".join(fields),
                fields,
            )
        )
        return
    results.append(_accept(artifact, "prompt_injection_flag_validator"))


def _append_boundary_denial_results(results: list[ValidatorResult], artifact: Mapping[str, Any]) -> None:
    _append_key_denial_result(
        results,
        artifact,
        "raw_text_payload_denial_validator",
        "raw_text_payload_field_present",
        INLINE_RAW_TEXT_PAYLOAD_KEYS,
    )
    _append_key_denial_result(
        results,
        artifact,
        "no_future_outcome_validator",
        "future_outcome_field_present",
        FUTURE_OUTCOME_KEYS,
    )
    _append_key_denial_result(results, artifact, "no_trade_field_validator", "trade_signal_field_present", TRADE_FIELD_KEYS)
    _append_key_denial_result(results, artifact, "no_order_intent_validator", "order_intent_field_present", ORDER_INTENT_KEYS)
    _append_key_denial_result(
        results,
        artifact,
        "no_position_target_validator",
        "position_target_field_present",
        POSITION_TARGET_KEYS,
    )
    _append_key_denial_result(
        results,
        artifact,
        "broker_execution_field_denial_validator",
        "broker_execution_field_present",
        BROKER_EXECUTION_KEYS,
    )
    _append_key_denial_result(
        results,
        artifact,
        "no_trade_field_validator",
        "forbidden_boundary_field_present",
        AUTHORITY_BOUNDARY_KEYS,
    )


def _append_key_denial_result(
    results: list[ValidatorResult],
    artifact: Mapping[str, Any],
    validator_id: str,
    reason_code: str,
    forbidden_keys: frozenset[str],
) -> None:
    fields = tuple(_find_keys(artifact, forbidden_keys))
    if fields:
        results.append(_reject(artifact, validator_id, reason_code, ",".join(fields), fields))
        return
    results.append(_accept(artifact, validator_id))


def _append_credential_leak_result(results: list[ValidatorResult], artifact: Mapping[str, Any]) -> None:
    if contains_secret_like_value(artifact):
        results.append(_reject(artifact, "credential_leak_validator", "secret_like_value_detected"))
        return
    results.append(_accept(artifact, "credential_leak_validator"))


def _append_non_claims_result(results: list[ValidatorResult], artifact: Mapping[str, Any]) -> None:
    claims = set(ensure_strings(artifact.get("non_claims", [])))
    missing = tuple(sorted(set(MANDATORY_CLAIM_EVENT_NON_CLAIMS) - claims))
    if missing:
        results.append(_reject(artifact, "non_claims_validator", "missing_mandatory_non_claims", ",".join(missing), ("non_claims",)))
        return
    results.append(_accept(artifact, "non_claims_validator"))


def _append_ledger_synthetic_fixture_scope_result(
    results: list[ValidatorResult], artifact: Mapping[str, Any], ledger: FLWCAtomicClaimLedgerV1 | None
) -> None:
    if ledger is None:
        results.append(_reject(artifact, "synthetic_fixture_scope_validator", "atomic_claim_ledger_invalid"))
        return
    fields: list[str] = []
    if ledger.validation_status != ValidatorStatus.ACCEPT:
        fields.append("validation_status")
    if ledger.claim_count != 1:
        fields.append("claim_count")
    if fields:
        results.append(_reject(artifact, "synthetic_fixture_scope_validator", "synthetic_fixture_scope_invalid", ",".join(fields), tuple(fields)))
        return
    results.append(_accept(artifact, "synthetic_fixture_scope_validator"))


def _append_claim_synthetic_fixture_scope_result(
    results: list[ValidatorResult], artifact: Mapping[str, Any], claim: FLWCAtomicClaimV1 | None
) -> None:
    if claim is None:
        results.append(_reject(artifact, "synthetic_fixture_scope_validator", "atomic_claim_invalid"))
        return
    fields: list[str] = []
    if claim.extraction_method != ClaimExtractionMethod.MANUAL_FIXTURE:
        fields.append("extraction_method")
    if claim.model_ref is not None:
        fields.append("model_ref")
    if claim.prompt_template_ref is not None:
        fields.append("prompt_template_ref")
    if claim.status != ClaimStatus.PROPOSED:
        fields.append("status")
    if claim.validation_status != ValidatorStatus.ACCEPT:
        fields.append("validation_status")
    if claim.license_state != LicenseState.ALLOWED_FULL_TEXT:
        fields.append("license_state")
    if claim.rights_scope != RightsScope.RESEARCH_INTERNAL_ONLY:
        fields.append("rights_scope")
    if claim.raw_storage_policy != RawStoragePolicy.ALLOWED_FULL_TEXT:
        fields.append("raw_storage_policy")
    if claim.retention_policy != "synthetic_fixture_retention_internal_only":
        fields.append("retention_policy")
    if claim.source_trust_tier != SourceTrustTier.TIER_4_MANUAL_REVIEW_ONLY:
        fields.append("source_trust_tier")
    if claim.prompt_injection_flags:
        fields.append("prompt_injection_flags")
    if fields:
        results.append(_reject(artifact, "synthetic_fixture_scope_validator", "synthetic_fixture_scope_invalid", ",".join(fields), tuple(fields)))
        return
    results.append(_accept(artifact, "synthetic_fixture_scope_validator"))


def _append_event_table_synthetic_fixture_scope_result(
    results: list[ValidatorResult], artifact: Mapping[str, Any], event_table: FLWCFinancialEventTableV1 | None
) -> None:
    if event_table is None:
        results.append(_reject(artifact, "synthetic_fixture_scope_validator", "financial_event_table_invalid"))
        return
    fields: list[str] = []
    if event_table.validation_status != ValidatorStatus.ACCEPT:
        fields.append("validation_status")
    if event_table.event_count != 1:
        fields.append("event_count")
    if fields:
        results.append(_reject(artifact, "synthetic_fixture_scope_validator", "synthetic_fixture_scope_invalid", ",".join(fields), tuple(fields)))
        return
    results.append(_accept(artifact, "synthetic_fixture_scope_validator"))


def _append_event_synthetic_fixture_scope_result(
    results: list[ValidatorResult], artifact: Mapping[str, Any], event: FLWCFinancialEventV1 | None
) -> None:
    if event is None:
        results.append(_reject(artifact, "synthetic_fixture_scope_validator", "financial_event_invalid"))
        return
    fields: list[str] = []
    if event.event_derivation_method != EventDerivationMethod.CLAIM_SET_COMPILER:
        fields.append("event_derivation_method")
    if event.status != FinancialEventStatus.PROPOSED:
        fields.append("status")
    if event.validation_status != ValidatorStatus.ACCEPT:
        fields.append("validation_status")
    if event.event_type == FinancialEventType.RUMOR_OR_UNVERIFIED_EVENT:
        fields.append("event_type")
    if event.raw_storage_policy != RawStoragePolicy.ALLOWED_FULL_TEXT:
        fields.append("raw_storage_policy")
    if event.retention_policy != "synthetic_fixture_retention_internal_only":
        fields.append("retention_policy")
    if event.source_trust_tier != SourceTrustTier.TIER_4_MANUAL_REVIEW_ONLY:
        fields.append("source_trust_tier")
    if event.prompt_injection_flags:
        fields.append("prompt_injection_flags")
    if fields:
        results.append(_reject(artifact, "synthetic_fixture_scope_validator", "synthetic_fixture_scope_invalid", ",".join(fields), tuple(fields)))
        return
    results.append(_accept(artifact, "synthetic_fixture_scope_validator"))


def _append_claim_event_pair_ref_result(
    results: list[ValidatorResult],
    artifact: Mapping[str, Any],
    claim: FLWCAtomicClaimV1 | None,
    event: FLWCFinancialEventV1 | None,
) -> None:
    if claim is None or event is None:
        results.append(_reject(artifact, "claim_event_ref_validator", "claim_event_pair_artifact_invalid"))
        return
    fields: list[str] = []
    if claim.claim_id not in event.evidence_claim_refs:
        fields.append("financial_event.evidence_claim_refs")
    if claim.source_document_id not in event.source_document_refs:
        fields.append("financial_event.source_document_refs")
    if not set(claim.raw_evidence_refs).issubset(set(event.raw_evidence_refs)):
        fields.append("financial_event.raw_evidence_refs")
    if claim.source_manifest_ref not in event.source_manifest_refs:
        fields.append("financial_event.source_manifest_refs")
    if claim.license_manifest_ref not in event.license_manifest_refs:
        fields.append("financial_event.license_manifest_refs")
    if fields:
        field_refs = tuple(dict.fromkeys(fields))
        results.append(_reject(artifact, "claim_event_ref_validator", "claim_event_ref_mismatch", ",".join(field_refs), field_refs))
        return
    results.append(_accept(artifact, "claim_event_ref_validator"))
    results.append(_accept(artifact, "source_manifest_ref_validator"))
    results.append(_accept(artifact, "license_manifest_ref_validator"))


def _append_claim_event_pair_carry_forward_result(
    results: list[ValidatorResult],
    artifact: Mapping[str, Any],
    claim: FLWCAtomicClaimV1 | None,
    event: FLWCFinancialEventV1 | None,
) -> None:
    if claim is None or event is None:
        results.append(_reject(artifact, "raw_storage_policy_validator", "claim_event_pair_artifact_invalid"))
        return
    fields: list[str] = []
    if event.raw_storage_policy != claim.raw_storage_policy:
        fields.extend(("atomic_claim.raw_storage_policy", "financial_event.raw_storage_policy"))
    if event.retention_policy != claim.retention_policy:
        fields.extend(("atomic_claim.retention_policy", "financial_event.retention_policy"))
    if event.source_trust_tier != claim.source_trust_tier:
        fields.extend(("atomic_claim.source_trust_tier", "financial_event.source_trust_tier"))
    if event.prompt_injection_flags != claim.prompt_injection_flags:
        fields.extend(("atomic_claim.prompt_injection_flags", "financial_event.prompt_injection_flags"))
    if claim.prompt_injection_flags or event.prompt_injection_flags:
        fields.extend(("atomic_claim.prompt_injection_flags", "financial_event.prompt_injection_flags"))
    if fields:
        field_refs = tuple(dict.fromkeys(fields))
        reason_code = (
            "prompt_injection_quarantine_missing"
            if any(field.endswith("prompt_injection_flags") for field in field_refs)
            else "claim_event_carry_forward_mismatch"
        )
        validator_id = "prompt_injection_flag_validator" if reason_code == "prompt_injection_quarantine_missing" else "raw_storage_policy_validator"
        results.append(_reject(artifact, validator_id, reason_code, ",".join(field_refs), field_refs))
        return
    results.append(_accept(artifact, "raw_storage_policy_validator"))
    results.append(_accept(artifact, "retention_policy_validator"))


def _append_claim_event_pair_timestamp_result(
    results: list[ValidatorResult],
    artifact: Mapping[str, Any],
    claim: FLWCAtomicClaimV1 | None,
    event: FLWCFinancialEventV1 | None,
) -> None:
    if claim is None or event is None:
        results.append(_reject(artifact, "timestamp_validator", "claim_event_pair_artifact_invalid"))
        return
    if claim.source_timestamp_ns is None or event.source_timestamp_ns is None:
        results.append(_reject(artifact, "timestamp_validator", "source_timestamp_missing", fields=("source_timestamp_ns",)))
        return
    if event.available_from_ns < claim.available_from_ns:
        results.append(
            _reject(
                artifact,
                "available_from_asof_validator",
                "event_available_before_claim_available",
                fields=("atomic_claim.available_from_ns", "financial_event.available_from_ns"),
            )
        )
        return
    results.append(_accept(artifact, "timestamp_validator"))
    results.append(_accept(artifact, "available_from_asof_validator"))


def _append_claim_event_pair_lineage_result(
    results: list[ValidatorResult],
    artifact: Mapping[str, Any],
    claim: FLWCAtomicClaimV1 | None,
    event: FLWCFinancialEventV1 | None,
) -> None:
    fields: list[str] = []
    if claim is None or not _is_non_empty_string(claim.lineage_digest):
        fields.append("atomic_claim.lineage_digest")
    if event is None or not _is_non_empty_string(event.lineage_digest):
        fields.append("financial_event.lineage_digest")
    if fields:
        results.append(_reject(artifact, "lineage_digest_validator", "lineage_digest_missing", ",".join(fields), tuple(fields)))
        return
    results.append(_accept(artifact, "lineage_digest_validator"))


def _append_pair_non_claims_result(results: list[ValidatorResult], artifact: Mapping[str, Any], fields_to_check: tuple[str, ...]) -> None:
    fields: list[str] = []
    missing: set[str] = set()
    for field in fields_to_check:
        value = artifact.get(field)
        claims = set(ensure_strings(value.get("non_claims", []) if isinstance(value, Mapping) else []))
        local_missing = set(MANDATORY_CLAIM_EVENT_NON_CLAIMS) - claims
        if local_missing:
            fields.append(f"{field}.non_claims")
            missing |= local_missing
    if fields:
        results.append(_reject(artifact, "non_claims_validator", "missing_mandatory_non_claims", ",".join(sorted(missing)), tuple(fields)))
        return
    results.append(_accept(artifact, "non_claims_validator"))


def _append_claim_event_pair_synthetic_scope_result(
    results: list[ValidatorResult],
    artifact: Mapping[str, Any],
    claim: FLWCAtomicClaimV1 | None,
    event: FLWCFinancialEventV1 | None,
) -> None:
    if claim is None or event is None:
        results.append(_reject(artifact, "synthetic_fixture_scope_validator", "claim_event_pair_artifact_invalid"))
        return
    fields: list[str] = []
    if claim.extraction_method != ClaimExtractionMethod.MANUAL_FIXTURE:
        fields.append("atomic_claim.extraction_method")
    if claim.status != ClaimStatus.PROPOSED:
        fields.append("atomic_claim.status")
    if event.event_derivation_method != EventDerivationMethod.CLAIM_SET_COMPILER:
        fields.append("financial_event.event_derivation_method")
    if event.status != FinancialEventStatus.PROPOSED:
        fields.append("financial_event.status")
    if claim.raw_storage_policy != RawStoragePolicy.ALLOWED_FULL_TEXT:
        fields.append("atomic_claim.raw_storage_policy")
    if event.raw_storage_policy != RawStoragePolicy.ALLOWED_FULL_TEXT:
        fields.append("financial_event.raw_storage_policy")
    if claim.retention_policy != "synthetic_fixture_retention_internal_only":
        fields.append("atomic_claim.retention_policy")
    if event.retention_policy != "synthetic_fixture_retention_internal_only":
        fields.append("financial_event.retention_policy")
    if claim.source_trust_tier != SourceTrustTier.TIER_4_MANUAL_REVIEW_ONLY:
        fields.append("atomic_claim.source_trust_tier")
    if event.source_trust_tier != SourceTrustTier.TIER_4_MANUAL_REVIEW_ONLY:
        fields.append("financial_event.source_trust_tier")
    if claim.prompt_injection_flags:
        fields.append("atomic_claim.prompt_injection_flags")
    if event.prompt_injection_flags:
        fields.append("financial_event.prompt_injection_flags")
    if fields:
        field_refs = tuple(fields)
        results.append(_reject(artifact, "synthetic_fixture_scope_validator", "synthetic_fixture_scope_invalid", ",".join(field_refs), field_refs))
        return
    results.append(_accept(artifact, "synthetic_fixture_scope_validator"))


def _append_raw_evidence_pair_validation_result(
    results: list[ValidatorResult],
    artifact: Mapping[str, Any],
    raw_evidence_vault_manifest: Mapping[str, Any],
    raw_evidence_record: Mapping[str, Any],
    source_document_index: Mapping[str, Any],
    source_manifest: Mapping[str, Any],
    license_manifest: Mapping[str, Any],
) -> None:
    summary = validate_raw_evidence_index_pair(
        raw_evidence_vault_manifest,
        raw_evidence_record,
        source_document_index,
        source_manifest,
        license_manifest,
    )
    aggregate = summary["aggregate_result"]
    if aggregate == ValidatorStatus.ACCEPT.value:
        results.append(_accept(artifact, "source_license_pairing_validator"))
        return
    if aggregate == ValidatorStatus.REJECT.value:
        results.append(_reject(artifact, "source_license_pairing_validator", "raw_evidence_pair_not_accepted", str(aggregate)))
        return
    if aggregate == ValidatorStatus.HOLD_REVIEW.value:
        results.append(_hold(artifact, "source_license_pairing_validator", "raw_evidence_pair_requires_review", str(aggregate)))
        return
    results.append(_neutralize(artifact, "source_license_pairing_validator", "raw_evidence_pair_neutralized", str(aggregate)))


def _append_compiler_output_ref_result(
    results: list[ValidatorResult],
    artifact: Mapping[str, Any],
    ledger: FLWCAtomicClaimLedgerV1 | None,
    claim: FLWCAtomicClaimV1 | None,
    event_table: FLWCFinancialEventTableV1 | None,
    event: FLWCFinancialEventV1 | None,
    vault: FLWCRawEvidenceVaultManifestV1 | None,
    record: FLWCRawEvidenceRecordV1 | None,
    index: FLWCSourceDocumentIndexV1 | None,
    source: FLWCSourceManifestV1 | None,
    license_: FLWCLicenseManifestV1 | None,
) -> None:
    if None in (ledger, claim, event_table, event, vault, record, index, source, license_):
        results.append(_reject(artifact, "claim_event_ref_validator", "claim_event_compiler_artifact_invalid"))
        return
    assert ledger and claim and event_table and event and vault and record and index and source and license_
    fields: list[str] = []
    if record.evidence_id not in ledger.input_evidence_refs:
        fields.append("atomic_claim_ledger.input_evidence_refs")
    if source.source_manifest_id not in ledger.input_source_manifest_refs:
        fields.append("atomic_claim_ledger.input_source_manifest_refs")
    if license_.license_manifest_id not in ledger.input_license_manifest_refs:
        fields.append("atomic_claim_ledger.input_license_manifest_refs")
    if claim.claim_id not in event.evidence_claim_refs:
        fields.append("financial_event.evidence_claim_refs")
    if ledger.claim_ledger_id not in event_table.input_claim_ledger_refs:
        fields.append("financial_event_table.input_claim_ledger_refs")
    if claim.source_document_id != index.source_document_id:
        fields.append("atomic_claim.source_document_id")
    if record.evidence_id not in claim.raw_evidence_refs:
        fields.append("atomic_claim.raw_evidence_refs")
    if claim.source_manifest_ref != source.source_manifest_id:
        fields.append("atomic_claim.source_manifest_ref")
    if claim.license_manifest_ref != license_.license_manifest_id:
        fields.append("atomic_claim.license_manifest_ref")
    if claim.license_state != license_.license_state:
        fields.append("atomic_claim.license_state")
    if claim.rights_scope != license_.rights_scope:
        fields.append("atomic_claim.rights_scope")
    if index.source_document_id not in event.source_document_refs:
        fields.append("financial_event.source_document_refs")
    if record.evidence_id not in event.raw_evidence_refs:
        fields.append("financial_event.raw_evidence_refs")
    if source.source_manifest_id not in event.source_manifest_refs:
        fields.append("financial_event.source_manifest_refs")
    if license_.license_manifest_id not in event.license_manifest_refs:
        fields.append("financial_event.license_manifest_refs")
    if dict(event.license_state_summary).get(license_.license_manifest_id) != license_.license_state.value:
        fields.append("financial_event.license_state_summary")
    if dict(event.rights_scope_summary).get(license_.license_manifest_id) != license_.rights_scope.value:
        fields.append("financial_event.rights_scope_summary")
    if ledger.claim_count != 1:
        fields.append("atomic_claim_ledger.claim_count")
    if event_table.event_count != 1:
        fields.append("financial_event_table.event_count")
    if fields:
        field_refs = tuple(dict.fromkeys(fields))
        results.append(_reject(artifact, "claim_event_ref_validator", "claim_event_ref_mismatch", ",".join(field_refs), field_refs))
        return
    results.append(_accept(artifact, "claim_event_ref_validator"))
    results.append(_accept(artifact, "source_manifest_ref_validator"))
    results.append(_accept(artifact, "license_manifest_ref_validator"))


def _append_compiler_output_carry_forward_result(
    results: list[ValidatorResult],
    artifact: Mapping[str, Any],
    claim: FLWCAtomicClaimV1 | None,
    event: FLWCFinancialEventV1 | None,
    record: FLWCRawEvidenceRecordV1 | None,
    index: FLWCSourceDocumentIndexV1 | None,
    source: FLWCSourceManifestV1 | None,
    license_: FLWCLicenseManifestV1 | None,
) -> None:
    if None in (claim, event, record, index, source, license_):
        results.append(_reject(artifact, "raw_storage_policy_validator", "claim_event_compiler_artifact_invalid"))
        return
    assert claim and event and record and index and source and license_
    fields: list[str] = []
    expected_raw_storage_policy = record.raw_storage_policy
    if index.raw_storage_policy != expected_raw_storage_policy or source.raw_storage_policy != expected_raw_storage_policy:
        fields.extend(("source_document_index.raw_storage_policy", "source_manifest.raw_storage_policy"))
    if license_.raw_storage_policy != expected_raw_storage_policy:
        fields.append("license_manifest.raw_storage_policy")
    if claim.raw_storage_policy != expected_raw_storage_policy:
        fields.append("atomic_claim.raw_storage_policy")
    if event.raw_storage_policy != expected_raw_storage_policy:
        fields.append("financial_event.raw_storage_policy")

    expected_retention_policy = record.retention_policy
    if index.retention_policy != expected_retention_policy or source.retention_policy != expected_retention_policy:
        fields.extend(("source_document_index.retention_policy", "source_manifest.retention_policy"))
    if license_.retention_policy != expected_retention_policy:
        fields.append("license_manifest.retention_policy")
    if claim.retention_policy != expected_retention_policy:
        fields.append("atomic_claim.retention_policy")
    if event.retention_policy != expected_retention_policy:
        fields.append("financial_event.retention_policy")

    expected_source_trust_tier = record.source_trust_tier
    if index.source_trust_tier != expected_source_trust_tier or source.source_trust_tier != expected_source_trust_tier:
        fields.extend(("source_document_index.source_trust_tier", "source_manifest.source_trust_tier"))
    if claim.source_trust_tier != expected_source_trust_tier:
        fields.append("atomic_claim.source_trust_tier")
    if event.source_trust_tier != expected_source_trust_tier:
        fields.append("financial_event.source_trust_tier")

    if claim.prompt_injection_flags != record.prompt_injection_flags:
        fields.extend(("atomic_claim.prompt_injection_flags", "raw_evidence_record.prompt_injection_flags"))
    if event.prompt_injection_flags != index.prompt_injection_flags:
        fields.extend(("financial_event.prompt_injection_flags", "source_document_index.prompt_injection_flags"))
    if claim.prompt_injection_flags or event.prompt_injection_flags or record.prompt_injection_flags or index.prompt_injection_flags:
        fields.extend(
            (
                "atomic_claim.prompt_injection_flags",
                "financial_event.prompt_injection_flags",
                "raw_evidence_record.prompt_injection_flags",
                "source_document_index.prompt_injection_flags",
            )
        )
    if fields:
        field_refs = tuple(dict.fromkeys(fields))
        reason_code = (
            "prompt_injection_quarantine_missing"
            if any(field.endswith("prompt_injection_flags") for field in field_refs)
            else "claim_event_carry_forward_mismatch"
        )
        validator_id = "prompt_injection_flag_validator" if reason_code == "prompt_injection_quarantine_missing" else "raw_storage_policy_validator"
        results.append(_reject(artifact, validator_id, reason_code, ",".join(field_refs), field_refs))
        return
    results.append(_accept(artifact, "raw_storage_policy_validator"))
    results.append(_accept(artifact, "retention_policy_validator"))


def _append_compiler_output_timestamp_result(
    results: list[ValidatorResult],
    artifact: Mapping[str, Any],
    ledger: FLWCAtomicClaimLedgerV1 | None,
    claim: FLWCAtomicClaimV1 | None,
    event_table: FLWCFinancialEventTableV1 | None,
    event: FLWCFinancialEventV1 | None,
    record: FLWCRawEvidenceRecordV1 | None,
    index: FLWCSourceDocumentIndexV1 | None,
) -> None:
    if None in (ledger, claim, event_table, event, record, index):
        results.append(_reject(artifact, "timestamp_validator", "claim_event_compiler_artifact_invalid"))
        return
    assert ledger and claim and event_table and event and record and index
    fields: list[str] = []
    if claim.source_timestamp_ns is None:
        fields.append("atomic_claim.source_timestamp_ns")
    if event.source_timestamp_ns is None:
        fields.append("financial_event.source_timestamp_ns")
    if fields:
        results.append(_reject(artifact, "timestamp_validator", "source_timestamp_missing", ",".join(fields), tuple(fields)))
        return
    if (
        claim.available_from_ns > ledger.source_cutoff_ns
        or claim.source_timestamp_ns > ledger.source_cutoff_ns
        or event.available_from_ns > event_table.source_cutoff_ns
        or (event.event_time_ns is not None and event.event_time_ns > event_table.source_cutoff_ns)
        or record.available_from_ns > ledger.source_cutoff_ns
        or index.available_from_ns > ledger.source_cutoff_ns
    ):
        results.append(
            _reject(
                artifact,
                "available_from_asof_validator",
                "available_from_after_source_cutoff",
                fields=(
                    "atomic_claim_ledger.source_cutoff_ns",
                    "atomic_claim.available_from_ns",
                    "financial_event_table.source_cutoff_ns",
                    "financial_event.available_from_ns",
                ),
            )
        )
        return
    results.append(_accept(artifact, "timestamp_validator"))
    results.append(_accept(artifact, "available_from_asof_validator"))


def _append_compiler_output_source_span_result(
    results: list[ValidatorResult],
    artifact: Mapping[str, Any],
    claim: FLWCAtomicClaimV1 | None,
    index: FLWCSourceDocumentIndexV1 | None,
) -> None:
    if claim is None or index is None:
        results.append(_reject(artifact, "source_span_ref_validator", "claim_event_compiler_artifact_invalid", fields=("source_span_refs",)))
        return
    invalid: list[str] = []
    out_of_range: list[str] = []
    for ref in claim.source_span_refs:
        parsed = _parse_span_ref(ref, index.source_document_id)
        if parsed is None:
            invalid.append(ref)
            continue
        start, end = parsed
        if start < 1 or end < start or end > index.segment_count:
            out_of_range.append(ref)
    if invalid:
        results.append(_reject(artifact, "source_span_ref_validator", "source_span_ref_invalid", ",".join(invalid), ("atomic_claim.source_span_refs",)))
        return
    if out_of_range:
        results.append(
            _reject(
                artifact,
                "source_span_ref_validator",
                "source_document_segment_ref_invalid",
                ",".join(out_of_range),
                ("atomic_claim.source_span_refs", "source_document_index.segment_count"),
            )
        )
        return
    results.append(_accept(artifact, "source_span_ref_validator"))


def _append_compiler_output_lineage_result(
    results: list[ValidatorResult],
    artifact: Mapping[str, Any],
    ledger: FLWCAtomicClaimLedgerV1 | None,
    claim: FLWCAtomicClaimV1 | None,
    event_table: FLWCFinancialEventTableV1 | None,
    event: FLWCFinancialEventV1 | None,
) -> None:
    fields: list[str] = []
    for field, item in (
        ("atomic_claim_ledger.lineage_digest", ledger),
        ("atomic_claim.lineage_digest", claim),
        ("financial_event_table.lineage_digest", event_table),
        ("financial_event.lineage_digest", event),
    ):
        if item is None or not _is_non_empty_string(item.lineage_digest):
            fields.append(field)
    if fields:
        results.append(_reject(artifact, "lineage_digest_validator", "lineage_digest_missing", ",".join(fields), tuple(fields)))
        return
    results.append(_accept(artifact, "lineage_digest_validator"))


def _append_compiler_output_prompt_injection_result(
    results: list[ValidatorResult],
    artifact: Mapping[str, Any],
    record: FLWCRawEvidenceRecordV1 | None,
    index: FLWCSourceDocumentIndexV1 | None,
) -> None:
    if record is None or index is None:
        results.append(_reject(artifact, "prompt_injection_flag_validator", "claim_event_compiler_artifact_invalid"))
        return
    if record.prompt_injection_flags or index.prompt_injection_flags:
        results.append(
            _reject(
                artifact,
                "prompt_injection_flag_validator",
                "prompt_injection_quarantine_missing",
                fields=("raw_evidence_record.prompt_injection_flags", "source_document_index.prompt_injection_flags"),
            )
        )
        return
    _append_prompt_injection_result(results, artifact)


def _append_compiler_output_synthetic_scope_result(
    results: list[ValidatorResult],
    artifact: Mapping[str, Any],
    ledger: FLWCAtomicClaimLedgerV1 | None,
    claim: FLWCAtomicClaimV1 | None,
    event_table: FLWCFinancialEventTableV1 | None,
    event: FLWCFinancialEventV1 | None,
) -> None:
    if None in (ledger, claim, event_table, event):
        results.append(_reject(artifact, "synthetic_fixture_scope_validator", "claim_event_compiler_artifact_invalid"))
        return
    assert ledger and claim and event_table and event
    fields: list[str] = []
    if ledger.validation_status != ValidatorStatus.ACCEPT or ledger.claim_count != 1:
        fields.append("atomic_claim_ledger")
    if claim.extraction_method != ClaimExtractionMethod.MANUAL_FIXTURE or claim.status != ClaimStatus.PROPOSED:
        fields.append("atomic_claim")
    if event_table.validation_status != ValidatorStatus.ACCEPT or event_table.event_count != 1:
        fields.append("financial_event_table")
    if event.event_derivation_method != EventDerivationMethod.CLAIM_SET_COMPILER or event.status != FinancialEventStatus.PROPOSED:
        fields.append("financial_event")
    if fields:
        field_refs = tuple(fields)
        results.append(_reject(artifact, "synthetic_fixture_scope_validator", "synthetic_fixture_scope_invalid", ",".join(field_refs), field_refs))
        return
    results.append(_accept(artifact, "synthetic_fixture_scope_validator"))


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
    if "atomic_claim" in artifact or "financial_event" in artifact:
        claim = artifact.get("atomic_claim")
        event = artifact.get("financial_event")
        ledger = artifact.get("atomic_claim_ledger")
        claim_id = claim.get("claim_id") if isinstance(claim, Mapping) else None
        event_id = event.get("event_id") if isinstance(event, Mapping) else None
        ledger_id = ledger.get("claim_ledger_id") if isinstance(ledger, Mapping) else None
        return f"{ledger_id or 'unknown_ledger'}:{claim_id or 'unknown_claim'}:{event_id or 'unknown_event'}"
    for field in ("claim_ledger_id", "claim_id", "event_table_id", "event_id", "source_manifest_ref", "license_manifest_ref"):
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
        "claim_ledger_id",
        "claim_id",
        "event_table_id",
        "event_id",
        "source_document_id",
        "source_manifest_ref",
        "license_manifest_ref",
        "source_manifest_id",
        "license_manifest_id",
        "evidence_id",
    ):
        value = artifact.get(key)
        if isinstance(value, str) and value.strip():
            refs.append(value)
    for key in (
        "atomic_claim_ledger",
        "atomic_claim",
        "financial_event_table",
        "financial_event",
        "raw_evidence_vault_manifest",
        "raw_evidence_record",
        "source_document_index",
        "source_manifest",
        "license_manifest",
    ):
        value = artifact.get(key)
        if isinstance(value, Mapping):
            refs.extend(_input_refs(value))
    return tuple(refs)


def _non_claims_checked(artifact: Mapping[str, Any]) -> tuple[str, ...]:
    claims = list(ensure_strings(artifact.get("non_claims", [])))
    for key in (
        "atomic_claim_ledger",
        "atomic_claim",
        "financial_event_table",
        "financial_event",
        "raw_evidence_vault_manifest",
        "raw_evidence_record",
        "source_document_index",
        "source_manifest",
        "license_manifest",
    ):
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
    start = int(span_match.group("start"))
    end = int(span_match.group("end"))
    return start, end


def _find_keys(obj: Any, forbidden_keys: frozenset[str], prefix: str = "") -> list[str]:
    fields: list[str] = []
    if isinstance(obj, Mapping):
        for key, value in obj.items():
            key_text = str(key)
            path = f"{prefix}.{key_text}" if prefix else key_text
            if key_text in forbidden_keys:
                fields.append(path)
            fields.extend(_find_keys(value, forbidden_keys, path))
    elif isinstance(obj, list):
        for index, item in enumerate(obj):
            fields.extend(_find_keys(item, forbidden_keys, f"{prefix}[{index}]"))
    return fields


def _find_nonempty_prompt_injection_flag_fields(obj: Any, prefix: str = "") -> list[str]:
    fields: list[str] = []
    if isinstance(obj, Mapping):
        for key, value in obj.items():
            key_text = str(key)
            path = f"{prefix}.{key_text}" if prefix else key_text
            if key_text == "prompt_injection_flags" and isinstance(value, list) and value:
                fields.append(path)
            fields.extend(_find_nonempty_prompt_injection_flag_fields(value, path))
    elif isinstance(obj, list):
        for index, item in enumerate(obj):
            fields.extend(_find_nonempty_prompt_injection_flag_fields(item, f"{prefix}[{index}]"))
    return fields


def _is_non_empty_string(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


__all__ = [
    "validate_atomic_claim",
    "validate_atomic_claim_file",
    "validate_atomic_claim_ledger",
    "validate_atomic_claim_ledger_file",
    "validate_claim_event_compiler_output",
    "validate_claim_event_compiler_output_file",
    "validate_claim_event_pair",
    "validate_claim_event_pair_file",
    "validate_financial_event",
    "validate_financial_event_file",
    "validate_financial_event_table",
    "validate_financial_event_table_file",
]
