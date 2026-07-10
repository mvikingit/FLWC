from __future__ import annotations

import json
import re
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from flwc.schemas.candidate_package import (
    FLWCCandidateEvidencePackageV1,
    FLWCCandidatePayloadPolicyV1,
    MANDATORY_PACKAGE_NON_CLAIMS,
    MANDATORY_SYNTHETIC_NON_CLAIMS,
    PACKAGE_POSITIVE_INT_FIELDS,
    PACKAGE_REF_LIST_FIELDS,
    PAYLOAD_FALSE_FLAGS,
    PayloadClass,
    SchemaIssue,
)
from flwc.schemas.common import (
    B0_VALIDATOR_NON_CLAIMS,
    ValidatorResult,
    ValidatorStatus,
    ValidatorSummary,
    ensure_strings,
)


SECRET_PATTERNS = (
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    re.compile(r"\bghp_[A-Za-z0-9_]{20,}\b"),
    re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b"),
    re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{20,}\b"),
)

FORBIDDEN_TRADE_FIELDS = frozenset(
    {
        "trade_signal",
        "trade_signal_id",
        "trade_action",
        "trade_side",
        "trade_direction",
        "scanner_signal",
        "scanner_result",
        "scanner_action",
    }
)
FORBIDDEN_ORDER_FIELDS = frozenset({"order_intent", "order_action", "order_type", "order_side", "order_quantity"})
FORBIDDEN_POSITION_FIELDS = frozenset(
    {"position_target", "target_position", "position_size", "position_sizing", "position_quantity"}
)
FORBIDDEN_BROKER_EXECUTION_FIELDS = frozenset(
    {
        "broker",
        "broker_id",
        "broker_account",
        "broker_route",
        "broker_routing",
        "execution_instruction",
        "execution_route",
        "execution_destination",
    }
)

SCHEMA_REASON_PRIORITY = (
    "artifact_not_mapping",
    "schema_version_invalid",
    "required_field_missing",
    "field_type_invalid",
    "enum_value_invalid",
    "required_list_empty",
    "required_map_empty",
)


def validate_candidate_package(package: Mapping[str, Any]) -> dict[str, Any]:
    """Validate a synthetic FLWCCandidateEvidencePackageV1 fixture.

    B0 validators are deterministic fixture-only gates. They do not ingest
    sources, repair artifacts, promote truth, or create runtime/trading authority.
    """
    if not isinstance(package, Mapping):
        result = _reject(
            {},
            "candidate_package_schema_validator",
            "artifact_not_mapping",
            "candidate package must be a JSON object",
            ("$",),
        )
        return _summary({}, [result])

    results: list[ValidatorResult] = []
    parsed_package, schema_issues = FLWCCandidateEvidencePackageV1.from_mapping(package)
    payload_policy, payload_issues = FLWCCandidatePayloadPolicyV1.from_mapping(package.get("payload_policy"))

    _append_schema_result(results, package, schema_issues)
    _append_manifest_ref_result(results, package, "source_manifest_refs", "source_manifest_ref_validator")
    _append_manifest_ref_result(results, package, "license_manifest_refs", "license_manifest_ref_validator")
    _append_source_license_pairing_result(results, package)
    _append_rights_scope_result(results, package)
    _append_raw_storage_policy_result(results, package)
    _append_timestamp_result(results, package)
    _append_available_from_asof_result(results, package)
    _append_lineage_digest_result(results, package)
    _append_payload_policy_result(results, package, payload_policy, payload_issues)
    _append_bounded_payload_result(results, package, payload_policy, payload_issues)
    _append_payload_flag_denial_result(
        results,
        package,
        payload_policy,
        "raw_text_payload_denial_validator",
        "raw_text_in_payload",
        "raw_text_payload_denied",
    )
    _append_payload_flag_denial_result(
        results,
        package,
        payload_policy,
        "raw_llm_output_denial_validator",
        "raw_llm_output_in_payload",
        "raw_llm_output_denied",
    )
    _append_payload_flag_denial_result(
        results,
        package,
        payload_policy,
        "full_rag_context_denial_validator",
        "full_rag_context_in_payload",
        "full_rag_context_denied",
    )
    _append_payload_flag_denial_result(
        results,
        package,
        payload_policy,
        "future_outcome_denial_validator",
        "future_outcome_in_payload",
        "future_outcome_denied",
    )
    _append_boundary_result(
        results,
        package,
        payload_policy,
        "no_trade_field_validator",
        "trade_signal_fields_present",
        FORBIDDEN_TRADE_FIELDS,
        "trade_signal_field_present",
    )
    _append_boundary_result(
        results,
        package,
        payload_policy,
        "no_order_intent_validator",
        "order_intent_fields_present",
        FORBIDDEN_ORDER_FIELDS,
        "order_intent_field_present",
    )
    _append_boundary_result(
        results,
        package,
        payload_policy,
        "no_position_target_validator",
        "position_target_fields_present",
        FORBIDDEN_POSITION_FIELDS,
        "position_target_field_present",
    )
    _append_boundary_result(
        results,
        package,
        payload_policy,
        "broker_execution_field_denial_validator",
        "broker_or_execution_fields_present",
        FORBIDDEN_BROKER_EXECUTION_FIELDS,
        "broker_execution_field_present",
    )
    _append_credential_leak_result(results, package)
    _append_prompt_injection_result(results, package)
    _append_non_claims_result(results, package)
    _append_synthetic_fixture_scope_result(results, package, parsed_package, payload_policy)

    return _summary(package, results)


def validate_candidate_package_file(path: str | Path) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as fh:
        package = json.load(fh)
    return validate_candidate_package(package)


def _append_schema_result(results: list[ValidatorResult], package: Mapping[str, Any], issues: tuple[SchemaIssue, ...]) -> None:
    if not issues:
        results.append(_accept(package, "candidate_package_schema_validator"))
        return

    reason_code = _first_schema_reason(issues)
    results.append(
        _reject(
            package,
            "candidate_package_schema_validator",
            reason_code,
            _issue_detail(issues),
            _issue_fields(issues),
        )
    )


def _append_manifest_ref_result(
    results: list[ValidatorResult], package: Mapping[str, Any], field_name: str, validator_id: str
) -> None:
    if not _is_non_empty_string_list(package.get(field_name)):
        results.append(_reject(package, validator_id, "required_manifest_refs_missing", fields=(field_name,)))
        return
    results.append(_accept(package, validator_id))


def _append_source_license_pairing_result(results: list[ValidatorResult], package: Mapping[str, Any]) -> None:
    source_refs = _string_list(package.get("source_manifest_refs"))
    license_refs = _string_list(package.get("license_manifest_refs"))
    fields: list[str] = []
    if not source_refs:
        fields.append("source_manifest_refs")
    if not license_refs:
        fields.append("license_manifest_refs")
    if len(source_refs) != len(license_refs):
        fields.extend(["source_manifest_refs", "license_manifest_refs"])
    for summary_field in ("license_state_summary", "rights_scope_summary", "raw_storage_policy_summary"):
        summary = package.get(summary_field)
        if not isinstance(summary, Mapping) or any(source_ref not in summary for source_ref in source_refs):
            fields.append(summary_field)
    if fields:
        results.append(
            _reject(
                package,
                "source_license_pairing_validator",
                "source_license_pairing_invalid",
                ",".join(sorted(set(fields))),
                tuple(sorted(set(fields))),
            )
        )
        return
    results.append(_accept(package, "source_license_pairing_validator"))


def _append_rights_scope_result(results: list[ValidatorResult], package: Mapping[str, Any]) -> None:
    summary = package.get("rights_scope_summary")
    if not _is_string_map(summary) or any(value != "research_internal_only" for value in summary.values()):
        results.append(_reject(package, "rights_scope_validator", "rights_scope_invalid", fields=("rights_scope_summary",)))
        return
    results.append(_accept(package, "rights_scope_validator"))


def _append_raw_storage_policy_result(results: list[ValidatorResult], package: Mapping[str, Any]) -> None:
    summary = package.get("raw_storage_policy_summary")
    if not _is_string_map(summary) or any(value != "allowed_full_text" for value in summary.values()):
        results.append(
            _reject(package, "raw_storage_policy_validator", "raw_storage_policy_invalid", fields=("raw_storage_policy_summary",))
        )
        return
    results.append(_accept(package, "raw_storage_policy_validator"))


def _append_timestamp_result(results: list[ValidatorResult], package: Mapping[str, Any]) -> None:
    invalid_fields = tuple(field for field in PACKAGE_POSITIVE_INT_FIELDS if not _is_positive_int(package.get(field)))
    if invalid_fields:
        results.append(
            _reject(
                package,
                "timestamp_validator",
                "timestamp_field_missing_or_invalid",
                ",".join(invalid_fields),
                invalid_fields,
            )
        )
        return
    results.append(_accept(package, "timestamp_validator"))


def _append_available_from_asof_result(results: list[ValidatorResult], package: Mapping[str, Any]) -> None:
    candidate_build_as_of_ns = package.get("candidate_build_as_of_ns")
    source_cutoff_ns = package.get("source_cutoff_ns")
    if _is_positive_int(candidate_build_as_of_ns) and _is_positive_int(source_cutoff_ns) and source_cutoff_ns > candidate_build_as_of_ns:
        results.append(
            _reject(
                package,
                "available_from_asof_validator",
                "source_cutoff_after_candidate_build",
                fields=("source_cutoff_ns", "candidate_build_as_of_ns"),
            )
        )
        return
    results.append(_accept(package, "available_from_asof_validator"))


def _append_lineage_digest_result(results: list[ValidatorResult], package: Mapping[str, Any]) -> None:
    fields: list[str] = []
    for field_name in ("candidate_digest", "lineage_digest"):
        if not _is_non_empty_string(package.get(field_name)):
            fields.append(field_name)
    for field_name in PACKAGE_REF_LIST_FIELDS:
        if not _is_non_empty_string_list(package.get(field_name)):
            fields.append(field_name)
    if fields:
        results.append(
            _reject(
                package,
                "lineage_digest_validator",
                "lineage_or_digest_missing",
                ",".join(fields),
                tuple(fields),
            )
        )
        return
    results.append(_accept(package, "lineage_digest_validator"))


def _append_payload_policy_result(
    results: list[ValidatorResult],
    package: Mapping[str, Any],
    payload_policy: FLWCCandidatePayloadPolicyV1 | None,
    payload_issues: tuple[SchemaIssue, ...],
) -> None:
    if payload_policy is None:
        results.append(
            _reject(
                package,
                "payload_policy_validator",
                "payload_policy_missing_or_invalid",
                _issue_detail(payload_issues),
                _issue_fields(payload_issues) or ("payload_policy",),
            )
        )
        return
    unsafe_flags = payload_policy.unsafe_true_flags()
    if unsafe_flags:
        results.append(
            _reject(
                package,
                "payload_policy_validator",
                "forbidden_payload_flag_not_false",
                ",".join(unsafe_flags),
                tuple(f"payload_policy.{flag}" for flag in unsafe_flags),
            )
        )
        return
    if PayloadClass.SYNTHETIC_FIXTURE_PAYLOAD not in payload_policy.allowed_payload_classes:
        results.append(
            _reject(
                package,
                "payload_policy_validator",
                "synthetic_payload_class_missing",
                fields=("payload_policy.allowed_payload_classes",),
            )
        )
        return
    results.append(_accept(package, "payload_policy_validator"))


def _append_bounded_payload_result(
    results: list[ValidatorResult],
    package: Mapping[str, Any],
    payload_policy: FLWCCandidatePayloadPolicyV1 | None,
    payload_issues: tuple[SchemaIssue, ...],
) -> None:
    if payload_policy is None:
        results.append(
            _reject(
                package,
                "bounded_payload_validator",
                "payload_policy_missing_or_invalid",
                _issue_detail(payload_issues),
                _issue_fields(payload_issues) or ("payload_policy",),
            )
        )
        return
    if payload_policy.runtime_payload_bounded is not True:
        results.append(
            _reject(
                package,
                "bounded_payload_validator",
                "runtime_payload_not_bounded",
                fields=("payload_policy.runtime_payload_bounded",),
            )
        )
        return
    if payload_policy.max_payload_bytes <= 0:
        results.append(
            _reject(
                package,
                "bounded_payload_validator",
                "max_payload_bytes_invalid",
                fields=("payload_policy.max_payload_bytes",),
            )
        )
        return
    payload_size_bytes = _json_size_bytes(package)
    if payload_size_bytes is None or payload_size_bytes > payload_policy.max_payload_bytes:
        results.append(
            _reject(
                package,
                "bounded_payload_validator",
                "payload_exceeds_max_payload_bytes",
                str(payload_size_bytes),
                ("payload_policy.max_payload_bytes",),
            )
        )
        return
    results.append(_accept(package, "bounded_payload_validator"))


def _append_payload_flag_denial_result(
    results: list[ValidatorResult],
    package: Mapping[str, Any],
    payload_policy: FLWCCandidatePayloadPolicyV1 | None,
    validator_id: str,
    flag_name: str,
    reason_code: str,
) -> None:
    if payload_policy is None:
        results.append(_reject(package, validator_id, "payload_policy_missing_or_invalid", fields=("payload_policy",)))
        return
    if getattr(payload_policy, flag_name) is not False:
        results.append(_reject(package, validator_id, reason_code, fields=(f"payload_policy.{flag_name}",)))
        return
    results.append(_accept(package, validator_id))


def _append_boundary_result(
    results: list[ValidatorResult],
    package: Mapping[str, Any],
    payload_policy: FLWCCandidatePayloadPolicyV1 | None,
    validator_id: str,
    flag_name: str,
    forbidden_fields: frozenset[str],
    reason_code: str,
) -> None:
    field_refs = list(_find_forbidden_field_refs(package, forbidden_fields))
    if payload_policy is None:
        field_refs.append("payload_policy")
    elif getattr(payload_policy, flag_name) is not False:
        field_refs.append(f"payload_policy.{flag_name}")

    if field_refs:
        results.append(_reject(package, validator_id, reason_code, ",".join(field_refs), tuple(field_refs)))
        return
    results.append(_accept(package, validator_id))


def _append_credential_leak_result(results: list[ValidatorResult], package: Mapping[str, Any]) -> None:
    if _contains_secret_like_value(package):
        results.append(_reject(package, "credential_leak_validator", "secret_like_value_detected"))
        return
    results.append(_accept(package, "credential_leak_validator"))


def _append_prompt_injection_result(results: list[ValidatorResult], package: Mapping[str, Any]) -> None:
    value = package.get("prompt_injection_flags")
    if value is None:
        results.append(_accept(package, "prompt_injection_flag_validator"))
        return
    if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
        results.append(_reject(package, "prompt_injection_flag_validator", "field_type_invalid", fields=("prompt_injection_flags",)))
        return
    if value:
        results.append(
            _reject(
                package,
                "prompt_injection_flag_validator",
                "prompt_injection_flags_present",
                ",".join(value),
                ("prompt_injection_flags",),
            )
        )
        return
    results.append(_accept(package, "prompt_injection_flag_validator"))


def _append_non_claims_result(results: list[ValidatorResult], package: Mapping[str, Any]) -> None:
    non_claims = set(ensure_strings(package.get("non_claims", [])))
    missing_non_claims = tuple(sorted(set(MANDATORY_PACKAGE_NON_CLAIMS) - non_claims))
    if missing_non_claims:
        results.append(
            _reject(
                package,
                "non_claims_validator",
                "missing_mandatory_non_claims",
                ",".join(missing_non_claims),
                ("non_claims",),
            )
        )
        return
    results.append(_accept(package, "non_claims_validator"))


def _append_synthetic_fixture_scope_result(
    results: list[ValidatorResult],
    package: Mapping[str, Any],
    parsed_package: FLWCCandidateEvidencePackageV1 | None,
    payload_policy: FLWCCandidatePayloadPolicyV1 | None,
) -> None:
    fields: list[str] = []
    if package.get("package_scope") != "synthetic_fixture_only":
        fields.append("package_scope")
    non_claims = set(ensure_strings(package.get("non_claims", [])))
    if set(MANDATORY_SYNTHETIC_NON_CLAIMS) - non_claims:
        fields.append("non_claims")
    if not _summary_values_equal(package.get("license_state_summary"), "allowed_full_text"):
        fields.append("license_state_summary")
    if not _summary_values_equal(package.get("rights_scope_summary"), "research_internal_only"):
        fields.append("rights_scope_summary")
    if not _summary_values_equal(package.get("raw_storage_policy_summary"), "allowed_full_text"):
        fields.append("raw_storage_policy_summary")
    if payload_policy is None or PayloadClass.SYNTHETIC_FIXTURE_PAYLOAD not in payload_policy.allowed_payload_classes:
        fields.append("payload_policy.allowed_payload_classes")
    if parsed_package is not None and parsed_package.package_scope.value != "synthetic_fixture_only":
        fields.append("package_scope")

    if fields:
        reason_code = "b0_non_synthetic_scope_rejected" if "package_scope" in fields else "synthetic_fixture_policy_invalid"
        field_refs = tuple(sorted(set(fields)))
        results.append(_reject(package, "synthetic_fixture_scope_validator", reason_code, ",".join(field_refs), field_refs))
        return
    results.append(_accept(package, "synthetic_fixture_scope_validator"))


def _summary(package: Mapping[str, Any], results: list[ValidatorResult]) -> dict[str, Any]:
    artifact_ref = _artifact_ref(package)
    summary = ValidatorSummary.from_results(
        validator_summary_id=f"{artifact_ref}:validator_summary",
        input_artifact_refs=(artifact_ref,),
        validator_results=tuple(results),
    )
    return summary.as_dict()


def _reject(
    package: Mapping[str, Any],
    validator_id: str,
    reason_code: str,
    detail: str = "",
    fields: tuple[str, ...] = (),
) -> ValidatorResult:
    return _result(package, validator_id, ValidatorStatus.REJECT, reason_code, detail, fields)


def _accept(package: Mapping[str, Any], validator_id: str, reason_code: str = "accepted") -> ValidatorResult:
    return _result(package, validator_id, ValidatorStatus.ACCEPT, reason_code)


def _result(
    package: Mapping[str, Any],
    validator_id: str,
    status: ValidatorStatus,
    reason_code: str,
    detail: str = "",
    fields: tuple[str, ...] = (),
) -> ValidatorResult:
    return ValidatorResult(
        validator_id=validator_id,
        result=status,
        reason_code=reason_code,
        reason_detail_bounded=detail,
        field_refs=fields,
        artifact_ref=_artifact_ref(package),
        artifact_schema_version=_artifact_schema_version(package),
        input_refs=_input_refs(package),
        lineage_digest_checked=_lineage_digest(package),
        non_claims_checked=tuple(sorted(ensure_strings(package.get("non_claims", [])))),
        non_claims=B0_VALIDATOR_NON_CLAIMS,
    )


def _artifact_ref(package: Mapping[str, Any]) -> str:
    value = package.get("candidate_package_id")
    return value if isinstance(value, str) and value.strip() else "unknown_candidate_package"


def _artifact_schema_version(package: Mapping[str, Any]) -> str:
    value = package.get("schema_version")
    return value if isinstance(value, str) else ""


def _lineage_digest(package: Mapping[str, Any]) -> str | None:
    value = package.get("lineage_digest")
    return value if isinstance(value, str) else None


def _input_refs(package: Mapping[str, Any]) -> tuple[str, ...]:
    refs: list[str] = []
    for field_name in PACKAGE_REF_LIST_FIELDS:
        refs.extend(_string_list(package.get(field_name)))
    return tuple(refs)


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


def _contains_secret_like_value(obj: Any) -> bool:
    text = json.dumps(obj, sort_keys=True, ensure_ascii=False)
    return any(pattern.search(text) for pattern in SECRET_PATTERNS)


def _json_size_bytes(obj: Any) -> int | None:
    try:
        return len(json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8"))
    except TypeError:
        return None


def _find_forbidden_field_refs(obj: Any, forbidden_fields: frozenset[str], prefix: str = "") -> tuple[str, ...]:
    refs: list[str] = []
    if isinstance(obj, Mapping):
        for key, value in obj.items():
            key_ref = f"{prefix}.{key}" if prefix else str(key)
            if isinstance(key, str) and key in forbidden_fields:
                refs.append(key_ref)
            refs.extend(_find_forbidden_field_refs(value, forbidden_fields, key_ref))
    elif isinstance(obj, list):
        for index, value in enumerate(obj):
            refs.extend(_find_forbidden_field_refs(value, forbidden_fields, f"{prefix}[{index}]"))
    return tuple(refs)


def _summary_values_equal(value: object, expected: str) -> bool:
    return _is_string_map(value) and all(item == expected for item in value.values())


def _is_non_empty_string(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _is_positive_int(value: object) -> bool:
    return type(value) is int and value > 0


def _is_non_empty_string_list(value: object) -> bool:
    return bool(_string_list(value))


def _string_list(value: object) -> tuple[str, ...]:
    if not isinstance(value, list):
        return ()
    if any(not isinstance(item, str) or not item.strip() for item in value):
        return ()
    return tuple(value)


def _is_string_map(value: object) -> bool:
    return isinstance(value, Mapping) and bool(value) and all(
        isinstance(key, str) and key.strip() and isinstance(item, str) and item.strip() for key, item in value.items()
    )
