from __future__ import annotations

from copy import deepcopy
from typing import Any

from flwc.compiler.claim_event_fixtures import build_valid_claim_event_compiler_output


def build_valid_validator_suite_packet(**overrides: Any) -> dict[str, object]:
    packet = build_valid_claim_event_compiler_output()
    return _with_overrides(packet, overrides)


def build_source_license_reject_validator_suite_packet() -> dict[str, object]:
    packet = build_valid_validator_suite_packet()
    packet["license_manifest"]["source_id"] = "synthetic_source_mismatch"
    return packet


def build_raw_evidence_reject_validator_suite_packet() -> dict[str, object]:
    packet = build_valid_validator_suite_packet()
    packet["raw_evidence_record"]["raw_text"] = "synthetic inline raw text denied"
    return packet


def build_claim_event_reject_validator_suite_packet() -> dict[str, object]:
    packet = build_valid_validator_suite_packet()
    packet["financial_event"]["model_output"] = "synthetic model output denied"
    return packet


def build_hold_review_validator_suite_packet() -> dict[str, object]:
    packet = build_valid_validator_suite_packet()
    packet["source_manifest"]["revision_policy"] = "custom_review_policy"
    return packet


def _with_overrides(base: dict[str, object], overrides: dict[str, Any]) -> dict[str, object]:
    result = deepcopy(base)
    for key, value in overrides.items():
        result[key] = value
    return result


__all__ = [
    "build_claim_event_reject_validator_suite_packet",
    "build_hold_review_validator_suite_packet",
    "build_raw_evidence_reject_validator_suite_packet",
    "build_source_license_reject_validator_suite_packet",
    "build_valid_validator_suite_packet",
]
