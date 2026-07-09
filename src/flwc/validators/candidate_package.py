from __future__ import annotations

import json
import re
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from flwc.schemas.common import ValidatorResult, ValidatorStatus, ensure_strings
from flwc.validators.core import aggregate_validator_results

MANDATORY_PACKAGE_NON_CLAIMS = {
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
}

PAYLOAD_FALSE_FLAGS = {
    "raw_text_in_payload",
    "raw_llm_output_in_payload",
    "full_rag_context_in_payload",
    "future_outcome_in_payload",
    "trade_signal_fields_present",
    "order_intent_fields_present",
    "position_target_fields_present",
    "broker_or_execution_fields_present",
}

SECRET_PATTERNS = [
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    re.compile(r"\bghp_[A-Za-z0-9_]{20,}\b"),
    re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b"),
    re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{20,}\b"),
]


def _reject(validator_id: str, reason_code: str, detail: str = "", fields: tuple[str, ...] = ()) -> ValidatorResult:
    return ValidatorResult(
        validator_id=validator_id,
        result=ValidatorStatus.REJECT,
        reason_code=reason_code,
        reason_detail_bounded=detail,
        field_refs=fields,
        non_claims=("fixture_validator_only", "not_truth_authority", "not_runtime_authority"),
    )


def _accept(validator_id: str, reason_code: str = "accepted") -> ValidatorResult:
    return ValidatorResult(
        validator_id=validator_id,
        result=ValidatorStatus.ACCEPT,
        reason_code=reason_code,
        non_claims=("fixture_validator_only", "not_truth_authority", "not_runtime_authority"),
    )


def _contains_secret_like_value(obj: Any) -> bool:
    text = json.dumps(obj, sort_keys=True, ensure_ascii=False)
    return any(p.search(text) for p in SECRET_PATTERNS)


def validate_candidate_package(package: Mapping[str, Any]) -> dict[str, Any]:
    """Validate a synthetic FLWCCandidateEvidencePackageV1 fixture.

    This is a B0 fixture-only validator scaffold. It is not source-ingestion,
    not production authority, and not external admission authority.
    """
    results: list[ValidatorResult] = []

    if package.get("schema_version") != "FLWCCandidateEvidencePackageV1":
        results.append(_reject("candidate_package_schema_validator", "schema_version_invalid", fields=("schema_version",)))
    else:
        results.append(_accept("candidate_package_schema_validator"))

    non_claims = set(ensure_strings(package.get("non_claims", [])))
    missing_non_claims = sorted(MANDATORY_PACKAGE_NON_CLAIMS - non_claims)
    if missing_non_claims:
        results.append(_reject("non_claims_validator", "missing_mandatory_non_claims", ",".join(missing_non_claims), ("non_claims",)))
    else:
        results.append(_accept("non_claims_validator"))

    payload_policy = package.get("payload_policy")
    if not isinstance(payload_policy, Mapping):
        results.append(_reject("payload_policy_validator", "payload_policy_missing_or_invalid", fields=("payload_policy",)))
    else:
        bad_true = sorted(k for k in PAYLOAD_FALSE_FLAGS if payload_policy.get(k) is not False)
        if bad_true:
            results.append(_reject("payload_policy_validator", "forbidden_payload_flag_not_false", ",".join(bad_true), tuple(f"payload_policy.{k}" for k in bad_true)))
        elif payload_policy.get("runtime_payload_bounded") is not True:
            results.append(_reject("bounded_payload_validator", "runtime_payload_not_bounded", fields=("payload_policy.runtime_payload_bounded",)))
        elif not isinstance(payload_policy.get("max_payload_bytes"), int) or payload_policy.get("max_payload_bytes") <= 0:
            results.append(_reject("bounded_payload_validator", "max_payload_bytes_invalid", fields=("payload_policy.max_payload_bytes",)))
        else:
            results.append(_accept("payload_policy_validator"))
            results.append(_accept("bounded_payload_validator"))

    for field in ("source_manifest_refs", "license_manifest_refs"):
        value = package.get(field)
        if not isinstance(value, list) or not value:
            results.append(_reject(f"{field}_validator", "required_manifest_refs_missing", fields=(field,)))
        else:
            results.append(_accept(f"{field}_validator"))

    timestamp_rejected = False
    for field in ("candidate_build_as_of_ns", "source_cutoff_ns", "created_at_ns"):
        if not isinstance(package.get(field), int) or package[field] <= 0:
            timestamp_rejected = True
            results.append(_reject("timestamp_validator", "timestamp_field_missing_or_invalid", fields=(field,)))
    if not timestamp_rejected:
        results.append(_accept("timestamp_validator"))

    if _contains_secret_like_value(package):
        results.append(_reject("credential_leak_validator", "secret_like_value_detected"))
    else:
        results.append(_accept("credential_leak_validator"))

    aggregate = aggregate_validator_results(results)
    return {
        "schema_version": "FLWCValidatorSummaryV1",
        "aggregate_result": aggregate.value,
        "validator_results": [r.as_dict() for r in results],
        "non_claims": [
            "fixture_only",
            "not_truth_authority",
            "not_source_ingestion",
            "not_runtime_authority",
            "not_trade_signal",
        ],
    }


def validate_candidate_package_file(path: str | Path) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as fh:
        package = json.load(fh)
    return validate_candidate_package(package)
